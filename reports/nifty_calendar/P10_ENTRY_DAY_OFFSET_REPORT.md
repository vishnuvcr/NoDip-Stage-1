# P10 Entry-Day Offset Research

## Frozen design
- Entry time: 09:15 IST open.
- Gate: CBR <= 1.20; no threshold re-optimization.
- Four-leg structure: buy near PE, sell near CE, buy far CE, sell far PE.
- Near/far expiries remain those of the underlying canonical cycle; exit at near-expiry close.
- Day offsets are defined on NSE trading sessions: D-1 is the session immediately before the previous expiry, D0 is the previous-expiry session, and D+1..D+5 are subsequent trading sessions.
- A candidate after the near-expiry date is marked AFTER_NEAR_EXPIRY and is not a trade.
- Development sample: 2022-2024. OOS sample: 2025 onward.

## Development screen (informational; OOS not used to choose a candidate)

- D-1: 75 trades / 134 cycles; gross ₹161,935.00; net at 2pt ₹84,118.48; PF 4.626; coverage 94.0%.
- D+2: 75 trades / 134 cycles; gross ₹151,540.00; net at 2pt ₹75,865.26; PF 7.540; coverage 96.3%.
- D+1: 79 trades / 134 cycles; gross ₹128,382.50; net at 2pt ₹47,835.40; PF 9.078; coverage 96.3%.
- D0: 75 trades / 134 cycles; gross ₹101,857.50; net at 2pt ₹25,149.05; PF 3.614; coverage 95.5%.
- D+4: 57 trades / 134 cycles; gross ₹60,158.75; net at 2pt ₹2,467.51; PF 3.309; coverage 97.0%.
- D+3: 56 trades / 134 cycles; gross ₹53,945.00; net at 2pt ₹-3,508.25; PF 3.264; coverage 96.3%.
- D+5: 40 trades / 134 cycles; gross ₹21,531.25; net at 2pt ₹-19,525.52; PF 1.732; coverage 68.7%.

## OOS results — all seven offsets are reported without post-hoc selection

- D-1: 44 trades / 88 cycles; gross ₹90,808.25; net at 0/0.5/1/2pt = ₹74,246.23 / ₹61,646.23 / ₹49,046.23 / ₹23,846.23; PF 2.922; drawdown ₹30,663.75.
- D0: 42 trades / 88 cycles; gross ₹133,757.75; net at 0/0.5/1/2pt = ₹117,810.36 / ₹105,830.36 / ₹93,850.36 / ₹69,890.36; PF 11.925; drawdown ₹4,143.75.
- D+1: 36 trades / 88 cycles; gross ₹99,992.75; net at 0/0.5/1/2pt = ₹87,251.90 / ₹76,971.90 / ₹66,691.90 / ₹46,131.90; PF 4.540; drawdown ₹13,406.25.
- D+2: 44 trades / 88 cycles; gross ₹129,107.75; net at 0/0.5/1/2pt = ₹113,707.53 / ₹101,127.53 / ₹88,547.53 / ₹63,387.53; PF 8.100; drawdown ₹9,213.75.
- D+3: 36 trades / 88 cycles; gross ₹50,454.25; net at 0/0.5/1/2pt = ₹38,109.18 / ₹27,869.18 / ₹17,629.18 / ₹-2,850.82; PF 1.993; drawdown ₹18,667.50.
- D+4: 33 trades / 88 cycles; gross ₹80,699.00; net at 0/0.5/1/2pt = ₹69,517.50 / ₹60,177.50 / ₹50,837.50 / ₹32,157.50; PF 3.834; drawdown ₹11,388.75.
- D+5: 19 trades / 88 cycles; gross ₹17,240.00; net at 0/0.5/1/2pt = ₹11,245.22 / ₹5,865.22 / ₹485.22 / ₹-10,274.78; PF 2.359; drawdown ₹6,685.25.

## Source
- Rissin historical_daily/NIFTY annual Parquet, derived from NSE F&O bhavcopy; NIFTY opening spot from Yahoo daily chart.

## Selection rule for any future promotion
- No OOS result is used to choose a winner in this phase. If a single offset is later promoted, it must be selected from the 2022-2024 development sample under a pre-registered rule and then validated on an untouched later period.

## Cost model
- Same P8 historical stress model: ₹20/order, eight option executions, statutory charges, 0.05% exchange-charge stress and 0/0.5/1/2 point adverse slippage per execution.
- Cost outputs are modeled and are not claims of realized Paytm Money fills.

## Research conclusion status
- This run is a seven-offset timing screen. It does not alter the canonical P8/P9 rules until a development-selected offset survives unseen validation and execution-cost stress.

## OOS paired bootstrap versus D+1

- D-1: mean ₹-104.37; 95% CI ₹-1,403.35 to ₹1,114.14.
- D0: mean ₹383.69; 95% CI ₹-797.17 to ₹1,480.94.
- D+2: mean ₹330.85; 95% CI ₹-445.32 to ₹1,099.05.
- D+3: mean ₹-562.94; 95% CI ₹-1,480.49 to ₹308.59.
- D+4: mean ₹-219.25; 95% CI ₹-1,179.47 to ₹716.87.
- D+5: mean ₹-940.37; 95% CI ₹-1,975.86 to ₹-69.96.

The bootstrap is an unadjusted seven-comparison robustness analysis, not a confirmatory multiple-testing procedure.

## Final status

P10 COMPLETE. D0 and D+2 remain development-only candidates for a separate selection and fresh validation phase. No offset is promoted directly from this OOS screen.
