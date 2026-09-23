# Final Research Manuscript — NIFTY 4-Leg Calendar Strategy

## Abstract

This study evaluates a frozen four-leg NIFTY calendar strategy using a 09:15 IST entry, a calendar-balance-ratio (CBR) gate of <=1.20, a common ATM strike across near/far expiries, and exit at the near-expiry close. The research proceeded through specification freeze, independent verification, loss-trade audit, unseen post-2024 validation, event-driven timing analysis, and a seven-offset entry-day screen. The final fixed-offset screen tested D-1, D0, D+1, D+2, D+3, D+4 and D+5 relative to the previous expiry.

The main empirical result is that the seven-offset OOS screen contains several positive net-P&L observations under the modeled cost framework, especially D0 and D+2. However, the paired OOS bootstrap does not statistically distinguish D0 or D+2 from the canonical D+1 reference, and no offset is promoted directly from OOS. A deterministic development-only selection rule later identifies D-1, but the required fresh post-P10 validation cannot yet be executed because the pinned intraday option source contains no completed cycle after the P10 cutoff. The research therefore stops at a data-availability gate rather than reusing the same OOS observations or searching further parameters.

## 1. Research Questions

1. Does the frozen four-leg structure produce positive executable returns after explicit costs and slippage?
2. Is the CBR<=1.20 gate robust on an unseen temporal holdout?
3. Does event-driven intraday timing improve on the frozen 09:15 entry?
4. Does changing only the entry session relative to the previous expiry materially alter results?
5. Does a development-selected entry offset survive a genuinely later unseen period?

## 2. Strategy Specification

| Component | Frozen rule |
|---|---|
| Entry time | 09:15 IST |
| Gate | CBR <= 1.20 |
| Structure | Buy near PE, sell near CE, buy far CE, sell far PE |
| Strike | Nearest common ATM strike; 25-point ATM QC |
| Exit | Near-expiry close |
| Position size | One historical lot per leg |
| Adjustments | None |
| Cost stress | Brokerage/statutory/exchange-charge model + 0/0.5/1/2-point adverse slippage |

## 3. Data and Validation

The 2022-2024 public-source history was independently reconciled. The P8 temporal holdout used post-2024 data. P9 used a secondary Rissin/Upstox 1-minute option source for intraday timing validation. P10 used the same historical daily option source for the seven-offset screen. All numerical outputs are preserved in the repository ledgers and error log.

## 4. P7 Loss Audit

The strict 84-cycle baseline contained 32 losing trades. The loss audit identified a recurring adverse payoff signature and proposed CBR<=1.20 as a candidate filter. The frozen P6 strategy itself was not rewritten; the filter was carried forward for independent validation.

## 5. P8 Unseen Validation

The CBR<=1.20 gate was tested unchanged on the post-2024 temporal holdout. The result supported further research but was not promoted to live trading. The canonical P8 fixed-time reference remains the 09:15 entry with the frozen gate.

## 6. P9 Event-Driven Timing

Event-driven first-qualifying entry was tested while keeping the structure and CBR threshold fixed. After source-quality and ATM-selection controls, the event-driven approach produced weaker paired results than the canonical fixed 09:15 control and was not promoted. Modeled event-driven net P&L became negative at 0.5-point adverse slippage and above.

## 7. P10 Entry-Day Offset Experiment

### 7.1 Design

Seven trading-session offsets were pre-registered: D-1, D0, D+1, D+2, D+3, D+4 and D+5. The entry time, CBR threshold, four-leg construction, strike semantics, exit and cost model were held fixed.

### 7.2 OOS results

| Offset | Trades | Gross P&L | PF | Net @ 0.5 pt | Net @ 1 pt | Net @ 2 pt |
|---|---:|---:|---:|---:|---:|---:|
| D-1 | 44 | ₹90,808 | 2.922 | ₹61,646 | ₹49,046 | ₹23,846 |
| D0 | 42 | ₹133,758 | 11.925 | ₹105,830 | ₹93,850 | ₹69,890 |
| D+1 | 36 | ₹99,993 | 4.540 | ₹76,972 | ₹66,692 | ₹46,132 |
| D+2 | 44 | ₹129,108 | 8.100 | ₹101,128 | ₹88,548 | ₹63,388 |
| D+3 | 36 | ₹50,454 | 1.993 | ₹27,869 | ₹17,629 | -₹2,851 |
| D+4 | 33 | ₹80,699 | 3.834 | ₹60,178 | ₹50,838 | ₹32,158 |
| D+5 | 19 | ₹17,240 | 2.359 | ₹5,865 | ₹485 | -₹10,275 |

### 7.3 Paired robustness against D+1

