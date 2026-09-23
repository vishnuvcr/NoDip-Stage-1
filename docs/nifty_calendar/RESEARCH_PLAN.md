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

### P10 — Entry-day offset research
Status: COMPLETE — NOT PROMOTED.

Research question:
> Keeping the 09:15 IST entry, CBR<=1.20 gate, four-leg structure and near-expiry exit fixed, does changing the trading session relative to the previous expiry improve robustness?

Pre-registered offsets:
- D-1: session immediately before previous expiry.
- D0: previous-expiry session.
- D+1: first session after previous expiry.
- D+2, D+3, D+4, D+5: subsequent sessions.

Interpretation:
- Offsets are trading-session offsets, not calendar-day offsets.
- If an offset falls after the near expiry, the cycle is marked AFTER_NEAR_EXPIRY and is not executed.
- All seven offsets are evaluated; no OOS-driven selection is allowed.

Design:
- Development sample: 2022-2024.
- Unseen OOS: 2025 onward.
- Entry: 09:15 IST daily open.
- Frozen gate: CBR<=1.20.
- Same common ATM strike across near/far CE/PE.
- Exit: near-expiry close.
- Historical lot sizes preserved.
- Brokerage/statutory charges, 0.05% exchange stress and 0/0.5/1/2 point adverse slippage included.

Selection:
- The seven offsets were treated as a pre-registered timing screen.
- OOS was not used to choose a winner.
- OOS paired bootstrap versus D+1: D-1 mean ₹-104.37 (95% CI ₹-1,403.35 to ₹1,114.14); D0 +₹383.69 (−₹797.17 to +₹1,480.94); D+2 +₹330.85 (−₹445.32 to +₹1,099.05); D+3 −₹562.94 (−₹1,480.49 to +₹308.59); D+4 −₹219.25 (−₹1,179.47 to +₹716.87); D+5 −₹940.37 (−₹1,975.86 to −₹69.96).
- D0 and D+2 therefore remain development-only candidates, not validated replacements for D+1.


Outputs:
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_LEDGER.csv
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_SUMMARY.csv
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_PAIRED.csv
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_REPORT.md
- reports/nifty_calendar/P10_OOS_PAIRED_BOOTSTRAP.md
- reports/nifty_calendar/P10_FINAL_RESEARCH_CONCLUSION.md

### P11 — Forward / paper-execution validation
Status: COMPLETE / BLOCKED BY DATA AVAILABILITY.
The pinned public option source ended before the fresh cutoff; no fresh post-P10 cycle was available. No P10 observations were reused.

### P12 — Far-expiry selection research
Status: COMPLETE — EXPLORATORY.
Tested F+1, F+2, F+3 and F+4 far expiries using the new four-leg orientation and a frozen entry-only normalized-credit selector.

### P13 — Fresh far-expiry validation on pinned public source
Status: COMPLETE — INSUFFICIENT FRESH SAMPLE.
The public source still ended at 2026-06-29, so zero post-2026-08-26 cycles were available.

### P14 — Official NSE fresh far-expiry validation
Status: COMPLETE — FRESH SAMPLE TOO SMALL.
The frozen P12 selector was evaluated on three completed post-cutoff cycles from official NSE daily F&O bhavcopy data. No score, horizon or threshold was retuned. The correct status is prospective paper monitoring, not live approval.

### P12 — Far-expiry selection extension
Status: COMPLETE — EXPLORATORY, NOT PROMOTED.

Research question:
> For the frozen near-expiry structure, does selecting the far expiry from F+1/F+2/F+3/F+4 using only 09:15 entry information improve net outcomes?

Frozen primary selector:
`(near CE - near PE + far PE - far CE) / NIFTY spot open`

Select the highest score among candidates with the same ATM strike and positive four-leg entry price/volume. Tie-break to the shorter horizon.

2025+ evaluation result was exploratory because the period had already been exposed in P10:
- F+1: 72 trades; gross ₹29,542.50; PF 1.321; net @2pt ₹-76,675.51.
- F+2: 73 trades; gross ₹-23,165.50; PF 0.836; net @2pt ₹-132,050.98.
- F+3: 64 trades; gross ₹33,141.75; PF 1.288; net @2pt ₹-62,956.75.
- F+4: 42 trades; gross ₹90,236.75; PF 2.373; net @2pt ₹26,958.30.
- Adaptive: 77 trades; gross ₹144,277.50; PF 2.763; net @2pt ₹30,311.14.

### P13 — Fresh far-expiry validation
Status: COMPLETE — DATA SOURCE BLOCKED.

The pinned Hugging Face daily source available to the runner ended at 2026-06-29, before the frozen P10/P12 cutoff of 2026-08-26. No fresh cycle was evaluated and no old OOS observation was reused.

### P14 — Official NSE fresh far-expiry validation
Status: COMPLETE — PAPER MONITORING ONLY.

To remove the P13 source-age problem, P14 downloaded official NSE F&O UDiFF bhavcopy archives for the three completed post-cutoff weekly cycles available by 2026-09-22.

Fresh cycles:
- 2026-09-02 entry → 2026-09-08 near expiry.
- 2026-09-09 entry → 2026-09-15 near expiry.
- 2026-09-16 entry → 2026-09-22 near expiry.

P14 froze the P12 adaptive rule without modification. It selected F+1 on all 3 fresh cycles.

Fresh adaptive result:
- 3 trades.
- Gross P&L ₹6,714.50.
- Net P&L at 0/0.5/1/2 adverse-slippage points: ₹6,096.46 / ₹5,316.46 / ₹4,536.46 / ₹2,976.46.
- No gross losing trade in the three-cycle sample.
- Because n=3, no statistical significance or population-level robustness claim is permitted.

Outputs:
- reports/nifty_calendar/P14_NSE_SOURCE_MANIFEST.csv
- reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_LEDGER.csv
- reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_SUMMARY.csv
- reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_COSTS.csv
- reports/nifty_calendar/P14_ADAPTIVE_SELECTION.csv
- reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_REPORT.md
- reports/nifty_calendar/P14_FINAL_RESEARCH_CONCLUSION.md

### Final research stop condition
Status: CLOSED FOR RETROSPECTIVE PARAMETER SEARCH.

No further far-expiry horizon, score weight, CBR threshold or entry-time parameter search is performed on the current sample. The next research action is prospective paper monitoring with the frozen P12 selector as new weekly cycles complete.
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

P0-P14 are closed. The current research stops after official-NSE fresh validation. No further far-expiry horizons, selector weights or parameter searches are performed on the existing sample. Future work is prospective paper monitoring and re-validation only when additional completed post-cutoff cycles become available. Failed validation is recorded as a scientific outcome, not silently repaired.