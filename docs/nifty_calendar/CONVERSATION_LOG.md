# Conversation / Decision Log

## 2026-09-23

### P0-P8 historical research
- User requested a NIFTY four-leg calendar research program.
- Initial frozen timing was the first eligible trading day after weekly expiry at 09:15 IST open.
- P0-P8 were executed on separate research branches.
- P7 identified the candidate calendar-balance gate CBR <= 1.20.
- P8 validated that gate unchanged on the post-2024 temporal holdout.
- P8 conclusion: supported for further research, not promoted to live trading.

### 2026-09-23 — New entry-timing question
- User asked whether the strategy can enter during the trading day when all other criteria are met instead of relying on a fixed clock time.
- The repository's canonical frozen baseline is 09:15 IST; a 09:30 implementation can be treated as a fixed-time variant, but P6/P8 remain the canonical 09:15 reference.
- Decision: open a separate P9 phase rather than altering P8.
- P9 rule to test: on each eligible day, enter exactly once at the first intraday timestamp when CBR <= 1.20, the current common ATM strike is valid, and all four near/far contracts are simultaneously executable.
- The 1.20 threshold remains frozen; P9 will not search alternate thresholds.
- No-lookahead rule: quote/tick data may use contemporaneous executable prices; with 1-minute OHLC-only data, signal at minute close and execute at the next available minute price.
- P9 is currently data-blocked because the repository does not yet contain timestamped intraday multi-expiry option quotes sufficient to reconstruct the four legs.
- A manual GitHub Actions workflow and detailed P9 research plan were added to the dedicated branch.