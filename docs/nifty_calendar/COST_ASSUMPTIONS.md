# Transaction-Cost Assumptions — NIFTY 2022-2024

## Historical sample window

The validated trade ledger runs from 2022-01-28 through 2024-08-30. Therefore all completed trades predate the 1-Oct-2024 option-sale STT increase.

## Broker

Paytm Money F&O FAQ:
- Brokerage = Rs 10 per unique executed F&O order.
- Eight completed option executions per strategy cycle => Rs 80 brokerage per cycle.

Source:
https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web

Paytm Money pricing page:
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
