# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

This repository is the research home for the frozen NIFTY four-leg weekly/three-week calendar strategy specified in the project conversation.

## Current active research

- Strategy: NIFTY 4-leg weekly / 3-week calendar
- Status: Strategy rules locked for historical backtest
- Active research branch: `research/nifty-4leg-calendar-v1`
- Entry: first trading day after the previous NIFTY weekly expiry, using 09:15 IST session-open prices
- Exit: near weekly expiry trading-day close for all four legs
- Costs/slippage: modeled explicitly in the backtest; no net-performance claim is made until the data and execution assumptions are verified

See `docs/PROJECT_RULES.md` and the active research branch for the phase plan, logs, and outputs.

## Important

Historical option data must be sourced and documented. Official NSE data will be preferred. Bulk redistribution of exchange-owned raw data will not be assumed permissible; the repository will retain manifests, hashes, derived trade-level research data, and reproducible acquisition code rather than silently committing restricted raw archives.

