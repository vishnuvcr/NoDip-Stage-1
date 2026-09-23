# Phase Status

Last updated: 2026-09-23  — P0-P6 complete for 2022-2024 study

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Entry: first trading day after prior expiry, 09:15 open; near-expiry close exit; four legs fixed; historical expiry regime versioned |
| P1 Literature / market structure | COMPLETE | NSE expiry/lot rules, public datasets, Paytm Money fee sources and weekly-option/calendar-spread literature reviewed |
| P2 Data acquisition | COMPLETE | 2022-2024 public NIFTY archive acquired/cached; source ticker schema and C/P→CE/PE mapping validated |
| P3 Engine/tests | COMPLETE | Frozen engine, historical lot sizes, CI fixes and regression tests completed |
| P4 Historical backtest | COMPLETE | 59 valid executable trades; gross P&L ₹52,827.50; trade ledger and annual results committed |
| P5 Verification/robustness | COMPLETE | Corrected positive-open validation: 57 primary-valid cycles reproduced; 27 primary rejects recovered at the same strike; 28 source-specific strike-reselection cycles retained as sensitivity; 20 primary rejects unresolved; 2 primary-valid cycles not reproduced |
| P6 Final manuscript | COMPLETE | Final strict 84-cycle frozen-protocol manuscript, figures, statistics, trade-level appendix, cost sensitivity and validation checks committed |
