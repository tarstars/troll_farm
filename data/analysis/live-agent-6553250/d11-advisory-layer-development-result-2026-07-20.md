# D11 resident-gated advisory layer — development result (2026-07-20)

## Decision

**Reject every tested inference-time D11 advisory policy.  Do not open a prospective block and
do not alter the resident, candidate, submission, or Arena state.**

The narrow second-worker idle override is the only positive result, but it misses the frozen
map-level confidence gate and its gain is almost entirely one-map-specific.  Preserve it as a
mechanistic lead for a resident-state residual learner, not as a hand-written selector.

## Complete execution

All 576 planned exact-engine games completed on reused seeds 0--7, both seats, the frozen
six-opponent panel, and six paired policies.  Every policy retained the resident worker count in
96/96 cells.

| Policy | Map-balanced margin delta | 95% map CI | Worst opponent | Overrides | Activated cells | Worst decile |
|---|---:|---:|---:|---:|---:|---:|
| second worker, resident `WAIT` only | **+2.375** | `[-2.303, +7.053]` | **+0.688** | 869 (1.73%) | 91 | -1.9 |
| starter, local crop action | -2.729 | `[-6.434, +0.976]` | -14.188 | 228 (0.45%) | 53 | -51.0 |
| second worker, local crop action | -6.552 | `[-14.833, +1.728]` | -25.938 | 452 (0.91%) | 67 | -68.3 |
| second worker, any productive local action | -7.469 | `[-16.343, +1.405]` | -25.625 | 538 (1.08%) | 69 | -71.8 |
| both workers, any productive local action | -105.948 | `[-140.300, -71.596]` | -181.250 | 10,247 (19.77%) | 96 | -301.8 |

No policy passes all nine frozen gates.  The idle-only rule passes every gate except the 95%
lower bound over eight map means, which is -2.303 rather than nonnegative.

## What the positive result really contains

The idle-only rule changes just 12 of 96 paired terminal outcomes: ten wins, two losses, and 84
ties versus the resident.  Its cell mean is +2.375 with normal 95% CI `[+0.660, +4.090]`; wood
edge rises by +0.583.  It is nonnegative against every opponent, including +1.063 against the
resident itself.

That apparent breadth is misleading at the map level.  Seeds 0--4 and 6 have exactly zero mean
effect, seed 5 is -0.083, and seed 7 is +19.083.  The largest loss is -18 on seed 7, seat 1,
against the resident; the largest gain is +40 on the same seed and seat against `gold_adaptive`.
The rule therefore identifies a real local opportunity but does not establish a portable
policy.

The broader rules confirm the earlier role-substitution diagnosis.  PPO actions are sometimes
locally executable, but replacing resident transit or task execution breaks assignment and
route coordination.  Increasing override coverage monotonically increases this failure rather
than recovering the actor's curriculum score.

## Next experiment

Run one explicitly diagnostic replication of the idle-only mechanism on a separate development
map block.  Its purpose is to decide whether there is enough outcome-changing, cross-map signal
to justify an offline resident-state residual dataset.  It cannot promote the rule.

If the effect is sufficiently distributed, collect exact one-intervention continuation labels
at resident-`WAIT` decisions and distill a small accept/reject controller using full resident
state and recent resident intent.  If it remains concentrated or reverses, stop adapting D11 and
build the next PPO curriculum around resident trajectories, joint assignments, and full-game
reward from the outset.

## Evidence

- protocol: `d11-advisory-layer-development-protocol-2026-07-20.md`;
- rows: `d11-advisory-layer-development-seeds0-7.tsv`, SHA-256
  `f9821dd0933ad9f9d89baa8e7c0c6c4a4b4084f2df984e3e514980d814172f7b`;
- analysis: `d11-advisory-layer-development-2026-07-20.json`, SHA-256
  `1c65e125852b2acd795ffc6d52e30ecdb820823b6f6e4b34451264c86f35f33b`;
- analyzer: `cgauto/d11_advisory_layer_analysis.py`, SHA-256
  `f065304b82cd8ac2b5493d3522fd31757625f9779b801e54878629fac8700be6`;
- exact runner: `rust/src/bin/d11_recipe_catalog.rs`, SHA-256
  `3547ff337a69c668d66b865c029af11c5581771b88d124bdc71c6d34a49f4515`.

