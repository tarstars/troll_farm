# D41c exact-prior residual PPO — result (2026-07-21)

## Verdict

**FAIL and close this temperature-4/teacher-auxiliary PPO recipe.** The run is mechanically clean,
but the final deterministic checkpoint makes zero deviations from D40 on all 85,128 development
decisions. It therefore has exactly D40's scores and fails the required improvement, opponent-family,
nonzero-disagreement, and conditional-repeat gates.

This is an under-learning result, not policy collapse. Preserve D41b's exact-prior representation;
do not promote the checkpoint, lower the prior temperature by inspection, rerun seed 411, or open
confirmation/Arena.

The authoritative result is `d41c-residual-ppo-seed411-result.json`, SHA-256
`d9e86a7d322c47fe9929e86e958f2bf37acba321bc2e831f2b6c5baff661e1d9`.

## Frozen execution

- exactly 1,048,576 transitions, 256 updates, and model seed 411;
- 6,303 complete training episodes with maximum reward-identity error `1.041e-5` margin points;
- 1,036,537 rank-zero, 11,816 rank-one, 222 rank-two, and one rank-three sampled actions;
- 1.1481% sampled disagreement, zero illegal actions, and zero terminal integrity failures;
- 1,745.80 seconds wall, 28,756.90 CPU seconds, **16.47 effective CPU cores**, and 600.63
  end-to-end transitions/s including four optimization epochs;
- 737 trainable actor parameters and an 8,897-parameter training-only critic; and
- final checkpoint SHA-256
  `1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a`.

The actor did move: L2 drift is 0.4693 against a 5.6569 initial norm. PPO KL remained near
`1e-9--1e-8`, clipping stayed zero, and deterministic teacher accuracy stayed 100% throughout.
Thus finite optimization occurred, but not at the scale needed to overcome the frozen prior.

## Development gate

| Metric | D40 | D41c | Required | Verdict |
|---|---:|---:|---:|---|
| Mean margin | +41.082 | +41.082 | D40 +5 | fail |
| Mean own score | 218.311 | 218.311 | at least D40 -5 | pass |
| Worker two | 99.61% | 99.61% | >=95% | pass |
| Worker three | 92.38% | 92.38% | >=88% | pass |
| Crops | 100% | 100% | >=97% | pass |
| D40 disagreement | — | **0/85,128** | `(0, 15%]` | fail |

All eight opponent-family deltas are exactly zero, so the five-family improvement gate fails while
the -15 worst-regression gate passes. Margin remains +167.217 above random and all integrity gates
pass. Because the non-repeat gates failed, the protocol correctly skipped the conditional repeat;
`repeat_exact=false` records “not run,” not nondeterminism.

## Residual-scale diagnosis

The post-result diagnostic replays the frozen development trajectory and compares residual logits
without changing actions. Of 85,128 decisions, 52,801 have a rank-one alternative and 32,327 are
singletons.

- Rank-one residual advantage has mean `-0.00068`, median approximately zero, p99 `+0.2803`, and
  maximum only **+0.3323**.
- Changing argmax requires overcoming the temperature-4 rank gap. The closest state is still
  **3.6677 logits** short; median shortfall is 4.0000.
- The residual prefers rank one over rank zero before adding the prior in 47.83% of actionable
  states, so it learned relative structure, but at roughly one-twelfth the minimum required scale.
- Every best alternative remains prior rank one. No hidden rank-two proposal is close to activation.

The diagnostic artifact is `d41c-residual-gap-diagnostic-2026-07-21.json`, SHA-256
`b1add08420f61286c08b09ab035d558d919b098acec150d18aa2385c64cffa26`.

## Multilevel conclusion

- **Environment/compute:** pass. Parallel rollout, rank ABI, rewards, legality, and CPU utilization
  are all adequate for million-transition experiments.
- **Representation:** pass as a safe anchor. D40 remains exact and the residual learns measurable
  relative preferences.
- **Optimization recipe:** fail. Temperature 4 plus teacher cross-entropy creates a cumulative
  trust region much stronger than PPO's observed reward gradients; more transitions under the same
  decaying schedule have low expected value.
- **Strategy:** unresolved. Zero deterministic deviations mean D41c does not tell us whether its
  strongest rank-one preferences are good single actions whose effect was suppressed, or merely
  harmless logit noise.

## Next experiment

Run the preregistered exact one-deviation continuation audit on fresh maps. At D40 states, compare
one rank-one action followed by exact D40 against uninterrupted D40. Contrast states with the
largest positive D41c residual gap against deterministic hash controls, stratified by opponent,
branch, and phase. This directly estimates action value before changing temperature or launching
another learner.
