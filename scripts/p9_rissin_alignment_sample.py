from __future__ import annotations
from pathlib import Path
import duckdb
import pandas as pd

OUT=Path('reports/nifty_calendar/P9_RISSIN_ALIGNMENT_SAMPLE.csv')
DATES=[
 ('2025-02-07','2025-02-13','2025-03-06'),
 ('2025-05-02','2025-05-08','2025-05-29'),
 ('2025-09-03','2025-09-09','2025-09-30'),
 ('2026-04-01','2026-04-07','2026-04-28'),
 ('2026-07-01','2026-07-07','2026-07-28')
]
RISSIN2025="hf://datasets/rissin/nse-options-intraday/upstox_intraday/NIFTY/NIFTY_2025.parquet"
RISSIN2026="hf://datasets/rissin/nse-options-intraday/upstox_intraday/NIFTY/NIFTY_2026.parquet"
SPOT="hf://datasets/thetrademarkk/india-index-options-1m/index/NIFTY.parquet"

def read(con,path,date,near,far):
    q=f"""
    SELECT timestamp,date,expiry,strike,option_type,open,close,volume
    FROM read_parquet('{path}')
    WHERE date='{date}' AND expiry IN ('{near}','{far}') AND option_type IN ('CE','PE')
    """
    df=con.execute(q).fetch_df()
    if not df.empty:
        df['timestamp']=pd.to_datetime(df['timestamp'],errors='coerce')
        if getattr(df['timestamp'].dt,'tz',None) is not None:
            df['timestamp']=df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        for c in ['open','close','volume','strike']: df[c]=pd.to_numeric(df[c],errors='coerce')
        df['expiry']=df['expiry'].astype(str)
    return df

def main():
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=8")
    rows=[]
    for ed,ne,fe in DATES:
        path=RISSIN2025 if ed.startswith('2025') else RISSIN2026
        x=read(con,path,ed,ne,fe)
        if x.empty:
            rows.append({'entry_date':ed,'near_expiry':ne,'far_expiry':fe,'near_rows':0,'far_rows':0,'common_strike_sample':''})
            continue
        n=x[x.expiry.eq(ne)&x.volume.fillna(0).gt(0)&x.close.gt(0)]
        f=x[x.expiry.eq(fe)&x.volume.fillna(0).gt(0)&x.close.gt(0)]
        n=n.pivot_table(index=['timestamp','strike'],columns='option_type',values=['close','volume'],aggfunc='last').reset_index()
        f=f.pivot_table(index=['timestamp','strike'],columns='option_type',values=['close','volume'],aggfunc='last').reset_index()
        if len(n)==0 or len(f)==0:
            common=pd.DataFrame()
        else:
            common=n.merge(f,on=['timestamp','strike'],how='inner')
        complete=0
        sample=[]
        if len(common):
            cols=[('close','CE'),('close','PE'),('volume','CE'),('volume','PE')]
            flat=[]
            for pref in ['near','far']:
                for col in cols:
                    flat.append(f'{pref}_{col[0]}_{col[1]}')
            common.columns=[f'{a}_{b}' if b else a for a,b in common.columns.to_flat_index()] if isinstance(common.columns,pd.MultiIndex) else common.columns
            # rebuild simple names robustly
            req=[c for c in common.columns if ('close_CE' in c or 'close_PE' in c or 'volume_CE' in c or 'volume_PE' in c)]
            # count timestamps with >=1 complete strike
            for _,g in common.groupby('timestamp'):
                for strike,gg in g.groupby('strike'):
                    txt=gg.to_string(index=False)
                    sample.append(float(strike))
                    complete+=1
            sample=sorted(set(sample))[:10]
        rows.append({'entry_date':ed,'near_expiry':ne,'far_expiry':fe,'near_rows':len(n),'far_rows':len(f),'common_strike_sample':';'.join(map(str,sample[:10])),'common_panel_rows':complete})
    pd.DataFrame(rows).to_csv(OUT,index=False)
if __name__=='__main__': main()
