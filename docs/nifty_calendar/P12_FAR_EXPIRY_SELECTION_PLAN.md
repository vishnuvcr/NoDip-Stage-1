# P12 Far-Expiry Selection Research Plan — NIFTY Four-Leg Calendar

## Research question

Does the NIFTY four-leg position perform differently when the far expiry is chosen 1, 2, 3 or 4 listed weekly expiries after the near expiry, and can the far expiry be selected at 09:15 using only information available at entry?

## Frozen trade structure

- Entry session: D+1 trading session after the previous listed NIFTY expiry, matching the P10 reference entry-day population.
- Entry time: 09:15 IST.
- Near expiry: the first listed expiry after the previous expiry.
- Candidate far expiries: F1, F2, F3, F4 = the 1st, 2nd, 3rd and 4th listed expiries after the near expiry.
- Same ATM strike across the near expiry and the selected far expiry. The ATM strike is determined from the near-expiry 09:15 listed strikes nearest to the NIFTY spot open.
- Position: short near CE, long near PE, long far CE, short far PE.
- Exit: near-expiry close.
- No stop, target, adjustment, rolling or discretionary intervention.
- Historical lot sizes are date-effective.

## Primary experiment

Evaluate each fixed far horizon F1, F2, F3 and F4 separately on the same D+1/09:15 cycle population.

## Frozen far-expiry selection criterion

At 09:15, among F1-F4 candidates that have all four far/near legs available at the same ATM strike and positive volume, calculate:

`entry_credit_points = near_CE - near_PE + far_PE - far_CE`

`entry_credit_yield = entry_credit_points / NIFTY_spot_open`

Select the far expiry with the **maximum entry_credit_yield**. A positive value is an entry credit; a negative value is an entry debit. No future price, close, realized volatility or P&L is used in selection.

Rationale: the selected structure is symmetric in calls/puts across maturities, so this metric directly measures the net amount received at entry in normalized option-point terms. It is observable, parameter-free and does not use future information.

Ties are resolved by choosing the shorter far-expiry horizon.

## Samples

- Development: entry dates 2022-01-01 through 2024-12-31.
- OOS: entry dates 2025-01-01 onward through the latest fully completed near expiry in the pinned source.
- All four fixed horizons and the adaptive selector are reported on identical eligible cycle populations where possible.

## Secondary sensitivity

Report the historical CBR <= 1.20 condition as a diagnostic overlay, but do not use it to choose the far expiry in the primary experiment. This keeps P12 focused on the user's new far-expiry question rather than importing an old filter as a hidden selection parameter.

## Metrics

For each fixed horizon and the adaptive selector report:
- cycles, executable trades and coverage;
- gross P&L, mean/median trade P&L, win rate, profit factor;
- maximum drawdown and worst trade;
- bootstrap 95% interval of total gross P&L;
- net P&L after the existing brokerage/statutory/exchange stress model at 0, 0.5, 1 and 2 points adverse slippage per execution;
- selection frequency F1/F2/F3/F4 for the adaptive rule;
- entry-credit distribution and selected-score distribution.

## Scientific control

Fixed-horizon OOS results are descriptive. The adaptive selector is a pre-specified entry-time rule and is applied mechanically to OOS without using OOS P&L to modify it. No far horizon is promoted merely because its OOS result is the largest.

## Stop condition

P12 ends after the fixed F1-F4 comparison and the frozen adaptive selector evaluation. No further far-expiry horizons, thresholds or score weights are searched in this phase.