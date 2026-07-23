# D37 complete factorized macro PPO — frozen protocol (2026-07-21)

## Question

D35 proves that persistent factorized jobs, target provenance, and repeated completion-boundary
decisions have causal terminal value. D36 proves that returning those jobs to the resident cannot
produce a strong complete economy. D37 asks the next architectural question: **can a compact
learned scheduler own the entire trajectory and combine renewable production, workforce growth,
and rival-loop suppression without the primitive-action drift seen in D21?**

D37 is a local learning pilot, not a candidate study. A pass authorizes a larger replica portfolio
and exact-engine qualification only. It does not authorize source integration, TestSession,
submission, resident replacement, or Arena activity.

## Frozen complete controller boundary

- Start from the exact initial official-map state and control through exact terminal/stall state.
- Use both seats and the unchanged eight D34--D36 mechanism opponents.
- No command from the resident, productive farm, D11 actor, or any other policy may execute on our
  side. There is no phase handoff or inference-time fallback.
- Cap the pilot at three own workers. Global choices are `NO_TRAIN`, persistent
  `TRAIN_PRODUCER_2211`, and persistent `TRAIN_CHOPPER_2202`; the selected goal is attempted only
  when legal and may be changed at a later decision boundary.
- A learned decision occurs for the global TRAIN goal and whenever an own worker is free. Existing
  jobs remain active asynchronously while free workers are reassigned in stable unit-id order.
- After all currently free workers receive jobs, the exact referee advances until terminal or the
  first job completion/invalidation, successful TRAIN/new worker, or one-turn idle completion.

This makes the learned policy the complete scheduler while retaining deterministic mechanics in
the same sense that a primitive legal-action mask and movement resolver are environment mechanics.

## Frozen factorized action interface

Each free worker selects one masked role/target action:

1. `IDLE_ONE_TURN` at its current cell;
2. `BANK` at our shack when carrying inventory;
3. `FELL_BANK` at a live tree, with creator provenance retained as a target attribute;
4. `HARVEST_BANK` at a ripe plant;
5. `RENEW` at a ripe plant, with a deterministic reachable player-favored planting cell;
6. `MINE_BANK` at a reachable iron-adjacent cell.

`BANK`, acquisition, planting, and return-to-shack phases are deterministic persistent executor
states. A target invalidated by simultaneous opponent play frees the worker at the next boundary;
it never invokes another policy. Targets and planting cells already reserved by active or newly
selected jobs are masked. Every worker always has `IDLE_ONE_TURN`, so an empty action set is an
integrity failure.

Use a fixed spatial action tensor: three global TRAIN planes and six worker-role planes over the
canonical 11 x 22 board. Only the relevant stage's cells are legal. Pressure is not a separate
role; natural/own/opponent/ambiguous provenance is encoded in the observation and attached to every
tree target, preserving the D35a/D35c conclusion.

## Frozen observation and history contract

Reuse the accepted D11 player-relative 104-channel state encoding, but regenerate it from the exact
official engine. Add only prospectively specified channels for:

- four plant-provenance classes;
- active worker role and reserved target by role;
- current decision stage, selected/free worker ordinal, and persistent TRAIN goal;
- job age/completion status; and
- compact cumulative and recent own/opponent counts for PLANT, HARVEST, CHOP, DROP, MINE, and
  TRAIN, plus worker counts and score/wood trajectories.

No opponent nickname/index, seed, future state, terminal outcome, resident outcome, exact opponent
policy type, or hindsight rollout value may enter the actor observation. All count updates use only
commands and state changes already observed by the controller. The exact channel list and scales
must be frozen in a schema manifest before any learning outcome is generated; schema changes then
require a new experiment identifier.

## Environment integrity and preflight

Implementation uses a batched Rust environment with a NumPy/ctypes wrapper. Before learning:

1. official map/state/referee parity must match D33 fixtures and exact-engine controls;
2. all direct commands must be legal, all candidate keys unique, reservations collision-free, and
   provenance complete after every step;
3. the undiscounted vector reward must telescope separately to terminal own score, opponent score,
   and margin in every episode within `1e-4` score points;
4. a deterministic highest-rate heuristic and its complete episode rows must be byte-identical on
   two independent runs;
5. every TRAIN success must match its requested spec, no branch may exceed three workers, and new
   workers must enter the free-worker queue exactly once;
6. exact terminal replay from the recorded macro actions must reproduce every state/outcome hash;
7. random legal and deterministic heuristic controls must both complete all cells with zero empty
   masks or invalid selections; and
8. the heuristic must beat random by at least +50 mean margin, create a renewable crop in at least
   60% of episodes, train worker two in at least 80%, train worker three in at least 15%, and execute
   a median of at least four non-idle jobs.

