# Phase Status

Last updated: 2026-09-23 — P0-P8 complete; P9 event-driven entry-timing phase opened; public intraday source audit complete and acquisition path prepared

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
| P9 Event-driven intraday entry timing | IN PROGRESS / ACQUISITION PREPARED | Alternate-source audit completed. Primary public candidate is Hugging Face thetrademarkk 1-minute NIFTY option data; Kaggle 2024 and rissin HF are secondary/cross-check sources; acquisition workflow committed but no workflow run has yet been observed |
| P10 Forward / paper-execution validation | PLANNED | Fixed rule only after P9 design is settled; timestamped executable quotes, real costs and forward paper ledger |

## P9 boundary

P6 and P8 remain reference results. P9 may change entry timing only; it may not rewrite the frozen 1.20 threshold or the four-leg/exit structure.

## P9 data-source finding

The source audit identified public 1-minute datasets with explicit expiry/strike information. None of the currently identified public schemas provides reliable historical bid/ask quotes.

- Primary candidate: `thetrademarkk/india-index-options-1m` — 1-minute NIFTY index plus option files partitioned by actual expiry date, with strike, CE/PE, OHLCV and OI.
- Secondary candidate: `rissin/nse-options-intraday` — 1-minute NIFTY options with explicit expiry, strike and option type; intraday provenance is Upstox.
- 2024 cross-check: Kaggle `Historical Nifty Options 2024 All Expiries`, with expiry/trade-day file structure and separate NIFTY spot files.
- Higher-fidelity fallback: QuantDev-stack OptionVault, which advertises 1-minute, 1-second, tick/Level-2 and Greeks samples; full historical access is licensed/commercial.

## P9 immediate blocker

Numerical event-driven scoring remains blocked until a runner successfully materializes and validates the timestamped multi-expiry source files. No P9 performance result has been claimed.