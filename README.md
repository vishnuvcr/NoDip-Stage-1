# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P10 complete. P9 event-driven timing remains discarded. P10 tested seven fixed entry sessions relative to the previous expiry; no offset is promoted directly from OOS. P11 reached the fresh-data gate and is closed for this dataset because no completed cycle exists after the P10 cutoff.**

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

## P11 — Forward / paper-execution validation

### Final status

**BLOCKED — FRESH DATA UNAVAILABLE**

A deterministic development-only selection rule was preregistered: require >=90% development coverage and PF>2, then select the highest development net P&L at 2-point adverse slippage. This selects **D-1** using 2022-2024 development data only.

The P10 OOS cutoff is 2026-08-26. The pinned option source available to the P11 runner contains no completed cycle after that cutoff, so P11 cannot legitimately evaluate D-1 without reusing already-seen OOS observations.

- [P11 plan](docs/nifty_calendar/P11_FORWARD_VALIDATION_PLAN.md)
- [P11 report](reports/nifty_calendar/P11_FORWARD_VALIDATION_REPORT.md)
- [P11 conclusion](reports/nifty_calendar/P11_FINAL_RESEARCH_CONCLUSION.md)
- [Final research manuscript](reports/nifty_calendar/FINAL_RESEARCH_MANUSCRIPT_2026.md)
- [P11 ledger](reports/nifty_calendar/P11_FORWARD_TRADE_LEDGER.csv)

## P10 — Entry-day offset research

The frozen 09:15 + CBR<=1.20 criteria were tested on seven trading-session offsets relative to the previous expiry: D-1, D0, D+1, D+2, D+3, D+4, D+5.

### Authoritative OOS result

| Offset | Trades | Gross P&L | PF | Net at 0.5 pt | Net at 1 pt | Net at 2 pt |
|---|---:|---:|---:|---:|---:|---:|
| D-1 | 44 | ₹90,808.25 | 2.922 | ₹61,646.23 | ₹49,046.23 | ₹23,846.23 |
| D0 | 42 | ₹133,757.75 | 11.925 | ₹105,830.36 | ₹93,850.36 | ₹69,890.36 |
| D+1 | 36 | ₹99,992.75 | 4.540 | ₹76,971.90 | ₹66,691.90 | ₹46,131.90 |
| D+2 | 44 | ₹129,107.75 | 8.100 | ₹101,127.53 | ₹88,547.53 | ₹63,387.53 |
| D+3 | 36 | ₹50,454.25 | 1.993 | ₹27,869.18 | ₹17,629.18 | ₹-2,850.82 |
| D+4 | 33 | ₹80,699.00 | 3.834 | ₹60,177.50 | ₹50,837.50 | ₹32,157.50 |
| D+5 | 19 | ₹17,240.00 | 2.359 | ₹5,865.22 | ₹485.22 | ₹-10,274.78 |

The authoritative OOS population contains 88 cycles and 88 distinct previous-expiry dates after the mapping audit.

### Paired OOS robustness vs D+1

- D-1: mean ₹-104.37; bootstrap 95% CI ₹-1,403.35 to ₹1,114.14.
- D0: mean ₹+383.69; CI ₹-797.17 to ₹+1,480.94.
- D+2: mean ₹+330.85; CI ₹-445.32 to ₹+1,099.05.
- D+3: mean ₹-562.94; CI ₹-1,480.49 to ₹+308.59.
- D+4: mean ₹-219.25; CI ₹-1,179.47 to ₹+716.87.
- D+5: mean ₹-940.37; CI ₹-1,975.86 to ₹-69.96.

No offset is promoted directly from the OOS screen. D0 and D+2 remain development-only candidates for a separate selection/validation phase; D+5 shows a negative paired result.

### P10 records

- Plan: docs/nifty_calendar/P10_ENTRY_DAY_OFFSET_PLAN.md
- Final conclusion: reports/nifty_calendar/P10_FINAL_RESEARCH_CONCLUSION.md
- Paired bootstrap: reports/nifty_calendar/P10_OOS_PAIRED_BOOTSTRAP.md
- Detailed report: reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_REPORT.md
- Ledger: reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_LEDGER.csv

## Research stop condition

P0-P10 are closed. P11 is closed at the fresh-data availability gate. No additional entry-day offsets or parameter searches are performed on the existing sample. A future run may resume P11 only after genuinely fresh post-cutoff option data are added to the pinned cache.
