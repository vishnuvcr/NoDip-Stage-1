from __future__ import annotations
import argparse, io, re, subprocess, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OFFSETS = [-1, 0, 1, 2, 3, 4, 5]
OFFSET_LABEL = {-1:'D-1',0:'D0',1:'D+1',2:'D+2',3:'D+3',4:'D+4',5:'D+5'}
THRESHOLD = 1.20
HEADERS = {'User-Agent':'Mozilla/5.0 (compatible; NoDip research bot)','Accept':'*/*'}

p8 = importlib.util.spec_from_file_location('p8', ROOT/'scripts/p8_score.py')
p8m = importlib.util.module_from_spec(p8); assert p8.loader is not None; p8.loader.exec_module(p8m)
rec = importlib.util.spec_from_file_location('rec', ROOT/'scripts/reconcile_rejections_nse.py')
recm = importlib.util.module_from_spec(rec); assert rec.loader is not None; rec.loader.exec_module(recm)

def archives(mirror_root: Path) -> dict[pd.Timestamp,str]:
    raw = subprocess.check_output(['git','-C',str(mirror_root),'ls-tree','-r','--name-only','HEAD','data'], text=True)
    pat_new = re.compile(r'data/(?:2024|2025|2026)/\\d{2}/BhavCopy_NSE_FO_0_0_0_(\\d{8})_F_0000\\.csv\\.zip$')
    pat_old = re.compile(r'data/(?:2022|2023|2024)/\\d{2}/fo(\\d{2})([A-Z]{3})(\\d{4})bhav\\.csv\\.zip$')
    out={}
    for line in raw.splitlines():
        x=line.strip(); m=pat_new.match(x)
        if m: out[pd.to_datetime(m.group(1),format='%Y%m%d')]=x; continue
        m=pat_old.match(x)
        if m:
            d=pd.to_datetime(f'{m.group(1)}{m.group(2)}{m.group(3)}',format='%d%b%Y')
            out[d]=x
    if not out: raise RuntimeError('No F&O BhavCopy archives found')
    return dict(sorted(out.items()))

def load_cycles(dev_path: Path, oos_path: Path, trading: list[pd.Timestamp]) -> pd.DataFrame:
    dev=pd.read_csv(dev_path); dev['sample']='DEVELOPMENT'
    oos=pd.read_csv(oos_path); oos['sample']='OOS'
    # Development cycle audit already contains the exact prior expiry.
    dev['previous_expiry']=dev['previous_expiry'].astype(str)
    dev['cycle_id']='DEV_'+dev['candidate_index'].astype(str)
    oos['near_expiry']=pd.to_datetime(oos['near_expiry']).dt.strftime('%Y-%m-%d')
    oos['far_expiry']=pd.to_datetime(oos['far_expiry']).dt.strftime('%Y-%m-%d')
    oos['cycle_id']='OOS_'+oos.index.astype(str)
    exps=sorted(pd.to_datetime(oos['near_expiry']).unique())
    prev={str(exps[i]):str(exps[i-1]) for i in range(1,len(exps))}
    oos['previous_expiry']=oos['near_expiry'].map(prev).fillna('2024-12-26')
    keep=['cycle_id','sample','previous_expiry','near_expiry','far_expiry']
    out=pd.concat([dev[keep],oos[keep]],ignore_index=True)
    return out

def spot_map() -> dict[str,float]:
    s=requests.Session(); start=pd.Timestamp('2022-01-01',tz='Asia/Kolkata'); end=pd.Timestamp('2027-01-01',tz='Asia/Kolkata')
    url='https://query1.finance.yahoo.com/v8/finance/chart/^NSEI'
    p1=int(start.tz_convert('UTC').timestamp()); p2=int(end.tz_convert('UTC').timestamp())
    r=s.get(url,params={'period1':p1,'period2':p2,'interval':'1d','events':'history'},headers=HEADERS,timeout=30); r.raise_for_status()
    js=r.json()['chart']['result'][0]
    ts=js['timestamp']; op=js['indicators']['quote'][0]['open']
    out={}
    for t,v in zip(ts,op):
        if v is None: continue
        d=pd.to_datetime(t,unit='s',utc=True).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
        out[d]=float(v)
    return out

