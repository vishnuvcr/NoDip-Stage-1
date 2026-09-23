# Research Plan — NIFTY 4-Leg Calendar

## Core research question

Does the frozen four-leg structure produce a persistent positive expected return on NIFTY after realistic transaction costs and execution slippage when entered on the first eligible trading day after weekly expiry and exited at the following weekly expiry?

## Current extension question

Can the frozen P7/P8 calendar-balance gate (CBR <= 1.20) be converted from a fixed-time entry into an event-driven entry, where the strategy enters at the first intraday timestamp on the eligible day when all other frozen criteria are simultaneously satisfied?

## Aims

- Establish a reproducible historical backtest.
- Separate gross option-payoff behaviour from executable net returns.
- Quantify drawdowns, tail losses, capital use and sensitivity to execution costs.
- Detect data or contract-definition failures before interpreting performance.
- Test whether adaptive entry timing adds robustness without re-optimizing the gate.

## Phases

### P0 — Specification freeze
Status: COMPLETE.

### P1 — Literature / market structure
Status: COMPLETE.

### P2 — Data acquisition and validation
Status: COMPLETE for the 2022-2024 public-source daily dataset.

### P3 — Mechanical engine and tests
Status: COMPLETE.

### P4 — Historical backtest
Status: COMPLETE for the 2022-2024 public-source subset.

### P5 — Verification / robustness
Status: COMPLETE.

### P6 — Final manuscript
Status: COMPLETE.

### P7 — Loss audit / entry tuning
Status: COMPLETE.
The only retained candidate gate is:

(far CE / near CE) / (far PE / near PE) <= 1.20

It remains unchanged.

### P8 — Unseen post-2024 validation
Status: COMPLETE.
The 1.20 gate passed one genuine temporal holdout and is supported for further research, but not approved for live capital.

### P9 — Event-driven intraday entry timing
Status: COMPLETE — NOT PROMOTED.

Research question:
> On each eligible trading day, can the strategy enter at the first timestamp at which CBR <= 1.20 and all four near/far legs are simultaneously executable, instead of using a fixed opening timestamp?

Frozen:
- eligible day;
- four-leg structure;
- CBR threshold 1.20;
- same-strike rule;
- near-expiry close exit;
- one lot per leg;
- no stop/target/roll/averaging/adjustment.

Execution:
- primary public source failed ATM/far-expiry source-quality QC and was rejected;
- secondary Rissin/Upstox 1-minute options were tested on the same 86-cycle post-2024 OOS population;
- signal on completed 1-minute close;
- next available minute open execution;
- positive four-leg volume/price requirement;
- deterministic ATM QC: common strike within 25 points of contemporaneous spot.

Final P9 result:
- fixed source diagnostic: 14 executable trades, gross ₹19,737.25, win rate 78.57%, PF 5.613;
- event-driven: 65 executable trades, gross ₹43,607.25, win rate 64.62%, PF 1.755, gross max DD ₹33,429;
- event-driven modeled net at 0.05% exchange stress: ₹17,798.70 / ₹-781.30 / ₹-19,361.30 / ₹-56,521.30 for 0 / 0.5 / 1 / 2 points adverse slippage;
- on 33 event dates that passed the canonical 09:15 P8 gate, event gross was ₹42,312.50 versus canonical P8 fixed-gate ₹104,231.75; mean paired difference ₹-1,876.34, median ₹-746.25, bootstrap 95% CI approximately ₹-3,990.63 to ₹-347.55;
- 32 dates failed the 09:15 gate but qualified later; those event trades produced gross ₹1,294.75 and PF 1.029;
- pre-registered cutoffs 15:00/15:15/15:30/15:40 all remained negative at 0.5-point adverse slippage and beyond.

P9 conclusion:
Adaptive first-qualifying intraday entry does not support replacing the fixed 09:15 entry. The threshold, four-leg structure and exit remain frozen.

P9 outputs:
- reports/nifty_calendar/P9_FINAL_RESEARCH_CONCLUSION.md
- reports/nifty_calendar/P9_SECONDARY_VALIDATION_REPORT.md
- reports/nifty_calendar/P9_RISSIN_OOS_COMPARISON.csv
- reports/nifty_calendar/P9_RISSIN_OOS_COSTS.csv
- reports/nifty_calendar/P9_RISSIN_CUTOFF_SENSITIVITY.csv
- reports/nifty_calendar/P9_RISSIN_CUTOFF_SENSITIVITY_REPORT.md

### P10 — Forward / paper-execution validation
Status: PLANNED.
If P9 produces a defensible specification, keep the exact rule frozen and record timestamped live/paper observations, actual quotes, fills, costs, slippage and residual loss mechanisms without retuning on the same observation stream.

## Current statistical outputs from P8

- 86 executable post-2024 cycles
- 42 fixed-gate trades
- Fixed-gate gross P&L ₹126,460.50
- Win rate 76.19%
- Profit factor 5.115
- Gross max drawdown ₹13,406.25
- Worst trade ₹-12,502.75
- At 2-point adverse slippage and 0.05% exchange-charge stress: modeled net P&L ₹64,304.41

## Execution-cost policy

Historical and forward analyses must keep brokerage, statutory charges, exchange-charge sensitivity and adverse slippage explicit. Modeled costs are not claims of realized Paytm Money fills.

## Research stop condition

Research stops after the defined phases P9/P10, or earlier if data quality cannot support a defensible conclusion. Failed validation is recorded as a scientific outcome, not silently repaired.