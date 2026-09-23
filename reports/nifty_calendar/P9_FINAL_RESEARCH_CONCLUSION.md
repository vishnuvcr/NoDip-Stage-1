# P9 Final Research Conclusion — Event-Driven Intraday Entry Timing

Date: 2026-09-23

## Research question

Can the frozen NIFTY four-leg calendar strategy replace its fixed 09:15 entry with the first intraday timestamp on the eligible day at which the frozen calendar-balance gate CBR <= 1.20 becomes valid and all four legs are simultaneously executable?

## Decision

**P9 COMPLETE — event-driven entry timing is NOT supported for promotion.**

The 1.20 threshold and four-leg structure remain frozen. No new threshold was optimized.

The decisive test used an unseen post-2024 OOS population and a secondary 1-minute NIFTY option source. The first public option source was rejected by source-quality QC because far-expiry intraday coverage was too sparse to reconstruct a defensible ATM panel. The Rissin/Upstox-derived 1-minute source provided the usable secondary test.

## Data and methodology

### Primary public source QC

Thetrademarkk india-index-options-1m successfully supplied 1-minute NIFTY index and option expiry files, but the far-expiry panel was too sparse on the audited 2026-04-01 sample:

- near-expiry rows for the day: 58,868
- far-expiry rows for the day: 903
- sampled far-expiry rows at 09:15, 09:16, 09:22 and 09:26: only 2–4 rows/minute
- at 09:22 and 09:26 the only complete common executable strike was 20,500 while NIFTY was about 22,894–22,900
- therefore the first primary-source timing result was rejected as a source-quality diagnostic, not treated as strategy performance.

### Secondary OOS source

Rissin nse-options-intraday Upstox 1-minute NIFTY option data were used for the secondary validation. The OOS population is the same 86 executable post-2024 cycles used in P8.

The spot series remained the 1-minute NIFTY index from thetrademarkk source so that the cross-check isolates the option-data source while keeping spot selection consistent.

Entry convention:
- signal from the completed 1-minute bar;
- select the nearest common executable strike to contemporaneous spot;
- require all four legs with positive volume and positive prices;
- execute at the next available minute open;
- exit at the last common near-expiry-day executable close;
- compare fixed 09:15 versus first qualifying event-driven entry;
- transaction-cost sensitivity uses the same P8 modeled cost framework with 0, 0.5, 1 and 2 NIFTY points adverse slippage and 0.05% exchange-charge stress.

## Results

| Metric | Fixed 09:15 control | Event-driven first qualifying |
|---|---:|---:|
| Executable trades | 26 | 70 |
| Gross P&L | ₹40,506.25 | ₹37,291.40 |
| Win rate | 80.77% | 62.86% |
| Profit factor | 5.029 | 1.576 |
| Gross max drawdown | ₹7,489.50 | ₹26,467.50 |
| Worst trade | ₹-5,391.75 | ₹-9,984.75 |

The two arms produced identical results on all 26 paired dates. The difference came entirely from the 44 additional event-only trades created by allowing the entry to occur later.

### Event-only trades

44 trades were added by the adaptive timing rule:

- gross P&L: ₹-3,214.85
- win rate: 52.27%
- profit factor: 0.941
- worst trade: ₹-9,984.75

Of those 44 additional trades:

| Event-only subset | Trades | Gross P&L | Win rate | Profit factor |
|---|---:|---:|---:|---:|
| Originally gate-pass at the fixed observation, but not executable at 09:15 | 20 | ₹10,749.75 | 60.00% | 1.823 |
| Originally gate-fail, then became CBR<=1.20 later in the day | 24 | ₹-13,964.60 | 45.83% | 0.665 |

The negative gate-fail subset more than offset the positive contribution from delayed entries on originally gate-pass days.

### Timing and ATM quality

For event-driven trades:
- median qualifying signal time: 09:16 IST
- median ATM distance: 48.3 NIFTY points (0.189%)
- 75th percentile ATM distance: 117.45 points (0.455%)
- 90th percentile ATM distance: 306.65 points (1.212%)
- maximum observed ATM distance: 844.35 points (3.617%)

Thus the secondary source generally reconstructed a near-spot common strike, but some sparse/late observations still produced materially wider strike distances. This is an execution-data limitation to retain in future research.

## Cost and slippage sensitivity

At 0.05% exchange-charge stress:

| Slippage per execution | Fixed 09:15 net P&L | Event-driven net P&L |
|---|---:|---:|
| 0.0 points | ₹29,499.84 | ₹9,222.87 |
| 0.5 points | ₹22,139.84 | ₹-10,837.13 |
| 1.0 point | ₹14,779.84 | ₹-30,897.13 |
| 2.0 points | ₹59.84 | ₹-71,017.13 |

The event-driven arm therefore fails the pre-specified execution-robustness criterion: a modest 0.5-point adverse-slippage assumption makes the modeled net result negative.

The cost estimates are modeled research assumptions, not realized Paytm Money fills.

## Interpretation

The evidence does not support replacing the fixed opening entry with a first-intraday qualifying entry under the frozen CBR<=1.20 rule.

The important mechanism is not that late entry always loses. Some delayed entries on dates that already belonged to the gate-pass population were profitable. The deterioration came primarily from recovering dates that failed the gate at the opening observation and only became CBR<=1.20 later. That group had PF below 1 and a large negative tail.

Waiting for the term-structure imbalance to become favorable later in the day can admit trades that no longer carry the favorable selection embedded in the opening state.

## Statistical interpretation

The comparison is a paired OOS diagnostic, not a new threshold-selection exercise.

The paired dates are unchanged between fixed-time and event-driven arms because when the frozen gate qualifies at 09:15 the first event timestamp is also 09:15. The economic difference is therefore concentrated in the 44 event-only trades.

No alternative CBR threshold was searched in P9. No post-hoc timing cutoff was selected for performance.

## Strengths

- Genuine post-2024 temporal holdout.
- Frozen CBR threshold and four-leg structure.
- Secondary option-data source used for the decisive test.
- Explicit contemporaneous four-leg availability.
- Next-minute execution convention for 1-minute data.
- Transaction costs and adverse slippage included.
- Primary-source quality failure was detected and rejected before interpretation.
- Event-only trades were decomposed by their original fixed-observation gate status.

## Limitations

- The secondary source is an Upstox-derived public dataset rather than a certified exchange tick archive.
- Historical bid/ask quotes were unavailable, so the analysis cannot claim true historical market-order replay.
- Exact 09:15 fixed control is source-coverage constrained to 26 executable observations in the secondary dataset; it is not identical to the 42-trade P8 daily-open population.
- Some secondary-source event observations have wider ATM distance than ideal.
- No statistical test can eliminate uncertainty caused by source-specific contract availability and execution assumptions.

## Conclusion

P9 is complete.

The event-driven adaptation fails to provide a robust improvement over the fixed opening entry under the frozen CBR<=1.20 strategy. The additional trades are economically weak in aggregate and highly sensitive to realistic slippage.

**The frozen fixed-time strategy remains the research reference. P9 event-driven entry timing is not promoted to the next live/paper specification.**

## Next phase

P10 should therefore return to the frozen fixed rule and conduct forward/paper-execution validation with timestamped executable quotes, real observed spreads, brokerage/statutory charges, slippage, and a pre-registered paper ledger.

Any future attempt to design a new intraday timing/filter rule must be a separate development phase with a new unseen temporal holdout.