# P14 Official NSE Fresh Far-Expiry Validation Plan

## Purpose

Re-run the frozen P12 far-expiry adaptive rule on a genuinely post-cutoff sample using fresh official NSE F&O UDiFF bhavcopy files, because the public Hugging Face cache used by P13 terminates at 2026-06-29.

## Frozen rule

- Entry: D+1 trading session after previous listed NIFTY expiry.
- Entry-time proxy: daily option `OpnPric` (09:15 market-open proxy) and underlying price from the same NSE bhavcopy.
- Near expiry: next listed weekly expiry.
- Far candidates: F+1, F+2, F+3, F+4 subsequent listed expiries.
- Strike: same ATM strike nearest to the NIFTY underlying price, with <=25-point ATM QC.
- Position: short near CE, long near PE, long selected far CE, short selected far PE.
- Exit: near-expiry close (`ClsPric`) on the near-expiry session.
- Far-expiry selection score: `(near CE - near PE + far PE - far CE) / NIFTY underlying price`.
- Select highest score among candidates whose four entry legs exist with positive volume and price. Ties select the shorter far expiry.
- No CBR filter, threshold, weighting or other parameter is added in P14.

## Fresh sample

- P10/P12 cutoff: 2026-08-26.
- Fresh dates are strictly after the cutoff.
- Only cycles whose near-expiry exit date is <= the latest official NSE trading date downloaded are eligible.
- Current expected completed fresh cycles are limited by the calendar; with the current date 2026-09-23, the latest fully completed weekly cycle should occur before the 23-Sep session.

## Data source and integrity

NSE's current derivatives reports page identifies the F&O UDiFF Common Bhavcopy Final as the current daily derivative archive. P14 downloads the daily official archive for the fresh date range, records HTTP status and file checksum, parses only NIFTY index options, and retains the raw compressed files in the GitHub Actions cache. [NSE current reports page](https://www.nseindia.com/all-reports-derivatives)

## Outputs

- source manifest with date, URL, status, byte size and SHA256;
- fresh cycle ledger including rejected/non-executable reasons;
- F+1..F+4 fixed diagnostics;
- frozen adaptive-selection result;
- net P&L at 0/0.5/1/2 points adverse slippage;
- exact fresh sample coverage;
- conclusion that distinguishes small-sample insufficiency from strategy failure.

## Statistical rule

With only a few post-cutoff weekly cycles, no claim of statistical significance or population-level robustness is made. Bootstrap is reported only as a descriptive diagnostic and will be labelled low-power.

## Stop condition

P14 stops after the official-NSE fresh validation. No parameter search or far-expiry score tuning is performed.