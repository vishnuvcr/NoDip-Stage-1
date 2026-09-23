# P7 Loss-Trades Audit — NIFTY 4-Leg Calendar — 2022-2024

## Scope
- Strict frozen-protocol trades audited: 84
- Losing trades: 32
- Non-losing trades: 52
- Gross P&L: ₹83,030.00
- Total loss from losing trades: ₹-42,747.50
- Average losing trade: ₹-1,335.86
- Median losing trade: ₹-938.75

## Loss attribution by leg
- Near PE contribution across losing trades: ₹-79,366.25
- Near CE contribution across losing trades: ₹-91,253.75
- Far CE contribution across losing trades: ₹52,385.00
- Far PE contribution across losing trades: ₹75,487.50

The near-expiry legs are the main loss source: their combined contribution is materially negative, while the far legs provide offsetting gains but do not fully absorb the front-week losses.

## Loss-signature audit
- bearish-like far-week adverse signature: 6 trades; total loss ₹-1,832.50; average ₹-305.42.
- bullish-like front-week adverse signature: 19 trades; total loss ₹-30,827.50; average ₹-1,622.50.
- mixed signature: 7 trades; total loss ₹-10,087.50; average ₹-1,441.07.

The largest recurring pattern is the bullish-like front-week adverse signature: 19 of 32 losing trades (59.4%) and ₹30,827.50 of absolute loss (72.1%). This is an inferred option-payoff signature, not a direct observation of intraday NIFTY path.

## Loss severity concentration
- Losses ≤ -₹500: 20 trades, 94.6% of total absolute loss.
- Losses ≤ -₹1,000: 14 trades, 83.1% of total absolute loss.
- Losses ≤ -₹1,500: 11 trades, 75.2% of total absolute loss.
- Losses ≤ -₹2,000: 9 trades, 67.4% of total absolute loss.
- Losses ≤ -₹2,500: 5 trades, 45.9% of total absolute loss.
- Losses ≤ -₹3,000: 4 trades, 39.9% of total absolute loss.

## Entry-state differences between losses and wins
- Mean initial net debit: losses ₹81.33; non-losses ₹51.45.
- Mean near-call/far-call ratio: losses 0.409; non-losses 0.455.
- Mean near-put/far-put ratio: losses 0.529; non-losses 0.475.

These are associations in the historical sample, not causal estimates.

## Exploratory improvement tests

The candidate filters below are deliberately simple and are not allowed to overwrite the frozen result:
- initial net debit ≤ 80 points;
- near-call/far-call premium ratio ≥ 0.45;
- near-put/far-put premium ratio ≤ 0.55;
- combined call/put balance filter using both ratio conditions.

The combined balance filter reduces the strict sample to a small subset. Its improved win rate and drawdown must therefore be weighed against the large reduction in trade count and the risk of in-sample selection bias.

## Practical improvement path
1. First priority: improve execution measurement, not the payoff formula. The major losses originate in front-week option repricing, so synchronized bid/ask or tick data are required to know whether entry/exit slippage and transient adverse moves are larger than the daily-bar model indicates.
2. Second: investigate a pre-trade term-structure balance filter using the two premium-ratio diagnostics. Treat it as a hypothesis and validate it on a held-out period before adoption.
3. Third: test a maximum-loss or delta/volatility hedge only with intraday data. The current daily dataset cannot credibly simulate intratrade stop-outs or dynamic hedging.
4. Preserve the frozen 84-trade baseline as the control group for every future experiment.

## Important conclusion
The loss audit does not identify a single universally correct fix. The clearest empirical weakness is concentration of losses in the near-expiry legs, especially in bullish-like front-week adverse signatures. Simple entry-state filters can reduce loss frequency and drawdown in-sample, but they also discard profitable trades and have not been out-of-sample validated.