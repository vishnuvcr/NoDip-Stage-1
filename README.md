# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**Strategy locked. P0/P1 complete. P2/P3 active. Automated GitHub Actions execution is now enabled; the first runs exposed and logged CI setup/import defects before data could be used. No historical performance number is claimed yet.**

Active branch: `research-nifty-4leg-calendar-v1`

### Frozen strategy
- Entry: first trading day after the previous NIFTY weekly expiry.
- Entry: 09:15 IST market-open.
- ATM: nearest listed strike to the 09:15 NIFTY spot open.
- Buy near-weekly ATM PE.
- Sell near-weekly ATM CE.
- Buy the same-strike far-weekly ATM CE, with far expiry three weekly intervals after near expiry.
- Sell the same-strike far-weekly ATM PE.
- Exit every leg at the near-expiry trading-day close.
- One lot per leg using historical contract lot size.
- No adjustments, rolling, targets, stop-losses or averaging.

### Phase documents
- [Research plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/DATA_SPEC.md)
- [Sources and literature](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/SOURCES.md)
- [Error log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/CONVERSATION_LOG.md)
- [Project rules](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/PROJECT_RULES.md)
- [Manual backtest workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/.github/workflows/nifty-calendar-backtest.yml)

### Execution infrastructure
- [Main execution runner](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/execute-nifty-calendar.yml)
- [Draft execution PR #1](https://github.com/vishnuvcr/NoDip-Stage-1/pull/1)

The first historical execution source is the public `NSEIndexOptionsData` archive for 2022-2024. It contains NIFTY minute data and embedded NIFTY spot data. The preparation script converts 09:15 opens and expiry-session final closes into the frozen backtest schema.

Gross P&L, slippage sensitivity, brokerage and statutory-cost layers remain separate. No unverified historical performance is presented as a trading result.
