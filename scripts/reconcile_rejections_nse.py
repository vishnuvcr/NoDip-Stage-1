from __future__ import annotations

import argparse
import io
import math
import subprocess
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests


NSE_BASE = "https://nsearchives.nseindia.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NoDip research bot)",
    "Accept": "*/*",
    "Connection": "keep-alive",
}
UDIFF_START = pd.Timestamp("2024-07-08")


def nse_url(d: date) -> str:
    ts = pd.Timestamp(d)
    if ts >= UDIFF_START:
        return f"{NSE_BASE}/content/fo/BhavCopy_NSE_FO_0_0_0_{ts:%Y%m%d}_F_0000.csv.zip"
    mon = ts.strftime("%b").upper()
    return f"{NSE_BASE}/content/historical/DERIVATIVES/{ts:%Y}/{mon}/fo{ts:%d}{mon}{ts:%Y}bhav.csv.zip"


def download_day(
    d: date,
    cache_dir: Path,
    mirror_root: Path,
) -> tuple[date, Path | None, str | None]:
    out = cache_dir / f"{d:%Y%m%d}.zip"
    if out.exists() and out.stat().st_size > 1000:
        return d, out, None

    ts = pd.Timestamp(d)
    if ts >= UDIFF_START:
        mirror_name = f"BhavCopy_NSE_FO_0_0_0_{ts:%Y%m%d}_F_0000.csv.zip"
    else:
        mirror_name = "fo" + f"{ts:%d}" + ts.strftime("%b").upper() + f"{ts:%Y}bhav.csv.zip"

    rel = Path("data") / f"{ts:%Y}" / f"{ts:%m}" / mirror_name
    git_path = str(rel).replace("\\", "/")
    try:
        proc = subprocess.run(
            ["git", "-C", str(mirror_root), "show", f"HEAD:{git_path}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=45,
        )
        payload = proc.stdout
        if not payload.startswith(b"PK"):
            return d, None, f"GitHub mirror non-zip payload for {git_path}"
        tmp = out.with_suffix(".part")
        tmp.write_bytes(payload)
        tmp.replace(out)
        return d, out, None
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.decode("utf-8", errors="replace").strip().splitlines()
        return d, None, f"GitHub mirror git-show failed for {git_path}: {err[-1] if err else 'unknown'}"
    except Exception as exc:
        return d, None, f"GitHub mirror local access failed for {git_path}: {repr(exc)}"


def read_nifty_options(path: Path, d: date) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        csv_name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
        with zf.open(csv_name) as fh:
            raw = pd.read_csv(fh, low_memory=False)

    if "FinInstrmTp" in raw.columns:
        out = pd.DataFrame({
            "date": pd.to_datetime(raw["TradDt"]),
            "symbol": raw["TckrSymb"].astype("string").str.strip(),
            "instrument": raw["FinInstrmTp"].astype("string").str.strip(),
            "expiry": pd.to_datetime(raw["XpryDt"], errors="coerce"),
            "strike": pd.to_numeric(raw["StrkPric"], errors="coerce"),
            "option_type": raw["OptnTp"].astype("string").str.strip(),
            "open": pd.to_numeric(raw["OpnPric"], errors="coerce"),
            "close": pd.to_numeric(raw["ClsPric"], errors="coerce"),
            "contracts": pd.to_numeric(raw["TtlTradgVol"], errors="coerce"),
            "oi": pd.to_numeric(raw["OpnIntrst"], errors="coerce"),
            "underlying": pd.to_numeric(raw["UndrlygPric"], errors="coerce"),
        })
        out = out[(out["symbol"] == "NIFTY") & (out["instrument"] == "IDO")]
    else:
        raw = raw.rename(columns=lambda c: str(c).strip().upper())
        out = pd.DataFrame({
            "date": pd.to_datetime(raw["TIMESTAMP"], format="%d-%b-%Y", errors="coerce"),
            "symbol": raw["SYMBOL"].astype("string").str.strip(),
            "instrument": raw["INSTRUMENT"].astype("string").str.strip(),
            "expiry": pd.to_datetime(raw["EXPIRY_DT"], format="%d-%b-%Y", errors="coerce"),
            "strike": pd.to_numeric(raw["STRIKE_PR"], errors="coerce"),
            "option_type": raw["OPTION_TYP"].astype("string").str.strip(),
            "open": pd.to_numeric(raw["OPEN"], errors="coerce"),
            "close": pd.to_numeric(raw["CLOSE"], errors="coerce"),
            "contracts": pd.to_numeric(raw["CONTRACTS"], errors="coerce"),
            "oi": pd.to_numeric(raw["OPEN_INT"], errors="coerce"),
            "underlying": pd.NA,
        })
        out = out[(out["symbol"] == "NIFTY") & (out["instrument"] == "OPTIDX")]

    return out[[
        "date", "symbol", "expiry", "strike", "option_type",
        "open", "close", "contracts", "oi", "underlying",
    ]].reset_index(drop=True)


def yahoo_open(entry_date: str, session: requests.Session) -> float | None:
    d = pd.Timestamp(entry_date, tz="Asia/Kolkata")
    start = int(d.tz_convert("UTC").timestamp())
    end = int((d + pd.Timedelta(days=1)).tz_convert("UTC").timestamp())
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI"
        f"?period1={start}&period2={end}&interval=1d&events=history"
    )
    r = session.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    js = r.json()
    result = js["chart"]["result"]
    if not result:
        return None
    q = result[0]["indicators"]["quote"][0]
    vals = q.get("open") or []
    for v in vals:
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            return float(v)
    return None


