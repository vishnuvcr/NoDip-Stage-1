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
- primary public source was subjected to source-quality QC and rejected for P9 performance because far-expiry intraday coverage was too sparse;
- secondary Rissin/Upstox 1-minute option data were used on the same 86-cycle post-2024 OOS population;
- signal on completed 1-minute close;
- next available minute open execution;
- positive four-leg volume/price requirement;
- explicit adverse slippage and transaction-cost sensitivity.

Final P9 result:
- fixed 09:15 secondary-source control: 26 trades, gross ₹40,506.25, win rate 80.77%, PF 5.029, gross max DD ₹7,489.50;
- event-driven arm: 70 trades, gross ₹37,291.40, win rate 62.86%, PF 1.576, gross max DD ₹26,467.50;
- event-only incremental trades: 44, gross ₹-3,214.85, win rate 52.27%, PF 0.941;
- 24 originally gate-fail dates that only qualified later: gross ₹-13,964.60, PF 0.665;
- event-driven modeled net P&L at 0.05% exchange stress: ₹9,222.87 / ₹-10,837.13 / ₹-30,897.13 / ₹-71,017.13 for 0 / 0.5 / 1 / 2 points adverse slippage;
- therefore the event-driven timing adaptation is not promoted.

Primary-source QC:
The thetrademarkk source acquired 192/201 requested expiry files, but the far expiry on 2026-04-01 contained only 903 rows for the day. The only four-leg common strike at sampled qualifying timestamps was 20,500 while NIFTY was around 22,900. The primary timing output was rejected before performance interpretation.

P9 conclusion:
Adaptive first-qualifying intraday entry does not improve the frozen strategy under the secondary OOS test and is highly cost/slippage sensitive. Keep the fixed-time reference frozen.

P9 outputs:
- reports/nifty_calendar/P9_FINAL_RESEARCH_CONCLUSION.md
- reports/nifty_calendar/P9_SECONDARY_VALIDATION_REPORT.md
- reports/nifty_calendar/P9_RISSIN_OOS_COMPARISON.csv
- reports/nifty_calendar/P9_RISSIN_OOS_COSTS.csv
- docs/nifty_calendar/P9_ALTERNATE_DATA_SOURCE_AUDIT.md

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