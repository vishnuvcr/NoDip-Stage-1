# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P14 retrospective research complete. P9 event-driven timing remains discarded. P10 completed the seven-offset timing screen. P11/P13 were blocked by stale source data. P12 introduced the frozen far-expiry selector. P14 completed a genuinely fresh official-NSE validation on three post-cutoff weekly cycles. Current status: PAPER MONITORING ONLY — INSUFFICIENT FRESH SAMPLE.**

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

## P12 — Far-expiry selection research

P12 tested the user's new structure with the far expiry set to F+1, F+2, F+3 and F+4 listed expiries after the near expiry.

### Entry-time selection rule

At 09:15, among candidates with the same ATM strike and all four entry legs executable, select the far expiry with the highest normalized entry credit:

(near CE - near PE + far PE - far CE) / spot open

This is an entry-only score; no future P&L is used.

### Evaluation-period result

| Strategy | Trades | Gross P&L | PF | Net @ 2 pt |
|---|---:|---:|---:|---:|
| F+1 | 72 | ₹29,543 | 1.321 | -₹76,676 |
| F+2 | 73 | -₹23,166 | 0.836 | -₹132,051 |
| F+3 | 64 | ₹33,142 | 1.288 | -₹62,957 |
| F+4 | 42 | ₹90,237 | 2.373 | ₹26,958 |
| Adaptive | 77 | ₹144,278 | 2.763 | ₹30,311 |

The adaptive rule selected F+1 on 59/77 evaluation trades, F+2 on 8, F+3 on 6 and F+4 on 4.

Important: the 2025+ evaluation period was already exposed during P10, so P12 is exploratory rather than fresh confirmatory OOS validation. A genuinely new post-P10 holdout is still required before promotion.

- [P12 plan](docs/nifty_calendar/P12_FAR_EXPIRY_SELECTION_PLAN.md)
- [P12 report](reports/nifty_calendar/P12_FAR_EXPIRY_SELECTION_REPORT.md)
- [P12 conclusion](reports/nifty_calendar/P12_FINAL_RESEARCH_CONCLUSION.md)
- [P12 summary](reports/nifty_calendar/P12_FAR_EXPIRY_SUMMARY.csv)
- [P12 cost sensitivity](reports/nifty_calendar/P12_FAR_EXPIRY_COST_SENSITIVITY.csv)
## P12 — Far-expiry selection extension

P12 tested the user's new structure with far expiries F+1/F+2/F+3/F+4 and froze an entry-only far-expiry selector:

`(near CE - near PE + far PE - far CE) / NIFTY spot open`

On the already-exposed 2025+ evaluation period, the adaptive rule produced 77 trades, gross P&L ₹144,277.50, PF 2.763 and net P&L ₹30,311.14 at 2-point adverse slippage. This was exploratory, not fresh confirmatory OOS.

- [P12 plan](reports/nifty_calendar/P12_FAR_EXPIRY_SELECTION_PLAN.md)
- [P12 report](reports/nifty_calendar/P12_FAR_EXPIRY_SELECTION_REPORT.md)
- [P12 conclusion](reports/nifty_calendar/P12_FINAL_RESEARCH_CONCLUSION.md)
- [P12 summary](reports/nifty_calendar/P12_FAR_EXPIRY_SUMMARY.csv)

## P13 — Fresh-data gate

P13 correctly refused to reuse old observations because the pinned Hugging Face daily source ended at 2026-06-29 while the frozen cutoff was 2026-08-26. Fresh cycles: **0**.

- [P13 report](reports/nifty_calendar/P13_FRESH_FAR_EXPIRY_VALIDATION_REPORT.md)
- [P13 conclusion](reports/nifty_calendar/P13_FINAL_RESEARCH_CONCLUSION.md)

## P14 — Official NSE fresh validation

P14 re-tested the exact frozen P12 selector on three genuinely fresh post-cutoff weekly cycles using official NSE F&O UDiFF bhavcopy archives.

| Metric | Fresh P14 result |
|---|---:|
| Completed weekly cycles | 3 |
| Adaptive trades | 3 |
| Adaptive gross P&L | ₹6,714.50 |
| Net @ 0-point slippage | ₹6,096.46 |
| Net @ 0.5-point slippage | ₹5,316.46 |
| Net @ 1-point slippage | ₹4,536.46 |
| Net @ 2-point slippage | ₹2,976.46 |
| Far expiry selected | F+1 on 3/3 cycles |

The three-cycle sample is too small for a reliable statistical inference, and the selector did not actually switch among far horizons in the fresh sample. Therefore the research result is **PAPER MONITORING ONLY — INSUFFICIENT FRESH SAMPLE**.

- [P14 plan](docs/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_PLAN.md)
- [P14 source manifest](reports/nifty_calendar/P14_NSE_SOURCE_MANIFEST.csv)
- [P14 fresh ledger](reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_LEDGER.csv)
- [P14 summary](reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_SUMMARY.csv)
- [P14 costs](reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_COSTS.csv)
- [P14 report](reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_REPORT.md)
- [P14 conclusion](reports/nifty_calendar/P14_FINAL_RESEARCH_CONCLUSION.md)
- [Final manuscript](reports/nifty_calendar/FINAL_RESEARCH_MANUSCRIPT_2026.md)
## Research stop condition

P0-P14 retrospective research is closed. No additional historical far-expiry horizons, score weights, CBR thresholds or timing parameters will be searched on the existing sample. The next activity is prospective paper monitoring of the frozen P12/P14 selector as new weekly cycles complete.

## P14 — Official NSE fresh far-expiry validation

P14 re-tested the frozen P12 far-expiry selector using official NSE F&O daily UDiFF bhavcopy data strictly after the P10/P12 cutoff of 2026-08-26.

| Strategy | Fresh trades | Gross P&L | Net @ 2-pt slippage |
|---|---:|---:|---:|
| F+1 | 3 | ₹6,714.50 | ₹2,976.46 |
| F+2 | 3 | ₹3,081.00 | −₹709.34 |
| F+3 | 3 | ₹6,100.25 | ₹2,260.39 |
| F+4 | 0 | — | — |
| Adaptive | 3 | ₹6,714.50 | ₹2,976.46 |

The frozen adaptive selector chose **F+1 on all three fresh cycles**. Because only three completed cycles were available, this is descriptive evidence only and does not establish statistical robustness or live readiness.

- [P14 plan](docs/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_PLAN.md)
- [P14 report](reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_REPORT.md)
- [P14 conclusion](reports/nifty_calendar/P14_FINAL_RESEARCH_CONCLUSION.md)
- [P14 source manifest](reports/nifty_calendar/P14_NSE_SOURCE_MANIFEST.csv)
- [P14 trade ledger](reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_LEDGER.csv)
