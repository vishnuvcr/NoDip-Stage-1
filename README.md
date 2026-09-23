# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P7 complete for the 2022-2024 frozen-strategy study; final result uses the strict independently reconciled 84-cycle sample, followed by a loss-trade audit.**

The study froze a four-leg NIFTY calendar structure before interpretation and then validated its historical data coverage with an independent public mirror of NSE F&O bhavcopy archives plus an independent NIFTY spot-open diagnostic.

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

The original 59-trade primary-source result (₹52,827.50 gross P&L, 44.0% coverage) is preserved as provenance. The 28 source-specific strike-reselection cycles are reported as sensitivity evidence, not merged into the strict frozen-protocol result. Zero-open/non-traded option rows were excluded from executable fills.


### P7 loss-trades audit

The 84-trade strict baseline contains **32 losing trades**. The loss audit found that near-expiry legs account for the dominant loss contribution, with a recurring bullish-like front-week adverse payoff signature accounting for 72.1% of absolute losing-trade P&L. Exploratory entry-state filters reduce drawdown in-sample but are not validated strategy changes.

- [Loss audit report](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/LOSS_AUDIT_REPORT_2022_2024.md)
- [Loss-trade ledger](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/LOSS_TRADE_AUDIT_2022_2024.csv)
- [Filter sensitivity](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/LOSS_FILTER_SENSITIVITY_2022_2024.csv)
- [Cost-aware filter sensitivity](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/reports/nifty_calendar/LOSS_FILTER_COST_SENSITIVITY_2022_2024.csv)
- [P7 audit plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p7-loss-audit/docs/nifty_calendar/P7_LOSS_AUDIT_PLAN.md)

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
