# Phase Status

Last updated: 2026-09-23 — P0-P8 complete; P9 event-driven entry-timing phase COMPLETE; event-driven timing not promoted; P10 forward/paper validation planned

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
| P9 Event-driven intraday entry timing | COMPLETE | Primary public source failed ATM/far-expiry coverage QC; secondary Rissin OOS test found 70 event trades vs 26 fixed-control trades, but 44 incremental trades lost ₹3,214.85 gross and event net P&L became negative from 0.5-point slippage onward |
| P10 Forward / paper-execution validation | PLANNED | Return to the frozen fixed rule; use timestamped executable quotes, observed spreads, real costs and a pre-registered paper ledger |

## P9 final decision

Event-driven first-qualifying entry is not promoted. P9 did not alter the CBR threshold, four-leg structure, strike semantics, or exit rule.

### Secondary-source OOS result

| Metric | Fixed 09:15 | Event-driven |
|---|---:|---:|
| Executable trades | 26 | 70 |
| Gross P&L | ₹40,506.25 | ₹37,291.40 |
| Win rate | 80.77% | 62.86% |
| Profit factor | 5.029 | 1.576 |
| Gross max drawdown | ₹7,489.50 | ₹26,467.50 |
| Worst trade | ₹-5,391.75 | ₹-9,984.75 |
| 0-point slippage net | ₹29,499.84 | ₹9,222.87 |
| 0.5-point slippage net | ₹22,139.84 | ₹-10,837.13 |
| 1-point slippage net | ₹14,779.84 | ₹-30,897.13 |
| 2-point slippage net | ₹59.84 | ₹-71,017.13 |

### Incremental event-only trades

- 44 additional trades were admitted by waiting intraday.
- Aggregate gross P&L: ₹-3,214.85.
- Win rate: 52.27%.
- Profit factor: 0.941.
- 20 were originally gate-pass at the fixed observation: +₹10,749.75 gross.
- 24 were originally gate-fail but became CBR<=1.20 later: ₹-13,964.60 gross.

### Quality diagnostics

- Event median signal time: 09:16 IST.
- Event median ATM distance: 48.3 points / 0.189%.
- Event 90th percentile ATM distance: 306.65 points / 1.212%.
- Maximum event ATM distance: 844.35 points / 3.617%.

## P9 source-quality finding

The primary thetrademarkk source successfully acquired 192/201 required expiry files and 1-minute NIFTY spot, but far-expiry intraday coverage was too sparse. On 2026-04-01 the far expiry had only 903 rows for the day, and the only four-leg common strike at the sampled qualifying timestamps was 20,500 while NIFTY was about 22,900.

The primary-source event result was therefore rejected as a performance estimate before the secondary test.

## Research stop / next phase

P9 stops here. The next phase is P10 forward/paper-execution validation of the frozen fixed rule. Any new intraday timing/filter idea must be a separate development phase with a new unseen temporal holdout.