# D41d residual-ranked one-deviation continuation — frozen protocol (2026-07-21)

## Question and authorization

D41c learned subthreshold residual preferences but made zero deterministic changes. D41d asks
whether its strongest rank-one preferences identify individually valuable actions under exact D40
continuation, or whether the explored alternatives are already harmful one at a time.

This protocol authorizes a fresh state manifest, exact paired one-deviation simulations, statistical
analysis, tests, and written results. It authorizes no learning, prior-temperature change,
confirmation, candidate construction, TestSession, submission, or Arena.

## Fresh state bank and frozen proposals

Use maps **9,760,000--9,760,031**, both seats, and all eight D40 opponents: 512 uninterrupted D40
episodes. These maps are disjoint from D41 training/development and the sealed 9,720,000 confirmation
block.

At every D40 decision with at least two legal candidates:

1. compute the frozen seed-411 residual logits from checkpoint SHA-256
   `1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a`;
2. define the proposal as exact-prior rank one, matching 98.16% of D41c's sampled nonteacher actions;
3. record residual gap `residual(rank1) - residual(rank0)` without observing any deviated outcome;
4. stratify by four D40 branches, early/middle/late turns (`<100`, `100--199`, `>=200`), and eight
   opponents; and
5. preserve task index, decision ordinal, action IDs, candidate count, turn, branch, phase, and
   residual gap in a hashed manifest.

Create two nonoverlapping cohorts per stratum before any deviation simulation:

- **residual-top:** up to eight states with the largest residual gap, stable state identity as tie
  break; and
- **hash-control:** up to four remaining states with the smallest SHA-256 of
  `(map, seat, opponent, decision ordinal)`, independent of features or outcomes.

This yields at most 1,152 states. Sparse strata may contribute fewer; report all counts. No state
may occur in both cohorts and no outcome-dependent replacement is allowed.

## Exact paired continuation

For every manifest state, reconstruct the corresponding macro environment from the official map,
seat, and opponent. Replay exact D40 actions through the recorded decision ordinal and require the
teacher/proposal action IDs, branch, turn, and candidate count to match the manifest. Then:

- baseline is uninterrupted D40 to terminal; and
- treatment takes exactly the recorded rank-one action once, then returns to D40 at every later
  boundary through terminal.

Record paired own score, opponent score, margin, workforce, crops, successful trains, invalidations,
integrity counters, action/state hashes, and elapsed time. Parallel task execution may use 20 CPU
threads, but an A/A subset must reproduce exact rows.

Any replay mismatch, illegal proposal, nonterminal loop, worker-cap breach, invalid direct command,
provenance failure, or relevant prediction failure invalidates the run rather than being dropped.

## Frozen analysis and decision rules

For each cohort, branch, phase, and opponent report sample count, mean/median/quantiles of paired
margin, own-score, and opponent-score delta; positive/tie/negative rates; standard error and
descriptive normal 95% interval; worker/crop transitions; and catastrophe changes (`margin <= -100`).

The residual contains a useful one-step ranking signal only if the residual-top cohort has:

1. at least 256 valid samples;
2. mean paired margin delta at least **+3** with lower descriptive 95% bound above zero;
3. positive-delta rate at least **55%**;
4. mean advantage over hash-control at least **+3**;
5. at least four opponent means nonnegative and no opponent mean below -15; and
6. zero integrity/replay failures.

A branch-specific signal may independently open a branch-gated follow-up if it has at least 64
samples, mean margin delta at least +5, positive rate at least 55%, and lower 95% bound above zero.

- **Top passes, control does not:** D41c learned useful ranking but its scale was suppressed. Next
  distill a confidence/branch gate from continuation labels while retaining exact D40 fallback.
- **Both pass:** rank-one D40 alternatives are generically underexploited; improve the deterministic
  prior before another PPO run.
- **Neither passes:** the sampled proposals are individually harmful or neutral; do not merely lower
  temperature. Expand the continuation action set or objective instead.

The study is diagnostic even if a rule passes. Any learned selector requires a new protocol and
fresh development/confirmation blocks.
