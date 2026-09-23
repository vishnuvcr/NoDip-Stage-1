from __future__ import annotations

from pathlib import Path
import importlib.util
import duckdb
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'reports/nifty_calendar/P9_HF_OOS_FETCH_MANIFEST.csv'
OOS=ROOT/'reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv'
OUT=ROOT/'reports/nifty_calendar/P9_OOS_DUCKDB_COMPARISON.csv'
COST=ROOT/'reports/nifty_calendar/P9_OOS_DUCKDB_COSTS.csv'
REPORT=ROOT/'reports/nifty_calendar/P9_OOS_DUCKDB_REPORT.md'

p8_path=ROOT/'scripts/p8_score.py'
spec=importlib.util.spec_from_file_location('p8',p8_path)
p8=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(p8)

CACHE:dict[tuple[str,str],pd.DataFrame]={}

HF='https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/resolve/main/'

def path_map(m):
    return {Path(r.file).stem:(HF+r.file) for _,r in m[m.kind.eq('option')].iterrows()}

def index_url():
    return HF+'index/NIFTY.parquet'

def query_date(con,path,date):
    key=(path,date)
    if key in CACHE:
        return CACHE[key]
    q="""
    SELECT timestamp, open, close, volume, strike, option_type
    FROM read_parquet(?)
    WHERE CAST(timestamp AS DATE)=CAST(? AS DATE)
      AND option_type IN ('CE','PE')
      AND strike IS NOT NULL
    """
    df=con.execute(q,[path,date]).fetch_df()
    if not df.empty:
        df['timestamp']=pd.to_datetime(df['timestamp'],errors='coerce')
        if getattr(df['timestamp'].dt,'tz',None) is not None:
            df['timestamp']=df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        for c in ['open','close','volume','strike']:
            df[c]=pd.to_numeric(df[c],errors='coerce')
        df['option_type']=df['option_type'].astype(str).str.upper()
        df=df.dropna(subset=['timestamp','strike'])
    CACHE[key]=df
    return df

def spot_for(con,path,date):
    q="""
    SELECT timestamp, close AS spot_close
    FROM read_parquet(?)
    WHERE CAST(timestamp AS DATE)=CAST(? AS DATE)
    ORDER BY timestamp
    """
    df=con.execute(q,[path,date]).fetch_df()
    df['timestamp']=pd.to_datetime(df['timestamp'],errors='coerce')
    if getattr(df['timestamp'].dt,'tz',None) is not None:
        df['timestamp']=df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    df['spot_close']=pd.to_numeric(df['spot_close'],errors='coerce')
    return df.dropna(subset=['timestamp','spot_close'])

