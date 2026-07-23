# D15 resident residual PPO signal — development protocol (2026-07-20)

## Hypothesis

A compact PPO policy trained on exact resident states, explicit joint intent, and full-game
margin reward can learn a sparse set of safe local overrides.  The D11 actor failed because it
was trained on a different state distribution and then substituted at inference time; D15 trains
the residual decision directly in the deployed control context.

## Frozen environment and model

- D14 exact resident residual environment, Stage-A `KEEP + local action` mask.
- Scenario stream begins at 120,000 (map 10,000); all runs see the same stream.
- Deterministic evaluation scenarios 240,000--240,239 (maps 20,000--20,019), both seats and all
  six opponents.
- Width-8, two-block convolutional actor/critic; 137 input channels, 13-plane spatial actor.
- Plane-0 bias makes deterministic initialization choose `KEEP`.
- Per-turn margin-change reward divided by 100; gamma 0.999, GAE lambda 0.98.
- 32 environments, 64 rollout decisions, 131,072 transitions per run, three PPO epochs,
  minibatch 512, learning rate 2.5e-4, entropy coefficient 0.002.

## Frozen exploration comparison

Run four independent jobs in parallel:

| Run | Model seed | Initial `KEEP` bias |
|---|---:|---:|
| `b05-s9101` | 9101 | 0.5 |
| `b05-s9102` | 9102 | 0.5 |
| `b15-s9201` | 9201 | 1.5 |
| `b15-s9202` | 9202 | 1.5 |

Bias 0.5 tests broader but still resident-centered exploration; bias 1.5 tests a safer
distribution.  No run-specific tuning is allowed.

## Analysis

Pair each deterministic learned evaluation with all-`KEEP` in the same scenario.  Report map-
balanced margin and wood deltas, opponent means, worst opponent, changed cells/maps, override
episode and decision counts, worst-decile cell delta, and catastrophic margins at or below -100.

This is a learning-signal test, not a promotion test.  A run demonstrates useful signal only if:

1. it completes the training and all 240 deterministic evaluation scenarios;
2. deterministic overrides occur in at least 5% of episodes and change at least 12/240 terminal
   margins;
3. map-balanced mean margin delta versus `KEEP` is nonnegative;
4. worst opponent mean delta is at least -5;
5. worst-decile cell delta is at least -20;
6. catastrophic-loss count does not increase by more than two.

Select all signal-positive runs for a larger replicated cycle.  If none passes, use the logs to
distinguish three outcomes: collapse to `KEEP`, unsafe widespread intervention, or learned but
unprofitable sparse intervention.  Do not relax the gate or construct a candidate.

## Outputs

- one checkpoint and training/evaluation JSON per run under the D15 prefix;
- `d15-resident-residual-ppo-signal-analysis-2026-07-20.json`;
- `d15-resident-residual-ppo-signal-result-2026-07-20.md`.
