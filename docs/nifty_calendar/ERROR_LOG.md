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
