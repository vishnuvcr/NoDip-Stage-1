from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import math
import pandas as pd

MANIFEST=Path('reports/nifty_calendar/P9_HF_FETCH_MANIFEST.csv')
STRICT=Path('reports/nifty_calendar/STRICT_TRADE_LEVEL_RESULTS_2022_2024.csv')
OOS=Path('reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv')
OUT=Path('reports/nifty_calendar/P9_EVENT_TIMING_LEDGER.csv')
SUMMARY=Path('reports/nifty_calendar/P9_EVENT_TIMING_REPORT.md')

def load_cycles():
    s=pd.read_csv(STRICT)
    s['sample']='2022_2024'
    s=s[['entry_date','near_expiry','far_expiry','strike','lot_near','lot_far','sample']].copy()
    o=pd.read_csv(OOS)
    o=o[o['status'].eq('EXECUTABLE')].copy()
    o['sample']='2025_onward'
    o=o[['entry_date','near_expiry','far_expiry','strike','lot_near','lot_far','sample']].copy()
    df=pd.concat([s,o],ignore_index=True).drop_duplicates(subset=['entry_date','near_expiry','far_expiry','sample']).reset_index(drop=True)
    for c in ['entry_date','near_expiry','far_expiry']:
        df[c]=pd.to_datetime(df[c]).dt.strftime('%Y-%m-%d')
    return df

def path_map(manifest):
    m=manifest[manifest['status'].eq('DOWNLOADED')].copy()
    return {Path(row.file).stem:row.local_path for _,row in m[m['kind'].eq('option')].iterrows()}

def prep_option(path, target_dates):
    cols=['timestamp','open','high','low','close','volume','strike','option_type','expiry']
    df=pd.read_parquet(path,columns=cols)
    ts=pd.to_datetime(df['timestamp'],errors='coerce')
    df['timestamp']=ts
    df['date']=ts.dt.strftime('%Y-%m-%d')
    df=df[df['date'].isin(target_dates)].copy()
    df['option_type']=df['option_type'].astype(str).str.upper()
    df['strike']=pd.to_numeric(df['strike'],errors='coerce')
    for c in ['open','high','low','close','volume']:
        df[c]=pd.to_numeric(df[c],errors='coerce')
    df=df[df['option_type'].isin(['CE','PE']) & df['strike'].notna()].copy()
    return df[['timestamp','date','strike','option_type','open','high','low','close','volume']]

def pivot_four(near,far,date):
    n=near[near['date'].eq(date)].copy(); f=far[far['date'].eq(date)].copy()
    n=n[(n['volume'].fillna(0)>0) & n['close'].notna() & (n['close']>0)].copy()
    f=f[(f['volume'].fillna(0)>0) & f['close'].notna() & (f['close']>0)].copy()
    def p(df,pfx,price='close'):
        z=df.pivot_table(index=['timestamp','strike'],columns='option_type',values=[price,'volume'],aggfunc='last')
        if z.empty:return z
        z.columns=[f'{pfx}_{a}_{b}' for a,b in z.columns]
        return z.reset_index()
    a=p(n,'near'); b=p(f,'far')
    if a.empty or b.empty:return pd.DataFrame()
    x=a.merge(b,on=['timestamp','strike'],how='inner')
    return x

def add_spot(x, spot):
    return pd.merge_asof(x.sort_values('timestamp'),spot.sort_values('timestamp'),on='timestamp',direction='nearest',tolerance=pd.Timedelta('1min'))

