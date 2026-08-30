# ppo-h gamma/lambda validity audit

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed code: `main@5b0de4eeeb7ed1d23f1f60a1008c9172941209dd`

## Verdict

`ppo-h` is a valid **gamma-only sensitivity run**, but it is **not a test of undiscounted long-horizon credit** while `gae_lambda` remains at its default `0.95`.

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
```

The recent remedy runs used gamma `0.999`; `ppo-h` changes gamma to `1.0` while the board calls it the next test of long-horizon credit. The implementation also normalizes advantages separately in every minibatch before the PPO policy loss.

## Quantitative consequence

With lambda fixed at `0.95`, the across-turn GAE trace factor changes only from:

```text
0.999 * 0.95 = 0.94905
```

to:

```text
1.0 * 0.95 = 0.95
```

A terminal signal's direct trace coefficient is therefore:

| turn boundaries back | gamma=.999, lambda=.95 | gamma=1, lambda=.95 | relative increase |
|---:|---:|---:|---:|
| 10 | 0.59278 | 0.59874 | 1.0% |
| 25 | 0.27054 | 0.27739 | 2.5% |
| 50 | 0.07319 | 0.07694 | 5.1% |
| 100 | 0.00536 | 0.00592 | 10.5% |
| 200 | 0.0000287 | 0.0000351 | 22.2% |

Both estimators still suppress a terminal reward very strongly at ordinary game distances. Per-minibatch advantage normalization removes much of a pure scale change as well. `gamma=1` does alter the Bellman delta and can produce a real difference, but it does not remove the dominant lambda trace decay.

## What the result can establish

A positive or negative `ppo-h` result can establish sensitivity to the small `gamma=.999 -> 1.0` change under `lambda=.95`.

It cannot by itself establish:

- that undiscounted terminal credit cures or fails to cure policy erosion;
- that the final score reached early fruit-chain decisions without substantial decay;
- that the remaining problem is or is not long-horizon credit assignment.

## Cheapest next diagnostic

Before launching another long run, use one already-saved rollout and recompute advantages without touching the environment or policy under three estimators:

```text
A: gamma=.999, lambda=.95   # prior remedy
B: gamma=1.0,  lambda=.95   # ppo-h
C: gamma=1.0,  lambda=1.0   # undiscounted Monte-Carlo-like trace
```

Apply the trainer's actual minibatch normalization, then report:

1. correlation and cosine similarity of normalized A versus B, and A versus C;
2. fraction of rows whose advantage sign changes;
3. results split by distance in turns from terminal reward;
4. PLAN rows versus TROLL rows;
5. fruit-chain actions (`PICK`, `PLANT`, `HARVEST`, `DROP`) versus all others.

If A and B are nearly identical while C differs materially, `ppo-h` was not the experiment its owner-facing label suggests. A matched-seed `gamma=1, lambda=1` run can then test the long-horizon hypothesis, with its expected higher variance named in advance. An explicit terminal-return auxiliary target is another possible follow-up, but it is a new design rather than a one-variable confirmation.

## Recommendation

```text
KEEP ppo-h running if already started.
RELABEL it gamma-only sensitivity, not undiscounted credit.
RUN the offline three-estimator advantage diagnostic before interpreting or extending it.
```

No training process, checkpoint, dataset, environment, YT operation, platform submission, or Arena state was changed by this audit.
