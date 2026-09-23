# Error Log

## 2026-09-23 — Wrong repository branch created before repository confirmation
- Event: an initial research branch was accidentally created in vishnuvcr/Nifty before the user specified the target repo.
- Impact: no strategy files, data, results or README changes for this study were written there; only an empty branch was created.
- Correction: target repo changed to vishnuvcr/NoDip-Stage-1; all study artifacts are being created there.
- Prevention: verify the target repository before every new research branch/phase.

## 2026-09-23 — GitHub Actions Python setup cache failure
- Event: the first NIFTY backtest workflow used setup-python pip caching without requirements.txt or pyproject.toml.
- Impact: the workflow stopped during environment setup before tests or data acquisition.
- Correction: authoritative runner no longer requests pip dependency caching; the branch workflow was corrected as well.
- Prevention: use a dependency lock file or install dependencies explicitly without setup-python pip caching.

## 2026-09-23 — Test package import failure
- Event: pytest could not import src.nifty_calendar because the source package/import path was not explicit in CI.
- Impact: research execution stopped before public-data acquisition.
- Correction: package initializers and an explicit test import path were added.
- Prevention: CI now sets PYTHONPATH and the source package has __init__.py files.

## 2026-09-23 — Public archive assumed every month existed
- Event: the first public-data preparation script assumed 12 monthly parquet files for every year.
- Impact: the 2022 run stopped on a 404 for 2022/nifty/12.parquet.
- Correction: the script now queries the public repository directory and processes only files that actually exist.
- Prevention: discover remote file manifests instead of inferring filenames from calendar assumptions.

## 2026-09-23 — Public NIFTY ticker schema mismatch
- Event: the public NIFTY mirror uses NIFTY04JAN24C18300 / NIFTY04JAN24P18300, with a single C/P, while the parser expected CE/PE.
- Impact: the first successful data-preparation run produced a zero-trade ledger even though the source contained millions of option rows.
- Detection: dedicated ticker-diagnostic workflow verified 5,137,099 rows and 773 unique option tickers in one public month, with 0/773 matches under the old regex.
- Correction: parser changed to single-letter C/P and vectorized string extraction; preparation now aborts on zero parsed contracts instead of silently producing a zero-trade backtest.
- Prevention: public-source schema diagnostics are now part of the workflow and must pass before numerical interpretation.

## 2026-09-23 — Source labels were not normalized to engine labels
- Event: after correcting the public parser to recognize single-letter C/P tickers, the preparation output still used C/P labels while the frozen engine expects CE/PE labels.
- Impact: the corrected full run would still reject all four legs during trade selection.
- Correction: preparation now maps C -> CE and P -> PE, with a regression test.
- Prevention: source-to-engine schema mapping is now explicitly tested before the historical run.

## 2026-09-23 — Pandas 3 lot-size assignment failure
- Event: the first run with the corrected data schema reached the backtest but failed in normalize() while assigning the lot-size fallback.
- Root cause: when no lot sizes were missing, pandas 3.x could reject assigning an empty DatetimeArray result from Series.map into an integer column.
- Impact: the backtest stopped immediately after data preparation; no trades were evaluated.
- Correction: normalize() now uses nullable Int64 lot-size storage and only performs the fallback assignment when missing_lot.any() is true.
- Prevention: regression tests now cover both existing integer lot sizes and missing lot-size fallback.

## 2026-09-23 — First validated 2022-2024 backtest completed with partial cycle coverage
- Event: the corrected workflow completed successfully and produced 59 valid executable strategy cycles.
- Audit: 134 potential cycles were examined; 75 were rejected (9 no common strike, 62 missing entry leg, 4 missing exit leg).
- Impact: the gross and cost-adjusted figures are conditional on the 44.0% executable subset and may be affected by non-random missingness.
- Handling: the limitation is now recorded in the robustness report and phase status; no extrapolation is made to the rejected cycles.

## 2026-09-23 — P5 secondary-source execution deferred to GitHub Actions
- Event: direct container access to the NSE archive host and package installation from the public network were unavailable in the model runtime.
- Impact: the independent NSE reconciliation could not be executed locally.
- Correction: the reconciliation was implemented as a GitHub Actions workflow with cached raw NSE inputs, using the official NSE bhavcopy URL formats and an independent NIFTY spot cross-check.
- Prevention: keep source acquisition and full-data reconciliation in the CI runner where network access is available; retain cached raw inputs for reproducibility.

## 2026-09-23 — P5 workflow command-generation and observability issues
- Event: early workflow-generation attempts had JavaScript template/string interpolation errors and a contents-fetch 404 while files were still being created.
- Impact: no research result was produced by those failed tool calls.
- Correction: the workflow and scripts were rewritten and validated through GitHub file reads; the known NIFTY workflow was used to trigger the P5 execution.
- Prevention: validate generated workflow content before relying on a run and use the GitHub Actions REST run/job endpoints to monitor execution.