D0 had mean paired difference +₹383.69 with bootstrap 95% CI -₹797.17 to +₹1,480.94. D+2 had mean +₹330.85 with CI -₹445.32 to +₹1,099.05. D-1, D+3 and D+4 also had confidence intervals spanning zero. D+5 had mean -₹940.37 with CI -₹1,975.86 to -₹69.96. These intervals are unadjusted for the seven-comparison screen and are therefore descriptive robustness statistics rather than confirmatory multiple-testing results.

### 7.4 Interpretation

The OOS screen shows that entry timing within the expiry cycle matters materially in the sample. Nevertheless, raw P&L alone cannot justify a timing switch because D0 and D+2 were not statistically separated from D+1 in the paired OOS bootstrap. The later offsets D+3 and D+5 also show noticeably weaker cost robustness.

## 8. P11 Fresh Validation Gate

A development-only selection rule was preregistered after P10: require >=90% development executable coverage and PF>2, then select the highest development net P&L at 2-point adverse slippage. Under the 2022-2024 development data this rule selects D-1.

The fresh-validation cutoff was fixed at 2026-08-26, the end of the P10 OOS entry sample. When P11 was executed, the pinned option-data source available to the runner ended at 2026-06-29, so there were zero completed fresh cycles after the cutoff. P11 therefore could not be evaluated without contaminating the fresh holdout with already-used observations.

### P11 decision

**PAPER-MONITORING ONLY / INSUFFICIENT FRESH SAMPLE**

This is a data-availability stop, not evidence of strategy failure.

## 9. Statistical and Economic Interpretation

The research supports the following statements:

- The frozen four-leg structure has generated positive sample outcomes under several historical configurations.
- CBR<=1.20 survived one temporal holdout and remained a useful frozen research gate.
- Event-driven entry did not improve the canonical fixed 09:15 entry under the tested source and cost model.
- The seven entry-day offsets exhibit heterogeneous results, but OOS paired evidence does not identify a statistically distinct replacement for D+1.
- Cost and execution assumptions remain economically material.
- A future unseen validation period is required before a development-selected offset can be considered validated.

The research does not establish a population-level guaranteed edge, exact real-world broker fill performance, or live-trading readiness.

## 10. Strengths

Chronology was preserved across phases; the main timing experiment was preregistered; source-quality errors were logged; independent reconciliation was performed; non-executable cycles were retained rather than extrapolated; execution costs were made explicit; and OOS observations were not used to choose an offset inside P10.

## 11. Limitations

1. Intraday option history remains limited in the pinned public source.
2. Historical bid/ask quotes are unavailable in the Rissin/Upstox source used for P9/P10, so slippage is modeled rather than observed.
3. The fresh P11 holdout could not be populated from the pinned source.
4. The seven-offset paired bootstrap was not adjusted for multiplicity.
5. P10 is still a relatively small historical sample, so tail and regime dependence remain important.
6. No real-money execution or broker-fill ledger was used.

## 12. Conclusion

The final NoDip Stage-1 research state is a **closed historical research result with a prospective validation gate**, not a live-trading approval. The canonical strategy remains the frozen 09:15 entry with CBR<=1.20 and no discretionary adjustments. P10 demonstrates that D0 and D+2 can look stronger than D+1 in a historical OOS screen, but that result does not by itself justify replacing D+1. The preregistered P11 selection rule chooses D-1 from development data, yet there is currently no unseen completed sample in the pinned option dataset on which to validate D-1.

Accordingly, the scientifically defensible stop point is: **do not search additional entry offsets or retune the rule on the existing data. Resume only when a genuinely fresh post-cutoff expiry cycle is available, then run the already-frozen P11 workflow and record the result without changing the selection rule.**

## 13. Future Research

1. Add completed post-P10 1-minute option data to the pinned cache.
2. Run the existing P11 D-1 fresh validation without changing its selection rule.
3. Validate timestamped executable quotes/spreads when a licensed source permits it.
4. Extend the final cost model with the complete Paytm Money schedule used operationally, keeping modeled and observed costs separate.
5. Conduct prospective paper trading without retuning during the monitoring period.

## 14. Repository Records

- P10 report: `reports/nifty_calendar/P10_ENTRY_DAY_OFFSET_REPORT.md`
- P10 conclusion: `reports/nifty_calendar/P10_FINAL_RESEARCH_CONCLUSION.md`
- P10 paired bootstrap: `reports/nifty_calendar/P10_OOS_PAIRED_BOOTSTRAP.md`
- P11 plan: `docs/nifty_calendar/P11_FORWARD_VALIDATION_PLAN.md`
- P11 report: `reports/nifty_calendar/P11_FORWARD_VALIDATION_REPORT.md`
- P11 conclusion: `reports/nifty_calendar/P11_FINAL_RESEARCH_CONCLUSION.md`
- P11 ledger: `reports/nifty_calendar/P11_FORWARD_TRADE_LEDGER.csv`
- Error log: `docs/nifty_calendar/ERROR_LOG.md`
- Phase status: `docs/nifty_calendar/PHASE_STATUS.md`