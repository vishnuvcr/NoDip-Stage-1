# NIFTY 4-Leg Calendar — P5 Robustness and Cost Analysis (2022-2024)

## Status

Preliminary robustness phase completed for the available 2022-2024 trade ledger. The strategy definition was not changed.

## Backtest coverage

The engine generated 138 distinct NIFTY expiry dates and evaluated 134 possible strategy cycles under the frozen four-expiry construction.

- Valid executable cycles: 59
- Rejected cycles: 75
- Coverage: 59 / 134 = 44.0%

Rejection audit from the executed run:
- No common executable strike across near/far expiries: 9
- Missing entry leg: 62
- Missing exit leg: 4

This is the principal limitation of this dataset. The 59-trade result is therefore a result on the subset of cycles for which all four legs were present with valid entry and exit observations, not a complete 2022-2024 population estimate. Missingness may be non-random.

## Gross result

- 59 valid trades
- Gross P&L: ₹52,827.50
- Mean trade: ₹895.38
- Median trade: ₹866.25
- Win rate: 64.41%
- Profit factor: 2.549
- Maximum drawdown: ₹5,650.00
- Best trade: ₹20,081.25
- Worst trade: -₹5,650.00

Annual gross P&L:
- 2022: ₹5,045.00 across 9 trades
- 2023: ₹25,677.50 across 29 trades
- 2024: ₹22,105.00 across 21 trades

The circular 3-trade block bootstrap used by the workflow produced a 95% interval of ₹13,151.84 to ₹100,043.59 for total P&L.

## Exact slippage sensitivity

For each trade, slippage is charged separately to all eight executions using the historical lot size of the relevant leg. This replaces the earlier common-average-lot approximation.

| Adverse slippage per execution | Total P&L (₹) | Win rate | Max drawdown (₹) |
|---:|---:|---:|---:|
| 0.00 points | 52,827.50 | 64.41% | -5,650.00 |
| 0.25 points | 47,577.50 | 62.71% | -6,067.50 |
| 0.50 points | 42,327.50 | 62.71% | -7,067.50 |
| 1.00 point | 31,827.50 | 59.32% | -9,067.50 |
| 2.00 points | 10,827.50 | 54.24% | -13,960.00 |

## Documented Paytm Money / statutory cost layer

Paytm Money's F&O FAQ states ₹10 brokerage per executed order, so eight executions imply ₹80 brokerage per completed strategy cycle. Paytm Money's pricing page states statutory, regulatory and exchange charges are levied at actuals. The historical Paytm Money STT update documents the option-sale STT increase from 0.0625% to 0.1% effective 1-Oct-2024; the whole 2022-2024 sample in this study ends before that change, so 0.0625% is used for every sale in this sample.

The known statutory/brokerage layer used here is:
- Brokerage: ₹10 × 8 = ₹80 per trade
- STT: 0.0625% of option premium sold
- Stamp duty: 0.003% of option premium bought
- SEBI turnover fee: 0.0001% of premium turnover
- GST: 18% on brokerage + SEBI fee
- Exchange transaction charges: not hard-coded as a historical Paytm-specific rate because Paytm's public pricing page states exchange charges are levied at actuals; instead, an exchange-charge sensitivity is shown below.

Known costs across 59 trades, excluding exchange transaction charges and GST on those exchange charges: approximately ₹7,060.36.

## Exchange-charge sensitivity

To avoid inventing a historical Paytm pass-through rate, three premium-turnover sensitivities are shown: 0.03503%, 0.05000%, and 0.05300%. These are sensitivity assumptions rather than asserted historical Paytm contract-note rates.

| Exchange-charge assumption | Net P&L after brokerage, statutory charges, GST and exchange-charge sensitivity (₹) |
|---:|---:|
| 0.03503% of premium turnover | 43,912.11 |
| 0.05000% of premium turnover | 43,119.36 |
| 0.05300% of premium turnover | 42,960.49 |

## Combined slippage + cost sensitivity

Using 0.05000% exchange-charge sensitivity:

| Adverse slippage / execution | Net P&L (₹) |
|---:|---:|
| 0.00 points | 43,119.36 |
| 0.25 points | 37,869.36 |
| 0.50 points | 32,619.36 |
| 1.00 point | 22,119.36 |
| 2.00 points | 1,119.36 |

## Interpretation

Within the 59 valid executable cycles, gross P&L remains positive after the documented brokerage/statutory layer and remains positive under a 1-point adverse-slippage assumption plus a 0.05% exchange-charge sensitivity.

The result becomes approximately flat at a 2-point adverse-slippage assumption after costs.

The principal uncertainty is not the arithmetic of the 59 trades. It is the 44.0% cycle coverage: 75 of 134 possible cycles were excluded because the public data did not provide a complete executable four-leg observation. Therefore this should be treated as a conditional historical result, not yet as a complete estimate of strategy performance over the full period.

## Next verification step

P5 should remain open until the 75 rejected cycles are independently audited against another historical option source and the exact Paytm Money exchange-charge pass-through applicable to each historical period can be reconstructed. No parameter tuning should be performed from this sample.
