from __future__ import annotations

import argparse
from pathlib import Path

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


def historical_lot(expiry: pd.Timestamp) -> int:
    if expiry < pd.Timestamp("2024-05-02"):
        return 50
    if expiry < pd.Timestamp("2025-01-02"):
        return 25
    if expiry < pd.Timestamp("2026-01-06"):
        return 75
    return 65


def parse_options_vectorized(opt: pd.DataFrame) -> pd.DataFrame:
    # Public mirror ticker schema observed in CI:
    # NIFTY04JAN24C18300 / NIFTY04JAN24P18300
    extracted = opt["Ticker"].str.extract(
        r"^NIFTY(?P<expiry>\d{2}[A-Z]{3}\d{2})(?P<option>[CP])(?P<strike>\d+)$"
    )

    valid = extracted["expiry"].notna()
    print(f"Parsed option rows: {int(valid.sum()):,}/{len(opt):,}")
    if not valid.any():
        print(
            "Ticker parser produced zero matches. Sample:",
            opt["Ticker"].drop_duplicates().head(20).tolist(),
        )
        return pd.DataFrame(
            columns=[
                "date",
                "symbol",
                "expiry",
                "strike",
                "option_type",
                "open",
                "close",
                "lot_size",
                "Date/Time",
            ]
        )

    out = opt.loc[valid].copy()
    parsed = extracted.loc[valid]
    out["expiry"] = pd.to_datetime(
        parsed["expiry"], format="%d%b%y", errors="coerce"
    )
    out["option_type"] = parsed["option"].astype(str)
    out["strike"] = pd.to_numeric(parsed["strike"], errors="coerce")
    out["symbol"] = "NIFTY"
    out["date"] = out["Date/Time"].dt.normalize()
    out["time"] = out["Date/Time"].dt.strftime("%H:%M")
    return out


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

            raw_nonspot = df.loc[df["Ticker"].ne("NIFTY"), "Ticker"]
            print("Ticker sample:", raw_nonspot.drop_duplicates().head(20).tolist())

            spot = df[df["Ticker"].eq("NIFTY")][["Date/Time", "Open"]].copy()
            spot_parts.append(spot)

            opt = df.loc[
                df["Ticker"].ne("NIFTY"),
                ["Ticker", "Date/Time", "Open", "Close", "Volume", "Open Interest"],
            ].copy()

            opt = parse_options_vectorized(opt)
            if opt.empty:
                raise RuntimeError(
                    f"No option tickers parsed from {year}-{month:02d}; "
                    "stop instead of silently producing a zero-trade backtest."
                )

            opens = opt.loc[
                opt["time"].eq("09:15"),
                ["date", "symbol", "expiry", "strike", "option_type", "Open"],
            ].rename(columns={"Open": "open"})

            closes = (
                opt.sort_values("Date/Time")
                .groupby(
                    ["date", "symbol", "expiry", "strike", "option_type"],
                    as_index=False,
                )
                .tail(1)
            )[
                ["date", "symbol", "expiry", "strike", "option_type", "Close"]
            ].rename(columns={"Close": "close"})

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
        .drop_duplicates(
            ["date", "expiry", "strike", "option_type"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    spot = pd.concat(spot_parts, ignore_index=True)
    spot["date"] = spot["Date/Time"].dt.normalize()
    spot["time"] = spot["Date/Time"].dt.strftime("%H:%M")
    spot = (
        spot.loc[spot["time"].eq("09:15")]
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
