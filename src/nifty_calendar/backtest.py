from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_FO = {
    "date",
    "symbol",
    "expiry",
    "strike",
    "option_type",
    "open",
    "close",
}
REQUIRED_SPOT = {"date", "open"}


def historical_nifty_lot_size(expiry: pd.Timestamp) -> int:
    e = pd.Timestamp(expiry)
    if e < pd.Timestamp("2021-08-05"):
        return 75
    if e < pd.Timestamp("2024-05-02"):
        return 50
    if e < pd.Timestamp("2025-01-02"):
        return 25
    if e < pd.Timestamp("2026-01-06"):
        return 75
    return 65


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"]).dt.normalize()
    out["expiry"] = pd.to_datetime(out["expiry"]).dt.normalize()
    out["strike"] = pd.to_numeric(out["strike"], errors="coerce")
    out["open"] = pd.to_numeric(out["open"], errors="coerce")
    out["close"] = pd.to_numeric(out["close"], errors="coerce")

    if "lot_size" not in out.columns:
        out["lot_size"] = pd.Series(pd.NA, index=out.index, dtype="Int64")
    else:
        out["lot_size"] = pd.to_numeric(out["lot_size"], errors="coerce").astype("Int64")

    # Avoid assigning an empty DatetimeArray into an integer column when no
    # rows are missing. This is a pandas 3.x compatibility issue.
    missing_lot = out["lot_size"].isna() & out["expiry"].notna()
    if missing_lot.any():
        fallback = out.loc[missing_lot, "expiry"].map(
            historical_nifty_lot_size
        ).astype("Int64")
        out.loc[missing_lot, "lot_size"] = fallback

    out["option_type"] = out["option_type"].astype(str).str.upper()
    out["symbol"] = out["symbol"].astype(str).str.upper()
    return out


def nearest_common_strike(
    day: pd.DataFrame,
    expiry_near: pd.Timestamp,
    expiry_far: pd.Timestamp,
    spot_open: float,
) -> float:
    subset = day[
        (day["symbol"] == "NIFTY")
        & (day["expiry"].isin([expiry_near, expiry_far]))
        & (day["option_type"].isin(["CE", "PE"]))
    ]
    near = subset[subset["expiry"] == expiry_near]
    far = subset[subset["expiry"] == expiry_far]
    n = set(near.loc[near["open"].notna(), "strike"].unique())
    f = set(far.loc[far["open"].notna(), "strike"].unique())
    common = sorted(n.intersection(f))
    if not common:
        raise ValueError("No common executable strike for both expiries")
    return min(common, key=lambda k: (abs(k - spot_open), k))


def leg_row(
    fo: pd.DataFrame,
    date: pd.Timestamp,
    expiry: pd.Timestamp,
    strike: float,
    opt: str,
) -> pd.Series:
    m = fo[
        (fo["date"] == date)
        & (fo["symbol"] == "NIFTY")
        & (fo["expiry"] == expiry)
        & (fo["strike"] == strike)
        & (fo["option_type"] == opt)
    ]
    if len(m) != 1:
        raise ValueError(
            f"Expected one contract row, got {len(m)} for "
            f"{date.date()} {expiry.date()} {strike} {opt}"
        )
    return m.iloc[0]


