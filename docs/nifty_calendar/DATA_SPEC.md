# Data Specification

## Preferred source

NSE official historical equity-derivatives archives and historical reports.

NSE documents that NIFTY weekly index options expire on Tuesday, with the previous trading day used when Tuesday is a trading holiday. Current NSE documentation also shows a 50-point strike interval for NIFTY weekly/monthly index options. These rules are versioned in the research scripts rather than assumed constant across all history.

## Required contract-level fields

- Trading date
- Underlying
- Expiry date
- Strike
- CE/PE
- Open
- High
- Low
- Close
- Volume / contracts
- Open interest
- Underlying value when available
- Lot size when available

## Entry/exit observations

Entry day:
- NIFTY spot OPEN (reference for ATM)
- Four option OPEN prices

Exit day:
- Four option CLOSE prices

Supporting:
- expiry calendar
- applicable lot size history
- futures OPEN for independent forward/ATM sensitivity analysis

## Quality gates

A trade is valid only when:
- entry date exists as a trading session;
- both expiry dates are mapped;
- all four contracts exist;
- all four entry OPEN prices are numeric and > 0;
- all four exit CLOSE prices are numeric;
- lot size is known from an applicable source or validated contract metadata.

Missing data is logged as a data-quality event, not filled from a future day or interpolated.

## Derived data retained in repo

- source manifest and URLs
- per-file hashes
- cleaned trade-level dataset
- validation summaries
- backtest results
- charts and tables

Bulk exchange-owned raw archives will not be committed unless licensing/redistribution is verified.
