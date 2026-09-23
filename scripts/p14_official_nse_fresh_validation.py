from __future__ import annotations

import io, hashlib, zipfile, importlib.util
from datetime import date, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
CUTOFF=pd.Timestamp('2026-08-26')
START=date(2026,8,27); END=date(2026,9,23)
FRESH_CYCLE_DATES=[date(2026,9,2),date(2026,9,8),date(2026,9,9),date(2026,9,15),date(2026,9,16),date(2026,9,22)]
HORIZONS=[1,2,3,4]; LABELS={1:'F+1',2:'F+2',3:'F+3',4:'F+4'}; ATM_QC=25.0
DATA=ROOT/'data/cache/p14_nse'; OUT=ROOT/'reports/nifty_calendar'

spec=importlib.util.spec_from_file_location('rec',ROOT/'scripts/reconcile_rejections_nse.py')
rec=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(rec)

def daterange(a,b):
    d=a
    while d<=b:
        yield d; d+=timedelta(days=1)

def fetch_day(sess,d):
    DATA.mkdir(parents=True,exist_ok=True)
    path=DATA/f'{d:%Y%m%d}.zip'
    if path.exists() and path.stat().st_size>1000:
        return {'date':d.isoformat(),'url':'CACHED','status':'CACHED','bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    filename=rec.nse_url(d).rsplit('/',1)[-1]
    urls=[f'https://archives.nseindia.com/content/fo/{filename}',f'https://nsearchives.nseindia.com/content/fo/{filename}']
    headers={'Accept':'application/zip,application/octet-stream;q=0.9,*/*;q=0.8','Referer':'https://www.nseindia.com/all-reports-derivatives','User-Agent':'Mozilla/5.0 (compatible; NSE-FNO-Data-bank/1.0; +https://github.com/SantoshSrinivas79/NSE-FNO-Data-bank)'}
    errors=[]
    for url in urls:
        for attempt in range(4):
            try:
                r=sess.get(url,headers=headers,timeout=45,allow_redirects=True)
                if r.status_code==404:
                    break
                if r.status_code==200 and r.content.startswith(b'PK'):
                    path.write_bytes(r.content)
                    return {'date':d.isoformat(),'url':url,'status':'DOWNLOADED','bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest()}
                errors.append(f'{url}: HTTP {r.status_code} content_type={r.headers.get("content-type")} bytes={len(r.content)} prefix={r.content[:20]!r}')
            except Exception as e:
                errors.append(f'{url}: {e!r}')
        # try next archive host
    return {'date':d.isoformat(),'url':';'.join(urls),'status':'ERROR','bytes':0,'sha256':' | '.join(errors)}

def read_zip(path,d):
    try:
        df=rec.read_nifty_options(path,d)
        if df.empty:return df
        df['date']=pd.to_datetime(df['date']).dt.normalize(); df['expiry']=pd.to_datetime(df['expiry']).dt.normalize()
        df['option_type']=df['option_type'].astype(str).str.upper(); df['strike']=pd.to_numeric(df['strike'],errors='coerce')
        df['open']=pd.to_numeric(df['open'],errors='coerce'); df['close']=pd.to_numeric(df['close'],errors='coerce'); df['contracts']=pd.to_numeric(df['contracts'],errors='coerce'); df['underlying']=pd.to_numeric(df['underlying'],errors='coerce')
        return df
    except Exception:
        return pd.DataFrame()

def get1(df,exp,strike,opt,field):
    m=df[(df.expiry==pd.Timestamp(exp))&(df.strike==float(strike))&(df.option_type==opt)]
    if len(m)!=1:return None
    v=m.iloc[0][field]; return float(v) if pd.notna(v) and float(v)>0 else None

def spot_open(day):
    x=day['underlying'].dropna(); return float(x.median()) if not x.empty else None

def choose_strike(entry,near,spot):
    x=entry[(entry.expiry==pd.Timestamp(near))&entry.option_type.isin(['CE','PE'])&entry.open.gt(0)&entry.contracts.fillna(0).gt(0)]
    if x.empty:return None
    common=set(x.loc[x.option_type=='CE','strike'].dropna()) & set(x.loc[x.option_type=='PE','strike'].dropna())
    if not common:return None
    k=min(common,key=lambda s:(abs(float(s)-spot),float(s))); return float(k)

def cand(entry,exitd,near,far,strike,spot):
    names={'entry_near_ce':(near,'CE'),'entry_near_pe':(near,'PE'),'entry_far_ce':(far,'CE'),'entry_far_pe':(far,'PE')}
    e={k:get1(entry,*v,'open') for k,v in names.items()}
    vols=[]
    for exp,opt in [(near,'CE'),(near,'PE'),(far,'CE'),(far,'PE')]:
        m=entry[(entry.expiry==pd.Timestamp(exp))&(entry.strike==strike)&(entry.option_type==opt)]
        if len(m)!=1:return None
        vols.append(float(m.iloc[0].contracts) if pd.notna(m.iloc[0].contracts) else 0.0)
    if any(v is None for v in e.values()) or any(v<=0 for v in vols):return None
    x={'exit_near_ce':get1(exitd,near,strike,'CE','close'),'exit_near_pe':get1(exitd,near,strike,'PE','close'),'exit_far_ce':get1(exitd,far,strike,'CE','close'),'exit_far_pe':get1(exitd,far,strike,'PE','close')}
    score=(e['entry_near_ce']-e['entry_near_pe']+e['entry_far_pe']-e['entry_far_ce'])/spot
    return {**e,**x,'selection_score':score,'entry_credit_points':e['entry_near_ce']-e['entry_near_pe']+e['entry_far_pe']-e['entry_far_ce'],'atm_distance_points':abs(strike-spot),'cbr':(e['entry_far_ce']/e['entry_near_ce'])/(e['entry_far_pe']/e['entry_near_pe']),'exit_available':all(v is not None for v in x.values()),'volume_min':min(vols)}

def pnl(row,near,far):
    if not row.get('exit_available'):return None
    ln=rec.lot_size(pd.Timestamp(near)); lf=rec.lot_size(pd.Timestamp(far))
    row['lot_near']=ln; row['lot_far']=lf
    row['pnl_inr']=(row['exit_near_pe']-row['entry_near_pe'])*ln+(row['entry_near_ce']-row['exit_near_ce'])*ln+(row['exit_far_ce']-row['entry_far_ce'])*lf+(row['entry_far_pe']-row['exit_far_pe'])*lf
    return row

def net_cost(r,slip):
    ln,lf=float(r['lot_near']),float(r['lot_far'])
    eb=r['entry_near_pe']*ln+r['entry_far_ce']*lf; es=r['entry_near_ce']*ln+r['entry_far_pe']*lf; xb=r['exit_near_ce']*ln+r['exit_far_pe']*lf; xs=r['exit_near_pe']*ln+r['exit_far_ce']*lf
    premium=eb+es+xb+xs
    brokerage=8*10.0
    stt=0.0015*(es+xs)
    stamp=0.00003*(eb+xb); sebi=0.000001*premium; exchange=0.0005*premium; gst=0.18*(brokerage+exchange+sebi)
    return float(r['pnl_inr']-brokerage-stt-stamp-sebi-exchange-gst-slip*(4*ln+4*lf))

def perf(x):
    a=pd.to_numeric(x,errors='coerce').dropna().to_numpy(float)
    if len(a)==0:return {'n':0,'gross':0.0,'mean':np.nan,'win':np.nan,'pf':np.nan,'dd':np.nan,'worst':np.nan}
    pos=a[a>0]; neg=a[a<0]; curve=np.cumsum(a); dd=curve-np.maximum.accumulate(curve)
    return {'n':len(a),'gross':float(a.sum()),'mean':float(a.mean()),'win':float((a>0).mean()),'pf':float(pos.sum()/(-neg.sum())) if len(neg) else np.inf,'dd':float(dd.min()),'worst':float(a.min())}

def main():
    sess=requests.Session(); manifest=[]
    days=FRESH_CYCLE_DATES
    def one(d):
        local=requests.Session()
        for attempt in range(3):
            m=fetch_day(local,d)
            if m['status'] in ('CACHED','DOWNLOADED') or m['status'].startswith('HTTP_404'):
                return m
        return m
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs={ex.submit(one,d):d for d in days}
        for fut in as_completed(futs):
            manifest.append(fut.result())
    manifest=sorted(manifest,key=lambda x:x['date'])
    pd.DataFrame(manifest).to_csv(OUT/'P14_NSE_SOURCE_MANIFEST.csv',index=False)
    frames=[]
    for m in manifest:
        path=DATA/f"{pd.Timestamp(m['date']):%Y%m%d}.zip"
        if path.exists():
            z=read_zip(path,pd.Timestamp(m['date']));
            if not z.empty:frames.append(z)
    if not frames:
        manifest_df=pd.DataFrame(manifest)
        status_counts=manifest_df['status'].value_counts(dropna=False).to_dict() if not manifest_df.empty else {}
        (OUT/'P14_OFFICIAL_NSE_FRESH_VALIDATION_REPORT.md').write_text('\n'.join([
            '# P14 Official NSE Fresh Far-Expiry Validation Report','',
            '## Source access gate',
            '- No usable official NSE F&O UDiFF archive was parsed by the runner.',
            f'- Attempted trading dates: {len(manifest)}.',
            f'- Status counts: {status_counts}.',
            '',
            '## Decision',
            '**FRESH DATA SOURCE BLOCKED — NO STRATEGY RESULT PRODUCED**',
            '',
            'This is a data-access/source-availability failure, not a strategy loss result. No P12 observations were reused.'
        ])+'\n',encoding='utf-8')
        (OUT/'P14_FINAL_RESEARCH_CONCLUSION.md').write_text('\n'.join([
            '# P14 Final Research Conclusion','',
            '**FRESH DATA SOURCE BLOCKED — NO STRATEGY RESULT PRODUCED**','',
            'Official NSE fresh data could not be acquired and parsed from the runner. P14 therefore cannot validate or reject the frozen P12 adaptive rule.'
        ])+'\n',encoding='utf-8')
        raise SystemExit(0)
    all_df=pd.concat(frames,ignore_index=True)
    all_df=all_df[(all_df.option_type.isin(['CE','PE']))&(all_df.strike.notna())].copy()
    dates=sorted(all_df.date.unique()); exps=sorted(all_df.expiry.unique())
    latest=pd.Timestamp(max(dates))
    cycle_specs=[
        ('2026-09-01','2026-09-02','2026-09-08',['2026-09-15','2026-09-22','2026-09-29','2026-10-06']),
        ('2026-09-08','2026-09-09','2026-09-15',['2026-09-22','2026-09-29','2026-10-06','2026-10-13']),
        ('2026-09-15','2026-09-16','2026-09-22',['2026-09-29','2026-10-06','2026-10-13','2026-10-20']),
    ]
    dates_set={pd.Timestamp(d).date() for d in dates}
    cycles=[]
    for prev,entry,near,fars in cycle_specs:
        if pd.Timestamp(entry)<=CUTOFF or pd.Timestamp(near)>latest: continue
        if pd.Timestamp(entry).date() not in dates_set or pd.Timestamp(near).date() not in dates_set: continue
        cycles.append({'cycle_id':f'P14_{entry.replace("-","")}', 'previous_expiry':prev, 'entry_date':entry, 'near_expiry':near, 'f1_expiry':fars[0], 'f2_expiry':fars[1], 'f3_expiry':fars[2], 'f4_expiry':fars[3]})
    ledger=[]
    for c in cycles:
        ed=pd.Timestamp(c['entry_date']); near=c['near_expiry']; entry=all_df[all_df.date==ed]; exitd=all_df[all_df.date==pd.Timestamp(near)]; sp=spot_open(entry)
        base={**c,'spot_open':sp}
        if sp is None: ledger.append({**base,'status':'MISSING_SPOT'}); continue
        strike=choose_strike(entry,near,sp)
        if strike is None or abs(strike-sp)>ATM_QC:ledger.append({**base,'status':'NO_VALID_ATM','strike':strike});continue
        candidates={}
        for h in HORIZONS:
            far=c[f'f{h}_expiry']; cc=cand(entry,exitd,near,far,strike,sp)
            if cc is None: ledger.append({**base,'horizon':h,'horizon_label':LABELS[h],'far_expiry':far,'strike':strike,'status':'NO_ENTRY_LEG'}); continue
            cc['far_expiry']=far; cc['horizon']=h; cc['horizon_label']=LABELS[h]; cc['strike']=strike; cc['entry_date']=c['entry_date']; cc['near_expiry']=near; cc['previous_expiry']=c['previous_expiry']; cc['cycle_id']=c['cycle_id']; cc['spot_open']=sp
            cc=pnl(cc,near,far) if cc['exit_available'] else cc; cc['status']='EXECUTABLE' if cc.get('pnl_inr') is not None else 'NO_EXIT_LEG'; ledger.append(cc); candidates[h]=cc
        eligible=[v for v in candidates.values() if np.isfinite(v['selection_score'])]
        if eligible:
            sel=max(eligible,key=lambda v:(v['selection_score'],-v['horizon'])); sr=dict(sel); sr['status']='ADAPTIVE_SELECTED'; ledger.append(sr)
    ledger=pd.DataFrame(ledger); ledger.to_csv(OUT/'P14_OFFICIAL_NSE_FRESH_LEDGER.csv',index=False)
    summary=[]; costs=[]
    for label,h in [('F+1',1),('F+2',2),('F+3',3),('F+4',4),('ADAPTIVE',0)]:
        if h==0:x=ledger[ledger.status.eq('ADAPTIVE_SELECTED')].copy()
        else:x=ledger[ledger.horizon.eq(h)&ledger.status.eq('EXECUTABLE')].copy() if 'horizon' in ledger.columns else ledger.iloc[0:0]
        p=perf(x['pnl_inr'] if 'pnl_inr' in x else pd.Series(dtype=float)); summary.append({'strategy':label,'trades':p['n'],'gross_pnl':p['gross'],'mean_pnl':p['mean'],'win_rate':p['win'],'profit_factor':p['pf'],'max_drawdown':abs(p['dd']) if np.isfinite(p['dd']) else np.nan,'worst_trade':p['worst'],'coverage':p['n']/len(cycles) if cycles else np.nan})
        for slip in [0,0.5,1,2]:
            if all(col in x.columns for col in ['lot_near','lot_far','pnl_inr']): y=x.dropna(subset=['lot_near','lot_far','pnl_inr'])
            else:y=x.iloc[0:0]
            costs.append({'strategy':label,'slippage_points':slip,'net_pnl':float(y.apply(lambda r:net_cost(r,slip),axis=1).sum()) if not y.empty else 0.0})
    sm=pd.DataFrame(summary); cs=pd.DataFrame(costs); sm.to_csv(OUT/'P14_OFFICIAL_NSE_FRESH_SUMMARY.csv',index=False); cs.to_csv(OUT/'P14_OFFICIAL_NSE_FRESH_COSTS.csv',index=False)
    sel=ledger[ledger.status.eq('ADAPTIVE_SELECTED')].copy() if 'status' in ledger.columns else ledger.iloc[0:0]; freq={f'F+{h}':int((sel.horizon==h).sum()) if 'horizon' in sel.columns else 0 for h in HORIZONS}; pd.DataFrame([{'latest_source_date':str(latest.date()),'fresh_cycles':len(cycles),'selected_trades':len(sel),**freq}]).to_csv(OUT/'P14_ADAPTIVE_SELECTION.csv',index=False)
    status_counts=ledger['status'].value_counts().to_dict() if 'status' in ledger.columns else {}
    adaptive=sm[sm.strategy.eq('ADAPTIVE')].iloc[0]; net2=float(cs[(cs.strategy=='ADAPTIVE')&(cs.slippage_points==2)].net_pnl.iloc[0])
    if len(sel)<8:decision='INSUFFICIENT FRESH SAMPLE — CONTINUE PROSPECTIVE PAPER MONITORING'
    elif net2<=0:decision='FROZEN RULE FAILED FRESH 2-POINT COST GATE'
    else:decision='PRELIMINARY FRESH COST GATE PASSED — PAPER MONITORING ONLY'
    report=['# P14 Official NSE Fresh Far-Expiry Validation Report','', '## Source','- Official NSE F&O UDiFF Common Bhavcopy Final; daily files from 2026-08-27 through 2026-09-23 were attempted and cached.','- NIFTY option rows only; source manifest records each date, response, size and SHA256.','', '## Frozen strategy','- D+1 after previous expiry; 09:15 market-open proxy; F+1/F+2/F+3/F+4 far expiries.','- Adaptive score = (near CE - near PE + far PE - far CE) / NIFTY underlying price.','- Highest score selected using entry information only.','- Same ATM strike; <=25-point QC.','',f'## Fresh data gate\n- P10/P12 cutoff: {CUTOFF.date()}\n- Latest official NSE parsed date: {latest.date()}\n- Fresh completed cycles: {len(cycles)}\n- Ledger status counts: {status_counts}\n', '## Results']
    for _,r in sm.iterrows(): report.append(f"- {r.strategy}: {int(r.trades)} trades; gross ₹{r.gross_pnl:,.2f}; PF {r.profit_factor:.3f}; win {r.win_rate:.1%}; DD ₹{r.max_drawdown:,.2f}; net @2pt ₹{float(cs[(cs.strategy==r.strategy)&(cs.slippage_points==2)].net_pnl.iloc[0]):,.2f}.")
    report += ['', '## Adaptive selection frequency',str(freq),'', '## Paytm Money brokerage input','- P14 models ₹10 brokerage per unique executed order based on Paytm Money’s current F&O FAQ.','- Eight option orders per completed cycle are modeled.','- STT is 0.15% on option-sale premium for trades after 2026-04-01; stamp duty, SEBI fee, GST and a 0.05% exchange-charge stress are included.','- Adverse slippage is separately tested at 0/0.5/1/2 points per execution.','', '## Decision',f'**{decision}**', '', '- This is a genuinely fresh official-NSE post-cutoff sample. Because the number of completed weekly cycles is small, no statistical significance claim is made.', '- The P14 test does not retune the adaptive score or search further far-expiry horizons.']
    (OUT/'P14_OFFICIAL_NSE_FRESH_VALIDATION_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    (OUT/'P14_FINAL_RESEARCH_CONCLUSION.md').write_text('\n'.join(['# P14 Final Research Conclusion','',f'Decision: **{decision}**.',f'Fresh completed cycles: {len(cycles)}.',f'Adaptive selected trades: {len(sel)}.',f'Adaptive net P&L @2pt: ₹{net2:,.2f}.','', 'The data are now sourced from official NSE daily F&O UDiFF bhavcopy rather than the stale public Hugging Face cache.','', 'No parameter or far-expiry score change was made in P14.']),encoding='utf-8')
    pd.DataFrame({'phase':['P0-P13','P14 Official NSE fresh validation'],'status':['COMPLETE / CLOSED','COMPLETE'],'notes':['Prior phases preserved.',f'Frozen P12 adaptive far-expiry rule evaluated on {len(cycles)} fresh post-cutoff completed cycles; decision: {decision}.']}).to_csv(ROOT/'reports/nifty_calendar/P14_PHASE_STATUS.csv',index=False)
    print(sm.to_string(index=False)); print('fresh_cycles',len(cycles),'latest',latest.date(),'decision',decision)

if __name__=='__main__': main()