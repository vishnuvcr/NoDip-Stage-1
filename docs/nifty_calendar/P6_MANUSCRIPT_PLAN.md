# P6 Manuscript Plan — NIFTY 4-Leg Calendar — 2022-2024

## Objective
Convert the validated P0-P5 research record into a reproducible research manuscript without changing the frozen strategy.

## Required sections
1. Title, abstract and keywords.
2. Research questions and hypotheses.
3. Background and literature review.
4. Data sources, historical expiry calendar, lot sizes and transaction-cost assumptions.
5. Frozen strategy specification and mechanical execution protocol.
6. Statistical methodology, coverage audit, cross-source validation and bootstrap procedure.
7. Primary-source and independent-secondary-source results.
8. Execution-cost and Paytm Money sensitivity analysis.
9. Discussion of the 75 previously rejected cycles and source-coverage bias.
10. Strengths, limitations, reproducibility and threats to validity.
11. Conclusion and future research.
12. Trade-level and source-reconciliation appendices.
13. Supplementary data/code/workflow index.

## Final validated result basis
- Candidate cycles: 134.
- Primary public-source executable cycles: 59/134.
- Independent secondary-source executable cycles: 132/134.
- All 75 primary rejected cycles are complete on the independent public mirror of NSE F&O bhavcopy.
- Two primary-valid cycles remain unconstructible on the independent source because that source has no common strike.
- Independent-secondary gross P&L: ₹127,185.00 across 132 complete cycles.
- Independent-secondary win rate: 57.58%.
- Independent-secondary profit factor: 1.542.
- Independent-secondary maximum drawdown: ₹90,152.50.
- Three-trade circular-block bootstrap 95% interval for total gross P&L: approximately ₹-67,517 to ₹342,107.

## Figures
- Cumulative gross P&L.
- Drawdown.
- Annual gross P&L.
- Net P&L cost sensitivity.

## Non-goals
- No strategy parameter changes.
- No post-hoc entry/exit filters.
- No optimization of the frozen rule.
- No claim that daily OHLC guarantees executable bid/ask fills.
- No exact historical Paytm Money exchange pass-through rate unless contract-note evidence is available.

## Completion criterion
P6 closes when the manuscript, figures, appendices, source/coverage audit, cost sensitivity and phase/README links are committed and internally consistent.
