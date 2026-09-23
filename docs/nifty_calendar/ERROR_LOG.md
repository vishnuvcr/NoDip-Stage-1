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


## 2026-09-23 — P9 full-file DuckDB timing result rejected
- Event: the first completed DuckDB timing workflow produced 86 OOS rows but 0 executable timing trades; most rows failed inside the analysis with `KeyError: 'timestamp'`, and one row had an exit-helper attribute error.
- Impact: the output is rejected as an implementation artifact and is not a P9 strategy result.
- Correction: a remote-predicate DuckDB implementation was added. It reads the public Hugging Face Parquet source directly with date predicates instead of downloading whole expiry files, and it uses direct expiry URLs from the OOS ledger rather than relying on the repository file listing.
- Prevention: do not interpret a zero-trade result when the row-level error rate is non-zero; require executable-row and error-rate checks before performance analysis.


## 2026-09-23 — P9 source-alignment audit dependency failure
- Event: the first timestamp/ATM alignment audit workflow omitted the `huggingface_hub` package and failed before the audit script ran.
- Impact: no alignment conclusion was produced by that failed run.
- Correction: the workflow now installs `huggingface_hub`; the subsequent audit completed successfully.
- Prevention: any workflow invoking `hf_hub_download` must list `huggingface_hub` explicitly in its install step.

## 2026-09-23 — P9 primary-source far-expiry intraday sparsity
- Event: the primary public 1-minute source was found to have extremely sparse far-expiry observations on the 2026-04-01 sample: the near expiry had tens of thousands of option rows, while the far expiry had only 903 rows for the entire trading day and only 2–4 rows at sampled minutes.
- Impact: the frozen nearest-common-strike rule can select a strike far from the current NIFTY spot simply because the far-expiry source has few contemporaneous strikes. The first apparent event trade used strike 20,500 with NIFTY near 22,900.
- Handling: the one-trade P9 primary-source result is rejected for performance interpretation until a second option-data source demonstrates adequate multi-strike far-expiry coverage.
- Prevention: P9 source validation must record ATM-distance and far-expiry coverage at the signal timestamp; sparse-common-strike cases remain a data-quality limitation, not a trading conclusion.

## 2026-09-23 — P9 primary timing output rejected for ATM inconsistency
- Event: the remote DuckDB P9 scan completed its analysis step and produced one apparent event trade on 2026-04-01.
- QC failure: the reconstructed event strike was 20,500 while the independently audited intraday NIFTY series was around 22,843 at 09:15 and the corresponding daily spot open was 22,899.
- Root cause: the primary source has only 2–4 far-expiry rows at several sampled opening/event timestamps, so nearest-common-strike selection is not a valid ATM reconstruction when the far-expiry panel is sparse.
- Impact: the one-trade primary P9 result is rejected and must not be used for performance inference.
- Additional issue: the primary scanner's fixed arm produced 0 trades and therefore was not a valid recreation of the authoritative P8 fixed-gate reference.
- Correction: require explicit ATM-distance QC and four-leg panel coverage before scoring; use the P8 fixed-gate ledger as the reference arm; validate a secondary option source before any P9 performance interpretation.
- Prevention: sparse-contract panels are treated as source-quality failures, not as eligible trading opportunities.

## 2026-09-23 — P9 remote DuckDB result persistence conflict
- Event: the remote-predicate analysis step completed successfully, but its GitHub Actions commit step failed during git rebase because generated P9_OOS_DUCKDB_COMPARISON.csv conflicted with a newer branch commit.
- Impact: workflow conclusion was failure even though the analysis code step succeeded; persisted output required subsequent branch reconciliation.
- Correction: classify the run as a persistence-layer failure separately from the numerical QC failure and avoid interpreting the generated file as validated research output.
- Prevention: future generated-output workflows should synchronize to the latest branch before committing generated artifacts, rather than rebasing a local commit that modifies the same generated file.


