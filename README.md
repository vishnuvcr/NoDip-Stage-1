# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**Strategy locked. P0/P1 complete. P2/P3 active. The public 2022-2024 data source was validated and a ticker-schema defect that caused the initial zero-trade run has been corrected. A fresh full execution is being triggered.**

Active branch: `research-nifty-4leg-calendar-v1`

### Frozen strategy
- Entry: first trading day after the previous NIFTY weekly expiry.
- Entry: 09:15 IST market-open.
- ATM: nearest listed strike to the 09:15 NIFTY spot open.
- Buy near-weekly ATM PE.
- Sell near-weekly ATM CE.
- Buy the same-strike far-weekly ATM CE.
- Sell the same-strike far-weekly ATM PE.
- Far expiry: three weekly intervals after near expiry.
- Exit all four legs at the near-expiry trading-day close.
- One lot per leg using historical contract lot size.
- No adjustments, rolling, target, stop-loss or averaging.

### Latest data-integrity finding
The public NIFTY archive uses ticker symbols such as NIFTY04JAN24C18300 / NIFTY04JAN24P18300, with a single C/P. The original parser expected CE/PE, which caused a zero-trade result despite valid option data. A dedicated diagnostic workflow confirmed the source schema; the research branch now uses a vectorized single-letter parser and aborts if zero contracts are parsed.

### Research documents
- [Research plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/DATA_SPEC.md)
- [Sources and literature](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/SOURCES.md)
- [Error log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/CONVERSATION_LOG.md)
- [Project rules](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/PROJECT_RULES.md)

### Execution infrastructure
- [Manual backtest workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/.github/workflows/nifty-calendar-backtest.yml)
- [Main research runner](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/execute-nifty-calendar.yml)
- [Public ticker diagnostic](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/diagnose-public-tickers.yml)
- [Draft execution PR #1](https://github.com/vishnuvcr/NoDip-Stage-1/pull/1)

No gross or net performance figure is accepted until the corrected parser produces a validated trade ledger and the ledger passes source-quality checks.
