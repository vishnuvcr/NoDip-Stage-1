# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**Strategy locked. P0/P1 complete. P2/P3 active. Public 2022-2024 data schema is now understood end-to-end: source C/P tickers are normalized to the frozen engine's CE/PE labels, and parser regression tests pass. A fresh full backtest run is being triggered.**

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
- Exit all legs at near-expiry trading-day close.
- One historical lot per leg.
- No adjustments, rolling, target, stop-loss or averaging.

### Data integrity
The public NIFTY mirror uses tickers such as NIFTY04JAN24C18300 / NIFTY04JAN24P18300. The source schema defect and the subsequent C/P-to-CE/PE normalization defect have both been logged and regression-tested. The historical engine will not accept a result until the corrected pipeline yields a populated trade ledger and passes source-quality checks.

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

No performance figure is accepted yet. Gross, slippage-adjusted and transaction-cost-adjusted results will be reported separately.
