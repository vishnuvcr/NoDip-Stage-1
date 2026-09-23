from __future__ import annotations

from pathlib import Path
import pandas as pd

MANIFEST=Path('reports/nifty_calendar/P9_HF_FETCH_MANIFEST.csv')
OUT_MD=Path('reports/nifty_calendar/P9_HF_SCHEMA_VALIDATION.md')
OUT_CSV=Path('reports/nifty_calendar/P9_HF_SCHEMA_SUMMARY.csv')

REQ_OPTION={'timestamp','open','high','low','close','volume','open_interest','strike','option_type','expiry'}
REQ_INDEX={'timestamp','open','high','low','close'}

def check_file(path:str, kind:str):
    if kind=='index':
        df=pd.read_parquet(path, columns=['timestamp','open','high','low','close'])
        req=REQ_INDEX
    else:
        df=pd.read_parquet(path, columns=['timestamp','open','high','low','close','volume','open_interest','strike','option_type','expiry'])
        req=REQ_OPTION
    cols=set(df.columns)
    missing=sorted(req-cols)
    result={'rows':len(df),'missing_columns':';'.join(missing),'min_timestamp':'','max_timestamp':'','ce_rows':None,'pe_rows':None,'positive_volume_ratio':None,'positive_close_ratio':None}
    if len(df):
        ts=pd.to_datetime(df['timestamp'], errors='coerce')
        result['min_timestamp']=str(ts.min())
        result['max_timestamp']=str(ts.max())
        if kind=='option':
            result['ce_rows']=int((df['option_type'].astype(str).str.upper()=='CE').sum())
            result['pe_rows']=int((df['option_type'].astype(str).str.upper()=='PE').sum())
            result['positive_volume_ratio']=float((pd.to_numeric(df['volume'],errors='coerce').fillna(0)>0).mean())
            result['positive_close_ratio']=float((pd.to_numeric(df['close'],errors='coerce').fillna(0)>0).mean())
    return result

def main():
    m=pd.read_csv(MANIFEST)
    rows=[]
    for _,r in m[m['status'].eq('DOWNLOADED')].iterrows():
        try:
            kind='index' if r['kind']=='index' else 'option'
            z=check_file(r['local_path'],kind)
            z.update({'kind':kind,'file':r['file'],'status':'OK' if not z['missing_columns'] else 'SCHEMA_MISSING'})
            rows.append(z)
        except Exception as e:
            rows.append({'kind':r['kind'],'file':r['file'],'status':'READ_ERROR:'+type(e).__name__,'rows':0,'missing_columns':'','min_timestamp':'','max_timestamp':'','ce_rows':None,'pe_rows':None,'positive_volume_ratio':None,'positive_close_ratio':None})
    out=pd.DataFrame(rows)
    out.to_csv(OUT_CSV,index=False)
    option=out[out['kind'].eq('option')]
    ok=int((out['status']=='OK').sum())
    errors=int((out['status']!='OK').sum())
    ce_missing=int((option['ce_rows'].fillna(0)==0).sum()) if len(option) else 0
    pe_missing=int((option['pe_rows'].fillna(0)==0).sum()) if len(option) else 0
    md=[
        '# P9 Hugging Face Schema Validation',
        '',
        f'- Downloaded files inspected: {len(out)}',
        f'- Files passing required-column schema: {ok}',
        f'- Files with read/schema errors: {errors}',
        f'- Option files with no CE rows: {ce_missing}',
        f'- Option files with no PE rows: {pe_missing}',
        '',
        'The source is considered usable for the P9 historical timing scan only when the four-leg panels can be reconstructed at timestamp level. This file validates parquet readability and schema; it is not itself a trading result.',
    ]
    OUT_MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
    if errors:
        raise SystemExit(2)

if __name__=='__main__': main()