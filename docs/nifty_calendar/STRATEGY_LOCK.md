# NIFTY 4-Leg Weekly / 3-Week Calendar — LOCKED

Status: FROZEN FOR BACKTEST
Branch: research-nifty-4leg-calendar-v1
Lock date: 2026-09-23

## Rules

1. Instrument: NIFTY 50 index options.
2. Entry date: first trading day after the previous NIFTY weekly expiry.
3. Entry time: 09:15 IST market-open bar.
4. Near expiry: the first weekly NIFTY expiry after the entry session.
5. Far expiry: the weekly expiry exactly three weekly intervals after the near expiry, using the actual exchange expiry calendar. The far contract is the fourth expiry in the sequence beginning with the near expiry.
6. ATM strike: nearest currently listed strike to the NIFTY 50 spot OPEN at 09:15 IST. The selected strike is recorded explicitly for every trade.
7. Legs:
   - Buy 1 near-expiry ATM PE.
   - Sell 1 near-expiry ATM CE.
   - Buy 1 far-expiry ATM CE.
   - Sell 1 far-expiry ATM PE.
8. Entry fill: session OPEN price of each selected option contract on the entry date. If a contract has no valid open print, the trade is DATA_INVALID and is not silently substituted.
9. Exit: close all four legs on the near-expiry trading day using each contract's official daily CLOSE. No early exit, no roll, no adjustment.
10. Quantity: one contract of each leg (one lot) with the historically applicable lot size. P&L is reported both in index points and INR.
11. No discretionary filters, stop-loss, target, adjustment, averaging, strike shift, or signal overlay.
12. No overlapping positions: one strategy cycle per weekly expiry sequence.
13. The primary frozen definition uses the single entry-time spot ATM strike for all four legs. The screenshots are treated as illustrative examples, not as a separate hidden strike-selection rule.

## Execution cost layers

The research will publish:
- Gross mark-to-market P&L.
- P&L with adverse slippage sensitivity.
- P&L net of broker/exchange/statutory costs using a documented Paytm Money assumption set where historical applicability can be established.
- No net profitability claim is made from gross P&L alone.

## Data integrity

Daily OHLC is sufficient for this frozen 09:15-open / expiry-close protocol because both entry and exit are defined at daily bar endpoints. Intraday data will be used for spot/open validation when available and for a secondary execution-sensitivity check; it is not allowed to silently replace a missing official daily contract record.
