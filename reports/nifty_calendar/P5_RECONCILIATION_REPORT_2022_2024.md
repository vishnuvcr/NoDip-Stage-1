# P5 Independent Reconciliation — NIFTY 4-Leg Calendar — 2022-2024

## Source design
Primary source: public NIFTY options mirror used by the locked backtest.
Secondary contract source: an independent GitHub mirror of NSE F&O bhavcopy archives; the research uses the mirror copy for the full 2022-2024 sample.
Independent spot cross-check: Yahoo Finance NIFTY 50 daily session OPEN for each candidate entry date.

## Cycle coverage reconciliation
- Candidate strategy cycles: 134
- Primary valid cycles: 59
- Primary rejected cycles: 75
- Secondary fully executable cycles: 132
- Primary rejects recovered by secondary source: 75
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
| RECOVERED_BY_SECONDARY | 75 |
| PRIMARY_VALID_SECONDARY_COMPLETE | 57 |
| PRIMARY_VALID_SECONDARY_NONEXECUTABLE | 2 |

## Secondary P&L

- Secondary complete cycles: 132
- Secondary total P&L across complete cycles: ₹127,185.00
- Secondary mean trade: ₹963.52
- Secondary win rate: 57.58%

## Cross-source price and spot checks
- Matched-cycle maximum absolute option price difference: median ₹8.5000; p95 ₹70.4200; max ₹93.5000.
- Yahoo-vs-primary NIFTY open difference on candidate entry dates: median 0.0496 index points; p95 22.2598; max 126.8000.

## Interpretation rule
A primary rejection is not treated as a genuine market non-trade unless the independent NSE source also fails to provide the required frozen-protocol contract data. A complete secondary cycle is classified as a data-coverage recovery, not as an intentional strategy filter.

## Reproducibility
The compact NSE rows used for reconciliation are cached in data/cache/nifty_secondary_reconciliation_2022_2024.csv; raw NSE downloads remain in the GitHub Actions cache so reruns do not repeatedly download the same daily files.