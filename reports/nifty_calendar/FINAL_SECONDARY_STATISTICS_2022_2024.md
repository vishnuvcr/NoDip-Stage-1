# Final Secondary-Source Statistics — NIFTY 4-Leg Calendar — 2022-2024

## Population
- Candidate cycles: 134
- Complete independent-secondary cycles: 132
- Coverage: 98.5%
- Primary rejects recovered by secondary: 75/75
- Primary-valid cycles also complete on secondary: 57/59
- Primary-valid cycles not constructible on secondary: 2

## Gross performance
- Gross P&L: ₹127,185.00
- Mean trade: ₹963.52
- Median trade: ₹519.38
- Win rate: 57.58% (76/132)
- Profit factor: 1.542
- Maximum drawdown: ₹90,152.50
- Best trade: ₹62,080.00
- Worst trade: ₹-31,597.50
- Circular 3-trade block bootstrap 95% interval for total gross P&L: ₹-67,517.25 to ₹342,106.84

## Annual decomposition

| Year | Trades | Gross P&L (₹) | Mean trade (₹) |
|---:|---:|---:|---:|
| 2022 | 46 | 41,190.00 | 895.43 |
| 2023 | 51 | 82,880.00 | 1,625.10 |
| 2024 | 35 | 3,115.00 | 89.00 |

## Cost sensitivity at 0.05000% exchange-charge rate

| Brokerage / order | 0 pt slippage | 0.50 pt | 1.00 pt | 2.00 pt |
|---:|---:|---:|---:|---:|
| ₹10 | ₹105,167.95 | ₹80,817.95 | ₹56,467.95 | ₹7,767.95 |
| ₹15 | ₹98,937.55 | ₹74,587.55 | ₹50,237.55 | ₹1,537.55 |
| ₹20 | ₹92,707.15 | ₹68,357.15 | ₹44,007.15 | ₹-4,692.85 |

## Validation
- Repository tests: 4 passed.
- P6 GitHub Actions manuscript-validation run: successful.
- Manuscript, four SVG figures, secondary trade ledger, and cost-sensitivity ledger all passed file/link checks.

## Interpretation
The historical result is a descriptive sample result, not a forecast. The bootstrap interval crosses zero, and daily OHLC does not prove simultaneous executable four-leg fills.