from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'reports/nifty_calendar/P9_HF_OOS_FETCH_MANIFEST.csv'
OOS=ROOT/'reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv'
OUT=ROOT/'reports/nifty_calendar/P9_OOS_FASTV2_COMPARISON.csv'
COST=ROOT/'reports/nifty_calendar/P9_OOS_FASTV2_COSTS.csv'
REPORT=ROOT/'reports/nifty_calendar/P9_OOS_FASTV2_REPORT.md'

def load_mod(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m

p8=load_mod(ROOT/'scripts/p8_score.py','p8')

COLS=['timestamp','open','close','volume','strike','option_type']

def read_date(path,date):
    start=pd.Timestamp(date+' 00:00:00',tz='Asia/Kolkata')
    end=start+pd.Timedelta(days=1)
    filters=[[('timestamp','>=',start),('timestamp','<',end)]]
    try:
        df=pd.read_parquet(path,columns=COLS,filters=filters)
    except Exception:
        df=pd.read_parquet(path,columns=COLS)
        ts=pd.to_datetime(df['timestamp'],errors='coerce')
        if ts.dt.tz is None:
            mask=ts.dt.strftime('%Y-%m-%d').eq(date)
        else:
            mask=ts.dt.tz_convert('Asia/Kolkata').dt.strftime('%Y-%m-%d').eq(date)
        df=df[mask].copy()
    if df.empty:return df
    df['timestamp']=pd.to_datetime(df['timestamp'],errors='coerce')
    if df['timestamp'].dt.tz is not None:
        df['timestamp']=df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    df['option_type']=df['option_type'].astype(str).str.upper()
    for c in ['open','close','volume','strike']:
        df[c]=pd.to_numeric(df[c],errors='coerce')
    return df[df['option_type'].isin(['CE','PE']) & df['strike'].notna()].copy()

def path_map(m):
    return {Path(r.file).stem:r.local_path for _,r in m[m.status.eq('DOWNLOADED') & m.kind.eq('option')].iterrows()}

def signal(near,far,spot,cutoff):
    n=near[(near.volume.fillna(0)>0)&near.close.gt(0)].copy()
    f=far[(far.volume.fillna(0)>0)&far.close.gt(0)].copy()
    def piv(df,pfx):
        x=df.pivot_table(index=['timestamp','strike'],columns='option_type',values=['close','volume','open'],aggfunc='last')
        if x.empty:return pd.DataFrame()
        x.columns=[f'{pfx}_{a}_{b}' for a,b in x.columns]
        return x.reset_index()
    x=piv(n,'near').merge(piv(f,'far'),on=['timestamp','strike'],how='inner')
    if x.empty:return None
    sp=spot.sort_values('timestamp')
    x=pd.merge_asof(x.sort_values('timestamp'),sp,on='timestamp',direction='backward',tolerance=pd.Timedelta(minutes=1))
    x=x[x['spot_close'].notna()].copy()
    if x.empty:return None
    x['dist']=(x.strike-x.spot_close).abs()
    x['time']=x.timestamp.dt.strftime('%H:%M')
    x=x[(x.time>='09:15')&(x.time<=cutoff)].sort_values(['timestamp','dist','strike'])
    if x.empty:return None
    x=x.groupby('timestamp',as_index=False).head(1).copy()
    req=['near_close_CE','near_close_PE','far_close_CE','far_close_PE','near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    if any(c not in x.columns for c in req):return None
    x=x.dropna(subset=req)
    x=x[(x[['near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']]>0).all(axis=1)]
    x=x[(x[['near_close_CE','near_close_PE','far_close_CE','far_close_PE']]>0).all(axis=1)]
    if x.empty:return None
    x['cbr']=(x.far_close_CE/x.near_close_CE)/(x.far_close_PE/x.near_close_PE)
    h=x.loc[x.cbr<=1.2].sort_values('timestamp').head(1)
    if h.empty:return None
    h=h.iloc[0]
    return {'signal_timestamp':h.timestamp,'strike':float(h.strike),'cbr':float(h.cbr)}

def fill(near,far,date,strike,ts):
    n=near[(near.strike.eq(strike))&near.volume.fillna(0).gt(0)].copy()
    f=far[(far.strike.eq(strike))&far.volume.fillna(0).gt(0)].copy()
    def piv(df,p):
        x=df.pivot_table(index='timestamp',columns='option_type',values='open',aggfunc='last')
        return x.rename(columns={'CE':p+'_CE','PE':p+'_PE'}).reset_index() if not x.empty else x.reset_index()
    x=piv(n,'near').merge(piv(f,'far'),on='timestamp',how='inner')
    x=x[x.timestamp>pd.Timestamp(ts)].sort_values('timestamp')
    if x.empty:return None
    req=['near_CE','near_PE','far_CE','far_PE']; x=x.dropna(subset=req)
    if x.empty:return None
    h=x.iloc[0]
    return {'fill_timestamp':h.timestamp,'entry_near_ce':float(h.near_CE),'entry_near_pe':float(h.near_PE),'entry_far_ce':float(h.far_CE),'entry_far_pe':float(h.far_PE)}

def exits(near,far,date,strike):
    def last(df):
        x=df[(df.strike.eq(strike))&df.volume.fillna(0).gt(0)&df.close.gt(0)].copy()
        if x.empty:return None
        p=x.pivot_table(index='timestamp',columns='option_type',values='close',aggfunc='last')
        if not {'CE','PE'}.issubset(p.columns):return None
        h=p.sort_index().dropna().iloc[-1]
        return {'ce':float(h.CE),'pe':float(h.PE)}
    n=last(near); f=last(far)
    if n is None or f is None:return None
    return {'exit_near_ce':n['ce'],'exit_near_pe':n['pe'],'exit_far_ce':f['ce'],'exit_far_pe':f['pe']}

def pnl(f,x,lot):
    pts=(x.exit_near_pe-f.entry_near_pe)-(x.exit_near_ce-f.entry_near_ce)+(x.exit_far_ce-f.entry_far_ce)-(x.exit_far_pe-f.entry_far_pe)
    return float(pts),float(pts*lot)

def main():
    manifest=pd.read_csv(MANIFEST)
    pm=path_map(manifest)
    cycles=pd.read_csv(OOS); cycles=cycles[cycles.status.eq('EXECUTABLE')].copy()
    for c in ['entry_date','near_expiry','far_expiry']:
        cycles[c]=pd.to_datetime(cycles[c]).dt.strftime('%Y-%m-%d')
    idx_path=manifest.loc[manifest.kind.eq('index')&manifest.status.eq('DOWNLOADED'),'local_path'].iloc[0]
    idx=pd.read_parquet(idx_path,columns=['timestamp','close'])
    idx['timestamp']=pd.to_datetime(idx['timestamp'])
    if idx['timestamp'].dt.tz is not None: idx['timestamp']=idx['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    idx=idx.rename(columns={'close':'spot_close'})
    rows=[]
    for cc in cycles.to_dict('records'):
        ne,fe,ed=cc['near_expiry'],cc['far_expiry'],cc['entry_date']
        if ne not in pm or fe not in pm:
            rows.append({**cc,'status':'SOURCE_GAP'}); continue
        try:
            near_entry=read_date(pm[ne],ed); far_entry=read_date(pm[fe],ed)
            near_exit=read_date(pm[ne],ne); far_exit=read_date(pm[fe],ne)
            sp=idx[idx.timestamp.dt.strftime('%Y-%m-%d').eq(ed)][['timestamp','spot_close']].copy()
            result={**cc,'status':'ANALYZED'}
            for arm,cutoff in [('fixed','09:15'),('event','15:30')]:
                sig=signal(near_entry,far_entry,sp,cutoff)
                result[f'{arm}_status']='NO_TRIGGER'
                if sig is None: continue
                fl=fill(near_entry,far_entry,ed,sig['strike'],sig['signal_timestamp'])
                if fl is None: result[f'{arm}_status']='NO_FILL'; continue
                ex=exits(near_exit,far_exit,ne,sig['strike'])
                if ex is None: result[f'{arm}_status']='NO_EXIT'; continue
                row=pd.Series({**fl,**ex})
                pts,inr=pnl(fl,row,float(cc['lot_near']))
                result.update({f'{arm}_status':'EXECUTABLE',f'{arm}_signal_timestamp':sig['signal_timestamp'],f'{arm}_strike':sig['strike'],f'{arm}_cbr':sig['cbr'],f'{arm}_pnl_points':pts,f'{arm}_pnl_inr':inr,f'{arm}_fill_timestamp':fl['fill_timestamp'],f'{arm}_entry_near_ce':fl['entry_near_ce'],f'{arm}_entry_near_pe':fl['entry_near_pe'],f'{arm}_entry_far_ce':fl['entry_far_ce'],f'{arm}_entry_far_pe':fl['entry_far_pe'],f'{arm}_exit_near_ce':ex['exit_near_ce'],f'{arm}_exit_near_pe':ex['exit_near_pe'],f'{arm}_exit_far_ce':ex['exit_far_ce'],f'{arm}_exit_far_pe':ex['exit_far_pe'],f'{arm}_delay_minutes':(pd.Timestamp(fl['fill_timestamp'])-pd.Timestamp(ed+' 09:15:00')).total_seconds()/60.0})
            rows.append(result)
        except Exception as e:
            rows.append({**cc,'status':'ERROR','reason':type(e).__name__+':'+str(e)[:200]})
    out=pd.DataFrame(rows); out.to_csv(OUT,index=False)
    cost=[]
    for arm in ['fixed','event']:
        sub=out[out[f'{arm}_status'].eq('EXECUTABLE')].copy()
        p=pd.to_numeric(sub.get(f'{arm}_pnl_inr',pd.Series(dtype=float)),errors='coerce').dropna().to_numpy(float)
        if len(p):
            curve=np.cumsum(p); dd=curve-np.maximum.accumulate(curve); pos=p[p>0];neg=p[p<0]
            stat={'n':len(p),'gross':float(p.sum()),'win':float((p>0).mean()),'pf':float(pos.sum()/(-neg.sum())) if len(neg) else float('inf'),'dd':abs(float(dd.min())),'worst':float(p.min())}
        else: stat={'n':0,'gross':0.0,'win':np.nan,'pf':np.nan,'dd':np.nan,'worst':np.nan}
        for slip in [0,0.5,1,2]:
            net_total=0.0
            for _,r in sub.iterrows():
                rr=pd.Series({'entry_date':r.entry_date,'near_expiry':r.near_expiry,'lot_near':r.lot_near,'lot_far':r.lot_far,'entry_near_pe':r[f'{arm}_entry_near_pe'],'entry_near_ce':r[f'{arm}_entry_near_ce'],'entry_far_ce':r[f'{arm}_entry_far_ce'],'entry_far_pe':r[f'{arm}_entry_far_pe'],'exit_near_pe':r[f'{arm}_exit_near_pe'],'exit_near_ce':r[f'{arm}_exit_near_ce'],'exit_far_ce':r[f'{arm}_exit_far_ce'],'exit_far_pe':r[f'{arm}_exit_far_pe'],'pnl_inr':r[f'{arm}_pnl_inr']})
                net_total+=p8.net_cost(rr,slip,0.0005)
            cost.append({'arm':arm,'n':stat['n'],'gross_pnl_inr':stat['gross'],'win_rate':stat['win'],'profit_factor':stat['pf'],'gross_max_drawdown_inr':stat['dd'],'worst_trade_inr':stat['worst'],'slippage_points':slip,'exchange_rate':0.0005,'net_pnl_inr':net_total})
    pd.DataFrame(cost).to_csv(COST,index=False)
    paired=out[out.fixed_status.eq('EXECUTABLE')&out.event_status.eq('EXECUTABLE')].copy()
    report=['# P9 OOS Fast V2 — Fixed 09:15 vs Event 15:30','',f'- OOS cycles: {len(out)}',f'- Source gaps: {int((out.status=="SOURCE_GAP").sum())}',f'- Fixed trades: {int((out.fixed_status=="EXECUTABLE").sum())}',f'- Event trades: {int((out.event_status=="EXECUTABLE").sum())}',f'- Paired dates: {len(paired)}']
    if len(paired):
        d=paired.event_pnl_inr-paired.fixed_pnl_inr; report += [f'- Mean event minus fixed: ₹{d.mean():,.2f}',f'- Median event minus fixed: ₹{d.median():,.2f}',f'- Event higher on {int((d>0).sum())}/{len(d)} paired dates']
    report += ['', 'Primary signal: frozen CBR <= 1.20; 1-minute close -> next-minute open.', 'Costs: same P8 modeled stress, 0/0.5/1/2 points slippage.']
    REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')

if __name__=='__main__': main()