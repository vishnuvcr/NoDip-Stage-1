# P9 Final Research Conclusion — Event-Driven Intraday Entry Timing

## Result
P9 tested whether the frozen CBR<=1.20 four-leg strategy should enter at the first intraday qualifying timestamp instead of the frozen 09:15 IST entry. The event-driven variant is not promoted.

## Source validation
The primary public intraday source was rejected because far-expiry coverage was too sparse. On 2026-04-01 it had only 903 far-expiry rows for the session and the apparent common-strike trade selected 20,500 while NIFTY was around 22,900.

The secondary Rissin/Upstox 1-minute source was tested over the same 86-cycle post-2024 OOS population. NSE specifies a 50-point strike interval for NIFTY weekly/monthly contracts; the deterministic ATM QC therefore required the common strike to be within 25 points of contemporaneous spot.

## Secondary OOS after ATM QC

| Metric | Fixed source diagnostic | Event-driven |
|---|---:|---:|
| Executable trades | 14 | 65 |
| Gross P&L | ₹19,737.25 | ₹43,607.25 |
| Win rate | 78.57% | 64.62% |
| Profit factor | 5.613 | 1.755 |
| Gross max drawdown | ₹2,180.75 | ₹33,429.00 |
| Worst trade | ₹-2,180.75 | ₹-9,984.75 |
| Net at 0-point slippage | ₹13,418.43 | ₹17,798.70 |
| Net at 0.5-point slippage | ₹9,458.43 | ₹-781.30 |
| Net at 1-point slippage | ₹5,498.43 | ₹-19,361.30 |
| Net at 2-point slippage | ₹-2,421.57 | ₹-56,521.30 |

The 14-trade fixed source control is only a source-completeness diagnostic; the canonical fixed-time benchmark remains the P8 daily ledger.

## Canonical P8 paired comparison
- 33 event trades occurred on dates that passed the frozen gate at 09:15.
- Event gross on those 33 dates: ₹42,312.50.
- Canonical P8 fixed-gate gross on the same dates: ₹104,231.75.
- Mean event-minus-fixed difference: ₹-1,876.34 per date; median ₹-746.25.
- Event was higher on 12/33 dates and lower on 21/33.
- Deterministic 20,000-resample bootstrap 95% CI for the mean paired difference: approximately ₹-3,990.63 to ₹-347.55.
- 32 dates failed the 09:15 gate but qualified later; those event trades produced ₹1,294.75 gross and PF 1.029.

## Latest-entry sensitivity
| Latest signal | Trades | Gross P&L | Net at 0.5 pt | Net at 1 pt | Net at 2 pt |
|---|---:|---:|---:|---:|---:|
| 15:00 | 63 | ₹37,787.00 | ₹-5,170.99 | ₹-23,190.99 | ₹-59,230.99 |
| 15:15 | 64 | ₹38,465.75 | ₹-5,126.99 | ₹-23,446.99 | ₹-60,086.99 |
| 15:30 | 65 | ₹43,607.25 | ₹-781.30 | ₹-19,361.30 | ₹-56,521.30 |
| 15:40 | 65 | ₹43,607.25 | ₹-781.30 | ₹-19,361.30 | ₹-56,521.30 |

No later cutoff restored positive net P&L at 0.5-point adverse slippage. The 15:30 and 15:40 results are identical.

## Conclusion
P9 does not support replacing the fixed 09:15 entry with first-qualifying intraday entry. The threshold, four-leg structure and exit remain frozen. P10 should return to the fixed rule and use forward/paper execution with timestamped executable quotes, observed spread/slippage and actual costs.

## Limitations
- Public historical sources are OHLC-based rather than reliable historical bid/ask replay.
- Secondary source reconstruction has 9 no-panel cycles and 3 event no-exit rows.
- The event-vs-P8 comparison is source-aware rather than identical-feed replay.