# D16 resident residual Monte Carlo teacher density — development protocol (2026-07-20)

## Hypothesis

On-policy PPO collapses to `KEEP` because harmful interventions dominate exploration.  Exact
one-intervention continuation can expose rare positive exceptions directly: clone a real
resident decision, apply one legal local alternative, then return control permanently to the
resident and compare terminal outcome with the all-`KEEP` continuation.

This is an offline teacher-density audit.  It does not put Monte Carlo search in the submission
and cannot select or promote a policy.

## Frozen block and sampling

- Scenario IDs 360,000--360,239: maps 30,000--30,019, both seats, all six opponents.
- Traverse the all-`KEEP` resident trajectory in every scenario.
- Treat every legal non-`KEEP` state/action pair as a sampling candidate.
- Use deterministic uniform reservoir sampling with ten candidates per scenario.
- Total labels: 240 × 10 = 2,400.
- For each sampled event:
  1. retain an exact clone of game, resident, opponent, history, joint command, and decision phase;
  2. execute the sampled local action once;
  3. use `KEEP` for every later unit decision;
  4. compare terminal margin, wood edge, turn, and worker counts with the scenario's resident
     terminal outcome.
- Re-run the first sampled clone with pure `KEEP` in every scenario and require exact equality to
  the main resident trajectory; this validates clone fidelity.
- Execute scenarios with 20 independent worker threads.

## Report

Report terminal margin and wood advantages overall and by map, opponent, seat, active role,
resident verb, alternative verb/action plane, turn quartile, and worker specification.  Include
positive/tie/negative counts, positive concentration, catastrophic changes, and continuation
latency.

## Frozen density gate

Counterfactual distillation is worth a larger dataset only if all conditions hold:

1. 2,400/2,400 labels complete and clone fidelity passes in 240/240 scenarios;
2. at least 2% (48) labels have positive terminal margin advantage;
3. at least 24 labels improve margin by +2 or more;
4. positive labels occur on at least 8/20 maps, against at least 4/6 opponents, and in both
   starter and second-worker roles;
5. at least two alternative action planes have positive labels;
6. no single map contributes more than 30% of all positive labels.

The gate intentionally concerns label density and distribution, not average policy strength.
Passing authorizes a larger frozen train/validation label corpus and supervised distillation.
Failure closes Stage-A local residual learning; do not tune the sampling block or return to the
same PPO formulation.

## Outputs

- rows: `d16-resident-residual-mc-teacher-density-scenarios360000-360239.tsv`;
- analysis: `d16-resident-residual-mc-teacher-density-2026-07-20.json`;
- result: `d16-resident-residual-mc-teacher-density-result-2026-07-20.md`.
