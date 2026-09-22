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