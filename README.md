# NoDip Stage 1 — NIFTY 4-Leg Calendar Research

## Current research status — 2026-09-23

**Frozen strategy. Preliminary 2022-2024 backtest completed. P5 independent-source verification is now running.**

Preliminary result on the available public NIFTY option dataset:
- 59 valid executable cycles
- Gross P&L: ₹52,827.50
- Win rate: 64.41%
- Profit factor: 2.549
- Maximum drawdown: ₹5,650
- Candidate cycles: 134
- Executable coverage: 44.0%

The result is conditional because 75 candidate cycles were rejected for incomplete executable data. It is not yet treated as a full-population performance claim.

### Frozen strategy
- First trading day after previous NIFTY weekly expiry.
- 09:15 IST market-open entry.
- ATM = nearest listed strike to NIFTY spot open.
- Buy near ATM PE.
- Sell near ATM CE.
- Buy same-strike far ATM CE.
- Sell same-strike far ATM PE.
- Far expiry = three weekly intervals after near expiry.
- Exit all four legs at near-expiry trading-day close.
- One historical lot per leg.
- No adjustments, rolling, target, stop-loss or averaging.

### Research documents
- [Research plan](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/RESEARCH_PLAN.md)
- [Strategy lock](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/STRATEGY_LOCK.md)
- [Phase status](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/PHASE_STATUS.md)
- [Backtest report](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/reports/nifty_calendar/RESULTS_2022_2024.md)
- [Robustness report](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/reports/nifty_calendar/ROBUSTNESS_2022_2024.md)
- [Cost assumptions](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/COST_ASSUMPTIONS.md)
- [Data specification](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/DATA_SPEC.md)
- [Sources and literature](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/SOURCES.md)
- [Error log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/nifty_calendar/ERROR_LOG.md)
- [Conversation log](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p5-reconciliation/docs/nifty_calendar/CONVERSATION_LOG.md)
- [P5 cycle audit](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p5-reconciliation/reports/nifty_calendar/CYCLE_AUDIT_2022_2024.csv)
- [P5 reconciliation report](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p5-reconciliation/reports/nifty_calendar/P5_RECONCILIATION_REPORT_2022_2024.md)
- [Paytm historical brokerage sensitivity](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-p5-reconciliation/reports/nifty_calendar/PAYTM_BROKERAGE_SENSITIVITY_2022_2024.csv)
- [Project rules](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/docs/PROJECT_RULES.md)

### Execution infrastructure
- [Main research runner](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/execute-nifty-calendar.yml)
- [Manual backtest workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/research-nifty-4leg-calendar-v1/.github/workflows/nifty-calendar-backtest.yml)
- [Public ticker diagnostic](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/diagnose-public-tickers.yml)
- [P5 manual reconciliation workflow](https://github.com/vishnuvcr/NoDip-Stage-1/blob/main/.github/workflows/p5-nifty-reconciliation.yml)

The next research step is independent reconciliation of the 75 rejected cycles. Paytm Money brokerage is being modeled by the documented historical client cohorts (₹10/₹15/₹20 per executed order) rather than assuming a single rate. No claim about full-period strategy performance is made until the independent validation is completed.


## NoDip NIFTY 4-Leg Calendar Research — latest status 2026-09-23

**P0-P6 complete for the 2022-2024 study.** The frozen strategy specification was preserved throughout the research.

Final independently reconciled result:
- 134 candidate cycles
- 132 complete cycles on the independent NSE F&O public mirror (98.5% coverage)
- all 75 primary-source rejected cycles recovered
- gross P&L ₹127,185.00
- win rate 57.58%
- profit factor 1.542
- maximum drawdown ₹90,152.50
- circular 3-cycle block-bootstrap 95% interval for total gross P&L: ₹-67,517.25 to ₹342,106.84

The original primary-source backtest remains preserved as provenance: 59 executable cycles, gross P&L ₹52,827.50, and 44.0% primary-source coverage. The independent reconciliation shows that this 44.0% figure was mainly a source-coverage limitation.

Research branch: research-nifty-4leg-calendar-p6-manuscript

Final manuscript: reports/nifty_calendar/MANUSCRIPT_NIFTY_4LEG_CALENDAR_2022_2024.md

Phase status: docs/nifty_calendar/PHASE_STATUS.md

P6 validation workflow: .github/workflows/p6-nifty-manuscript.yml
