from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def max_drawdown(series: pd.Series) -> float:
    curve = series.cumsum()
    return float((curve - curve.cummax()).min())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    df = pd.read_csv(args.trades)
    n = len(df)
    if n == 0:
        raise SystemExit("Trade ledger is empty")

    lot_sum_per_trade = 2.0 * (
        df["lot_near_pe"]
        + df["lot_near_ce"]
        + df["lot_far_ce"]
        + df["lot_far_pe"]
    )

    buy_turnover = (
        df["entry_near_pe"] * df["lot_near_pe"]
        + df["entry_far_ce"] * df["lot_far_ce"]
        + df["exit_near_ce"] * df["lot_near_ce"]
        + df["exit_far_pe"] * df["lot_far_pe"]
    )
    sell_turnover = (
        df["entry_near_ce"] * df["lot_near_ce"]
        + df["entry_far_pe"] * df["lot_far_pe"]
        + df["exit_near_pe"] * df["lot_near_pe"]
        + df["exit_far_ce"] * df["lot_far_ce"]
    )
    premium_turnover = buy_turnover + sell_turnover

    # Historical sample ends before the 1-Oct-2024 STT change.
    # Paytm Money's Aug-2023 public policy created three client cohorts:
    # ₹10/order for accounts established before 5-Aug-2022,
    # ₹15/order for accounts established 5-Aug-2022 to 24-Aug-2023,
    # ₹20/order for new accounts from 25-Aug-2023.
    # The user's actual cohort is unknown, so brokerage is a scenario variable.
    stt = sell_turnover * 0.000625
    stamp = buy_turnover * 0.00003
    sebi = premium_turnover * 0.000001

    out = pd.DataFrame({
        "entry_date": df["entry_date"],
        "gross_pnl_inr": df["pnl_inr"],
    })

    for bpo in (10.0, 15.0, 20.0):
        brokerage = pd.Series(8.0 * bpo, index=df.index)
        known_cost = brokerage + stt + stamp + sebi + 0.18 * (brokerage + sebi)
        out[f"known_cost_broker_{bpo:.0f}_per_order_inr"] = known_cost

    for slip in (0.25, 0.50, 1.00, 2.00):
        out[f"pnl_after_slippage_{slip:.2f}"] = (
            df["pnl_inr"] - slip * lot_sum_per_trade
        )

    for bpo in (10.0, 15.0, 20.0):
        brokerage = pd.Series(8.0 * bpo, index=df.index)
        for exch in (0.0003503, 0.0005, 0.00053):
            exch_cost = premium_turnover * exch
            gst = 0.18 * (brokerage + sebi + exch_cost)
            net = df["pnl_inr"] - (
                brokerage + stt + stamp + sebi + exch_cost + gst
            )
            out[f"net_broker_{bpo:.0f}_per_order_exchange_{exch:.5f}"] = net
            for slip in (0.25, 0.50, 1.00, 2.00):
                out[
                    f"net_broker_{bpo:.0f}_per_order_{slip:.2f}_slippage_exchange_{exch:.5f}"
                ] = net - slip * lot_sum_per_trade

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)

    print("Trades:", n)
    print("Gross:", df["pnl_inr"].sum())
    for bpo in (10.0, 15.0, 20.0):
        brokerage = pd.Series(8.0 * bpo, index=df.index)
        known_cost = brokerage + stt + stamp + sebi + 0.18 * (brokerage + sebi)
        print("Brokerage cohort", bpo, "known costs:", round(known_cost.sum(), 2))
        for exch in (0.0003503, 0.0005, 0.00053):
            col = f"net_broker_{bpo:.0f}_per_order_exchange_{exch:.5f}"
            print("  exchange sensitivity", exch, "net", round(out[col].sum(), 2))


if __name__ == "__main__":
    main()
