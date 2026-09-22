# Phase Status

Last updated: 2026-09-23

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Entry: first trading day after prior expiry, 09:15 open; near-expiry close exit; four legs fixed; historical expiry regime versioned |
| P1 Literature / market structure | COMPLETE | NSE expiry/lot rules, public datasets, Paytm Money fee sources and weekly-option/calendar-spread literature reviewed |
| P2 Data acquisition | COMPLETE | 2022-2024 public NIFTY archive acquired/cached; source ticker schema and C/P→CE/PE mapping validated |
| P3 Engine/tests | COMPLETE | Frozen engine, historical lot sizes, CI fixes and regression tests completed |
| P4 Historical backtest | COMPLETE | 59 valid executable trades; gross P&L ₹52,827.50; trade ledger and annual results committed |
| P5 Verification/robustness | IN PROGRESS | Leg-specific slippage, known brokerage/statutory costs and exchange-charge sensitivity completed; 44.0% cycle coverage remains the main validation issue |
| P6 Final manuscript | PENDING | Awaiting P5 independent-source reconciliation and final figures/tables |
