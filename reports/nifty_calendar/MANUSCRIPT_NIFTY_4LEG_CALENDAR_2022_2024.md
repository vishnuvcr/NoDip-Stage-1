# Final NIFTY 4-Leg Calendar Manuscript — 2022-2024

## Abstract
This study evaluates a frozen four-leg NIFTY 50 weekly/three-week calendar rule with no discretionary adjustment. The primary public dataset initially produced only 59 complete cycles from 134 candidate cycles. Independent reconciliation against a public mirror of NSE F&O bhavcopy archives and an independent NIFTY spot-open diagnostic reconstructed 132 complete cycles. The independent secondary re-run re-applies the frozen common-ATM rule using the independent spot open when selecting the common strike.

Across 132 complete secondary cycles, cumulative gross P&L was Rs 188,237.50, mean cycle P&L Rs 1,426.04, median Rs 580.63, win rate 59.09%, profit factor 1.889, maximum drawdown Rs -57,380.00, best cycle Rs 62,080.00, and worst cycle Rs -31,597.50. The 20,000-replication circular three-cycle block bootstrap 95% interval for total gross P&L was Rs 6,927.47 to Rs 408,770.34.

The key validation finding is that the original 44.0% coverage was primarily a source-coverage limitation, not an intentional trading filter. All 75 primary-source rejections were reconstructed on the independent public source; 27 retained the primary strike and 48 required independent re-selection of the common ATM strike. Two primary-valid cycles remained non-executable on the independent source because no common strike was present there.

## Research questions and aims
The primary question is whether the frozen four-leg structure shows positive historical performance after realistic costs and slippage. Validation questions address source coverage, cross-source contract reconstruction, and sensitivity to execution assumptions. The strategy was frozen before interpretation and was not optimized from the results.

## Frozen protocol
- Entry: first trading day after the previous NIFTY weekly expiry, using the 09:15 IST market-open price.
- Near expiry: first weekly expiry after entry.
- Far expiry: the fourth expiry in the sequence beginning with the near expiry.
- Strike: nearest common listed strike to the NIFTY spot OPEN.
- Legs: long near PE, short near CE, long far CE, short far PE.
- Exit: all four legs at near-expiry daily CLOSE.
- Quantity: one historical lot per leg.
- No stop, target, roll, averaging, signal overlay or discretionary strike shift.

## Data and independent validation
The primary dataset was a public NIFTY option archive normalized from single-letter C/P labels to CE/PE. The independent contract source is the public SantoshSrinivas79/NSE-FNO-Data-bank mirror of daily NSE F&O bhavcopy archives. Yahoo Finance NIFTY 50 daily OPEN was used as the independent spot diagnostic for secondary strike selection. The study treats the mirror as a validation aid, not as an official exchange endpoint.

### Coverage audit
| Primary outcome | Cycles |
|---|---:|
| Valid executable | 59 |
| Missing entry leg | 48 |
| Missing entry + exit leg | 16 |
| No common strike | 9 |
| Missing exit leg | 2 |
| Total rejected | 75 |

### Secondary reconciliation
- Candidate cycles: 134
- Primary-valid cycles: 59
- Primary rejects: 75
- Secondary complete cycles: 132
- Primary rejects recovered at the same strike: 27
- Primary rejects recovered after independent strike re-selection: 48
- Primary-valid and secondary-complete: 57
- Primary-valid and secondary-non-executable: 2

## Statistical methods
Descriptive statistics include total and per-cycle P&L, win rate, profit factor, best and worst cycle, drawdown and annual decomposition. Dependence is handled diagnostically with a circular block bootstrap of three weekly cycles, 20,000 replications, fixed seed 20260923.

## Results

| Metric | Primary public subset | Independent secondary |
|---|---:|---:|
| Cycles | 59 | 132 / 134 |
| Coverage | 44.0% | 98.5% |
| Gross P&L | Rs 52,827.50 | Rs 188,237.50 |
| Mean cycle | Rs 895.38 | Rs 1,426.04 |
| Median cycle | Rs 866.25 | Rs 580.63 |
| Win rate | 64.41% | 59.09% |
| Profit factor | 2.549 | 1.889 |
| Maximum drawdown | Rs 5,650.00 | Rs 57,380.00 |
| Best cycle | Rs 20,081.25 | Rs 62,080.00 |
| Worst cycle | Rs -5,650.00 | Rs -31,597.50 |
| Circular block-bootstrap 95% interval | Rs 13,151.84 to Rs 100,043.59 | Rs 6,927.47 to Rs 408,770.34 |

### Annual independent results
| Year | Cycles | Gross P&L (Rs) | Mean cycle (Rs) |
|---:|---:|---:|---:|
| 2022 | 46 | 78,342.50 | 1,703.10 |
| 2023 | 51 | 106,780.00 | 2,093.73 |
| 2024 | 35 | 3,115.00 | 89.00 |

