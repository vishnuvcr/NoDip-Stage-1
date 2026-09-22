# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**Strategy locked. P0/P1/P2/P3 complete. P4 historical backtest is active. The latest run reached the strategy engine and exposed a pandas 3.x lot-size dtype bug; that bug is fixed and regression-tested. A fresh cached-data execution is now being triggered.**

Active branch: `research-nifty-4leg-calendar-v1`

### Frozen strategy
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

### Latest correction
The backtest failed only after data preparation because pandas 3.x rejected an empty DatetimeArray assignment into the integer lot-size column when there were no missing lot sizes. The engine now uses nullable Int64 storage and only applies the fallback assignment when missing lot sizes actually exist. Regression tests cover both cases.

### Research documents
- [Research plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/DATA_SPEC.md)
- [Sources and literature](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/SOURCES.md)
- [Error log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/CONVERSATION_LOG.md)
- [Project rules](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/PROJECT_RULES.md)

### Execution
- [Main research runner](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/execute-nifty-calendar.yml)
- [Manual backtest workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/.github/workflows/nifty-calendar-backtest.yml)
- [Public ticker diagnostic](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/diagnose-public-tickers.yml)
- [Draft execution PR #1](https://github.com/vishnuvcr/NoDip-Stage-1/pull/1)

No performance figure is accepted until the corrected engine produces and validates the trade ledger. Gross, slippage-adjusted and transaction-cost-adjusted results will be separated.
