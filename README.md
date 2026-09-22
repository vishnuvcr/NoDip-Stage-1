# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**Strategy locked. P0-P4 complete. P5 robustness is active.**

The frozen 2022-2024 backtest completed successfully:

- 59 valid executable strategy cycles
- Gross P&L: ₹52,827.50
- Win rate: 64.41%
- Profit factor: 2.549
- Maximum drawdown: ₹5,650
- 44.0% executable-cycle coverage (59 of 134 candidate cycles)

The result is therefore a **conditional subset result**, not yet a complete estimate of the whole 2022-2024 population. The principal issue is data availability: 75 candidate cycles were rejected because of missing/common-strike/exit-leg data.

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

## Robustness already completed
Leg-specific slippage sensitivity at 0.25, 0.50, 1.00 and 2.00 points per execution is calculated. Brokerage and documented statutory charges are modeled, and exchange-charge sensitivity is shown without inventing a historical Paytm-specific pass-through rate.

At a 0.50-point adverse-slippage assumption and a 0.05% exchange-charge sensitivity, the 59-trade subset remains at approximately ₹32,619 net before any additional unmodeled charges.

## Research documents
- [Research plan](docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](docs/nifty_calendar/PHASE_STATUS.md)
- [Data specification](docs/nifty_calendar/DATA_SPEC.md)
- [Sources and literature](docs/nifty_calendar/SOURCES.md)
- [Cost assumptions](docs/nifty_calendar/COST_ASSUMPTIONS.md)
- [Robustness report](reports/nifty_calendar/ROBUSTNESS_2022_2024.md)
- [Backtest report](reports/nifty_calendar/RESULTS_2022_2024.md)
- [Error log](docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](docs/nifty_calendar/CONVERSATION_LOG.md)
- [Project rules](docs/PROJECT_RULES.md)

## Execution
- [Main research runner](.github/workflows/execute-nifty-calendar.yml)
- [Manual backtest workflow](.github/workflows/nifty-calendar-backtest.yml)
- [Public ticker diagnostic](.github/workflows/diagnose-public-tickers.yml)

P5 remains open until the rejected cycles are independently reconciled and the historical cost treatment is further validated.
