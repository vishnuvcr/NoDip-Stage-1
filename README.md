### Final validated result

| Metric | Result |
|---|---:|
| Candidate cycles | 134 |
| Strict frozen-protocol cycles | 84 |
| Strict coverage | 62.7% |
| Primary-valid and independently reproduced | 57 |
| Primary rejects recovered at same strike | 27 |
| Source-specific strike-reselection sensitivity cycles | 28 |
| Primary rejects still non-executable | 20 |
| Primary-valid source discrepancies | 2 |
| Gross P&L | ₹83,030.00 |
| Mean cycle | ₹988.45 |
| Median cycle | ₹598.75 |
| Win rate | 61.90% |
| Profit factor | 2.942 |
| Maximum drawdown | ₹8,022.50 |
| Bootstrap 95% interval | ₹31,147.19 to ₹139,293.78 |

The strict result excludes source-specific strike re-selection and treats zero-open/non-traded option rows as non-executable. The prior 132-cycle union is retained only as a superseded validation intermediate.

# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P6 complete for the 2022-2024 study. Strategy remains frozen.**

### Independently reconciled historical result

- Candidate cycles: 134
- Independent-secondary complete cycles: 132 (98.5% coverage)
- All 75 primary-source rejects recovered on the independent source
- Gross P&L: ₹188,237.50
- Win rate: 59.09%
- Profit factor: 1.889
- Maximum drawdown: ₹57,380.00
- Bootstrap 95% interval for total gross P&L: ₹6,927.47 to ₹408,770.34
- Primary-source comparison remains documented separately: 59 executable cycles and ₹52,827.50 gross P&L

The 44.0% primary-source coverage was therefore a data-coverage limitation rather than an intentional strategy filter. Two primary-valid cycles remain source discrepancies because the independent source contains no common strike under the frozen same-strike rule.

## Frozen strategy

- First trading day after previous NIFTY weekly expiry.
- 09:15 IST market-open entry.
- ATM = nearest listed strike to NIFTY spot open.
- Buy near ATM PE.
- Sell near ATM CE.
- Buy same-strike far ATM CE.
- Sell same-strike far ATM PE.
- Far expiry = three weekly intervals after near expiry.
- Exit all four legs at near-expiry trading-day close.
- One historical lot per leg.
- No adjustments, rolling, target, stop-loss or averaging.

## Execution-cost sensitivity

At a 0.05% exchange-charge sensitivity:

| Brokerage | 0 pt slip | 0.50 pt | 1.00 pt | 2.00 pt |
|---:|---:|---:|---:|---:|
| ₹10/order | ₹166,171.23 | ₹141,821.23 | ₹117,471.23 | ₹68,771.23 |
| ₹15/order | ₹159,940.83 | ₹135,590.83 | ₹111,240.83 | ₹62,540.83 |
| ₹20/order | ₹153,710.43 | ₹129,360.43 | ₹105,010.43 | ₹56,310.43 |

These are modeled sensitivities, not claims of realized fills.

## Final manuscript and research files

- reports/nifty_calendar/MANUSCRIPT_NIFTY_4LEG_CALENDAR_2022_2024.md
- reports/nifty_calendar/FINAL_SECONDARY_STATISTICS_2022_2024.md
- reports/nifty_calendar/P5_RECONCILIATION_REPORT_2022_2024.md
- reports/nifty_calendar/P5_SECONDARY_RECONCILIATION_2022_2024.csv
- reports/nifty_calendar/SECONDARY_TRADE_LEVEL_RESULTS_2022_2024.csv
- reports/nifty_calendar/SECONDARY_COST_SENSITIVITY_2022_2024.csv
- reports/nifty_calendar/figures/cumulative_pnl.svg
- reports/nifty_calendar/figures/drawdown.svg
- reports/nifty_calendar/figures/annual_pnl.svg
- reports/nifty_calendar/figures/cost_sensitivity.svg
- docs/nifty_calendar/RESEARCH_PLAN.md
- docs/nifty_calendar/STRATEGY_LOCK.md
- docs/nifty_calendar/PHASE_STATUS.md
- docs/nifty_calendar/ERROR_LOG.md
- docs/nifty_calendar/CONVERSATION_LOG.md
- docs/nifty_calendar/P6_MANUSCRIPT_PLAN.md
- .github/workflows/p6-nifty-manuscript.yml

## Validation

P6 GitHub Actions validation is rerun from the corrected independent 132-cycle ledger; repository tests and manuscript/asset checks pass. Repository tests: 4 passed. The manuscript assets and internal research outputs passed file/link checks.

## Next research directions

The closed study identifies, but does not apply, future work on longer history, strict out-of-sample validation, intraday executable bid/ask replay, liquidity constraints, regime stratification, and exact historical broker contract-note validation.


## P7 loss audit / entry candidate

P7 audited all 32 losing trades in the strict 84-cycle sample. A candidate entry gate was identified:
`(far CE / near CE) / (far PE / near PE) <= 1.20`.

The gate retains 52/84 cycles in the historical sample and is **not** promoted into the frozen P6 strategy. It requires a genuinely unseen post-2024 validation before any live-use consideration.

- [P7 loss audit report](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/ENTRY_TUNING_REPORT_2022_2024.md)
- [P7 candidate entry criteria](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/ENTRY_CRITERIA_CANDIDATE_2022_2024.md)
- [P7 loss ledger](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/LOSS_AUDIT_2022_2024.csv)

## P8 unseen post-2024 validation
The fixed P7 candidate gate was evaluated unchanged on the post-2024 temporal holdout.
- P8 plan: docs/nifty_calendar/P8_OOS_VALIDATION_PLAN.md
- P8 candidate lock: docs/nifty_calendar/P8_OOS_CANDIDATE_LOCK.md
- P8 OOS report: reports/nifty_calendar/P8_OOS_VALIDATION_REPORT_2025_ONWARD.md
- P8 OOS ledger: reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv
