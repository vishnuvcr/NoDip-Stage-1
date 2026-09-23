# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P8 complete. P9 event-driven entry timing is now open as a separate research phase and is currently data-blocked.**

## Frozen validated reference

P8 validated the fixed calendar-balance gate on the post-2024 temporal holdout:

(far CE / near CE) / (far PE / near PE) <= 1.20

P8 conclusion: supported for further research, not promoted to live trading.

- P8 plan: docs/nifty_calendar/P8_OOS_VALIDATION_PLAN.md
- P8 candidate lock: docs/nifty_calendar/P8_OOS_CANDIDATE_LOCK.md
- P8 report: reports/nifty_calendar/P8_OOS_VALIDATION_REPORT_2025_ONWARD.md
- P8 conclusion: reports/nifty_calendar/P8_FINAL_RESEARCH_CONCLUSION.md

## P9 — Event-driven intraday entry timing

User question:

> Can the strategy enter when all other criteria are met during the trading day, rather than using a fixed clock time?

Research rule:

Enter exactly once at the first intraday timestamp on the first eligible trading day when:
1. CBR <= 1.20;
2. a valid current common ATM strike exists;
3. near CE/PE and far CE/PE are all available and executable at that timestamp.

The four-leg structure, 1.20 gate and near-expiry close exit remain frozen.

P9 is not a threshold-optimization phase. It tests timing only.

### Data requirement

The existing daily OPEN/CLOSE archive cannot determine an intraday trigger time or reliable contemporaneous four-leg fills. P9 therefore requires timestamped NIFTY spot plus multi-expiry option data, preferably with bid/ask and quote size.

NSE states that normal equity-derivatives trading runs from 09:15 to 15:40 IST and provides historical order/trade data as a separate historical-data service. These are candidate sources for an auditable intraday dataset.

Public research projects also show that 1-minute NIFTY option datasets can exist, but coverage and contract fidelity must be independently validated before research use.

### P9 files

- docs/nifty_calendar/P9_ENTRY_TIMING_PLAN.md
- docs/nifty_calendar/P9_TRIGGER.md
- .github/workflows/p9-entry-timing.yml
- docs/nifty_calendar/PHASE_STATUS.md

### P10 planned

After P9, the next planned phase is fixed-rule forward/paper-execution validation using timestamped executable quotes, explicit costs and slippage, with no contemporaneous threshold retuning.

## Historical reference result

| Metric | Result |
|---|---:|
| Candidate cycles | 134 |
| Strict frozen-protocol cycles | 84 |
| Strict coverage | 62.7% |
| Gross P&L | ₹83,030.00 |
| Win rate | 61.90% |
| Profit factor | 2.942 |
| Maximum drawdown | ₹8,022.50 |
| Bootstrap 95% interval | ₹31,147.19 to ₹139,293.78 |

## P8 OOS reference

| Metric | Fixed P7 gate |
|---|---:|
| Executable post-2024 cycles | 86 |
| Gate trades | 42 |
| Gross P&L | ₹126,460.50 |
| Win rate | 76.19% |
| Profit factor | 5.115 |
| Gross max drawdown | ₹13,406.25 |
| Worst trade | ₹-12,502.75 |
| Net at 2-point slippage, 0.05% exchange stress | ₹64,304.41 |

These are historical modeled results, not claims of realized live fills.

## Research records

- docs/nifty_calendar/RESEARCH_PLAN.md
- docs/nifty_calendar/PHASE_STATUS.md
- docs/nifty_calendar/ERROR_LOG.md
- docs/nifty_calendar/CONVERSATION_LOG.md