# P7 Loss-Trades Audit Plan — NIFTY 4-Leg Calendar — 2022-2024

## Purpose

Audit every losing trade in the final strict 84-cycle frozen-protocol sample, identify the mechanical source of losses, and test a small set of pre-specified risk/selection hypotheses without overwriting the frozen historical baseline.

## Research questions

1. How many strict trades lose money and how much of total P&L do they consume?
2. Which of the four legs is the main source of loss on losing trades?
3. Do losses cluster around identifiable entry-state features such as initial net debit, near/far call-premium ratio, or near/far put-premium ratio?
4. Are losses dominated by a directional signature, by the near-expiry legs, or by far-expiry repricing?
5. Which simple improvement candidates reduce loss frequency/drawdown without simply discarding too much profitable exposure?
6. Can any proposed improvement be considered validated, or only exploratory, given the 84-trade sample and lack of intraday bid/ask data?

## Scope and frozen baseline

The main historical result remains unchanged:
- 134 candidate cycles.
- 84 strict independently validated cycles using the frozen primary strike.
- 28 source-specific strike-reselection cycles remain separate sensitivity evidence.
- 20 primary rejects remain unresolved on the independent source.
- 2 primary-valid cycles remain source-discrepant.

No P7 filter or risk rule may rewrite the P0-P6 historical result.

## Audit steps

### P7.1 — Loss ledger
Status: COMPLETE when generated.
Create a row-level audit for all strict losing trades with:
- four leg P&Ls;
- total P&L;
- initial net debit;
- near/far premium ratios;
- loss signature;
- loss concentration rank.

### P7.2 — Loss attribution
Status: COMPLETE when generated.
Quantify:
- loss count and loss sum;
- contribution of each leg;
- directional/signature categories;
- year-by-year loss concentration;
- contribution of the largest losses.

### P7.3 — Improvement hypotheses
Status: COMPLETE when generated.
Test a small fixed set:
- initial net debit <= ₹80;
- near-call/far-call premium ratio >= 0.45;
- near-put/far-put premium ratio <= 0.55;
- combined call/put balance filter.

These are exploratory historical hypotheses, not changes to the frozen strategy.

### P7.4 — Cost-aware sensitivity
Status: COMPLETE when generated.
Recalculate gross and modeled net P&L for each candidate filter under:
- ₹10/₹15/₹20 Paytm Money historical brokerage cohorts;
- 0.05000% exchange-charge sensitivity;
- 0, 0.50, 1.00 and 2.00 index-point adverse slippage per execution.

### P7.5 — Robustness interpretation
Status: COMPLETE when generated.
Assess whether a candidate materially improves:
- gross P&L;
- win rate;
- profit factor;
- maximum drawdown;
- worst trade;
- retained trade count.

No candidate is considered a validated strategy improvement unless it survives a separate out-of-sample test.

## Important limitation

A stop-loss or intratrade adjustment cannot be validated from the current daily entry/expiry-close dataset because the historical path between entry and exit is not observed. Tick/bid/ask data are required for a credible intratrade stop/hedge study.

## Stop condition

P7 ends after the row-level loss audit, attribution, fixed-hypothesis sensitivity, and cost analysis. It does not become an open-ended optimization phase.
