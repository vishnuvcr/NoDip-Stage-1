# Phase Status

Last updated: 2026-09-23 — P0-P10 complete; P10 offset screen closed without direct promotion; P11 forward/paper validation planned

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Entry: first trading day after prior expiry, 09:15 open; near-expiry close exit; four legs fixed; historical expiry regime versioned |
| P1 Literature / market structure | COMPLETE | NIFTY weekly-option market design, expiry/lot rules, public datasets, execution/cost literature and broker-cost sources reviewed |
| P2 Data acquisition | COMPLETE | 2022-2024 public NIFTY archive acquired/cached; source ticker schema and C/P to CE/PE mapping validated |
| P3 Engine/tests | COMPLETE | Frozen engine, historical lot sizes, CI fixes and regression tests completed |
| P4 Historical backtest | COMPLETE | 59 valid executable trades; gross P&L ₹52,827.50 |
| P5 Verification/robustness | COMPLETE | Corrected independent-source validation; strict frozen-protocol sample established |
| P6 Final manuscript | COMPLETE | Strict 84-cycle manuscript, figures, statistics, trade-level appendix and cost/slippage sensitivity committed |
| P7 Loss audit / entry tuning | COMPLETE | 32 losses audited; candidate calendar-balance gate <=1.20 identified; P6 unchanged |
| P8 Unseen post-2024 validation | COMPLETE | Frozen 1.20 gate tested unchanged on 2025+ temporal holdout; supported for further research, not promoted to live trading |
| P9 Event-driven intraday entry timing | COMPLETE | Primary source failed ATM/far-expiry coverage QC. After deterministic 25-point ATM QC, Rissin OOS had 65 event trades, gross ₹43,607.25, PF 1.755; modeled event net was negative from 0.5-point slippage. On 33 event dates that passed the canonical P8 09:15 gate, mean event-minus-fixed was ₹-1,876.34 with bootstrap 95% CI ₹-3,990.63 to ₹-347.55. Event-driven timing is not promoted. |
| P10 Entry-day offset research | COMPLETE | Seven pre-registered trading-session offsets tested at frozen 09:15 + CBR<=1.20. Corrected OOS has 88 cycles. D0 and D+2 show the strongest raw OOS net under 2-point stress, but paired bootstrap CIs versus D+1 include zero; D+5 is negative and has a paired CI entirely below zero. No offset promoted directly from OOS. |
| P11 Forward / paper-execution validation | PLANNED | Freeze any development-selected offset only after unseen validation; use timestamped executable quotes, observed spreads, real costs and a pre-registered paper ledger |

## P9 final decision

Event-driven first-qualifying entry is not promoted. The 1.20 threshold, four-leg structure, strike semantics and near-expiry exit remain frozen.

### Secondary-source OOS after deterministic ATM QC

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

The fixed source diagnostic does not replace the canonical P8 fixed-gate ledger because of incomplete intraday source coverage.

### Canonical P8 paired comparison

- 33 event trades occurred on dates that passed CBR<=1.20 at 09:15 in P8: gross ₹42,312.50.
- Canonical P8 fixed-gate P&L on the same dates: ₹104,231.75.
- Event minus fixed: ₹-61,919.25 total; mean ₹-1,876.34; median ₹-746.25.
- Event higher on 12/33 dates and lower on 21/33.
- Bootstrap 95% CI for mean paired difference: approximately ₹-3,990.63 to ₹-347.55.
- 32 event trades arose on dates that failed the 09:15 gate but qualified later: gross ₹1,294.75; PF 1.029.

### Latest-entry sensitivity

- 15:00: 63 trades, net at 1-point slippage ₹-23,190.99.
- 15:15: 64 trades, net at 1-point slippage ₹-23,446.99.
- 15:30: 65 trades, net at 1-point slippage ₹-19,361.30.
- 15:40: 65 trades, net at 1-point slippage ₹-19,361.30.
- No later pre-registered cutoff restored positive net P&L at 0.5-point adverse slippage.

## P9 source-quality finding

The primary thetrademarkk source successfully acquired 192/201 required expiry files and 1-minute NIFTY spot, but far-expiry intraday coverage was too sparse. On 2026-04-01 the far expiry had only 903 rows for the day, and the only four-leg common strike at the sampled qualifying timestamps was 20,500 while NIFTY was about 22,900.

The primary-source event result was therefore rejected as a performance estimate before the secondary test.

## Research stop / next phase

P9 stops here. The next phase is P10 forward/paper-execution validation of the frozen fixed rule. Any new intraday timing/filter idea must be a separate development phase with a new unseen temporal holdout.
## P10 entry-day offset conclusion

- OOS population: 88 expiry cycles, with 88 distinct previous-expiry dates after the corrected mapping audit.
- D0: 42 trades, gross ₹133,757.75, PF 11.925, net ₹69,890.36 at 2-point adverse slippage.
- D+2: 44 trades, gross ₹129,107.75, PF 8.100, net ₹63,387.53 at 2-point adverse slippage.
- D+1 canonical reference: 36 trades, gross ₹99,992.75, PF 4.540, net ₹46,131.90 at 2-point adverse slippage.
- D+5: 19 trades, gross ₹17,240.00, net ₹-10,274.78 at 2-point slippage.
- Paired OOS bootstrap vs D+1: D0 mean +₹383.69 (CI −₹797.17 to +₹1,480.94); D+2 mean +₹330.85 (CI −₹445.32 to +₹1,099.05); D+5 mean −₹940.37 (CI −₹1,975.86 to −₹69.96).
- No offset is promoted directly from the seven-offset OOS screen.

## Research stop / next phase

P10 stops here. P11 is forward/paper execution after a development-only offset-selection rule and a fresh unseen temporal holdout. No additional day offsets are searched in P10.
