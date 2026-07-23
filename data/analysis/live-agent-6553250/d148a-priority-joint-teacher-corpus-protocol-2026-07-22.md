# D148a fresh-map priority joint teacher corpus — frozen protocol

Date: 2026-07-22  
Status: frozen after D147's full interface pass and excluded-seed D148 smoke, before touching any
D148 training seed or creating its YT build

## Hypothesis and allocation

D144 found robust incremental value from two q6 interventions and D146 retained 94.92% of that
value with 64 outcome-blind, early/immediate-prioritized schedules per task. Test transfer on 64
fresh discovery maps `9,844,136--9,844,199`. Reserve the adjacent 16 maps
`9,844,200--9,844,215` untouched for later prospective model validation.

Run eight independent 8-map joint shards and eight matching exact-one-use shards, all with 16 CPU
slots, under the exact YT root `//home/delivery_ml/research/tarstars/troll_farm`. Each joint shard
simulates one control plus 64 prioritized double schedules per task. It then selects the best
executed pair by margin, own score, opponent score, and stable source-replica tie break, and replays
that pair once to emit every legal candidate through the second action: 64 state plus 379 action
features. Exact shards run the already-validated D112 native teacher on the same maps.

The two-pass layout is intentional. Emitting every feature vector for every search episode would
create a multi-gigabyte redundant corpus; replaying the selected pair preserves the actual joint
second-state distribution while keeping repeated model fits practical.

## Pre-launch evidence

- D148's source-replica order exactly equals D146's frozen priority selection for all 128 D144
  tasks.
- Focused collector/analysis/driver/YT tests pass 12/12.
- Two excluded-seed 8-schedule runs are byte-identical for population, manifest, candidates, and
  replays.
- An excluded-seed full-budget smoke completes 1,040 population episodes at 5.87 episodes/s in the
  least-amortized one-map configuration, selects 15 valid pairs, emits 647 candidate rows, and
  exactly replays all selected terminals.

## Frozen mechanics gates

- the operation must complete exactly 16 prescribed shards with 16 threads each;
- every joint shard must finish within 2,700 active seconds and every exact shard within 1,200;
- the reconstructed population must contain exactly 66,560 unique episodes: one control and 64
  priority schedules for each of 1,024 tasks;
- source replicas, scheduled boundaries, selected actions, hashes, caps, map/seat/opponent mapping,
  and terminal arithmetic must reproduce their deterministic definitions;
- exact-one-use mechanics, finite features, root accounting, paired returns, and controls must
  pass the established D112/D133 zero-support-aware gates;
- joint control terminals must exactly equal exact-teacher baselines;
- each manifest row must be the deterministic best sampled episode with exactly two executed
  interventions, and every replay terminal must exactly equal that population row;
- candidate rows must use the exact 443-feature schema and satisfy D147's finite, group-state,
  legal-count, unique-slot, zero-control, chosen-action, wait-stage, and nonzero-selected-action
  invariants; and
- invalid-command, provenance, and deposit-prediction failure totals must all be zero. Environmental
  job invalidations are descriptive and must reproduce on replay, but are not integrity failures.

## Frozen transfer gates

Compare the best sampled executed pair with the exact best of control and one-use arms per task.
The 64-map aggregate must:

- add at least `+2.5` mean margin beyond the exact one-use oracle;
- strictly improve at least 20% of all tasks;
- have positive mean increment in at least six of eight opponent families;
- have nonnegative worst-family mean increment;
- introduce no crop failure relative to the exact one-use selection; and
- retain worker-three reach within five percentage points of exact one use.

For block robustness, split the fresh panel into its four consecutive 16-map blocks. Every block
must have positive mean increment and at least three blocks must strictly improve at least 15% of
their tasks.

If mechanics and transfer pass, build a grouped/cross-fitted joint two-stage policy from D148 while
keeping seeds `9,844,200--9,844,215` sealed. If mechanics pass but transfer fails, retain D144 as a
real discovery result but do not fit a new controller from a nontransferring population. D148
cannot qualify a candidate, open the validation panel, change the resident, submit, or interact
with Arena.
