# P9 Alternate Data Source Audit

Last reviewed: 2026-09-23

## Objective

Find independently accessible intraday NIFTY option data capable of reconstructing the P9 event-driven entry rule:
- timestamped NIFTY spot;
- near and far weekly expiries;
- common strike;
- CE and PE for both expiries;
- intraday pricing;
- preferably volume/OI and bid/ask;
- enough history for a development sample and a later temporal holdout.

P9 requires the data to be usable without look-ahead. Daily EOD data is insufficient.

## Source screening

| Source | Resolution | Expiry identity | NIFTY spot | Bid/ask | Period advertised | P9 status |
|---|---|---|---|---|---|---|
| Hugging Face — thetrademarkk/india-index-options-1m | 1 min OHLCV + OI | Actual expiry files; strike/type columns | Separate 1-min NIFTY index file | No | ~2021-2026 | **PRIMARY CANDIDATE** |
| Hugging Face — rissin/nse-options-intraday | 1 min OHLCV | Explicit expiry + strike + type | Underlying field present; verify spot linkage | No | Oct-2024 to 2026 | **SECONDARY CANDIDATE** |
| Kaggle — Historical Nifty Options 2024 All Expiries | Intraday according to linked GitHub query engine | File structure encodes expiry and trade date | Separate monthly NIFTY files | No | 2024 | **DEVELOPMENT / CROSS-CHECK CANDIDATE** |
| Hugging Face — artist-23/nifty-options-data | 1 min | `expiry_type` only in exposed schema; no explicit expiry date | Spot column included | No | 2020-2025 | **NOT SUFFICIENT ALONE** |
| GitHub — SauMStats/nifty-options-data-engine | Wrapper/API | Uses Kaggle 2024 dataset plus a 2026 live-collected dataset | Yes | No | 2024 + 2026 | **DATA ACCESS/SCHEMA REFERENCE** |
| GitHub — SynapticTrading/options_dataprocessing | 1 min OHLCV | 69 expiry dates reported | Vendor dataset; spot merge not the primary focus | No | Jan-Oct 2025 | **SECONDARY REFERENCE** |
| GitHub — ICICI Breeze market-data pipeline | 1 min OHLCV/OI | NIFTY weekly options | Spot indices included | API/account required | User-generated historical download | **FALLBACK ACQUISITION PATH** |

## Primary candidate: thetrademarkk

The Hugging Face dataset reports:
- 1-minute OHLCV(+OI) for NIFTY, BANKNIFTY and SENSEX;
- NIFTY option files under `options/NIFTY/`;
- files named by actual expiry date, e.g. `2022-04-07.parquet`;
- option rows containing timestamp, OHLC, volume, open interest, strike, option type and expiry;
- a separate 1-minute NIFTY index file;
- partial coverage caveat for illiquid/far strikes;
- CC BY-NC 4.0 dataset licence.

This is the best currently identified public source for reconstructing the P9 signal panel because the near/far contracts can be addressed by their actual expiry dates. The absence of bid/ask means the historical execution arm must use the pre-registered 1-minute close -> next available minute execution convention, with slippage sensitivity.

## Secondary candidate: rissin

The Hugging Face dataset reports:
- NIFTY 1-minute intraday data from October 2024 onward;
- explicit `expiry`, `strike`, `option_type`, timestamp, OHLC and volume;
- `oi` is NaN for the Upstox intraday track;
- data were collected through the Upstox historical API;
- licence is listed as `other`.

This is useful for source-level reconciliation, but it should not be treated as fully independent from any other Upstox-derived archive until provenance is checked.

## Kaggle candidate

Kaggle's `historical-nifty-options-2024-all-expiries` states that it contains the full 2024 NIFTY options history, arranged by month and by `Nifty-{expiry day}-{trade day}.csv`, plus monthly NIFTY spot files and a yearly expiry file.

A GitHub query engine built specifically around that Kaggle archive exposes minute-level option queries with explicit expiry/trade-date parameters and columns including timestamp, expiry date, strike, option type, OHLC, volume, OI and spot. This makes the Kaggle archive a useful 2024 development/cross-check source, subject to direct file-level validation.

## Source that is not sufficient alone

`artist-23/nifty-options-data` exposes 1-minute rows with timestamp, OHLC, IV, volume, OI, strike price, spot, `expiry_type`, `strike_type` and option type. The public schema shown through Hugging Face does not expose an explicit expiry date in each row. Because P9 depends on identifying the near expiry and the expiry exactly three weekly intervals later, this source is not sufficient by itself without reconstructing contract identity from the underlying files.

## Acquisition order

1. thetrademarkk — build the first compact P9 intraday panel.
2. Kaggle 2024 — cross-check the 2024 subset where contract/file structure permits.
3. rissin — cross-check the 2025+ subset and investigate overlapping Upstox provenance.
4. ICICI Breeze pipeline — keep as a reproducible fallback requiring an account/API.
5. Paid certified feeds are a last resort only if public sources fail the coverage/execution audit.

## Data integrity tests before P9 scoring

Every source must pass:
- actual expiry identity test;
- near/far three-week mapping test;
- same-strike CE/PE availability test;
- timestamp timezone test;
- NIFTY spot alignment test;
- duplicate timestamp test;
- zero-volume/non-traded fill test;
- missing-minute test;
- expiry-day close test;
- strike-grid test;
- independent sample-date comparison against another source.

No P9 performance result will be interpreted until these tests pass.

## Important execution limitation

None of the currently identified public datasets provides reliable historical bid/ask quotes in the exposed schema. P9 therefore cannot claim true historical market-order fills from these sources. It can, however, test the event-driven signal using minute OHLC with conservative next-minute execution and explicit adverse-slippage sensitivity. A future bid/ask dataset can become a separate execution-validation layer.