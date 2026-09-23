# P9 Secondary Validation Report — Rissin / Upstox 1-minute

## Dataset and execution convention
- 86 post-2024 executable OOS cycles inherited from P8.
- Option source: `rissin/nse-options-intraday` Upstox 1-minute NIFTY option data.
- Spot source: `thetrademarkk/india-index-options-1m` 1-minute NIFTY index.
- Signal: completed 1-minute close.
- Fill: next available qualifying minute open.
- Costs: same P8 brokerage/statutory/exchange stress model and 0/0.5/1/2 point adverse slippage.
- ATM QC: common strike within 25 points of contemporaneous spot. NSE specifies a 50-point NIFTY strike interval for weekly/monthly contracts.

## QC and trade counts
- 9 cycles: no complete four-leg panel.
- 3 event rows: no executable exit.
- Fixed source diagnostic: 14 executable trades.
- Event-driven: 65 executable trades.
- Event median ATM distance: 12.1 points (0.052%).
- Event maximum ATM distance: 24.2 points.
- Event median signal time: 09:22 IST.

## Cost results
| Arm | 0 pt | 0.5 pt | 1 pt | 2 pt |
|---|---:|---:|---:|---:|
| Fixed source diagnostic | ₹13,418.43 | ₹9,458.43 | ₹5,498.43 | ₹-2,421.57 |
| Event-driven | ₹17,798.70 | ₹-781.30 | ₹-19,361.30 | ₹-56,521.30 |

## Interpretation
The fixed source diagnostic is not used as the canonical fixed benchmark because of incomplete intraday coverage. The canonical P8 daily ledger is used for paired comparison on dates where the event signal occurred.

## Final P9 status
Event-driven timing is not promoted. P10 returns to the frozen 09:15 rule for forward/paper validation.