# P12 Far-Expiry Selection Research Report

## Frozen structure
- Entry session: D+1 after previous listed expiry.
- Entry time: 09:15 IST.
- Near expiry: next listed expiry.
- Candidate far expiries: F+1 to F+4 subsequent listed expiries.
- Position: short near CE, long near PE, long far CE, short far PE.
- Same ATM strike across candidates, chosen from the near-expiry 09:15 strike closest to spot; 25-point ATM QC.
- Exit: near-expiry close.

## Research-status caveat
- The 2025+ evaluation period was already exposed in P10, so P12 is exploratory rather than confirmatory fresh OOS validation. A future fresh holdout is still required before any live/paper promotion.

## Primary adaptive selection criterion
- Eligibility: same ATM strike, all four entry legs positive, positive entry volume.
- Score = (near CE - near PE + far PE - far CE) / spot open.
- Select the far expiry with the highest score.
- Score uses entry data only; no future close/P&L is used.

## Results
- F+1 DEVELOPMENT: 153 trades, gross ₹38,051.25, win 62.1%, PF 1.359, DD ₹17,781.25, net@2pt ₹-110,409.11.
- F+2 DEVELOPMENT: 152 trades, gross ₹57,793.75, win 59.9%, PF 1.403, DD ₹43,681.25, net@2pt ₹-91,796.26.
- F+3 DEVELOPMENT: 129 trades, gross ₹28,908.75, win 57.4%, PF 1.229, DD ₹46,613.75, net@2pt ₹-98,698.54.
- F+4 DEVELOPMENT: 75 trades, gross ₹50,743.75, win 54.7%, PF 1.630, DD ₹24,567.50, net@2pt ₹-24,389.77.
- ADAPTIVE DEVELOPMENT: 155 trades, gross ₹143,106.25, win 70.3%, PF 2.869, DD ₹13,635.00, net@2pt ₹-8,325.28.
- F+1 OOS: 72 trades, gross ₹29,542.50, win 52.8%, PF 1.321, DD ₹47,520.00, net@2pt ₹-76,675.51.
- F+2 OOS: 73 trades, gross ₹-23,165.50, win 50.7%, PF 0.836, DD ₹77,988.75, net@2pt ₹-132,050.98.
- F+3 OOS: 64 trades, gross ₹33,141.75, win 54.7%, PF 1.288, DD ₹53,985.00, net@2pt ₹-62,956.75.
- F+4 OOS: 42 trades, gross ₹90,236.75, win 69.0%, PF 2.373, DD ₹34,368.75, net@2pt ₹26,958.30.
- ADAPTIVE OOS: 77 trades, gross ₹144,277.50, win 58.4%, PF 2.763, DD ₹36,963.75, net@2pt ₹30,311.14.

## Adaptive selection frequency
- DEVELOPMENT: F+1=106, F+2=25, F+3=16, F+4=8.
- OOS: F+1=59, F+2=8, F+3=6, F+4=4.

## Cost sensitivity
| sample      | strategy   |   slippage_points |   net_pnl_inr |
|:------------|:-----------|------------------:|--------------:|
| DEVELOPMENT | F+1        |               0   |      -1409.11 |
| DEVELOPMENT | F+1        |               0.5 |     -28659.1  |
| DEVELOPMENT | F+1        |               1   |     -55909.1  |
| DEVELOPMENT | F+1        |               2   |    -110409    |
| DEVELOPMENT | F+2        |               0   |      17003.7  |
| DEVELOPMENT | F+2        |               0.5 |     -10196.3  |
| DEVELOPMENT | F+2        |               1   |     -37396.3  |
| DEVELOPMENT | F+2        |               2   |     -91796.3  |
| DEVELOPMENT | F+3        |               0   |      -6698.54 |
| DEVELOPMENT | F+3        |               0.5 |     -29698.5  |
| DEVELOPMENT | F+3        |               1   |     -52698.5  |
| DEVELOPMENT | F+3        |               2   |     -98698.5  |
| DEVELOPMENT | F+4        |               0   |      29610.2  |
| DEVELOPMENT | F+4        |               0.5 |      16110.2  |
| DEVELOPMENT | F+4        |               1   |       2610.23 |
| DEVELOPMENT | F+4        |               2   |     -24389.8  |
| DEVELOPMENT | ADAPTIVE   |               0   |     102275    |
| DEVELOPMENT | ADAPTIVE   |               0.5 |      74624.7  |
| DEVELOPMENT | ADAPTIVE   |               1   |      46974.7  |
| DEVELOPMENT | ADAPTIVE   |               2   |      -8325.28 |
| OOS         | F+1        |               0   |       6124.49 |
| OOS         | F+1        |               0.5 |     -14575.5  |
| OOS         | F+1        |               1   |     -35275.5  |
| OOS         | F+1        |               2   |     -76675.5  |
| OOS         | F+2        |               0   |     -48211    |
| OOS         | F+2        |               0.5 |     -69171    |
| OOS         | F+2        |               1   |     -90131    |
| OOS         | F+2        |               2   |    -132051    |
| OOS         | F+3        |               0   |      10323.2  |
| OOS         | F+3        |               0.5 |      -7996.75 |
| OOS         | F+3        |               1   |     -26316.8  |
| OOS         | F+3        |               2   |     -62956.8  |
| OOS         | F+4        |               0   |      75118.3  |
| OOS         | F+4        |               0.5 |      63078.3  |
| OOS         | F+4        |               1   |      51038.3  |
| OOS         | F+4        |               2   |      26958.3  |
| OOS         | ADAPTIVE   |               0   |     118631    |
| OOS         | ADAPTIVE   |               0.5 |      96551.1  |
| OOS         | ADAPTIVE   |               1   |      74471.1  |
| OOS         | ADAPTIVE   |               2   |      30311.1  |

