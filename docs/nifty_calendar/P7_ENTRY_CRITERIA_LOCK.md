# P7 Candidate Entry Criteria Lock — v1

Status: CANDIDATE — NOT FROZEN FOR LIVE USE

## Entry gate

Enter the P6 four-leg structure only when:

calendar-balance ratio <= 1.20

where:

calendar-balance ratio = (far CE entry premium / near CE entry premium) /
                         (far PE entry premium / near PE entry premium)

## Rules retained unchanged from P6

- First trading session after previous NIFTY weekly expiry.
- 09:15 IST entry.
- Nearest common ATM strike.
- Buy near PE.
- Sell near CE.
- Buy far CE.
- Sell far PE.
- Exit all legs at near-expiry close.
- One historical lot per leg.
- No adjustment, roll, averaging, stop or target.

## Research status

This candidate gate was identified from the P7 loss audit. It is not promoted into the P6 frozen strategy. A genuinely unseen post-2024 dataset must be used for independent validation before any production decision.
