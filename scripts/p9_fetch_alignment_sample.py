from pathlib import Path
from huggingface_hub import hf_hub_download
import pandas as pd

REPO='thetrademarkk/india-index-options-1m'
FILES=[
 'options/NIFTY/2026-04-07.parquet',
 'options/NIFTY/2026-04-28.parquet',
 'index/NIFTY.parquet'
]
OUT=Path('reports/nifty_calendar/P9_ALIGNMENT_SAMPLE_MANIFEST.csv')

rows=[]
for f in FILES:
    p=hf_hub_download(repo_id=REPO,repo_type='dataset',filename=f)
    rows.append({'file':f,'status':'DOWNLOADED','local_path':p,'bytes':Path(p).stat().st_size})
pd.DataFrame(rows).to_csv(OUT,index=False)