## 2026-09-23 — P9 secondary Rissin OOS validation completed
- Event: the secondary Rissin/Upstox 1-minute option source completed the predefined OOS timing comparison on all 86 post-2024 executable cycles.
- Result: fixed 09:15 control produced 26 executable trades; first-qualifying event-driven entry produced 70 executable trades.
- The 44 incremental event-only trades produced gross P&L ₹-3,214.85 and PF 0.941.
- The 24 incremental trades that were gate-fail at the fixed observation but later became CBR<=1.20 produced gross P&L ₹-13,964.60 and PF 0.665.
- At 0.05% exchange-charge stress, event-driven modeled net P&L was ₹9,222.87 with zero added slippage and negative at 0.5/1/2-point adverse slippage.
- Interpretation: P9 does not support promoting event-driven timing. No threshold or structure was retuned.
## 2026-09-23 — P9 cutoff-sensitivity workflow syntax failure
- Event: the first P9 latest-entry sensitivity workflow (run 35837987402) failed before producing outputs.
- Root cause: the generated Python source contained escaped quotes (`\\\"`) inside an f-string expression, producing a Python `SyntaxError` at line 66.
- Correction: the f-string was rewritten with normal Python quotes; the workflow commit step also now uses plain `\${GITHUB_REF_NAME}` shell expansion after fetch/reset.
- Impact: no numerical cutoff-sensitivity result was produced by the failed run.
- Prevention: validate generated Python syntax in CI before interpreting downstream results, and avoid double-escaping source-code quotes during repository writes.

## 2026-09-23 — P9 first Rissin result superseded by deterministic ATM QC
- Event: the initial Rissin run reported 26 fixed-source trades and 70 event trades before enforcing the contract-definition ATM-distance check.
- Impact: those pre-QC figures are not the authoritative P9 result because some selected common strikes were more than one strike interval from spot.
- Correction: re-ran the identical secondary-source population with the frozen 50-point NIFTY strike interval and a deterministic maximum ATM distance of 25 points. The authoritative result is 14 fixed diagnostic trades and 65 event trades.
- Prevention: source-quality/contract-definition filters must execute before any performance metrics are persisted as final results.

## 2026-09-23 — P9 latest-entry sensitivity completed after syntax correction
- Event: corrected workflow run 35838201255 completed successfully after two earlier syntax-failure/cancellation attempts.
- Result: 15:00/15:15/15:30/15:40 produced 63/64/65/65 event trades; all were negative at 0.5-point adverse slippage and beyond.
- Interpretation: the cutoff analysis is a pre-registered robustness table; no cutoff was selected for profitability.

## 2026-09-23 — P10 entry-day offset phase initiated
- Event: the user discarded the P9 event-driven timing idea and requested fixed 09:15 entry testing on D-1, D0, D+1, D+2, D+3, D+4 and D+5 relative to the previous expiry.
- Correction to phase design: entry offsets are defined on NSE trading sessions rather than calendar days; this avoids non-trading dates and is recorded before scoring.
- Prevention: all seven offsets are pre-registered, CBR remains frozen at 1.20, and OOS data are not used to select an offset.

## 2026-09-23 — P10 local execution network unavailable
- Event: a local container validation attempt could not clone the research branch because the runtime could not resolve github.com.
- Impact: local syntax execution could not be used as an independent check.
- Correction: GitHub Actions remains the authoritative execution environment for P10, consistent with earlier P5/P8 network constraints.
- Prevention: keep CI execution as the reproducibility path when the model runtime has no external network access.

## 2026-09-23 — P10 entry-day offset workflow failure
Run ID: 35840948323
Step failure requires inspection before any numerical interpretation.

## 2026-09-23 — P10 entry-day offset workflow failure
Run ID: 35841010407
Step failure requires inspection before any numerical interpretation.

## 2026-09-23 — P10 entry-day offset workflow failure
Run ID: 35841182028
Step failure requires inspection before any numerical interpretation.

