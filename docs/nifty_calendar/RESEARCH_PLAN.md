# Research Plan — NIFTY 4-Leg Calendar

## Research question

Does the frozen four-leg structure produce a persistent positive expected return on NIFTY after realistic transaction costs and execution slippage when entered at the first trading session after weekly expiry and exited at the following weekly expiry?

## Aims

- Establish a reproducible historical backtest.
- Separate gross option-payoff behaviour from executable net returns.
- Quantify drawdowns, tail losses, capital use and sensitivity to execution costs.
- Detect data or contract-definition failures before interpreting performance.

## Phases

### P0 — Specification freeze
Status: COMPLETE.
Freeze entry, expiry selection, ATM rule, four legs, exit and no-adjustment rule.

### P1 — Literature / market structure
Status: COMPLETE.
Review NIFTY weekly-option market design, expiry changes, strike scheme, settlement, liquidity/execution literature, transaction-cost rules and public implementations.

### P2 — Data acquisition and validation
Status: COMPLETE for the 2022-2024 public-source dataset.
The source was downloaded/cached, its ticker schema was diagnosed, C/P was mapped to CE/PE, and the normalized trade-input data was produced.

### P3 — Mechanical engine and tests
Status: COMPLETE.
Expiry mapping, four-leg construction, historical lot-size handling, P&L and regression tests are implemented.

### P4 — Historical backtest
Status: COMPLETE for the 2022-2024 public-source subset.
The frozen strategy produced 59 valid executable cycles and gross P&L of ₹52,827.50.

### P5 — Verification / robustness
Status: IN PROGRESS.
Completed: exact leg-specific slippage sensitivity, documented brokerage/statutory cost model, exchange-charge sensitivity, drawdown/win-rate sensitivity and cycle-coverage audit.

Remaining:
- independently reconcile rejected cycles against a second historical option source;
- independently spot-check contract prices and 09:15 spot opens;
- reconstruct exact historical Paytm Money exchange-charge pass-through if contract-note-level data becomes available.

### P6 — Final manuscript
Status: PENDING.
The manuscript will be produced after P5 closes, with tables, charts, trade-level appendix, methods, statistical inference, limitations and supplementary material.

## Current statistical outputs

Primary 2022-2024 subset:
- 59 valid trades
- Gross P&L ₹52,827.50
- Win rate 64.41%
- Profit factor 2.549
- Max drawdown ₹5,650
- 3-trade circular-block bootstrap 95% interval for total P&L: ₹13,151.84 to ₹100,043.59

Coverage:
- 134 possible strategy cycles in the available expiry range
- 59 valid = 44.0% executable coverage
- 75 rejected: 9 no common strike, 62 missing entry leg, 4 missing exit leg

## Execution-cost analysis

The robustness report models:
- ₹80 brokerage per strategy cycle (8 executed option orders at ₹10/order)
- 0.0625% historical STT on option sales through the sample window
- 0.003% buy-side stamp duty
- 0.0001% SEBI fee
- 18% GST on applicable broker/regulatory/exchange charges
- exchange-charge sensitivity rather than an invented Paytm-specific historical pass-through rate
- exact per-leg slippage at 0.25, 0.50, 1.00 and 2.00 index points per execution

## Stop condition

Research stops after P6 or earlier if data quality cannot support a defensible conclusion. A result that fails validation is recorded as a research outcome, not silently repaired.
