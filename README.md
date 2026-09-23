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

**Event-driven first-qualifying entry is not supported for promotion.**

P9 kept the 1.20 threshold, four-leg structure, same-strike semantics and near-expiry exit frozen.

### Secondary OOS result

| Metric | Fixed 09:15 | Event-driven |
|---|---:|---:|
| Executable trades | 26 | 70 |
| Gross P&L | ₹40,506.25 | ₹37,291.40 |
| Win rate | 80.77% | 62.86% |
| Profit factor | 5.029 | 1.576 |
| Gross max drawdown | ₹7,489.50 | ₹26,467.50 |
| Worst trade | ₹-5,391.75 | ₹-9,984.75 |
| Net at 0-point slippage | ₹29,499.84 | ₹9,222.87 |
| Net at 0.5-point slippage | ₹22,139.84 | ₹-10,837.13 |
| Net at 1-point slippage | ₹14,779.84 | ₹-30,897.13 |
| Net at 2-point slippage | ₹59.84 | ₹-71,017.13 |

### Incremental-trade mechanism

The event-driven arm adds 44 trades beyond the 26 paired fixed-control dates:

- 44 event-only trades gross: ₹-3,214.85; win rate 52.27%; PF 0.941.
- 20 originally gate-pass but unavailable at 09:15: +₹10,749.75 gross.
- 24 originally gate-fail but qualifying later: ₹-13,964.60 gross; PF 0.665.

The negative late-qualifying gate-fail group more than offset the positive contribution from delayed entries on originally gate-pass days.

### Entry-time / ATM diagnostics

- Median event signal time: 09:16 IST.
- Median ATM distance: 48.3 points / 0.189%.
- 90th percentile ATM distance: 306.65 points / 1.212%.
- Maximum ATM distance: 844.35 points / 3.617%.

### Primary-source QC finding

The first public source acquisition succeeded for 192/201 required expiry files, but its far-expiry intraday coverage was too sparse. On 2026-04-01 the far expiry contained only 903 rows for the day, and the only four-leg common strike at the sampled qualifying timestamps was 20,500 while NIFTY was about 22,900.

That primary-source event result was rejected as a performance estimate before the secondary-source test.

## P9 research records

- docs/nifty_calendar/P9_FINAL_RESEARCH_CONCLUSION.md
- reports/nifty_calendar/P9_SECONDARY_VALIDATION_REPORT.md
- reports/nifty_calendar/P9_RISSIN_OOS_COMPARISON.csv
- reports/nifty_calendar/P9_RISSIN_OOS_COSTS.csv
- docs/nifty_calendar/P9_ALTERNATE_DATA_SOURCE_AUDIT.md
- docs/nifty_calendar/ERROR_LOG.md
- docs/nifty_calendar/PHASE_STATUS.md

## Next phase

P10 is planned as forward/paper-execution validation of the frozen fixed rule, using timestamped executable quotes, observed spread, brokerage/statutory charges, slippage and a pre-registered paper ledger. New intraday timing ideas require a separate development phase and unseen validation.