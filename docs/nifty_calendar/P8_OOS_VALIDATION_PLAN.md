# P8 Out-of-Sample Validation Plan — NIFTY 4-Leg Calendar

## Phase boundary

P8 is a genuinely unseen temporal validation of the P7 candidate gate on data after 31-Dec-2024. The P6 frozen strategy and the P7 threshold are not re-optimized in P8.

Validation population:
- Start: 2025-01-01.
- Data availability ceiling: the independent NSE F&O mirror's latest committed archive available to the workflow.
- P8 candidate: `calendar_balance_ratio <= 1.20`.
- No threshold search, no alternative entry filters, no post-entry adjustment, no stop-loss tuning.

## Research questions

1. Does the P7 gate retain positive gross and cost-adjusted P&L on an unseen post-2024 sample?
2. Does it reduce loss frequency/drawdown relative to the unchanged P6 protocol on the same executable OOS cycles?
3. How much OOS sample is executable under the same positive-entry-print/common-strike rules?
4. Are the OOS results robust to realistic Paytm Money brokerage, statutory STT changes, exchange-charge sensitivity and adverse slippage?
5. Which specific failure modes remain after the fixed gate?

## Aim

Independently test the fixed P7 candidate rule without changing its threshold or the P6 four-leg construction.

## Objectives

- Reconstruct each eligible NIFTY weekly cycle mechanically from 2025 onward.
- Use an independent NSE F&O bhavcopy mirror for option prices.
- Use independent NIFTY spot OPEN observations for ATM selection.
- Apply the same common-ATM, four-leg, near-expiry-exit protocol.
- Record every cycle, including non-executable/data-gap reasons.
- Evaluate baseline P6 and fixed-gate P7 side-by-side on the same executable OOS population.
- Report gross results, win rate, profit factor, maximum drawdown, worst loss, bootstrap intervals and cost-adjusted results.
- Preserve raw/compact data provenance and hashes so the run is reproducible.

## Scientific methodology

### 1. Temporal split

Development: 2022-2024.
Validation: 2025 onward only.

No 2025+ observation may be used to choose the 1.20 threshold.

### 2. Contract-calendar handling

The expiry calendar is derived from the observed market calendar and the documented NSE regime change:
- NIFTY weekly contracts remained Thursday expiries through the August 2025 cycle.
- New NIFTY weekly contracts moved to Tuesday expiry from 2-Sep-2025.
- Holiday expiries use the previous trading day.

The first OOS cycle is anchored to the last 2024 NIFTY weekly expiry and then advances mechanically through observed trading dates.

### 3. Strike and execution rules

For each cycle:
- entry = first trading session after the prior weekly expiry;
- common ATM strike = closest common listed strike to independent NIFTY spot OPEN;
- all four entry option OPEN prices must be strictly positive;
- four legs remain: long near PE, short near CE, long far CE, short far PE;
- exit = near-expiry session CLOSE for all four legs;
- one historical lot per leg;
- no adjustments.

A cycle with missing required entry/exit prints is recorded as non-executable and excluded from performance denominators.

### 4. Fixed candidate rule

```
call_ratio = far_CE_entry / near_CE_entry
put_ratio  = far_PE_entry / near_PE_entry
calendar_balance_ratio = call_ratio / put_ratio

P7 gate passes iff calendar_balance_ratio <= 1.20
```

The threshold is frozen for all P8 observations.

### 5. Data

Primary OOS option data:
- SantoshSrinivas79/NSE-FNO-Data-bank, original NSE F&O bhavcopy ZIPs.
- UDiFF format used from 8-Jul-2024 onward.

Independent spot OPEN:
- Yahoo Finance NIFTY 50 daily OPEN, queried only for OOS entry dates.

The workflow caches the mirror clone and compact parsed rows so reruns do not repeatedly download the same raw archives.

### 6. Cost model

Primary OOS net-P&L scenario:
- Paytm Money brokerage: ₹20 per executed order.
- Eight option executions per completed cycle.
- Exchange-charge sensitivity: 0.05% of option premium turnover, deliberately above the documented NSE transaction-charge level used as a conservative stress assumption.
- STT: 0.10% on option-sale premium through 31-Mar-2026; 0.15% from 1-Apr-2026.
- Stamp duty: 0.003% on option buys.
- SEBI turnover fee: 0.0001%.
- GST: 18% on brokerage, exchange and SEBI charges.
- Adverse slippage: 0, 0.5, 1.0 and 2.0 index points per execution.

The ₹20 brokerage assumption is consistent with Paytm Money's published flat F&O brokerage for newer accounts; statutory STT is applied by execution date rather than using the obsolete pre-Oct-2024 rate.

## Statistical analyses

For baseline and gated OOS samples:
- trade count;
- gross and net cumulative P&L;
- mean, median and standard deviation of cycle P&L;
- win rate;
- profit factor;
- maximum drawdown;
- worst trade;
- percentage of losses removed by the fixed gate;
- paired per-cycle difference between baseline and gated cumulative contribution;
- circular/block bootstrap 95% intervals for total P&L;
- year-wise and expiry-regime summaries;
- cost/slippage sensitivity table.

No multiple-threshold search is permitted.

## Results and inference rule

P8 is a validation phase, not a parameter-discovery phase.

The fixed gate is:
- **supported for further research** only if it shows non-negative/positive performance after the specified cost/slippage assumptions with adequate executable coverage and without a small-number-of-trades anomaly;
- **not supported** if the OOS evidence is negative or materially dependent on optimistic execution assumptions;
- **inconclusive** if data coverage or executable sample size is insufficient.

These are descriptive research conclusions, not a claim of future trading success.

## Strengths

- Genuine temporal holdout.
- Candidate threshold frozen before OOS data are scored.
- Independent NSE-derived option source.
- Independent spot-open cross-check.
- Full cycle-level audit, including missing-data failures.
- Costs and slippage explicitly stress-tested.
- P6 baseline remains unchanged and is evaluated on the same OOS executable cycles.

## Limitations

- Daily OPEN/CLOSE data do not reveal intraday bid/ask path or fill quality.
- Yahoo spot OPEN can differ from exchange timestamps/source conventions.
- The independent mirror is a secondary distribution of NSE files rather than a direct authenticated contract-note feed.
- Market-impact/liquidity and order-book depth are not observed.
- P8 does not establish live forward performance beyond the available historical window.

## Stop condition

P8 ends after one frozen OOS run, statistical/cost analysis, audit of residual losses, and a reproducible report. No additional threshold tuning is allowed inside P8.

## Deliverables

- `reports/nifty_calendar/P8_OOS_VALIDATION_REPORT_2025_ONWARD.md`
- `reports/nifty_calendar/P8_OOS_TRADE_LEDGER_2025_ONWARD.csv`
- `reports/nifty_calendar/P8_OOS_COST_SENSITIVITY_2025_ONWARD.csv`
- `reports/nifty_calendar/P8_DATA_MANIFEST_2025_ONWARD.csv`
- `docs/nifty_calendar/P8_OOS_CANDIDATE_LOCK.md`
- workflow logs/artifact bundle
