# Transaction-Cost Assumptions — NIFTY 2022-2024

## Historical sample window

The validated trade ledger runs from 2022-01-28 through 2024-08-30. Therefore all completed trades predate the 1-Oct-2024 option-sale STT increase.

## Broker

The historical sample must not use a single Paytm Money brokerage rate for all clients.

Paytm Money's 25-Aug-2023 official pricing announcement states:
- Accounts opened before 05-Aug-2022: ₹10 per executed Intraday/F&O order.
- Accounts opened from 05-Aug-2022 through 24-Aug-2023: ₹15 per executed Intraday/F&O order.
- Accounts opened from 25-Aug-2023: ₹20 per executed order.
- The later Paytm Money pricing update states that brokerage was aligned to a flat ₹20 across segments from 15-Jan-2025.

The 2022-2024 study does not know the user's account cohort, so the research reports ₹10, ₹15 and ₹20 per executed order as three brokerage scenarios. Each strategy cycle has eight executions, so brokerage alone is ₹80, ₹120 or ₹160 per completed cycle.

Sources:
- https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/
- https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/
- https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web

Current Paytm Money F&O FAQ:
- The current FAQ page says ₹10 per unique executed F&O order.
- The pricing page says statutory/regulatory/exchange charges are levied at actuals.

- Statutory, regulatory and exchange charges are levied at actuals as stipulated from time to time.
- Because the historical Paytm-specific exchange pass-through rate is not fully exposed on the public pricing page, the research does not pretend to know an exact historical client rate.

Source:
https://www.paytmmoney.com/stocks/pricing

## Statutory charges used

### STT
For sale of options:
- 0.0625% of option premium through 30-Sep-2024.
- Increased to 0.1% effective 1-Oct-2024.

Sources:
- Income Tax Department Finance (No. 2) Act 2024 memorandum:
  https://www.indiabudget.gov.in/budget2024-25/doc/memo.pdf
- Paytm Money pricing update:
  https://www.paytmmoney.com/blog/paytm-money-pricing-update-revised-charges-effective-from-1st-october/

### Stamp duty
- 0.003% on non-delivery securities transaction consideration, buyer-side for exchange trades.

Source:
https://www.sebi.gov.in/sebi_data/attachdocs/jan-2024/1706503271496.pdf

### SEBI turnover fee
- 0.00010% used for the historical cost model.

Paytm Money source describing the charge:
https://www.paytmmoney.com/blog/trade-charges-paytm-money/

## GST

18% applied to:
- brokerage
- SEBI fee
- the exchange transaction charge sensitivity

## Exchange-transaction-charge sensitivity

Three scenarios are used:
- 0.03503% of option premium turnover
- 0.05000%
- 0.05300%

These are explicit sensitivity assumptions, not assertions of the exact historical Paytm client pass-through rate. NSE's October 2024 uniform rate was Rs 35.03 per lakh of premium value per side (0.03503%), while Paytm-related public pricing aggregators quote 0.053% on option premium. The study therefore reports a range rather than treating either as historical Paytm contract-note truth.

NSE October 2024 circular:
https://nsearchives.nseindia.com/content/circulars/FA64232.pdf

## Slippage

Slippage is modeled per execution, separately for every leg and using the historical lot size of that leg. Each trade has eight executions.

Scenarios:
0.25, 0.50, 1.00 and 2.00 index points per execution.

This is a sensitivity analysis, not an assertion that these were the realized bid/ask spreads.
