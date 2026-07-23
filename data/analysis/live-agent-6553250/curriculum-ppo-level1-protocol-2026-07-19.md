# Curriculum PPO Level 1 protocol — frozen 2026-07-19

## Decision and scope

The exact Legend resident remains frozen:

- source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
- bytes: 62,725
- SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- Arena agent/submission: `6560353` / `41012883`

No source submission, Arena replacement, or resident mutation is authorized by this experiment.
Level 1 is an offline capability test for a new whole-policy architecture.

The architecture choice follows a public-strategy audit:

- Yann Moisan's contest #3 postmortem describes essentially the two-worker heuristic family from
  which the current resident descends: fund a second troll, jointly select trees to chop, and use
  fruit planting late in the game.
- Delineate's contest-winning write-up describes a different architecture: curriculum PPO first
  learns movement toward a specified worker build, then random worker builds, then whole worker
  plans and finally terminal score differential.  The final controller uses a spatial policy,
  separate worker-plan selection, joint-action conflict handling, and no runtime Monte Carlo.
- The current field reference games show that the remaining gap is complete score flow: strong
  agents combine fruit renewal, banking, later workers, and wood conversion while the resident
  usually remains a two-worker wood-only policy.

Primary references:

- <https://www.yannmoisan.com/spring-challenge-2026-postmortem.html>
- <https://gist.github.com/delineate/93ba9d48102e442e764db39d85ac44a3>
- <https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241>

This evidence prioritizes curriculum learning over another isolated target bonus or a revival of
runtime MCTS.  It does not imply that a reproduction will be cheap or that local learning will
transfer to Legend.

## Frozen Level 1 question

Can a small spatial actor-critic learn, from shaped reward, the complete resource-acquisition loop
needed to train one fixed requested worker on previously unseen 16x8 through 22x11 maps?

The requested second worker is fixed to `(ms=1, cc=3, hp=0, chop=1)`.  At workforce one its
payable cost is PLUM 2, LEMON 10, APPLE 1, and IRON 2.  Generated starts already satisfy PLUM,
APPLE, and IRON, so this first curriculum isolates one nontrivial currency loop: locate LEMON,
move, harvest, return, drop, repeat, vacate the shack, and train.  Harder and randomized builds
are forbidden until this loop is learned prospectively.

The opponent waits and never trains.  A legal `TRAIN 1 3 0 1` is automatically requested on every
turn, matching the curriculum abstraction in which the movement policy is responsible for
funding a requested worker rather than selecting the worker plan itself.  An episode succeeds
when player zero owns the requested second worker.  It ends on success or after 180 turns.

## Frozen environment and action interface

The environment uses `game::mapgen::generate_bronze`, `FastState`, `NavTable`, and `step_fast` from
the Rust simulator.  This is the only local generator with the calibrated variable Legend-sized
geometry.  The old Python generator is fixed at 16x8 and is ineligible for training.

One selected troll receives a 104x11x22 unsigned-byte observation.  The schema contains terrain,
shacks, selected/own/opponent trolls and their statistics/cargo, per-species plant state, both
inventories, turn/score/workforce globals, requested-worker statistics/cost/deficit, and compact
progress features.  Values are normalized to `[0,255]`; padded cells are identified by an
in-bounds plane.

The spatial head has exactly 13x11x22 logits:

1. `MOVE` to a cell; moving to the current cell is the canonical wait action;
2. `HARVEST` at the selected troll's cell;
3. `CHOP` at that cell;
4. `DROP` at that cell;
5. `MINE` at that cell;
6. four `PLANT` planes, one per fruit species; and
7. four `PICK` planes, one per fruit species.

Illegal actions are masked.  Level 1 exposes sensible move goals only: the current cell, current
plants, own shack, and iron cells.  This preserves the deployable action representation without
forcing the first curriculum to search hundreds of equivalent empty-cell targets.

The policy is a compact residual convolutional actor-critic.  The pilot width is 16 with four
residual blocks; width is not eligible for tuning on the held-out Level 1 evaluation bank.
Training uses masked categorical PPO with generalized advantage estimation.

