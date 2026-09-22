# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Status — 2026-09-23

**P0 specification freeze and P1 market-structure review are complete. P2 data acquisition and P3 backtest-engine implementation are underway. No numerical backtest result is claimed yet.**

Active branch: `research-nifty-4leg-calendar-v1`

### Frozen strategy
- Enter on the first trading day after the previous NIFTY weekly expiry.
- Use the 09:15 IST market-open.
- Select the nearest listed NIFTY strike to the 09:15 spot open.
- Buy near-weekly ATM PE and sell near-weekly ATM CE.
- Buy the same-strike far-weekly ATM CE and sell the same-strike far-weekly ATM PE.
- Far expiry is exactly three weekly intervals after the near expiry.
- Exit all four legs at the near-expiry trading-day close.
- One lot per leg using each contract's historically applicable lot size.
- No adjustment, rolling, stop, target or averaging.

### Research documents
- [Research plan](docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](docs/nifty_calendar/DATA_SPEC.md)
- [Sources](docs/nifty_calendar/SOURCES.md)
- [Error log](docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](docs/nifty_calendar/CONVERSATION_LOG.md)
- [Project rules](docs/PROJECT_RULES.md)
- [Manual backtest workflow](.github/workflows/nifty-calendar-backtest.yml)

### Execution model
The workflow uses reproducible NSE daily derivatives acquisition, independent NIFTY spot data for the ATM reference, deterministic four-leg P&L calculation, and GitHub Actions artifacts for normalized data. Gross P&L is kept separate from slippage and Paytm Money transaction costs.
