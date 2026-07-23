# D112a dense q6 counterfactual teacher — frozen protocol

Date: 2026-07-22  
Status: frozen after implementation smoke, before any D112a signal-panel outcome

## Hypothesis and abstraction change

D110 and D111 show that exact one-use linear q6 controllers can be profitable on individual
blocks, but whole-policy terminal selection does not transfer. D111's consecutive shared-parent
fitness correlations are `-0.517`, `-0.679`, `-0.016`, and `+0.537`; final-generation versus
selection correlation is `-0.479`. More terminal population search is therefore unwarranted.

D112 changes credit density. Along each exact D40 trajectory, enumerate every eligible q6
boundary and every deduplicated noncontrol q6 proposal. For one proposal at a time, replay all
earlier boundaries as D40 control, apply the paired proposal, and finish with D40. Work backward
per task with

`V[t] = max(V[t+1], max_a G[t,a], 0)`

where `G[t,a]` is that proposal's terminal margin gain over D40. The proposal target is
`G[t,a] - V[t+1]`; control means wait for the best later one-use opportunity. This is an offline
Monte-Carlo teacher. Runtime search, environment cloning, opponent-family identity as an input,
and more than one intervention are excluded.

## Implementation smoke and isolation

Seed `9,843,000` is consumed only for implementation validation and is excluded from every D112a
signal statistic and future fit. The smoke produced 16 exact baselines, 60 boundaries, and 977
counterfactual arms at 17.17 arms/s with 20 workers. Replays, feature equality, paired gains,
single-intervention counters, and mechanics all passed. Its outcomes set no D112a threshold.

The signal panel is untouched seeds `9,843,100--9,843,107`, both seats and all eight opponents:
128 tasks. Source searches found no earlier artifact using this range. The fixed expert bank is
`d105a-q6-expert-population.tsv`; q6 proposal construction, 64 expert representatives, exact D40
control, 64 state features, and 379 control-relative action features are unchanged from D108.

## Execution

Build `d112_q6_dense_counterfactual_teacher` in release mode. Run the full panel from a new
process with all 20 available CPU workers, then repeat it from another process. Require byte-exact
arm and baseline TSVs before interpreting value. Each task's control trace must exactly reproduce
its separately computed D40 terminal.

The collector must emit one row for every present noncontrol representative at every baseline
boundary. Each row carries only outcome-blind state/action features plus proposal mechanics and
the terminal continuation. No action or boundary may be filtered by its outcome.

## Frozen gates

### Mechanics and coverage

- exactly 128 unique baselines on the prescribed task grid and at least one boundary per task;
- at least 6,000 arm rows, with each boundary containing exactly `proposal_count - 1` unique live
  noncontrol slots and consistent root metadata;
- byte-identical repeated baselines and arm matrices;
- finite 64-value state features, finite nonzero 379-value action differences, and identical root
  state/features when replayed;
- exact `paired_gain = (arm_margin - baseline_margin) / 100` within `1e-6`;
- exactly one intervention, matching noncontrol/joint counters, and zero direct-command,
  provenance, or deposit-prediction failures in every continuation; and
- measured end-to-end throughput at least 12 arms/s on 20 workers.

### Teacher signal

Choose the exact one-use oracle independently per task, including no intervention at gain zero.
Require:

- mean oracle margin gain at least `+20` score points and strict gain on at least 75% of tasks;
- at least seven positive opponent-family oracle means and worst-family mean at least `+8`;
- oracle mean own-score gain nonnegative or mean opponent-score gain nonpositive;
- backward-DP act-now roots between 5% and 90% of all roots;
- strictly positive arm advantages between 1% and 50% of all arms, with at least 40% strictly
  negative, so the fit has both abstention and intervention supervision; and
- target standard deviation at least five score points.

### Oracle safety

Require 100% crop creation for oracle-selected outcomes and worker-three reach within five
percentage points of exact D40. These are feasibility checks on the teacher, not evidence that a
learned scorer will preserve them.

## Decision

- **Mechanics or reproducibility failure:** repair the collector only; do not interpret signal.
- **Signal or oracle-safety failure:** close this one-use dense-teacher formulation without fitting
  a scorer or changing a threshold on these maps.
- **Full pass:** open D112b on entirely new train/validation maps. Fit a small regularized
  deployable scorer to the frozen act-now-versus-wait targets, select hyperparameters without the
  D112a signal panel, and qualify the frozen scorer closed-loop on still-new maps.

D112a cannot create, submit, or install an Arena candidate and authorizes no TestSession, Arena,
submission, or resident mutation.
