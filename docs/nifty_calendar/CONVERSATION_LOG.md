# Conversation / Decision Log

## 2026-09-23
- User requested a simple NIFTY backtest for a four-leg structure:
  1. buy weekly ATM PE
  2. sell weekly ATM CE
  3. buy CE three weeks later
  4. sell PE three weeks later
  5. exit all legs at weekly expiry
- User then fixed entry timing: first trading day after the previous expiry, morning open entry.
- Strategy was requested to be locked.
- User specified the research repository: https://github.com/vishnuvcr/NoDip-Stage-1.
- Frozen interpretation: entry at the 09:15 IST open; exit at near-expiry close; no discretionary changes.
