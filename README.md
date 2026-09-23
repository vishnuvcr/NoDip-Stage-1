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
