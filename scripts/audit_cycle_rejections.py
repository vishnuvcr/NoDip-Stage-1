from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.nifty_calendar.backtest import (
    historical_nifty_lot_size,
    load_table,
    normalize,
)


def _candidate_expiries(fo: pd.DataFrame) -> list[pd.Timestamp]:
    expiries = sorted(fo.loc[fo["symbol"] == "NIFTY", "expiry"].dropna().unique())
    return [
        pd.Timestamp(e)
        for e in expiries
        if pd.Timestamp(e) >= pd.Timestamp("2021-08-05")
    ]


def _leg_count(
    fo: pd.DataFrame,
    date: pd.Timestamp,
    expiry: pd.Timestamp,
    strike: float | None,
    opt: str,
) -> tuple[int, int]:
    if strike is None:
        return 0, 0
    m = fo[
        (fo["date"] == date)
        & (fo["symbol"] == "NIFTY")
        & (fo["expiry"] == expiry)
        & (fo["strike"] == strike)
        & (fo["option_type"] == opt)
    ]
    return len(m), int(m["open"].notna().sum())


def _common_strikes(
    fo: pd.DataFrame,
    date: pd.Timestamp,
    near: pd.Timestamp,
    far: pd.Timestamp,
) -> tuple[list[float], list[float], list[float]]:
    subset = fo[
        (fo["date"] == date)
        & (fo["symbol"] == "NIFTY")
        & (fo["expiry"].isin([near, far]))
        & (fo["option_type"].isin(["CE", "PE"]))
    ]
    near_all = subset[subset["expiry"] == near]
    far_all = subset[subset["expiry"] == far]
    near_exec = sorted(near_all.loc[near_all["open"].gt(0), "strike"].dropna().unique())
    far_exec = sorted(far_all.loc[far_all["open"].gt(0), "strike"].dropna().unique())
    common = sorted(set(near_exec).intersection(far_exec))
    return near_exec, far_exec, common


