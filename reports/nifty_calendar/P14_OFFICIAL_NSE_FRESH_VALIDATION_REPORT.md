# P14 Official NSE Fresh Far-Expiry Validation Report

## Source
- Official NSE F&O UDiFF Common Bhavcopy Final; daily files from 2026-08-27 through 2026-09-23 were attempted and cached.
- NIFTY option rows only; source manifest records each date, response, size and SHA256.

## Frozen strategy
- D+1 after previous expiry; 09:15 market-open proxy; F+1/F+2/F+3/F+4 far expiries.
- Adaptive score = (near CE - near PE + far PE - far CE) / NIFTY underlying price.
- Highest score selected using entry information only.
- Same ATM strike; <=25-point QC.

## Fresh data gate
- P10/P12 cutoff: 2026-08-26
- Latest official NSE parsed date: 2026-09-22
- Fresh completed cycles: 3
- Ledger status counts: {'EXECUTABLE': 9, 'NO_ENTRY_LEG': 3, 'ADAPTIVE_SELECTED': 3}

## Results
- F+1: 3 trades; gross ₹6,714.50; PF inf; win 100.0%; DD ₹0.00; net @2pt ₹2,976.46.
- F+2: 3 trades; gross ₹3,081.00; PF inf; win 100.0%; DD ₹0.00; net @2pt ₹-709.34.
- F+3: 3 trades; gross ₹6,100.25; PF 9.091; win 66.7%; DD ₹754.00; net @2pt ₹2,260.39.
- F+4: 0 trades; gross ₹0.00; PF nan; win nan%; DD ₹nan; net @2pt ₹0.00.
- ADAPTIVE: 3 trades; gross ₹6,714.50; PF inf; win 100.0%; DD ₹0.00; net @2pt ₹2,976.46.

## Adaptive selection frequency
{'F+1': 3, 'F+2': 0, 'F+3': 0, 'F+4': 0}

## Paytm Money brokerage input
- P14 models ₹10 brokerage per unique executed order based on Paytm Money’s current F&O FAQ.
- Eight option orders per completed cycle are modeled.
- STT is 0.15% on option-sale premium for trades after 2026-04-01; stamp duty, SEBI fee, GST and a 0.05% exchange-charge stress are included.
- Adverse slippage is separately tested at 0/0.5/1/2 points per execution.

## Decision
**INSUFFICIENT FRESH SAMPLE — CONTINUE PROSPECTIVE PAPER MONITORING**

- This is a genuinely fresh official-NSE post-cutoff sample. Because the number of completed weekly cycles is small, no statistical significance claim is made.
- The P14 test does not retune the adaptive score or search further far-expiry horizons.
