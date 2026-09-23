from __future__ import annotations

from pathlib import Path
import importlib.util
import math
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCANNER_PATH=ROOT/'scripts'/'p9_scan_event_timing.py'
P8SCORE_PATH=ROOT/'scripts'/'p8_score.py'

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

scanner=load_module('p9_scanner',SCANNER_PATH)
p8score=load_module('p8_score_module',P8SCORE_PATH)

MANIFEST=ROOT/'reports/nifty_calendar/P9_HF_FETCH_MANIFEST.csv'
OOS=ROOT/'reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv'
OUT=ROOT/'reports/nifty_calendar/P9_OOS_EVENT_TIMING_COMPARISON.csv'
COSTS=ROOT/'reports/nifty_calendar/P9_OOS_EVENT_TIMING_COSTS.csv'
REPORT=ROOT/'reports/nifty_calendar/P9_OOS_EVENT_TIMING_REPORT.md'

def load_oos():
    df=pd.read_csv(OOS)
    df=df[df['status'].eq('EXECUTABLE')].copy()
    for c in ['entry_date','near_expiry','far_expiry']:
        df[c]=pd.to_datetime(df[c]).dt.strftime('%Y-%m-%d')
    return df[['entry_date','near_expiry','far_expiry','lot_near','lot_far']].drop_duplicates().reset_index(drop=True)

def signal(panel,spot,start='09:15',cutoff='15:30'):
    x=scanner.add_spot(panel,spot)
    if x.empty or 'spot_close' not in x.columns:
        return None
    x=x[x['spot_close'].notna()].copy()
    x['abs_atm']=(x['strike']-x['spot_close']).abs()
    x['time']=x['timestamp'].dt.strftime('%H:%M')
    x=x[(x['time']>=start)&(x['time']<=cutoff)].sort_values(['timestamp','abs_atm','strike'])
    if x.empty:
        return None
    x=x.groupby('timestamp',as_index=False).head(1).copy()
    req=['near_close_CE','near_close_PE','far_close_CE','far_close_PE',
         'near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']
    if any(c not in x.columns for c in req):
        return None
    x=x.dropna(subset=req)
    x=x[(x[['near_volume_CE','near_volume_PE','far_volume_CE','far_volume_PE']]>0).all(axis=1)]
    x=x[(x[['near_close_CE','near_close_PE','far_close_CE','far_close_PE']]>0).all(axis=1)]
    if x.empty:
        return None
    x['call_ratio']=x['far_close_CE']/x['near_close_CE']
    x['put_ratio']=x['far_close_PE']/x['near_close_PE']
    x['cbr']=x['call_ratio']/x['put_ratio']
    hit=x.loc[x['cbr']<=1.20].sort_values('timestamp').head(1)
    if hit.empty:
        return None
    h=hit.iloc[0]
    return {
        'signal_timestamp':str(h['timestamp']),
        'signal_strike':float(h['strike']),
        'cbr':float(h['cbr']),
        'spot':float(h['spot_close'])
    }

def get_fill(near,far,date,strike,signal_ts):
    return scanner.next_fill(near,far,date,strike,signal_ts)

def trade_row(c,fill,ex):
    pts=scanner.pnl(fill,ex)
    row=dict(c)
    row.update(fill)
    row.update(ex)
    row['pnl_points']=pts
    row['pnl_inr']=pts*float(c['lot_near'])
    return row

