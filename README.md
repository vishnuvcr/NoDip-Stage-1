# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P6 complete for the 2022-2024 frozen-strategy study.**

The study froze a four-leg NIFTY calendar structure before interpretation and then validated its historical data coverage with an independent public mirror of NSE F&O bhavcopy archives plus an independent NIFTY spot-open diagnostic.

### Final independently reconstructed result

| Metric | Result |
|---|---:|
| Candidate cycles | 134 |
| Complete independent cycles | 132 |
| Independent coverage | 98.5% |
| Primary-source valid cycles | 59 |
| Primary-source rejected cycles | 75 |
| Primary rejects recovered at same strike | 27 |
| Primary rejects recovered after independent strike re-selection | 48 |
| Gross P&L | ₹188,237.50 |
| Mean cycle | ₹1,426.04 |
| Median cycle | ₹580.63 |
| Win rate | 59.09% |
| Profit factor | 1.889 |
| Maximum drawdown | ₹57,380.00 |
| Bootstrap 95% interval | ₹6,927.47 to ₹408,770.34 |

At 0.05000% exchange-charge sensitivity, modeled cumulative net P&L is ₹166,171.23 / ₹159,940.83 / ₹153,710.43 at 0.00-point slippage for ₹10/₹15/₹20 brokerage cohorts, and ₹68,771.23 / ₹62,540.83 / ₹56,310.43 at 2.00-point slippage.

The original 59-trade primary-source result (₹52,827.50 gross P&L, 44.0% coverage) is preserved as provenance. The research does not treat 44.0% as the strategy's intrinsic trading frequency because 75 rejected cycles were reconstructed on an independent source.

## Frozen strategy

- First trading day after previous NIFTY weekly expiry.
- 09:15 IST market-open entry.
- ATM = nearest common listed strike to NIFTY spot open.
- Buy near ATM PE.
- Sell near ATM CE.
- Buy same-strike far ATM CE.
- Sell same-strike far ATM PE.
- Far expiry = three weekly intervals after near expiry.
- Exit all four legs at near-expiry trading-day close.
- One historical lot per leg.
- No adjustments, rolling, target, stop-loss or averaging.

## Final research files

- [Final manuscript](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/reports/nifty_calendar/MANUSCRIPT_NIFTY_4LEG_CALENDAR_2022_2024.md)
- [Final statistics](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/reports/nifty_calendar/FINAL_SECONDARY_STATISTICS_2022_2024.md)
- [P5 reconciliation report](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/reports/nifty_calendar/P5_RECONCILIATION_REPORT_2022_2024.md)
- [Secondary trade-level ledger](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/reports/nifty_calendar/SECONDARY_TRADE_LEVEL_RESULTS_2022_2024.csv)
- [Secondary cost sensitivity](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/reports/nifty_calendar/SECONDARY_COST_SENSITIVITY_2022_2024.csv)
- [Phase status](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/docs/nifty_calendar/PHASE_STATUS.md)
- [Error log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/docs/nifty_calendar/CONVERSATION_LOG.md)
- [Sources and literature](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/docs/nifty_calendar/SOURCES.md)
- [Cost assumptions](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/docs/nifty_calendar/COST_ASSUMPTIONS.md)

## Phase infrastructure

- [P5 reconciliation workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/.github/workflows/p5-nifty-reconciliation.yml)
- [P6 final manuscript workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/.github/workflows/p6-nifty-manuscript.yml)
- [Research plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p6-manuscript/docs/nifty_calendar/RESEARCH_PLAN.md)

## Interpretation

This is a historical descriptive study, not a forecast. Daily OHLC data does not establish synchronized live execution, bid/ask fills, queue priority or market impact. The study's future work is longer-history validation, strict out-of-sample testing, executable bid/ask replay, liquidity constraints and regime analysis without modifying the frozen result.
