# P13 Fresh Far-Expiry Validation Report

## Frozen rule
- D+1 entry, 09:15 market-open proxy, near expiry next listed expiry.
- Far candidates F+1 through F+4.
- Adaptive score = (near CE - near PE + far PE - far CE) / spot open.
- Choose highest score using entry information only.
- No threshold/weight/horizon tuning was performed in P13.

## Fresh-data gate
- P10/P12 cutoff: 2026-08-26
- Latest source trading date: 2026-06-29
- Fresh completed cycles: 0

## Results
- F+1: 0 trades, gross ₹0.00, PF nan, win nan%, DD ₹nan, net@2pt ₹0.00.
- F+2: 0 trades, gross ₹0.00, PF nan, win nan%, DD ₹nan, net@2pt ₹0.00.
- F+3: 0 trades, gross ₹0.00, PF nan, win nan%, DD ₹nan, net@2pt ₹0.00.
- F+4: 0 trades, gross ₹0.00, PF nan, win nan%, DD ₹nan, net@2pt ₹0.00.
- ADAPTIVE: 0 trades, gross ₹0.00, PF nan, win nan%, DD ₹nan, net@2pt ₹0.00.

## Adaptive selection frequency
- {'F+1': 0, 'F+2': 0, 'F+3': 0, 'F+4': 0}

## Fresh ledger status counts
- {'NO_FRESH_ROWS': 1}

## Data-quality interpretation
- This is the first evaluation of the frozen P12 rule on dates strictly after 2026-08-26 available in the current dataset.
- The entry uses the same daily-open proxy used by P12; it is not a historical bid/ask or exact exchange tick-fill reconstruction.

## Decision
**INSUFFICIENT FRESH SAMPLE — CONTINUE PROSPECTIVE PAPER MONITORING**
