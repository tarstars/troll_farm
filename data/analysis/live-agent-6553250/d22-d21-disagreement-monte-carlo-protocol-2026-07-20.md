# D22 D21-disagreement Monte Carlo — frozen diagnostic protocol (2026-07-20)

## Question

Why did the technically stable D21 PPO policy lose `-2.685` paired terminal margin?

D22 distinguishes two explanations without training another policy:

1. **direct proposal harm:** D21's changed actions are already worse when applied once from a
   shared D11 state and followed by the exact D11 continuation; or
2. **compounding/distribution failure:** individual D21 changes are locally useful, but applying
   the replacement policy repeatedly moves it into damaging state distributions.

A third possible outcome is a mixed distribution with a sparse, opponent-spanning positive tail.
That may justify a separately frozen confidence-gated residual study, but not a candidate.

## Fixed policies and environment

- Baseline and continuation: accepted D11 checkpoint
  `curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt`, SHA-256
  `44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`.
- Proposal policy: rejected D21 final checkpoint
  `d21-competitive-ppo-pilot-seed2107-final.pt`, SHA-256
  `d51dd99260aa33b447c1371a8f1857a0771f7421c9b90a13322d9bf01f78c8cb`.
- Reuse the accepted D21 Level-6 environment exactly: six independently hashed opponents, eight
  worker recipes, two controlled workers, legal action mask, and exact turn-300 termination.
- Use new discovery-only seeds `[8,300,000, 8,300,240)`.  They are not validation, a holdout, or
  an Arena proxy.

## Shared-state disagreement selection

Run deterministic D11 from every seed.  Before every decision, evaluate both frozen actors on
the identical D11 state.  A candidate exists only when both masked actions are legal and differ.

Partition the exact referee turn into four preregistered bands:

1. `[0, 75)`;
2. `[75, 150)`;
3. `[150, 225)`; and
4. `[225, 300)`.

For each seed and band, select at most one disagreement using the smallest deterministic SplitMix
priority derived from `(seed, decision index, band)`.  Selection must not inspect the terminal
result, action verb, opponent, recipe, or advantage.  This yields at most 960 interventions and
prevents dense-disagreement seeds from dominating.

Record the exact turn, sequential worker phase, D11 action/plane, D21 action/plane, opponent, and
recipe.  Add read-only exact-turn telemetry if needed; no environment dynamics or actor inputs may
change.

## Counterfactual replay

For every selected event:

1. reconstruct the same seed;
2. follow deterministic D11 byte-for-byte until the selected decision;
3. execute the single stored D21 action once;
4. immediately return to deterministic D11 for every later decision; and
5. continue to exact turn 300.

Pair that terminal margin with the unchanged all-D11 terminal from the same seed.  Opponent logic
remains state-reactive, so the result measures the complete causal consequence of the one action,
not a fixed opponent score.  Never use D21 again after the intervention.

Repeat the all-D11 baseline once and require identical episode rows.  Reject any replay where the
stored action is no longer legal, the pre-intervention state is not identical, the episode does
not end at turn 300, or return identity exceeds `1e-4` margin points.

## Frozen readiness gates

The diagnostic is valid only if all of the following hold:

1. both all-D11 runs cover all 240 seeds, end at turn 300, select no illegal action, and have
   identical terminal rows;
2. D21 selects no illegal action on any inspected shared state;
3. at least 480 interventions are selected in total and at least 80 occur in every turn band;
4. every opponent has at least 40 interventions and every recipe at least 25; and
5. every counterfactual replay is legal, finite, reaches turn 300, and preserves reward identity.

Failure is an instrumentation/coverage result and authorizes no policy conclusion.

## Frozen classifications

For each intervention define `advantage = one-D21-action terminal margin - all-D11 margin`.

- **Compounding/distribution failure:** readiness passes, overall mean advantage is positive,
  at least four of six opponent means are nonnegative, positive-advantage rate is at least 30%,
  and new-catastrophe rate is at most 1%.
- **Direct proposal harm:** readiness passes, overall mean advantage is nonpositive and fewer than
  20% of interventions gain at least +10 margin.
- **Mixed sparse opportunity:** readiness passes, the compounding gate fails, but at least 20% of
  interventions gain at least +10, those gains appear in at least five opponents and six recipes,
  and new-catastrophe rate is at most 2%.
- **Mixed unsafe:** readiness passes and none of the above conjunctions holds.

Also report mean, median, quantiles, worst decile, new catastrophes, and results by turn band,
opponent, recipe, and action-plane transition.  These labels are diagnostic.  Even a sparse
opportunity authorizes only a new distillation/readiness protocol on a disjoint block.

## Compute and project rule

Run locally and vectorize the four intervention arms across seeds.  This is a bounded exact-engine
diagnostic; YT is unnecessary and remains ineligible for this workflow without a new parity gate.
Do not modify the stable resident, submission default, sealed field data, or Arena state.
