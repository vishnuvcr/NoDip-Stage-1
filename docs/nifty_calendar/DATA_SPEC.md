# Data Specification

## Preferred source

NSE official historical equity-derivatives archives and historical reports.

NIFTY weekly expiry timing is versioned by the actual contract dates. NSE's June 2025 circular changed NIFTY weekly expiry from Thursday to Tuesday for newly generated September 2025 onward weekly contracts; existing contracts expiring on or before 31-Aug-2025 retained their prior dates.

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
- NIFTY spot OPEN
- four option OPEN prices

Exit day:
- four option CLOSE prices

Supporting:
- actual expiry calendar
- applicable contract lot size
- optional futures OPEN for independent forward-sensitivity checks

## Lot-size history

For INR conversion, use the lot size attached to each actual option contract rather than one constant multiplier:
- NIFTY weekly contracts were 75 lots before the 2021 reduction.
- August 2021 weekly expiries onward used 50.
- May 2024 weekly expiry onward used 25.
- New index contracts introduced from 20-Nov-2024 used 75.
- January 2026 weekly expiries onward used 65 under the next revision.

These transitions are sourced from NSE circulars and are validated against contract-level metadata whenever available.

## Quality gates

A trade is valid only when:
- entry date exists as a trading session;
- near and far expiry dates are mapped from the historical contract calendar;
- all four contracts exist on entry and expiry dates;
- all four entry OPEN prices are numeric;
- all four exit CLOSE prices are numeric;
- lot sizes are known for each leg or are independently validated.

Missing data is logged as a data-quality event, not filled from a future day or interpolated.

## Derived data retained in repo

- source manifest and URLs
- per-file hashes
- cleaned trade-level dataset
- validation summaries
- backtest results
- charts and tables

Bulk exchange-owned raw archives will not be committed unless licensing/redistribution is verified.
