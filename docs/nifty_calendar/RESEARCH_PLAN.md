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
Status: IN PROGRESS / DATA-BLOCKED.

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

Primary signal rule:
- scan forward through the trading session;
- select the current ATM strike from timestamped NIFTY spot;
- require all four contracts at that strike;
- require executable contemporaneous quotes;
- enter exactly once at the first qualifying timestamp;
- skip the day if no qualifying timestamp occurs.

No-lookahead rule:
- tick/quote data: signal and fill use contemporaneous executable prices;
- 1-minute OHLC-only data: signal on minute close and execute at the next available minute price, with slippage;
- daily data cannot test P9.

Comparison arms:
1. P8 fixed-time CBR<=1.20 reference;
2. P9 first-qualifying event-driven entry;
3. skipped day when the event never occurs.

Pre-specified latest-entry sensitivity:
- 15:00, 15:15, 15:30 and full 15:40 derivatives session where data quality permits.
These are operational cutoffs, not parameters to select after seeing results.

Required data:
- timestamped NIFTY spot;
- timestamped NIFTY options covering at least near and far weekly expiries on common strikes;
- price, expiry, strike, CE/PE, volume and OI;
- preferred bid/ask and quote size;
- tick/1-second preferred, 1-minute acceptable secondary.

Current blocker:
The repository contains daily option data but no validated intraday multi-expiry quote dataset adequate for P9. No numerical P9 performance result is claimed until that data exists.

P9 work packages:
1. data-source audit and coverage validation;
2. deterministic event detector;
3. executable four-leg fill model;
4. paired fixed-vs-event-driven historical comparison;
5. residual loss-mechanism analysis;
6. unseen temporal holdout.

Primary statistics:
- paired trade-date comparison;
- bootstrap confidence intervals for cumulative and mean P&L;
- win rate, profit factor, drawdown and tail losses;
- entry-time distribution;
- cost/slippage sensitivity;
- regime and year breakdown;
- non-parametric paired tests where appropriate.

P9 stop condition:
Stop without promotion if contemporaneous four-leg execution cannot be reconstructed or if the apparent effect disappears under executable cost/slippage assumptions.

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