def signal_from(near,far,spot,start,end):
    n=near[(near.volume.fillna(0)>0)&near.close.gt(0)].copy()
    f=far[(far.volume.fillna(0)>0)&far.close.gt(0)].copy()
    def piv(df,p):
        x=df.pivot_table(index=['timestamp','strike'],columns='option_type',values=['close','volume','open'],aggfunc='last')
        if x.empty:return pd.DataFrame()
        x.columns=[f'{p}_{a}_{b}' for a,b in x.columns]
        return x.reset_index()
    a=piv(n,'near'); b=piv(f,'far')
    if a.empty or b.empty or 'timestamp' not in a.columns or 'timestamp' not in b.columns:return None
    x=a.merge(b,on=['timestamp','strike'],how='inner')
    if x.empty or 'timestamp' not in x.columns:return None
    if spot.empty or 'timestamp' not in spot.columns:return None
    x=pd.merge_asof(x.sort_values('timestamp'),spot.sort_values('timestamp'),on='timestamp',direction='backward',tolerance=pd.Timedelta(minutes=1))
    x=x[x.spot_close.notna()].copy()
    if x.empty:return None
    x['dist']=(x.strike-x.spot_close).abs()
    x['tm']=x.timestamp.dt.strftime('%H:%M')
    x=x[(x.tm>=start)&(x.tm<=end)].sort_values(['timestamp','dist','strike'])
    x=x.groupby('timestamp',as_index=False).head(1)
    req=['near_close_CE','near_close_PE','far_close_CE','far_close_PE','near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    if any(c not in x.columns for c in req): return None
    x=x.dropna(subset=req)
    x=x[(x[['near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']]>0).all(axis=1)]
    x=x[(x[['near_close_CE','near_close_PE','far_close_CE','far_close_PE']]>0).all(axis=1)]
    if x.empty:return None
    x['cbr']=(x.far_close_CE/x.near_close_CE)/(x.far_close_PE/x.near_close_PE)
    hit=x.loc[x.cbr<=1.2].sort_values('timestamp').head(1)
    if hit.empty:return None
    h=hit.iloc[0]
    return {'signal_timestamp':h.timestamp,'strike':float(h.strike),'cbr':float(h.cbr)}

def next_fill(near,far,strike,ts):
    n=near[(near.strike.eq(strike))&(near.volume.fillna(0)>0)].copy()
    f=far[(far.strike.eq(strike))&(far.volume.fillna(0)>0)].copy()
    def piv(df,p):
        x=df.pivot_table(index='timestamp',columns='option_type',values='open',aggfunc='last')
        return x.rename(columns={'CE':p+'_CE','PE':p+'_PE'}).reset_index() if not x.empty else pd.DataFrame()
    x=piv(n,'near').merge(piv(f,'far'),on='timestamp',how='inner')
    x=x[x.timestamp>pd.Timestamp(ts)].sort_values('timestamp')
    req=['near_CE','near_PE','far_CE','far_PE']
    x=x.dropna(subset=req)
    if x.empty:return None
    h=x.iloc[0]
    return {'fill_timestamp':h.timestamp,'entry_near_ce':float(h.near_CE),'entry_near_pe':float(h.near_PE),'entry_far_ce':float(h.far_CE),'entry_far_pe':float(h.far_PE)}

def exits(near,far,strike):
    def last(df):
        x=df[(df.strike.eq(strike))&(df.volume.fillna(0)>0)&df.close.gt(0)].copy()
        if x.empty:return None
        p=x.pivot_table(index='timestamp',columns='option_type',values='close',aggfunc='last')
        if not {'CE','PE'}.issubset(p.columns):return None
        h=p.sort_index().dropna().iloc[-1]
        return {'ce':float(h.CE),'pe':float(h.PE)}
    n=last(near); f=last(far)
    if n is None or f is None:return None
    return {'exit_near_ce':n['ce'],'exit_near_pe':n['pe'],'exit_far_ce':f['ce'],'exit_far_pe':f['pe']}

def main():
    con=duckdb.connect()
    con.execute("SET TimeZone='Asia/Kolkata'")
    manifest=pd.read_csv(MANIFEST)
    pmap=path_map(manifest)
    idx_path=index_url()
    cycles=pd.read_csv(OOS); cycles=cycles[cycles.status.eq('EXECUTABLE')].copy()
    for c in ['entry_date','near_expiry','far_expiry']:
        cycles[c]=pd.to_datetime(cycles[c]).dt.strftime('%Y-%m-%d')
    rows=[]
    for c in cycles.to_dict('records'):
        ed,ne,fe=c['entry_date'],c['near_expiry'],c['far_expiry']
        base={**c,'status':'ANALYZED'}
        if ne not in pmap or fe not in pmap:
            rows.append({**c,'status':'SOURCE_GAP'});continue
        try:
            near_e=query_date(con,pmap[ne],ed); far_e=query_date(con,pmap[fe],ed)
            near_x=query_date(con,pmap[ne],ne); far_x=query_date(con,pmap[fe],ne)
            spot=spot_for(con,idx_path,ed)
            for arm,cut in [('fixed','09:15'),('event','15:30')]:
                sig=signal_from(near_e,far_e,spot,'09:15',cut)
                base[f'{arm}_status']='NO_TRIGGER'
                if sig is None: continue
                fl=next_fill(near_e,far_e,sig['strike'],sig['signal_timestamp'])
                if fl is None: base[f'{arm}_status']='NO_FILL';continue
                ex=exits(near_x,far_x,sig['strike'])
                if ex is None: base[f'{arm}_status']='NO_EXIT';continue
                pts=((ex['exit_near_pe']-fl['entry_near_pe'])-(ex['exit_near_ce']-fl['entry_near_ce'])+(ex['exit_far_ce']-fl['entry_far_ce'])-(ex['exit_far_pe']-fl['entry_far_pe']))
                base.update({
                    f'{arm}_status':'EXECUTABLE',
                    f'{arm}_signal_timestamp':str(sig['signal_timestamp']),
                    f'{arm}_strike':sig['strike'],
                    f'{arm}_cbr':sig['cbr'],
                    f'{arm}_fill_timestamp':str(fl['fill_timestamp']),
                    f'{arm}_entry_near_ce':fl['entry_near_ce'],
                    f'{arm}_entry_near_pe':fl['entry_near_pe'],
                    f'{arm}_entry_far_ce':fl['entry_far_ce'],
                    f'{arm}_entry_far_pe':fl['entry_far_pe'],
                    f'{arm}_exit_near_ce':ex['exit_near_ce'],
                    f'{arm}_exit_near_pe':ex['exit_near_pe'],
                    f'{arm}_exit_far_ce':ex['exit_far_ce'],
                    f'{arm}_exit_far_pe':ex['exit_far_pe'],
                    f'{arm}_pnl_points':float(pts),
                    f'{arm}_pnl_inr':float(pts*float(c['lot_near'])),
                    f'{arm}_delay_minutes':(pd.Timestamp(fl['fill_timestamp'])-pd.Timestamp(ed+' 09:15:00')).total_seconds()/60
                })
            rows.append(base)
        except Exception as e:
            rows.append({**c,'status':'ERROR','reason':type(e).__name__+':'+str(e)[:200]})
    out=pd.DataFrame(rows);out.to_csv(OUT,index=False)
    cost=[]
    for arm in ['fixed','event']:
        sub=out[out[f'{arm}_status'].eq('EXECUTABLE')].copy()
        for slip in [0,0.5,1,2]:
            n=0; net_total=0.0
            for _,r in sub.iterrows():
                rr=pd.Series({
                    'entry_date':r.entry_date,'near_expiry':r.near_expiry,'lot_near':r.lot_near,'lot_far':r.lot_far,
                    'entry_near_pe':r[f'{arm}_entry_near_pe'],'entry_near_ce':r[f'{arm}_entry_near_ce'],
                    'entry_far_ce':r[f'{arm}_entry_far_ce'],'entry_far_pe':r[f'{arm}_entry_far_pe'],
                    'exit_near_pe':r[f'{arm}_exit_near_pe'],'exit_near_ce':r[f'{arm}_exit_near_ce'],
                    'exit_far_ce':r[f'{arm}_exit_far_ce'],'exit_far_pe':r[f'{arm}_exit_far_pe'],
                    'pnl_inr':r[f'{arm}_pnl_inr']})
                net_total += p8.net_cost(rr,slip,0.0005); n+=1
            p=sub[f'{arm}_pnl_inr'].astype(float).to_numpy() if len(sub) else np.array([])
            pos=p[p>0];neg=p[p<0]; curve=np.cumsum(p) if len(p) else np.array([]); dd=(curve-np.maximum.accumulate(curve)).min() if len(curve) else np.nan
            cost.append({'arm':arm,'n':n,'gross_pnl_inr':float(p.sum()) if len(p) else 0.0,'win_rate':float((p>0).mean()) if len(p) else np.nan,'profit_factor':float(pos.sum()/(-neg.sum())) if len(neg) else np.nan,'gross_max_drawdown_inr':abs(float(dd)) if len(p) else np.nan,'worst_trade_inr':float(p.min()) if len(p) else np.nan,'slippage_points':slip,'exchange_rate':0.0005,'net_pnl_inr':net_total})
    pd.DataFrame(cost).to_csv(COST,index=False)
    paired=out[out.fixed_status.eq('EXECUTABLE')&out.event_status.eq('EXECUTABLE')].copy()
    d=paired.event_pnl_inr-paired.fixed_pnl_inr if len(paired) else pd.Series(dtype=float)
    report=['# P9 OOS DuckDB Fixed 09:15 vs Event 15:30','',f'- OOS cycles: {len(out)}',f'- Source gaps: {int((out.status=="SOURCE_GAP").sum())}',f'- Fixed trades: {int((out.fixed_status=="EXECUTABLE").sum())}',f'- Event trades: {int((out.event_status=="EXECUTABLE").sum())}',f'- Paired dates: {len(paired)}']
    if len(paired):report += [f'- Mean event minus fixed: ₹{d.mean():,.2f}',f'- Median event minus fixed: ₹{d.median():,.2f}',f'- Event higher on {int((d>0).sum())}/{len(d)} paired dates']
    report += ['', 'Frozen CBR <= 1.20. 1-minute close -> next-minute open. Costs use the P8 modeled stress assumptions.']
    REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')
if __name__=='__main__':main()
