# D41f early/late rate-boundary one-deviation study — frozen protocol (2026-07-21)

## Question and authorization

D41e is prospectively positive but misses its +5 complete-policy floor because only 29.69% of
episodes activate. Rate-only episodes account for +4.093 of the +4.116 global gain, repeated
overrides do not dilute value, and evacuation does not replicate. D41f asks whether rank-one rate
actions immediately below the frozen 0.280 residual-gap boundary retain enough one-step value to
expand coverage safely.

This protocol authorizes one outcome-blind manifest on fresh D40 trajectories, paired one-deviation
continuations, exact repeats, analysis, and written results. It authorizes no complete-policy
threshold change, learning, D41e Stage B, confirmation, candidate construction, TestSession,
submission, or Arena.

## Frozen inputs and fresh bank

- maps **9,772,000--9,772,031**, both seats, all eight opponents: 512 D40 tasks;
- D41c seed-411 checkpoint SHA-256:
  `1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a`;
- exact D40 kernel SHA-256:
  `632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`;
- released environment SHA-256:
  `5839a7b888f2772e54a293a66ed5b186df378d5b8514f43a200898c8eef70173`;
- D41e mechanism artifact SHA-256:
  `1f4f34c470a2c76481ed90f98edaa16b4b457718df42ee7c4c013d263b50b8c7`.

The bank is disjoint from all D41 training/development/diagnostic blocks and the sealed 9,720,000
confirmation block.

## Outcome-blind boundary manifest

Replay uninterrupted D40. At every `rate` decision in early (`turn <100`) or late (`turn >=200`)
phase with at least two candidates, compute the frozen residual gap from rank zero to exact-prior
rank one. Assign gaps to these inclusive-lower/exclusive-upper bins, except the last which includes
0.340:

1. `[0.100,0.200)`;
2. `[0.200,0.240)`;
3. `[0.240,0.260)`;
4. `[0.260,0.280)`;
5. `[0.280,0.300)`;
6. `[0.300,0.320)`;
7. `[0.320,0.340]`.

Within each bin × phase × opponent stratum, retain at most one state per task, choosing the state
with the smallest SHA-256 of `(map,seat,opponent,decision ordinal)`, then retain the 16 tasks with
the smallest same hash. Selection may inspect identities, branch, turn, phase, rank, action IDs,
candidate count, and residual gap only—never terminal or deviated outcomes. The maximum is 1,792
states. Sparse strata keep all available states and are reported, not replenished from another bin.

## Exact paired continuation

For every manifest row, reconstruct the task and replay exact D40 through the decision ordinal.
Require the task, turn, branch, candidate count, D40 action, and rank-one action to match. Baseline
continues D40; treatment takes rank one exactly once and then returns to D40 through terminal.

Run all rows with 20 threads. Independently rerun the first 96 manifest rows twice and require both
repeats and the matching full-run subset to be behaviorally exact excluding elapsed time. Any
illegal action, replay mismatch, nonterminal loop, direct-command/provenance/relevant-prediction
failure, or worker-cap breach invalidates the study.

## Frozen analysis

Report paired margin, own-score, and opponent-score distributions by bin, phase, opponent, and
bin × phase; positive/tie/negative rates; descriptive normal intervals; workforce/crop transitions;
and catastrophe changes.

A single below-boundary bin is useful only with at least 128 rows, mean margin at least +5, positive
rate at least 55%, and lower descriptive 95% bound above zero.

For each candidate lower threshold in `0.100, 0.200, 0.240, 0.260, 0.280`, pool that bin and every
higher bin through 0.340. A threshold qualifies for a later complete-policy hypothesis only if:

1. at least 384 rows;
2. mean margin at least **+8** and lower descriptive bound above **+4**;
3. positive rate at least 60%;
4. early mean at least +8 and late mean at least +4;
5. at least six opponent means positive and none below -10; and
6. all integrity/replay gates pass.

Select the **lowest** qualifying threshold, but only if at least one newly sampled bin below 0.280
also passes its individual useful-bin gate. This selection is discovery: a chosen threshold must be
frozen under a new protocol and evaluated as a complete policy on new maps beginning at 9,773,000.

If no below-boundary bin passes, close residual-gap expansion. The next approach must predict value
from richer candidate/state features or expand the proposal set; do not rerun D41e or relax its +5
gate.
