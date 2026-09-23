from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def lot_size(expiry: pd.Timestamp) -> int:
    if expiry < pd.Timestamp("2024-05-02"):
        return 50
    if expiry < pd.Timestamp("2025-01-02"):
        return 25
    if expiry < pd.Timestamp("2026-01-06"):
        return 75
    return 65


def get_price(day: pd.DataFrame, expiry: pd.Timestamp, strike: float, option_type: str, field: str) -> float:
    m = day[
        (day["expiry"] == expiry)
        & (day["strike"] == strike)
        & (day["option_type"] == option_type)
    ]
    if len(m) != 1:
        raise ValueError(
            f"Expected exactly one {field} row, got {len(m)} for "
            f"{expiry.date()} {strike} {option_type}"
        )
    value = pd.to_numeric(m.iloc[0][field], errors="coerce")
    if pd.isna(value):
        raise ValueError(
            f"Missing {field} for {expiry.date()} {strike} {option_type}"
        )
    return float(value)


def build(ledger: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    raw = raw.copy()
    raw["date"] = pd.to_datetime(raw["date"])
    raw["expiry"] = pd.to_datetime(raw["expiry"])
    raw["strike"] = pd.to_numeric(raw["strike"], errors="coerce")
    raw["open"] = pd.to_numeric(raw["open"], errors="coerce")
    raw["close"] = pd.to_numeric(raw["close"], errors="coerce")

    rows = []
    for _, r in ledger.iterrows():
        entry_date = pd.Timestamp(r["entry_date"])
        near = pd.Timestamp(r["near_expiry"])
        far = pd.Timestamp(r["far_expiry"])
        strike = float(r["secondary_strike"])
        entry = raw[raw["date"] == entry_date]
        exit_ = raw[raw["date"] == near]

        vals = {
            "entry_date": entry_date,
            "near_expiry": near,
            "far_expiry": far,
            "strike": strike,
            "lot_near": lot_size(near),
            "lot_far": lot_size(far),
        }
        legs = [
            ("near_pe", near, "PE"),
            ("near_ce", near, "CE"),
            ("far_ce", far, "CE"),
            ("far_pe", far, "PE"),
        ]
        for name, expiry, opt in legs:
            vals[f"entry_{name}"] = get_price(entry, expiry, strike, opt, "open")
            vals[f"exit_{name}"] = get_price(exit_, expiry, strike, opt, "close")

        ln = vals["lot_near"]
        lf = vals["lot_far"]
        vals["pnl_inr"] = (
            (vals["exit_near_pe"] - vals["entry_near_pe"]) * ln
            + (vals["entry_near_ce"] - vals["exit_near_ce"]) * ln
            + (vals["exit_far_ce"] - vals["entry_far_ce"]) * lf
            + (vals["entry_far_pe"] - vals["exit_far_pe"]) * lf
        )
        rows.append(vals)

    return pd.DataFrame(rows).sort_values("entry_date").reset_index(drop=True)


def cost_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    buy_turnover = (
        df["entry_near_pe"] * df["lot_near"]
        + df["entry_far_ce"] * df["lot_far"]
        + df["exit_near_ce"] * df["lot_near"]
        + df["exit_far_pe"] * df["lot_far"]
    )
    sell_turnover = (
        df["entry_near_ce"] * df["lot_near"]
        + df["entry_far_pe"] * df["lot_far"]
        + df["exit_near_pe"] * df["lot_near"]
        + df["exit_far_ce"] * df["lot_far"]
    )
    premium_turnover = buy_turnover + sell_turnover
    execution_lot = 2 * (
        df["lot_near"] + df["lot_near"] + df["lot_far"] + df["lot_far"]
    )

    rows = []
    for broker in (10.0, 15.0, 20.0):
        brokerage = pd.Series(8.0 * broker, index=df.index)
        stt = sell_turnover * 0.000625
        stamp = buy_turnover * 0.00003
        sebi = premium_turnover * 0.000001
        for exchange in (0.0003503, 0.0005, 0.00053):
            exchange_cost = premium_turnover * exchange
            gst = 0.18 * (brokerage + sebi + exchange_cost)
            net = df["pnl_inr"] - (
                brokerage + stt + stamp + sebi + exchange_cost + gst
            )
            row = {
                "brokerage_per_order": broker,
                "exchange_rate": exchange,
                "gross_pnl_inr": df["pnl_inr"].sum(),
                "net_no_slippage_inr": net.sum(),
            }
            for slip in (0.25, 0.50, 1.00, 2.00):
                row[f"net_{slip:.2f}pt_slippage_inr"] = (
                    net - slip * execution_lot
                ).sum()
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, type=Path)
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--out-ledger", required=True, type=Path)
    ap.add_argument("--out-costs", required=True, type=Path)
    args = ap.parse_args()

    ledger = pd.read_csv(args.ledger, parse_dates=["entry_date", "near_expiry", "far_expiry"])
    raw = pd.read_csv(args.raw)
    df = build(ledger, raw)
    args.out_ledger.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_ledger, index=False)

    costs = cost_sensitivity(df)
    args.out_costs.parent.mkdir(parents=True, exist_ok=True)
    costs.to_csv(args.out_costs, index=False)

    print(f"Built {len(df)} complete secondary trade records")
    print(f"Gross P&L: {df['pnl_inr'].sum():,.2f}")
    print(costs.to_string(index=False))


if __name__ == "__main__":
    main()
