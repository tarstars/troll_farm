# ppo-h gamma/lambda and rollout-horizon validity audit

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed code: `main@e02e88c8afadc31dc16109ed85eb3c547913943e`
Revision: r2 — corrects the earlier suggestion that gamma=1, lambda=1 alone would test full-game credit

## Verdict

`ppo-h` is a valid **gamma-only sensitivity run**, but it is **not a test of undiscounted long-horizon credit** for two independent reasons:

1. `gae_lambda` remains at its default `0.95`;
2. each rollout stores only `32` mini-steps per environment, so terminal reward can propagate directly through only a small fragment of a 300-turn game. Earlier decisions depend on the critic bootstrap.

Do not cancel a run already in flight. Keep its checkpoint and evidence. The correction is to the interpretation and to the next diagnostic.

## Load-bearing code

`local_claude_1/nn-bot/train_ppo_full.py::compute_gae` uses, at every turn boundary:

```python
delta_discount = gamma
trace_factor = gamma * gae_lambda
```

The parser defaults are:

```text
gamma = 0.997
gae_lambda = 0.95
rollout_steps = 128  # parser default
```

The actual Phase-3 recipes on the card and YT launcher use `rollout_steps = 32`. A rollout step is one PLAN or TROLL network decision, not one game turn.

The recent remedy runs used gamma `0.999`; `ppo-h` changes gamma to `1.0`. The implementation also normalizes advantages separately in every minibatch before the PPO policy loss.

## Lambda consequence

With lambda fixed at `0.95`, the across-turn GAE trace factor changes only from:

```text
0.999 * 0.95 = 0.94905
```

to:

```text
1.0 * 0.95 = 0.95000
```

A terminal signal's coefficient, if it were in the same rollout, would be:

| turn boundaries back | gamma=.999, lambda=.95 | gamma=1, lambda=.95 | relative increase |
|---:|---:|---:|---:|
| 10 | 0.59278 | 0.59874 | 1.0% |
| 25 | 0.27054 | 0.27739 | 2.5% |
| 50 | 0.07319 | 0.07694 | 5.1% |
| 100 | 0.00536 | 0.00592 | 10.5% |
| 200 | 0.0000287 | 0.0000351 | 22.2% |

Both estimators suppress a distant terminal reward strongly. Per-minibatch advantage normalization removes much of a pure scale change as well.

## The stricter limit: a 32-mini-step buffer

One game turn contains:

```text
1 PLAN decision + one TROLL decision per own troll
```

So a 32-step rollout spans at most approximately:

| own trolls | mini-steps per turn | real turns in one rollout |
|---:|---:|---:|
| 1 | 2 | 16.0 |
| 2 | 3 | 10.7 |
| 3 | 4 | 8.0 |
| 4 | 5 | 6.4 |
| 5 | 6 | 5.3 |

Only decisions inside the same buffer as a terminal transition receive the terminal score directly through GAE. All earlier decisions see it only through `next_value`, the critic prediction at the buffer boundary.

Training for more total updates does not lengthen this direct credit horizon. Setting gamma and lambda to one would remove decay **inside the same 32-step buffer**, but would still not create a turn-300-to-turn-50 Monte Carlo return. The previous r1 suggestion that a matched-seed `(gamma=1, lambda=1)` run alone would test the full long-horizon hypothesis was therefore too strong and is withdrawn.

## Why the current explained variance is not a full-game value certificate

The logged explained variance compares rollout-start values to TD(lambda) targets that themselves contain bootstrapped value predictions. It is a useful training diagnostic, but it does not establish accuracy against the realised full-episode end margin.

This matters especially during critic warm-up:

- the actor is frozen;
- the value head is trained on short bootstrapped rollouts;
- most buffers contain no terminal transition;
- the target beyond roughly 5–16 turns is supplied by the same critic being fitted.

A high rollout explained variance can coexist with poor prediction of the final 300-turn result. Conversely gamma=1 can lower that metric simply by making the bootstrapped target harder, without testing whether terminal credit would improve the policy if it were available.

## What ppo-h can establish

A positive or negative `ppo-h` result can establish sensitivity to the small `gamma=.999 -> 1.0` change under:

```text
lambda = .95
rollout_steps = 32 mini-steps
current critic bootstrap
```

It cannot establish:

- that undiscounted terminal credit cures or fails to cure policy erosion;
- that final score reaches early fruit-chain decisions directly;
- that long-horizon credit is acquitted;
- that an episode-cap curriculum is the only remaining lever.

## Cheapest decisive diagnostics

### 1. Within-buffer estimator comparison

On one saved rollout, recompute advantages under:

```text
A: gamma=.999, lambda=.95
B: gamma=1.0,  lambda=.95
C: gamma=1.0,  lambda=1.0
```

Apply the actual minibatch normalization and report correlations, sign changes, PLAN/TROLL split and fruit-chain rows. This establishes how little A and B differ locally. It does **not** test full-game credit.

### 2. Full-episode critic audit

Using complete, fixed-policy clone episodes already available from the bench or freshly generated without policy updates:

1. compute realised undiscounted return-to-go at every mini-step from the true terminal margin and any retained shaping;
2. run the clone critic, critic-warm-up checkpoint and selected PPO checkpoints on those exact observations;
3. compare prediction bias, RMSE and explained variance against realised full-episode returns;
4. split by turns-to-terminal, PLAN/TROLL phase and fruit-chain action;
5. separately compare the current 32-step TD(lambda) target to the realised return.

This tells whether the critic actually transports terminal information across buffer boundaries.

### 3. Direct-credit census

For ordinary training buffers, report:

- fraction containing a terminal transition;
- fraction of rows with an actual terminal reward in their backward GAE suffix;
- maximum and median real-turn distance from those rows to terminal;
- fraction whose target is purely bootstrap beyond the local rewards.

## Options if full-episode value prediction is poor

These are different experiments and should not be bundled:

- pretrain the value head on complete fixed-policy episodes and realised return-to-go;
- use episode-aligned or substantially longer rollouts for a bounded matched-seed test, with memory cost stated;
- add an explicit terminal-return auxiliary target;
- adopt the source-backed assigned-target/reward-shaping curriculum described in the separate curriculum audit.

A gamma=1, lambda=1 run is useful only after its limited within-buffer meaning is made explicit, or after the rollout/target design is changed so terminal returns actually reach the decisions under study.

## Recommendation

```text
KEEP ppo-h evidence, but label it gamma-only under a 32-step bootstrapped estimator.
RETRACT “discount fully swept/acquitted.”
RUN the within-buffer comparison and full-episode critic audit before another explanatory long run.
DO NOT treat gamma=1, lambda=1 alone as a full-game credit test.
```

No training process, checkpoint, dataset, environment, YT operation, platform submission, or Arena state was changed by this audit.
