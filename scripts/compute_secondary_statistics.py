from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def circular_block_bootstrap(x: np.ndarray, reps: int = 20000, block: int = 3, seed: int = 20260923) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(reps, nb))
    offsets = np.arange(block)
    idx = (starts[:, :, None] + offsets[None, None, :]) % n
    vals = x[idx].reshape(reps, nb * block)[:, :n]
    out = vals.sum(axis=1)
    return tuple(np.quantile(out, [0.025, 0.975]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, type=Path)
    ap.add_argument("--costs", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-annual", required=True, type=Path)
    args = ap.parse_args()

    df = pd.read_csv(args.ledger, parse_dates=["entry_date", "near_expiry", "far_expiry"]).sort_values("entry_date").reset_index(drop=True)
    if len(df) != 132:
        raise SystemExit(f"Expected 132 complete secondary cycles, got {len(df)}")
    x = df["pnl_inr"].to_numpy(float)
    cum = np.cumsum(x)
    dd = cum - np.maximum.accumulate(cum)
    wins = x[x > 0]
    losses = x[x < 0]
    pf = wins.sum() / abs(losses.sum())
    ci_lo, ci_hi = circular_block_bootstrap(x)

    annual = df.assign(year=df["entry_date"].dt.year).groupby("year", as_index=False).agg(
        trades=("pnl_inr", "size"),
        gross_pnl=("pnl_inr", "sum"),
        mean_trade=("pnl_inr", "mean"),
    )
    costs = pd.read_csv(args.costs)
    rows = costs[costs["exchange_rate"].eq(0.0005)].copy().sort_values("brokerage_per_order")

    report = [
        "# Final Secondary-Source Statistics — NIFTY 4-Leg Calendar — 2022-2024",
        "",
        "## Population",
        "- Candidate cycles: 134",
        "- Complete independent-secondary cycles: 132",
        "- Coverage: 98.5%",
        "- Primary rejects recovered: 75/75",
        "- Primary-valid cycles also complete: 57/59",
        "- Primary-valid cycles not constructible on secondary: 2",
        "",
        "## Gross performance",
        f"- Gross P&L: ₹{x.sum():,.2f}",
        f"- Mean trade: ₹{x.mean():,.2f}",
        f"- Median trade: ₹{np.median(x):,.2f}",
        f"- Win rate: {(x > 0).mean():.2%} ({int((x > 0).sum())}/132)",
        f"- Profit factor: {pf:.3f}",
        f"- Maximum drawdown: ₹{dd.min():,.2f}",
        f"- Best trade: ₹{x.max():,.2f}",
        f"- Worst trade: ₹{x.min():,.2f}",
        f"- Circular 3-trade block bootstrap 95% interval: ₹{ci_lo:,.2f} to ₹{ci_hi:,.2f}",
        "",
        "## Annual decomposition",
        "",
        "| Year | Trades | Gross P&L (₹) | Mean trade (₹) |",
        "|---:|---:|---:|---:|",
    ]
    for _, r in annual.iterrows():
        report.append(f"| {int(r.year)} | {int(r.trades)} | {r.gross_pnl:,.2f} | {r.mean_trade:,.2f} |")

    report += [
        "",
        "## Cost sensitivity at 0.05000% exchange-charge rate",
        "",
        "| Brokerage / order | 0 pt | 0.50 pt | 1.00 pt | 2.00 pt |",
        "|---:|---:|---:|---:|---:|",
    ]
    for _, r in rows.iterrows():
        report.append(
            f"| ₹{r.brokerage_per_order:.0f} | {r.net_no_slippage_inr:,.2f} | "
            f"{r['net_0.50pt_slippage_inr']:,.2f} | {r['net_1.00pt_slippage_inr']:,.2f} | "
            f"{r['net_2.00pt_slippage_inr']:,.2f} |"
        )

    report += [
        "",
        "## Interpretation",
        "The 132-cycle secondary result is a descriptive historical reconstruction using an independent public contract mirror and independent spot-open diagnostic. It does not establish a future expected return or live four-leg execution quality.",
    ]
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(report), encoding="utf-8")
    args.out_annual.parent.mkdir(parents=True, exist_ok=True)
    annual.to_csv(args.out_annual, index=False)
    print(args.out_report.read_text())


if __name__ == "__main__":
    main()
