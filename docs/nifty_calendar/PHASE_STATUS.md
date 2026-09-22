# Phase Status

Last updated: 2026-09-23

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Entry: first trading day after prior expiry, 09:15 open; near-expiry close exit; four legs fixed; historical expiry regime versioned |
| P1 Literature / market structure | COMPLETE | NSE expiry/lot rules, public datasets, Paytm Money fee sources and academic weekly-option/calendar-spread literature reviewed |
| P2 Data acquisition | COMPLETE | Public 2022-2024 NIFTY archive downloaded/cached; source ticker schema and source-to-engine C/P->CE/PE mapping validated |
| P3 Engine/tests | COMPLETE | Engine implemented; CI import/setup and pandas 3 dtype defects corrected; regression tests pass |
| P4 Historical backtest | IN PROGRESS | Latest run reached the engine but failed on pandas 3 lot-size normalization; fix committed and a fresh run is being triggered |
| P5 Verification/robustness | IN PROGRESS | Requires validated trade ledger |
| P6 Final manuscript | PENDING | Requires validated results |