## Adaptive paired comparisons vs fixed horizons
| sample      | comparison      |   paired_cycles |   mean_delta_inr |   median_delta_inr |   adaptive_higher |   fixed_higher |   same |
|:------------|:----------------|----------------:|-----------------:|-------------------:|------------------:|---------------:|-------:|
| DEVELOPMENT | ADAPTIVE_vs_F+1 |             153 |          664.542 |              0     |                45 |              2 |    106 |
| DEVELOPMENT | ADAPTIVE_vs_F+2 |             152 |          525.345 |             22.5   |                77 |             50 |     25 |
| DEVELOPMENT | ADAPTIVE_vs_F+3 |             129 |          659.496 |            112.5   |                70 |             43 |     16 |
| DEVELOPMENT | ADAPTIVE_vs_F+4 |              75 |          494.717 |            257.5   |                43 |             24 |      8 |
| OOS         | ADAPTIVE_vs_F+1 |              72 |         1463.86  |              0     |                13 |              0 |     59 |
| OOS         | ADAPTIVE_vs_F+2 |              73 |         2263.15  |            776.25  |                45 |             20 |      8 |
| OOS         | ADAPTIVE_vs_F+3 |              64 |         1627.28  |            309.375 |                35 |             23 |      6 |
| OOS         | ADAPTIVE_vs_F+4 |              42 |          834.262 |             60     |                21 |             17 |      4 |

## Bootstrap intervals
- F+1 DEVELOPMENT: total P&L bootstrap 95% CI ₹-20,483.34 to ₹94,692.59.
- F+2 DEVELOPMENT: total P&L bootstrap 95% CI ₹-37,470.16 to ₹147,153.06.
- F+3 DEVELOPMENT: total P&L bootstrap 95% CI ₹-57,988.75 to ₹113,032.41.
- F+4 DEVELOPMENT: total P&L bootstrap 95% CI ₹-28,655.00 to ₹136,432.13.
- ADAPTIVE DEVELOPMENT: total P&L bootstrap 95% CI ₹77,127.16 to ₹205,456.38.
- F+1 OOS: total P&L bootstrap 95% CI ₹-42,315.04 to ₹97,093.18.
- F+2 OOS: total P&L bootstrap 95% CI ₹-100,470.18 to ₹53,859.21.
- F+3 OOS: total P&L bootstrap 95% CI ₹-62,511.91 to ₹138,191.02.
- F+4 OOS: total P&L bootstrap 95% CI ₹-5,393.01 to ₹186,877.71.
- ADAPTIVE OOS: total P&L bootstrap 95% CI ₹50,163.14 to ₹241,344.93.

## Limitations
- The public daily source provides end-of-day option OHLCV; historical bid/ask quotes are not available in this source.
- Modeled slippage/costs are sensitivities, not observed Paytm Money fills.
- Adaptive selection is a pre-registered entry-time rule; it is not optimized against OOS P&L.

## Phase conclusion
- P12 is closed after fixed F+1/F+2/F+3/F+4 comparison and the frozen adaptive selector. No additional far-expiry horizons or score weights are searched in this phase.
