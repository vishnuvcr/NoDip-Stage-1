# P9 — Event-Driven Intraday Entry Timing Research Plan

## Phase status

Status: PROPOSED / DATA-BLOCKED

Parent phase: P8 unseen post-2024 validation.
Branch: `research-nifty-4leg-calendar-p9-entry-timing`

P6 remains frozen. P8 remains a completed temporal validation of the fixed 1.20 candidate. P9 does not overwrite either result.

## Research question

Can the frozen P7 candidate gate

[
\mathrm{CBR}=
\frac{\mathrm{Far\ CE}/\mathrm{Near\ CE}}
{\mathrm{Far\ PE}/\mathrm{Near\ PE}}
\le 1.20
]

be used as an **event-driven entry condition** on the first eligible trading day, entering at the first intraday timestamp when all other frozen criteria are satisfied, rather than relying on a fixed opening timestamp?

### Secondary questions

1. How often does the 1.20 gate first become valid after the opening observation?
2. Does delayed entry materially change entry debit, four-leg relative pricing, and subsequent P&L?
3. Does event-driven entry reduce the residual loss mechanisms identified in P8, especially far-leg deterioration?
4. How sensitive are results to execution assumptions, timestamp granularity, and the latest permissible entry time?
5. Does the event-driven rule remain defensible on a genuinely unseen temporal holdout?

## What is frozen

The following are inherited unchanged from P6/P8:

- Eligible day: first trading session after the prior NIFTY weekly expiry.
- Four-leg structure:
  - BUY near-expiry ATM PE.
  - SELL near-expiry ATM CE.
  - BUY far-expiry ATM CE, three weekly intervals after near expiry.
  - SELL far-expiry ATM PE.
- The four legs use the **same strike selected at the actual entry timestamp**.
- Entry gate remains exactly CBR <= 1.20.
- No threshold search in P9.
- Exit remains all four legs at the near-expiry trading-day close.
- No stop, target, roll, averaging, or post-entry adjustment.
- One applicable lot per leg.
- Brokerage, statutory charges, exchange-charge sensitivity and adverse slippage remain explicit.

P6 and P8 results are not rewritten. They remain the fixed-time reference arms.

## Event-driven entry definition

Primary proposed rule:

> On each eligible trading day, scan forward from the start of continuous trading. Enter exactly once, at the **first timestamp** for which:
>
> 1. the current NIFTY spot permits a valid listed common ATM strike;
> 2. all four required contracts exist for that strike and the required near/far expiries;
> 3. all four legs have an executable contemporaneous quote;
> 4. CBR <= 1.20 using only information available at that timestamp.

If the gate never becomes valid during the permissible trading session, skip the day.

There is no second entry or re-entry on a day after the first qualifying event.

### Timestamp / look-ahead rule

- Tick or quote data: evaluate the condition from the contemporaneous quote snapshot and model fills using contemporaneous bid/ask prices (or explicitly defined market-order side prices).
- 1-minute OHLC data only: do **not** compute the signal from a completed minute and fill at an unobserved price inside that same minute. The primary conservative convention will be signal on minute close and fill at the next available minute's executable price, with slippage sensitivity.
- Daily OPEN data alone is insufficient to test this phase.

### Latest-entry policy

The research comparison will report a primary session-wide event-driven arm plus pre-specified operational cutoffs as sensitivity cases. The cutoff is an execution constraint, not an alpha parameter, and is not to be selected after seeing performance.

Initial sensitivity cutoffs:
- 15:00 IST
- 15:15 IST
- 15:30 IST
- full derivatives session to 15:40 IST where data quality permits

The primary interpretation will not choose the cutoff that produces the largest return.

## Data required

Minimum preferred dataset:

- NIFTY spot timestamped intraday observations.
- NIFTY option-chain timestamped observations for the near and far weekly expiries.
- At minimum: timestamp, expiry, strike, CE/PE, price, volume and OI.
- Preferred: bid, ask and quote size for each leg.
- Preferred resolution: tick/quote or 1-second; acceptable secondary: 1-minute.

