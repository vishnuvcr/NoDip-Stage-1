# P9 Rissin pre-specified latest-entry sensitivity

- This is a pre-specified operational cutoff sensitivity, not a post-hoc parameter search.
- Entry rule remains frozen: first intraday qualifying CBR <= 1.20 with a true ATM common strike and all four executable legs.
- ATM QC: NIFTY strike interval is 50 points; common strike must be within 25 points of contemporaneous spot.
- Signal uses the minute close; entry uses the next available minute open.

## Summary
- 15:00: 63 trades, gross ₹37,787.00, PF 1.655, net at 1-point slippage ₹-23,190.99, net at 2-point slippage ₹-59,230.99.
- 15:15: 64 trades, gross ₹38,465.75, PF 1.666, net at 1-point slippage ₹-23,446.99, net at 2-point slippage ₹-60,086.99.
- 15:30: 65 trades, gross ₹43,607.25, PF 1.755, net at 1-point slippage ₹-19,361.30, net at 2-point slippage ₹-56,521.30.
- 15:40: 65 trades, gross ₹43,607.25, PF 1.755, net at 1-point slippage ₹-19,361.30, net at 2-point slippage ₹-56,521.30.

## Interpretation rule
No cutoff is selected for profitability. The cutoffs are reported as pre-registered sensitivity checks.

NSE contract specification source:
https://www.nseindia.com/static/products-services/equity-derivatives-nifty50