## 2026-09-23 — P10 pandas sample-column collision
- Event: P10 run 35841182028 downloaded and loaded the Rissin daily historical Parquet source successfully, passed Python syntax validation, then failed during summary construction with KeyError: False.
- Root cause: `ledger.sample` resolved to pandas DataFrame.sample() rather than the column named `sample`, so the filter evaluated incorrectly.
- Correction: summary filtering now uses the explicit `ledger['sample']` column reference.
- Impact: no numerical P10 result from this run is accepted.
- Prevention: avoid DataFrame attribute access for columns whose names overlap pandas methods (`sample`, `size`, `mean`, etc.).

## 2026-09-23 — P10 OOS previous-expiry mapping bug
- Event: P10 run 35841355984 completed the seven-offset computation but its OOS summary was invalid because every OOS cycle inherited the fallback previous-expiry date 2024-12-26.
- Root cause: the OOS near-expiry column was normalized to YYYY-MM-DD strings, while the previous-expiry lookup keys were built from raw NumPy datetime representations, so the dictionary lookup missed every row and fell back to the first-cycle date.
- Detection: the OOS ledger showed identical D-1/D0/D+1 entry dates for nearly all cycles and only two OOS cycles were executable.
- Correction: previous-expiry mapping now uses the already-normalized YYYY-MM-DD strings and includes a sanity check requiring multiple distinct mapped previous-expiry dates.
- Impact: the OOS results from run 35841355984 are rejected and replaced by a re-run after the mapping fix.
- Prevention: all date-key joins in phase scripts must normalize both sides to the same explicit string/date representation before mapping.

## 2026-09-23 — P10 workflow commit step discarded regenerated outputs
- Event: run 35841545509 executed the corrected script successfully, but its conflict-safe commit step reset the workspace to the branch tip after computation and did not rerun the generator. The generated files were therefore overwritten by the previously committed P10 outputs, so no new result commit was produced.
- Correction: the conflict-safe commit step now regenerates the P10 outputs after the branch reset and before `git add`/push.
- Impact: run 35841545509 output files are not accepted as the authoritative corrected result despite the computation step succeeding.
- Prevention: conflict-safe output workflows must regenerate artifacts after any `git reset --hard` that can overwrite generated files.

## 2026-09-23 — P11 forward validation workflow failure
Run ID: 35846047483
Step failure requires inspection before any numerical interpretation.

## 2026-09-23 — P11 forward validation workflow failure
Run ID: 35846127246
Step failure requires inspection before any numerical interpretation.

## 2026-09-23 — P11 run 35846642900 cancelled by concurrency replacement
- Event: run 35846642900 began after the P11 script fix but was cancelled when the workflow-file trigger created run 35846661383.
- Impact: no numerical output from the cancelled run was interpreted.
- Handling: run 35846661383 completed successfully and produced the authoritative P11 fresh-data gate result.

## 2026-09-23 — P11 fresh-data gate completed successfully
- Event: run 35846661383 completed after syntax validation and P11 execution.
- Result: latest source trading date available to the runner was 2026-06-29; the frozen P10 OOS cutoff is 2026-08-26; zero completed fresh P11 cycles were available after the cutoff.
- Interpretation: P11 stopped for data availability. This is not a strategy-loss result and no P10 OOS observations were reused.
- Prevention: do not resume P11 until a completed post-cutoff cycle is added to the pinned intraday cache.

## 2026-09-23 — P12 far-expiry workflow failure
Run ID: 35883781404
Step failure requires inspection before numerical interpretation.

## 2026-09-23 — P12 far-expiry workflow failure
Run ID: 35884371489
Step failure requires inspection before numerical interpretation.

## 2026-09-23 — P13 fresh far-expiry validation failure
Run ID: 35885232033
Step failure requires inspection before numerical interpretation.

## 2026-09-23 — P13 fresh far-expiry validation failure
Run ID: 35885317254
Step failure requires inspection before numerical interpretation.

## 2026-09-23 — P13 fresh far-expiry validation failure
Run ID: 35885474287
Step failure requires inspection before numerical interpretation.

## 2026-09-23 — P13 fresh far-expiry validation failure
Run ID: 35885715169
Step failure requires inspection before numerical interpretation.

## 2026-09-23 — P13 fresh far-expiry validation failure
Run ID: 35886104185
Step failure requires inspection before numerical interpretation.
