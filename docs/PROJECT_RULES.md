# NoDip Stage-1 Research Operating Rules

1. Research proceeds in explicit phases and stops at the proposed phase boundary unless a serious data/integrity issue requires intervention.
2. Strategy definitions are frozen before historical performance is measured.
3. Every phase has a dedicated Git branch and a manual GitHub Actions entry point.
4. Every execution step updates phase status; every error or failed assumption is logged.
5. Historical data must be reproducible. Prefer official NSE data; use independent/open sources for cross-checks.
6. Do not claim results until source coverage, contract mapping, holiday rules, and execution assumptions pass verification.
7. Backtests distinguish gross P&L from slippage, brokerage, taxes/fees and other transaction costs.
8. Avoid look-ahead: entry uses information available at the stated entry timestamp; expiry exit uses the stated exit price only.
9. Keep research outputs, manifests, hashes and derived trade-level datasets versioned. Do not commit exchange-owned bulk raw archives unless redistribution is verified as permitted.
10. The final deliverable includes research questions, aims/objectives, methodology, statistical analysis, results, inference, discussion, strengths/limitations, conclusion, future work, tables/charts and appendices.
