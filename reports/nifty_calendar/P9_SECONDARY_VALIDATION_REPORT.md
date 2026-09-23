# P9 Secondary Validation Report — Rissin/Upstox 1-Minute OOS

## Population
- 86 executable post-2024 cycles inherited from P8.
- Same eligible dates, near expiries, far expiries and lot sizes.
- No threshold changes.

## Source
Rissin nse-options-intraday, Upstox-derived 1-minute NIFTY option data.

## Execution
- Frozen CBR <= 1.20.
- Fixed control: signal at 09:15 and next-minute open execution.
- Event arm: first qualifying timestamp from 09:15 through 15:30, then next-minute open execution.
- Common strike selected from contemporaneous common executable CE/PE contracts using nearest-to-spot P6 semantics.
- Exit: last common executable near-expiry-day close.
- Costs: same P8 modeled stress, including 0/0.5/1/2 point adverse slippage and 0.05% exchange-charge sensitivity.

## Coverage
| State | Fixed | Event |
|---|---:|---:|
| Executable | 26 | 70 |
| No four-leg panel | 9 | 9 |
| No trigger | 49 | 1 |
| No exit | 2 | 6 |
| No fill | 0 | 0 |

## Performance
| Metric | Fixed | Event |
|---|---:|---:|
| Trades | 26 | 70 |
| Gross P&L | ₹40,506.25 | ₹37,291.40 |
| Win rate | 80.77% | 62.86% |
| Profit factor | 5.029 | 1.576 |
| Gross max drawdown | ₹7,489.50 | ₹26,467.50 |
| Worst trade | ₹-5,391.75 | ₹-9,984.75 |

## Incremental trades
The 44 event-only trades were:
- gross P&L: ₹-3,214.85
- win rate: 52.27%
- profit factor: 0.941

Split by original P8 gate state:
- 20 originally gate-pass but not executable at 09:15: gross ₹10,749.75, PF 1.823.
- 24 originally gate-fail and only qualifying later: gross ₹-13,964.60, PF 0.665.

## Slippage
At 0.05% exchange-charge stress:
- fixed 09:15: ₹29,499.84 / ₹22,139.84 / ₹14,779.84 / ₹59.84 net P&L for 0 / 0.5 / 1 / 2 points.
- event-driven: ₹9,222.87 / ₹-10,837.13 / ₹-30,897.13 / ₹-71,017.13 net P&L for 0 / 0.5 / 1 / 2 points.

## ATM / timing diagnostics
- Event median signal time: 09:16 IST.
- Event median ATM distance: 48.3 points / 0.189%.
- 90th percentile ATM distance: 306.65 points / 1.212%.
- Maximum ATM distance: 844.35 points / 3.617%.

## Interpretation
The event arm does not improve the frozen strategy. On paired dates it is unchanged from the fixed 09:15 control; the economic change comes from the 44 extra trades admitted by waiting for CBR to become valid later. Those incremental trades have PF below 1 and are negative after even modest slippage.

P9 therefore stops without promoting event-driven timing.

## Source-quality note
The first primary public source failed P9 source-quality QC because the far-expiry intraday panel was too sparse to reconstruct a defensible ATM strike. This secondary source is the accepted P9 analytical source for the OOS timing comparison, while still carrying the usual public-data and bid/ask limitations.