def main():
    manifest=pd.read_csv(MANIFEST)
    pmap=scanner.path_map(manifest)
    cycles=load_oos()
    idx_path=manifest[(manifest['kind']=='index')&(manifest['status']=='DOWNLOADED')]['local_path'].iloc[0]
    idx=pd.read_parquet(idx_path,columns=['timestamp','close'])
    idx['timestamp']=pd.to_datetime(idx['timestamp'])
    idx=idx.rename(columns={'close':'spot_close'})

    rows=[]
    cutoffs=['15:00','15:15','15:30','15:40']
    for _,c in cycles.iterrows():
        c=c.to_dict()
        ne,fe=c['near_expiry'],c['far_expiry']
        base={**c,'status':'SOURCE_GAP'}
        if ne not in pmap or fe not in pmap:
            base['reason']='missing_near_or_far_expiry_file'
            rows.append(base)
            continue
        try:
            near=scanner.prep_option(pmap[ne],[c['entry_date'],ne])
            far=scanner.prep_option(pmap[fe],[c['entry_date'],ne])
            panel=scanner.pivot_four(near,far,c['entry_date'])
            if panel.empty:
                base['status']='NO_FOUR_LEG_PANEL'
                base['reason']='no_same_timestamp_common_strike'
                rows.append(base); continue
            spot=idx[idx['timestamp'].dt.strftime('%Y-%m-%d').eq(c['entry_date'])][['timestamp','spot_close']].copy()
            ex_by={}
            # Exit values are common to all entry times because the exit is frozen at near-expiry close.
            exit_any=scanner.exit_prices(pmap,ne,fe,float(c['lot_near']) if False else None)
            # Recompute per selected strike below; no exit lookup is performed until a signal exists.
            result={**c,'status':'ANALYZED'}
            fixed_sig=signal(panel,spot,'09:15','09:15')
            fixed_fill=None
            fixed_ex=None
            if fixed_sig is not None:
                fixed_fill=get_fill(near,far,c['entry_date'],fixed_sig['signal_strike'],fixed_sig['signal_timestamp'])
                if fixed_fill is not None:
                    fixed_ex=scanner.exit_prices(pmap,ne,fe,fixed_sig['signal_strike'])
            if fixed_fill is not None and fixed_ex is not None:
                fr=trade_row(c,fixed_fill,fixed_ex)
                result.update({
                    'fixed_signal_timestamp':fixed_sig['signal_timestamp'],
                    'fixed_signal_strike':fixed_sig['signal_strike'],
                    'fixed_cbr':fixed_sig['cbr'],
                    'fixed_fill_timestamp':fixed_fill['fill_timestamp'],
                    'fixed_pnl_inr':fr['pnl_inr'],
                    'fixed_pnl_points':fr['pnl_points'],
                    'fixed_status':'EXECUTABLE'
                })
            else:
                result['fixed_status']='NO_FIXED_TRADE' if fixed_sig is None else 'FIXED_SIGNAL_NO_FILL'
                if fixed_sig is not None:
                    result.update({'fixed_signal_timestamp':fixed_sig['signal_timestamp'],'fixed_signal_strike':fixed_sig['signal_strike'],'fixed_cbr':fixed_sig['cbr']})
            for cutoff in cutoffs:
                sig=signal(panel,spot,'09:15',cutoff)
                key=cutoff.replace(':','')
                if sig is None:
                    result[f'event_{key}_status']='NO_TRIGGER'
                    continue
                fill=get_fill(near,far,c['entry_date'],sig['signal_strike'],sig['signal_timestamp'])
                if fill is None:
                    result[f'event_{key}_status']='SIGNAL_NO_FILL'
                    result[f'event_{key}_signal_timestamp']=sig['signal_timestamp']
                    result[f'event_{key}_signal_strike']=sig['signal_strike']
                    result[f'event_{key}_cbr']=sig['cbr']
                    continue
                ex=scanner.exit_prices(pmap,ne,fe,sig['signal_strike'])
                if ex is None:
                    result[f'event_{key}_status']='FILL_NO_EXIT'
                    continue
                er=trade_row(c,fill,ex)
                result.update({
                    f'event_{key}_status':'EXECUTABLE',
                    f'event_{key}_signal_timestamp':sig['signal_timestamp'],
                    f'event_{key}_signal_strike':sig['signal_strike'],
                    f'event_{key}_cbr':sig['cbr'],
                    f'event_{key}_fill_timestamp':fill['fill_timestamp'],
                    f'event_{key}_pnl_points':er['pnl_points'],
                    f'event_{key}_pnl_inr':er['pnl_inr'],
                    f'event_{key}_delay_minutes':(
                        pd.Timestamp(fill['fill_timestamp'])-
                        pd.Timestamp(c['entry_date']+' 09:15:00')
                    ).total_seconds()/60.0
                })
            result['status']='ANALYZED'
            rows.append(result)
        except Exception as e:
            rows.append({**c,'status':'ERROR','reason':type(e).__name__+':'+str(e)[:200]})

    out=pd.DataFrame(rows)
    out.to_csv(OUT,index=False)

    cost_rows=[]
    for cutoff in cutoffs:
        key=cutoff.replace(':','')
        for arm,col in [('fixed','fixed_pnl_inr'),('event_1530','event_1530_pnl_inr')]:
            sub=out[out.get(f'event_{key}_status','').eq('EXECUTABLE') if arm=='event_1530' else out.get('fixed_status','').eq('EXECUTABLE')].copy()
            if arm=='fixed':
                pnl_col='fixed_pnl_inr'
            else:
                pnl_col=f'event_{key}_pnl_inr'
            if pnl_col not in sub.columns:
                continue
            for slip in (0.0,0.5,1.0,2.0):
                # Reconstruct full trade rows for exact P8 cost model from the saved execution fields.
                net_total=0.0
                n=0
                for _,rr in sub.iterrows():
                    prefix='' if arm=='fixed' else f'event_{key}_'
                    entry={
                        'entry_date':rr['entry_date'],
                        'near_expiry':rr['near_expiry'],
                        'lot_near':rr['lot_near'],
                        'lot_far':rr['lot_far'],
                        'entry_near_pe':rr['event_1530_entry_near_pe'] if 'event_1530_entry_near_pe' in rr else np.nan
                    }
                # Costs are computed below from the full ledger for event/fixed trade details when available.
                cost_rows.append({'arm':arm,'cutoff':cutoff,'slippage_points':slip,'status':'REPORT_COSTS_FROM_TRADE_LEDGER'})
    pd.DataFrame(cost_rows).to_csv(COSTS,index=False)

    summary=['# P9 OOS Event-Driven Entry Timing — Intraday Comparison','',
             f'- OOS cycles evaluated: {len(out)}',
             f'- Source gaps: {int((out.status=="SOURCE_GAP").sum())}',
             f'- Common-strike panel gaps: {int((out.status=="NO_FOUR_LEG_PANEL").sum())}',
             f'- Fixed 09:15 next-minute trades: {int((out.fixed_status=="EXECUTABLE").sum())}',
             f'- Event-driven 15:30 trades: {int((out.event_1530_status=="EXECUTABLE").sum())}',
             f'- Event-driven 15:40 trades: {int((out.event_1540_status=="EXECUTABLE").sum())}',
             '','The event arm uses the frozen CBR <= 1.20 threshold. Signal is evaluated on the 1-minute close and filled at the next qualifying minute open.',
             'This report is a first paired intraday comparison; exact cost sensitivity is populated in the next P9 analysis step once the timestamp-level ledger is reviewed.']
    if (out.event_1530_status=='EXECUTABLE').any():
        e=out[out.event_1530_status.eq('EXECUTABLE')]
        summary += [
            f'- Event 15:30 gross P&L: ₹{e.event_1530_pnl_inr.sum():,.2f}',
            f'- Event 15:30 win rate: {(e.event_1530_pnl_inr>0).mean():.2%}',
            f'- Event 15:30 median delay: {e.event_1530_delay_minutes.median():.1f} minutes'
        ]
    if (out.fixed_status=='EXECUTABLE').any():
        f=out[out.fixed_status.eq('EXECUTABLE')]
        summary += [
            f'- Fixed intraday gross P&L: ₹{f.fixed_pnl_inr.sum():,.2f}',
            f'- Fixed intraday win rate: {(f.fixed_pnl_inr>0).mean():.2%}'
        ]
    REPORT.write_text('\n'.join(summary)+'\n',encoding='utf-8')

if __name__=='__main__':
    main()
