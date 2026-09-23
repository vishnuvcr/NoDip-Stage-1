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
Status: IN PROGRESS.
The manuscript is now being produced from the 132-cycle independently reconciled secondary ledger, with the 59-cycle primary-source result retained as a source-coverage comparison. It will include tables, charts, trade-level appendix, methods, statistical inference, limitations and supplementary material.

## Current statistical outputs

Primary 2022-2024 source result:
- 59 valid trades
- Gross P&L ₹52,827.50
- Win rate 64.41%
- Profit factor 2.549
- Max drawdown ₹5,650

Independent secondary validation result:
- 132 complete cycles of 134 candidates (98.5% coverage)
- Gross P&L ₹188,237.50
- Mean cycle ₹1,426.04
- Median cycle ₹580.63
- Win rate 59.09%
- Profit factor 1.889
- Max drawdown ₹57,380.00
- Best trade ₹62,080.00
- Worst trade ₹-31,597.50
- 3-trade circular-block bootstrap 95% interval for total P&L: approximately ₹6,927 to ₹408,770

Coverage interpretation:
- all 75 primary-source rejected cycles were reconstructed on the independent public NSE-bhavcopy mirror;
- 57 of 59 primary-valid cycles were also complete on the independent mirror;
- 27 of the 75 recovered rejects used the same strike as the primary source, while 48 required re-selection of the common ATM strike under the independent source's listed-strike grid;
- 2 primary-valid cycles were not constructible on the independent mirror because that source contained no common strike.

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
