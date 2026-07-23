# D162a resident-native bounded capital option — frozen protocol

Date: 2026-07-23  
Status: frozen before implementation or outcome generation

## Question

D161 closes D40/q6: even its per-task terminal oracle is not safely resident-dominant. D160 shows
that the exact resident has no natural third-worker affordability window. D162 asks the smallest
remaining causal question: can an exact-resident-native, bounded multi-turn reserve option create
useful third-worker headroom while preserving a warmed resident KEEP path?

This is an action-vocabulary pilot, not a deployable selector. It must not train PPO, use a model,
open new maps, contact YT or the platform, create a candidate, or alter the resident.

## Frozen panel

Reuse the first eight already-consumed D148/D161 maps, `9,844,136--9,844,143`, both seats and all
eight frozen opponent families: 128 tasks. Maps `9,844,144--9,844,199` remain available only for a
later expansion. Reserved maps `9,844,200--9,844,215` remain untouched.

Run the complete matrix once with one worker and once with 20 workers. Require byte-identical,
sorted output. The resident control must match D161 exactly on every shared score, workforce,
crop, mechanics, action-hash, and state-hash field.

## Frozen option interface

Every policy calls the unchanged exact resident on every referee turn, including intervention
turns, so its internal state remains warm. KEEP emits the resident command unchanged. A capital
option may activate only with exactly two own workers. It then:

1. computes the referee-exact bill from deposited bank and carried stock;
2. protects still-missing bill resources from resident PICK/PLANT consumption;
3. temporarily routes at most one suitable worker at a time to bank carried resources, harvest a
   reachable ripe missing fruit, or mine missing IRON while all other legal resident work remains;
4. emits TRAIN only from a deposited bill, suppressing same-turn PICK and shack-blocking MOVE;
5. commits when worker three appears, aborts at its fixed horizon, and otherwise immediately
   returns to the already-warmed exact resident; and
6. never owns post-training worker policy—the exact resident controls every worker after commit.

No crop planting, source construction, opponent identity branch, score branch, map identity,
outcome lookup, learned coefficient, or option restart is allowed.

The frozen catalog contains exact resident plus the Cartesian product:

- worker specification: minimal `1/1/0/1` or balanced `2/2/0/2`;
- activation turn: `72`, `104`, or `136`; and
- maximum active horizon: `32` or `64` referee turns.

There are therefore 13 policies and 1,664 rows per complete run.

## Frozen gates

### Integrity and mechanics

1. both matrices contain exactly 1,664 unique rows and are byte-identical;
2. exact resident reproduces D161 on all 128 tasks and all shared fields;
3. every row terminates with exact reward identity and zero provenance, ambiguous-birth, option
   command-legality, affordability, transaction, worker-cap, or horizon violations;
4. no option activates outside its start/deadline window, restarts, or changes a preactivation
   action hash; and
5. at least ten of twelve arms activate in at least 90% of tasks, at least four arms create worker
   three in at least 10% of tasks, successful training spans both seats and at least six families,
   and no task exceeds three own workers.

Any integrity failure is repaired without interpreting value. A clean mechanism failure closes
this exact one-lane reserve interface.

### Resident-relative capacity

Construct a per-task hindsight envelope over the 12 arms plus exact resident. An arm is eligible
for selection only if it does not remove all resident-created crops from a task that had one; ties
prefer resident, then earlier catalog order. Because resident is an explicit action, the envelope
may never select a strict regression.

The pilot opens expansion only if all conditions hold:

1. mean margin gain is at least `+8`, at least 25% of tasks strictly improve, and the map-clustered
   normal 95% lower bound is above zero;
2. at least six family means are positive and all family means are nonnegative;
3. both seats and at least three of the four consecutive two-map blocks have positive mean gain;
4. selected mean own-score delta is nonnegative or mean opponent-score delta is nonpositive;
5. selected crop-creation rate is no more than two percentage points below resident, and
   catastrophe count and negative-margin mass do not increase;
6. selected worker-three rate is at least 10%; and
7. at least four individual arms each have at least four strict resident-relative wins.

Passing opens only a preregistered expansion over the remaining 56 consumed D161 maps and the
construction of resident-relative option labels. Failure closes this exact reserve grammar; it
does not reopen D40/q6 or authorize parameter tuning on these outcomes.

## Infrastructure

No YT operation is part of D162. If later work uses YT, its canonical root is exactly
`//home/delivery_ml/research/tarstars/troll_farm`.
