# P9 Trigger

P9 was opened in response to the research question:

> Instead of entering at a fixed clock time, can the strategy enter during the eligible trading day when all other frozen criteria are first simultaneously satisfied?

The P9 candidate is:

`first intraday timestamp with CBR <= 1.20 and all four required contracts executable`.

The 1.20 threshold is frozen. P6/P8 remain the reference strategy and are not overwritten.

P9 numerical scoring is blocked until timestamped intraday option data capable of reconstructing both near and far expiries at the same strike is available.
