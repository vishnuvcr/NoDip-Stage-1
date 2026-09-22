# Research Plan — NIFTY 4-Leg Calendar

## Research question

Does the frozen four-leg structure produce a persistent positive expected return on NIFTY after realistic transaction costs and execution slippage when entered at the first trading session after weekly expiry and exited at the following weekly expiry?

## Aims

- Establish a reproducible historical backtest.
- Separate gross option-payoff behaviour from executable net returns.
- Quantify drawdowns, tail losses, capital use and sensitivity to slippage/costs.
- Detect data or contract-definition failures before interpreting performance.

## Phases

### P0 — Specification freeze
Status: COMPLETE.
Freeze entry, expiry selection, ATM rule, four legs, exit and no-adjustment rule.

### P1 — Literature / market-structure review
Status: IN PROGRESS.
Review NIFTY weekly-option market design, expiry changes, strike scheme, settlement, liquidity/execution literature and existing public implementations. Record sources in docs/nifty_calendar/SOURCES.md.

### P2 — Data acquisition and validation
Status: PENDING.
Acquire daily NIFTY option/futures/spot data from official NSE archives where possible. Cross-check selected fields against independent/open data sources. Build a reproducible manifest with date, contract, source, hash and validation state.

Minimum fields:
date, symbol, expiry, strike, option type, open, high, low, close, volume, open interest, underlying/futures fields, lot size where available.

### P3 — Mechanical engine and unit tests
Status: PENDING.
Implement expiry-calendar mapping, nearest-available-strike selection, four-leg construction, P&L, missing-data handling and cost model. Add deterministic tests using hand-checked examples.

### P4 — Historical backtest
Status: PENDING.
Run the frozen rule over the maximum common high-quality history supported by all four legs. No parameter tuning on the same sample.

### P5 — Verification / robustness
Status: PENDING.
Re-run using independent data where possible; test cost/slippage sensitivity; audit missing contracts, holiday expiry shifts, strike availability and lot-size changes; perform block-bootstrap confidence intervals and year/market-regime decomposition.

### P6 — Final manuscript
Status: PENDING.
Produce complete structured research report with methodology, results, statistical inference, figures, tables, limitations, conclusion and future research.

## Statistical analysis

Primary:
- total and annualized return on defined capital
- win rate, average trade, median trade, profit factor
- max drawdown and drawdown duration
- return volatility
- downside deviation / Sortino-style measure
- exposure time and capital utilization
- bootstrap confidence intervals for mean trade and cumulative P&L

Robustness:
- adverse slippage grid
- fee/cost sensitivity
- yearly and regime splits
- independent-source spot/contract validation
- missing-data stress test
- circular moving-block bootstrap to preserve serial dependence

No ranking against unrelated strategies is planned in this phase.

## Stop condition

The phase ends after P6 or earlier if data quality cannot support a defensible result. A failed hypothesis is a valid research outcome.
