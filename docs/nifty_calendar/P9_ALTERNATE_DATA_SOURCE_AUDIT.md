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

## Acquisition result — 2026-09-23

The first CI acquisition run completed successfully on GitHub Actions.

- Candidate source: `thetrademarkk/india-index-options-1m`
- Research cycles requested: 170 (84 historical strict + 86 P8 OOS executable)
- Unique NIFTY option expiry files required: 201
- Expiry files downloaded: 192
- Expiry files missing from the source manifest: 10
- Total downloaded option/index bytes during the run: ~671.8 MB
- 1-minute NIFTY index file downloaded successfully.
- Cycles for which both near and far expiry files are present: 157/170 (92.35%)
- Cycles blocked by a missing near or far expiry file: 13/170 (7.65%)

The missing files identified were:
- 2026-06-16
- 2026-06-23
- 2026-06-30
- 2026-08-11
- 2026-08-18
- 2026-08-25
- 2026-09-01
- 2026-09-08
- 2026-09-15
- 2026-09-22

The gap pattern is concentrated in later 2026 expiries and should be treated as a source-coverage boundary, not as strategy skips.

### Persistence correction

The first workflow successfully downloaded the raw files onto the GitHub Actions runner, but its cache step stored only the local manifest path rather than the Hugging Face raw-file cache. The workflow has now been corrected to cache:

`/home/runner/.cache/huggingface/hub/datasets--thetrademarkk--india-index-options-1m`

under a stable P9 cache key. The corrected workflow also adds parquet schema validation and the first event-driven timing scan.

Because the available connector does not expose a manual workflow-dispatch action, the corrected workflow has not yet produced a second run. No event-driven performance result is therefore claimed from this stage.


## Primary-source execution-quality finding

The first P9 timing scan is not an admissible performance estimate from the primary public source.

A targeted audit on 2026-04-01 showed:
- NIFTY index data at 1-minute resolution beginning 09:15 IST;
- near-expiry option rows: 58,868 for the day;
- far-expiry option rows: only 903 for the day;
- sampled far-expiry rows at 09:15, 09:16, 09:22 and 09:26: only 2–4 rows per minute.

Because the frozen P6 selection rule chooses the nearest common executable strike to spot, sparse far-expiry coverage can make the selected strike materially non-ATM even though it is mathematically the nearest remaining common strike. The first apparent P9 event trade on 2026-04-01 selected strike 20,500 while NIFTY spot was about 22,900.

Therefore the primary-source event-performance output is treated as **data-quality diagnostic evidence only**, not as a strategy performance result. The secondary Rissin/Upstox-derived 1-minute source is being used to test whether the anomaly is source-specific.


## Secondary-source P9 result

The Rissin/Upstox 1-minute source was used for the final OOS timing comparison after the primary source failed far-expiry coverage QC.

- Population: 86 post-2024 executable P8 cycles.
- Fixed 09:15 control: 26 trades; gross ₹40,506.25; win rate 80.77%; PF 5.029.
- Event-driven: 70 trades; gross ₹37,291.40; win rate 62.86%; PF 1.576.
- Incremental event-only trades: 44; gross ₹-3,214.85; PF 0.941.
- Original gate-fail dates that only qualified later: 24; gross ₹-13,964.60; PF 0.665.
- Event-driven net at 0.05% exchange stress: ₹9,222.87 / ₹-10,837.13 / ₹-30,897.13 / ₹-71,017.13 at 0 / 0.5 / 1 / 2 points adverse slippage.

P9 conclusion: event-driven timing is not promoted.