def audit(fo: pd.DataFrame, spot: pd.DataFrame) -> pd.DataFrame:
    expiries = _candidate_expiries(fo)
    spot_days = set(spot["date"].dropna())
    rows: list[dict] = []

    for i in range(1, len(expiries) - 3):
        previous_expiry = pd.Timestamp(expiries[i - 1])
        near_expiry = pd.Timestamp(expiries[i])
        far_expiry = pd.Timestamp(expiries[i + 3])

        candidates = sorted(
            d for d in spot_days if d > previous_expiry and d < near_expiry
        )
        base = {
            "candidate_index": i,
            "previous_expiry": previous_expiry.date().isoformat(),
            "near_expiry": near_expiry.date().isoformat(),
            "far_expiry": far_expiry.date().isoformat(),
            "entry_date": candidates[0].date().isoformat() if candidates else "",
            "spot_open": "",
            "primary_strike": "",
            "primary_reason": "",
            "near_common_strike_count": 0,
            "far_common_strike_count": 0,
            "common_strike_count": 0,
            "missing_entry_legs": "",
            "missing_exit_legs": "",
            "entry_open_missing": "",
            "exit_close_missing": "",
            "primary_near_pe_open": "",
            "primary_near_pe_close": "",
            "primary_near_ce_open": "",
            "primary_near_ce_close": "",
            "primary_far_ce_open": "",
            "primary_far_ce_close": "",
            "primary_far_pe_open": "",
            "primary_far_pe_close": "",
        }

        if not candidates:
            base["primary_reason"] = "NO_ENTRY_SESSION"
            rows.append(base)
            continue

        entry_date = candidates[0]
        spot_rows = spot[spot["date"] == entry_date]
        if len(spot_rows) != 1 or pd.isna(spot_rows.iloc[0]["open"]):
            base["primary_reason"] = "MISSING_SPOT_OPEN"
            rows.append(base)
            continue

        spot_open = float(spot_rows.iloc[0]["open"])
        base["spot_open"] = spot_open
        day_fo = fo[fo["date"] == entry_date]
        near_exec, far_exec, common = _common_strikes(
            fo, entry_date, near_expiry, far_expiry
        )
        base["near_common_strike_count"] = len(near_exec)
        base["far_common_strike_count"] = len(far_exec)
        base["common_strike_count"] = len(common)

        if not common:
            base["primary_reason"] = "NO_COMMON_STRIKE"
            rows.append(base)
            continue

        strike = min(common, key=lambda k: (abs(k - spot_open), k))
        base["primary_strike"] = strike

        expected = [
            ("near_pe", near_expiry, "PE"),
            ("near_ce", near_expiry, "CE"),
            ("far_ce", far_expiry, "CE"),
            ("far_pe", far_expiry, "PE"),
        ]
        missing_entry = []
        entry_open_missing = []
        for name, expiry, opt in expected:
            n_rows, n_open = _leg_count(fo, entry_date, expiry, strike, opt)
            if n_rows != 1:
                missing_entry.append(name)
            if n_open != 1:
                entry_open_missing.append(name)

        if missing_entry or entry_open_missing:
            base["primary_reason"] = "MISSING_ENTRY_LEG"
            base["missing_entry_legs"] = ";".join(missing_entry)
            base["entry_open_missing"] = ";".join(entry_open_missing)

        expected_exit = [
            ("near_pe", near_expiry, "PE"),
            ("near_ce", near_expiry, "CE"),
            ("far_ce", far_expiry, "CE"),
            ("far_pe", far_expiry, "PE"),
        ]
        missing_exit = []
        exit_close_missing = []
        for name, expiry, opt in expected_exit:
            n_rows, n_open = _leg_count(fo, near_expiry, expiry, strike, opt)
            if n_rows != 1:
                missing_exit.append(name)
            if n_open != 1:
                # _leg_count checks open; fetch close explicitly below.
                pass
            m = fo[
                (fo["date"] == near_expiry)
                & (fo["symbol"] == "NIFTY")
                & (fo["expiry"] == expiry)
                & (fo["strike"] == strike)
                & (fo["option_type"] == opt)
            ]
            if len(m) != 1 or m["close"].notna().sum() != 1:
                exit_close_missing.append(name)

        for name, expiry, opt in expected:
            m = fo[
                (fo["date"] == entry_date)
                & (fo["symbol"] == "NIFTY")
                & (fo["expiry"] == expiry)
                & (fo["strike"] == strike)
                & (fo["option_type"] == opt)
            ]
            if len(m) == 1:
                base[f"primary_{name}_open"] = float(m.iloc[0]["open"]) if pd.notna(m.iloc[0]["open"]) else ""
                base[f"primary_{name}_close"] = float(m.iloc[0]["close"]) if pd.notna(m.iloc[0]["close"]) else ""
            m2 = fo[
                (fo["date"] == near_expiry)
                & (fo["symbol"] == "NIFTY")
                & (fo["expiry"] == expiry)
                & (fo["strike"] == strike)
                & (fo["option_type"] == opt)
            ]
            if len(m2) == 1:
                base[f"primary_{name}_close"] = float(m2.iloc[0]["close"]) if pd.notna(m2.iloc[0]["close"]) else base[f"primary_{name}_close"]

        if missing_exit or exit_close_missing:
            base["primary_reason"] = (
                "MISSING_EXIT_LEG" if base["primary_reason"] == "" else base["primary_reason"] + "+MISSING_EXIT_LEG"
            )
            base["missing_exit_legs"] = ";".join(missing_exit)
            base["exit_close_missing"] = ";".join(exit_close_missing)

        if base["primary_reason"] == "":
            base["primary_reason"] = "VALID"

        rows.append(base)

    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fo", required=True, type=Path)
    ap.add_argument("--spot", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    fo = normalize(load_table(args.fo))
    spot = load_table(args.spot)
    spot["date"] = pd.to_datetime(spot["date"]).dt.normalize()
    spot["open"] = pd.to_numeric(spot["open"], errors="coerce")

    out = audit(fo, spot)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)

    print(out["primary_reason"].value_counts(dropna=False).to_string())
    print(f"Wrote {len(out)} candidate-cycle audit rows to {args.out}")


if __name__ == "__main__":
    main()
