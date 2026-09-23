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
    c = np.cumsum(x)
    return float((c - np.maximum.accumulate(c)).min())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict-ledger", required=True, type=Path)
    ap.add_argument("--recon", required=True, type=Path)
    ap.add_argument("--strict-costs", required=True, type=Path)
    ap.add_argument("--primary-trades", required=True, type=Path)
    ap.add_argument("--out-report", required=True, type=Path)
    ap.add_argument("--out-stats", required=True, type=Path)
    ap.add_argument("--out-annual", required=True, type=Path)
    ap.add_argument("--fig-dir", required=True, type=Path)
    args = ap.parse_args()

    strict = pd.read_csv(args.strict_ledger, parse_dates=["entry_date", "near_expiry", "far_expiry"]).sort_values("entry_date").reset_index(drop=True)
    recon = pd.read_csv(args.recon)
    costs = pd.read_csv(args.strict_costs)
    primary = pd.read_csv(args.primary_trades)

    if len(strict) != 84:
        raise SystemExit(f"Expected 84 strict trades, got {len(strict)}")

    x = strict["pnl_inr"].astype(float).to_numpy()
    total = float(x.sum())
    mean = float(x.mean())
    median = float(np.median(x))
    win = float((x > 0).mean())
    profit_factor = float(x[x > 0].sum() / (-x[x < 0].sum()))
    drawdown = max_dd(x)
    best = float(x.max())
    worst = float(x.min())
    ci_lo, ci_hi = bootstrap_ci(x)

    annual = strict.assign(year=strict["entry_date"].dt.year).groupby("year", as_index=False).agg(
        trades=("pnl_inr", "size"),
        gross_pnl=("pnl_inr", "sum"),
        mean_trade=("pnl_inr", "mean"),
        win_rate=("pnl_inr", lambda z: float((z > 0).mean())),
    )

    primary_valid_match = recon[recon["comparison_status"].eq("PRIMARY_VALID_SECONDARY_COMPLETE")]
    recovered_exact = recon[recon["comparison_status"].eq("RECOVERED_BY_SECONDARY_EXACT")]
    reselected = recon[recon["comparison_status"].eq("RECOVERED_BY_SECONDARY_RESELECTED")]
    unresolved = recon[recon["comparison_status"].eq("PRIMARY_REJECTED_SECONDARY_NONEXECUTABLE")]
    primary_only_gap = recon[recon["comparison_status"].eq("PRIMARY_VALID_SECONDARY_NONEXECUTABLE")]

    args.fig_dir.mkdir(parents=True, exist_ok=True)

    curve = np.cumsum(x)
    dd = curve - np.maximum.accumulate(curve)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(strict["entry_date"], curve)
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Strict frozen-protocol cumulative gross P&L")
    ax.set_xlabel("Entry date")
    ax.set_ylabel("Cumulative P&L (INR)")
    fig.tight_layout()
    fig.savefig(args.fig_dir / "cumulative_pnl.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(strict["entry_date"], dd)
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Strict frozen-protocol drawdown")
    ax.set_xlabel("Entry date")
    ax.set_ylabel("Drawdown (INR)")
    fig.tight_layout()
    fig.savefig(args.fig_dir / "drawdown.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(annual["year"].astype(str), annual["gross_pnl"])
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Annual strict frozen-protocol gross P&L")
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

    strict_out = strict.copy()
    strict_out["year"] = strict_out["entry_date"].dt.year
    strict_out.to_csv(args.out_annual, index=False)

    report = f"""
# NIFTY 4-Leg Weekly / 3-Week Calendar — 2022-2024 Research Manuscript

## Abstract

This study evaluates a frozen four-leg NIFTY 50 option structure using a pre-specified, non-discretionary entry, strike, expiry, and exit protocol. The strategy enters on the first trading session after the previous NIFTY weekly expiry at the 09:15 IST open, buys the near-expiry ATM put, sells the near-expiry ATM call, buys the same-strike farther-expiry call, and sells the same-strike farther-expiry put. All four positions are closed at the near-expiry daily close. No adjustment, rolling, stop, target, averaging or post-hoc signal is allowed.

A primary public option archive produced 59 apparently executable cycles from 134 candidate cycles. Independent reconciliation against a public mirror of NSE F&O bhavcopy archives audited all 134 candidates. During verification, zero option OPEN values associated with zero contract volume were identified as non-executable observations; those rows were not treated as fills. After this correction, 84 cycles are independently constructible at the same strike selected by the frozen primary protocol. A further 28 cycles can be reconstructed only after a source-specific strike re-selection, so they are retained as sensitivity evidence rather than included in the strict frozen-protocol result. Twenty primary-rejected cycles remain non-executable on the independent source, and two primary-valid cycles do not reproduce on the independent source.

Across the 84-cycle strict frozen-protocol validation sample, gross P&L is ₹{total:,.2f}, mean cycle P&L ₹{mean:,.2f}, median cycle P&L ₹{median:,.2f}, win rate {win:.2%}, profit factor {profit_factor:.3f}, and maximum drawdown ₹{abs(drawdown):,.2f}. The 20,000-replication circular three-cycle block bootstrap 95% interval for total gross P&L is ₹{ci_lo:,.2f} to ₹{ci_hi:,.2f}. These statistics are descriptive historical results and do not establish future expected returns or live execution performance.

## Research questions and aims

The primary question is whether the frozen four-leg structure shows positive historical performance after realistic costs and slippage. Validation questions address source coverage, cross-source contract reconstruction, and sensitivity to execution assumptions.

The aims are to establish a reproducible historical baseline, isolate data-quality effects from trading-rule effects, quantify P&L distribution and drawdown, and document realistic cost sensitivity without changing the frozen rule.

## Background and literature review

Weekly options introduce short-dated exposures in which implied volatility, time decay and expiry-specific microstructure can change rapidly. Prior academic work has examined the risk embedded in weekly options, the market effects of weekly-index-option introduction, expiry-day effects, and calendar-spread term structures. The literature reviewed for this project includes Andersen, Fusari and Todorov on short-term market risks implied by weekly options; Jain and Kotha on information absorption after weekly index options; Kumar on expiry-day effects; and Schneider and Tavin on calendar-spread option term structures.

The literature motivates the research design but does not supply the present strategy rule. The contribution here is a mechanically frozen historical implementation with explicit source reconciliation and transaction-cost treatment.

Official market-structure material was taken from NSE NIFTY 50 and equity-derivatives specifications, historical contract/price archives, lot-size circulars, and expiry-day revision material. Paytm Money historical pricing material was used only for documented brokerage-cohort scenarios and publicly exposed charge rules. The full source list is maintained in docs/nifty_calendar/SOURCES.md.

## Frozen strategy protocol

The strategy is frozen in docs/nifty_calendar/STRATEGY_LOCK.md.

| Component | Rule |
|---|---|
| Entry session | First trading day after the previous NIFTY weekly expiry |
| Entry time | 09:15 IST session open |
| Near expiry | First weekly NIFTY expiry after entry |
| Far expiry | Fourth expiry in the sequence beginning with the near expiry |
| Strike | Nearest listed common strike to the frozen NIFTY spot OPEN |
| Leg 1 | Buy 1 near-expiry PE |
| Leg 2 | Sell 1 near-expiry CE |
| Leg 3 | Buy 1 far-expiry CE |
| Leg 4 | Sell 1 far-expiry PE |
| Exit | Near-expiry trading-day CLOSE for all four legs |
| Quantity | One historically applicable lot per leg |
| Adjustments | None |

For execution validation, a contract OPEN is considered executable only when it is strictly positive. Zero or null opens are not accepted as executable fills.

## Data sources and preprocessing

The primary study dataset is a public NIFTY option archive normalized from single-letter C/P labels to CE/PE.

The independent contract source is the public SantoshSrinivas79/NSE-FNO-Data-bank mirror of daily NSE F&O bhavcopy archives. It is treated as a validation aid rather than as an authenticated exchange endpoint.

Yahoo Finance NIFTY 50 daily OPEN values are used only as a diagnostic cross-check and do not override the frozen primary spot value when deciding the strict frozen-protocol strike.

### Primary coverage audit

| Primary outcome | Cycles |
|---|---:|
| Primary-valid executable | 59 |
| Missing entry leg | 48 |
| Missing entry + exit leg | 16 |
| No common strike | 9 |
| Missing exit leg | 2 |
| Primary-rejected total | 75 |
| Candidate cycles | 134 |

### Independent reconciliation

| Reconciliation outcome | Cycles |
|---|---:|
| Primary-valid and independently executable | {len(primary_valid_match)} |
| Primary rejects recovered at the same primary strike | {len(recovered_exact)} |
| Primary rejects recovered only after source-specific strike re-selection | {len(reselected)} |
| Primary rejects still non-executable | {len(unresolved)} |
| Primary-valid but not independently reproducible | {len(primary_only_gap)} |

Thus, the strict frozen-protocol independent validation sample is {len(strict)} cycles ({len(strict)/134:.1%} of all candidates). The 28 source-specific re-selections are reported separately and are not used as the main performance estimate.

## Statistical methodology

Descriptive measures are total P&L, mean and median cycle P&L, win rate, profit factor, best/worst trade, cumulative P&L, maximum drawdown, and annual decomposition.

Because weekly strategy cycles form a time series rather than independent observations, a circular block bootstrap with block length three cycles and 20,000 replications is used as a diagnostic interval for cumulative P&L. The seed is fixed at 20260923 for reproducibility. The interval is not a model-free guarantee of future profitability.

### Transaction costs

Eight option executions occur per completed cycle. The model includes:
- Paytm Money historical brokerage scenarios of ₹10, ₹15, and ₹20 per executed order.
- 0.0625% STT on option sales during the sample window.
- 0.003% buyer-side stamp duty.
- 0.0001% SEBI turnover fee.
- 18% GST on applicable brokerage, SEBI and exchange charges.
- Exchange-charge sensitivity at 0.03503%, 0.05000% and 0.05300% of option premium turnover.
- Adverse slippage of 0.25, 0.50, 1.00 and 2.00 index points per execution.

Paytm Money's public historical exchange pass-through is not sufficiently exposed to reconstruct an exact client-specific historical rate for every period, so the analysis reports exchange-charge sensitivities rather than inventing a contract-note rate.

## Results

| Metric | Primary source | Strict independent validation |
|---|---:|---:|
| Candidate cycles | 134 | 134 |
| Executable cycles | 59 | 84 |
| Coverage | 44.0% | {len(strict)/134:.1%} |
| Gross P&L | ₹52,827.50 | ₹{total:,.2f} |
| Mean cycle | ₹895.38 | ₹{mean:,.2f} |
| Median cycle | ₹866.25 | ₹{median:,.2f} |
| Win rate | 64.41% | {win:.2%} |
| Profit factor | 2.549 | {profit_factor:.3f} |
| Max drawdown | ₹5,650.00 | ₹{abs(drawdown):,.2f} |
| Best cycle | ₹20,081.25 | ₹{best:,.2f} |
| Worst cycle | ₹-5,650.00 | ₹{worst:,.2f} |
| Bootstrap 95% interval | ₹13,151.84 to ₹100,043.59 | ₹{ci_lo:,.2f} to ₹{ci_hi:,.2f} |

### Annual decomposition

| Year | Cycles | Gross P&L (₹) | Mean cycle (₹) | Win rate |
|---:|---:|---:|---:|---:|
"""
    for _, row in annual.iterrows():
        report += f"| {int(row.year)} | {int(row.trades)} | {row.gross_pnl:,.2f} | {row.mean_trade:,.2f} | {row.win_rate:.2%} |\n"

    mid = costs[costs["exchange_rate"].eq(0.0005)].copy().sort_values("brokerage_per_order")
    report += """
### Source-reconciliation decomposition

"""
    report += f"- Primary-valid cycles independently reproduced: {len(primary_valid_match)}, gross P&L ₹{primary_valid_match['secondary_pnl_inr'].dropna().astype(float).sum():,.2f}.\n"
    report += f"- Primary-rejected cycles recovered at the same strike: {len(recovered_exact)}, gross P&L ₹{recovered_exact['secondary_pnl_inr'].dropna().astype(float).sum():,.2f}.\n"
    report += f"- Primary-rejected cycles recovered only after source-specific re-selection: {len(reselected)}, gross P&L ₹{reselected['secondary_pnl_inr'].dropna().astype(float).sum():,.2f}.\n"
    report += f"- Primary-rejected cycles still non-executable: {len(unresolved)}.\n"
    report += f"- Primary-valid cycles not independently reproducible: {len(primary_only_gap)}.\n"
    report += "\nThe strict estimate therefore includes only the 57 independently reproducible primary-valid cycles and the 27 primary-rejected cycles recovered at the same primary strike. The 28 reselected cycles are not counted in the strict result.\n"

    report += """
### Transaction-cost sensitivity at 0.05000% exchange-charge sensitivity

| Brokerage / order | 0 pt | 0.50 pt | 1.00 pt | 2.00 pt |
|---:|---:|---:|---:|---:|
"""
    for _, row in mid.iterrows():
        report += f"| ₹{row.brokerage_per_order:.0f} | ₹{row.net_no_slippage_inr:,.2f} | ₹{row['net_0.50pt_slippage_inr']:,.2f} | ₹{row['net_1.00pt_slippage_inr']:,.2f} | ₹{row['net_2.00pt_slippage_inr']:,.2f} |\n"

    net20_2 = mid.loc[mid["brokerage_per_order"].eq(20.0), "net_2.00pt_slippage_inr"].iloc[0]
    report += f"""
## Discussion

The original 44.0% primary-source coverage should not be interpreted as the strategy inherently trading in only 44% of candidate cycles. Independent reconciliation shows that the primary dataset omitted or misrepresented a substantial number of contract observations.

The independent audit also prevents the opposite overstatement. It found 20 primary rejects that still fail executable-entry reconstruction and two primary-valid cycles that do not reproduce on the independent source. It also found 28 cycles for which the independent source requires a different common strike. Those 28 are not silently folded into the strict frozen-protocol result because doing so would change the frozen strike-selection rule.

The strict evidence base is therefore larger than the original 59-cycle subset but smaller than the 132-cycle reconstructed union.

Daily OHLC establishes daily bar endpoints but not synchronized bid/ask fills across four option legs. The historical result should therefore be read as a reproducible mark-to-market simulation, not as a realized live-trading return.

## Strengths

1. Frozen strategy rule before result interpretation.
2. Explicit historical expiry and lot-size handling.
3. Full 134-cycle coverage audit.
4. Independent public contract-source reconciliation.
5. Zero-open/non-traded option rows excluded from executable fills.
6. Historical brokerage cohorts and per-execution slippage sensitivity.
7. Error log, cached data and CI workflows retained in the repository.

## Limitations

1. The independent contract source is a public mirror of NSE bhavcopy data.
2. Daily bars cannot establish synchronized live four-leg execution.
3. Twenty primary rejects remain non-executable on the independent source.
4. Twenty-eight cycles are source-sensitive because they require alternative secondary strike selection.
5. Two primary-valid cycles are not independently reproduced.
6. P&L is not normalized to margin, capital-at-risk or portfolio return.
7. The sample ends on 2024-08-30 and contains no genuine post-2024 holdout.

## Conclusion

The validated final historical result is the 84-cycle strict frozen-protocol sample. Gross P&L is ₹{total:,.2f}, win rate {win:.2%}, profit factor {profit_factor:.3f}, and maximum drawdown ₹{abs(drawdown):,.2f}. Under the 0.05000% exchange-charge sensitivity, the ₹20/order brokerage case remains positive through the tested 2.00-point adverse-slippage scenario at approximately ₹{net20_2:,.2f}.

This is a historical descriptive result. It does not establish a persistent future trading edge, an expected return, or a promise of executable live fills.

## Future research

The next scientifically useful extensions are to lengthen the sample, preserve a genuine post-2024 holdout, obtain synchronized bid/ask or tick-level execution data, quantify liquidity and open-interest conditions, and evaluate market-regime covariates such as India VIX, realized volatility, FII/DII flows, global equities, USD/INR, gold, rates, corporate actions and event/news windows without altering the frozen historical result.

Any future strategy modification should be treated as a new protocol and should not overwrite this historical baseline.

## Reproducibility and supplementary materials

- docs/nifty_calendar/STRATEGY_LOCK.md
- docs/nifty_calendar/RESEARCH_PLAN.md
- docs/nifty_calendar/PHASE_STATUS.md
- docs/nifty_calendar/ERROR_LOG.md
- docs/nifty_calendar/CONVERSATION_LOG.md
- docs/nifty_calendar/SOURCES.md
- docs/nifty_calendar/COST_ASSUMPTIONS.md
- reports/nifty_calendar/P5_SECONDARY_RECONCILIATION_2022_2024.csv
- reports/nifty_calendar/STRICT_TRADE_LEVEL_RESULTS_2022_2024.csv
- reports/nifty_calendar/STRICT_COST_SENSITIVITY_2022_2024.csv
- reports/nifty_calendar/STRICT_ANNUAL_RESULTS_2022_2024.csv
- reports/nifty_calendar/figures/cumulative_pnl.svg
- reports/nifty_calendar/figures/drawdown.svg
- reports/nifty_calendar/figures/annual_pnl.svg
- reports/nifty_calendar/figures/cost_sensitivity.svg

## References

1. NSE NIFTY 50 product and contract specifications; see docs/nifty_calendar/SOURCES.md.
2. NSE historical derivatives archives and expiry/lot-size circulars; see docs/nifty_calendar/SOURCES.md.
3. Paytm Money historical brokerage and F&O pricing material; see docs/nifty_calendar/COST_ASSUMPTIONS.md.
4. Andersen, Fusari & Todorov (2017), Short-Term Market Risks Implied by Weekly Options.
5. Jain & Kotha (2022), weekly index options and information absorption.
6. Kumar (2022), expiry-day effects and weekly index options.
7. Schneider & Tavin (2018), calendar-spread option term-structure effects.

## Appendix A — Study population

Candidate cycles: 134.

Primary-source executable cycles: 59.

Strict independent frozen-protocol cycles: 84.

Independent re-selection sensitivity cycles: 28.

Primary rejects still non-executable: 20.

Primary-valid cycles not independently reproducible: 2.

## Appendix B — Trade-level data

The complete strict 84-cycle trade-level ledger is committed as CSV. It contains every entry date, near/far expiry, selected strike, lot sizes, all eight option prices, source classification and INR P&L.

## Appendix C — Cost methodology

The cost sensitivity is computed from the exact premium turnover of the strict ledger. Each cycle has eight option executions. Slippage is charged per execution using the applicable historical lot size. The broker cohort is applied consistently across all eight executions.

## Appendix D — Data-validation notes

The project error log records the major data and workflow failures, including the public ticker-schema mismatch, incomplete primary coverage, NSE-host timeouts, independent-mirror filename issues, and the zero-open/non-traded observation issue discovered during final reconciliation.

## Appendix E — Figure index

1. reports/nifty_calendar/figures/cumulative_pnl.svg — strict cumulative gross P&L.
2. reports/nifty_calendar/figures/drawdown.svg — strict drawdown.
3. reports/nifty_calendar/figures/annual_pnl.svg — annual gross P&L.
4. reports/nifty_calendar/figures/cost_sensitivity.svg — cost and slippage sensitivity.

## Final status

P0-P6 are complete for the 2022-2024 research package. The 84-cycle strict frozen-protocol result is the final validated historical estimate; the 28 source-specific re-selection cycles are retained as sensitivity evidence and are not merged into the strict result.
"""

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(report, encoding="utf-8")

    stats = pd.DataFrame([{
        "candidate_cycles": 134,
        "strict_frozen_cycles": len(strict),
        "strict_coverage": len(strict) / 134,
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
        "primary_valid_secondary_complete": len(primary_valid_match),
        "recovered_exact": len(recovered_exact),
        "reselected_sensitivity": len(reselected),
        "unresolved_primary_rejects": len(unresolved),
        "primary_valid_secondary_nonexec": len(primary_only_gap),
    }])
    args.out_stats.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(args.out_stats, index=False)
    print(f"Wrote manuscript: {args.out_report}")
    print(f"Strict cycles: {len(strict)}, gross P&L: {total:,.2f}, profit factor: {profit_factor:.3f}")


if __name__ == "__main__":
    main()
