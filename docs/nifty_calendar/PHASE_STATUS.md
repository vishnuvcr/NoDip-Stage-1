# Phase Status

Last updated: 2026-09-23 — P14 official NSE fresh far-expiry validation completed.

| Phase | Status | Notes |
|---|---|---|
| P0-P10 | COMPLETE | Historical research and seven entry-day offsets completed. |
| P11 | COMPLETE — BLOCKED | No fresh post-P10 cycle existed in the pinned public option source. |
| P12 | COMPLETE — EXPLORATORY | F+1/F+2/F+3/F+4 and entry-only adaptive far-expiry selector tested. |
| P13 | COMPLETE — INSUFFICIENT FRESH SAMPLE | Public option source ended 2026-06-29, so zero fresh post-cutoff cycles. |
| P14 | COMPLETE — INSUFFICIENT FRESH SAMPLE | Official NSE daily F&O UDiFF bhavcopy supplied 3 fresh completed cycles. |

## P14 result

- Fresh cycles: 3
- Adaptive selected trades: 3
- Adaptive selection: F+1 on all 3 cycles
- Adaptive gross P&L: ₹6,714.50
- Adaptive net P&L at 2-point adverse slippage: ₹2,976.46
- Decision: **INSUFFICIENT FRESH SAMPLE — CONTINUE PROSPECTIVE PAPER MONITORING**

The 3-cycle result is descriptive only. No statistical significance claim or live/paper promotion is made from this sample.

## Repository records

- P14 plan: `docs/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_PLAN.md`
- P14 report: `reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_VALIDATION_REPORT.md`
- P14 conclusion: `reports/nifty_calendar/P14_FINAL_RESEARCH_CONCLUSION.md`
- P14 summary: `reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_SUMMARY.csv`
- P14 costs: `reports/nifty_calendar/P14_OFFICIAL_NSE_FRESH_COSTS.csv`
- P14 adaptive selection: `reports/nifty_calendar/P14_ADAPTIVE_SELECTION.csv`
