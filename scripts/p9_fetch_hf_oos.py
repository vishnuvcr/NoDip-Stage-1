from __future__ import annotations

from pathlib import Path
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO_ID='thetrademarkk/india-index-options-1m'
REPO_TYPE='dataset'
ROOT=Path('data/cache/p9_hf_probe_oos')
ROOT.mkdir(parents=True,exist_ok=True)
MANIFEST_OUT=Path('reports/nifty_calendar/P9_HF_OOS_FETCH_MANIFEST.csv')
REPORT_OUT=Path('reports/nifty_calendar/P9_HF_OOS_FETCH_REPORT.md')
CYCLES=Path('reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv')

def main():
    cycles=pd.read_csv(CYCLES)
    cycles=cycles[cycles['status'].eq('EXECUTABLE')].copy()
    for c in ['entry_date','near_expiry','far_expiry']:
        cycles[c]=pd.to_datetime(cycles[c]).dt.strftime('%Y-%m-%d')
    required=sorted(set(cycles['near_expiry'])|set(cycles['far_expiry']))
    api=HfApi()
    files=set(api.list_repo_files(repo_id=REPO_ID,repo_type=REPO_TYPE))
    rows=[]
    for expiry in required:
        filename=f'options/NIFTY/{expiry}.parquet'
        if filename not in files:
            rows.append({'kind':'option','file':filename,'status':'MISSING_FROM_SOURCE','local_path':'','bytes':''})
            continue
        path=hf_hub_download(repo_id=REPO_ID,repo_type=REPO_TYPE,filename=filename)
        rows.append({'kind':'option','file':filename,'status':'DOWNLOADED','local_path':path,'bytes':Path(path).stat().st_size})
    index_file='index/NIFTY.parquet'
    index_path=hf_hub_download(repo_id=REPO_ID,repo_type=REPO_TYPE,filename=index_file)
    rows.append({'kind':'index','file':index_file,'status':'DOWNLOADED','local_path':index_path,'bytes':Path(index_path).stat().st_size})
    out=pd.DataFrame(rows)
    out.to_csv(MANIFEST_OUT,index=False)
    ok=int((out.status=='DOWNLOADED').sum())
    miss=int((out.status=='MISSING_FROM_SOURCE').sum())
    total=int(pd.to_numeric(out.loc[out.status.eq('DOWNLOADED'),'bytes'],errors='coerce').fillna(0).sum())
    REPORT_OUT.write_text('\n'.join([
        '# P9 OOS Hugging Face Fetch Report',
        '',
        f'- OOS executable cycles in request set: {len(cycles)}',
        f'- Unique expiry files requested: {len(required)}',
        f'- Expiry/index files downloaded: {ok}',
        f'- Missing source expiry files: {miss}',
        f'- Bytes downloaded/restored during this lane: {total:,}',
        '- This lane uses only the unseen 2025+ P8 executable-cycle population.'
    ])+'\n',encoding='utf-8')

if __name__=='__main__':
    main()
