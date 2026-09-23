# Phase Status

Last updated: 2026-09-23  — P0-P6 complete for 2022-2024 study

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Entry: first trading day after prior expiry, 09:15 open; near-expiry close exit; four legs fixed; historical expiry regime versioned |
| P1 Literature / market structure | COMPLETE | NSE expiry/lot rules, public datasets, Paytm Money fee sources and weekly-option/calendar-spread literature reviewed |
| P2 Data acquisition | COMPLETE | 2022-2024 public NIFTY archive acquired/cached; source ticker schema and C/P→CE/PE mapping validated |
| P3 Engine/tests | COMPLETE | Frozen engine, historical lot sizes, CI fixes and regression tests completed |
| P4 Historical backtest | COMPLETE | 59 valid executable trades; gross P&L ₹52,827.50; trade ledger and annual results committed |
| P5 Verification/robustness | COMPLETE | Full 134-cycle reconciliation completed against an independent public mirror of NSE F&O bhavcopy plus Yahoo spot-open cross-check; 132/134 cycles complete on secondary source; all 75 primary rejects recovered |
| P6 Final manuscript | IN PROGRESS | Drafting final manuscript, figures, source-coverage interpretation, cost sensitivity and appendices from the 132-cycle independent ledger |
