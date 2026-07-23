# D149a joint two-stage structural cross-fit — result

Date: 2026-07-23  
Decision: **close the action-only joint controller on cross-fit**

Two complete 32-fit selections are byte-identical at SHA `7f590a53...`. No seed pair is eligible,
so D149 writes no full fit or checkpoint and does not open the reserved panel.

The gate has weak but real transfer. Across seeds, held balanced accuracy is 58.35%--59.70%; wait
recall is 73.01%--74.03%, and 90.98%--92.51% of inactive tasks have no false act over their full
included prefix. Act recall is only 43.69%--45.36%, below the frozen 50% floor for every seed.

The primary failure is proposal ranking. The best pair, 14902/14952, reaches only 9.79% exact held
top-1 accuracy against a 6.43% random baseline (1.52x, gates 15% and 2x). Its first-stage accuracy
is 12.37%, but second-stage accuracy is 7.22%, barely above random. Joint act-plus-exact-rank rates
are 0.77% at the first action and 6.44% at the second; no held active task reproduces both actions.
All other seeds show the same pattern. Training rank accuracy is only about 18%, so this is not
merely a high-capacity overfit.

The defect is concrete: D149a's ranker receives only the 379 proposal-delta features. Those encode
proposal semantics and six local context interactions, but omit the separate 64-state vector,
including the global economy, remaining intervention budget, and previous intervention kind. The
gate sees that state; proposal selection does not. This omission is especially damaging for the
second action, whose value is conditional on the state produced by the first.

Next test one isolated repair on the same consumed evidence: concatenate the 64 state features to
each proposal before the existing 16-unit ranker. Keep labels, folds, seeds, optimizer, gate,
threshold, and all D149a cross-fit gates unchanged. This adds only 1,024 ranker weights and tests the
missing-conditioning hypothesis without opening maps or tuning thresholds. If it fails, stop exact
winner imitation and change the target/evidence rather than widening the classifier repeatedly.

Result JSON SHA: `2fecb8f4...`.
