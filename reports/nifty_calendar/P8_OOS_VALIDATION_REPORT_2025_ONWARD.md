# P8 Out-of-Sample Validation Report — NIFTY 4-Leg Calendar

## Frozen validation design
- Development sample: 2022-2024.
- Unseen OOS sample: 2025 onward.
- Frozen candidate gate: calendar-balance ratio <= 1.20.
- No additional threshold or filter search was permitted.

## Coverage
- Scheduled cycles: 88
- Executable cycles: 86
- Non-executable cycles: 2
- Gate-pass cycles: 42 (48.8%)

## Gross performance

| Metric | P6 baseline | P7 fixed gate |
|---|---:|---:|
| Cycles | 86 | 42 |
| Gross P&L | ₹-24,361.25 | ₹126,460.50 |
| Mean cycle | ₹-283.27 | ₹3,010.96 |
| Median cycle | ₹245.62 | ₹2,390.63 |
| Win rate | 53.49% | 76.19% |
| Profit factor | 0.883 | 5.115 |
| Max drawdown | ₹90,742.50 | ₹13,406.25 |
| Worst trade | ₹-21,513.75 | ₹-12,502.75 |

## Bootstrap 95% intervals
- P6 baseline: ₹-176,463.88 to ₹117,347.48
- P7 fixed gate: ₹65,611.61 to ₹196,757.32

## Loss audit
- Baseline losses: 40
- Losses skipped by fixed gate: 30
- Winning cycles skipped by fixed gate: 14
- Residual gate-pass losses: 10

## Cost model
- Paytm Money brokerage: ₹20 per executed order.
- Eight option executions per completed cycle.
- STT: 0.10% on option-sale premium through 31-Mar-2026; 0.15% from 1-Apr-2026.
- Stamp duty: 0.003% on option buys.
- SEBI fee: 0.0001%.
- GST: 18% on brokerage, exchange and SEBI charges.
- Exchange-charge sensitivity: 0.05% stress case.
- Adverse slippage: 0, 0.5, 1 and 2 index points per execution.

| sample        |   slippage_points |   exchange_rate |   n |   net_pnl_inr |
|:--------------|------------------:|----------------:|----:|--------------:|
| P6_baseline   |               0   |          0.0005 |  86 |      -55347.6 |
| P7_fixed_gate |               0   |          0.0005 |  42 |      111664   |
| P6_baseline   |               0.5 |          0.0005 |  86 |      -79687.6 |
| P7_fixed_gate |               0.5 |          0.0005 |  42 |       99824.4 |
| P6_baseline   |               1   |          0.0005 |  86 |     -104028   |
| P7_fixed_gate |               1   |          0.0005 |  42 |       87984.4 |
| P6_baseline   |               2   |          0.0005 |  86 |     -152708   |
| P7_fixed_gate |               2   |          0.0005 |  42 |       64304.4 |

## Interpretation
P8 is a temporal validation of a pre-frozen historical candidate. Positive OOS evidence is limited to the observed holdout and execution assumptions; it is not a guarantee of future performance.

## Strengths and limitations
- Strengths: genuine temporal holdout, frozen threshold, independent NSE-derived option archive, independent spot-open input, full executable-cycle audit and explicit cost/slippage stress.
- Limitations: daily OHLC does not reconstruct intraday bid/ask paths; no market-impact model; mirror is a redistribution of exchange archives; Yahoo OPEN may differ slightly from exchange timestamp conventions.

## Reproducibility
- scripts/p8_prepare_cycles.py
- scripts/p8_fetch_spot.py
- scripts/p8_build_audit_input.py
- scripts/reconcile_rejections_nse.py
- reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv
- reports/nifty_calendar/P8_OOS_COST_SENSITIVITY_2025_ONWARD.csv

## Frozen mirror provenance
NSE F&O mirror commit: c052a3f880ac8f5deeef2f85a16c172b91cecba1
Validation boundary is the committed mirror snapshot used by this workflow.
