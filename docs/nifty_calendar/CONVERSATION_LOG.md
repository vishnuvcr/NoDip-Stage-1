# Conversation / Decision Log

## 2026-09-23
- User requested a simple NIFTY backtest for a four-leg structure:
  1. buy weekly ATM PE
  2. sell weekly ATM CE
  3. buy CE three weeks later
  4. sell PE three weeks later
  5. exit all legs at weekly expiry
- User fixed entry timing: first trading day after the previous expiry, morning open.
- Strategy was requested to be locked.
- User specified the research repository: https://github.com/vishnuvcr/NoDip-Stage-1.
- Frozen interpretation: entry at 09:15 IST open; exit at near-expiry close; no discretionary changes.
- User said "Ok proceed" and research execution began.
- CI failures were diagnosed and logged:
  - setup-python cache configuration
  - source-package import path
  - public archive month manifest
  - public NIFTY ticker schema (C/P vs CE/PE)
  - source-to-engine label normalization
  - pandas 3.x lot-size dtype assignment
- A successful GitHub Actions run completed the 2022-2024 preliminary backtest.
- Preliminary result: 59 valid executable cycles, gross P&L ₹52,827.50, 64.41% win rate, profit factor 2.549, max drawdown ₹5,650.
- Coverage audit: 134 candidate cycles were examined; 75 were rejected (9 no common strike, 62 missing entry leg, 4 missing exit leg), leaving 44.0% executable coverage.
- Robustness work added exact leg-specific slippage sensitivity, documented brokerage/statutory cost treatment, exchange-charge sensitivity and a reproducible trade-cost analysis script.
- Current phase state: P0-P4 complete; P5 robustness/independent reconciliation in progress; P6 manuscript pending.
- Latest user instruction: "Ok proceed".


## 2026-09-23 — P5 independent reconciliation initiated
- User confirmed continuation of the research.
- A dedicated P5 branch was created: research-nifty-4leg-calendar-p5-reconciliation.
- Added a full candidate-cycle audit that records the primary rejection reason, selected common strike, missing legs and primary leg prices.
- Added an independent NSE bhavcopy reconciliation script covering the full candidate set and an independent Yahoo NIFTY spot-open cross-check.
- Added manual-run and push-triggered GitHub Actions workflows with cached primary and secondary data.
- The first P5 execution is currently running on GitHub Actions; no independent-source result has been interpreted yet.
