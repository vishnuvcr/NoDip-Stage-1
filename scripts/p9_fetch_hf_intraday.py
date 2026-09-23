from __future__ import annotations

import csv
import os
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO_ID = 'thetrademarkk/india-index-options-1m'
REPO_TYPE = 'dataset'
ROOT = Path('data/cache/p9_hf_probe')
ROOT.mkdir(parents=True, exist_ok=True)
CYCLES = ROOT / 'P9_CYCLE_MANIFEST.csv'
MANIFEST_OUT = Path('reports/nifty_calendar/P9_HF_FETCH_MANIFEST.csv')
REPORT_OUT = Path('reports/nifty_calendar/P9_HF_FETCH_REPORT.md')

def load_cycles() -> pd.DataFrame:
    strict = pd.read_csv('reports/nifty_calendar/STRICT_TRADE_LEVEL_RESULTS_2022_2024.csv', usecols=['entry_date','near_expiry','far_expiry','strike'])
    oos = pd.read_csv('reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv', usecols=['entry_date','near_expiry','far_expiry','strike','status'])
    oos = oos[oos['status'].eq('EXECUTABLE')].drop(columns=['status'])
    df = pd.concat([strict, oos], ignore_index=True)
    df['entry_date'] = pd.to_datetime(df['entry_date']).dt.date.astype(str)
    df['near_expiry'] = pd.to_datetime(df['near_expiry']).dt.date.astype(str)
    df['far_expiry'] = pd.to_datetime(df['far_expiry']).dt.date.astype(str)
    return df.drop_duplicates().sort_values(['entry_date','near_expiry','far_expiry']).reset_index(drop=True)

def main() -> None:
    cycles = load_cycles()
    cycles.to_csv(CYCLES, index=False)
    api = HfApi()
    files = api.list_repo_files(repo_id=REPO_ID, repo_type=REPO_TYPE)
    option_files = sorted(f for f in files if f.startswith('options/NIFTY/') and f.endswith('.parquet'))
    required_expiries = sorted(set(cycles['near_expiry']) | set(cycles['far_expiry']))
    available = {Path(f).stem for f in option_files}
    rows = []
    for expiry in required_expiries:
        filename = f'options/NIFTY/{expiry}.parquet'
        if expiry not in available:
            rows.append({'kind':'option','file':filename,'status':'MISSING_FROM_SOURCE','local_path':'','bytes':''})
            continue
        path = hf_hub_download(repo_id=REPO_ID, repo_type=REPO_TYPE, filename=filename)
        size = Path(path).stat().st_size
        rows.append({'kind':'option','file':filename,'status':'DOWNLOADED','local_path':path,'bytes':size})
    index_file = 'index/NIFTY.parquet'
    index_path = hf_hub_download(repo_id=REPO_ID, repo_type=REPO_TYPE, filename=index_file)
    rows.append({'kind':'index','file':index_file,'status':'DOWNLOADED','local_path':index_path,'bytes':Path(index_path).stat().st_size})
    pd.DataFrame(rows).to_csv(MANIFEST_OUT, index=False)
    m = pd.DataFrame(rows)
    ok = int((m['status']=='DOWNLOADED').sum())
    miss = int((m['status']=='MISSING_FROM_SOURCE').sum())
    total_bytes = int(pd.to_numeric(m.loc[m['status']=='DOWNLOADED','bytes'], errors='coerce').fillna(0).sum())
    lines = [
        '# P9 Hugging Face Fetch Report',
        '',
        f'- Source: `{REPO_ID}`',
        f'- Eligible cycles requested: {len(cycles)}',
        f'- Unique option expiry files required: {len(required_expiries)}',
        f'- Files downloaded successfully: {ok}',
        f'- Files missing from source manifest: {miss}',
        f'- Bytes downloaded: {total_bytes:,}',
        f'- NIFTY 1-minute index file: {index_file}',
        '',
        'This phase only verifies source accessibility and caches the required expiry/index files in the runner. No P9 strategy performance is computed here.',
    ]
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()