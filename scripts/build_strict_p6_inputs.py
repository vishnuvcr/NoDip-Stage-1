from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


EXACT_STATUSES = {
    "PRIMARY_VALID_SECONDARY_COMPLETE",
    "RECOVERED_BY_SECONDARY_EXACT",
}


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
    premium = buy_turnover + sell_turnover
    execution_lot = 2 * (df["lot_near"] * 2 + df["lot_far"] * 2)

    rows = []
    for broker in (10.0, 15.0, 20.0):
        brokerage = pd.Series(8.0 * broker, index=df.index)
        stt = sell_turnover * 0.000625
        stamp = buy_turnover * 0.00003
        sebi = premium * 0.000001
        for exchange in (0.0003503, 0.0005, 0.00053):
            exchange_cost = premium * exchange
            gst = 0.18 * (brokerage + sebi + exchange_cost)
            net = df["pnl_inr"] - (
                brokerage + stt + stamp + sebi + exchange_cost + gst
            )
            rows.append({
                "brokerage_per_order": broker,
                "exchange_rate": exchange,
                "gross_pnl_inr": df["pnl_inr"].sum(),
                "net_no_slippage_inr": net.sum(),
                "net_0.25pt_slippage_inr": (net - 0.25 * execution_lot).sum(),
                "net_0.50pt_slippage_inr": (net - 0.50 * execution_lot).sum(),
                "net_1.00pt_slippage_inr": (net - 1.00 * execution_lot).sum(),
                "net_2.00pt_slippage_inr": (net - 2.00 * execution_lot).sum(),
            })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recon", required=True, type=Path)
    ap.add_argument("--secondary-ledger", required=True, type=Path)
    ap.add_argument("--out-ledger", required=True, type=Path)
    ap.add_argument("--out-costs", required=True, type=Path)
    args = ap.parse_args()

    recon = pd.read_csv(args.recon)
    ledger = pd.read_csv(args.secondary_ledger)

    exact = recon[recon["comparison_status"].isin(EXACT_STATUSES)][
        ["entry_date", "near_expiry", "far_expiry", "comparison_status"]
    ].copy()
    strict = ledger.merge(
        exact,
        on=["entry_date", "near_expiry", "far_expiry"],
        how="inner",
    ).sort_values("entry_date").reset_index(drop=True)

    if len(strict) != 84:
        raise SystemExit(
            f"Expected 84 strict frozen-protocol cycles, got {len(strict)}"
        )

    args.out_ledger.parent.mkdir(parents=True, exist_ok=True)
    strict.to_csv(args.out_ledger, index=False)

    costs = cost_sensitivity(strict)
    costs.to_csv(args.out_costs, index=False)

    print(f"Strict frozen-protocol cycles: {len(strict)}")
    print(f"Gross P&L: {strict['pnl_inr'].sum():,.2f}")
    print(costs.to_string(index=False))


if __name__ == "__main__":
    main()
