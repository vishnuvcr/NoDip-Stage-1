# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P9 complete. P9 event-driven entry timing was tested on an unseen post-2024 sample using a secondary 1-minute NIFTY option source and was not promoted. P10 forward/paper validation of the frozen fixed rule is planned.**

## Frozen validated reference

P8 validated the fixed calendar-balance gate on the post-2024 temporal holdout:

(far CE / near CE) / (far PE / near PE) <= 1.20

P8 conclusion: supported for further research, not promoted to live trading.

- P8 report: reports/nifty_calendar/P8_OOS_VALIDATION_REPORT_2025_ONWARD.md
- P8 conclusion: reports/nifty_calendar/P8_FINAL_RESEARCH_CONCLUSION.md

## P9 — Event-driven intraday entry timing

### Final decision

**Event-driven first-qualifying entry is not promoted.**

P9 kept the 1.20 threshold, four-leg structure, same-strike semantics and near-expiry exit frozen.

### Secondary OOS after deterministic ATM QC

| Metric | Fixed source diagnostic | Event-driven |
|---|---:|---:|
| Executable trades | 14 | 65 |
| Gross P&L | ₹19,737.25 | ₹43,607.25 |
| Win rate | 78.57% | 64.62% |
| Profit factor | 5.613 | 1.755 |
| Gross max drawdown | ₹2,180.75 | ₹33,429.00 |
| Worst trade | ₹-2,180.75 | ₹-9,984.75 |
| Net at 0-point slippage | ₹13,418.43 | ₹17,798.70 |
| Net at 0.5-point slippage | ₹9,458.43 | ₹-781.30 |
| Net at 1-point slippage | ₹5,498.43 | ₹-19,361.30 |
| Net at 2-point slippage | ₹-2,421.57 | ₹-56,521.30 |

The fixed source diagnostic is not the canonical fixed reference because of incomplete intraday source coverage; P8 remains the canonical fixed-time ledger.

### Canonical paired comparison

- 33 event trades occurred on dates that passed CBR<=1.20 at 09:15 in P8.
- Event gross on those dates: ₹42,312.50.
- Canonical P8 fixed-gate gross on the same dates: ₹104,231.75.
- Mean event-minus-fixed difference: ₹-1,876.34 per date; median ₹-746.25.
- Event was higher on 12/33 paired dates and lower on 21/33.
- Bootstrap 95% CI for the mean paired difference: approximately ₹-3,990.63 to ₹-347.55.
- 32 event trades occurred on dates that failed the 09:15 gate but qualified later; those trades produced ₹1,294.75 gross with PF 1.029.

### Pre-registered latest-entry sensitivity

| Latest signal | Trades | Gross P&L | Net at 0.5 pt | Net at 1 pt | Net at 2 pt |
|---|---:|---:|---:|---:|---:|
| 15:00 | 63 | ₹37,787.00 | ₹-5,170.99 | ₹-23,190.99 | ₹-59,230.99 |
| 15:15 | 64 | ₹38,465.75 | ₹-5,126.99 | ₹-23,446.99 | ₹-60,086.99 |
| 15:30 | 65 | ₹43,607.25 | ₹-781.30 | ₹-19,361.30 | ₹-56,521.30 |
| 15:40 | 65 | ₹43,607.25 | ₹-781.30 | ₹-19,361.30 | ₹-56,521.30 |

The event signal appeared predominantly near the open: median 09:22; only two qualifying event signals occurred after 15:00. No later cutoff improved the cost robustness.

### Primary-source QC finding

The first public source acquisition succeeded for 192/201 required expiry files, but its far-expiry intraday coverage was too sparse. On 2026-04-01 the far expiry contained only 903 rows for the day, and the primary scan selected strike 20,500 while NIFTY was about 22,900. That output was rejected before performance interpretation.

## P9 research records

- reports/nifty_calendar/P9_FINAL_RESEARCH_CONCLUSION.md
- reports/nifty_calendar/P9_SECONDARY_VALIDATION_REPORT.md
- reports/nifty_calendar/P9_RISSIN_OOS_COMPARISON.csv
- reports/nifty_calendar/P9_RISSIN_OOS_COSTS.csv
- reports/nifty_calendar/P9_RISSIN_CUTOFF_SENSITIVITY.csv
- reports/nifty_calendar/P9_RISSIN_CUTOFF_SENSITIVITY_REPORT.md
- docs/nifty_calendar/PHASE_STATUS.md
- docs/nifty_calendar/RESEARCH_PLAN.md
- docs/nifty_calendar/ERROR_LOG.md
- docs/nifty_calendar/CONVERSATION_LOG.md

## Next phase

P10 is planned as forward/paper-execution validation of the frozen fixed rule, using timestamped executable quotes, observed spread, brokerage/statutory charges, slippage and a pre-registered paper ledger. New intraday timing ideas require a separate development phase and unseen validation.

## Research stop condition

The defined P9 research phase is closed. P10 is the next planned phase; no additional P9 parameter search is permitted.
