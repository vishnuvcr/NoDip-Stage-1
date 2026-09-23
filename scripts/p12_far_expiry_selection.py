from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
YEARS = [2022, 2023, 2024, 2025, 2026]
HORIZONS = [1, 2, 3, 4]
LABELS = {1:'F+1',2:'F+2',3:'F+3',4:'F+4'}
HEADERS = {'User-Agent':'Mozilla/5.0 (compatible; NoDip research bot)','Accept':'*/*'}
ATMQC = 25.0

rec_spec = importlib.util.spec_from_file_location('rec', ROOT/'scripts/reconcile_rejections_nse.py')
rec = importlib.util.module_from_spec(rec_spec); assert rec_spec.loader is not None; rec_spec.loader.exec_module(rec)

OUT_LEDGER = ROOT/'reports/nifty_calendar/P12_FAR_EXPIRY_LEDGER.csv'
OUT_SUMMARY = ROOT/'reports/nifty_calendar/P12_FAR_EXPIRY_SUMMARY.csv'
OUT_COSTS = ROOT/'reports/nifty_calendar/P12_FAR_EXPIRY_COST_SENSITIVITY.csv'
OUT_SELECTION = ROOT/'reports/nifty_calendar/P12_ADAPTIVE_SELECTION.csv'
OUT_REPORT = ROOT/'reports/nifty_calendar/P12_FAR_EXPIRY_SELECTION_REPORT.md'
OUT_CONCLUSION = ROOT/'reports/nifty_calendar/P12_FINAL_RESEARCH_CONCLUSION.md'
OUT_STATUS = ROOT/'docs/nifty_calendar/PHASE_STATUS.md'

