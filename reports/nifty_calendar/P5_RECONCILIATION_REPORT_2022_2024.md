# P5 Independent Reconciliation — NIFTY 4-Leg Calendar — 2022-2024

## Source design
Primary source: public NIFTY options mirror used by the locked backtest.
Secondary contract source: NSE daily F&O bhavcopy.
Independent spot cross-check: Yahoo Finance NIFTY 50 daily session OPEN.

## Coverage
- Candidate cycles: 134
- Primary valid: 59
- Primary rejected: 75
- Secondary complete: 0
- Recovered by secondary: 0
- Primary-valid and secondary-complete: 0

## Primary rejection reasons

| Reason | Cycles |
|---|---:|
| MISSING_ENTRY_LEG | 48 |
| MISSING_ENTRY_LEG+MISSING_EXIT_LEG | 16 |
| NO_COMMON_STRIKE | 9 |
| MISSING_EXIT_LEG | 2 |

## Cross-source checks
- Yahoo-vs-primary NIFTY open difference: median 2.1508; p95 24.8795; max 126.8000 index points.

## Interpretation
Primary rejections are treated as genuine non-executions only when the independent NSE source also fails the frozen contract requirements. Secondary-complete cycles are data-coverage recoveries.