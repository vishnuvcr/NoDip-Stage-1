from __future__ import annotations

from pathlib import Path
import importlib.util
import duckdb
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OOS=ROOT/'reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv'
OUT=ROOT/'reports/nifty_calendar/P9_RISSIN_OOS_COMPARISON.csv'
COST=ROOT/'reports/nifty_calendar/P9_RISSIN_OOS_COSTS.csv'
REPORT=ROOT/'reports/nifty_calendar/P9_RISSIN_OOS_REPORT.md'

RISSIN_ROOT='upstox_intraday/NIFTY/'
HF_RISSIN='rissin/nse-options-intraday'
HF_TM='https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/resolve/main/index/NIFTY.parquet'

p8_path=ROOT/'scripts/p8_score.py'
spec=importlib.util.spec_from_file_location('p8',p8_path)
p8=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(p8)

def load_cycles():
    c=pd.read_csv(OOS)
    c=c[c.status.eq('EXECUTABLE')].copy()
    for col in ['entry_date','near_expiry','far_expiry']:
        c[col]=pd.to_datetime(c[col]).dt.strftime('%Y-%m-%d')
    return c

def normalize(df):
    if df.empty:return df
    df['timestamp']=pd.to_datetime(df['timestamp'],errors='coerce')
    if getattr(df['timestamp'].dt,'tz',None) is not None:
        df['timestamp']=df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    for col in ['open','close','volume','strike']:
        df[col]=pd.to_numeric(df[col],errors='coerce')
    df['expiry']=pd.to_datetime(df['expiry'],errors='coerce').dt.strftime('%Y-%m-%d')
    df['option_type']=df['option_type'].astype(str).str.upper()
    return df.dropna(subset=['timestamp','strike','expiry'])

def load_year(con,year,dates,expiries):
    if not dates or not expiries:return pd.DataFrame()
    path=f"hf://datasets/{HF_RISSIN}/upstox_intraday/NIFTY/NIFTY_{year}.parquet"
    date_sql=','.join("'" + d + "'" for d in sorted(dates))
    exp_sql=','.join("'" + e + "'" for e in sorted(expiries))
    q=f"""
    SELECT timestamp, date, expiry, strike, option_type, open, close, volume
    FROM read_parquet('{path}')
    WHERE date IN ({date_sql})
      AND expiry IN ({exp_sql})
      AND option_type IN ('CE','PE')
    """
    return normalize(con.execute(q).fetch_df())

def load_spot(con,dates):
    path='hf://datasets/thetrademarkk/india-index-options-1m/index/NIFTY.parquet'
    date_sql=','.join("'" + d + "'" for d in sorted(dates))
    q=f"""
    SELECT timestamp, close AS spot_close
    FROM read_parquet('{path}')
    WHERE CAST(timestamp AS DATE) IN ({date_sql})
    """
    df=con.execute(q).fetch_df()
    df['timestamp']=pd.to_datetime(df['timestamp'],errors='coerce')
    if getattr(df['timestamp'].dt,'tz',None) is not None:
        df['timestamp']=df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    df['spot_close']=pd.to_numeric(df['spot_close'],errors='coerce')
    return df.dropna(subset=['timestamp','spot_close'])
