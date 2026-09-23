# P5 Independent Reconciliation — NIFTY 4-Leg Calendar — 2022-2024

## Source design
Primary source: public NIFTY options mirror used by the locked backtest.
Secondary contract source: an independent GitHub mirror of NSE F&O bhavcopy archives; the research uses the mirror copy for the full 2022-2024 sample.
Independent spot cross-check: Yahoo Finance NIFTY 50 daily session OPEN for each candidate entry date.

## Cycle coverage reconciliation
- Candidate strategy cycles: 134
- Primary valid cycles: 59
- Primary rejected cycles: 75
- Secondary exact-primary-strike complete cycles: 123
- Secondary grid-alternative complete cycles: 9
- Primary rejects recovered at the exact frozen strike: 66
- Primary rejects with only a secondary-grid alternative: 9
- Primary-valid cycles also complete on secondary: 57
- Reconciliation scope: all 134 candidate cycles.

## Primary rejection reasons

| Reason | Cycles |
|---|---:|
| MISSING_ENTRY_LEG | 48 |
| MISSING_ENTRY_LEG+MISSING_EXIT_LEG | 16 |
| NO_COMMON_STRIKE | 9 |
| MISSING_EXIT_LEG | 2 |

## Secondary reconciliation status

| Status | Cycles |
|---|---:|
| RECOVERED_BY_SECONDARY_EXACT | 66 |
| PRIMARY_VALID_SECONDARY_COMPLETE | 57 |
| GRID_ALTERNATIVE_RECOVERY | 9 |
| PRIMARY_VALID_SECONDARY_NONEXECUTABLE | 2 |

## Secondary P&L

- Complete independent cycles: 132
- Complete independent gross P&L: ₹-299,485.00
- Mean trade: ₹-2,268.83
- Win rate: 54.55%
- Exact-primary-strike subset: 123 cycles; gross P&L ₹-323,470.00
- Secondary-grid-alternative subset: 9 cycles; gross P&L ₹23,985.00
- Primary-valid control subset: 57 cycles; gross P&L ₹49,408.75

## Cross-source price and spot checks
- Matched-cycle maximum absolute option price difference: median ₹7.6000; p95 ₹27.2300; max ₹55.8500.
- Yahoo-vs-primary NIFTY open difference on candidate entry dates: median 0.0496 index points; p95 22.2598; max 126.8000.

## Interpretation rule
A primary rejection is not treated as a genuine market non-trade unless the independent NSE source also fails to provide the required frozen-protocol contract data. A complete secondary cycle is classified as a data-coverage recovery, not as an intentional strategy filter.

## Reproducibility
The compact NSE rows used for reconciliation are cached in data/cache/nifty_secondary_reconciliation_2022_2024.csv; raw NSE downloads remain in the GitHub Actions cache so reruns do not repeatedly download the same daily files.