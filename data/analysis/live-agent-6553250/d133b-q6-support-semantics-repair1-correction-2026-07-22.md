# D133b support-audit factual correction

Date: 2026-07-22  
Scope: narrative count only; no gate, threshold, artifact, statistic, or decision changes

The frozen D133b protocol says five of nine listed prior 16-map panels are below 90% support. The
machine audit correctly reports **four of nine** below 90%; equivalently, only five of nine clear
90%. Every listed individual rate, the 2,076/2,304 pooled count (`90.10%`), and the
85.94%--92.97% range are correct.

The causal conclusion is unchanged and slightly clearer in pass-rate form: using the empirical
panel frequency, an every-block 90% requirement clears four independent blocks with probability
approximately `(5/9)^4 = 9.53%`. D133b's executable repair never gated on “five below”; it removes
only the support-percentage gate, retains all exact mechanics/sample/teacher/safety gates, and
requires the prospectively fixed D134 calibration-feasibility counts. No rerun or outcome change
is caused by this correction.
