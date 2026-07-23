# D10 post-decision attack-deadline screen — 2026-07-20

## Verdict

**Reject the temporal-window hypothesis.**  Forcing the repeated-pressure chopper back to its
natural-tree role at turns 120 through 220 does not restore the consumed teacher.  Success remains
86.60--87.20%, so late attack initiation is not the principal D10 defect.

This screen occurred only after the frozen D10 control decision and used consumed seeds 0--499.
It did not reopen D10, inspect the fixed actor, touch prospective seeds, train a model, or perform a
YT/Arena action.

## Method

For each deadline, replay the exact D10 teacher and opponent.  Immediately before a policy decision
at or after the deadline, if fewer than three destructions were confirmed, force only the
chopper's destruction-limit predicate to its completed state.  The chopper therefore returns to
the exact D9 natural-tree action.  Preserve map, player actions, opponent economy, roles, costs,
turn-180 objective, and timeout.  Record the true pre-cutoff destruction count separately from the
forced internal stop flag.

This is a diagnostic screen rather than a candidate implementation.  Its temporary ignored Rust
test was removed after execution.

## Results

| Stop pressure at turn | Success | Nontrivial | Worst recipe | Worst height | Terminal crop | Renewable harvest | >=2 destructions | >=3 destructions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 120 | **87.20%** | 88.14% | 78.57% | 82.93% | 87.20% | 87.80% | 94.60% | 81.40% |
| 140 | **86.80%** | 87.46% | 78.57% | 82.11% | 86.80% | 87.40% | 96.40% | 86.20% |
| 160 | **86.80%** | 87.46% | 78.57% | 82.11% | 86.80% | 87.40% | 98.20% | 87.60% |
| 180 | **86.60%** | 87.12% | 78.57% | 82.11% | 86.60% | 87.20% | 98.20% | 89.20% |
| 200 | **86.60%** | 87.12% | 78.57% | 82.11% | 86.60% | 87.20% | 98.20% | 89.20% |
| 220 | **86.60%** | 87.12% | 78.57% | 82.11% | 86.60% | 87.20% | 98.40% | 89.20% |

At the turn-180 screen, the 90th-percentile first/second/third confirmed destruction turns are
77/98/118.  Most third contacts are already complete long before the proposed deadline.  Even the
turn-120 cutoff retains the preregistered 80% three-destruction activation rate but improves
success by only 0.6 percentage points.

## Revised causal diagnosis

The prior count-two/failure correlation is a symptom, not proof of late censoring.  Code inspection
shows the actual recovery hole: when the crop is absent, the teacher can plant a carried banana or
pick one from home inventory, but if both are empty it moves home forever.  It never reacquires a
banana from a reachable natural or rival source.  Repeated destruction consumes the finite initial
seed stock, and stopping future attacks cannot recreate a seed.

The next smallest causal repair is therefore an **expert-only seed-reacquisition fallback**:

1. Preserve the exact D10 opponent and task.
2. When the crop is absent and carried/home banana stock is empty, route the teacher farmer to the
   best reachable banana-bearing source; harvest when ready, then replant through the existing
   path.
3. Do not gift a seed, reserve inventory, alter actor observations, change the opponent, or loosen
   success.
4. Prove that external-action trajectories are identical between D10 and the new mode, isolating
   the change to teacher label generation.

If this expert repair is control-valid, the unchanged actor can finally be evaluated against the
same recurrent-pressure task.  Only an actor failure at that point can authorize PPO and the YT
benchmark.
