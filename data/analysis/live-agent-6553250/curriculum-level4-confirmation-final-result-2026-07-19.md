# Curriculum Level 4 independent confirmation — final result, 2026-07-19

## Verdict

**Pass; Curriculum Level 4 is accepted.**  The independently initialized seed-89 transfer path
passes the frozen teacher/control validity check, clone safety gate, PPO Stage-A gate, final
functional gate, and strict recipe-by-role action audit.  It reproduces the seed-83 discovery
result on the exact unopened confirmation bank without checkpoint selection or adaptive tuning.

Acceptance establishes that one compact shared spatial actor can condition a complete two-role
renewable economy on any of eight requested first-worker recipes against a waiting opponent.  It
does **not** authorize a live submission: opponent interaction, autonomous macro selection,
official-field transfer, compact Rust inference, latency, and the 100 kB source limit remain open.

## Frozen execution integrity

- initialization: accepted independent Level-3 checkpoint -> seed-89 Level-4 online clone ->
  seed-89 PPO;
- training stream: starts at 6,900,000, exactly 4,000,000 decisions and 400 updates;
- exact evaluation interval: 2,017,000--2,018,999, all 2,000 seeds in order;
- 100 environments x 100-decision rollouts, four PPO epochs, 14 Torch threads;
- unchanged legal-teacher auxiliary coefficient 0.10;
- no checkpoint selection, restart, hyperparameter change, or outcome-dependent seed inspection;
- 16 undefined auxiliary labels were skipped among 4,000,000 labels, for 99.9996% legal-label
  coverage, exactly under the frozen divergence-state rule; and
- Stage A passed at exactly 1,000,000 decisions and the same process continued to the final step.

The first pathname-style shell invocation failed during package import before constructing an
environment or consuming a decision.  The corrected module invocation and its zero-decision
boundary are recorded separately.  During the live process the host temporarily entered battery
`power-saver`; this changed wall-clock throughput only.  Training state, configuration, decisions,
and seed order were unchanged.

## Final functional gate

| Metric | Final result | Frozen floor | Margin |
|---|---:|---:|---:|
| Overall success | 1,994/2,000 = **99.70%** | 83% | +16.70 pp |
| Nontrivial success | **99.75%** | 78% | +21.75 pp |
| Worst recipe success | **99.16%** | 68% | +31.16 pp |
| Worst height success | **99.60%** | 68% | +31.60 pp |
| Tracked crop created | **99.75%** | 86% | +13.75 pp |
| Renewable harvest | **99.85%** | 82% | +17.85 pp |
| Gain over random legal | **+99.70 pp** | +40 pp | +59.70 pp |
| Paired-teacher median delay | **0 turns** | <=40 turns | 40 turns |

The executable `level4` profile also applies a stricter final screen: 88% overall, 83%
nontrivial, 75% recipe and height floors, 90% crop creation, 87% renewable harvest, +50 points
over random, and at most 35 turns of delay.  `L4B` passes that screen as well, so the protocol and
implementation interpretations agree.

The weakest recipe is `compact-farmer` at 235/237 = 99.16%.  The eight recipe rates span
99.16--100%; the four height rates span 99.60--99.80%.  Median training/completion turns are
14/52, median post-training score gain is 15, the teacher is 100%, and random legal is 0% on this
bank.

## Strict action audit

| Audit measure | Result | Frozen requirement |
|---|---:|---:|
| Chopper exact productive-command choice | **67,629/70,480 = 95.95%** | >=50% |
| Farmer exact productive-command choice | **27,442/30,454 = 90.11%** | >=50% |
| Worst nonempty recipe-role cell | **84.36%** (`lean-chopper` farmer) | >=30% |
| Combined unjustified selected-unit waits | **29** | <=35,000 |

Every recipe-role cell passes with at least 54.36 percentage points of margin.  The 39,846 farmer
waits on the tracked unripe BANANA crop are the sole preregistered productive-wait exemption and
are not counted as unjustified.  The result therefore reflects correct spatial targets and role
conditioning, not merely terminal success or verb selection.

## Reproducibility anchors

- frozen protocol:
  `ea4c66a270effb9040db17b2476e61bcf88f1edf2719051f6ffea42571022596`;
- independent transfer clone:
  `a5aab5d22a667268316ab620767964f2f9a088af9e545a14f7993511a4780ead`;
- final checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
- final exact-bank evaluation:
  `d1122bc4d8b21c6ad0864a3b932194efd0ad6f6934ca7dc1c450de9376f86376`;
- training summary:
  `ee0bf24d002bb50a9eef2808c5f3174e4d38f6972e203839994e731278742f29`;
- strict action audit:
  `6f81cbb5439b023d6b72dc5ebc480009c35cee3d5c2f97c78d0df773a851b9ba`.

The run used 5,270.28 seconds wall and 73,044.37 CPU-seconds, with 69.30% aggregate host CPU.
That aggregate percentage is expected on this six-P-core-plus-eight-E-core host: 14 Torch threads
occupy approximately all 14 physical cores while the system meter divides by 20 logical CPUs.
A subsequent fixed-workload benchmark rejects 16, 18, and 20 threads and manual physical-core
pinning; the retained setting is 14 unbound threads.  The full result is recorded in
`ppo-thread-parallelism-benchmark-2026-07-19.md`.

## Decision and next abstraction

Discovery and independent confirmation agree: requested randomized recipes, worker funding,
farmer/chopper coordination, crop renewal, and post-training score flow are reproducible.  The
next curriculum may add exactly **one isolated opponent-interaction abstraction** while retaining
the accepted recipe catalog, two-role controller, observation/action ABI, and resident fallback.
The opponent policy, controls, seeds, success contract, and regression gates must be frozen before
opening the next learned stream.  No PPO artifact is an Arena candidate until deployment and
field-transfer gates are separately satisfied.
