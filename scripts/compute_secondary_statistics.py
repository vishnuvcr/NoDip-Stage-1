from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def circular_block_bootstrap(x: np.ndarray, reps: int = 20000, block: int = 3, seed: int = 20260923) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(x)
    out = np.empty(reps)
    for i in range(reps):
        starts = rng.integers(0, n, size=(n + block - 1) // block)
        sample: list[float] = []
        for start in starts:
            sample.extend(x[(start + np.arange(block)) % n])
        out[i] = np.sum(sample[:n])
    return tuple(np.quantile(out, [0.025, 0.975]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, type=Path)
    ap.add_argument("--costs", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-annual", required=True, type=Path)
    args = ap.parse_args()

    df = pd.read_csv(args.ledger, parse_dates=["entry_date", "near_expiry", "far_expiry"])
    if df.empty:
        raise SystemExit("Secondary ledger is empty")
    df = df.sort_values("entry_date").reset_index(drop=True)

    x = df["pnl_inr"].to_numpy(float)
    wins = x[x > 0]
    losses = x[x < 0]
    cum = np.cumsum(x)
    dd = cum - np.maximum.accumulate(cum)
    pf = wins.sum() / abs(losses.sum()) if len(losses) else float("inf")
    ci_lo, ci_hi = circular_block_bootstrap(x)

    annual = (
        df.assign(year=df["entry_date"].dt.year)
        .groupby("year", as_index=False)
        .agg(
            trades=("pnl_inr", "size"),
            gross_pnl=("pnl_inr", "sum"),
            mean_trade=("pnl_inr", "mean"),
        )
    )

    costs = pd.read_csv(args.costs)

    report = [
        "# Final Secondary-Source Statistics — NIFTY 4-Leg Calendar — 2022-2024",
        "",
        "## Population and gross performance",
        f"- Complete independently reconciled cycles: {len(df)} of 134 candidates",
        "- Secondary-source coverage: 98.5% (132/134)",
        f"- Gross P&L: ₹{x.sum():,.2f}",
        f"- Mean trade: ₹{x.mean():,.2f}",
        f"- Median trade: ₹{np.median(x):,.2f}",
        f"- Win rate: {(x > 0).mean():.2%} ({int((x > 0).sum())}/{len(x)})",
        f"- Profit factor: {pf:.3f}",
        f"- Maximum drawdown: ₹{dd.min():,.2f}",
        f"- Best trade: ₹{x.max():,.2f}",
        f"- Worst trade: ₹{x.min():,.2f}",
        f"- Circular 3-trade block bootstrap 95% interval for total gross P&L: ₹{ci_lo:,.2f} to ₹{ci_hi:,.2f}",
        "",
        "## Annual decomposition",
        "",
        "| Year | Trades | Gross P&L (₹) | Mean trade (₹) |",
        "|---:|---:|---:|---:|",
    ]
    for _, r in annual.iterrows():
        report.append(
            f"| {int(r.year)} | {int(r.trades)} | {r.gross_pnl:,.2f} | {r.mean_trade:,.2f} |"
        )

    report += [
        "",
        "## Cost sensitivity",
        "",
        "| Brokerage / order | Exchange rate | Net, 0 pt slippage | Net, 0.50 pt | Net, 1.00 pt | Net, 2.00 pt |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in costs.iterrows():
        report.append(
            f"| ₹{r.brokerage_per_order:.0f} | {r.exchange_rate:.5f} | "
            f"₹{r.net_no_slippage_inr:,.2f} | ₹{r['net_0.50pt_slippage_inr']:,.2f} | "
            f"₹{r['net_1.00pt_slippage_inr']:,.2f} | ₹{r['net_2.00pt_slippage_inr']:,.2f} |"
        )

    report += [
        "",
        "## Source interpretation",
        "- All 75 cycles rejected by the primary public dataset were complete on the independent public mirror of NSE F&O bhavcopy archives.",
        "- 57 of 59 primary-valid cycles were also complete on the independent source.",
        "- 2 primary-valid cycles were not constructible on the secondary source because that source contained no common strike for the frozen same-strike structure.",
        "- These source discrepancies are not treated as evidence of actual market non-trading; they are retained as data-source limitations.",
        "",
        "## Statistical caution",
        "The bootstrap interval is a dependence-aware resampling diagnostic, not a proof of stationarity or future performance. The historical daily OHLC convention also does not model bid/ask execution, queue position, market impact or order-leg synchronization.",
    ]

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(report), encoding="utf-8")
    args.out_annual.parent.mkdir(parents=True, exist_ok=True)
    annual.to_csv(args.out_annual, index=False)
    print(args.out_report.read_text())
