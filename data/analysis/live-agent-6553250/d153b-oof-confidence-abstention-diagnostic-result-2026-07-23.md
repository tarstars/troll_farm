# D153b out-of-fold confidence/abstention diagnostic — result

Date: 2026-07-23  
Decision: **close scalar confidence abstention for the compact snapshot scorer**

Two independent exports each contain all 64,912 held action scores (four seeds × 16,228 actions).
One of 32 model hashes differs at threaded floating-point scale, matching D153a; maximum prediction
drift is only `2.3842e-5` margin and every threshold policy is exactly identical A/B. Threshold zero
reproduces all four D153a held policies exactly.

No individual model or four-seed ensemble finds a supported high-precision region. The ensemble is
best at threshold zero: 97.14% action rate, **+1.843 mean value**, 43.23% harmful selections, and
6.06% oracle capture. At threshold 12 it acts 28.60%, but value falls to +0.152 and capture to
0.50%. At threshold 15 it acts 11.66%, loses -0.186, and still has negative folds. Higher thresholds
mostly choose control and therefore approach zero without recovering value.

The ensemble's best-action score is slightly anti-correlated with exact value (`r = -0.0317`). Its
highest score decile predicts +18.07 on average but realizes **-1.51**, with 46.67% harmful actions;
the second-highest decile realizes +4.62. Calibration is nonmonotone throughout. This rules out a
missed scalar cutoff: model confidence does not order held action quality.

Do not spend a nested cross-fit on threshold calibration and do not increase this MLP's capacity.
The next experiment must change representation or action abstraction while reusing the exact D152
corpus. Reserved maps remain sealed; no YT, Arena, Rust integration, checkpoint, submission, or
resident change occurred. Result JSON SHA: `bf57c758...`.
