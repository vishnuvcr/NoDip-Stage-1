from __future__ import annotations

from pathlib import Path
import importlib.util
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

scanner=load('scanner',ROOT/'scripts/p9_scan_event_timing.py')
p8score=load('p8score',ROOT/'scripts/p8_score.py')
MANIFEST=ROOT/'reports/nifty_calendar/P9_HF_OOS_FETCH_MANIFEST.csv'
OOS=ROOT/'reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv'
OUT=ROOT/'reports/nifty_calendar/P9_OOS_FAST_COMPARISON.csv'
COST=ROOT/'reports/nifty_calendar/P9_OOS_FAST_COSTS.csv'
REPORT=ROOT/'reports/nifty_calendar/P9_OOS_FAST_REPORT.md'

def signal(panel,spot,start,cutoff):
    x=scanner.add_spot(panel,spot)
    x=x[x['spot_close'].notna()].copy()
    x['abs_atm']=(x['strike']-x['spot_close']).abs()
    x['time']=x['timestamp'].dt.strftime('%H:%M')
    x=x[(x['time']>=start)&(x['time']<=cutoff)].sort_values(['timestamp','abs_atm','strike'])
    if x.empty:return None
    x=x.groupby('timestamp',as_index=False).head(1).copy()
    req=['near_close_CE','near_close_PE','far_close_CE','far_close_PE','near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    if any(c not in x.columns for c in req):return None
    x=x.dropna(subset=req)
    x=x[(x[['near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']]>0).all(axis=1)]
    x=x[(x[['near_close_CE','near_close_PE','far_close_CE','far_close_PE']]>0).all(axis=1)]
    if x.empty:return None
    x['cbr']=(x['far_close_CE']/x['near_close_CE'])/(x['far_close_PE']/x['near_close_PE'])
    h=x.loc[x['cbr']<=1.20].sort_values('timestamp').head(1)
    if h.empty:return None
    h=h.iloc[0]
    return {'signal_timestamp':str(h['timestamp']),'signal_strike':float(h['strike']),'cbr':float(h['cbr'])}

def do_trade(c,near,far,pmap,spot,start,cutoff):
    panel=scanner.pivot_four(near,far,c['entry_date'])
    if panel.empty:return None,'NO_PANEL'
    sig=signal(panel,spot,start,cutoff)
    if sig is None:return None,'NO_TRIGGER'
    fill=scanner.next_fill(near,far,c['entry_date'],sig['signal_strike'],sig['signal_timestamp'])
    if fill is None:return None,'NO_FILL'
    ex=scanner.exit_prices(pmap,c['near_expiry'],c['far_expiry'],sig['signal_strike'])
    if ex is None:return None,'NO_EXIT'
    pts=scanner.pnl(fill,ex)
    row={**c,**sig,**fill,**ex,'pnl_points':pts,'pnl_inr':pts*float(c['lot_near']),'delay_minutes':(pd.Timestamp(fill['fill_timestamp'])-pd.Timestamp(c['entry_date']+' 09:15:00')).total_seconds()/60.0}
    return row,'EXECUTABLE'

def net(rr,slip):
    s=pd.Series(rr)
    return p8score.net_cost(s,slip,0.0005)

def main():
    manifest=pd.read_csv(MANIFEST)
    pmap=scanner.path_map(manifest)
    cycles=pd.read_csv(OOS)
    cycles=cycles[cycles['status'].eq('EXECUTABLE')].copy()
    for c in ['entry_date','near_expiry','far_expiry']:
        cycles[c]=pd.to_datetime(cycles[c]).dt.strftime('%Y-%m-%d')
    idx_path=manifest[(manifest['kind']=='index')&(manifest['status']=='DOWNLOADED')]['local_path'].iloc[0]
    idx=pd.read_parquet(idx_path,columns=['timestamp','close'])
    idx['timestamp']=pd.to_datetime(idx['timestamp'])
    idx=idx.rename(columns={'close':'spot_close'})
    rows=[]
    for _,cc in cycles.iterrows():
        c=cc.to_dict()
        ne,fe=c['near_expiry'],c['far_expiry']
        if ne not in pmap or fe not in pmap:
            rows.append({**c,'status':'SOURCE_GAP'});continue
        try:
            near=scanner.prep_option(pmap[ne],[c['entry_date'],ne])
            far=scanner.prep_option(pmap[fe],[c['entry_date'],ne])
            spot=idx[idx['timestamp'].dt.strftime('%Y-%m-%d').eq(c['entry_date'])][['timestamp','spot_close']].copy()
            fixed,fstat=do_trade(c,near,far,pmap,spot,'09:15','09:15')
            event,estat=do_trade(c,near,far,pmap,spot,'09:15','15:30')
            row={**c,'status':'ANALYZED','fixed_status':fstat,'event_status':estat}
            if fixed is not None:
                for k,v in fixed.items(): row['fixed_'+k]=v
            if event is not None:
                for k,v in event.items(): row['event_'+k]=v
            rows.append(row)
        except Exception as e:
            rows.append({**c,'status':'ERROR','reason':type(e).__name__+':'+str(e)[:200]})
    out=pd.DataFrame(rows)
    out.to_csv(OUT,index=False)

    def perf(x):
        a=pd.to_numeric(x,errors='coerce').dropna().to_numpy(float)
        if len(a)==0:return {'n':0,'gross':0.0,'win':np.nan,'pf':np.nan,'dd':np.nan,'worst':np.nan}
        pos=a[a>0];neg=a[a<0];curve=np.cumsum(a);dd=curve-np.maximum.accumulate(curve)
        return {'n':len(a),'gross':float(a.sum()),'win':float((a>0).mean()),'pf':float(pos.sum()/(-neg.sum())) if len(neg) else float('inf'),'dd':float(dd.min()),'worst':float(a.min())}

    cost_rows=[]
    for arm,status_col,prefix in [('fixed','fixed_status','fixed_'),('event','event_status','event_')]:
        sub=out[out[status_col].eq('EXECUTABLE')].copy()
        pnl_col=f'{prefix}pnl_inr'
        p=perf(sub[pnl_col]) if pnl_col in sub.columns else perf(pd.Series(dtype=float))
        for slip in (0.0,0.5,1.0,2.0):
            net_sum=0.0
            for _,rr in sub.iterrows():
                t={
                    'entry_date':rr['entry_date'],'near_expiry':rr['near_expiry'],
                    'lot_near':rr['lot_near'],'lot_far':rr['lot_far'],
                    'entry_near_pe':rr[f'{prefix}entry_near_pe'],'entry_near_ce':rr[f'{prefix}entry_near_ce'],
                    'entry_far_ce':rr[f'{prefix}entry_far_ce'],'entry_far_pe':rr[f'{prefix}entry_far_pe'],
                    'exit_near_pe':rr[f'{prefix}exit_near_pe'],'exit_near_ce':rr[f'{prefix}exit_near_ce'],
                    'exit_far_ce':rr[f'{prefix}exit_far_ce'],'exit_far_pe':rr[f'{prefix}exit_far_pe'],
                    'pnl_inr':rr[f'{prefix}pnl_inr']}
                net_sum += net(t,slip)
            cost_rows.append({'arm':arm,'n':p['n'],'gross_pnl_inr':p['gross'],'win_rate':p['win'],'profit_factor':p['pf'],'gross_max_drawdown_inr':abs(p['dd']) if np.isfinite(p['dd']) else np.nan,'worst_trade_inr':p['worst'],'slippage_points':slip,'exchange_rate':0.0005,'net_pnl_inr':net_sum})
    pd.DataFrame(cost_rows).to_csv(COST,index=False)

    paired=out[(out.fixed_status.eq('EXECUTABLE'))&(out.event_status.eq('EXECUTABLE'))].copy()
    paired_cols={'fixed_pnl_inr','event_pnl_inr'}
    if not paired_cols.issubset(set(paired.columns)):
        paired=paired.iloc[0:0].copy()
    summary=[
        '# P9 OOS Fast Fixed-vs-Event Comparison','',
        f'- OOS cycles: {len(out)}',
        f'- Source gaps: {int((out.status=="SOURCE_GAP").sum())}',
        f'- Fixed 09:15 trades: {int((out.fixed_status=="EXECUTABLE").sum())}',
        f'- Event 15:30 trades: {int((out.event_status=="EXECUTABLE").sum())}',
        f'- Paired dates: {len(paired)}'
    ]
    if len(paired):
        d=paired.event_pnl_inr-paired.fixed_pnl_inr
        summary += [f'- Mean event minus fixed: ₹{d.mean():,.2f}',f'- Median event minus fixed: ₹{d.median():,.2f}',f'- Event higher on {int((d>0).sum())}/{len(d)} paired dates']
    summary += ['','Cost table: reports/nifty_calendar/P9_OOS_FAST_COSTS.csv']
    REPORT.write_text('\n'.join(summary)+'\n',encoding='utf-8')

if __name__=='__main__':main()