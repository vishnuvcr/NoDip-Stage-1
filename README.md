# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**P0-P8 complete. P9 event-driven entry timing is open; alternate-source audit is complete and acquisition is prepared, but numerical scoring is still blocked until timestamped files are successfully materialized and validated.**

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

### Acquisition

A Hugging Face acquisition script and manual GitHub Actions workflow have been added:

- `scripts/p9_fetch_hf_intraday.py`
- `.github/workflows/p9-data-acquisition.yml`

The workflow has not yet produced an observed run in the available GitHub connector, so raw intraday files are **not** being represented as already cached. This is an acquisition/runner issue, not evidence that the datasets are unavailable.

### Execution limitation

The public intraday candidates found so far expose OHLCV and expiry/strike identity, but not reliable historical bid/ask quotes in their published schemas. Therefore P9 historical testing will use the pre-registered 1-minute signal-close -> next-minute execution convention with adverse-slippage sensitivity. True bid/ask replay remains a separate execution-validation layer.

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