def read_day(mirror_root: Path, rel: str, exps: set[str]) -> pd.DataFrame:
    payload=subprocess.check_output(['git','-C',str(mirror_root),'show','HEAD:'+rel],timeout=90)
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        name=next(n for n in z.namelist() if n.lower().endswith('.csv'))
        raw=pd.read_csv(z.open(name),low_memory=False)
    if 'FinInstrmTp' in raw.columns:
        out=pd.DataFrame({'date':pd.to_datetime(raw['TradDt']),'symbol':raw['TckrSymb'].astype('string').str.strip(),'instrument':raw['FinInstrmTp'].astype('string').str.strip(),'expiry':pd.to_datetime(raw['XpryDt'],errors='coerce'),'strike':pd.to_numeric(raw['StrkPric'],errors='coerce'),'option_type':raw['OptnTp'].astype('string').str.strip(),'open':pd.to_numeric(raw['OpnPric'],errors='coerce'),'close':pd.to_numeric(raw['ClsPric'],errors='coerce'),'contracts':pd.to_numeric(raw['TtlTradgVol'],errors='coerce'),'oi':pd.to_numeric(raw['OpnIntrst'],errors='coerce')})
        out=out[(out.symbol=='NIFTY')&(out.instrument=='IDO')]
    else:
        raw=raw.rename(columns=lambda c:str(c).strip().upper())
        out=pd.DataFrame({'date':pd.to_datetime(raw['TIMESTAMP'],format='%d-%b-%Y',errors='coerce'),'symbol':raw['SYMBOL'].astype('string').str.strip(),'instrument':raw['INSTRUMENT'].astype('string').str.strip(),'expiry':pd.to_datetime(raw['EXPIRY_DT'],format='%d-%b-%Y',errors='coerce'),'strike':pd.to_numeric(raw['STRIKE_PR'],errors='coerce'),'option_type':raw['OPTION_TYP'].astype('string').str.strip(),'open':pd.to_numeric(raw['OPEN'],errors='coerce'),'close':pd.to_numeric(raw['CLOSE'],errors='coerce'),'contracts':pd.to_numeric(raw['CONTRACTS'],errors='coerce'),'oi':pd.to_numeric(raw['OPEN_INT'],errors='coerce')})
        out=out[(out.symbol=='NIFTY')&(out.instrument=='OPTIDX')]
    return out[out['expiry'].dt.strftime('%Y-%m-%d').isin(exps)].copy()

def choose(day: pd.DataFrame, near:str, far:str, spot:float):
    if day is None or day.empty: return None
    x=day[(day.expiry.isin(pd.to_datetime([near,far])))&(day.option_type.isin(['CE','PE']))&(day.open>0)&(day.contracts>0)].copy()
    if x.empty:return None
    n=x[(x.expiry==pd.Timestamp(near))].pivot_table(index='strike',columns='option_type',values='open',aggfunc='last')
    f=x[(x.expiry==pd.Timestamp(far))].pivot_table(index='strike',columns='option_type',values='open',aggfunc='last')
    common=sorted(set(n.dropna().index)&set(f.dropna().index))
    valid=[]
    for k in common:
        ok=True
        for exp,opt in [(near,'CE'),(near,'PE'),(far,'CE'),(far,'PE')]:
            m=x[(x.expiry==pd.Timestamp(exp))&(x.strike==k)&(x.option_type==opt)]
            if len(m)!=1: ok=False; break
        if ok: valid.append(float(k))
    if not valid:return None
    k=min(valid,key=lambda z:(abs(z-spot),z)); return k

def get_price(df, date_s, exp, strike, opt, field):
    m=df[(df.expiry==pd.Timestamp(exp))&(df.strike==float(strike))&(df.option_type==opt)]
    if len(m)!=1:return None
    v=m.iloc[0][field]
    return float(v) if pd.notna(v) and float(v)>0 else None