def build_trades(fo: pd.DataFrame, spot: pd.DataFrame) -> pd.DataFrame:
    expiries = sorted(fo.loc[fo["symbol"] == "NIFTY", "expiry"].dropna().unique())
    expiries = [
        pd.Timestamp(e)
        for e in expiries
        if pd.Timestamp(e) >= pd.Timestamp("2021-08-05")
    ]
    spot_days = set(spot["date"].dropna())

    audit = {
        "expiry_count": len(expiries),
        "no_entry_session": 0,
        "missing_spot_open": 0,
        "no_common_strike": 0,
        "missing_entry_leg": 0,
        "missing_exit_leg": 0,
        "valid_trades": 0,
    }

    trades = []
    for i in range(1, len(expiries) - 3):
        previous_expiry = pd.Timestamp(expiries[i - 1])
        near_expiry = pd.Timestamp(expiries[i])
        far_expiry = pd.Timestamp(expiries[i + 3])

        candidates = sorted(
            d for d in spot_days if d > previous_expiry and d < near_expiry
        )
        if not candidates:
            audit["no_entry_session"] += 1
            continue
        entry_date = candidates[0]

        spot_rows = spot[spot["date"] == entry_date]
        if len(spot_rows) != 1 or pd.isna(spot_rows.iloc[0]["open"]):
            audit["missing_spot_open"] += 1
            continue
        spot_open = float(spot_rows.iloc[0]["open"])

        day_fo = fo[fo["date"] == entry_date]
        try:
            strike = nearest_common_strike(
                day_fo, near_expiry, far_expiry, spot_open
            )
        except ValueError:
            audit["no_common_strike"] += 1
            continue

        try:
            legs = {
                "near_pe": leg_row(fo, entry_date, near_expiry, strike, "PE"),
                "near_ce": leg_row(fo, entry_date, near_expiry, strike, "CE"),
                "far_ce": leg_row(fo, entry_date, far_expiry, strike, "CE"),
                "far_pe": leg_row(fo, entry_date, far_expiry, strike, "PE"),
            }
        except ValueError:
            audit["missing_entry_leg"] += 1
            continue

        try:
            exits = {
                "near_pe": leg_row(fo, near_expiry, near_expiry, strike, "PE"),
                "near_ce": leg_row(fo, near_expiry, near_expiry, strike, "CE"),
                "far_ce": leg_row(fo, near_expiry, far_expiry, strike, "CE"),
                "far_pe": leg_row(fo, near_expiry, far_expiry, strike, "PE"),
            }
        except ValueError:
            audit["missing_exit_leg"] += 1
            continue

        if any(pd.isna(x["open"]) for x in legs.values()):
            audit["missing_entry_leg"] += 1
            continue
        if any(pd.isna(x["close"]) for x in exits.values()):
            audit["missing_exit_leg"] += 1
            continue

        for x in list(legs.values()) + list(exits.values()):
            if pd.isna(x["lot_size"]):
                x["lot_size"] = historical_nifty_lot_size(pd.Timestamp(x["expiry"]))

        pnl_points = (
            (float(exits["near_pe"]["close"]) - float(legs["near_pe"]["open"]))
            + (float(legs["near_ce"]["open"]) - float(exits["near_ce"]["close"]))
            + (float(exits["far_ce"]["close"]) - float(legs["far_ce"]["open"]))
            + (float(legs["far_pe"]["open"]) - float(exits["far_pe"]["close"]))
        )

        pnl_inr = (
            (float(exits["near_pe"]["close"]) - float(legs["near_pe"]["open"]))
            * float(legs["near_pe"]["lot_size"])
            + (float(legs["near_ce"]["open"]) - float(exits["near_ce"]["close"]))
            * float(legs["near_ce"]["lot_size"])
            + (float(exits["far_ce"]["close"]) - float(legs["far_ce"]["open"]))
            * float(legs["far_ce"]["lot_size"])
            + (float(legs["far_pe"]["open"]) - float(exits["far_pe"]["close"]))
            * float(legs["far_pe"]["lot_size"])
        )

        trades.append(
            {
                "entry_date": entry_date,
                "near_expiry": near_expiry,
                "far_expiry": far_expiry,
                "spot_open": spot_open,
                "strike": strike,
                "entry_near_pe": float(legs["near_pe"]["open"]),
                "entry_near_ce": float(legs["near_ce"]["open"]),
                "entry_far_ce": float(legs["far_ce"]["open"]),
                "entry_far_pe": float(legs["far_pe"]["open"]),
                "exit_near_pe": float(exits["near_pe"]["close"]),
                "exit_near_ce": float(exits["near_ce"]["close"]),
                "exit_far_ce": float(exits["far_ce"]["close"]),
                "exit_far_pe": float(exits["far_pe"]["close"]),
                "lot_near_pe": int(legs["near_pe"]["lot_size"]),
                "lot_near_ce": int(legs["near_ce"]["lot_size"]),
                "lot_far_ce": int(legs["far_ce"]["lot_size"]),
                "lot_far_pe": int(legs["far_pe"]["lot_size"]),
                "pnl_points": pnl_points,
                "pnl_inr": pnl_inr,
            }
        )
        audit["valid_trades"] += 1

    print("Backtest audit:", audit)
    return pd.DataFrame(trades)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fo", required=True, type=Path)
    parser.add_argument("--spot", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    fo = normalize(load_table(args.fo))
    spot = load_table(args.spot)
    spot["date"] = pd.to_datetime(spot["date"]).dt.normalize()
    spot["open"] = pd.to_numeric(spot["open"], errors="coerce")

    missing_fo = REQUIRED_FO - set(fo.columns)
    missing_spot = REQUIRED_SPOT - set(spot.columns)
    if missing_fo:
        raise ValueError(f"Missing FO columns: {sorted(missing_fo)}")
    if missing_spot:
        raise ValueError(f"Missing spot columns: {sorted(missing_spot)}")

    print(
        "Input summary:",
        {
            "fo_rows": len(fo),
            "fo_dates": fo["date"].min(),
            "fo_dates_max": fo["date"].max(),
            "expiries": fo["expiry"].nunique(),
            "spot_rows": len(spot),
        },
    )

    trades = build_trades(fo, spot)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(args.out, index=False)
    print(f"Wrote {len(trades)} trades to {args.out}")


if __name__ == "__main__":
    main()
