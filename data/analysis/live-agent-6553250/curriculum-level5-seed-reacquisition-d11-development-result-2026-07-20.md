# Curriculum Level 5 seed-reacquisition expert D11 development result — 2026-07-20

## Verdict

**Accept D11 as the first control-valid sustained interaction that defeats the fixed actor.**  On
exact unopened seeds 6,000--6,499, teacher/random/actor are 500/500, 0/500, and **397/500 =
79.40%**.  Every task and opponent mechanism gate passes under both teacher and actor, while the
actor fails all six player-robustness gates.

This authorizes failure diagnosis and a separately frozen clone/PPO protocol.  It does not
authorize prospective access, checkpoint replacement, deployment, or Arena submission by itself.

## Fresh controls

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **100% / 100%** | >=95% / >=95% | pass |
| Worst recipe / height | **100% / 100%** | >=90% / >=93% | pass |
| Terminal crop / renewable harvest | **100% / 100%** | >=95% / >=95% | pass |
| Illegal selections / earliest success | **0 / turn 180** | 0 / >=180 | pass |
| First / third-worker training | **100% / 97.40%** | >=98% / >=90% | pass |
| Fresh first / second funding receipt | **100% / 100%** | 100% / 100% | pass |
| Standard-chopper / feeder productivity | **100% / 94.80%** | >=98% / >=85% | pass |
| Rival crop creation / own harvest | **100% / 91.00%** | >=98% / >=85% | pass |
| At least one / two / three destructions | **99.40% / 98.60% / 96.00%** | >=98% / >=95% / >=90% | pass |
| Maximum destructions / workers | **3 / 3** | <=3 / <=3 | pass |
| Random legal | **0/500** | <=5% | pass |

The source fallback generalizes beyond its consumed screen: all eight recipes and four heights are
perfect without reducing pressure.

## Fixed actor

| Measure | Actor | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **79.40%** | >=85% | **fail** |
| Nontrivial success | **76.67%** | >=82% | **fail** |
| Worst recipe | **70.00%** | >=75% | **fail** |
| Worst height | **75.40%** | >=78% | **fail** |
| Terminal crop | **79.60%** | >=80% | **fail** |
| Renewable harvest | **83.60%** | >=90% | **fail** |
| Earliest success / paired median delay | **turn 180 / 0 turns** | >=180 / <=30 | pass |
| First / third-worker training | **100% / 97.80%** | >=98% / >=85% | pass |
| Fresh first / second receipt | **100% / 100%** | 100% / 100% | pass |
| Standard-chopper / feeder productivity | **100% / 94.20%** | >=98% / >=80% | pass |
| Rival crop creation / own harvest | **100% / 91.80%** | >=95% / >=80% | pass |
| At least one / two / three destructions | **99.60% / 97.20% / 84.40%** | >=95% / >=85% / >=70% | pass |
| Maximum destructions / workers | **3 / 3** | <=3 / <=3 | pass |

Opponent activation is at least as strong under the actor as required, excluding interaction
avoidance.  Zero paired median delay also shows that successful episodes retain the learned
turn-180 schedule; the deficit is concentrated in failed recovery trajectories.

## Failure decomposition

All 103 actor failures reach timeout, and every target worker is built.  Among failures:

- 102/103 end without the tracked crop;
- 82/103 never record renewable player harvest;
- 35/103 also remain short of the required score gain; and
- no successful episode ends without its crop.

| Confirmed destructions | Episodes | Successes | Success rate | Terminal crop rate |
|---:|---:|---:|---:|---:|
| 0 | 2 | 2 | 100% | 100% |
| 1 | 12 | 5 | 41.67% | 41.67% |
| 2 | 64 | 12 | **18.75%** | **18.75%** |
| 3 | 422 | 378 | 89.57% | 89.81% |

As in the weak D10 expert, ending below the cap signals a crop-less absorbing trajectory while the
opponent is still waiting for another crop to attack.  Unlike D10, the D11 expert proves those
states have real reachable recovery actions.  The actor has not learned to select them reliably.

## Conclusions at different abstraction levels

### Skill

The missing composition is `detect depleted crop supply -> locate real banana source -> harvest ->
return -> replant`.  Prior curricula trained initial planting and one bounded replant but did not
cover recovery after both carried and home seed inventories are exhausted.

### Representation

No new observation is required.  The fixed actor already receives plant species/fruits, inventory,
carried items, crop existence, distances, turn, and remaining-turn channels.  The failure is policy
coverage and credit assignment over a longer recovery chain.

### Curriculum

D11 validates the layered method: D10 first looked like an environment failure, the cutoff screen
falsified timing, and a stronger reference expert converted the same task into a clean actor test.
Learning should target D11 rather than making the opponent easier.

### Compute

The conditional YT trigger is now met for the first time.  Freeze one clone/PPO protocol, then run
the identical one-million-transition workload locally and on one YT RTX 4090 allocation with cold
startup separated.  Scale multi-million-transition replicas only if end-to-end throughput wins.

### Transfer

This is curriculum evidence, not a submission candidate.  Learned recovery must pass development,
an independent confirmation, compact deployment/parity, layered field evaluation, and finally
controlled Arena transfer before it can affect the resident.

## Next actions

1. Diagnose action disagreement specifically in crop-less/empty-seed states and freeze a
   teacher-anchored behavior-clone gate.
2. Freeze the PPO schedule and exact local/YT one-million-transition benchmark.
3. Train only if the clone does not already pass the D11 actor gate; retain independent seeds for
   confirmation and selection.
4. Keep prospective seeds 2,031,000--2,032,999 unopened until a learned development candidate
   passes every frozen gate.

## Reproducibility anchors

- D11 protocol: `fd91ab60be78fb5253f275be56e4b93a1828081aacf624d4c863f2529a3dda96`;
- readiness document: `62ed4afd59007976f7b780fc532882fa79bde699b430be1eed12df54c615d1ee`;
- fresh teacher: `86c7fc8e7beff228ad117bbb4ab64b704bcc7aeb2aac55a6fa252a79b947514a`;
- fresh random: `d9fe3ff35c6bc2f473b12c820f29d35dbd7f11d171c543eb1f76b1423925e0ca`;
- fixed actor: `c5c846a22d90867ddd29e410df89d3d6301f49a7e270ed79c66557621494e891`;
  and
- accepted checkpoint, unchanged:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
