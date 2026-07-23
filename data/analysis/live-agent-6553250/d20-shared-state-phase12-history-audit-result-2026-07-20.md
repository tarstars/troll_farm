# D20 shared-state Phase-12 history audit — result (2026-07-20)

## Decision

**Do not repeat the proposed large-data shared-state selector.  Phase 12 was already executed and
closed on 1,280 exact two-branch cells at each of turns 3, 5, and 10.**

The historical turn-10 learner reached the blocked-seed safety target, but failed when an entire
opponent family was held out.  More rows with the same trajectory representation are therefore
ineligible.  The stable resident, candidate, sealed blocks, submission, and Arena state remain
unchanged.

## What was actually completed

The Rust `labels` exporter already implemented the Phase-12 plan: it forked only the real resident
and worker-three continuations, recorded directly observable state snapshots and trajectory
deltas, and omitted embedded-model mismatch features.  Eighty maps, both seats, and eight actual
opponents produced 1,280 cells per decision turn.

| Decision | Observable trajectory features | Best blocked-seed precision | Selection | Mean margin / score gain | Held-opponent-family precision | Verdict |
|---:|---:|---:|---:|---:|---:|---|
| turn 3 | 378 | 79.22% | 154 / 1,280 | +5.702 / +5.595 | 70.04% | reject |
| turn 5 | 630 | 82.57% | 109 / 1,280 | +4.571 / +4.209 | 73.11% | reject |
| turn 10 | 1,260 | **91.43%** | 70 / 1,280 | +3.948 / +2.937 | **73.08%** | reject |

The positive-cell oracle remained large (roughly +19 to +23 mean margin across the three
prefixes), so the macro branch has real value.  The failure is transfer: within-known-opponent
history becomes predictive by turn 10, but the boundary does not generalize to an unseen policy.
This is the same abstraction-level lesson as D19, not an invitation to enlarge the forest.

## Consequence

The next experiment must optimize behavior closed-loop instead of imitating hindsight terminal
labels.  The accepted D11 spatial actor already has a compact, parity-qualified live inference
path and learned renewable-economy mechanics.  Its remaining defect is strategic: fixed recipes
and curriculum reward do not optimize complete game margin.  The next branch therefore adds a
full-length competitive environment with a mixed strategic opponent curriculum and telescoping
score-margin reward, then measures the unchanged D11 actor before authorizing any bounded PPO
pilot.

This is materially different from the closed branches:

- it does not predict a one-step counterfactual advantage;
- it does not classify a terminal worker-three label;
- it does not switch between paths after they have already diverged; and
- it evaluates the actor's own closed-loop trajectory for the full game.

## Evidence

- `norxondor-value-labels-discovery-322-401.tsv`;
- `norxondor-value-labels-turn5-discovery-322-401.tsv`;
- `norxondor-value-labels-turn10-discovery-322-401.tsv`;
- `norxondor-value-model-expanded-discovery-322-401-2026-07-18.json`;
- `norxondor-value-model-turn5-expanded-discovery-322-401-2026-07-18.json`;
- `norxondor-value-model-turn10-expanded-discovery-322-401-2026-07-18.json`;
- `norxondor-offline-distillation-and-native-controller-2026-07-18.md`.
