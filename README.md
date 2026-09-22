# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

This repository is the research home for the frozen NIFTY four-leg weekly/three-week calendar strategy.

## Current research status — 2026-09-23

**Strategy is locked. Historical backtest is not yet numerically claimed.**

Active branch: `research-nifty-4leg-calendar-v1`

Key frozen rules:
- Entry: first trading day after the previous NIFTY weekly expiry.
- Entry timestamp: 09:15 IST market-open.
- Near expiry: first weekly expiry after entry.
- Far expiry: three weekly intervals after the near expiry.
- ATM: nearest listed strike to the 09:15 NIFTY spot open, carried across all four legs.
- Legs: buy near ATM PE; sell near ATM CE; buy far ATM CE; sell far ATM PE.
- Exit: all four legs at the near-expiry trading-day close.
- No adjustment, rolling, target or stop-loss.

## Research documents

- [Research plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/RESEARCH_PLAN.md)
- [Locked strategy](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/DATA_SPEC.md)
- [Sources](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/SOURCES.md)
- [Error log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/CONVERSATION_LOG.md)

## Research policy

Official NSE historical data is preferred and independent/open datasets are used for validation. Raw exchange-owned bulk archives are not committed unless redistribution is verified. Derived trade-level datasets, manifests, hashes, code and final research outputs are versioned.

The study must report gross P&L separately from slippage and transaction-cost-adjusted P&L, and it will not present unverified historical performance as a trading result.