def panel(df,date,near,far):
    x=df[(df.date.eq(date))&(df.expiry.isin([near,far]))&(df.volume.fillna(0)>0)].copy()
    x=x[x.open.gt(0)&x.close.gt(0)]
    if x.empty:return pd.DataFrame()
    n=x[x.expiry.eq(near)]
    f=x[x.expiry.eq(far)]
    def p(z,pfx):
        y=z.pivot_table(index=['timestamp','strike'],columns='option_type',values=['open','close','volume'],aggfunc='last')
        if y.empty:return pd.DataFrame()
        y.columns=[f'{pfx}_{a}_{b}' for a,b in y.columns]
        return y.reset_index()
    a=p(n,'near'); b=p(f,'far')
    if a.empty or b.empty:return pd.DataFrame()
    z=a.merge(b,on=['timestamp','strike'],how='inner')
    req=['near_open_CE','near_open_PE','far_open_CE','far_open_PE',
         'near_close_CE','near_close_PE','far_close_CE','far_close_PE',
         'near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    return z.dropna(subset=req)

def choose_signal(z,spot,start='09:15',cutoff='15:30',fixed=False):
    if z.empty or spot.empty:return None
    x=pd.merge_asof(z.sort_values('timestamp'),spot.sort_values('timestamp'),
                    on='timestamp',direction='backward',tolerance=pd.Timedelta(minutes=1))
    x=x.dropna(subset=['spot_close']).copy()
    if x.empty:return None
    x['atm_distance_points']=(x['strike']-x['spot_close']).abs()
    x['atm_distance_pct']=x['atm_distance_points']/x['spot_close']*100
    x['time']=x.timestamp.dt.strftime('%H:%M')
    x=x[(x.time>=start)&(x.time<=cutoff)].sort_values(['timestamp','atm_distance_points','strike'])
    if fixed:
        x=x[x.time.eq('09:15')]
    if x.empty:return None
    x=x.groupby('timestamp',as_index=False).head(1).copy()
    x['cbr']=(x.far_close_CE/x.near_close_CE)/(x.far_close_PE/x.near_close_PE)
    hit=x.loc[x.cbr<=1.2].sort_values('timestamp').head(1)
    if hit.empty:return None
    h=hit.iloc[0]
    return {
        'signal_timestamp':h.timestamp,
        'strike':float(h.strike),
        'cbr':float(h.cbr),
        'spot_close':float(h.spot_close),
        'atm_distance_points':float(h.atm_distance_points),
        'atm_distance_pct':float(h.atm_distance_pct)
    }

def next_fill(z,sig):
    x=z[z.timestamp>pd.Timestamp(sig['signal_timestamp'])].copy().sort_values('timestamp')
    req=['near_open_CE','near_open_PE','far_open_CE','far_open_PE','near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    if x.empty:return None
    x=x.dropna(subset=req)
    x=x[(x[['near_open_CE','near_open_PE','far_open_CE','far_open_PE']]>0).all(axis=1)]
    x=x[(x[['near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']]>0).all(axis=1)]
    if x.empty:return None
    h=x.iloc[0]
    return {'fill_timestamp':h.timestamp,'entry_near_ce':float(h.near_open_CE),'entry_near_pe':float(h.near_open_PE),
            'entry_far_ce':float(h.far_open_CE),'entry_far_pe':float(h.far_open_PE)}

def exits(df,near,far,strike):
    x=df[(df.date.eq(near))&(df.expiry.isin([near,far]))&(df.strike.eq(strike))&(df.volume.fillna(0)>0)&df.close.gt(0)].copy()
    if x.empty:return None
    p=x.pivot_table(index='timestamp',columns='expiry',values=['close','volume'],aggfunc='last')
    vals={}
    # Use last common timestamp having all four positive close/volume values.
    rows=[]
    for ts,g in x.groupby('timestamp'):
        row={}
        ok=True
        for exp,opt,key in [(near,'PE','exit_near_pe'),(near,'CE','exit_near_ce'),(far,'CE','exit_far_ce'),(far,'PE','exit_far_pe')]:
            m=g[(g.expiry.eq(exp))&(g.option_type.eq(opt))]
            if len(m)!=1 or not (float(m.volume.iloc[0])>0 and float(m.close.iloc[0])>0):
                ok=False;break
            row[key]=float(m.close.iloc[0])
        if ok:
            row['exit_timestamp']=ts; rows.append(row)
    if not rows:return None
    return sorted(rows,key=lambda r:r['exit_timestamp'])[-1]

def trade_pnl(fill,ex,lot_near,lot_far):
    pts=(ex['exit_near_pe']-fill['entry_near_pe'])-(ex['exit_near_ce']-fill['entry_near_ce'])+(ex['exit_far_ce']-fill['entry_far_ce'])-(ex['exit_far_pe']-fill['entry_far_pe'])
    return float(pts),float((ex['exit_near_pe']-fill['entry_near_pe'])*lot_near+(fill['entry_near_ce']-ex['exit_near_ce'])*lot_near+(ex['exit_far_ce']-fill['entry_far_ce'])*lot_far+(fill['entry_far_pe']-ex['exit_far_pe'])*lot_far)

def main():
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=8")
    cycles=load_cycles().to_dict('records')
    entry_dates=set(c['entry_date'] for c in cycles)
    entry_exps=set(e for c in cycles for e in [c['near_expiry'],c['far_expiry']])
    exit_dates=set(c['near_expiry'] for c in cycles)
    exit_exps=entry_exps
    all_dates=entry_dates|exit_dates

    years={2025:[d for d in all_dates if d.startswith('2025')],2026:[d for d in all_dates if d.startswith('2026')]}
    exp_by_year={2025:[e for e in entry_exps if e.startswith('2025') or e.startswith('2026')],2026:[e for e in entry_exps if e.startswith('2026')]}
    raw_by_year={}
    for y in [2025,2026]:
        raw_by_year[y]=load_year(con,y,years[y],exp_by_year[y])

    spot=load_spot(con,all_dates)
    rows=[]
    for c in cycles:
        y=int(c['entry_date'][:4])
        raw_entry=raw_by_year.get(y,pd.DataFrame())
        raw_exit=raw_by_year.get(int(c['near_expiry'][:4]),pd.DataFrame())
        z=panel(raw_entry,c['entry_date'],c['near_expiry'],c['far_expiry'])
        base={**c,'status':'ANALYZED'}
        if z.empty:
            base['fixed_status']='NO_PANEL';base['event_status']='NO_PANEL';rows.append(base);continue
        sp=spot[spot.timestamp.dt.strftime('%Y-%m-%d').eq(c['entry_date'])][['timestamp','spot_close']]
        for arm,fixed,cut in [('fixed',True,'09:15'),('event',False,'15:30')]:
            sig=choose_signal(z,sp,'09:15',cut,fixed=fixed)
            base[f'{arm}_status']='NO_TRIGGER'
            if sig is None:continue
            fl=next_fill(z,sig)
            if fl is None:base[f'{arm}_status']='NO_FILL';continue
            ex=exits(raw_exit,c['near_expiry'],c['far_expiry'],sig['strike'])
            if ex is None:base[f'{arm}_status']='NO_EXIT';continue
            pts,inr=trade_pnl(fl,ex,float(c['lot_near']),float(c['lot_far']))
            base.update({
                f'{arm}_status':'EXECUTABLE',f'{arm}_signal_timestamp':str(sig['signal_timestamp']),f'{arm}_strike':sig['strike'],f'{arm}_cbr':sig['cbr'],
                f'{arm}_spot_close':sig['spot_close'],f'{arm}_atm_distance_points':sig['atm_distance_points'],f'{arm}_atm_distance_pct':sig['atm_distance_pct'],
                f'{arm}_fill_timestamp':str(fl['fill_timestamp']),f'{arm}_entry_near_ce':fl['entry_near_ce'],f'{arm}_entry_near_pe':fl['entry_near_pe'],f'{arm}_entry_far_ce':fl['entry_far_ce'],f'{arm}_entry_far_pe':fl['entry_far_pe'],
                f'{arm}_exit_near_ce':ex['exit_near_ce'],f'{arm}_exit_near_pe':ex['exit_near_pe'],f'{arm}_exit_far_ce':ex['exit_far_ce'],f'{arm}_exit_far_pe':ex['exit_far_pe'],
                f'{arm}_pnl_points':pts,f'{arm}_pnl_inr':inr,f'{arm}_delay_minutes':(pd.Timestamp(fl['fill_timestamp'])-pd.Timestamp(c['entry_date']+' 09:15:00')).total_seconds()/60
            })
        rows.append(base)

    out=pd.DataFrame(rows);out.to_csv(OUT,index=False)

    costs=[]
    for arm in ['fixed','event']:
        sub=out[out[f'{arm}_status'].eq('EXECUTABLE')].copy()
        for slip in [0,0.5,1,2]:
            net_total=0.0
            for _,r in sub.iterrows():
                rr=pd.Series({
                    'entry_date':r.entry_date,'near_expiry':r.near_expiry,'lot_near':r.lot_near,'lot_far':r.lot_far,
                    'entry_near_pe':r[f'{arm}_entry_near_pe'],'entry_near_ce':r[f'{arm}_entry_near_ce'],'entry_far_ce':r[f'{arm}_entry_far_ce'],'entry_far_pe':r[f'{arm}_entry_far_pe'],
                    'exit_near_pe':r[f'{arm}_exit_near_pe'],'exit_near_ce':r[f'{arm}_exit_near_ce'],'exit_far_ce':r[f'{arm}_exit_far_ce'],'exit_far_pe':r[f'{arm}_exit_far_pe'],'pnl_inr':r[f'{arm}_pnl_inr']})
                net_total += p8.net_cost(rr,slip,0.0005)
            p=sub[f'{arm}_pnl_inr'].astype(float).to_numpy() if len(sub) else np.array([])
            pos=p[p>0];neg=p[p<0];curve=np.cumsum(p) if len(p) else np.array([]);dd=(curve-np.maximum.accumulate(curve)).min() if len(p) else np.nan
            costs.append({'arm':arm,'n':len(p),'gross_pnl_inr':float(p.sum()) if len(p) else 0.0,'win_rate':float((p>0).mean()) if len(p) else np.nan,'profit_factor':float(pos.sum()/(-neg.sum())) if len(neg) else np.nan,'max_dd_inr':abs(float(dd)) if len(p) else np.nan,'worst_inr':float(p.min()) if len(p) else np.nan,'slippage_points':slip,'exchange_rate':0.0005,'net_pnl_inr':net_total})
    pd.DataFrame(costs).to_csv(COST,index=False)

    paired=out[out.fixed_status.eq('EXECUTABLE')&out.event_status.eq('EXECUTABLE')].copy()
    report=['# P9 Rissin OOS Fixed 09:15 vs Event 15:30','',f'- OOS cycles: {len(out)}',f'- No four-leg panel: {int((out.fixed_status=="NO_PANEL").sum())}',f'- Fixed trades: {int((out.fixed_status=="EXECUTABLE").sum())}',f'- Event trades: {int((out.event_status=="EXECUTABLE").sum())}',f'- Paired dates: {len(paired)}']
    if len(paired):
        d=paired.event_pnl_inr-paired.fixed_pnl_inr
        report += [f'- Mean event minus fixed: ₹{d.mean():,.2f}',f'- Median event minus fixed: ₹{d.median():,.2f}',f'- Event higher on {int((d>0).sum())}/{len(d)} paired dates']
    e=out[out.event_status.eq('EXECUTABLE')]
    if len(e):
        report += [f'- Event median ATM distance: {e.event_atm_distance_points.median():.1f} points ({e.event_atm_distance_pct.median():.3f}%)',f'- Event median signal time: {pd.to_datetime(e.event_signal_timestamp).dt.strftime("%H:%M").sort_values().iloc[len(e)//2]}']
    report += ['', 'Option source: rissin/nse-options-intraday Upstox 1-minute track; spot source: thetrademarkk NIFTY index 1-minute series.', 'Frozen CBR <= 1.20. Signal on minute close, fill next available minute open.']
    REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')

if __name__=='__main__':main()
