from __future__ import annotations

import argparse
from pathlib import Path
import re

import pandas as pd
import requests


REPO_API = "https://api.github.com/repos/NagarajuGunda/NSEIndexOptionsData/contents"
RAW_BASE = "https://raw.githubusercontent.com/NagarajuGunda/NSEIndexOptionsData/main"


def list_month_files(year: int):
    r = requests.get(f"{REPO_API}/{year}/nifty", timeout=60)
    r.raise_for_status()
    items = r.json()
    files = []
    for item in items:
        name = item.get("name", "")
        if item.get("type") == "file" and name.endswith(".parquet") and name[:-8].isdigit():
            files.append(int(name[:-8]))
    return sorted(files)


def download_month(year: int, month: int, out_dir: Path) -> Path:
    out = out_dir / f"{year}_{month:02d}.parquet"
    if out.exists() and out.stat().st_size > 100_000:
        return out
    url = f"{RAW_BASE}/{year}/nifty/{month:02d}.parquet"
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_bytes(r.content)
    return out


def parse_ticker(ticker: str):
    if ticker == "NIFTY":
        return None
    m = re.match(r"^NIFTY(?P<expiry>\d{2}[A-Z]{3}\d{2})(?P<option>[CP]E)(?P<strike>\d+)$", ticker)
    if not m:
        return None
    return (
        pd.to_datetime(m.group("expiry"), format="%d%b%y"),
        m.group("option"),
        float(m.group("strike")),
    )


def historical_lot(expiry: pd.Timestamp) -> int:
    if expiry < pd.Timestamp("2024-05-02"):
        return 50
    if expiry < pd.Timestamp("2025-01-02"):
        return 25
    if expiry < pd.Timestamp("2026-01-06"):
        return 75
    return 65


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024])
    ap.add_argument("--raw-dir", type=Path, required=True)
    ap.add_argument("--fo-out", type=Path, required=True)
    ap.add_argument("--spot-out", type=Path, required=True)
    args = ap.parse_args()

    fo_parts = []
    spot_parts = []

    for year in args.years:
        months = list_month_files(year)
        if not months:
            raise RuntimeError(f"No NIFTY monthly parquet files found for {year}")
        print(f"{year}: available months {months}")

        for month in months:
            path = download_month(year, month, args.raw_dir)
            print(f"Reading {path}")
            df = pd.read_parquet(path)
            df["Date/Time"] = pd.to_datetime(df["Date/Time"])
            df["Ticker"] = df["Ticker"].astype(str)

            spot = df[df["Ticker"].eq("NIFTY")][["Date/Time", "Open"]].copy()
            spot_parts.append(spot)

            opt = df[df["Ticker"].ne("NIFTY")][
                ["Ticker", "Date/Time", "Open", "Close", "Volume", "Open Interest"]
            ].copy()

            parsed = opt["Ticker"].map(parse_ticker)
            valid = parsed.notna()
            opt = opt.loc[valid].copy()
            parsed = parsed.loc[valid]
            opt["expiry"] = parsed.map(lambda x: x[0])
            opt["option_type"] = parsed.map(lambda x: x[1])
            opt["strike"] = parsed.map(lambda x: x[2])
            opt["symbol"] = "NIFTY"
            opt["date"] = opt["Date/Time"].dt.normalize()
            opt["time"] = opt["Date/Time"].dt.strftime("%H:%M")

            opens = opt[opt["time"].eq("09:15")][
                ["date", "symbol", "expiry", "strike", "option_type", "Open"]
            ].rename(columns={"Open": "open"})

            closes = (
                opt.sort_values("Date/Time")
                .groupby(
                    ["date", "symbol", "expiry", "strike", "option_type"],
                    as_index=False,
                )
                .tail(1)
            )[["date", "symbol", "expiry", "strike", "option_type", "Close"]].rename(
                columns={"Close": "close"}
            )

            daily = opens.merge(
                closes,
                on=["date", "symbol", "expiry", "strike", "option_type"],
                how="outer",
            )
            daily["lot_size"] = daily["expiry"].map(historical_lot)
            fo_parts.append(daily)

    fo = pd.concat(fo_parts, ignore_index=True)
    fo = (
        fo.sort_values(["date", "expiry", "strike", "option_type"])
        .drop_duplicates(["date", "expiry", "strike", "option_type"], keep="last")
        .reset_index(drop=True)
    )

    spot = pd.concat(spot_parts, ignore_index=True)
    spot["date"] = spot["Date/Time"].dt.normalize()
    spot["time"] = spot["Date/Time"].dt.strftime("%H:%M")
    spot = (
        spot[spot["time"].eq("09:15")]
        .sort_values("Date/Time")
        .drop_duplicates("date", keep="last")
        .rename(columns={"Open": "open"})[["date", "open"]]
        .reset_index(drop=True)
    )

    args.fo_out.parent.mkdir(parents=True, exist_ok=True)
    args.spot_out.parent.mkdir(parents=True, exist_ok=True)
    fo.to_parquet(args.fo_out, index=False)
    spot.to_csv(args.spot_out, index=False)

    print(f"Prepared {len(fo):,} NIFTY option daily rows")
    print(f"Prepared {len(spot):,} NIFTY spot sessions")


if __name__ == "__main__":
    main()
