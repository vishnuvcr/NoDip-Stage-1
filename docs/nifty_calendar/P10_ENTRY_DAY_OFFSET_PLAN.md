# P10 Entry-Day Offset Research Plan

## Research question
Keeping the frozen 09:15 entry time, CBR<=1.20 gate, four-leg structure and near-expiry exit unchanged, does changing the entry session relative to the previous expiry improve robustness?

## Pre-registered entry sessions
- D-1: trading session immediately before the previous expiry.
- D0: previous-expiry trading session.
- D+1: first trading session after the previous expiry.
- D+2, D+3, D+4, D+5: subsequent NSE trading sessions.

These are trading-session offsets, not calendar-day offsets. A candidate occurring after the near-expiry date is classified as AFTER_NEAR_EXPIRY and excluded from execution.

## Frozen criteria
- 09:15 IST daily open.
- CBR <= 1.20.
- Same common ATM strike for near/far CE/PE, selected using the contemporaneous NIFTY opening spot.
- Buy near PE, sell near CE, buy far CE, sell far PE.
- Exit all four legs at the near-expiry close.
- Historical lot sizes preserved by expiry date.
- No stop-loss, target, roll, averaging or intraday timing optimization.

## Statistical design
1. Screen all seven offsets on 2022-2024 development data.
2. Report OOS results for all seven offsets on 2025+ without selecting on OOS.
3. Compare each offset against D+1 on the same underlying expiry cycles using cycle-level strategy P&L, where non-trade = zero contribution.
4. Keep brokerage, statutory charges, exchange stress and 0/0.5/1/2 point adverse slippage explicit.
5. If a single offset is later considered for promotion, choose it using a pre-registered development-only rule and validate it on a fresh unseen period.

## Data
- Independent NSE F&O mirror: SantoshSrinivas79/NSE-FNO-Data-bank.
- NIFTY opening spot: Yahoo chart daily NIFTY index.
- Historical lot sizes and file schema from the already audited P5/P8 parsers.

## Outputs
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_LEDGER.csv
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_SUMMARY.csv
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_PAIRED.csv
- reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_REPORT.md

## Stop condition
Stop after the seven offsets have been evaluated on development and unseen OOS samples, with cost/slippage sensitivity and execution-coverage diagnostics. No additional entry-day offsets are searched in P10.