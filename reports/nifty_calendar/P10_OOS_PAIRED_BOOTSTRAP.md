# P10 OOS Paired Bootstrap Statistics

Paired comparison is against the canonical D+1 offset on the same 88 OOS expiry cycles. Non-trades contribute zero P&L. For each offset, 20,000 cycle-level bootstrap resamples were generated from the paired differences.

| Offset | Mean difference vs D+1 | Bootstrap 95% CI | Higher cycles | Lower cycles |
|---|---:|---:|---:|---:|
| D-1 | ₹-104.37 | ₹-1,403.35 to ₹1,114.14 | 27 | 30 |
| D0 | ₹383.69 | ₹-797.17 to ₹1,480.94 | 32 | 21 |
| D+2 | ₹330.85 | ₹-445.32 to ₹1,099.05 | 32 | 27 |
| D+3 | ₹-562.94 | ₹-1,480.49 to ₹308.59 | 18 | 31 |
| D+4 | ₹-219.25 | ₹-1,179.47 to ₹716.87 | 23 | 30 |
| D+5 | ₹-940.37 | ₹-1,975.86 to ₹-69.96 | 19 | 29 |

Interpretation:
- D0 and D+2 have positive mean differences versus D+1, but their 95% bootstrap intervals include zero.
- D-1 and D+4 are also statistically indistinguishable from D+1 under this paired bootstrap.
- D+3 is negative on average but its interval includes zero.
- D+5 is the only tested offset whose paired bootstrap interval is entirely below zero versus D+1 in this seven-offset screen.
- These are unadjusted multiple comparisons and should not be treated as confirmatory hypothesis tests.