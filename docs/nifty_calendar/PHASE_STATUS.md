# Phase Status

Last updated: 2026-09-23 — P14 official NSE fresh far-expiry validation completed.

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Frozen four-leg calendar structure and execution assumptions. |
| P1 Literature / source validation | COMPLETE | Source and market-structure review completed. |
| P2 Data acquisition | COMPLETE | Historical public-source dataset cached/validated. |
| P3 Engine/tests | COMPLETE | Frozen mechanical engine and regression controls completed. |
| P4 Historical backtest | COMPLETE | Historical executable subset preserved. |
| P5 Verification/robustness | COMPLETE | Independent reconciliation and audits completed. |
| P6 Final manuscript | COMPLETE | Manuscript preserved and updated through P14. |
| P7 Loss audit / entry tuning | COMPLETE | CBR<=1.20 retained as a frozen research gate. |
| P8 Unseen post-2024 validation | COMPLETE | Fixed-time CBR gate validated; not live-approved. |
| P9 Event-driven timing | COMPLETE — NOT PROMOTED | Event-driven first-qualifying entry rejected after source QC and cost sensitivity. |
| P10 Entry-day offsets | COMPLETE — NOT PROMOTED | D-1,D0,D+1,D+2,D+3,D+4,D+5 tested without OOS winner selection. |
| P11 Forward validation | COMPLETE — DATA BLOCKED | Pinned source ended 2026-06-29 before 2026-08-26 cutoff. |
| P12 Far-expiry selection | COMPLETE — EXPLORATORY | F+1/F+2/F+3/F+4 compared; entry-only normalized-credit selector frozen. |
| P13 Fresh far-expiry validation | COMPLETE — DATA BLOCKED | No fresh cycles in stale pinned source. |
| P14 Official NSE fresh validation | COMPLETE — PAPER MONITORING ONLY | Three fresh cycles from official NSE UDiFF; adaptive selected F+1 on all 3. |

## Current research decision

**PAPER MONITORING ONLY — INSUFFICIENT FRESH SAMPLE**

P14 produced 3 fresh adaptive trades with gross P&L ₹6,714.50 and modeled net P&L ₹2,976.46 at 2-point adverse slippage. The sample is too small for statistical inference, and the adaptive selector did not switch among far-expiry horizons.

## Research stop condition

Retrospective research is closed at P14. No further historical parameter or far-expiry search is performed on the current dataset.

The next allowed activity is prospective paper monitoring with the frozen P12/P14 selector as new weekly cycles become available.
