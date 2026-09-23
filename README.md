# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P8 complete. P9 event-driven entry timing is open. Alternate-source discovery and the first primary-source acquisition are complete; the first event-driven timing scan is prepared but awaits execution on the corrected workflow.**

## Frozen validated reference

P8 validated the fixed calendar-balance gate on the post-2024 temporal holdout:

(far CE / near CE) / (far PE / near PE) <= 1.20

P8 conclusion: supported for further research, not promoted to live trading.

- P8 report: [reports/nifty_calendar/P8_OOS_VALIDATION_REPORT_2025_ONWARD.md](reports/nifty_calendar/P8_OOS_VALIDATION_REPORT_2025_ONWARD.md)
- P8 conclusion: [reports/nifty_calendar/P8_FINAL_RESEARCH_CONCLUSION.md](reports/nifty_calendar/P8_FINAL_RESEARCH_CONCLUSION.md)

## P9 — Event-driven intraday entry timing

### Research rule

Enter exactly once on the first eligible trading day at the first intraday timestamp when:
1. CBR <= 1.20;
2. current NIFTY permits a valid common ATM strike;
3. near CE/PE and far CE/PE are all simultaneously executable.

The four-leg structure, 1.20 gate and near-expiry close exit remain frozen. P9 tests timing only.

### Alternate data-source audit

| Source | Resolution | Expiry identity | P9 role |
|---|---|---|---|
| Hugging Face `thetrademarkk/india-index-options-1m` | 1 minute | Actual expiry files + strike/type | Primary public candidate |
| Hugging Face `rissin/nse-options-intraday` | 1 minute | Explicit expiry/strike/type | Secondary cross-check |
| Kaggle `Historical Nifty Options 2024 All Expiries` | Intraday | Expiry/trade-day file structure | 2024 development cross-check |
| GitHub `SauMStats/nifty-options-data-engine` | 1 minute query layer | Explicit expiry/trade date | Schema/query reference around Kaggle 2024 and 2026 data |
| GitHub `QuantDev-stack/OptionVault` | 1 minute + 1 second + tick/L2 samples | Explicit contract expiry/strike | Higher-fidelity licensed fallback |
| GitHub `JATINDHURVE/Indian-market-data-pipeline` | 1 minute | Expiry per contract | ICICI Breeze API fallback |

Source manifest: [reports/nifty_calendar/P9_ALTERNATE_DATA_SOURCES.csv](reports/nifty_calendar/P9_ALTERNATE_DATA_SOURCES.csv)

Detailed audit: [docs/nifty_calendar/P9_ALTERNATE_DATA_SOURCE_AUDIT.md](docs/nifty_calendar/P9_ALTERNATE_DATA_SOURCE_AUDIT.md)

### Primary source acquisition result

The first GitHub Actions acquisition run successfully downloaded the primary Hugging Face source files needed for the research:

- 170 input research cycles
- 201 unique near/far expiry files required
- 192 expiry files downloaded
- ~671.8 MB downloaded during the runner job
- 1-minute NIFTY index file downloaded
- 157/170 cycles (92.35%) have both required near and far expiry files
- 13/170 cycles are currently source-gapped because one of the needed later-2026 expiry files is absent

The acquisition manifest is cached as a research record:
[reports/nifty_calendar/P9_HF_FETCH_MANIFEST.csv](reports/nifty_calendar/P9_HF_FETCH_MANIFEST.csv)

The raw Hugging Face files were downloaded successfully on the CI runner but the first workflow cached only the manifest rather than the raw Hugging Face directory. The workflow has now been corrected to cache the actual Hugging Face raw-file directory under a stable key for subsequent scans.

### Current execution limitation

The public intraday candidates found so far expose OHLCV and expiry/strike identity, but not reliable historical bid/ask quotes in their published schemas. Therefore P9 historical testing will use the pre-registered 1-minute signal-close -> next-minute execution convention with adverse-slippage sensitivity. True bid/ask replay remains a separate execution-validation layer.

The corrected workflow also contains parquet-schema validation and the first event-driven timing scanner. A P9 performance result will not be interpreted until that scan completes successfully.

## P8 OOS reference

| Metric | Fixed P7 gate |
|---|---:|
| Executable post-2024 cycles | 86 |
| Gate trades | 42 |
| Gross P&L | ₹126,460.50 |
| Win rate | 76.19% |
| Profit factor | 5.115 |
| Gross max drawdown | ₹13,406.25 |
| Worst trade | ₹-12,502.75 |
| Net at 2-point slippage, 0.05% exchange stress | ₹64,304.41 |

These are historical modeled results, not claims of realized live fills.

## Research records

- `docs/nifty_calendar/RESEARCH_PLAN.md`
- `docs/nifty_calendar/PHASE_STATUS.md`
- `docs/nifty_calendar/ERROR_LOG.md`
- `docs/nifty_calendar/CONVERSATION_LOG.md`
