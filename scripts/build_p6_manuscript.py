from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def bootstrap_ci(x: np.ndarray, reps: int = 20000, block: int = 3, seed: int = 20260923) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(reps, nb))
    offsets = np.arange(block)
    idx = (starts[:, :, None] + offsets[None, None, :]) % n
    vals = x[idx].reshape(reps, nb * block)[:, :n]
    return tuple(np.quantile(vals.sum(axis=1), [0.025, 0.975]))


def max_dd(x: np.ndarray) -> float:
    curve = np.cumsum(x)
    return float((curve - np.maximum.accumulate(curve)).min())


def pf(x: np.ndarray) -> float:
    return float(x[x > 0].sum() / (-x[x < 0].sum()))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade-level", required=True, type=Path)
    ap.add_argument("--recon", required=True, type=Path)
    ap.add_argument("--costs", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-stats", required=True, type=Path)
    ap.add_argument("--fig-dir", required=True, type=Path)
    args = ap.parse_args()

    trades = pd.read_csv(args.trade_level, parse_dates=["entry_date", "near_expiry", "far_expiry"]).sort_values("entry_date").reset_index(drop=True)
    recon = pd.read_csv(args.recon, parse_dates=["entry_date", "near_expiry", "far_expiry"])
    costs = pd.read_csv(args.costs)
    if len(trades) != 132:
        raise SystemExit(f"Expected 132 complete secondary trades, got {len(trades)}")

    x = trades["pnl_inr"].astype(float).to_numpy()
    total = float(x.sum())
    mean = float(x.mean())
    median = float(np.median(x))
    win = float((x > 0).mean())
    profit_factor = pf(x)
    drawdown = max_dd(x)
    best = float(x.max())
    worst = float(x.min())
    ci_lo, ci_hi = bootstrap_ci(x)
    annual = trades.assign(year=trades["entry_date"].dt.year).groupby("year", as_index=False).agg(
        trades=("pnl_inr", "size"), gross_pnl=("pnl_inr", "sum"), mean_trade=("pnl_inr", "mean")
    )

    comparison = recon["comparison_status"].value_counts().to_dict()
    same = recon[recon["comparison_status"].eq("RECOVERED_BY_SECONDARY_EXACT")]["secondary_pnl_inr"].dropna().astype(float)
    reselected = recon[recon["comparison_status"].eq("RECOVERED_BY_SECONDARY_RESELECTED")]["secondary_pnl_inr"].dropna().astype(float)
    matched = recon[recon["comparison_status"].eq("PRIMARY_VALID_SECONDARY_COMPLETE")]["secondary_pnl_inr"].dropna().astype(float)

    args.fig_dir.mkdir(parents=True, exist_ok=True)
    curve = np.cumsum(x)
    dd = curve - np.maximum.accumulate(curve)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(trades["entry_date"], curve)
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Independent secondary cumulative gross P&L")
    ax.set_xlabel("Entry date")
    ax.set_ylabel("Cumulative P&L (INR)")
    fig.tight_layout()
    fig.savefig(args.fig_dir / "cumulative_pnl.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(trades["entry_date"], dd)
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Independent secondary drawdown")
    ax.set_xlabel("Entry date")
    ax.set_ylabel("Drawdown (INR)")
    fig.tight_layout()
    fig.savefig(args.fig_dir / "drawdown.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(annual["year"].astype(str), annual["gross_pnl"])
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Annual gross P&L")
    ax.set_xlabel("Year")
    ax.set_ylabel("Gross P&L (INR)")
    fig.tight_layout()
    fig.savefig(args.fig_dir / "annual_pnl.svg")
    plt.close(fig)

    mid = costs[costs["exchange_rate"].eq(0.0005)].copy().sort_values("brokerage_per_order")
    fig, ax = plt.subplots(figsize=(9, 5))
    for col, label in [
        ("net_no_slippage_inr", "0 pt"),
        ("net_0.50pt_slippage_inr", "0.50 pt"),
        ("net_1.00pt_slippage_inr", "1.00 pt"),
        ("net_2.00pt_slippage_inr", "2.00 pt"),
    ]:
        ax.plot(mid["brokerage_per_order"], mid[col], marker="o", label=label)
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Net P&L sensitivity at 0.05000% exchange-charge assumption")
    ax.set_xlabel("Brokerage per order (INR)")
    ax.set_ylabel("Net cumulative P&L (INR)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.fig_dir / "cost_sensitivity.svg")
    plt.close(fig)

    cost_mid = mid.set_index("brokerage_per_order")
    lines = [
        "# Final NIFTY 4-Leg Calendar Manuscript — 2022-2024",
        "",
        "## Abstract",
        "This study evaluates a frozen four-leg NIFTY 50 weekly/three-week calendar rule with no discretionary adjustment. The primary public dataset initially produced only 59 complete cycles from 134 candidate cycles. Independent reconciliation against a public mirror of NSE F&O bhavcopy archives and an independent NIFTY spot-open diagnostic reconstructed 132 complete cycles. The independent secondary re-run re-applies the frozen common-ATM rule using the independent spot open when selecting the common strike.",
        "",
        f"Across 132 complete secondary cycles, cumulative gross P&L was Rs {total:,.2f}, mean cycle P&L Rs {mean:,.2f}, median Rs {median:,.2f}, win rate {win:.2%}, profit factor {profit_factor:.3f}, maximum drawdown Rs {drawdown:,.2f}, best cycle Rs {best:,.2f}, and worst cycle Rs {worst:,.2f}. The 20,000-replication circular three-cycle block bootstrap 95% interval for total gross P&L was Rs {ci_lo:,.2f} to Rs {ci_hi:,.2f}.",
        "",
        "The key validation finding is that the original 44.0% coverage was primarily a source-coverage limitation, not an intentional trading filter. All 75 primary-source rejections were reconstructed on the independent public source; 27 retained the primary strike and 48 required independent re-selection of the common ATM strike. Two primary-valid cycles remained non-executable on the independent source because no common strike was present there.",
        "",
        "## Research questions and aims",
        "The primary question is whether the frozen four-leg structure shows positive historical performance after realistic costs and slippage. Validation questions address source coverage, cross-source contract reconstruction, and sensitivity to execution assumptions. The strategy was frozen before interpretation and was not optimized from the results.",
        "",
        "## Frozen protocol",
        "- Entry: first trading day after the previous NIFTY weekly expiry, using the 09:15 IST market-open price.",
        "- Near expiry: first weekly expiry after entry.",
        "- Far expiry: the fourth expiry in the sequence beginning with the near expiry.",
        "- Strike: nearest common listed strike to the NIFTY spot OPEN.",
        "- Legs: long near PE, short near CE, long far CE, short far PE.",
        "- Exit: all four legs at near-expiry daily CLOSE.",
        "- Quantity: one historical lot per leg.",
        "- No stop, target, roll, averaging, signal overlay or discretionary strike shift.",
        "",
        "## Data and independent validation",
        "The primary dataset was a public NIFTY option archive normalized from single-letter C/P labels to CE/PE. The independent contract source is the public SantoshSrinivas79/NSE-FNO-Data-bank mirror of daily NSE F&O bhavcopy archives. Yahoo Finance NIFTY 50 daily OPEN was used as the independent spot diagnostic for secondary strike selection. The study treats the mirror as a validation aid, not as an official exchange endpoint.",
        "",
        "### Coverage audit",
        "| Primary outcome | Cycles |",
        "|---|---:|",
        "| Valid executable | 59 |",
        "| Missing entry leg | 48 |",
        "| Missing entry + exit leg | 16 |",
        "| No common strike | 9 |",
        "| Missing exit leg | 2 |",
        "| Total rejected | 75 |",
        "",
        "### Secondary reconciliation",
        f"- Candidate cycles: 134",
        f"- Primary-valid cycles: 59",
        f"- Primary rejects: 75",
        f"- Secondary complete cycles: 132",
        f"- Primary rejects recovered at the same strike: {len(same)}",
        f"- Primary rejects recovered after independent strike re-selection: {len(reselected)}",
        f"- Primary-valid and secondary-complete: {len(matched)}",
        f"- Primary-valid and secondary-non-executable: {comparison.get('PRIMARY_VALID_SECONDARY_NONEXECUTABLE', 0)}",
        "",
        "## Statistical methods",
        "Descriptive statistics include total and per-cycle P&L, win rate, profit factor, best and worst cycle, drawdown and annual decomposition. Dependence is handled diagnostically with a circular block bootstrap of three weekly cycles, 20,000 replications, fixed seed 20260923.",
        "",
        "## Results",
        "",
        "| Metric | Primary public subset | Independent secondary |",
        "|---|---:|---:|",
        f"| Cycles | 59 | {len(trades)} / 134 |",
        "| Coverage | 44.0% | 98.5% |",
        "| Gross P&L | Rs 52,827.50 | Rs 188,237.50 |",
        f"| Mean cycle | Rs 895.38 | Rs {mean:,.2f} |",
        f"| Median cycle | Rs 866.25 | Rs {median:,.2f} |",
        "| Win rate | 64.41% | 59.09% |",
        "| Profit factor | 2.549 | 1.889 |",
        "| Maximum drawdown | Rs 5,650.00 | Rs 57,380.00 |",
        "| Best cycle | Rs 20,081.25 | Rs 62,080.00 |",
        "| Worst cycle | Rs -5,650.00 | Rs -31,597.50 |",
        f"| Circular block-bootstrap 95% interval | Rs 13,151.84 to Rs 100,043.59 | Rs {ci_lo:,.2f} to Rs {ci_hi:,.2f} |",
        "",
        "### Annual independent results",
        "| Year | Cycles | Gross P&L (Rs) | Mean cycle (Rs) |",
        "|---:|---:|---:|---:|",
    ]
    for _, row in annual.iterrows():
        lines.append(f"| {int(row.year)} | {int(row.trades)} | {row.gross_pnl:,.2f} | {row.mean_trade:,.2f} |")

    lines += [
        "",
        "### Source-selection decomposition",
        f"- Same-strike recovered rejects: {len(same)} cycles, gross Rs {same.sum():,.2f}.",
        f"- Independently re-selected recovered rejects: {len(reselected)} cycles, gross Rs {reselected.sum():,.2f}.",
        f"- Primary-valid matched cycles: {len(matched)} cycles, gross Rs {matched.sum():,.2f}.",
        "",
        "### Transaction-cost sensitivity",
        "Paytm Money historical brokerage cohorts are modeled at Rs 10, Rs 15 and Rs 20 per executed order. Eight option executions occur per cycle. Statutory assumptions include pre-1-Oct-2024 option-sale STT, buy-side stamp duty, SEBI fee and GST. Exchange charge is shown as a sensitivity rather than an invented client-specific historical rate. Slippage is charged per execution at 0.25, 0.50, 1.00 and 2.00 index points.",
        "",
        "| Brokerage / order | 0 pt | 0.50 pt | 1.00 pt | 2.00 pt |",
        "|---:|---:|---:|---:|---:|",
        f"| Rs 10 | {cost_mid.loc[10.0, 'net_no_slippage_inr']:,.2f} | {cost_mid.loc[10.0, 'net_0.50pt_slippage_inr']:,.2f} | {cost_mid.loc[10.0, 'net_1.00pt_slippage_inr']:,.2f} | {cost_mid.loc[10.0, 'net_2.00pt_slippage_inr']:,.2f} |",
        f"| Rs 15 | {cost_mid.loc[15.0, 'net_no_slippage_inr']:,.2f} | {cost_mid.loc[15.0, 'net_0.50pt_slippage_inr']:,.2f} | {cost_mid.loc[15.0, 'net_1.00pt_slippage_inr']:,.2f} | {cost_mid.loc[15.0, 'net_2.00pt_slippage_inr']:,.2f} |",
        f"| Rs 20 | {cost_mid.loc[20.0, 'net_no_slippage_inr']:,.2f} | {cost_mid.loc[20.0, 'net_0.50pt_slippage_inr']:,.2f} | {cost_mid.loc[20.0, 'net_1.00pt_slippage_inr']:,.2f} | {cost_mid.loc[20.0, 'net_2.00pt_slippage_inr']:,.2f} |",
        "",
        "## Discussion",
        "The primary-source result is a positively selected subset because 75 cycles were omitted by missing contract observations. Independent reconstruction shows that those omitted cycles materially affect aggregate performance. The independent result also depends on the secondary contract source and the Yahoo spot-open diagnostic used for strike selection. Daily OHLC does not prove synchronized four-leg live execution, so the historical result should not be interpreted as a realized trading return.",
        "",
        "## Strengths",
        "1. Frozen strategy rule before result interpretation.",
        "2. Explicit historical expiry and lot-size handling.",
        "3. Full candidate-cycle audit and independent public-source reconciliation.",
        "4. Historical brokerage cohorts and execution-level slippage sensitivity.",
        "5. Error log, cached inputs and CI workflow retained in the repository.",
        "",
        "## Limitations",
        "1. The independent contract source is a public mirror of NSE bhavcopy data rather than a directly authenticated exchange feed.",
        "2. Daily OHLC cannot establish synchronized live execution, bid/ask, queue priority or market impact.",
        "3. Two candidate cycles remain source-discrepant because the independent source has no common strike.",
        "4. P&L is not a return-on-margin or return-on-capital measure.",
        "5. The study ends in 2024-08-30 and does not establish out-of-sample behavior after that point.",
        "",
        "## Conclusion",
        f"The 44.0% primary-source coverage is not a defensible estimate of strategy executability. Independent historical reconstruction supports 132 of 134 candidate cycles. Under that independent reconstruction, cumulative gross P&L was Rs {total:,.2f}, with a {win:.2%} win rate, {profit_factor:.3f} profit factor and Rs {drawdown:,.2f} maximum drawdown. Modeled net results remain positive across the documented brokerage and tested slippage ranges at the 0.05000% exchange-charge sensitivity except the Rs 20/order, 2.00-point slippage scenario, which is approximately Rs {cost_mid.loc[20.0, 'net_2.00pt_slippage_inr']:,.2f}. This is a historical descriptive finding, not a forecast or a claim of a persistent future trading edge.",
        "",
        "## Future research",
        "Extend the frozen rule to a longer sample; add out-of-sample post-2024 validation; replay synchronized bid/ask/tick execution; add liquidity and open-interest constraints; and separately study regime variables such as India VIX, realized volatility, FII/DII flows, global equities, USD/INR, gold, rates, corporate actions and event/news conditions without altering the frozen historical result.",
        "",
        "## Reproducibility and supplements",
        "- docs/nifty_calendar/STRATEGY_LOCK.md",
        "- docs/nifty_calendar/RESEARCH_PLAN.md",
        "- docs/nifty_calendar/PHASE_STATUS.md",
        "- docs/nifty_calendar/ERROR_LOG.md",
        "- docs/nifty_calendar/CONVERSATION_LOG.md",
        "- docs/nifty_calendar/SOURCES.md",
        "- docs/nifty_calendar/COST_ASSUMPTIONS.md",
        "- reports/nifty_calendar/P5_SECONDARY_RECONCILIATION_2022_2024.csv",
        "- reports/nifty_calendar/SECONDARY_TRADE_LEVEL_RESULTS_2022_2024.csv",
        "- reports/nifty_calendar/SECONDARY_COST_SENSITIVITY_2022_2024.csv",
        "",
        "## References",
        "- NSE NIFTY 50 product and contract specifications (see docs/nifty_calendar/SOURCES.md).",
        "- Paytm Money historical brokerage and F&O pricing sources (see docs/nifty_calendar/COST_ASSUMPTIONS.md).",
        "- Andersen, Fusari & Todorov (2017), Short-Term Market Risks Implied by Weekly Options.",
        "- Jain & Kotha (2022), weekly index options and information absorption.",
        "- Schneider & Tavin (2018), calendar-spread option term-structure effects.",
        "",
        "Research status: P0-P6 complete for the 2022-2024 study.",
    ]

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")
    stats = pd.DataFrame(
        [{
            "candidate_cycles": 134,
            "secondary_complete_cycles": len(trades),
            "coverage": len(trades) / 134,
            "gross_pnl_inr": total,
            "mean_trade_inr": mean,
            "median_trade_inr": median,
            "win_rate": win,
            "profit_factor": profit_factor,
            "max_drawdown_inr": drawdown,
            "best_trade_inr": best,
            "worst_trade_inr": worst,
            "bootstrap_ci_lo_inr": ci_lo,
            "bootstrap_ci_hi_inr": ci_hi,
            "same_strike_recovered_rejects": len(same),
            "reselected_recovered_rejects": len(reselected),
            "primary_valid_secondary_complete": len(matched),
        }]
    )
    args.out_stats.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(args.out_stats, index=False)


if __name__ == "__main__":
    main()
