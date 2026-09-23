# P8 Final Research Conclusion — NIFTY 4-Leg Calendar

## Phase outcome

P8 is COMPLETE. The single P7 candidate entry gate was frozen before scoring:

\[
\text{Calendar Balance} =
\frac{\text{Far CE entry}/\text{Near CE entry}}
{\text{Far PE entry}/\text{Near PE entry}}
\le 1.20
\]

No alternative threshold, additional indicator, stop, target, or post-entry adjustment was searched in P8.

## Unseen temporal validation

Development sample: 2022-2024.

Validation sample: post-2024 cycles beginning 1-Jan-2025, using the frozen independent NSE F&O mirror snapshot and independent NIFTY spot OPEN observations.

- Scheduled cycles: 88
- Executable cycles: 86
- Non-executable: 2
- Fixed-gate trades: 42

The two non-executable cycles were excluded because the reconstructed secondary source could not identify a common executable strike.

## Gross OOS result

| Metric | Frozen P6 baseline | Frozen P7 gate |
|---|---:|---:|
| Trades | 86 | 42 |
| Gross P&L | ₹-24,361.25 | ₹126,460.50 |
| Win rate | 53.49% | 76.19% |
| Profit factor | 0.883 | 5.115 |
| Max drawdown | ₹90,742.50 | ₹13,406.25 |
| Worst trade | ₹-21,513.75 | ₹-12,502.75 |

Circular 3-trade-block bootstrap 95% interval for cumulative gross P&L:
- P6 baseline: ₹-176,463.88 to ₹117,347.48.
- P7 fixed gate: ₹65,611.61 to ₹196,757.32.

## Loss filtering

- Baseline losing cycles: 40.
- Losses skipped by the fixed gate: 30 (75.0%).
- Winning cycles skipped: 14.
- Residual gate-pass losses: 10.
- Aggregate residual gate-pass loss: ₹-30,730.50.

Residual-loss structure:
- 7/10 were near-structure adverse while the far structure was favorable enough to offset part of the loss.
- 3/10 were far-structure adverse while the near structure was favorable.
- 0/10 had both aggregate near and far P&L negative.

The largest residual loss was 11-Mar-2026: calendar balance 1.1160 and gross P&L ₹-12,502.75. Its near contribution was +₹46,878 while its far contribution was -₹59,380.75. This shows that the P7 gate reduces one historical failure mode but does not isolate the complete risk mechanism.

## Cost and slippage validation

Primary stress case:
- ₹20 Paytm Money brokerage per executed order.
- Eight option executions per completed cycle.
- Period-correct option-sale STT.
- 0.003% stamp duty on option buys.
- 0.0001% SEBI turnover fee.
- 18% GST on brokerage, exchange and SEBI charges.
- 0.05% exchange-charge stress.
- Adverse slippage of 0, 0.5, 1 and 2 index points per execution.

| Slippage | P6 net P&L | P7 fixed-gate net P&L |
|---:|---:|---:|
| 0 points | ₹-55,347.65 | ₹111,664.41 |
| 0.5 points | ₹-79,687.65 | ₹99,824.41 |
| 1 point | ₹-104,027.65 | ₹87,984.41 |
| 2 points | ₹-152,707.65 | ₹64,304.41 |

At 2-point adverse slippage, the fixed gate's cumulative net P&L remains positive. Its cost-adjusted maximum drawdown is approximately ₹19,270.53.

An additional current-rate exchange-charge sensitivity using 0.03503% instead of the 0.05% stress gave approximately:
- 0-point slippage: ₹112,684.23
- 2-point slippage: ₹65,324.23

This sensitivity is informational rather than the primary historical charge model.

## Time-regime diagnostics

| Period | Fixed-gate trades | Gross P&L | Net at 2-point slippage |
|---|---:|---:|---:|
| 2025 | 24 | ₹80,063.50 | ₹43,272.86 |
| 2026 | 18 | ₹46,397.00 | ₹21,031.55 |

The fixed gate was positive in both the Thursday-expiry regime and the Tuesday-expiry regime:
- Thursday regime: 17 trades, gross ₹71,471.25.
- Tuesday regime: 25 trades, gross ₹54,989.25.

This matters because the NSE weekly NIFTY expiry regime changed from Thursday to Tuesday beginning with the 2-Sep-2025 weekly expiry. P8 did not treat that rule change as a tuning variable; it was an exogenous contract-calendar rule.

## Scientific inference

The pre-frozen 1.20 gate has passed one genuine temporal holdout that is materially different from the 2022-2024 development sample. The evidence therefore supports carrying the fixed candidate into another research phase.

This is not evidence that the strategy is ready for live capital. The remaining uncertainty includes:
- only 42 gate-pass trades in the holdout;
- daily OPEN/CLOSE data do not reconstruct actual bid/ask execution paths;
- no market-impact/order-book model;
- independent spot OPEN can differ slightly from exchange timestamp conventions;
- the NSE F&O mirror is a redistribution of exchange archives;
- the available validation snapshot ends at the mirror boundary rather than providing a live forward track.

## Phase conclusion

**P8 conclusion: SUPPORTED FOR FURTHER RESEARCH, NOT PROMOTED TO LIVE TRADING.**

No additional entry criterion is selected in P8.

## Proposed P9 direction

P9 should be a fixed-rule forward/paper-execution validation:
1. keep the calendar-balance threshold exactly at 1.20;
2. do not use the new observations to retune the threshold;
3. capture timestamped bid/ask or executable quote evidence where available;
4. record actual brokerage, exchange/statutory costs, spread and slippage;
5. monitor residual loss mechanism, especially far-leg deterioration;
6. publish a pre-registered decision rule for whether the candidate advances toward implementation.

Any new loss filter or replacement threshold belongs to a separate development phase and must receive its own unseen validation set.
