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
Status: COMPLETE for the 2022-2024 validation sample.
Completed: exact leg-specific slippage sensitivity; historical Paytm brokerage-cohort scenarios; documented brokerage/statutory costs; exchange-charge sensitivity; full cycle-coverage audit; independent public mirror of NSE F&O bhavcopy reconciliation for all 134 candidate cycles; Yahoo NIFTY 50 OPEN cross-check; full secondary trade-level ledger and cost sensitivity.
Residual limitation: 2 of 134 candidate cycles are not constructible on the independent mirror because no common strike is present there, while the primary source treated them as valid. This is retained as a source-discrepancy limitation, not silently resolved. For the secondary re-run, the frozen ATM/common-strike rule is re-applied using the independent Yahoo NIFTY OPEN diagnostic; 27 primary rejects reproduce the primary strike and 48 require independent secondary-source strike re-selection.

No exact historical Paytm client-specific exchange pass-through was available from public pricing data, so the study retains explicit exchange-charge sensitivities rather than inventing a contract-note rate.

### P6 — Final manuscript
Status: COMPLETE.
The manuscript is finalized from the strict 84-cycle frozen-protocol independent validation sample, with the 59-cycle primary-source result retained as a source-coverage comparison and the 28 source-specific re-selection cycles retained only as sensitivity evidence. It includes tables, charts, trade-level appendix, methods, statistical inference, limitations and supplementary material.

## Current statistical outputs

Primary 2022-2024 source result:
- 59 valid trades
- Gross P&L ₹52,827.50
- Win rate 64.41%
- Profit factor 2.549
- Max drawdown ₹5,650

Strict independent validation result:
- 84 strict frozen-protocol cycles of 134 candidates (62.7% coverage)
- Gross P&L ₹83,030.00
- Mean cycle ₹988.45
- Median cycle ₹598.75
- Win rate 61.90%
- Profit factor 2.942
- Max drawdown ₹8,022.50
- Best trade ₹18,742.50
- Worst trade ₹-5,363.75
- 3-trade circular-block bootstrap 95% interval for total P&L: ₹31,147 to ₹139,294

Coverage interpretation:
- 57 of 59 primary-valid cycles were independently executable;
- 27 primary rejects were recovered at the same primary-selected strike;
- 28 primary rejects were executable only after source-specific secondary strike re-selection and are not counted in the strict estimate;
- 20 primary rejects remained non-executable on the independent source;
- 2 primary-valid cycles were not independently reproduced.

## Execution-cost analysis

The robustness report models:
- ₹80/₹120/₹160 brokerage per strategy cycle under the documented ₹10/₹15/₹20 historical Paytm Money client-cohort scenarios (8 executed option orders)
- 0.0625% historical STT on option sales through the sample window
- 0.003% buy-side stamp duty
- 0.0001% SEBI fee
- 18% GST on applicable broker/regulatory/exchange charges
- exchange-charge sensitivity rather than an invented Paytm-specific historical pass-through rate
- exact per-leg slippage at 0.25, 0.50, 1.00 and 2.00 index points per execution

## Stop condition

Research stops after P6 or earlier if data quality cannot support a defensible conclusion. A result that fails validation is recorded as a research outcome, not silently repaired.


### P7 — Loss audit / entry tuning
Status: IN PROGRESS.
Audit every losing trade in the strict 84-cycle sample, classify leg-level loss mechanisms, derive interpretable entry-time term-structure features, and propose one candidate entry gate without altering P6. The candidate must be reserved for independent post-2024 validation because repeated historical parameter search can create backtest overfitting.
