from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
import requests

ROOT=Path(__file__).resolve().parents[1]
CUTOFF=pd.Timestamp('2026-08-26')
YEARS=[2022,2023,2024,2025,2026]
HORIZONS=[1,2,3,4]
LABELS={1:'F+1',2:'F+2',3:'F+3',4:'F+4'}
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; NoDip research bot)','Accept':'*/*'}
ATMQC=25.0

spec=importlib.util.spec_from_file_location('p12',ROOT/'scripts/p12_far_expiry_selection.py')
p12=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(p12)

rec_spec=importlib.util.spec_from_file_location('rec',ROOT/'scripts/reconcile_rejections_nse.py')
rec=importlib.util.module_from_spec(rec_spec); assert rec_spec.loader is not None; rec_spec.loader.exec_module(rec)

OUT_LEDGER=ROOT/'reports/nifty_calendar/P13_FRESH_FAR_EXPIRY_LEDGER.csv'
OUT_SUMMARY=ROOT/'reports/nifty_calendar/P13_FRESH_FAR_EXPIRY_SUMMARY.csv'
OUT_COSTS=ROOT/'reports/nifty_calendar/P13_FRESH_FAR_EXPIRY_COSTS.csv'
OUT_REPORT=ROOT/'reports/nifty_calendar/P13_FRESH_FAR_EXPIRY_VALIDATION_REPORT.md'
OUT_CONCLUSION=ROOT/'reports/nifty_calendar/P13_FINAL_RESEARCH_CONCLUSION.md'
OUT_STATUS=ROOT/'docs/nifty_calendar/PHASE_STATUS.md'

def load_all(cache:Path):
    frames=[]; dates=set(); exps=set()
    for y in YEARS:
        path=hf_hub_download(repo_id='rissin/nse-options-intraday',filename=f'historical_daily/NIFTY/NIFTY_{y}.parquet',repo_type='dataset',cache_dir=str(cache))
        df=pd.read_parquet(path)
        df['date']=pd.to_datetime(df['date'],errors='coerce').dt.normalize()
        df['expiry']=pd.to_datetime(df['expiry'],errors='coerce').dt.normalize()
        df['strike']=pd.to_numeric(df['strike'],errors='coerce')
        df['open']=pd.to_numeric(df['open'],errors='coerce')
        df['close']=pd.to_numeric(df['close'],errors='coerce')
        df['volume']=pd.to_numeric(df['volume'],errors='coerce')
        df['underlying']=df['underlying'].astype(str).str.upper()
        df['option_type']=df['option_type'].astype(str).str.upper()
        df['granularity']=df['granularity'].astype(str).str.lower()
        df=df[(df['underlying']=='NIFTY')&(df['granularity']=='1d')].copy()
        frames.append(df[['date','expiry','strike','option_type','open','close','volume']])
        dates.update(df['date'].dropna().tolist()); exps.update(df['expiry'].dropna().tolist())
    return frames,sorted(dates),sorted(exps)

def spot_map():
    s=requests.Session()
    start=pd.Timestamp('2026-08-20',tz='Asia/Kolkata'); end=pd.Timestamp('2026-09-30',tz='Asia/Kolkata')
    p1=int(start.tz_convert('UTC').timestamp()); p2=int(end.tz_convert('UTC').timestamp())
    r=s.get('https://query1.finance.yahoo.com/v8/finance/chart/^NSEI',params={'period1':p1,'period2':p2,'interval':'1d','events':'history'},headers=HEADERS,timeout=30); r.raise_for_status()
    js=r.json()['chart']['result'][0]; out={}
    for t,v in zip(js['timestamp'],js['indicators']['quote'][0]['open']):
        if v is None: continue
        d=pd.to_datetime(t,unit='s',utc=True).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d'); out[d]=float(v)
    return out

def val(df,exp,strike,opt,field):
    m=df[(df.expiry==pd.Timestamp(exp))&(df.strike==float(strike))&(df.option_type==opt)]
    if len(m)!=1: return None
    v=m.iloc[0][field]
    return float(v) if pd.notna(v) and float(v)>0 else None

def near_atm(entry,near,spot):
    x=entry[(entry.expiry==pd.Timestamp(near))&entry.option_type.isin(['CE','PE'])&entry.open.gt(0)&entry.volume.fillna(0).gt(0)]
    if x.empty:return None
    ce=set(x.loc[x.option_type=='CE','strike'].dropna().unique()); pe=set(x.loc[x.option_type=='PE','strike'].dropna().unique())
    common=sorted(ce&pe)
    return float(min(common,key=lambda k:(abs(k-spot),k))) if common else None

def candidate(entry,exitd,near,far,strike,spot):
    legs=['near_ce','near_pe','far_ce','far_pe']
    specs={'entry_near_ce':(near,'CE'),'entry_near_pe':(near,'PE'),'entry_far_ce':(far,'CE'),'entry_far_pe':(far,'PE')}
    d={k:val(entry,*v,'open') for k,v in specs.items()}
    vol_ok=True; vols=[]
    for exp,opt in [(near,'CE'),(near,'PE'),(far,'CE'),(far,'PE')]:
        m=entry[(entry.expiry==pd.Timestamp(exp))&(entry.strike==strike)&(entry.option_type==opt)]
        if len(m)!=1: vol_ok=False; break
        vols.append(float(m.iloc[0].volume) if pd.notna(m.iloc[0].volume) else 0.0)
    if not vol_ok or any(v is None for v in d.values()) or any(v<=0 for v in vols): return None
    exits={k:val(exitd,*v,'close') for k,v in {'exit_near_ce':(near,'CE'),'exit_near_pe':(near,'PE'),'exit_far_ce':(far,'CE'),'exit_far_pe':(far,'PE')}.items()}
    score=(d['entry_near_ce']-d['entry_near_pe']+d['entry_far_pe']-d['entry_far_ce'])/spot
    out={**d,**exits,'selection_score':score,'entry_credit_points':d['entry_near_ce']-d['entry_near_pe']+d['entry_far_pe']-d['entry_far_ce'],'cbr':(d['entry_far_ce']/d['entry_near_ce'])/(d['entry_far_pe']/d['entry_near_pe']),'volume_min':min(vols),'volume_sum':sum(vols),'exit_available':all(v is not None for v in exits.values())}
    if out['exit_available']:
        ln=rec.lot_size(pd.Timestamp(near)); lf=rec.lot_size(pd.Timestamp(far)); out['lot_near']=ln; out['lot_far']=lf
        out['pnl_inr']=(out['exit_near_pe']-out['entry_near_pe'])*ln+(out['entry_near_ce']-out['exit_near_ce'])*ln+(out['exit_far_ce']-out['entry_far_ce'])*lf+(out['entry_far_pe']-out['exit_far_pe'])*lf
    return out

def net_cost(r,slip):
    ln,lf=float(r.lot_near),float(r.lot_far)
    eb=r.entry_near_pe*ln+r.entry_far_ce*lf; es=r.entry_near_ce*ln+r.entry_far_pe*lf
    xb=r.exit_near_ce*ln+r.exit_far_pe*lf; xs=r.exit_near_pe*ln+r.exit_far_ce*lf
    premium=eb+es+xb+xs
    er=0.0015 if pd.Timestamp(r.entry_date)>=pd.Timestamp('2026-04-01') else 0.001
    xr=0.0015 if pd.Timestamp(r.near_expiry)>=pd.Timestamp('2026-04-01') else 0.001
    brokerage=8*20; stt=es*er+xs*xr; stamp=(eb+xb)*0.00003; sebi=premium*0.000001; exchange=premium*0.0005; gst=0.18*(brokerage+exchange+sebi); slippage=slip*(4*ln+4*lf)
    return float(r.pnl_inr-brokerage-stt-stamp-sebi-exchange-gst-slippage)

def perf(a):
    x=pd.to_numeric(a,errors='coerce').dropna().to_numpy(float)
    if len(x)==0:return {'n':0,'gross':0.0,'mean':np.nan,'win':np.nan,'pf':np.nan,'dd':np.nan,'worst':np.nan}
    pos=x[x>0]; neg=x[x<0]; curve=np.cumsum(x); dd=curve-np.maximum.accumulate(curve)
    return {'n':len(x),'gross':float(x.sum()),'mean':float(x.mean()),'win':float((x>0).mean()),'pf':float(pos.sum()/(-neg.sum())) if len(neg) else np.inf,'dd':float(dd.min()),'worst':float(x.min())}

def main():
    cache=Path.home()/'.cache'/'huggingface'/'hub'
    frames,dates,exps=load_all(cache)
    max_date=pd.Timestamp(max(dates))
    cycles=p12.make_cycles(dates,exps)
    if cycles.empty: raise RuntimeError('No cycles generated')
    cycles['entry_date']=pd.to_datetime(cycles.entry_date); cycles['near_expiry']=pd.to_datetime(cycles.near_expiry)
    fresh=cycles[(cycles.entry_date>CUTOFF)&(cycles.near_expiry<=max_date)].copy()
    spot=spot_map()
    need_dates=set(fresh.entry_date.tolist())|set(fresh.near_expiry.tolist())
    need_exps=set(fresh.near_expiry.tolist())
    for h in HORIZONS: need_exps.update(pd.to_datetime(fresh[f'f{h}_expiry']).dropna().tolist())
    data=pd.concat([df[df.date.isin(need_dates)&df.expiry.isin(need_exps)] for df in frames],ignore_index=True)
    rows=[]
    for c in fresh.itertuples(index=False):
        ed=str(pd.Timestamp(c.entry_date).date()); near=str(pd.Timestamp(c.near_expiry).date()); sp=spot.get(ed)
        base={'cycle_id':c.cycle_id,'entry_date':ed,'previous_expiry':c.previous_expiry,'near_expiry':near,'spot_open':sp}
        if sp is None: rows.append({**base,'status':'MISSING_SPOT'}); continue
        entry=data[data.date==pd.Timestamp(ed)]; exitd=data[data.date==pd.Timestamp(near)]
        strike=near_atm(entry,near,float(sp))
        if strike is None or abs(strike-float(sp))>ATMQC: rows.append({**base,'status':'NO_VALID_NEAR_ATM','strike':strike}); continue
        cand={}
        for h in HORIZONS:
            far=str(pd.Timestamp(getattr(c,f'f{h}_expiry')).date())
            cc=candidate(entry,exitd,near,far,strike,float(sp))
            if cc is None: rows.append({**base,'horizon':h,'horizon_label':LABELS[h],'far_expiry':far,'strike':strike,'status':'NO_ENTRY_LEG'})
            else: rows.append({**base,'horizon':h,'horizon_label':LABELS[h],'far_expiry':far,'strike':strike,'status':'EXECUTABLE' if cc['exit_available'] else 'NO_EXIT_PRINT',**cc}); cand[h]=cc
        elig=[v for v in cand.values() if np.isfinite(v['selection_score'])]
        if elig:
            sel=max(elig,key=lambda v:(v['selection_score'],-v['horizon']))
            rows.append({**base,'horizon':sel['horizon'],'horizon_label':LABELS[sel['horizon']],'far_expiry':sel['far_expiry'],'strike':strike,'status':'ADAPTIVE_SELECTED',**sel})
    ledger=pd.DataFrame(rows)
    if ledger.empty:
        ledger=pd.DataFrame([{
            'status':'NO_FRESH_ROWS',
            'cutoff':str(CUTOFF.date()),
            'latest_source_date':str(max_date.date()),
            'fresh_cycles':len(fresh),
        }])
    if 'status' not in ledger.columns:
        ledger['status']='UNKNOWN'
    summary=[]; costs=[]
    for label,h in [('F+1',1),('F+2',2),('F+3',3),('F+4',4),('ADAPTIVE',0)]:
        if h==0:
            x=ledger[ledger['status'].eq('ADAPTIVE_SELECTED')].copy()
        elif 'horizon' in ledger.columns:
            x=ledger[ledger['horizon'].eq(h)&ledger['status'].eq('EXECUTABLE')].copy()
        else:
            x=ledger.iloc[0:0].copy()
        p=perf(x.pnl_inr if 'pnl_inr' in x else pd.Series(dtype=float))
        summary.append({'strategy':label,'scheduled_cycles':len(fresh),'executable_trades':len(x),'coverage':len(x)/len(fresh) if len(fresh) else np.nan,**p})
        for slip in [0,0.5,1,2]:
            y=x.dropna(subset=['lot_near','lot_far','pnl_inr']).copy()
            net=float(y.apply(lambda r:net_cost(r,slip),axis=1).sum()) if not y.empty else 0.0
            costs.append({'strategy':label,'slippage_points':slip,'net_pnl_inr':net})
    sel=ledger[ledger['status'].eq('ADAPTIVE_SELECTED')].copy()
    freq={f'F+{h}':int((sel.horizon==h).sum()) for h in HORIZONS}
    OUT_LEDGER.parent.mkdir(parents=True,exist_ok=True)
    ledger.to_csv(OUT_LEDGER,index=False); pd.DataFrame(summary).to_csv(OUT_SUMMARY,index=False); pd.DataFrame(costs).to_csv(OUT_COSTS,index=False); pd.DataFrame([freq|{'selected_trades':len(sel),'latest_source_date':str(max_date.date()),'cutoff':str(CUTOFF.date())}]).to_csv(ROOT/'reports/nifty_calendar/P13_ADAPTIVE_SELECTION.csv',index=False)
    report=['# P13 Fresh Far-Expiry Validation Report','', '## Frozen rule','- D+1 entry, 09:15 market-open proxy, near expiry next listed expiry.','- Far candidates F+1 through F+4.','- Adaptive score = (near CE - near PE + far PE - far CE) / spot open.','- Choose highest score using entry information only.','- No threshold/weight/horizon tuning was performed in P13.','', '## Fresh-data gate',f'- P10/P12 cutoff: {CUTOFF.date()}',f'- Latest source trading date: {max_date.date()}',f'- Fresh completed cycles: {len(fresh)}','', '## Results']
    for r in summary:
        m=pd.DataFrame(costs); z=m[(m.strategy==r['strategy'])&(m.slippage_points==2)]; n2=float(z.net_pnl_inr.iloc[0]) if not z.empty else 0.0
        report.append(f"- {r['strategy']}: {int(r['executable_trades'])} trades, gross ₹{r['gross']:,.2f}, PF {r['pf']:.3f}, win {r['win']:.1%}, DD ₹{abs(r['dd']):,.2f}, net@2pt ₹{n2:,.2f}.")
    report += ['', '## Adaptive selection frequency',f"- {freq}", '', '## Data-quality interpretation', '- This is the first evaluation of the frozen P12 rule on dates strictly after 2026-08-26 available in the current dataset.', '- The entry uses the same daily-open proxy used by P12; it is not a historical bid/ask or exact exchange tick-fill reconstruction.', '', '## Decision']
    n=len(sel); net2=float(pd.DataFrame(costs).query("strategy=='ADAPTIVE' and slippage_points==2").net_pnl_inr.iloc[0]) if n else 0.0
    if n<8: decision='INSUFFICIENT FRESH SAMPLE — CONTINUE PROSPECTIVE PAPER MONITORING'
    elif net2<=0: decision='FROZEN RULE FAILED FRESH 2-POINT COST GATE'
    else: decision='FRESH VALIDATION PASSED PRELIMINARY COST GATE — CONTINUE PAPER MONITORING'
    report.append(f'**{decision}**')
    OUT_REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')
    OUT_CONCLUSION.write_text('\n'.join(['# P13 Final Research Conclusion','',f'Decision: **{decision}**.','',f'Fresh completed cycles: {len(fresh)}.',f'Adaptive selected trades: {n}.',f'Adaptive net P&L at 2-point slippage: ₹{net2:,.2f}.','', 'No parameter or score changes were made in P13.']),encoding='utf-8')
    OUT_STATUS.write_text('\n'.join(['# Phase Status','',f'Last updated: 2026-09-23 — P13 fresh far-expiry validation completed.', '', '| Phase | Status | Notes |','|---|---|---|','| P0-P12 | COMPLETE / CLOSED | Prior phases preserved. |','| P13 Fresh far-expiry validation | COMPLETE | Frozen P12 adaptive rule tested on dates strictly after the P10/P12 cutoff. |', '',f'P13 decision: **{decision}**'])+'\n',encoding='utf-8')
    print(pd.DataFrame(summary).to_string(index=False)); print('selection',freq,'fresh cycles',len(fresh),'latest source',max_date.date())

if __name__=='__main__': main()