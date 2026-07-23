# D35b factorized joint persistent-bundle oracle — protocol (2026-07-20)

## Purpose

D35a rejects a flat joint-signature class but validates persistent unit jobs.  D35b tests whether
coordinating those jobs for the whole team contains enough terminal value to justify a factorized
learned scheduler.

This is a hindsight upper-bound experiment.  It uses actual local opponent identity and terminal
outcomes and is deliberately non-deployable.  A pass authorizes only construction of a learned
assignment environment; it cannot produce a candidate or authorize platform activity.

## Frozen substrate and roots

- Exact D33 official map generator and exact referee/stall semantics.
- Productive baseline: the frozen `private2` Gold farm used in D34.  D34's `ownership2` differs by
  only +5.649 margin and +1.691 own score; `private2` is selected because its complete state is
  clonable through exact common roots.
- Safety reference: exact stable resident run independently in every seed/seat/opponent scenario.
- Opponents: D34's eight fixed mechanism opponents, including resident, adaptive Gold, native
  three-worker, and the worker-rich balanced proxy.
- Development seeds: signed official seeds **9,200,000--9,200,009**.
- Sealed confirmation seeds: **9,200,010--9,200,029**.
- Both seats.  Capture the first live root at or after turns 50 and 100 with exactly two baseline
  workers.  The seed is the primary statistical unit.

## Frozen factorized bundle grammar

At a root, enumerate jobs independently for each existing worker and take their collision-safe
Cartesian product.  Each worker has at most two targets per acquisition kind, ordered by predicted
completion time, reward, and cell.

### Unit jobs

1. `KEEP`: leave that worker under the warmed productive baseline while other jobs execute.
2. `BANK`: bank existing cargo.
3. `FELL_BANK(tree)`: move, chop until wood is acquired or the target disappears, then bank.
4. `HARVEST_BANK(tree)`: move, harvest once, then bank the acquired fruit.
5. `RENEW(tree, cell)`: move to a ripe tree, harvest one seed, move to the nearest available
   player-favored planting cell within radius four of the own shack, plant that species, then bank
   remaining cargo.
6. `MINE_BANK(ore-door)`: move adjacent to reachable iron, mine once, then bank.

Target jobs are invalid if capability, reachability, cargo capacity, target state, or remaining
time is insufficient.  Two jobs may not reserve the same acquisition target or planting cell.
Unit ids are stable factor positions; workforce size is not encoded into a categorical class.

### Global train goal

Each joint bundle is crossed with one of three global goals while the root has fewer than three
workers:

- no train;
- train producer `2/2/1/1`; or
- train chopper `2/2/0/2`.

A goal never invents resources.  It emits TRAIN only when the exact live bank is affordable, the
shack is clear, at least 30 turns remain, and the original jobs have not invalidated.  The assigned
HARVEST/MINE/BANK jobs may make it affordable.  The goal ends after one successful train or when
all original jobs finish without affordability.

### Execution and continuation

The complete joint bundle starts simultaneously.  Each unit persists until completion,
invalidation, or turn 300; finished units immediately return to the warmed private-farm control.
The baseline policy is evaluated every turn so its sticky targets remain current.  After every job
and global goal end, the unchanged warmed farm controls the whole side to terminal play.  The
opponent is independently warmed from the exact prefix.

The control option executes no override.  It must reproduce the uninterrupted private-farm
terminal tuple exactly at every root.  The resident reference is a separate uninterrupted game,
not a root continuation.

## Bounded enumeration

- At most two jobs per acquisition kind per unit plus BANK.
- At most 96 legal joint bundles per root after target-collision deduplication and before the three
  train goals; if the raw product exceeds 96, order by summed predicted reward rate, then ETA,
  role tuple, and targets, and retain the first 96.
- Control is always option zero.
- Record role tuple, targets, train goal, predicted values, completion status, overridden actions,
  train success, terminal scores/wood/workers, and deltas from both farm and resident.

## Integrity gate

Before outcome selection require:

1. complete 10-seed × two-seat × eight-opponent scenarios and both roots where reached;
2. control terminal identity at every root;
3. byte-identical one-seed repeat;
4. no duplicate option key, target collision, invalid direct command, or train above three workers;
5. at least 240 roots and 10,000 non-control joint bundles; and
6. at least 95% of roots expose RENEW and FELL jobs and at least 50% expose MINE or a feasible train
   goal.

## Frozen representation upper-bound gate

At each root the hindsight oracle selects control or the largest terminal margin.  Ties choose
control, then fewer overridden actions, no train, and the lexicographic option key.  The
representation passes development only if all conditions hold:

1. non-control is selected on at least 25% of roots;
2. mean oracle margin gain over private farm is at least **+20** per root;
3. selected-root mean gain is at least **+35** and median at least **+15**;
4. mean oracle own-score delta from private farm is at least **-20**;
5. mean oracle opponent-score delta from private farm is at most **-20**;
6. relative to the independent resident reference, oracle own score retains at least **+68** and
   opponent score excess is at most **+65** (half the D34 farm production gain and a material
   reduction of its opponent excess);
7. all eight opponent-family mean oracle gains are nonnegative and at least six are +10 or better;
8. selected bundles include at least two distinct role tuples in ten roots each; and
9. catastrophe frequency and negative-margin mass do not exceed the private-farm control.

If all pass, freeze an unchanged 20-seed confirmation protocol.  Otherwise leave confirmation
sealed and reject this bundle grammar before policy learning.  Do not tune target count, root
turns, job termination, train specs, or thresholds on D35b outcomes.

## Planned artifacts

- runner: `rust/src/bin/d35b_factorized_joint_bundle_oracle.rs`;
- analyzer: `cgauto/analyze_d35b_factorized_joint_bundle_oracle.py`;
- focused Rust/Python tests, development rows/result, and a written verdict.
