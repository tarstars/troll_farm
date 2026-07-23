# Top-policy objective learning — Phase 9 discovery, 2026-07-18

## Verdict

**Reject a pooled top-five imitation policy.  Retain Escdemon as the first coherent complete-policy
target; do not build candidate code yet.**

The state-only objective layer generalizes across held games but not across held agents because
the top five represent different architectures.  Agent-specific validation identifies two
coherent targets, with rank-3 Escdemon substantially stronger and simpler to learn than the
pooled policy.

This is observational replay analysis on already-consumed data.  No prospective map block, live
source, submit helper, or arena state was changed.

## Dataset and labels

All 129 official games containing a current top-five agent decode cleanly: replay and command
turn counts match in 129/129 and there are zero unknown diff updates.  The resulting dataset has
91,427 per-worker turns.  Features use only current state and map information—turn phase, worker
ordinal/stats, cargo/fullness, bank distance, current cell type, workforce size, bank-score band,
resource distances, and cheap-train affordability.  Agent identity and outcome are excluded.

Commands are reduced to 18 high-level objectives.  The largest are `MOVE_OTHER` (21,760), CHOP
(18,983), `MOVE_TREE_RIPE` (13,202), `MOVE_TREE` (10,022), DROP (9,099), and HARVEST (8,125).
PICK and PLANT retain their resource kind.  This layer deliberately does not yet predict exact
target coordinates, multi-worker assignment, or TRAIN timing/spec.

## Shared-policy gate

A compact hierarchical frequency lookup was trained with five state-feature backoff levels.
Every held row is predicted by a model that excludes its game or agent.

| Validation | Accuracy | Macro F1 | Gain over fold-majority | Worst fold accuracy |
|---|---:|---:|---:|---:|
| 5-fold held game | 59.886% | 0.347 | +36.086 pp | 58.263% |
| leave one agent out | 51.567% | 0.252 | +27.766 pp | 39.132% |

The predeclared shared gate required 60% held-game accuracy, 0.35 macro F1, and at least 45%
accuracy for every held agent.  It fails all three narrowly or materially.  Common mechanics are
learnable—held-game recall is 92.0% DROP, 80.3% CHOP, 76.2% HARVEST—but rare seed-kind choices and
tree target classes remain weak.

The worst held agent is Escdemon.  That is not random noise: every one of the dataset's 2,387
`MOVE_BANK` labels belongs to Escdemon, while the other architectures encode banking movement
differently.  Pooling policies erases exactly the distinctive behavior we want to learn.

## Coherent architecture gates

Each agent was then trained and tested only on its own held games.  This is a target-selection
diagnostic, not a claim that its observed policy is causally better.

| Agent | Rank | Games | Accuracy | Macro F1 | Worst fold | Gate |
|---|---:|---:|---:|---:|---:|---|
| delineate | 1 | 26 | 60.413% | 0.329 | 59.322% | fail macro F1 |
| wala | 2 | 29 | 55.973% | 0.382 | 54.006% | fail accuracy |
| Escdemon | 3 | 26 | **77.682%** | **0.541** | **74.760%** | **pass** |
| norxondor_gorgonax | 4 | 30 | 66.695% | 0.360 | 64.991% | pass |
| laconic_pixel | 5 | 18 | 60.098% | 0.310 | 55.677% | fail macro F1 |

Escdemon is the strongest first target because its objective policy is markedly repeatable, it
uses a compact two-worker architecture close to the resident's resource envelope, and it avoids
the failed multi-worker transplant.  Norxondor remains the second target if a compact clone
cannot improve locally.

## Opening alignment with the resident

Escdemon always trains exactly one worker.  In all 26 games its selected worker is the
maximum-affordable movement/carry/chop vector at the actual train turn with harvest forced to
zero.  It trains on the first turn that its chosen spec is affordable in 25/26 games.

The resident's existing turn-one `TUNED_CARRY` planner already predicts the exact eventual
Escdemon spec in 14/26 initial states; mean talent L1 error is only 0.538 and maximum is 2.  This
is important: worker-stat enumeration is not the missing architecture.  The rejected rollout
option bought the current maximum on turn one, while Escdemon couples a later chosen-spec trigger
to a compact, highly predictable tree-conversion and banking policy.

The next implementation must therefore focus on the complete objective/target continuation and
training trigger.  Replacing the resident's planned spec with another max-bank formula would
repeat a closed experiment.

## Next gate

Before writing a standalone candidate:

1. add exact target-coordinate and multi-worker assignment labels for Escdemon;
2. infer its chosen-spec trigger with held-game validation, keeping max-affordable harvest-0 as
   the observed spec rule;
3. measure full command agreement on held games, not just objective labels;
4. implement a research policy only if command/objective coverage remains stable;
5. compare the complete policy with exact resident on reused discovery maps and diverse
   continuations before freezing any prospective protocol.

No arena action is implied.  GoldElite is not an acceptable shortcut: its arena opening agreement
is sparse and its continuation already caused the rejected rollout bias.

## Evidence

- `top-policy-objective-study-2026-07-18.json`
- `escdemon-resident-opening-alignment-2026-07-18.json`
- `escdemon-initial-26.maps`
- `escdemon-resident-opening-plans.tsv`
- `cgauto/top_policy_objective_study.py`
- `cgauto/agent_opening_plan_audit.py`
- `cgauto/make_agent_initial_dataset.py`
- `yamo_option_rollout_time opening-plan-grid`
