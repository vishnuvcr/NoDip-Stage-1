from __future__ import annotations

from pathlib import Path
import pandas as pd
import duckdb

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'reports/nifty_calendar/P9_HF_OOS_FETCH_MANIFEST.csv'
P8SPOT=ROOT/'reports/nifty_calendar/P8_SPOT_2025_ONWARD.csv'
OUT=ROOT/'reports/nifty_calendar/P9_SOURCE_ALIGNMENT_AUDIT.md'

DATE='2026-04-01'
NEAR='2026-04-07'
FAR='2026-04-28'

def option_date(con,path,date):
    return con.execute(
        """
        SELECT timestamp, open, close, volume, strike, option_type
        FROM read_parquet(?)
        WHERE CAST(timestamp AS DATE)=CAST(? AS DATE)
          AND option_type IN ('CE','PE')
        ORDER BY timestamp
        """,
        [path,date]
    ).fetch_df()

def idx_date(con,path,date):
    return con.execute(
        """
        SELECT timestamp, close
        FROM read_parquet(?)
        WHERE CAST(timestamp AS DATE)=CAST(? AS DATE)
        ORDER BY timestamp
        """,[path,date]
    ).fetch_df()

def normalize_ts(df,col='timestamp'):
    df[col]=pd.to_datetime(df[col],errors='coerce')
    if getattr(df[col].dt,'tz',None) is not None:
        df[col]=df[col].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    return df

def main():
    con=duckdb.connect()
    con.execute("SET TimeZone='Asia/Kolkata'")
    m=pd.read_csv(MANIFEST)
    pmap={Path(r.file).stem:r.local_path for _,r in m[m.kind.eq('option')&m.status.eq('DOWNLOADED')].iterrows()}
    ipath=m.loc[m.kind.eq('index')&m.status.eq('DOWNLOADED'),'local_path'].iloc[0]

    idx=normalize_ts(idx_date(con,ipath,DATE))
    ne=normalize_ts(option_date(con,pmap[NEAR],DATE))
    fe=normalize_ts(option_date(con,pmap[FAR],DATE))

    exp_spot=pd.read_csv(P8SPOT)
    exp_spot['entry_date']=pd.to_datetime(exp_spot['entry_date']).dt.strftime('%Y-%m-%d') if 'entry_date' in exp_spot.columns else exp_spot.iloc[:,0].astype(str)
    exp_row=exp_spot[exp_spot.iloc[:,0].astype(str).str.startswith(DATE)].head(1)

    lines=[
        '# P9 Primary-Source Timestamp / ATM Alignment Audit','',
        f'- Audit date: {DATE}',
        f'- Near expiry: {NEAR}',
        f'- Far expiry: {FAR}',
        '',
        '## Index timestamps',
        f'- Index rows: {len(idx)}',
        f'- First index timestamp: {idx.timestamp.min()}',
        f'- Last index timestamp: {idx.timestamp.max()}',
        f'- First 10 timestamps: {idx.timestamp.head(10).tolist()}',
        f'- First 10 closes: {idx.close.head(10).tolist()}',
        '',
        '## Reference daily spot open',
        exp_row.to_string(index=False),
        '',
        '## Option timestamps',
        f'- Near rows: {len(ne)}; first timestamp: {ne.timestamp.min()}; last: {ne.timestamp.max()}',
        f'- Far rows: {len(fe)}; first timestamp: {fe.timestamp.min()}; last: {fe.timestamp.max()}',
        f'- Near timestamp sample: {ne.timestamp.head(10).tolist()}',
        f'- Far timestamp sample: {fe.timestamp.head(10).tolist()}',
        '',
    ]

    for tm in ['09:15','09:16','09:22','09:26']:
        t=pd.Timestamp(f'{DATE} {tm}')
        n=ne[ne.timestamp.eq(t)].copy()
        f=fe[fe.timestamp.eq(t)].copy()
        lines += [f'## {tm}',f'- Near rows at exact timestamp: {len(n)}',f'- Far rows at exact timestamp: {len(f)}']
        if n.empty or f.empty:
            lines += ['No complete four-leg common-strike panel.','']
            continue
        def contracts(df,exp):
            y=df[df.option_type.isin(['CE','PE']) & df.volume.fillna(0).gt(0) & df.close.gt(0)].copy()
            piv=y.pivot_table(index='strike',columns='option_type',values=['close','volume'],aggfunc='last')
            out={}
            for strike in piv.index:
                try:
                    ce=float(piv.loc[strike,('close','CE')]); pe=float(piv.loc[strike,('close','PE')])
                    vce=float(piv.loc[strike,('volume','CE')]); vpe=float(piv.loc[strike,('volume','PE')])
                except Exception:
                    continue
                if min(ce,pe,vce,vpe)>0: out[float(strike)]={'ce':ce,'pe':pe}
            return out
        nc=contracts(n,'near'); fc=contracts(f,'far')
        common=sorted(set(nc).intersection(fc))
        if not common:
            lines += ['No complete four-leg common-strike panel.','']
            continue
        ix=idx[idx.timestamp.eq(t)]
        spot=float(ix.close.iloc[0]) if len(ix) else float('nan')
        rows=[]
        for strike in common:
            cr=fc[strike]['ce']/nc[strike]['ce']
            pr=fc[strike]['pe']/nc[strike]['pe']
            cbr=cr/pr
            rows.append({'strike':strike,'spot':spot,'distance_points':abs(strike-spot),'distance_pct':abs(strike-spot)/spot*100,'cbr':cbr})
        snap=pd.DataFrame(rows).sort_values(['distance_points','strike'])
        lines += [snap.head(25).to_string(index=False), '']
    OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__': main()
