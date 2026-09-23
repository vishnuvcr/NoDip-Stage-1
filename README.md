# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P6 complete for the 2022-2024 study. Strategy remains frozen.**

### Independently reconciled historical result

- Candidate cycles: 134
- Independent-secondary complete cycles: 132 (98.5% coverage)
- All 75 primary-source rejects recovered on the independent source
- Gross P&L: ₹127,185.00
- Win rate: 57.58%
- Profit factor: 1.542
- Maximum drawdown: ₹90,152.50
- Bootstrap 95% interval for total gross P&L: ₹-67,517.25 to ₹342,106.84
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
| ₹10/order | ₹105,167.95 | ₹80,817.95 | ₹56,467.95 | ₹7,767.95 |
| ₹15/order | ₹98,937.55 | ₹74,587.55 | ₹50,237.55 | ₹1,537.55 |
| ₹20/order | ₹92,707.15 | ₹68,357.15 | ₹44,007.15 | ₹-4,692.85 |

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

P6 GitHub Actions validation run 4 succeeded. Repository tests: 4 passed. The manuscript assets and internal research outputs passed file/link checks.

## Next research directions

The closed study identifies, but does not apply, future work on longer history, strict out-of-sample validation, intraday executable bid/ask replay, liquidity constraints, regime stratification, and exact historical broker contract-note validation.