### Source-selection decomposition
- Same-strike recovered rejects: 27 cycles, gross Rs -29,192.50.
- Independently re-selected recovered rejects: 48 cycles, gross Rs 161,846.25.
- Primary-valid matched cycles: 57 cycles, gross Rs 55,583.75.

### Transaction-cost sensitivity
Paytm Money historical brokerage cohorts are modeled at Rs 10, Rs 15 and Rs 20 per executed order. Eight option executions occur per cycle. Statutory assumptions include pre-1-Oct-2024 option-sale STT, buy-side stamp duty, SEBI fee and GST. Exchange charge is shown as a sensitivity rather than an invented client-specific historical rate. Slippage is charged per execution at 0.25, 0.50, 1.00 and 2.00 index points.

| Brokerage / order | 0 pt | 0.50 pt | 1.00 pt | 2.00 pt |
|---:|---:|---:|---:|---:|
| Rs 10 | 166,171.23 | 141,821.23 | 117,471.23 | 68,771.23 |
| Rs 15 | 159,940.83 | 135,590.83 | 111,240.83 | 62,540.83 |
| Rs 20 | 153,710.43 | 129,360.43 | 105,010.43 | 56,310.43 |

## Discussion
The primary-source result is a positively selected subset because 75 cycles were omitted by missing contract observations. Independent reconstruction shows that those omitted cycles materially affect aggregate performance. The independent result also depends on the secondary contract source and the Yahoo spot-open diagnostic used for strike selection. Daily OHLC does not prove synchronized four-leg live execution, so the historical result should not be interpreted as a realized trading return.

## Strengths
1. Frozen strategy rule before result interpretation.
2. Explicit historical expiry and lot-size handling.
3. Full candidate-cycle audit and independent public-source reconciliation.
4. Historical brokerage cohorts and execution-level slippage sensitivity.
5. Error log, cached inputs and CI workflow retained in the repository.

## Limitations
1. The independent contract source is a public mirror of NSE bhavcopy data rather than a directly authenticated exchange feed.
2. Daily OHLC cannot establish synchronized live execution, bid/ask, queue priority or market impact.
3. Two candidate cycles remain source-discrepant because the independent source has no common strike.
4. P&L is not a return-on-margin or return-on-capital measure.
5. The study ends in 2024-08-30 and does not establish out-of-sample behavior after that point.

## Conclusion
The 44.0% primary-source coverage is not a defensible estimate of strategy executability. Independent historical reconstruction supports 132 of 134 candidate cycles. Under that independent reconstruction, cumulative gross P&L was Rs 188,237.50, with a 59.09% win rate, 1.889 profit factor and Rs -57,380.00 maximum drawdown. Modeled net results remain positive across the tested brokerage, exchange-charge and slippage scenarios in the 2022-2024 sample, although the cushion narrows as execution costs increase. At Rs 20/order, 0.05000% exchange charges and 2.00-point adverse slippage, modeled cumulative net P&L is approximately Rs 56,310.43. This is a historical descriptive finding, not a forecast or a claim of a persistent future trading edge.

## Future research
Extend the frozen rule to a longer sample; add out-of-sample post-2024 validation; replay synchronized bid/ask/tick execution; add liquidity and open-interest constraints; and separately study regime variables such as India VIX, realized volatility, FII/DII flows, global equities, USD/INR, gold, rates, corporate actions and event/news conditions without altering the frozen historical result.

## Reproducibility and supplements
- docs/nifty_calendar/STRATEGY_LOCK.md
- docs/nifty_calendar/RESEARCH_PLAN.md
- docs/nifty_calendar/PHASE_STATUS.md
- docs/nifty_calendar/ERROR_LOG.md
- docs/nifty_calendar/CONVERSATION_LOG.md
- docs/nifty_calendar/SOURCES.md
- docs/nifty_calendar/COST_ASSUMPTIONS.md
- reports/nifty_calendar/P5_SECONDARY_RECONCILIATION_2022_2024.csv
- reports/nifty_calendar/SECONDARY_TRADE_LEVEL_RESULTS_2022_2024.csv
- reports/nifty_calendar/SECONDARY_COST_SENSITIVITY_2022_2024.csv

## References
- NSE NIFTY 50 product and contract specifications (see docs/nifty_calendar/SOURCES.md).
- Paytm Money historical brokerage and F&O pricing sources (see docs/nifty_calendar/COST_ASSUMPTIONS.md).
- Andersen, Fusari & Todorov (2017), Short-Term Market Risks Implied by Weekly Options.
- Jain & Kotha (2022), weekly index options and information absorption.
- Schneider & Tavin (2018), calendar-spread option term-structure effects.

Research status: P0-P6 complete for the 2022-2024 study.