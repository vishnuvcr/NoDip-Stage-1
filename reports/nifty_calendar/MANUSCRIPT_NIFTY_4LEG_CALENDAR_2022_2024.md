
# NIFTY 4-Leg Weekly / 3-Week Calendar — 2022-2024 Research Manuscript

## Abstract

This study evaluates a frozen four-leg NIFTY 50 option structure using a pre-specified, non-discretionary entry, strike, expiry, and exit protocol. The strategy enters on the first trading session after the previous NIFTY weekly expiry at the 09:15 IST open, buys the near-expiry ATM put, sells the near-expiry ATM call, buys the same-strike farther-expiry call, and sells the same-strike farther-expiry put. All four positions are closed at the near-expiry daily close. No adjustment, rolling, stop, target, averaging or post-hoc signal is allowed.

A primary public option archive produced 59 apparently executable cycles from 134 candidate cycles. Independent reconciliation against a public mirror of NSE F&O bhavcopy archives audited all 134 candidates. During verification, zero option OPEN values associated with zero contract volume were identified as non-executable observations; those rows were not treated as fills. After this correction, 84 cycles are independently constructible at the same strike selected by the frozen primary protocol. A further 28 cycles can be reconstructed only after a source-specific strike re-selection, so they are retained as sensitivity evidence rather than included in the strict frozen-protocol result. Twenty primary-rejected cycles remain non-executable on the independent source, and two primary-valid cycles do not reproduce on the independent source.

Across the 84-cycle strict frozen-protocol validation sample, gross P&L is ₹83,030.00, mean cycle P&L ₹988.45, median cycle P&L ₹598.75, win rate 61.90%, profit factor 2.942, and maximum drawdown ₹8,022.50. The 20,000-replication circular three-cycle block bootstrap 95% interval for total gross P&L is ₹31,147.19 to ₹139,293.78. These statistics are descriptive historical results and do not establish future expected returns or live execution performance.

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
| Primary-valid and independently executable | 57 |
| Primary rejects recovered at the same primary strike | 27 |
| Primary rejects recovered only after source-specific strike re-selection | 28 |
| Primary rejects still non-executable | 20 |
| Primary-valid but not independently reproducible | 2 |

Thus, the strict frozen-protocol independent validation sample is 84 cycles (62.7% of all candidates). The 28 source-specific re-selections are reported separately and are not used as the main performance estimate.

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
| Coverage | 44.0% | 62.7% |
| Gross P&L | ₹52,827.50 | ₹83,030.00 |
| Mean cycle | ₹895.38 | ₹988.45 |
| Median cycle | ₹866.25 | ₹598.75 |
| Win rate | 64.41% | 61.90% |
| Profit factor | 2.549 | 2.942 |
| Max drawdown | ₹5,650.00 | ₹8,022.50 |
| Best cycle | ₹20,081.25 | ₹18,742.50 |
| Worst cycle | ₹-5,650.00 | ₹-5,363.75 |
| Bootstrap 95% interval | ₹13,151.84 to ₹100,043.59 | ₹31,147.19 to ₹139,293.78 |

### Annual decomposition

| Year | Cycles | Gross P&L (₹) | Mean cycle (₹) | Win rate |
|---:|---:|---:|---:|---:|
| 2022 | 15 | 1,200.00 | 80.00 | 46.67% |
| 2023 | 38 | 42,175.00 | 1,109.87 | 63.16% |
| 2024 | 31 | 39,655.00 | 1,279.19 | 67.74% |

### Source-reconciliation decomposition

- Primary-valid cycles independently reproduced: 57, gross P&L ₹55,583.75.
- Primary-rejected cycles recovered at the same strike: 27, gross P&L ₹27,446.25.
- Primary-rejected cycles recovered only after source-specific re-selection: 28, gross P&L ₹6,487.50.
- Primary-rejected cycles still non-executable: 20.
- Primary-valid cycles not independently reproducible: 2.

The strict estimate therefore includes only the 57 independently reproducible primary-valid cycles and the 27 primary-rejected cycles recovered at the same primary strike. The 28 reselected cycles are not counted in the strict result.

### Transaction-cost sensitivity at 0.05000% exchange-charge sensitivity

| Brokerage / order | 0 pt | 0.50 pt | 1.00 pt | 2.00 pt |
|---:|---:|---:|---:|---:|
| ₹10 | ₹69,136.41 | ₹54,136.41 | ₹39,136.41 | ₹9,136.41 |
| ₹15 | ₹65,171.61 | ₹50,171.61 | ₹35,171.61 | ₹5,171.61 |
| ₹20 | ₹61,206.81 | ₹46,206.81 | ₹31,206.81 | ₹1,206.81 |

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

The validated final historical result is the 84-cycle strict frozen-protocol sample. Gross P&L is ₹83,030.00, win rate 61.90%, profit factor 2.942, and maximum drawdown ₹8,022.50. Under the 0.05000% exchange-charge sensitivity, the ₹20/order brokerage case remains positive through the tested 2.00-point adverse-slippage scenario at approximately ₹1,206.81.

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
