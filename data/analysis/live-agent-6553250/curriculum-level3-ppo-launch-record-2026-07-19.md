# Curriculum Level 3 PPO launch record — 2026-07-19

## Eligibility

The frozen Level-3 clone gate passed before prospective controls were generated.  The production
PPO path then passed an end-to-end development-only smoke: checkpoint restoration, sequential
two-role rollouts, teacher auxiliary labels, GAE/PPO updates, renewable evaluation metadata,
Level-3 Stage-A/Stage-B gate routing, checkpoint output, and summaries all completed.  The smoke
used seeds outside every frozen training or evaluation interval and carries no hypothesis evidence.

Focused curriculum/tooling tests pass 21/21.  The official run is therefore eligible.

## Prospective bank frozen before learned evaluation

Exact PPO evaluation covers seeds 2,011,000--2,012,999.

| Control | Success | Nontrivial | Worst height | Crop created | Renewable harvest | Median completion |
|---|---:|---:|---:|---:|---:|---:|
| Teacher | 2,000/2,000 | 1,395/1,395 | 100% | 100% | 100% | turn 46 |
| Random legal, RNG 71 | 0/2,000 | 0/1,395 | 0% | 17.45% | 1.25% | n/a |

The teacher control hash is
`553681d43c4c21ef3f281c967da6701aa7af9555800a6fb07d7ad5b4fc498287`; the random control hash is
`f3cba72bbf8bf07885e0b419cd5129fb256b8ddac7de9d1cc556b46f4478db2b`.

## Frozen action-audit interpretation

The final policy will be audited on the same exact 2,000 seeds.  A role's productive opportunity
is a post-training decision for which the deterministic teacher does not select MOVE to the active
unit's current cell.  A learned productive choice counts only when the complete action—including
the spatial target—equals the teacher action.  Same-verb/wrong-target choices are reported but do
not pass the gate.

A selected MOVE-current is unjustified except when the farmer is standing on the tracked BANANA
crop, the crop has no fruit, and the policy is waiting for regrowth.  Discovery requires at least
60% exact productive choices for farmer and chopper separately and at most 20,000 combined
unjustified waits.  This is stricter than a verb-only reading of the protocol and was fixed before
the four-million-decision run.

Action-audit source hash:
`51e8fe7152d507e512caf04efa5d65950080e74fba07258bab7631901fb679b0`.

## Immutable official command contract

- initialize checkpoint:
  `6ea48c4e65d8bb5d786e8b47966bc60bcdd8684cc9de9e580e4e3de5ca2a2a8d`;
- model seed 71; training seed stream begins at 6,100,000;
- 100 environments x 100-decision rollouts;
- 4,000,000 total decisions; Stage A at 1,000,000;
- four update epochs, minibatch 1,000, Adam `2.5e-4` linearly to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5;
- reward scale 0.01, gradient norm 0.5, target KL 0.03;
- teacher auxiliary coefficient 0.10; 14 Torch threads; and
- the unchanged Level-3 protocol hash
  `b43a586e2e8593b5044a219271721ece9c9d273f7cbf4d2b63d7cd86e59f896d`.

Trainer source hash:
`b22b059b5d19185fb4d16916ce941840ecb2687a45c68bb35b8d5e486ef0edb2`.

Any Stage-A functional failure stops the run.  A final functional pass still requires the separate
frozen action audit and, after that, an independent confirmation before Level 3 can be accepted.
