# P7 Losing-Trade Audit and Entry-Tuning Report — NIFTY 4-Leg Calendar — 2022-2024

## Scope
- P6 strict validation population: 84 cycles.
- P7 does not modify or replace the P6 frozen result.
- The proposed entry screen is a candidate rule for a future validation phase.

## Loss audit
- Total trades: 84
- Losing trades: 32 (38.10%)
- Total gross P&L: ₹81,117.50
- Aggregate losses: ₹-42,747.50
- Mean loss: ₹-1,335.86
- Median loss: ₹-938.75

### Loss mechanism by near-expiry legs

| Loss reason | Count | Share of losses | Gross loss |
|---|---:|---:|---:|
| BOTH_NEAR_ADVERSE | 20 | 62.5% | ₹-33,155.00 |
| BOTH_NEAR_FAVORABLE_BUT_FAR_OFFSETTING | 6 | 18.8% | ₹-1,832.50 |
| NEAR_PUT_ADVERSE | 6 | 18.8% | ₹-7,760.00 |

### Entry-feature separation: losing vs winning trades

| Feature | Loss median | Winner median |
|---|---:|---:|
| calendar_balance_ratio | 1.278 | 1.062 |
| call_ratio | 2.565 | 2.211 |
| put_ratio | 1.885 | 2.123 |
| entry_debit_ratio | 0.092 | 0.064 |
| calendar_asymmetry | 0.256 | 0.178 |

### Leg contribution finding
- Both near-expiry legs were individually adverse in 20 of 32 losses.
- Both far-expiry legs were individually favorable in 19 of 32 losses.

## Candidate entry gate

Enter only when calendar-balance ratio <= 1.20.

calendar-balance ratio = (far CE entry / near CE entry) / (far PE entry / near PE entry)

This is an entry-time condition. It uses no future P&L, exit information or post-entry adjustment.

### Candidate population effect
- Retained cycles: 52 / 84 (61.9%).
- Gross P&L: ₹83,068.75.
- Win rate: 78.85%.
- Profit factor: 8.289.
- Maximum drawdown: ₹3,355.00.
- Bootstrap 95% interval: ₹nan to ₹nan.
- Losses filtered: 22 of 32 (68.8%).
- Aggregate loss removed from the retained sample: ₹-31,351.25.
- Remaining losses: 10.

### Development/temporal diagnostic

| Population | Baseline gross P&L | Candidate gross P&L |
|---|---:|---:|
| 2022-2023 development | ₹43,375.00 | ₹61,367.50 |
| 2024 temporal holdout | ₹37,742.50 | ₹21,701.25 |

| Population | Baseline trades | Candidate trades | Baseline win | Candidate win |
|---|---:|---:|---:|---:|
| 2022-2023 | 53 | 36 | 58.49% | 77.78% |
| 2024 | 31 | 16 | 64.52% | 81.25% |

The 2024 line is a temporal diagnostic, not a clean independent confirmation, because the full 2022-2024 sample was inspected during research. A future post-2024 holdout is required before promoting this gate.

## Threshold sensitivity
|   threshold |   all_n |   all_gross_pnl |   all_win_rate |   all_profit_factor |   all_max_drawdown |   all_conservative_net20_2pt |   train_n_2022_2023 |   train_gross_pnl_2022_2023 |   train_conservative_net20_2pt |   test_n_2024 |   test_gross_pnl_2024 |   test_conservative_net20_2pt |
|------------:|--------:|----------------:|---------------:|--------------------:|-------------------:|-----------------------------:|--------------------:|----------------------------:|-------------------------------:|--------------:|----------------------:|------------------------------:|
|        1.15 |      45 |         75126.2 |       0.777778 |             8.48363 |            -3355   |                      31538.1 |                  33 |                     57902.5 |                        22680.1 |            12 |               17223.8 |                       8858.07 |
|        1.2  |      52 |         83068.8 |       0.788462 |             8.28913 |            -3355   |                      32896.6 |                  36 |                     61367.5 |                        23002.4 |            16 |               21701.2 |                       9894.18 |
|        1.25 |      56 |         82423.8 |       0.767857 |             7.18855 |            -4752.5 |                      27957.2 |                  40 |                     60722.5 |                        18063   |            16 |               21701.2 |                       9894.18 |
|        1.3  |      62 |         76827.5 |       0.709677 |             5.01923 |            -4752.5 |                      16465.4 |                  44 |                     59670   |                        12814.4 |            18 |               17157.5 |                       3651    |

## Conservative cost check
- Candidate net P&L at ₹20/order brokerage, 0.05000% exchange charges and 2-point adverse slippage: ₹32,896.55.

## Interpretation
The largest recurring loss mechanism is front-expiry deterioration: both near-expiry legs are adverse in most losing trades, while the far legs are often favorable. The candidate balance ratio is intended to screen out entry configurations where the call calendar is disproportionately richer than the put calendar.

The 1.20 threshold is a candidate research parameter, not a claimed optimal parameter. It must be frozen before any genuinely unseen post-2024 validation.

## Backtest-overfitting control
Finance research literature warns that repeatedly searching historical variants can create apparently strong in-sample results that fail out of sample. This phase therefore keeps one interpretable candidate gate, reports alternative thresholds, and explicitly reserves post-2024 data for future validation.

## Reproducibility
- docs/nifty_calendar/P7_LOSS_AUDIT_PLAN.md
- docs/nifty_calendar/P7_ENTRY_CRITERIA_LOCK.md
- reports/nifty_calendar/LOSS_AUDIT_2022_2024.csv
- reports/nifty_calendar/LOSS_TOP_TRADES_2022_2024.csv
- reports/nifty_calendar/ENTRY_FILTER_GRID_2022_2024.csv
- reports/nifty_calendar/ENTRY_CRITERIA_CANDIDATE_2022_2024.md