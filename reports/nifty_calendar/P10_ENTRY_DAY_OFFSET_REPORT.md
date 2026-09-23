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

- D-1: 1 trades / 88 cycles; gross ₹4,511.25; net at 0/0.5/1/2pt = ₹4,136.02 / ₹3,836.02 / ₹3,536.02 / ₹2,936.02; PF inf; drawdown ₹0.00.
- D0: 2 trades / 88 cycles; gross ₹3,296.25; net at 0/0.5/1/2pt = ₹2,554.07 / ₹1,954.07 / ₹1,354.07 / ₹154.07; PF 2.487; drawdown ₹0.00.
- D+1: 2 trades / 88 cycles; gross ₹2,133.75; net at 0/0.5/1/2pt = ₹1,378.14 / ₹778.14 / ₹178.14 / ₹-1,021.86; PF 2.371; drawdown ₹0.00.
- D+2: 2 trades / 88 cycles; gross ₹5,118.75; net at 0/0.5/1/2pt = ₹4,383.17 / ₹3,783.17 / ₹3,183.17 / ₹1,983.17; PF inf; drawdown ₹0.00.
- D+3: 2 trades / 88 cycles; gross ₹-5,081.25; net at 0/0.5/1/2pt = ₹-5,820.76 / ₹-6,420.76 / ₹-7,020.76 / ₹-8,220.76; PF 0.182; drawdown ₹0.00.
- D+4: 2 trades / 88 cycles; gross ₹4,556.25; net at 0/0.5/1/2pt = ₹3,812.62 / ₹3,212.62 / ₹2,612.62 / ₹1,412.62; PF inf; drawdown ₹0.00.
- D+5: 0 trades / 88 cycles; gross ₹0.00; net at 0/0.5/1/2pt = ₹0.00 / ₹0.00 / ₹0.00 / ₹0.00; PF inf; drawdown ₹0.00.

## Source
- Rissin historical_daily/NIFTY annual Parquet, derived from NSE F&O bhavcopy; NIFTY opening spot from Yahoo daily chart.

## Selection rule for any future promotion
- No OOS result is used to choose a winner in this phase. If a single offset is later promoted, it must be selected from the 2022-2024 development sample under a pre-registered rule and then validated on an untouched later period.

## Cost model
- Same P8 historical stress model: ₹20/order, eight option executions, statutory charges, 0.05% exchange-charge stress and 0/0.5/1/2 point adverse slippage per execution.
- Cost outputs are modeled and are not claims of realized Paytm Money fills.

## Research conclusion status
- This run is a seven-offset timing screen. It does not alter the canonical P8/P9 rules until a development-selected offset survives unseen validation and execution-cost stress.