The current repository does not contain a qualifying intraday four-leg quote archive, so no numerical P9 result is claimed yet.

Potential acquisition paths to evaluate:
- NSE historical order/trade data or licensed historical quote data.
- Broker/API historical option data where permitted.
- Public research datasets that contain both spot and multi-expiry NIFTY option intraday data.
- Public GitHub/Kaggle/Hugging Face datasets only after contract, timestamp and coverage validation.

## P9 work packages

### P9.1 — Data-source audit
- Identify candidate intraday datasets.
- Verify 2022-2026 coverage, expiry coverage, strike coverage and timestamp convention.
- Check whether at least three weekly expiries can be reconstructed on the same strike.
- Validate one or more dates against an independent source.

### P9.2 — Event detector
Implement a deterministic scanner:
- build current ATM strike from timestamped spot;
- retrieve near and far contracts;
- compute CBR;
- enforce four-leg quote availability;
- emit first qualifying timestamp only.

### P9.3 — Execution model
Primary:
- contemporaneous bid/ask where available;
- explicit leg-by-leg execution side;
- brokerage and statutory costs;
- 0, 0.5, 1 and 2 index-point adverse slippage sensitivities.

Secondary:
- next-minute execution for 1-minute-only datasets;
- LTP/mid-price sensitivity, clearly separated from executable bid/ask results.

### P9.4 — Historical comparison
Compare, on the same eligible dates:
1. fixed-open CBR gate (P8 reference);
2. event-driven first-qualifying entry;
3. no-trade when CBR never qualifies.

Report:
- number of entries and skipped days;
- entry-time distribution;
- entry CBR;
- entry debit;
- gross/net P&L;
- win rate;
- profit factor;
- max drawdown;
- worst trade;
- tail loss contribution;
- cost/slippage sensitivity;
- annual and expiry-regime breakdowns.

### P9.5 — Loss-mechanism analysis
For every event-driven losing trade:
- near vs far aggregate contribution;
- four individual leg contributions;
- whether the event-driven delay helped or hurt the entry;
- whether the residual far-leg deterioration observed in P8 remains.

### P9.6 — Temporal holdout
Any decision about advancing event-driven entry must use:
- development window for implementation details only;
- a later unseen temporal holdout for the final test;
- no threshold re-optimization after holdout results are inspected.

## Statistical analysis

Primary:
- paired trade-date comparison where both fixed-time and event-driven entries exist;
- bootstrap confidence intervals for cumulative P&L and mean trade P&L;
- distribution of entry delays;
- drawdown comparison;
- sign test / paired non-parametric comparison when sample assumptions are not justified.

Secondary:
- regression/association of entry delay with subsequent P&L;
- sensitivity to timestamp resolution;
- sensitivity to execution assumptions.

No model selection based on post-hoc performance ranking will be used to claim confirmation.

## Success / stop criteria

P9 advances only if:
- the event-driven rule is fully reproducible from timestamped information;
- the signal has no look-ahead;
- the four-leg fills are explicitly modeled;
- results survive realistic cost/slippage stress;
- and the final rule is tested on a genuinely unseen temporal sample.

P9 stops without promotion if:
- data cannot support contemporaneous four-leg reconstruction;
- the signal requires unverifiable fills;
- or the apparent benefit disappears under executable-cost assumptions.

## Expected outputs

- `docs/nifty_calendar/P9_ENTRY_TIMING_PLAN.md`
- `.github/workflows/p9-entry-timing.yml`
- event-detection and scoring scripts
- timestamp-level signal ledger
- trade ledger
- cost/slippage sensitivity
- loss-mechanism report
- final P9 conclusion
- updated manuscript/research plan if the phase produces a defensible result

## Important interpretation

This phase asks whether **entry timing can be adaptive while the entry criterion remains frozen**. It does not yet ask whether the 1.20 threshold itself should be changed.
