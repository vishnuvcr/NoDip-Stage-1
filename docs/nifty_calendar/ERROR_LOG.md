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

## 2026-09-23 — P5 execution currently in progress
- Event: GitHub Actions run 35789188159 (run 14) started successfully and remains in progress at the public-data preparation step; run 35789173734 (run 13) was also triggered by the preceding workflow edit.
- Impact: no P5 reconciliation outputs are yet committed to the research branch, so the 44.0% coverage figure remains the only verified coverage result.
- Handling: do not interpret the P5 hypothesis as confirmed until the independent NSE reconciliation completes.


## 2026-09-23 — P5 workflow recursion from broad path filters
- Event: the P5 branch workflow initially triggered on changes under docs/ and reports/ and then committed its own output files back to the same branch.
- Impact: several overlapping P5 workflow runs were started while the research files were being updated.
- Correction: the P5 workflow now triggers only for its workflow file, the two reconciliation scripts, and the NIFTY calendar source package; outputs committed by the workflow no longer retrigger it. Concurrency cancellation was also added.
- Prevention: phase workflows must never watch the output paths they themselves commit.


## 2026-09-23 — P5 reconciliation patch generation syntax error
- Event: one tool-side JavaScript patch attempt omitted a declaration before a template assignment.
- Impact: the patch was rejected before any repository write; no research artifact was changed by that failed call.
- Correction: the script patch was resent with explicit declarations and committed successfully.
- Prevention: validate tool-side patch construction before invoking repository writes.