def first_signal(panel, spot, entry_date, cutoff='15:30'):
    if panel.empty:return None
    x=add_spot(panel,spot)
    if 'spot_close' not in x.columns:return None
    x['abs_atm']=(x['strike']-x['spot_close']).abs()
    # Pick the closest common strike for each timestamp, using only observations at that timestamp.
    x=x[x['spot_close'].notna()].copy()
    if x.empty:return None
    x['time']=x['timestamp'].dt.strftime('%H:%M')
    x=x[(x['time']>='09:15')&(x['time']<=cutoff)].copy()
    x=x.sort_values(['timestamp','abs_atm','strike'])
    chosen=x.groupby('timestamp',as_index=False).head(1).copy()
    # Required columns are prices and positive volume in all four legs.
    req=['near_close_CE','near_close_PE','far_close_CE','far_close_PE','near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    if any(c not in chosen.columns for c in req):return None
    q=chosen.copy()
    q=q[(q[req].notna()).all(axis=1)]
    q=q[(q[['near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']]>0).all(axis=1)]
    q=q[(q[['near_close_CE','near_close_PE','far_close_CE','far_close_PE']]>0).all(axis=1)]
    if q.empty:return None
    q['call_ratio']=q['far_close_CE']/q['near_close_CE']
    q['put_ratio']=q['far_close_PE']/q['near_close_PE']
    q['cbr']=q['call_ratio']/q['put_ratio']
    q=q.sort_values('timestamp')
    hit=q[q['cbr']<=1.20].head(1)
    if hit.empty:return None
    h=hit.iloc[0]
    return {'signal_timestamp':str(h['timestamp']),'signal_strike':float(h['strike']),'cbr':float(h['cbr']),'spot':float(h['spot_close'])}

def next_fill(near,far,date,strike,signal_ts):
    target=pd.Timestamp(signal_ts)
    n=near[(near['date'].eq(date))&(near['strike'].eq(strike)) & (near['volume'].fillna(0)>0)].copy()
    f=far[(far['date'].eq(date))&(far['strike'].eq(strike)) & (far['volume'].fillna(0)>0)].copy()
    if n.empty or f.empty:return None
    def p(df,pfx):
        z=df.pivot_table(index='timestamp',columns='option_type',values='open',aggfunc='last')
        z=z.rename(columns={'CE':f'{pfx}_CE','PE':f'{pfx}_PE'}).reset_index()
        return z
    x=p(n,'near').merge(p(f,'far'),on='timestamp',how='inner')
    x=x[x['timestamp']>target].sort_values('timestamp')
    req=['near_CE','near_PE','far_CE','far_PE']
    x=x[x[req].notna().all(axis=1)]
    if x.empty:return None
    h=x.iloc[0]
    return {'fill_timestamp':str(h['timestamp']),'entry_near_ce':float(h['near_CE']),'entry_near_pe':float(h['near_PE']),'entry_far_ce':float(h['far_CE']),'entry_far_pe':float(h['far_PE'])}

def exit_prices(path_map, near_expiry, far_expiry, strike):
    def last(path):
        cols=['timestamp','close','volume','strike','option_type']
        df=pd.read_parquet(path,columns=cols)
        ts=pd.to_datetime(df['timestamp']); date=ts.dt.strftime('%Y-%m-%d')
        df=df[(date==near_expiry)&(df['strike']==strike)&(df['volume'].fillna(0)>0)&(df['close'].notna())&(df['close']>0)].copy()
        if df.empty:return None
        piv=df.pivot_table(index='timestamp',columns='option_type',values='close',aggfunc='last')
        if not {'CE','PE'}.issubset(set(piv.columns)):return None
        h=piv.sort_index().dropna().iloc[-1]
        return {'close_ce':float(h['CE']),'close_pe':float(h['PE'])}
    n=last(path_map[near_expiry]); f=last(path_map[far_expiry])
    if n is None or f is None:return None
    return {'exit_timestamp_near':near_expiry,'exit_near_ce':n['close_ce'],'exit_near_pe':n['close_pe'],'exit_far_ce':f['close_ce'],'exit_far_pe':f['close_pe']}

def pnl(e,x,exitp):
    pts=(exitp['exit_near_pe']-e['entry_near_pe'])-(exitp['exit_near_ce']-e['entry_near_ce'])+(exitp['exit_far_ce']-e['entry_far_ce'])-(exitp['exit_far_pe']-e['entry_far_pe'])
    return float(pts)

def main():
    manifest=pd.read_csv(MANIFEST)
    pmap=path_map(manifest)
    cycles=load_cycles()
    idx_path=manifest[(manifest['kind']=='index')&(manifest['status']=='DOWNLOADED')]['local_path'].iloc[0]
    idx=pd.read_parquet(idx_path,columns=['timestamp','close'])
    idx['timestamp']=pd.to_datetime(idx['timestamp']); idx=idx.rename(columns={'close':'spot_close'})
    rows=[]
    for i,c in cycles.iterrows():
        ne,fe=c.near_expiry,c.far_expiry
        if ne not in pmap or fe not in pmap:
            rows.append({**c.to_dict(),'status':'SOURCE_GAP','reason':'missing_near_or_far_expiry_file'}); continue
        try:
            n=prep_option(pmap[ne],[c.entry_date,ne]); f=prep_option(pmap[fe],[c.entry_date,ne])
            panel=pivot_four(n,f,c.entry_date)
            if panel.empty:
                rows.append({**c.to_dict(),'status':'NO_FOUR_LEG_PANEL','reason':'no_same_timestamp_common_strike'}); continue
            spot=idx[idx['timestamp'].dt.strftime('%Y-%m-%d').eq(c.entry_date)][['timestamp','spot_close']].copy()
            sig=first_signal(panel,spot,c.entry_date,'15:30')
            if sig is None:
                rows.append({**c.to_dict(),'status':'NO_TRIGGER','reason':'CBR_never_below_1_20_or_no_executable_common_ATM'}); continue
            fill=next_fill(n,f,c.entry_date,sig['signal_strike'],sig['signal_timestamp'])
            if fill is None:
                rows.append({**c.to_dict(),**sig,'status':'SIGNAL_NO_FILL','reason':'no_next_minute_four_leg_fill'}); continue
            ex=exit_prices(pmap,ne,fe,sig['signal_strike'])
            if ex is None:
                rows.append({**c.to_dict(),**sig,**fill,'status':'FILL_NO_EXIT','reason':'missing_near_expiry_exit_fill'}); continue
            points=pnl(fill,{'status':1},ex)
            lot=float(c.lot_near)
            rows.append({**c.to_dict(),**sig,**fill,**ex,'status':'EXECUTABLE','pnl_points':points,'pnl_inr':points*lot,'delay_minutes':(pd.Timestamp(fill['fill_timestamp'])-pd.Timestamp(c.entry_date+' 09:15:00')).total_seconds()/60.0})
        except Exception as e:
            rows.append({**c.to_dict(),'status':'ERROR','reason':type(e).__name__+':'+str(e)[:200]})
    out=pd.DataFrame(rows)
    out.to_csv(OUT,index=False)
    execd=out[out['status'].eq('EXECUTABLE')].copy()
    summary=[
        '# P9 Event-Driven Timing Scan — First HF Candidate',
        '',
        f'- Input cycles: {len(out)}',
        f'- Executable event-driven trades: {len(execd)}',
        f'- Source gaps: {int((out.status=="SOURCE_GAP").sum())}',
        f'- No four-leg panels: {int((out.status=="NO_FOUR_LEG_PANEL").sum())}',
        f'- No CBR trigger: {int((out.status=="NO_TRIGGER").sum())}',
        f'- Signal but no next-minute fill: {int((out.status=="SIGNAL_NO_FILL").sum())}',
        f'- Fill but no exit: {int((out.status=="FILL_NO_EXIT").sum())}',
        f'- Data/scan errors: {int((out.status=="ERROR").sum())}',
        '',
    ]
    if len(execd):
        wins=int((execd['pnl_inr']>0).sum()); losses=int((execd['pnl_inr']<0).sum())
        gross=float(execd['pnl_inr'].sum()); winrate=100*wins/len(execd)
        pos=execd.loc[execd['pnl_inr']>0,'pnl_inr'].sum(); neg=-execd.loc[execd['pnl_inr']<0,'pnl_inr'].sum()
        pf=(pos/neg) if neg else math.inf
        summary += [f'- Gross event-driven P&L: ₹{gross:,.2f}',f'- Win rate: {winrate:.2f}%',f'- Profit factor: {pf:.3f}',f'- Median entry delay from 09:15: {execd["delay_minutes"].median():.1f} minutes',f'- First qualifying signal time (median): {pd.to_datetime(execd["signal_timestamp"]).dt.strftime("%H:%M").sort_values().iloc[len(execd)//2]}']
    summary += ['', 'This is a first-source research scan using 1-minute OHLC and next-minute open execution. It is not yet the final P9 temporal validation or bid/ask execution validation.']
    SUMMARY.write_text('\n'.join(summary)+'\n',encoding='utf-8')

if __name__=='__main__': main()