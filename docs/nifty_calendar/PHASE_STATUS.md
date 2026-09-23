# Phase Status

Last updated: 2026-09-23 — P0-P8 complete; P9 event-driven entry-timing phase active; primary-source QC exposed a far-expiry sparsity failure; secondary-source validation is running

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
| P9 Event-driven intraday entry timing | IN PROGRESS / SECONDARY SOURCE VALIDATION | Primary HF acquisition succeeded (192/201 expiry files; ~671.8 MB; 157/170 cycles with both near/far files), but the first primary timing output is rejected because far-expiry coverage is too sparse and produced an invalid 20,500 strike against NIFTY near 22,899. Rissin secondary-source OOS validation is running. |
| P10 Forward / paper-execution validation | PLANNED | Fixed rule only after P9 design is settled; timestamped executable quotes, real costs and forward paper ledger |

## P9 boundary

P6 and P8 remain reference results. P9 may change entry timing only; it may not rewrite the frozen 1.20 threshold or the four-leg/exit structure.

## P9 data-source finding

The source audit identified public 1-minute datasets with explicit expiry/strike information. None of the currently identified public schemas provides reliable historical bid/ask quotes.

- Primary candidate: thetrademarkk/india-index-options-1m — 1-minute NIFTY index plus option files partitioned by actual expiry date, with strike, CE/PE, OHLCV and OI.
- Secondary candidate: rissin/nse-options-intraday — 1-minute NIFTY options with explicit expiry, strike and option type; intraday provenance is Upstox.
- 2024 cross-check: Kaggle Historical Nifty Options 2024 All Expiries, with expiry/trade-day file structure and separate NIFTY spot files.
- Higher-fidelity fallback: QuantDev-stack OptionVault, which advertises 1-minute, 1-second, tick/Level-2 and Greeks samples; full historical access is licensed/commercial.

## P9 acquisition result

- 170 input research cycles
- 201 unique option expiry files requested
- 192 expiry files downloaded
- ~671.8 MB downloaded in the successful acquisition run
- 1-minute NIFTY index file downloaded
- 157/170 cycles ready for intraday reconstruction (92.35%)
- 13/170 cycles source-gapped because required later-2026 expiry files are absent from the source snapshot

The initial successful workflow cached only the manifest, not the raw Hugging Face directory. The workflow has since been corrected to cache the actual Hugging Face dataset directory under a stable key.

## P9 immediate blocker

Primary-source timing output is rejected on source-quality grounds, not strategy performance grounds. The 2026-04-01 audit shows the NIFTY index series is around 22,843–22,899 during the opening minutes, while the primary option panel is so sparse on the far expiry that the reconstructed event trade selected strike 20,500. P9 will not interpret any performance result until a secondary option source passes ATM-distance, four-leg completeness, error-rate and paired-reference checks.