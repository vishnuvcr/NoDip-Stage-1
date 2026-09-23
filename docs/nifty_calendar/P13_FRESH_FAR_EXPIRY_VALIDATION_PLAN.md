# P13 Fresh Far-Expiry Validation Plan

## Purpose

Validate the frozen P12 far-expiry adaptive rule on data that was not part of the P10/P12 evaluation period.

## Frozen rule carried forward without modification

- Entry: D+1 trading session after previous listed NIFTY expiry.
- Entry time proxy: 09:15 IST market open, represented by the daily option `open` and NIFTY daily opening value used in P12.
- Near expiry: next listed expiry.
- Far candidates: F+1, F+2, F+3, F+4 subsequent listed expiries.
- Same ATM strike: nearest listed near-expiry strike to the NIFTY opening value, with <=25 index-point ATM QC.
- Position: short near CE, long near PE, long selected far CE, short selected far PE.
- Exit: near-expiry close.
- Selection score: `(near CE - near PE + far PE - far CE) / NIFTY spot open`.
- Select the eligible far expiry with the highest score; ties go to the shorter far expiry.
- No CBR threshold, score weight, expiry horizon or cost parameter may be changed in P13.

## Fresh holdout definition

- P10/P12 exposed evaluation cutoff: 2026-08-26 entry date.
- Fresh sample: entry_date strictly greater than 2026-08-26.
- A cycle is eligible only when its near expiry is already <= the latest source trading date.
- No observations from 2022-2025 or the P10/P12 evaluation sample are used for selection or parameter tuning.

## Data source

The current pinned public dataset is re-read from `rissin/nse-options-intraday`. The dataset card states the historical daily track is derived from NSE F&O bhavcopy and covers NIFTY through the present; the Upstox intraday track is separately documented. P13 uses the same daily methodology as P12 for exact comparability. The current dataset page reports an update within the last week.

## Outputs

- Fresh cycle/trade count and data coverage.
- F+1/F+2/F+3/F+4 fixed diagnostics.
- Frozen adaptive rule result.
- Gross P&L and net P&L under 0/0.5/1/2-point adverse slippage.
- Brokerage/statutory/exchange stress identical to P12.
- Win rate, profit factor, worst trade, drawdown.
- Bootstrap distribution only as a descriptive interval; with a small fresh sample it will be explicitly classified as low-power.
- Per-cycle ledger, including non-executable reasons.

## Promotion gate

P13 does not promote from a small fresh sample.

To reach paper-eligible status the frozen adaptive rule would need a sufficiently long fresh sample, positive net P&L at 1-point and 2-point adverse slippage, no major data-quality defects, and no single observation dominating the total result.

If the fresh sample is too small, the correct result is `INSUFFICIENT FRESH SAMPLE — CONTINUE PROSPECTIVE PAPER MONITORING`, not a rejection and not a promotion.

## Stop condition

P13 ends after running the frozen validation. No further far-expiry search or adaptive-score tuning is allowed in this phase.