The frozen run uses 100 environments x 100 rollout turns, four PPO epochs, minibatches of 1,000,
Adam at `2.5e-4` with linear decay, `gamma=0.99`, `GAE lambda=0.95`, clipping `0.2`, entropy
coefficient `0.01`, value coefficient `0.5`, and gradient norm `0.5`.  Raw environment rewards
and reported episode returns remain exactly as defined below; the optimizer receives a constant
`0.01` reward scale so the critic's MSE cannot dominate the shared trunk.  Torch uses 14 physical
cores: on this hybrid CPU, 20 logical threads cause frequency collapse and lower sustained
throughput by more than an order of magnitude.

## Reward fixed before outcomes

The reward is potential-based progress plus a terminal bonus:

- the potential estimates turns still required to bank the requested resource deficits, counting
  correctly carried items and travel to the next useful tree/iron approach or back to the shack;
- per transition reward is `old_potential - new_potential - 0.01`;
- successful construction adds `+20`;
- timeout adds `-20`.

No score, wood, opponent suppression, arbitrary action bonus, or imitation label is present in
Level 1.  The potential may accelerate the requested skill but cannot by itself establish
whole-game value.

## Data partition and training budget

- implementation/debug seeds: `0..9999`; never report these as generalization evidence;
- training stream: starts at `1,000,000`, deterministically advanced by vector-environment slot;
- replicate training stream: starts at `3,000,000` and is never used by the first run;
- frozen held-out evaluation: `2,000,000..2,000,999` (1,000 episodes);
- frozen replicate evaluation: `2,001,000..2,001,999`, opened only if the first learned model
  passes its gate;
- Stage A budget: at most 250,000 agent transitions;
- Stage B budget: at most 1,000,000 cumulative transitions for the first run;
- replicate run: a different initialization/training stream, at most 1,000,000 transitions, only
  after the first run passes Stage B.

Random-legal and deterministic shortest-useful-path baselines are evaluated on the frozen bank
before judging the learned model.  They are controls, not training demonstrations.

## Frozen gates and stop rules

### E0 — integrity

- release build and focused Rust/Python tests pass;
- repeated reset plus identical action streams produce byte-identical observations, masks,
  rewards, terminal flags, and episode statistics;
- every unmasked action decodes to its documented command and no masked-only engine command is
  required by the deterministic teacher;
- the existing slow/fast one-step resynchronization check has zero inventory and plant-count
  differences on at least 30 seeds.  Position divergence is reported separately: both local
  engines use deterministic substitutes for the referee's randomized path ties, so exact position
  parity is not claimed.

Failure closes this implementation until repaired; it does not reject curriculum PPO.

### E1 — resource use

- batched environment-only throughput is at least 25,000 transitions/s on this host;
- combined rollout inference is at least 1,000 transitions/s;
- PPO updates use at least 70% aggregate host CPU on a representative sample, unless wall-clock
  throughput is already above 5,000 transitions/s;
- peak resident memory remains below 16 GiB.

### L1A — early learning

At or before 250,000 transitions, deterministic held-out success must be both:

- at least 40%; and
- at least 20 percentage points above the random-legal baseline.

If L1A fails, stop this reward/network instance.  Do not extend the budget or tune on the held-out
bank.

### L1B — learned capability

At or before 1,000,000 transitions, the first run must achieve all of:

- at least 70% held-out success;
- at least 30 percentage points above random legal;
- median completion turn no more than 25 turns slower than the deterministic teacher among seeds
  both solve; and
- no map-height bucket below 55% success.

If it passes, open the replicate bank and train once from a different initialization.  The
replicate passes at 60% success with no height bucket below 45%.  Level 1 is accepted only if both
runs pass their respective gates.

## Interpretation and next branch

- E0 failure means environment work remains.
- E1 failure means vectorization/runtime work remains.
- L1 failure rejects only this fixed reward/network instance; inspect failure by action family,
  resource deficit, travel distance, and map height before proposing one revised curriculum.
- L1 acceptance authorizes Level 2: random requested worker specifications with the same automatic
  training abstraction.  It does not authorize a resident candidate.
- Only later levels may learn worker-plan selection, multiple selected trolls, self-play/league
  opponents, and terminal score differential.  A deployable survivor must still fit the 100,000
  character source cap, meet turn latency, pass local whole-game safety, and then pass the frozen
  layered TestSession field gate plus a separate confirmation bank.
