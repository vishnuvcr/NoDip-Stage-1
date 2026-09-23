# P10 Final Research Conclusion — Entry-Day Offset Screen

## Research question
Does keeping the 09:15 IST entry and CBR<=1.20 gate fixed, while changing only the trading session relative to the previous expiry, improve the four-leg NIFTY calendar strategy?

## Protocol
- Seven pre-registered trading-session offsets: D-1, D0, D+1, D+2, D+3, D+4, D+5.
- Entry: 09:15 IST.
- Gate: CBR<=1.20.
- Four legs unchanged.
- Common ATM strike selected from contemporaneous opening spot.
- Exit: near-expiry close.
- Historical lot sizes preserved.
- Same brokerage/statutory/exchange-stress/slippage model as P8.
- Development: 2022-2024.
- Unseen OOS: 2025 onward.

## Development results
| Offset | Trades | Gross P&L | PF | Net at 2pt slippage |
|---|---:|---:|---:|---:|
| D-1 | 75 | ₹161,935.00 | 4.626 | ₹84,118.48 |
| D0 | 75 | ₹101,857.50 | 3.614 | ₹25,149.05 |
| D+1 | 79 | ₹128,382.50 | 9.078 | ₹47,835.40 |
| D+2 | 75 | ₹151,540.00 | 7.540 | ₹75,865.26 |
| D+3 | 56 | ₹53,945.00 | 3.264 | ₹-3,508.25 |
| D+4 | 57 | ₹60,158.75 | 3.309 | ₹2,467.51 |
| D+5 | 40 | ₹21,531.25 | 1.732 | ₹-19,525.52 |

## Unseen OOS results
| Offset | Trades | Gross P&L | Win rate | PF | Max DD | Net at 0.5pt | Net at 1pt | Net at 2pt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D-1 | 44 | ₹90,808.25 | 72.73% | 2.922 | ₹30,663.75 | ₹61,646.23 | ₹49,046.23 | ₹23,846.23 |
| D0 | 42 | ₹133,757.75 | 80.95% | 11.925 | ₹4,143.75 | ₹105,830.36 | ₹93,850.36 | ₹69,890.36 |
| D+1 | 36 | ₹99,992.75 | 72.22% | 4.540 | ₹13,406.25 | ₹76,971.90 | ₹66,691.90 | ₹46,131.90 |
| D+2 | 44 | ₹129,107.75 | 75.00% | 8.100 | ₹9,213.75 | ₹101,127.53 | ₹88,547.53 | ₹63,387.53 |
| D+3 | 36 | ₹50,454.25 | 55.56% | 1.993 | ₹18,667.50 | ₹27,869.18 | ₹17,629.18 | ₹-2,850.82 |
| D+4 | 33 | ₹80,699.00 | 72.73% | 3.834 | ₹11,388.75 | ₹60,177.50 | ₹50,837.50 | ₹32,157.50 |
| D+5 | 19 | ₹17,240.00 | 68.42% | 2.359 | ₹6,685.25 | ₹5,865.22 | ₹485.22 | ₹-10,274.78 |

## OOS paired robustness versus D+1
- D-1 mean difference: ₹-104.37; bootstrap 95% CI ₹-1,403.35 to ₹1,114.14.
- D0 mean difference: ₹383.69; bootstrap 95% CI ₹-797.17 to ₹1,480.94.
- D+2 mean difference: ₹330.85; bootstrap 95% CI ₹-445.32 to ₹1,099.05.
- D+3 mean difference: ₹-562.94; bootstrap 95% CI ₹-1,480.49 to ₹308.59.
- D+4 mean difference: ₹-219.25; bootstrap 95% CI ₹-1,179.47 to ₹716.87.
- D+5 mean difference: ₹-940.37; bootstrap 95% CI ₹-1,975.86 to ₹-69.96.

## Inference
The screen shows a clear separation between the earlier offsets and the later tail of the expiry week in economic performance, but the OOS paired evidence does not statistically distinguish D0 or D+2 from the canonical D+1 at the unadjusted bootstrap level. D+5 is the only offset in this screen with a paired bootstrap interval entirely below D+1.

D0 and D+2 also show the largest raw OOS net P&L under 2-point adverse slippage, while D+3 and D+5 become negative at the same stress. These results are descriptive because the seven offsets were all examined on the same OOS period.

## Data-quality note
The corrected ledger contains 88 distinct OOS cycles with 88 distinct previous-expiry dates. Executable-cycle coverage is 76/88 for D-1/D0/D+1/D+2/D+3, 74/88 for D+4 and 54/88 for D+5. Non-executable observations are retained rather than extrapolated.

## Conclusion
P10 does not justify promoting an alternative entry day directly from the seven-offset OOS screen. D0 and D+2 are the strongest raw candidates for a **development-only** next step, but neither is statistically separated from D+1 in the paired OOS bootstrap. D+5 shows a negative paired result and weaker cost robustness.

## Next phase
Freeze the P10 screen. Any candidate offset must be chosen using a pre-registered development-only rule from 2022-2024 and then tested on a fresh unseen temporal holdout before paper/live execution. P11 remains forward/paper validation, not live deployment.

Source: Rissin `nse-options-intraday` daily NIFTY Parquet, whose dataset card states that its historical daily track is derived from NSE F&O bhavcopy and covers NIFTY from 2001 onward. citeturn399512search0turn399512search1