def load_year(path_cache: Path, year: int) -> pd.DataFrame:
    path = hf_hub_download(
        repo_id='rissin/nse-options-intraday',
        filename=f'historical_daily/NIFTY/NIFTY_{year}.parquet',
        repo_type='dataset',
        cache_dir=str(path_cache),
    )
    df = pd.read_parquet(path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    df['expiry'] = pd.to_datetime(df['expiry'], errors='coerce').dt.normalize()
    df['strike'] = pd.to_numeric(df['strike'], errors='coerce')
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    df['underlying'] = df['underlying'].astype(str).str.upper()
    df['option_type'] = df['option_type'].astype(str).str.upper()
    df['granularity'] = df['granularity'].astype(str).str.lower()
    return df[(df['underlying']=='NIFTY') & (df['granularity']=='1d')].copy()

def spot_map() -> dict[str,float]:
    s = requests.Session()
    start = pd.Timestamp('2022-01-01', tz='Asia/Kolkata')
    end = pd.Timestamp('2027-01-01', tz='Asia/Kolkata')
    p1 = int(start.tz_convert('UTC').timestamp())
    p2 = int(end.tz_convert('UTC').timestamp())
    r = s.get('https://query1.finance.yahoo.com/v8/finance/chart/^NSEI', params={'period1':p1,'period2':p2,'interval':'1d','events':'history'}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    js = r.json()['chart']['result'][0]
    out={}
    for t,v in zip(js['timestamp'], js['indicators']['quote'][0]['open']):
        if v is None: continue
        d=pd.to_datetime(t,unit='s',utc=True).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
        out[d]=float(v)
    return out

def make_cycles(all_dates: list[pd.Timestamp], all_expiries: list[pd.Timestamp]) -> pd.DataFrame:
    td = sorted(set(all_dates)); exps = sorted(set(all_expiries)); rows=[]
    for i in range(1, len(exps)-4):
        prev, near = exps[i-1], exps[i]
        fars = exps[i+1:i+5]
        if len(fars) < 4: continue
        entry_candidates=[d for d in td if d > prev and d < near]
        if not entry_candidates: continue
        entry=entry_candidates[0]
        rows.append({
            'cycle_id': f'C_{entry:%Y%m%d}',
            'sample': 'DEVELOPMENT' if entry.year <= 2024 else 'OOS',
            'previous_expiry': prev.strftime('%Y-%m-%d'),
            'near_expiry': near.strftime('%Y-%m-%d'),
            'entry_date': entry.strftime('%Y-%m-%d'),
            'f1_expiry': fars[0].strftime('%Y-%m-%d'),
            'f2_expiry': fars[1].strftime('%Y-%m-%d'),
            'f3_expiry': fars[2].strftime('%Y-%m-%d'),
            'f4_expiry': fars[3].strftime('%Y-%m-%d'),
        })
    c=pd.DataFrame(rows)
    c=c[(pd.to_datetime(c['near_expiry']) <= pd.Timestamp(max(td)))].copy()
    return c

def get_single(df: pd.DataFrame, expiry: str, strike: float, opt: str, field: str) -> float | None:
    m=df[(df['expiry']==pd.Timestamp(expiry)) & (df['strike']==float(strike)) & (df['option_type']==opt)]
    if len(m)!=1: return None
    v=m.iloc[0][field]
    return float(v) if pd.notna(v) and float(v)>0 else None

def valid_near_strike(entry: pd.DataFrame, near: str, spot: float) -> float | None:
    x=entry[(entry['expiry']==pd.Timestamp(near)) & entry['option_type'].isin(['CE','PE']) & entry['open'].gt(0) & entry['volume'].fillna(0).gt(0)]
    if x.empty: return None
    ce=set(x.loc[x['option_type']=='CE','strike'].dropna().unique())
    pe=set(x.loc[x['option_type']=='PE','strike'].dropna().unique())
    common=sorted(ce & pe)
    if not common: return None
    return float(min(common,key=lambda k:(abs(k-spot),k)))

def candidate(entry: pd.DataFrame, exitd: pd.DataFrame, near: str, far: str, strike: float, spot: float) -> dict | None:
    entry_legs={
        'entry_near_ce':get_single(entry,near,strike,'CE','open'),
        'entry_near_pe':get_single(entry,near,strike,'PE','open'),
        'entry_far_ce':get_single(entry,far,strike,'CE','open'),
        'entry_far_pe':get_single(entry,far,strike,'PE','open'),
    }
    vols=[]
    for exp,opt in [(near,'CE'),(near,'PE'),(far,'CE'),(far,'PE')]:
        m=entry[(entry['expiry']==pd.Timestamp(exp))&(entry['strike']==strike)&(entry['option_type']==opt)]
        vols.append(float(m.iloc[0]['volume']) if len(m)==1 and pd.notna(m.iloc[0]['volume']) else 0.0)
    if any(v is None for v in entry_legs.values()) or any(v<=0 for v in vols): return None
    exit_legs={
        'exit_near_ce':get_single(exitd,near,strike,'CE','close'),
        'exit_near_pe':get_single(exitd,near,strike,'PE','close'),
        'exit_far_ce':get_single(exitd,far,strike,'CE','close'),
        'exit_far_pe':get_single(exitd,far,strike,'PE','close'),
    }
    pnl_available=all(v is not None for v in exit_legs.values())
    entry_credit=entry_legs['entry_near_ce']-entry_legs['entry_near_pe']+entry_legs['entry_far_pe']-entry_legs['entry_far_ce']
    cbr=(entry_legs['entry_far_ce']/entry_legs['entry_near_ce'])/(entry_legs['entry_far_pe']/entry_legs['entry_near_pe'])
    out={**entry_legs,**exit_legs,'entry_credit_points':entry_credit,'entry_credit_yield':entry_credit/spot,'cbr':cbr,'atm_distance_points':abs(strike-spot),'atm_distance_pct':abs(strike-spot)/spot*100,'exit_available':pnl_available,'volume_min':min(vols),'volume_sum':sum(vols)}
    if pnl_available:
        ln=rec.lot_size(pd.Timestamp(near)); lf=rec.lot_size(pd.Timestamp(far))
        out['lot_near']=ln; out['lot_far']=lf
        out['pnl_points']=(out['exit_near_pe']-out['entry_near_pe'])+(out['entry_near_ce']-out['exit_near_ce'])+(out['exit_far_ce']-out['entry_far_ce'])+(out['entry_far_pe']-out['exit_far_pe'])
        out['pnl_inr']=(out['exit_near_pe']-out['entry_near_pe'])*ln+(out['entry_near_ce']-out['exit_near_ce'])*ln+(out['exit_far_ce']-out['entry_far_ce'])*lf+(out['entry_far_pe']-out['exit_far_pe'])*lf
    return out

def net_cost(r: pd.Series, slip: float, exchange_rate: float=0.0005) -> float:
    ln,lf=float(r['lot_near']),float(r['lot_far'])
    eb=r['entry_near_pe']*ln+r['entry_far_ce']*lf
    es=r['entry_near_ce']*ln+r['entry_far_pe']*lf
    xb=r['exit_near_ce']*ln+r['exit_far_pe']*lf
    xs=r['exit_near_pe']*ln+r['exit_far_ce']*lf
    premium=eb+es+xb+xs
    er=0.0015 if pd.Timestamp(r['entry_date'])>=pd.Timestamp('2026-04-01') else 0.001
    xr=0.0015 if pd.Timestamp(r['near_expiry'])>=pd.Timestamp('2026-04-01') else 0.001
    brokerage=8*20
    stt=es*er+xs*xr
    stamp=(eb+xb)*0.00003
    sebi=premium*0.000001
    exchange=premium*exchange_rate
    gst=0.18*(brokerage+exchange+sebi)
    slippage=slip*(4*ln+4*lf)
    return float(r['pnl_inr']-brokerage-stt-stamp-sebi-exchange-gst-slippage)

def perf(vals: pd.Series) -> dict:
    a=pd.to_numeric(vals,errors='coerce').dropna().to_numpy(float)
    if len(a)==0: return {'n':0,'gross':0.0,'mean':np.nan,'median':np.nan,'win':np.nan,'pf':np.nan,'dd':np.nan,'worst':np.nan}
    pos=a[a>0]; neg=a[a<0]; curve=np.cumsum(a); dd=curve-np.maximum.accumulate(curve)
    return {'n':len(a),'gross':float(a.sum()),'mean':float(a.mean()),'median':float(np.median(a)),'win':float((a>0).mean()),'pf':float(pos.sum()/(-neg.sum())) if len(neg) else np.inf,'dd':float(dd.min()),'worst':float(a.min())}

def bootstrap_ci(vals: pd.Series, reps: int=10000, seed: int=20260923) -> tuple[float,float]:
    a=pd.to_numeric(vals,errors='coerce').dropna().to_numpy(float)
    if len(a)==0: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); s=rng.integers(0,len(a),size=(reps,len(a)))
    totals=a[s].sum(axis=1); return tuple(np.quantile(totals,[0.025,0.975]))

def main() -> None:
    cache=Path.home()/'.cache'/'huggingface'/'hub'
    frames=[]; dates=set(); expiries=set()
    for y in YEARS:
        df=load_year(cache,y); frames.append(df)
        dates.update(df['date'].dropna().unique().tolist()); expiries.update(df['expiry'].dropna().unique().tolist())
    cycles=make_cycles(sorted(pd.Timestamp(x) for x in dates),sorted(pd.Timestamp(x) for x in expiries))
    spots=spot_map()
    if cycles.empty: raise RuntimeError('No cycles generated for P12')
    # Re-use the already downloaded annual parquet files from the HF cache and only keep needed entry/exit rows.
    needed_dates=set(pd.to_datetime(cycles['entry_date']).tolist()) | set(pd.to_datetime(cycles['near_expiry']).tolist())
    needed_exps=set(pd.to_datetime(cycles[[f'f{i}_expiry' for i in HORIZONS]].stack()).dropna().tolist()) | set(pd.to_datetime(cycles['near_expiry']).tolist())
    day_frames=[]
    for df in frames:
        z=df[df['date'].isin(needed_dates) & df['expiry'].isin(needed_exps)].copy()
        if not z.empty: day_frames.append(z[['date','expiry','strike','option_type','open','close','volume']])
    data=pd.concat(day_frames,ignore_index=True)
    rows=[]
    for c in cycles.itertuples(index=False):
        entry_date=c.entry_date; near=c.near_expiry; spot=spots.get(entry_date,np.nan)
        base={'cycle_id':c.cycle_id,'sample':c.sample,'previous_expiry':c.previous_expiry,'entry_date':entry_date,'near_expiry':near,'spot_open':spot}
        entry=data[data['date']==pd.Timestamp(entry_date)].copy(); exitd=data[data['date']==pd.Timestamp(near)].copy()
        if not np.isfinite(spot):
            for h in HORIZONS: rows.append({**base,'horizon':h,'horizon_label':LABELS[h],'status':'MISSING_SPOT'}); continue
        strike=valid_near_strike(entry,near,spot)
        if strike is None or abs(strike-spot)>ATMQC:
            for h in HORIZONS: rows.append({**base,'horizon':h,'horizon_label':LABELS[h],'strike':strike,'status':'NO_VALID_NEAR_ATM'}); continue
        cand={}
        for h in HORIZONS:
            far=getattr(c,f'f{h}_expiry')
            try: cc=candidate(entry,exitd,near,far,strike,spot)
            except Exception: cc=None
            if cc is None:
                rows.append({**base,'horizon':h,'horizon_label':LABELS[h],'far_expiry':far,'strike':strike,'status':'NO_ENTRY_LEG'})
            else:
                rows.append({**base,'horizon':h,'horizon_label':LABELS[h],'far_expiry':far,'strike':strike,'status':'EXECUTABLE' if cc.get('exit_available') else 'NO_EXIT_PRINT',**cc})
                cand[h]={**cc,'far_expiry':far,'horizon':h,'strike':strike}
        eligible=[v for v in cand.values() if v.get('exit_available') and np.isfinite(v['entry_credit_yield'])]
        # Primary adaptive selection is made only from entry-observable candidates.
        entry_only=[]
        for h in HORIZONS:
            if h in cand and np.isfinite(cand[h]['entry_credit_yield']): entry_only.append(cand[h])
        if entry_only:
            selected=max(entry_only,key=lambda v:(v['entry_credit_yield'],-v['horizon']))
            rows.append({**base,'horizon':selected['horizon'],'horizon_label':LABELS[selected['horizon']], 'far_expiry':selected['far_expiry'],'strike':strike,'status':'ADAPTIVE_SELECTED','selection_score':selected['entry_credit_yield'], 'entry_credit_points':selected['entry_credit_points'],'cbr':selected['cbr'],'exit_available':selected.get('exit_available',False), 'entry_near_ce':selected['entry_near_ce'],'entry_near_pe':selected['entry_near_pe'],'entry_far_ce':selected['entry_far_ce'],'entry_far_pe':selected['entry_far_pe'], 'exit_near_ce':selected.get('exit_near_ce'), 'exit_near_pe':selected.get('exit_near_pe'), 'exit_far_ce':selected.get('exit_far_ce'), 'exit_far_pe':selected.get('exit_far_pe'), 'lot_near':selected.get('lot_near'), 'lot_far':selected.get('lot_far'), 'pnl_points':selected.get('pnl_points'), 'pnl_inr':selected.get('pnl_inr')})
    ledger=pd.DataFrame(rows)
    # Summaries
    summaries=[]; costs=[]; selections=[]
    for sample in ['DEVELOPMENT','OOS']:
        sub=ledger[ledger['sample']==sample]
        for label,h in [('F+1',1),('F+2',2),('F+3',3),('F+4',4),('ADAPTIVE',0)]:
            if h==0: x=sub[sub['status']=='ADAPTIVE_SELECTED'].copy()
            else: x=sub[(sub['horizon']==h)&(sub['status']=='EXECUTABLE')].copy()
            p=perf(x['pnl_inr']) if not x.empty else perf(pd.Series(dtype=float))
            ci=bootstrap_ci(x['pnl_inr']) if not x.empty else (np.nan,np.nan)
            summaries.append({'sample':sample,'strategy':label,'cycles':int(sub['cycle_id'].nunique()),'executable_trades':len(x),'coverage':float(len(x)/sub['cycle_id'].nunique()) if sub['cycle_id'].nunique() else np.nan,**p,'bootstrap_total_ci_low':ci[0],'bootstrap_total_ci_high':ci[1]})
            for slip in [0,0.5,1,2]:
                xx=x.dropna(subset=['lot_near','lot_far','pnl_inr']).copy()
                net=float(xx.apply(lambda r:net_cost(r,slip),axis=1).sum()) if not xx.empty else 0.0
                costs.append({'sample':sample,'strategy':label,'slippage_points':slip,'net_pnl_inr':net})
        sel=sub[sub['status']=='ADAPTIVE_SELECTED']
        selections.append({'sample':sample,'selected_trades':len(sel),'F+1':int((sel['horizon']==1).sum()),'F+2':int((sel['horizon']==2).sum()),'F+3':int((sel['horizon']==3).sum()),'F+4':int((sel['horizon']==4).sum())})
    summ=pd.DataFrame(summaries); costdf=pd.DataFrame(costs); selfreq=pd.DataFrame(selections)
    ledger.to_csv(OUT_LEDGER,index=False); summ.to_csv(OUT_SUMMARY,index=False); costdf.to_csv(OUT_COSTS,index=False); selfreq.to_csv(OUT_SELECTION,index=False)
    paired=[]
    for sample in ['DEVELOPMENT','OOS']:
        a=ledger[(ledger['sample']==sample)&(ledger['status']=='ADAPTIVE_SELECTED')][['cycle_id','pnl_inr','lot_near','lot_far','entry_date','near_expiry','entry_near_pe','entry_near_ce','entry_far_ce','entry_far_pe','exit_near_pe','exit_near_ce','exit_far_ce','exit_far_pe']].copy()
        for h in HORIZONS:
            x=ledger[(ledger['sample']==sample)&(ledger['horizon']==h)&(ledger['status']=='EXECUTABLE')][['cycle_id','pnl_inr','lot_near','lot_far','entry_date','near_expiry','entry_near_pe','entry_near_ce','entry_far_ce','entry_far_pe','exit_near_pe','exit_near_ce','exit_far_ce','exit_far_pe']].copy()
            x=x.rename(columns={'pnl_inr':'fixed_pnl'})
            z=a.merge(x,on='cycle_id',suffixes=('_adaptive','_fixed'))
            if not z.empty:
                z['delta']=z['pnl_inr']-z['fixed_pnl']
                paired.append({'sample':sample,'comparison':f'ADAPTIVE_vs_{LABELS[h]}','paired_cycles':len(z),'mean_delta_inr':float(z['delta'].mean()),'median_delta_inr':float(z['delta'].median()),'adaptive_higher':int((z['delta']>0).sum()),'fixed_higher':int((z['delta']<0).sum()),'same':int((z['delta']==0).sum())})
    pairdf=pd.DataFrame(paired); pairdf.to_csv(ROOT/'reports/nifty_calendar/P12_ADAPTIVE_PAIRED_COMPARISONS.csv',index=False)
    report=['# P12 Far-Expiry Selection Research Report','', '## Frozen structure','- Entry session: D+1 after previous listed expiry.','- Entry time: 09:15 IST.','- Near expiry: next listed expiry.','- Candidate far expiries: F+1 to F+4 subsequent listed expiries.','- Position: short near CE, long near PE, long far CE, short far PE.','- Same ATM strike across candidates, chosen from the near-expiry 09:15 strike closest to spot; 25-point ATM QC.','- Exit: near-expiry close.','', '## Research-status caveat
- The 2025+ evaluation period was already exposed in P10, so P12 is exploratory rather than confirmatory fresh OOS validation. A future fresh holdout is still required before any live/paper promotion.

## Primary adaptive selection criterion','- Eligibility: same ATM strike, all four entry legs positive, positive entry volume.','- Score = (near CE - near PE + far PE - far CE) / spot open.','- Select the far expiry with the highest score.','- Score uses entry data only; no future close/P&L is used.','', '## Results']
    for _,r in summ.iterrows():
        m=costdf[(costdf['sample']==r['sample'])&(costdf['strategy']==r['strategy'])&(costdf['slippage_points']==2)]
        net2=float(m['net_pnl_inr'].iloc[0]) if not m.empty else 0.0
        report.append(f"- {r.strategy} {r['sample']}: {int(r.executable_trades)} trades, gross ₹{r.gross:,.2f}, win {r.win:.1%}, PF {r.pf:.3f}, DD ₹{abs(r.dd):,.2f}, net@2pt ₹{net2:,.2f}.")
    report += ['', '## Adaptive selection frequency']
    for _,r in selfreq.iterrows(): report.append(f"- {r['sample']}: F+1={int(r['F+1'])}, F+2={int(r['F+2'])}, F+3={int(r['F+3'])}, F+4={int(r['F+4'])}.")
    report += ['', '## Cost sensitivity', costdf.to_markdown(index=False), '', '## Adaptive paired comparisons vs fixed horizons', pairdf.to_markdown(index=False), '', '## Bootstrap intervals']
    for _,r in summ.iterrows(): report.append(f"- {r['strategy']} {r['sample']}: total P&L bootstrap 95% CI ₹{r.bootstrap_total_ci_low:,.2f} to ₹{r.bootstrap_total_ci_high:,.2f}.")
    report += ['', '## Limitations','- The public daily source provides end-of-day option OHLCV; historical bid/ask quotes are not available in this source.','- Modeled slippage/costs are sensitivities, not observed Paytm Money fills.','- Adaptive selection is a pre-registered entry-time rule; it is not optimized against OOS P&L.','', '## Phase conclusion','- P12 is closed after fixed F+1/F+2/F+3/F+4 comparison and the frozen adaptive selector. No additional far-expiry horizons or score weights are searched in this phase.']
    OUT_REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')
    decision='P12 COMPLETE — FAR-EXPIRY OUTCOMES AND ENTRY-TIME SELECTION TESTED'
    OUT_CONCLUSION.write_text('\n'.join(['# P12 Final Research Conclusion','',decision,'','The primary adaptive rule selects the far expiry using only 09:15 entry information: maximum normalized entry credit among F+1 to F+4 eligible candidates. Fixed-horizon and evaluation-holdout results are reported in P12_FAR_EXPIRY_SUMMARY.csv and P12_FAR_EXPIRY_COST_SENSITIVITY.csv. The evaluation holdout was already exposed during P10, so these P12 results are exploratory.','', 'No further far-expiry search or score-weight optimization is performed in P12.']),encoding='utf-8')
    phase=['# Phase Status','', 'Last updated: 2026-09-23 — P12 far-expiry research completed.','', '| Phase | Status | Notes |','|---|---|---|','| P0-P11 | COMPLETE / CLOSED | Prior research phases preserved. |','| P12 Far-expiry selection | COMPLETE | F+1/F+2/F+3/F+4 fixed horizons and pre-registered entry-credit adaptive selection tested. |','', 'P12 stop condition: no additional far-expiry horizons or adaptive-score weights are searched in this phase.']
    OUT_STATUS.write_text('\n'.join(phase)+'\n',encoding='utf-8')
    print(summ.to_string(index=False))
    print(selfreq.to_string(index=False))

if __name__=='__main__': main()