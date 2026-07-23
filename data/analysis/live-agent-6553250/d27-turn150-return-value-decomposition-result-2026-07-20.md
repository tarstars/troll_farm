# D27 turn-150 return-value decomposition — result (2026-07-20)

## Verdict

**Cold re-entry is a primary D26 failure.**  On the exact shared farm state at turn 150, replacing
`ownership2` with a cold resident costs -20.649 terminal margin, with a seed-clustered 95%
interval of [-29.581, -11.718].  This satisfies the frozen diagnostic criterion by a wide margin
and prioritizes implementable handoff-state mechanisms next.

D27 is read-only.  It opens no seed, revives no rejected branch, authorizes no candidate, and
causes no Arena action.

## Integrity

All 1,920 expected cells match across the two D24 files and D26.  There are no missing or duplicate
branches, all root fields match, and every D24 resident terminal field and command hash exactly
matches D26.  For margin, scores, and wood, the decomposition identity has zero residual in every
cell.

The two compared branches are identical from turn 75 through turn 149 by deterministic source
construction: same root, `ownership2` instance, warmed opponent instance, and command sequence.
Only their turn-150 continuation differs.

## Decomposition

| Seed-clustered component | Margin | 95% interval | Own score | Opponent score | Own wood | Opponent wood |
|---|---:|---:|---:|---:|---:|---:|
| Permanent farm path, `F - R` | +21.609 | [+8.852, +34.367] | +63.783 | +42.174 | +14.357 | +8.469 |
| Cold return at 150, `P - F` | **-20.649** | **[-29.581, -11.718]** | **-35.449** | -14.799 | -6.118 | -2.855 |
| Observed pulse, `P - R` | +0.960 | [-3.919, +5.839] | +28.334 | +27.374 | +8.240 | +5.615 |

The return does restore suppression: the opponent loses 14.80 score relative to continuing the
farm.  But it destroys 35.45 own score, so the net continuation cost is 20.65 margin.  This is not
an adaptive-Gold-only effect.  Return effects are negative against all eight families, ranging
from -9.733 against Silver to -37.750 against Printer; adaptive Gold is -17.475.

## Tail and regime structure

| Terminal policy | Mean cell margin | Catastrophes | Negative-margin mass | Ratio to resident |
|---|---:|---:|---:|---:|
| Resident | +38.137 | 15.00% | 59,015 | 1.000x |
| Permanent farm | +59.747 | 12.55% | 58,605 | 0.993x |
| Turn-150 cold return | +39.097 | 16.51% | 64,270 | 1.089x |

On the resident's 288 catastrophic cells, the permanent farm improves margin by +54.566, but the
cold return gives back -44.003 of that benefit.  It leaves only the +10.563 pulse improvement
reported by D26.

The return behaves mostly as an aggressive hedge rather than a uniformly inferior continuation:

- in 979/1,920 cells the farm path is positive and the return is negative;
- in 700/1,920 cells the farm path is negative and the return is positive;
- only 226 cells have both components with the same nonzero sign; and
- 15 cells contain a zero component.

Thus returning often repairs a bad farm trajectory, but it removes more value from good farm
trajectories than it saves from bad ones.  A fixed switch compresses the farm's outcome spread at
the cost of nearly all mean advantage and creates more deep losses than either full policy.

## Interpretation boundaries

The combined consumed 120-map corpus makes the permanent farm look much stronger than either D24
half alone: +21.61 seed mean, fewer catastrophes, and almost equal negative mass.  This is useful
mechanistic evidence, not a retrospective validation pass.  D24's sealed half failed its frozen
gates, and combining development with failed confirmation cannot authorize submission.

D27 also cannot yet say that internal memory alone causes the return loss.  The cold bot both
forgets resident history and reinstates the resident's lower-production scheduling.  The next
experiment must hold the turn-150 game state and post-150 policy family fixed while varying only
how the resident state is carried across the farm interval.

## Next experiment

Compare two small, implementable alternatives at the same frozen turn-150 handoff:

1. **paused resident:** retain the exact warmed turn-75 resident object without asking it for
   hypothetical commands during the farm interval, then resume it at turn 150;
2. **shadow resident:** retain the resident and advance it on each observed farm state while
   discarding its hypothetical commands, then activate it at turn 150.

Cold restart, permanent farm, and warmed resident remain controls.  The paused variant is directly
deployable.  The shadow variant is diagnostic because its remembered commitments may refer to
commands that were not executed; it requires a later actual-command observer before deployment.
No cutoff may be tuned in this experiment.

## Evidence and hashes

- protocol: `d27-turn150-return-value-decomposition-protocol-2026-07-20.md`;
- analyzer: `cgauto/d27_return_value_decomposition.py`;
- result JSON: `d27-turn150-return-value-decomposition-50000-50119.json`.

SHA-256:

- protocol: `ba9d30c72df5f917ac28d0f8deafbfa72d60a52b80b6d8dd351fb5209fdb3308`;
- analyzer: `c519fa5003dd1d933705580a0dfc6abc43f099478be885973bd6b7fec9c044f2`;
- JSON: `a26566bf27b555eae79caee11ba73cdbdd426d838fc5f54f7e927d693db43060`.
