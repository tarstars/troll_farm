# D15 resident residual PPO signal — development result (2026-07-20)

## Decision

**No useful deterministic PPO signal.  All four runs collapse to exact `KEEP`; do not scale,
promote, integrate, or construct a candidate from D15.**

The environment remains qualified.  The failed component is the on-policy learning objective:
rare beneficial exceptions, if they exist, are overwhelmed by the much larger cost of random
local interventions.

## Complete execution

All four frozen jobs completed 131,072 transitions and all 240 deterministic paired evaluation
scenarios.  The four jobs ran concurrently and consumed 524,288 aggregate training decisions.

| Run | Bias | Final exploratory margin | Final exploratory overrides/game | Entropy | Deterministic overrides | Paired delta |
|---|---:|---:|---:|---:|---:|---:|
| `b05-s9101` | 0.5 | -13.13 | 45.92 | 0.107 | **0 / 240** | 0.00 |
| `b05-s9102` | 0.5 | -31.61 | 60.35 | 0.360 | **0 / 240** | 0.00 |
| `b15-s9201` | 1.5 | -11.06 | 36.78 | 0.123 | **0 / 240** | 0.00 |
| `b15-s9202` | 1.5 | -6.54 | 35.90 | 0.080 | **0 / 240** | 0.00 |

Every deterministic evaluation is byte-for-byte behaviorally equivalent to all-`KEEP`: mean
margin +59.26, wood edge +20.35, zero changed outcomes, and zero overrides.  Consequently every
run fails the activation and changed-outcome gates and is classified `collapse_to_keep`.

## What was learned

PPO did learn the dominant fact in the environment: most unconstrained local overrides are bad.
During training, the safer runs reduced stochastic interventions from roughly 70--76 per game to
about 36--37 and improved exploratory margins from roughly -58/-40 to -11/-7.  The broader runs
also became safer but remained noisier.  Critics reached high within-rollout explained variance.

That is genuine optimization, but it is not the capability we need.  The deterministic actor
implements the safe prior everywhere rather than identifying positive exceptions.  More
transitions under the same on-policy distribution would mainly sharpen this universal `KEEP`
solution; changing initialization bias from 0.5 to 1.5 did not change the terminal mode.

## Next hypothesis: counterfactual advantage teacher

The exact environment now makes a better learning signal possible.  At a resident decision with
one or more legal alternatives:

1. clone the full game, resident state, opponent state, command history, and decision phase;
2. branch once with `KEEP` and once with one local alternative;
3. after that single intervention, use `KEEP` for both branches to terminal;
4. label the state/action by exact terminal margin and wood-edge advantage;
5. oversample positive and high-cost negative examples when fitting a compact residual scorer.

This is offline Monte Carlo continuation, not runtime search.  It avoids the prior 200+ ms live
rollout cost: deployment evaluates only the distilled compact model.  It also avoids D15's class
imbalance because alternatives receive explicit paired advantages instead of being discovered
through rare stochastic trajectories.

First run a bounded teacher-density audit.  If positive one-intervention advantages are too rare,
map-specific, or opponent-specific, stop local residual learning.  If they are distributed,
freeze train/validation map blocks and distill them before any policy rollout test.

## Evidence

- protocol: `d15-resident-residual-ppo-signal-protocol-2026-07-20.md`;
- paired analysis SHA-256:
  `356d878f0ffefd97c2a7e5322f396a4290bc364e3618d0202d688f593a82e57b`;
- trainer SHA-256:
  `d8d419be6e98aa9d320fcf8a41707ab2d5fd9945c58dae424f09c79ebbd9ca32`;
- analyzer SHA-256:
  `afd8f0a6162a00bd50a22260d177c2e1a31dfc37ba6fe8396feed5fc1a0a3cda`;
- evaluation KEEP baseline SHA-256:
  `15ac9c333a9ce674e0678e604311d3a6ca06536f324e064c01fca6afc8f03822`;
- checkpoint SHA-256 values:
  - `b05-s9101`: `f0a7968ea6b3ed6afe58c45dc583cb48ccf474997a7bc8ed605c91fc6871e2e8`;
  - `b05-s9102`: `9820976a2f8332778923a5c574fc4ee8d1107def15027348ddb2cfd159ecf6e7`;
  - `b15-s9201`: `02a8028b757ff0608ede4ae91ab21e3a549a08d785aae502a256ab34615da90d`;
  - `b15-s9202`: `51422a7439823e47d11493fe7d7b1a7eaea720e84101da37e7d6e97effe0fc54`.
