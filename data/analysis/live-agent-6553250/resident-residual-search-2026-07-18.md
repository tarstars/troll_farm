# Resident-backed residual search — 2026-07-18

## Hypothesis

The GoldElite residual-search experiment showed that bounded, role-preserving MOVE corrections can
add value without replacing a complete policy. It was never a deployable result because GoldElite
was both its baseline and continuation. This phase tests the same architecture around the actual
62,725-byte Yamo/Orchard resident.

This is deliberately different from the rejected Norxondor program:

- the resident produces every root state and remains the continuation;
- search changes at most one MOVE target and never interrupts CHOP, HARVEST, DROP, PICK, PLANT,
  MINE, or TRAIN;
- an accepted target is committed for at most eight turns and then returns to resident control;
- short exact rollouts compare each correction with byte-equivalent resident commands from the
  same state;
- GoldElite and Scheduler are ambiguity models, not replacement policies.

## Predeclared smoke protocol

The implementation screen uses already-consumed discovery seeds **0--4**, both seats, and the
eight existing deterministic opponent continuations. It opens no new validation or holdout data.

The initial profile is frozen from the prior residual experiment:

- search begins at turn 80 after a chop-capable worker exists;
- at most 14 joint commands, including exact resident control;
- four-turn screen, top four finalists, then sixteen-turn evaluation;
- require at least +5 leaf value against both GoldElite and Scheduler;
- commit one changed target for at most eight turns;
- suppress a target after an expired commitment fails to unlock direct work.

The algorithmic smoke gate requires:

1. at least one accepted deviation;
2. at least +2 mean paired margin and +2 own-score delta versus resident;
3. at least five of eight nonnegative opponent mean-margin deltas;
4. worst opponent mean-margin delta at least -5;
5. decision-time p95 at most 45 ms and no decision above 50 ms in the release timing sample.

Failing the score/opponent gate closes direct transplantation of this residual evaluator. Failing
only source size or timing permits offline own-state label generation and compact distillation,
but not an online candidate. No smoke outcome authorizes a candidate, holdout, submit-helper
change, or arena write.

The resident artifact and checksum remain:

- `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`;
- 62,725 bytes;
- SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

## Initial all-MOVE result

The frozen seeds 0--4 screen covers 80 opponent cells. Search evaluates 10,456 states and accepts
49 deviations in 37 cells.

- +1.200 mean paired margin, 17/52/11 cells, range -13 to +34;
- +0.913 mean own score, 17/59/4 cells, range -17 to +12;
- all eight opponent mean-margin deltas are nonnegative; the worst is Scheduler at +0.100;
- 130.047 ms decision p95, 224.449 ms maximum, and 8,421/22,509 decisions over 50 ms.

The profile fails both +2 effect gates and both timing gates. Direct online transplantation is
closed, and the all-MOVE teacher does not qualify for own-state distillation.

## Behavior-neutral event audit

A repeat on the same consumed cells added event telemetry without changing the evaluator. Several
actual opponent implementations retain process-sensitive hash iteration, so the repeat has 48
rather than 49 accepted events and is descriptive rather than exact repeat evidence.

| Changed target | Events | Median turn | Mean scenario margin | Mean scenario score | Singleton W/T/L |
|---|---:|---:|---:|---:|---:|
| shack / bank | 21 | 129 | +6.429 | +3.619 | 9/3/4 |
| plum tree | 8 | 81 | +0.875 | +2.875 | 3/0/2 |
| banana tree | 14 | 126.5 | +4.214 | +0.286 | 1/1/6 |
| apple tree | 5 | 136 | -4.200 | -2.200 | 0/0/2 |

The tree-target signal is not coherent: singleton banana and apple corrections mostly lose even
though both rollout models predict at least +5. Bank redirects are the only class with positive
margin and score in both all-event and singleton views. This motivates one restricted replication,
not threshold tuning of the failed all-MOVE profile.

## Predeclared bank-only replication

Seeds **5--19** are historically consumed discovery maps but are disjoint from the event audit.
The bank-only profile is fixed before running them:

- retain exact resident control plus only candidates whose changed target is our shack;
- keep turn 80, 4/16-turn horizons, +5 two-model floor, and eight-turn commitment unchanged;
- keep all direct work and TRAIN commands immutable;
- require at least 20 accepted deviations across 240 cells;
- require +2 mean margin, +2 mean own score, five nonnegative opponent means, and a worst opponent
  mean of at least -5;
- evaluate timing separately at p95 <=45 ms and maximum <=50 ms.

If the algorithmic gate passes but timing fails, the bank decision may become an offline own-state
teacher. If the algorithmic gate fails, close the residual branch without another candidate class,
horizon, threshold, or seed sweep. The range is discovery/replication only and cannot become a
holdout.

## Bank-only result and final verdict

The replication covers all 240 predeclared cells and accepts 103 redirects in 83 cells, well above
the activation minimum.

- +0.508 mean margin, 38/173/29 cells, range -33 to +27;
- +0.554 mean own score, 31/189/20 cells, range -22 to +24;
- 7/8 opponent margin means nonnegative; ScriptBoss is worst at -0.300;
- 92.852 ms decision p95, 229.508 ms maximum, and 15,237/67,289 decisions over 50 ms.

The effect is smaller than the audit suggested and misses both +2 gates by a wide margin. The
result also demonstrates why target-class postselection on a tiny event audit is not prospective
evidence: bank redirects were the best descriptive class on seeds 0--4 but do not replicate at a
useful magnitude on 5--19.

**Close the resident residual branch.** The existing GoldElite result does not transfer strongly
enough to Yamo/Orchard, broad MOVE corrections are too slow and weak, and the only coherent class
does not replicate. Do not tune the start turn, leaf margin, horizons, commitment, candidate class,
or seed range; do not distill, package, validate, or submit it.

## Evidence

- `yamo-resident-residual-smoke-0-4.tsv`
- `yamo-resident-residual-study-smoke-0-4-2026-07-18.json`
- `yamo-resident-residual-event-audit-0-4.tsv`
- `yamo-resident-residual-event-audit-0-4-2026-07-18.json`
- `yamo-resident-bank-residual-replication-5-19.tsv`
- `yamo-resident-bank-residual-replication-5-19-2026-07-18.json`
