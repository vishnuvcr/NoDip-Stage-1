# Phase Status

Last updated: 2026-09-23

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Entry: first trading day after prior expiry, 09:15 open; near expiry exit close; four legs fixed; historical expiry-day regime explicitly versioned |
| P1 Literature / market structure | COMPLETE | NSE contract/expiry rules, 2025 expiry-day change, public datasets, Paytm Money fee sources and academic weekly-option/calendar-spread literature reviewed |
| P2 Data acquisition | IN PROGRESS | Official NSE archive is preferred; current execution environment cannot directly download NSE/Kaggle binaries, so reproducible GitHub Actions acquisition and independent-source validation are being built |
| P3 Engine/tests | PENDING | |
| P4 Historical backtest | BLOCKED BY DATA | Mechanical specification is ready; numerical results wait for validated contract-level historical data |
| P5 Verification/robustness | PENDING | |
| P6 Final manuscript | PENDING | |
