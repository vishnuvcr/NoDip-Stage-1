# Error Log

## 2026-09-23 — Wrong repository branch created before repository confirmation
- Event: an initial research branch was accidentally created in vishnuvcr/Nifty before the user specified the target repo.
- Impact: no strategy files, data, results or README changes for this study were written there; only an empty branch was created.
- Correction: target repo changed to vishnuvcr/NoDip-Stage-1; all study artifacts are being created there.
- Prevention: verify the target repository before every new research branch/phase.

## 2026-09-23 — GitHub Actions Python setup cache failure
- Event: the first NIFTY backtest workflow used setup-python pip caching without requirements.txt or pyproject.toml.
- Impact: the workflow stopped during environment setup before tests or data acquisition.
- Correction: the authoritative runner workflow does not request pip dependency caching; the branch workflow will be corrected separately.
- Prevention: either provide a dependency lock file or omit setup-python pip caching when dependencies are installed explicitly.

## 2026-09-23 — Test package import failure
- Event: pytest could not import src.nifty_calendar because src was not a Python package.
- Impact: the research execution stopped before public-data acquisition.
- Correction: added src/__init__.py and src/nifty_calendar/__init__.py.
- Prevention: import/package checks are now part of the execution path.