Use official seeds 9,600,000--9,600,015, both seats, and all eight opponents: 256 episodes per
control. Repeat only the deterministic heuristic. These are engineering/preflight cells and cannot
select a learned checkpoint.

## Frozen behavior initialization

Generate exactly 200,000 macro decisions from the deterministic highest-rate/provenance heuristic
on a disjoint hashed stream beginning at 9,700,000. The heuristic may see only the same deployable
observation, candidates, and history as the actor. Hold the final 10% by contiguous episode seed;
do not rebalance or resample after generation.

Train one compact spatial actor/critic with model seed 3701. The actor uses the fixed nine-plane
mask; a scalar critic receives the same encoded state. Behavior cloning is accepted only if the
final, predeclared epoch reaches at least 85% held-decision accuracy, at least 70% on every worker
role with 500 or more held examples, at least 90% on the global TRAIN stage, and zero illegal
deterministic actions in 256 fresh smoke episodes. No best-epoch selection is allowed.

The behavior-cloned actor is an initialization and paired control, not a selectable candidate.

## Frozen conservative PPO pilot

Freeze the behavior-cloned actor byte-for-byte. Add a zero-initialized residual actor branch and a
fresh critic; keep the base actor frozen throughout PPO. The executed policy is always
`base_logits + residual_logits`, so it remains one complete learned controller—there is no
fallback gate. Penalize policy KL to the frozen base distribution and retain a small heuristic
auxiliary only to protect mechanics.

Run exactly one local pilot unless a separately preregistered backend-parity benchmark authorizes
YT:

- model seed 3707 and hashed training stream beginning at 10,000,000;
- 96 vector environments x 64 macro decisions per update;
- exactly 600,000 macro decisions;
- four PPO epochs, minibatch 1,024, Adam `2.0e-4` decaying linearly to zero;
- gamma 1.0, GAE lambda 0.95, clip 0.15, entropy coefficient 0.005, value coefficient
  0.5, gradient norm 0.5, and target update KL 0.02;
- exact margin-delta reward scaled by 0.01, reference-KL coefficient 0.05, and legal heuristic
  auxiliary coefficient 0.05; and
- no intermediate evaluation, adaptive early stopping, reward shaping, terminal asset bonus,
  checkpoint selection, or hyperparameter selection.

Every semi-Markov reward covers all exact referee turns advanced by the chosen macro action and
must preserve terminal return identity. Gamma remains one so variable job duration does not create
an implicit preference for short jobs.

## Frozen development evaluation

Evaluate only the final PPO checkpoint and the frozen behavior actor on official seeds
9,610,000--9,610,031, both seats, all eight opponents: 512 paired episodes each. Compute unchanged
resident and productive-farm controls on the same cells. Cluster uncertainty by map seed.

The pilot passes only if all hold:

1. every episode/action is finite, legal, deterministic on repeat, and exactly replayable;
2. final mean margin improves by at least +5 over behavior initialization, at least six of eight
   opponent-family means are nonnegative, and no family regresses below -10;
3. final own score does not fall below behavior initialization and opponent score does not rise by
   more than +5;
4. versus resident, final own-score gain is at least +68, opponent-score excess is at most +65,
   and margin gain is at least +25;
5. at least six opponent families gain +50 own score and at least six gain +15 margin versus
   resident, with all eight means nonnegative;
6. crop creation remains at least 70%, worker-two training at least 90%, and worker-three training
   at least 25%; and
7. catastrophe frequency and negative-margin mass do not exceed either behavior initialization or
   resident.

A pass opens seeds 9,620,000--9,620,063 for one unchanged confirmation and then a frozen independent
replica portfolio. Any failure closes this exact environment/model/optimizer combination and leaves
confirmation sealed. Diagnose the failed abstraction—action coverage, initialization, optimization,
or generalization—without tuning on consumed cells.

## Compute rule

Keep preflight, behavior data generation, smoke, and the first 600k pilot local. Record environment
steps/s, inference/training time, host CPU use, and projected replica cost. YT is economically
eligible for later replicas because the prior RTX 4090 run was 9.82x faster, but technically
ineligible until this exact macro environment clears a fresh frozen local/YT backend-parity check.

## Planned artifacts

- Rust library module and focused exact-engine/action/executor tests;
- Python ctypes environment, schema manifest, and corruption/repeat tests;
- preflight controls and machine-readable gate;
- behavior dataset, final behavior checkpoint, and held-action audit;
- frozen pilot checkpoint, training summary, paired development evaluation, and written verdict;
- update to the standing Legend top-three cycle log after every gate.