## 2026-09-23 — P5 workflow recursion from broad path filters
- Event: the P5 branch workflow initially triggered on changes under docs/ and reports/ and then committed its own output files back to the same branch.
- Impact: several overlapping P5 workflow runs were started while the research files were being updated.
- Correction: the workflow was narrowed to its code/workflow paths and concurrency cancellation was added.
- Prevention: phase workflows must never watch their own output paths.

## 2026-09-23 — P5 source-path and reconciliation failures
- Event: multiple early secondary-source runs failed because of NSE archive timeouts, filename prefix/month-case mismatches, and one argument/scope bug.
- Impact: those runs did not produce interpretable numerical results.
- Correction: the mirror-first path, exact filename conventions, explicit rejected-plus-control scope, and independent strike-selection logic were corrected before the final P5 result.
- Prevention: verify source manifests and CLI scope before bulk execution.

## 2026-09-23 — P6 branch stale-input synchronization
- Event: the P6 manuscript branch initially used stale P5 inputs.
- Impact: the first manuscript reflected the superseded 132-cycle union rather than the corrected strict frozen-protocol sample.
- Correction: final P5 outputs were synchronized before rebuilding P6.
- Prevention: phase-transition branches must refresh upstream artifacts before generating downstream statistics.

## 2026-09-23 — P7 ledger type and provenance failures
- Event: the first P7 audit attempted classification before numeric coercion and separately used a manually copied 84-row ledger that did not match the canonical P6 artifact.
- Impact: those runs were rejected and did not alter the final research result.
- Correction: numeric schema validation and deterministic regeneration from canonical P5/P6 inputs were added.

## 2026-09-23 — P8 workflow execution failures
- Event: several P8 workflow attempts failed before completion, including an invalid detached-checkout command and related runner setup issues.
- Correction: the P8 workflow now uses the cached mirror snapshot directly and the final OOS result was successfully completed and committed.

## 2026-09-23 — P9 tool-side patch syntax failure
- Event: an initial attempt to write the P9 alternate-data source audit failed with a tool-side JavaScript quoting/template syntax error.
- Impact: no repository file was changed by that failed call.
- Correction: the audit document was rewritten using line-array construction and then committed successfully.
- Prevention: avoid nested template strings when repository content contains Markdown backticks or quote-heavy schema descriptions.

## 2026-09-23 — P9 acquisition run initially appeared absent, then completed successfully
- Event: the first query after adding the P9 Hugging Face acquisition workflow returned zero runs, but a subsequent workflow-run query confirmed run 35831140990 completed successfully.
- Result: 192/201 requested NIFTY option expiry files were downloaded (~671.8 MB) and the 1-minute NIFTY index file was downloaded.
- Impact: no research interpretation was affected; the initial zero-run response was transient connector observability.
- Follow-up: the successful acquisition is now recorded in the P9 source audit and phase status.

## 2026-09-23 — P9 public-source schema limitation
- Event: the public intraday candidates identified so far expose OHLCV and expiry/strike data but not reliable historical bid/ask quotes in their published schema.
- Impact: these sources cannot support a claim of exact historical market-order fills.
- Handling: when a qualifying intraday dataset is acquired, P9 will use the pre-registered 1-minute signal-close to next-minute execution convention with explicit adverse slippage. True bid/ask validation remains a separate execution-validation layer.

## 2026-09-23 — P9 raw-cache path correction
- Event: the first successful acquisition workflow cached data/cache/p9_hf_probe, which contained the manifest but not the raw Hugging Face Parquet files stored under /home/runner/.cache/huggingface/hub.
- Impact: the raw 671.8 MB source files were not persisted in the Actions cache for reuse by a later scan.
- Correction: the workflow was updated to cache the actual Hugging Face dataset directory under a stable cache key and to run parquet schema validation plus the first event-driven timing scan.
- Prevention: verify the cache path against the actual downloader destination before declaring raw data cached.

## 2026-09-23 — P9 DuckDB OOS scanner implementation errors
- Event: the first DuckDB OOS scan completed its workflow step and committed outputs, but the ledger showed 83/86 cycles failing inside the analysis with `KeyError: 'timestamp'`. One cycle also raised `AttributeError: 'dict' object has no attribute 'ce'`.
- Root cause: empty entry-day near/far pivots were not rejected before the timestamp merge, and the exit helper returned dictionaries that were accessed as objects.
- Impact: the first DuckDB numerical output is rejected and must not be interpreted.
- Correction: the scanner now checks for empty/missing timestamp columns before `merge_asof` and accesses exit dictionaries by key.
- Prevention: zero-row and empty-arm cases remain explicit non-trade states rather than exceptions.
