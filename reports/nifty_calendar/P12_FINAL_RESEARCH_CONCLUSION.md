# P12 Final Research Conclusion — Far-Expiry Selection

## Research question

Test the fixed four-leg NIFTY structure with the far expiry set to 1, 2, 3 or 4 listed weekly expiries after the near expiry, and define an entry-time rule to choose among them.

## Frozen entry rule

- Entry: D+1 trading session after previous expiry, 09:15 IST.
- Near expiry: next listed expiry.
- Far candidates: F+1, F+2, F+3, F+4 subsequent listed expiries.
- Position: short near CE, long near PE, long far CE, short far PE.
- Same near-expiry ATM strike across far-expiry candidates.
- Exit: near-expiry close.
- No CBR gate was imposed in the primary P12 experiment.

## Entry-time far-expiry selection rule

For each eligible candidate at 09:15:

score = (near_CE - near_PE + far_PE - far_CE) / spot_open

Eligibility requires the same ATM strike and positive entry price/volume for all four legs.

Select the candidate with the highest score. This uses entry information only and never uses the future exit or P&L.

## Evaluation results

The 2025+ evaluation period was already exposed during P10, so these results are exploratory rather than fresh confirmatory OOS validation.

### Development, 2022-2024

| Strategy | Trades | Gross P&L | PF | Net @ 2 pt |
|---|---:|---:|---:|---:|
| F+1 | 153 | ₹38,051 | 1.359 | -₹110,409 |
| F+2 | 152 | ₹57,794 | 1.403 | -₹91,796 |
| F+3 | 129 | ₹28,909 | 1.229 | -₹98,699 |
| F+4 | 75 | ₹50,744 | 1.630 | -₹24,390 |
| Adaptive | 155 | ₹143,106 | 2.869 | -₹8,325 |

### 2025+ evaluation period

| Strategy | Trades | Gross P&L | PF | Net @ 2 pt |
|---|---:|---:|---:|---:|
| F+1 | 72 | ₹29,543 | 1.321 | -₹76,676 |
| F+2 | 73 | -₹23,166 | 0.836 | -₹132,051 |
| F+3 | 64 | ₹33,142 | 1.288 | -₹62,957 |
| F+4 | 42 | ₹90,237 | 2.373 | ₹26,958 |
| Adaptive | 77 | ₹144,278 | 2.763 | ₹30,311 |

Adaptive selection frequency in the evaluation period was F+1 59/77, F+2 8/77, F+3 6/77 and F+4 4/77.

## Interpretation

1. Far-expiry choice materially changes the economics of this structure.
2. In the evaluation period, F+2 was the weakest fixed horizon; F+4 was the only fixed horizon with positive net P&L at the project's 2-point adverse-slippage stress.
3. The entry-credit adaptive rule produced ₹30,311 net at the same 2-point stress, slightly above fixed F+4, while generating more trades.
4. On paired executable cycles, the adaptive rule had positive mean P&L differences versus every fixed horizon in both development and evaluation periods. These paired comparisons are descriptive and were not multiplicity-adjusted.
5. The adaptive rule was not optimized against evaluation-period P&L, but the evaluation period was already exposed by P10. Therefore the result is hypothesis-supporting, not confirmatory.

## Main limitation

The daily option source supplies OHLCV, not historical bid/ask quotes. Brokerage, statutory charges, exchange-charge stress and adverse slippage are modeled. These are not observed Paytm Money fills.

## Research decision

P12 is COMPLETE as an exploratory far-expiry research phase.

The result is not promoted to live or confirmed paper deployment. The far-expiry adaptive rule and F+4 fixed horizon both require a genuinely fresh post-P10 holdout before any promotion decision.

No additional far-expiry horizons or score weights are searched in P12.

## Repository records

- docs/nifty_calendar/P12_FAR_EXPIRY_SELECTION_PLAN.md
- reports/nifty_calendar/P12_FAR_EXPIRY_SELECTION_REPORT.md
- reports/nifty_calendar/P12_FAR_EXPIRY_SUMMARY.csv
- reports/nifty_calendar/P12_FAR_EXPIRY_COST_SENSITIVITY.csv
- reports/nifty_calendar/P12_ADAPTIVE_SELECTION.csv
- reports/nifty_calendar/P12_ADAPTIVE_PAIRED_COMPARISONS.csv
- reports/nifty_calendar/P12_FAR_EXPIRY_LEDGER.csv