# P8 OOS Candidate Lock

Status: FROZEN FOR P8 VALIDATION

The only candidate rule tested in P8 is:

`(far CE entry / near CE entry) / (far PE entry / near PE entry) <= 1.20`

Everything else is frozen from P6:
- first session after prior NIFTY weekly expiry;
- 09:15 market-open price convention using daily OPEN;
- closest common ATM strike;
- buy near PE;
- sell near CE;
- buy far CE;
- sell far PE;
- exit at near-expiry CLOSE;
- one applicable historical lot per leg;
- no stop, target, roll, averaging or adjustment.

P8 must not test 1.15, 1.25, 1.30, alternate ratios, or any newly discovered variable. Any later optimization becomes a separate phase with its own unseen validation set.
