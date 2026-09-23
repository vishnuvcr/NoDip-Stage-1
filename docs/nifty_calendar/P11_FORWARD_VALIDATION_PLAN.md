# P11 Forward / Paper-Execution Validation Plan — NIFTY 4-Leg Calendar

## Purpose

P10 closed the pre-registered seven-offset screen without directly promoting any entry day. P11 is the final finite validation gate: select one offset using development data only, freeze it, and evaluate it on a genuinely later temporal period that was not used in P0-P10 selection.

## Development-only selection rule

The rule is frozen in this document before any P11 fresh-holdout result is interpreted:
1. Consider all seven P10 offsets.
2. Use 2022-2024 development data only.
3. Require development executable-cycle coverage >= 90%.
4. Require development profit factor > 2.0.
5. Among the qualifying offsets, select the one with the highest net P&L under 2-point adverse slippage.
6. Tie-break: higher development profit factor, then higher coverage.
7. Do not use any 2025+ P10 OOS result to choose the offset.

Under the already-computed P10 development table, this deterministic rule selects D-1.

## Frozen strategy for P11

- Entry session: D-1 relative to the previous NIFTY weekly expiry.
- Entry time: 09:15 IST.
- Calendar-balance ratio: <= 1.20.
- Four-leg structure unchanged.
- Same common ATM strike semantics.
- One historical lot per leg.
- No stop-loss, target, averaging, rolling or discretionary adjustment.
- Exit at the near-expiry session close.
- Historical contract/lot-size rules remain date-effective.
- The strategy must not be retuned using P11 observations.

## Fresh holdout

The P10 OOS sample ends at the latest entry date contained in P8_CYCLES_2025_ONWARD.csv (2026-08-26). P11 begins strictly after that date and uses only subsequently completed expiry cycles available in the pinned intraday dataset.

The P11 script will reconstruct the post-P10 weekly-expiry sequence from the available dataset, generate only completed cycles whose entry and near-expiry sessions are both available, exclude incomplete/future cycles, and preserve all non-executable observations in the ledger.

## Execution reconstruction

Use the P9 Rissin/Upstox 1-minute NIFTY option dataset, not EOD settlement alone.

At 09:15 IST:
- require all four legs to have positive price/volume;
- use the common nearest-ATM strike subject to the frozen 25-point ATM QC;
- enter at the observed 09:15 minute-open;
- record exact timestamp, strike, CBR, prices and volume.

At near-expiry exit:
- use the last common executable timestamp for the four legs;
- record exact prices/volume;
- apply the same historical lot-size logic.

No bid/ask is inferred. Adverse point slippage is applied explicitly as a sensitivity rather than claiming an observed broker fill.

## Costs

Report 0, 0.5, 1 and 2 index-option points adverse slippage per execution, the same brokerage/statutory/exchange-charge stress model used in P8/P10, and gross/net P&L separately.

These are modeled costs, not claims about realized Paytm Money fills.

## Statistical outputs

The P11 report will contain number of completed fresh cycles, executable trades, gate-pass rate, win rate, profit factor, gross/net P&L, maximum drawdown, worst trade, per-trade ledger, slippage sensitivity, exact data coverage and source-quality exclusions.

A bootstrap interval will be reported only when the sample is large enough to make it informative; with very few fresh cycles the report will explicitly classify the evidence as insufficient rather than manufacture statistical precision.

## Promotion gate

P11 does not promote a strategy from a tiny fresh sample.

For capital/paper promotion, all of the following must hold:
1. complete fresh validation sample;
2. no unresolved source-quality or implementation errors;
3. positive net P&L under 1-point adverse slippage;
4. positive net P&L under 2-point adverse slippage;
5. no single trade contributes more than 50% of total gross P&L;
6. no post-hoc parameter change;
7. sufficiently long fresh coverage for meaningful prospective monitoring.

If the current fresh dataset is too short, the result is PAPER-MONITORING ONLY / INSUFFICIENT FRESH SAMPLE, and the research stops at that gate rather than searching more offsets.

## Scientific questions

- Does the development-selected D-1 entry survive a genuinely later temporal period?
- Does it remain positive after the project's explicit execution-cost stress?
- Are results driven by one or two large observations?
- Does the previously observed loss mechanism recur?

## Status

P10: COMPLETE.
P11: BLOCKED — FRESH DATA UNAVAILABLE.