def lot_size(expiry: str) -> int:
    e = pd.Timestamp(expiry)
    if e < pd.Timestamp("2024-05-02"):
        return 50
    if e < pd.Timestamp("2025-01-02"):
        return 25
    if e < pd.Timestamp("2026-01-06"):
        return 75
    return 65


def rows_for(df: pd.DataFrame, dt: str, expiry: str, strike: float, opt: str) -> pd.DataFrame:
    return df[
        (df["date"].dt.normalize() == pd.Timestamp(dt))
        & (df["expiry"].dt.normalize() == pd.Timestamp(expiry))
        & (df["strike"] == float(strike))
        & (df["option_type"] == opt)
    ]


def choose_common_strike(day: pd.DataFrame, near: str, far: str, spot_open: float) -> float | None:
    sub = day[
        day["expiry"].isin([pd.Timestamp(near), pd.Timestamp(far)])
        & day["option_type"].isin(["CE", "PE"])
    ]
    n = set(sub[(sub["expiry"] == pd.Timestamp(near)) & sub["open"].gt(0)]["strike"].dropna().unique())
    f = set(sub[(sub["expiry"] == pd.Timestamp(far)) & sub["open"].gt(0)]["strike"].dropna().unique())
    common = sorted(n & f)
    if not common:
        return None
    return float(min(common, key=lambda k: (abs(k - spot_open), k)))


