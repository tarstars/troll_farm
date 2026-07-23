# D84a truncated counterfactual feasibility — frozen protocol (2026-07-21)

## Question

D82 exposes +11.240 safe terminal-oracle margin at a sparse threatened-own-crop root, while D83
shows that a static snapshot ridge model captures only 10.56% of it.  Earlier online Monte Carlo
is not a direct answer: it compared two 240-turn workforce continuations under every compatible
opponent model and cost 209.487 ms median / 279.460 ms p95.  Can even an optimistic, much smaller
lookahead rank D82's semantic responses with enough value inside the 50 ms warm-turn limit?

D84a is a consumed-map feasibility upper bound.  It uses the *actual local opponent mode* that
generated each outcome, assumes independent branch states already exist, and omits state cloning,
candidate enumeration, opponent inference, thread creation, and controller overhead from timing.
These advantages are unavailable in Arena.  Failure therefore closes the current direct online
counterfactual branch; pass only authorizes a resettable-proxy implementation on fresh maps.

## Frozen roots, arms, and horizons

Replay exact D40 on consumed D82 maps 9,914,000--9,914,031, both seats, and all eight local
opponents.  Reconstruct the unchanged first `Rate` root containing a non-control `FELL_BANK`,
`HARVEST_BANK`, or `RENEW` candidate on an `Own`-provenance crop with opponent distance at most
two.  The four arms and exact-prior tie rules are identical to D82.

After the root action, return to exact D40 and record cumulative endpoints after
`1, 2, 4, 8, 16, 32` post-root macro decisions.  A macro decision includes execution of the
selected persistent job to the next natural controller boundary.  If terminal occurs early,
repeat the terminal endpoint for later horizons.  Record actual endpoint turn so unequal physical
time exposure remains visible.

For player `p`, define the coefficient-free liquid value as:

`current score + carried PLUM + LEMON + APPLE + BANANA + 4 * carried WOOD`.

IRON, crops, workers, future yield, map seed, seat, and opponent identity receive no invented
value.  Liquid margin is own liquid value minus opponent liquid value.  At each horizon select the
available arm with maximum liquid margin only if it is strictly above control; ties prefer control,
then harvest, renew, fell.  No terminal safety field may influence selection.

## Frozen execution and integrity

1. Generate the complete 4 x 512 x 6 endpoint matrix twice with 20 threads.  All columns except
   elapsed microseconds must be byte-identical.
2. Require exact D82 root identity, availability, rank, plane, and terminal arm join; zero illegal,
   fallback, finite, provenance, deposit-prediction, or endpoint-accounting failure; and exact
   control parity for unavailable arms.
3. Separately repeat maps 9,914,000--9,914,007 twice with one worker thread.  Timing begins
   immediately before the already-reconstructed root action and ends at each horizon.  Structural
   fields must repeat; timing need not.
4. Per rooted task/horizon, `serial` latency is the sum over control plus available semantic arms;
   the unattainable perfect-parallel lower bound is their maximum.  For each task use the worse of
   the two isolated repeats, then report median, p95, and maximum.  Pre-root replay and all omitted
   live costs remain excluded.

Integrity failure quarantines both value and latency and permits only a defect repair.

## Frozen value and latency gates

For every horizon report complete selected-policy terminal deltas against D82 control.  A horizon
passes value only if all hold:

1. mean terminal margin gain is at least +5.6201171875, exactly half D82's +11.240234375 oracle;
2. at least 30% of rooted tasks strictly improve and at most 25% regress;
3. mean own-score delta is nonnegative or mean opponent-score delta is nonpositive;
4. at least six opponent-family means are nonnegative and the worst is at least -2;
5. intervention rate among rooted tasks is 10%--70%, with at least two semantic arms selected in
   at least eight tasks each;
6. selected terminal crop creation is 100%, and worker-three reach degrades by at most five
   percentage points from control.

A horizon passes latency only if its optimistic perfect-parallel lower bound has p95 at most
35 ms and maximum at most 45 ms.  Serial latency is descriptive and cannot substitute for this
gate.  The 10--15 ms reserve is for the live costs deliberately omitted above.

## Decision rule

- If one or more horizons pass both conjunctions, freeze the *shortest* passing horizon and open
  D84b: a resettable, opponent-identity-blind proxy implementation and fresh-map fidelity test.
- If none pass, close direct online threatened-response Monte Carlo at this simulator/action
  representation.  Preserve D82 as an offline teacher and move to a different sequential or
  representation-learning approach; do not tune horizons, liquid weights, thresholds, arms, or
  the consumed D82 rows.
- Integrity failure permits only unchanged reruns after a mechanical repair.

No D84a outcome creates a candidate or authorizes TestSession, submission, resident replacement,
sealed-map access, or Arena activity.
