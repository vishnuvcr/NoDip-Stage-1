from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import yfinance as yf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    # yfinance end is exclusive.
    end_plus_one = (pd.Timestamp(args.end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.download(
        "^NSEI",
        start=args.start,
        end=end_plus_one,
        auto_adjust=False,
        progress=False,
        actions=False,
    )
    if df.empty:
        raise RuntimeError("No NIFTY spot data returned by Yahoo Finance")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    out = pd.DataFrame({
        "date": pd.to_datetime(df.index).tz_localize(None).normalize(),
        "open": pd.to_numeric(df["Open"], errors="coerce"),
        "high": pd.to_numeric(df["High"], errors="coerce"),
        "low": pd.to_numeric(df["Low"], errors="coerce"),
        "close": pd.to_numeric(df["Close"], errors="coerce"),
    }).dropna(subset=["open"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"Saved {len(out)} spot sessions to {args.out}")

if __name__ == "__main__":
    main()
