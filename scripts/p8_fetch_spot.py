from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote
import numpy as np
import pandas as pd
import requests

def fetch(d: pd.Timestamp) -> tuple[str, float]:
    ts = d.tz_localize("Asia/Kolkata")
    p1 = int(ts.tz_convert("UTC").timestamp())
    p2 = int((ts + pd.Timedelta(days=1)).tz_convert("UTC").timestamp())
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + quote("^NSEI", safe="")
    r = requests.get(
        url,
        params={"period1": p1, "period2": p2, "interval": "1d", "events": "history"},
        headers={"User-Agent": "NoDip-research/1.0"},
        timeout=20,
    )
    r.raise_for_status()
    result = r.json()["chart"]["result"][0]
    for value in result["indicators"]["quote"][0].get("open", []):
        if value is not None and np.isfinite(float(value)):
            return d.strftime("%Y-%m-%d"), float(value)
    raise RuntimeError(f"No usable NIFTY open for {d.date()}")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    df = pd.read_csv(args.cycles)
    dates = sorted(set(df.loc[df["entry_date"].astype(bool), "entry_date"]))
    rows = []
    for text in dates:
        d, value = fetch(pd.Timestamp(text))
        rows.append({"entry_date": d, "spot_open": value})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out, index=False)
    print(f"spot_rows={len(rows)}")

if __name__ == "__main__":
    main()