def evaluate(cycles: pd.DataFrame, trading: list[pd.Timestamp], daily: dict[pd.Timestamp,pd.DataFrame], spots: dict[str,float]) -> pd.DataFrame:
    pos={d:i for i,d in enumerate(trading)}; rows=[]
    for _,c in cycles.iterrows():
        prev=pd.Timestamp(c.previous_expiry); near=str(c.near_expiry); far=str(c.far_expiry)
        if prev not in pos:
            for off in OFFSETS: rows.append({**c.to_dict(),'offset':off,'offset_label':OFFSET_LABEL[off],'entry_date':'','status':'NO_PREVIOUS_EXPIRY'})
            continue
        for off in OFFSETS:
            idx=pos[prev]+off
            base={**c.to_dict(),'offset':off,'offset_label':OFFSET_LABEL[off],'entry_date':'','status':'','status_detail':'','spot_open':np.nan,'strike':np.nan,'cbr':np.nan,'atm_distance_points':np.nan,'atm_distance_pct':np.nan,'pnl_inr':np.nan}
            if idx<0 or idx>=len(trading): base['status']='NO_TRADING_DATE'; rows.append(base); continue
            edate=trading[idx]; base['entry_date']=edate.strftime('%Y-%m-%d')
            if edate>pd.Timestamp(near): base['status']='AFTER_NEAR_EXPIRY'; rows.append(base); continue
            sp=spots.get(base['entry_date'])
            if sp is None: base['status']='MISSING_SPOT'; rows.append(base); continue
            base['spot_open']=sp
            entry=daily.get(edate); exitd=daily.get(pd.Timestamp(near))
            if entry is None or entry.empty: base['status']='NO_ENTRY_SOURCE'; rows.append(base); continue
            if exitd is None or exitd.empty: base['status']='NO_EXIT_SOURCE'; rows.append(base); continue
            strike=choose(entry,near,far,sp)
            if strike is None: base['status']='NO_EXECUTABLE_COMMON_STRIKE'; rows.append(base); continue
            base['strike']=strike; base['atm_distance_points']=abs(strike-sp); base['atm_distance_pct']=base['atm_distance_points']/sp*100
            vals={}
            missing=[]
            for name,exp,opt in [('near_pe',near,'PE'),('near_ce',near,'CE'),('far_ce',far,'CE'),('far_pe',far,'PE')]:
                vals['entry_'+name]=get_price(entry,base['entry_date'],exp,strike,opt,'open')
                if vals['entry_'+name] is None: missing.append('entry_'+name)
                vals['exit_'+name]=get_price(exitd,near, str(exp),strike,opt,'close')
                if vals['exit_'+name] is None: missing.append('exit_'+name)
            if missing: base['status']='MISSING_LEG_PRINT'; base['status_detail']=';'.join(missing); rows.append(base); continue
            base.update(vals)
            base['call_ratio']=vals['entry_far_ce']/vals['entry_near_ce']
            base['put_ratio']=vals['entry_far_pe']/vals['entry_near_pe']
            base['cbr']=base['call_ratio']/base['put_ratio']
            base['gate_pass']=bool(base['cbr']<=THRESHOLD)
            ln=recm.lot_size(near); lf=recm.lot_size(far); base['lot_near']=ln; base['lot_far']=lf
            base['pnl_points']=(vals['exit_near_pe']-vals['entry_near_pe'])-(vals['exit_near_ce']-vals['entry_near_ce'])+(vals['exit_far_ce']-vals['entry_far_ce'])-(vals['exit_far_pe']-vals['entry_far_pe'])
            base['pnl_inr']=(vals['exit_near_pe']-vals['entry_near_pe'])*ln+(vals['entry_near_ce']-vals['exit_near_ce'])*ln+(vals['exit_far_ce']-vals['entry_far_ce'])*lf+(vals['entry_far_pe']-vals['exit_far_pe'])*lf
            base['status']='EXECUTABLE'; base['status_detail']='GATE_PASS' if base['gate_pass'] else 'GATE_FAIL'; rows.append(base)
    return pd.DataFrame(rows)

