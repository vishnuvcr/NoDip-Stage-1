# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Status — 2026-09-23

**P0 specification freeze is complete. P1 market-structure/data-source review has started. No historical performance number is claimed yet.**

Active branch: `research-nifty-4leg-calendar-v1`

### Frozen strategy
- Enter on the first trading day after the previous NIFTY weekly expiry.
- Use the 09:15 IST market-open.
- Select the nearest listed NIFTY strike to the 09:15 spot open.
- Buy near-weekly ATM PE and sell near-weekly ATM CE.
- Buy the same-strike far-weekly ATM CE and sell the same-strike far-weekly ATM PE, with the far expiry exactly three weekly intervals after the near expiry.
- Exit all four legs at the near-expiry trading-day close.
- One lot per leg; no adjustment, rolling, stop, target or averaging.

### Research documents
- [Research plan](docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](docs/nifty_calendar/DATA_SPEC.md)
- [Sources](docs/nifty_calendar/SOURCES.md)
- [Error log](docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](docs/nifty_calendar/CONVERSATION_LOG.md)
- [Project rules](docs/PROJECT_RULES.md)

Historical data, slippage and Paytm Money transaction-cost assumptions will be documented before any net-performance conclusion.
