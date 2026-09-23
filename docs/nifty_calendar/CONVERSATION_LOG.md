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


## 2026-09-23 — P5 independent reconciliation completed
- The independent public mirror of NSE F&O bhavcopy was used for the full 134-cycle candidate set.
- Result: 132/134 candidate cycles are complete on the independent source (98.5% coverage).
- All 75 cycles rejected by the primary source were recovered as complete secondary-source cycles.
- 57 of the 59 primary-valid cycles were also complete on the independent source.
- Two primary-valid cycles (2023-06-02 and 2023-06-23) lacked a common strike on the independent source and remain classified as source discrepancies.
- Secondary complete-cycle gross P&L: ₹127,185.00 across 132 cycles; win rate 57.58%; profit factor 1.542; maximum drawdown ₹90,152.50.
- The 59-trade primary-source result remains in the manuscript as a source-coverage comparison rather than the final population result.
- Full secondary trade-level price ledger and Paytm Money brokerage/exchange/slippage sensitivity are now cached in the repository.
- P5 is COMPLETE. P6 manuscript phase is now in progress.


## 2026-09-23 — Final P5/P6 correction and manuscript completion
- Final verification identified zero-open option observations with zero contract volume as non-executable; those observations were removed from fill eligibility rather than treated as fills.
- Corrected independent reconciliation: 57 primary-valid cycles reproduced; 27 primary rejects recovered at the same strike; 28 source-specific strike-reselection cycles retained as sensitivity only; 20 primary rejects remain non-executable; 2 primary-valid cycles remain source-discrepant.
- Final strict frozen-protocol validation sample: 84 cycles of 134 candidates (62.7% coverage).
- Final strict gross P&L: ₹83,030.00; mean ₹988.45; median ₹598.75; win rate 61.90%; profit factor 2.942; maximum drawdown ₹8,022.50.
- Final 3-cycle circular-block bootstrap 95% interval: ₹31,147 to ₹139,294.
- Final cost sensitivity at 0.05000% exchange-charge assumption remains positive at ₹20/order brokerage and 2.00-point adverse slippage: approximately ₹1,206.81.
- P6 manuscript, figures, strict trade ledger, annual results and cost-sensitivity files were rebuilt and committed on research-nifty-4leg-calendar-p6-manuscript.


## 2026-09-23 — P7 loss-trades audit completed
- User requested an audit of losing trades, reasons for losses, and ways to improve the structure.
- Dedicated branch created: research-nifty-4leg-calendar-p7-loss-audit.
- All 32 losing trades in the strict 84-cycle baseline were audited.
- Total losing-trade loss: ₹42,747.50 across 32 trades; winning trades contributed ₹125,777.50, so losses offset about 34.0% of winning P&L.
- Near-expiry PE and CE contributions across losing trades were ₹-79,366.25 and ₹-91,253.75; far-expiry CE and PE contributed ₹52,385.00 and ₹75,487.50.
- 19/32 losses showed a bullish-like front-week adverse payoff signature, accounting for 72.1% of absolute loss.
- Losing trades had higher mean initial net debit (₹81.33 vs ₹51.45 for non-losses), lower near-call/far-call ratio (0.409 vs 0.455), and higher near-put/far-put ratio (0.529 vs 0.475).
- Exploratory filters were tested. The combined call/put balance filter kept 28/84 trades, raised in-sample win rate to 85.71% and reduced max drawdown to ₹1,027.50, but gross P&L fell to ₹63,415 and the small retained sample creates substantial selection-bias risk.
- No intraday stop-loss recommendation was accepted because daily entry/expiry-close data cannot establish the path or executable stop fills.