def strategy_metrics(sub: pd.DataFrame) -> dict:
    x=sub.copy(); x['strategy_pnl']=np.where((x.status=='EXECUTABLE') & x.gate_pass.eq(True),pd.to_numeric(x.pnl_inr,errors='coerce'),0.0)
    a=x.strategy_pnl.to_numpy(float); pos=a[a>0]; neg=a[a<0]; curve=np.cumsum(a); dd=curve-np.maximum.accumulate(curve)
    gross=float(a.sum()); ntr=int(((x.status=='EXECUTABLE')&(x.gate_pass.astype(bool))).sum())
    return {'cycles':len(x),'trades':ntr,'gross':gross,'mean_cycle':float(a.mean()),'win':float((a>0).mean()),'pf':float(pos.sum()/(-neg.sum())) if len(neg) else np.inf,'dd':float(dd.min()),'worst':float(a.min())}

def net_total(sub:pd.DataFrame, slip:float)->float:
    x=sub[(sub.status=='EXECUTABLE') & sub.gate_pass.eq(True)].copy(); total=0.0
    for _,r in x.iterrows(): total+=p8m.net_cost(r,slip,0.0005)
    return float(total)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mirror-root',required=True,type=Path); ap.add_argument('--dev-cycles',required=True,type=Path); ap.add_argument('--oos-cycles',required=True,type=Path); ap.add_argument('--out-ledger',required=True,type=Path); ap.add_argument('--out-summary',required=True,type=Path); ap.add_argument('--out-paired',required=True,type=Path); ap.add_argument('--out-report',required=True,type=Path); args=ap.parse_args()
    files=archives(args.mirror_root); trading=sorted(files); cycles=load_cycles(args.dev_cycles,args.oos_cycles,trading); spots=spot_map()
    req={}
    pos={d:i for i,d in enumerate(trading)}
    for _,c in cycles.iterrows():
        p=pd.Timestamp(c.previous_expiry)
        if p not in pos: continue
        for off in OFFSETS:
            idx=pos[p]+off
            if 0<=idx<len(trading): req.setdefault(trading[idx],set()).update([str(c.near_expiry),str(c.far_expiry)])
        if pd.Timestamp(c.near_expiry) in files: req.setdefault(pd.Timestamp(c.near_expiry),set()).update([str(c.near_expiry),str(c.far_expiry)])
    daily={}
    def task(item):
        d,exps=item; return d, read_day(args.mirror_root,files[d],exps)
    with ThreadPoolExecutor(max_workers=12) as pool:
        futs={pool.submit(task,item):item[0] for item in req.items()}
        for fut in as_completed(futs): d,df=fut.result(); daily[d]=df
    ledger=evaluate(cycles,trading,daily,spots)
    summaries=[]; paired=[]
    for sample in ['DEVELOPMENT','OOS']:
        s=ledger[ledger.sample==sample]
        for off in OFFSETS:
            x=s[s.offset==off]; m=strategy_metrics(x)
            summaries.append({'sample':sample,'offset':off,'offset_label':OFFSET_LABEL[off],**m,'net_0pt':net_total(x,0.0),'net_0.5pt':net_total(x,0.5),'net_1pt':net_total(x,1.0),'net_2pt':net_total(x,2.0),'gate_pass_executable':int(((x.status=='EXECUTABLE') & x.gate_pass.eq(True)).sum()),'executable_cycles':int((x.status=='EXECUTABLE').sum()),'coverage':float((x.status=='EXECUTABLE').mean()),'median_atm_points':float(pd.to_numeric(x.loc[x.status=='EXECUTABLE','atm_distance_points'],errors='coerce').median()) if (x.status=='EXECUTABLE').any() else np.nan})
            base=x[x.offset==1][['cycle_id','status','gate_pass','pnl_inr']].copy()
        base['base_pnl']=np.where((base['status']=='EXECUTABLE') & base['gate_pass'].eq(True),pd.to_numeric(base['pnl_inr'],errors='coerce'),0.0)
        base=base[['cycle_id','base_pnl']]
        if len(base):
            for off in OFFSETS:
                y=x[x.offset==off].copy(); y['strategy_pnl']=np.where((y.status=='EXECUTABLE')&y.gate_pass.eq(True),pd.to_numeric(y.pnl_inr,errors='coerce'),0.0)
                z=base.merge(y[['cycle_id','strategy_pnl']],on='cycle_id',how='inner'); z['delta_vs_Dplus1']=z.strategy_pnl-z.base_pnl
                if off==1: continue
                paired.append({'sample':sample,'offset':off,'offset_label':OFFSET_LABEL[off],'paired_cycles':len(z),'sum_delta_vs_Dplus1':float(z.delta_vs_Dplus1.sum()),'mean_delta_vs_Dplus1':float(z.delta_vs_Dplus1.mean()) if len(z) else np.nan,'median_delta_vs_Dplus1':float(z.delta_vs_Dplus1.median()) if len(z) else np.nan,'offset_higher_cycles':int((z.delta_vs_Dplus1>0).sum()),'offset_lower_cycles':int((z.delta_vs_Dplus1<0).sum()),'same_cycles':int((z.delta_vs_Dplus1==0).sum())})
    outp=args.out_ledger; outp.parent.mkdir(parents=True,exist_ok=True); ledger.to_csv(outp,index=False)
    sm=pd.DataFrame(summaries).sort_values(['sample','offset']); sm.to_csv(args.out_summary,index=False); pd.DataFrame(paired).to_csv(args.out_paired,index=False)
    dev=sm[sm['sample']=='DEVELOPMENT'].sort_values('net_2pt',ascending=False); oos=sm[sm['sample']=='OOS'].sort_values('offset')
    lines=['# P10 Entry-Day Offset Research','', '## Frozen design','- Entry time: 09:15 IST open.','- Gate: CBR <= 1.20; no threshold re-optimization.','- Four-leg structure: buy near PE, sell near CE, buy far CE, sell far PE.','- Near/far expiries remain those of the underlying canonical cycle; exit at near-expiry close.','- Day offsets are defined on NSE trading sessions: D-1 is the session immediately before the previous expiry, D0 is the previous-expiry session, and D+1..D+5 are subsequent trading sessions.','- A candidate after the near-expiry date is marked AFTER_NEAR_EXPIRY and is not a trade.','- Development sample: 2022-2024. OOS sample: 2025 onward.','', '## Development screen (informational; OOS not used to choose a candidate)','']
    for _,r in dev.iterrows(): lines.append(f"- {r.offset_label}: {int(r.trades)} trades / {int(r.cycles)} cycles; gross ₹{r.gross:,.2f}; net at 2pt ₹{r.net_2pt:,.2f}; PF {r.pf:.3f}; coverage {r.coverage:.1%}.")
    lines += ['', '## OOS results — all seven offsets are reported without post-hoc selection','']
    for _,r in oos.iterrows(): lines.append(f"- {r.offset_label}: {int(r.trades)} trades / {int(r.cycles)} cycles; gross ₹{r.gross:,.2f}; net at 0/0.5/1/2pt = ₹{r.net_0pt:,.2f} / ₹{r.net_0.5pt:,.2f} / ₹{r.net_1pt:,.2f} / ₹{r.net_2pt:,.2f}; PF {r.pf:.3f}; drawdown ₹{abs(r.dd):,.2f}.")
    lines += ['', '## Selection rule for any future promotion','- No OOS result is used to choose a winner in this phase. If a single offset is later promoted, it must be selected from the 2022-2024 development sample under a pre-registered rule and then validated on an untouched later period.','', '## Cost model','- Same P8 historical stress model: ₹20/order, eight option executions, statutory charges, 0.05% exchange-charge stress and 0/0.5/1/2 point adverse slippage per execution.','- Cost outputs are modeled and are not claims of realized Paytm Money fills.','', '## Research conclusion status','- This run is a seven-offset timing screen. It does not alter the canonical P8/P9 rules until a development-selected offset survives unseen validation and execution-cost stress.']
    args.out_report.parent.mkdir(parents=True,exist_ok=True); args.out_report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(sm.to_string(index=False)); print('Development screen top by 2-point net:', dev.iloc[0].offset_label if len(dev) else 'none')

if __name__=='__main__': main()
