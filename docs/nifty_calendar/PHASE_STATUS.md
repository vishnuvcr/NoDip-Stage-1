# Phase Status

Last updated: 2026-09-23 — P11 stopped at the fresh-data availability gate.

| Phase | Status | Notes |
|---|---|---|
| P0 Specification freeze | COMPLETE | Frozen four-leg calendar structure and 09:15 entry. |
| P1 Literature / market structure | COMPLETE | Sources, market structure and cost literature reviewed. |
| P2 Data acquisition | COMPLETE | 2022-2024 source data and later validation datasets cached/validated. |
| P3 Engine/tests | COMPLETE | Frozen engine and regression controls complete. |
| P4 Historical backtest | COMPLETE | Original 59-trade result preserved. |
| P5 Verification/robustness | COMPLETE | Independent reconciliation completed. |
| P6 Final manuscript | COMPLETE | Strict 84-cycle manuscript completed. |
| P7 Loss audit / entry tuning | COMPLETE | 32 losses audited; CBR <= 1.20 retained only as candidate. |
| P8 Unseen post-2024 validation | COMPLETE | Fixed 09:15 CBR gate validated on 2025+ holdout; not live-approved. |
| P9 Event-driven intraday entry timing | COMPLETE | Event-driven replacement rejected after source QC and cost sensitivity. |
| P10 Entry-day offset research | COMPLETE | Seven offsets tested; no direct OOS promotion. |
| P11 Forward / paper-execution validation | BLOCKED — FRESH DATA UNAVAILABLE | No completed cycle exists after the P10 cutoff in the pinned option source; no reuse of P10 OOS data permitted. |

Research stop condition: P11 is closed for this dataset. No further offsets or parameter searches are performed.