def secondary_cycle(cycle: pd.Series, daily: dict[pd.Timestamp, pd.DataFrame], yahoo: float | None) -> dict:
    entry = cycle["entry_date"]
    near = cycle["near_expiry"]
    far = cycle["far_expiry"]
    primary_spot = float(cycle["spot_open"])
    secondary_spot = float(yahoo) if yahoo is not None else primary_spot
    entry_df = daily.get(pd.Timestamp(entry))
    exit_df = daily.get(pd.Timestamp(near))

    row = {
        "entry_date": entry,
        "near_expiry": near,
        "far_expiry": far,
        "secondary_spot_open": secondary_spot,
        "primary_spot_open": primary_spot,
        "spot_abs_diff": abs(secondary_spot - primary_spot),
        "primary_reason": cycle["primary_reason"],
        "primary_strike": cycle["primary_strike"],
        "secondary_strike": "",
        "secondary_status": "",
        "comparison_status": "",
        "strike_mode": "",
        "secondary_missing_entry": "",
        "secondary_missing_exit": "",
        "secondary_max_abs_price_diff": "",
        "secondary_pnl_inr": "",
    }

    if entry_df is None or exit_df is None:
        row["secondary_status"] = "SECONDARY_SOURCE_GAP"
        return row

    primary_strike = pd.to_numeric(pd.Series([cycle.get("primary_strike", None)]), errors="coerce").iloc[0]
    # Independently re-apply the frozen ATM/common-strike rule using the
    # secondary spot-open diagnostic. This strike drives the independent P&L.
    strike = choose_common_strike(entry_df, near, far, secondary_spot)
    if strike is None:
        row["secondary_status"] = "SECONDARY_CONFIRMS_NO_COMMON_STRIKE"
        row["strike_mode"] = "NO_COMMON_STRIKE"
        return row
    row["secondary_strike"] = strike
    row["strike_mode"] = (
        "SAME_AS_PRIMARY_STRIKE"
        if pd.notna(primary_strike) and float(primary_strike) == float(strike)
        else "SECONDARY_RESELECTED_STRIKE"
    )
    legs = {
        "near_pe": (near, "PE"),
        "near_ce": (near, "CE"),
        "far_ce": (far, "CE"),
        "far_pe": (far, "PE"),
    }
    exits = legs.copy()

    missing_entry = []
    missing_exit = []
    diffs = []
    prices = {}

    for name, (exp, opt) in legs.items():
        m = rows_for(entry_df, entry, exp, strike, opt)
        if len(m) != 1 or m["open"].isna().sum() != 0 or float(m.iloc[0]["open"]) <= 0:
            missing_entry.append(name)
        if len(m) == 1:
            prices[f"entry_{name}"] = float(m.iloc[0]["open"])
            p = m.iloc[0]["open"]
            prim_col = f"primary_{name}_open"
            prim_val = pd.to_numeric(pd.Series([cycle.get(prim_col, None)]), errors="coerce").iloc[0]
            if pd.notna(prim_val) and pd.notna(p):
                diffs.append(abs(float(prim_val) - float(p)))

        m2 = rows_for(exit_df, near, exp, strike, opt)
        if len(m2) != 1 or m2["close"].isna().sum() != 0:
            missing_exit.append(name)
        if len(m2) == 1:
            prices[f"exit_{name}"] = float(m2.iloc[0]["close"])
            p = m2.iloc[0]["close"]
            prim_col = f"primary_{name}_close"
            if prim_col in cycle.index and pd.notna(cycle[prim_col]) and pd.notna(p):
                diffs.append(abs(float(cycle[prim_col]) - float(p)))

    row["secondary_missing_entry"] = ";".join(missing_entry)
    row["secondary_missing_exit"] = ";".join(missing_exit)
    row["secondary_max_abs_price_diff"] = max(diffs) if diffs else ""

    if missing_entry:
        row["secondary_status"] = "SECONDARY_CONFIRMS_MISSING_ENTRY"
        return row
    if missing_exit:
        row["secondary_status"] = "SECONDARY_CONFIRMS_MISSING_EXIT"
        return row

    ns = lot_size(near)
    fs = lot_size(far)
    pnl = (
        (prices["exit_near_pe"] - prices["entry_near_pe"]) * ns
        + (prices["entry_near_ce"] - prices["exit_near_ce"]) * ns
        + (prices["exit_far_ce"] - prices["entry_far_ce"]) * fs
        + (prices["entry_far_pe"] - prices["exit_far_pe"]) * fs
    )
    row["secondary_pnl_inr"] = pnl
    row["secondary_status"] = "SECONDARY_COMPLETE"
    row["secondary_strike"] = strike
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--rows-out", required=True, type=Path)
    ap.add_argument("--cache-dir", required=True, type=Path)
    ap.add_argument("--mirror-root", required=True, type=Path)
    ap.add_argument("--rejected-only", action="store_true",
                    help="Reconcile every rejected cycle and skip primary-valid cycles.")
    ap.add_argument("--valid-sample", type=int, default=0,
                    help="Also reconcile this many deterministic evenly-spaced primary-valid cycles.")
    args = ap.parse_args()

    audit = pd.read_csv(args.audit)
    if audit.empty:
        raise SystemExit("Cycle audit is empty")

    rejected = audit[audit["primary_reason"] != "VALID"].copy()
    valid = audit[audit["primary_reason"] == "VALID"].copy()

    if args.rejected_only:
        scope = rejected
        if args.valid_sample > 0 and not valid.empty:
            k = min(args.valid_sample, len(valid))
            if k == 1:
                picked = valid.iloc[[len(valid) // 2]]
            else:
                positions = [
                    round(i * (len(valid) - 1) / (k - 1))
                    for i in range(k)
                ]
                picked = valid.iloc[positions]
            scope = pd.concat([scope, picked], ignore_index=True)
    else:
        scope = audit.copy()

    audit = scope
    recon_set = audit.copy()
    if audit.empty:
        raise SystemExit("Selected reconciliation scope is empty")

    dates = set()
    for _, r in audit.iterrows():
        dates.add(pd.Timestamp(r["entry_date"]).date())
        dates.add(pd.Timestamp(r["near_expiry"]).date())

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    downloads = {}

    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {
            pool.submit(download_day, d, args.cache_dir, args.mirror_root): d
            for d in sorted(dates)
        }
        for fut in as_completed(futs):
            d, path, err = fut.result()
            downloads[pd.Timestamp(d)] = (path, err)

    daily: dict[pd.Timestamp, pd.DataFrame] = {}
    source_errors = []
    rows_to_save = []
    for dt, (path, err) in sorted(downloads.items()):
        if err:
            source_errors.append((dt.date().isoformat(), err))
            continue
        df = read_nifty_options(path, dt.date())
        # Retain the NIFTY rows needed for the expiry dates in the audit set.
        keep_exps = set()
        for _, r in recon_set[recon_set["entry_date"] == dt.date().isoformat()].iterrows():
            keep_exps.update([r["near_expiry"], r["far_expiry"]])
        for _, r in recon_set[recon_set["near_expiry"] == dt.date().isoformat()].iterrows():
            keep_exps.update([r["near_expiry"], r["far_expiry"]])
        df = df[df["expiry"].dt.strftime("%Y-%m-%d").isin(keep_exps)].copy()
        daily[dt] = df
        if not df.empty:
            rows_to_save.append(df.assign(source="NSE_bhavcopy"))

    yahoo = {}
    entry_dates = sorted({str(x) for x in recon_set["entry_date"]})
    def _yahoo_task(d: str) -> tuple[str, float | None, str | None]:
        try:
            return d, yahoo_open(d, requests.Session()), None
        except Exception as exc:
            return d, None, repr(exc)

    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = [pool.submit(_yahoo_task, d) for d in entry_dates]
        for fut in as_completed(futs):
            d, val, err = fut.result()
            yahoo[d] = val
            if err:
                source_errors.append((d, "Yahoo spot: " + err))

    results = []
    for _, cycle in recon_set.iterrows():
        results.append(secondary_cycle(cycle, daily, yahoo.get(cycle["entry_date"])))

    out = pd.DataFrame(results)
    out["comparison_status"] = out.apply(
        lambda r: (
            "PRIMARY_VALID_SECONDARY_COMPLETE"
            if r["primary_reason"] == "VALID" and r["secondary_status"] == "SECONDARY_COMPLETE"
            else "RECOVERED_BY_SECONDARY_EXACT"
            if r["primary_reason"] != "VALID" and r["secondary_status"] == "SECONDARY_COMPLETE" and r["strike_mode"] == "SAME_AS_PRIMARY_STRIKE"
            else "RECOVERED_BY_SECONDARY_RESELECTED"
            if r["primary_reason"] != "VALID" and r["secondary_status"] == "SECONDARY_COMPLETE"
            else "PRIMARY_REJECTED_SECONDARY_NONEXECUTABLE"
            if r["primary_reason"] != "VALID"
            else "PRIMARY_VALID_SECONDARY_NONEXECUTABLE"
        ),
        axis=1,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)

    if rows_to_save:
        rows = pd.concat(rows_to_save, ignore_index=True)
        rows["date"] = rows["date"].dt.strftime("%Y-%m-%d")
        rows["expiry"] = rows["expiry"].dt.strftime("%Y-%m-%d")
    else:
        rows = pd.DataFrame(columns=[
            "date","symbol","expiry","strike","option_type",
            "open","close","contracts","oi","underlying","source"
        ])
    args.rows_out.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(args.rows_out, index=False)

    print("Secondary status counts:")
    print(out["secondary_status"].value_counts(dropna=False).to_string())
    print(f"Downloaded/parsed dates: {len(daily)}")
    if source_errors:
        print("Secondary source errors:")
        for d, e in source_errors:
            print(d, e)
    print(f"Wrote reconciliation: {args.out}")
    print(f"Wrote compact NSE rows: {args.rows_out}")


if __name__ == "__main__":
    main()
