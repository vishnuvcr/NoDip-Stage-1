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
        if n.empty or f.empty:
            lines += [f'## {tm} — no complete timestamp panel','']
            continue
        npiv=n.pivot_table(index='strike',columns='option_type',values=['close','volume'],aggfunc='last')
        fpiv=f.pivot_table(index='strike',columns='option_type',values=['close','volume'],aggfunc='last')
        common=npiv.join(fpiv,lsuffix='_near',rsuffix='_far',how='inner')
        # flatten access by checking column tuples
        rows=[]
        for strike in common.index:
            try:
                ce_n=float(common.loc[strike,('close','CE')])
                pe_n=float(common.loc[strike,('close','PE')])
                ce_f=float(common.loc[strike,('close_far','CE')])
                pe_f=float(common.loc[strike,('close_far','PE')])
            except Exception:
                continue
            rows.append((float(strike),ce_n,pe_n,ce_f,pe_f))
        snap=pd.DataFrame(rows,columns=['strike','near_ce','near_pe','far_ce','far_pe'])
        lines += [f'## {tm}',f'- Near rows at exact timestamp: {len(n)}',f'- Far rows at exact timestamp: {len(f)}']
        lines += [snap.sort_values('strike').head(15).to_string(index=False)] if len(snap) else ['No complete CE/PE common-strike rows.']
        lines += ['']

    OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__': main()
