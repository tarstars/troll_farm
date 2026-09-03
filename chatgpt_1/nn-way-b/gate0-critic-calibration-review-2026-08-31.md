# Gate 0 review: independent critic calibration

Date: 2026-08-31
Agent: `chatgpt_1`
Task: `20260829-nn-bot-way-b`
Reviewed delivery: `agent/claude_1@44e873ad897b61a641c629bd4e69c74e157c676a`
Reviewed files:

- `local_claude_1/nn-bot/critic_calibration.py`
- `tests/test_critic_calibration.py`
- `claude_1/results/nn-bot-way-b-critic-calibration/RUNBOOK.md`

Verdict: **the complete-episode collector is valuable, but four interpretation/population repairs are required before these runs can close Gate 0.** The current host runs may finish and may be retained as exploratory evidence. Do not use their cross-checkpoint comparison as a gate verdict yet.

## What is correct and useful

The script correctly:

- uses the trainer's actual environment, observation, masking and decoding paths;
- plays episodes to a real terminal state;
- computes a Monte Carlo return-to-go with no critic bootstrap;
- applies discount only when a game turn executes, never between mini-steps of one turn;
- keeps the measured network and checkpoint immutable;
- records calibration by turn band, board size, seat and row class;
- reports bias, RMSE and MAE separately from ranking and scale statistics.

The return-to-go recurrence itself is sound.

## Blocker 1: explained variance does not punish constant bias

The implementation uses:

```python
1 - Var(realized - predicted) / Var(realized)
```

That statistic is invariant to a constant offset. If:

```text
predicted = realized + 10
```

then `realized - predicted` is the constant `-10`, its variance is zero, and explained variance is **1.0**, despite a ten-unit bias and large RMSE.

Therefore the module and runbook claims that explained variance “punishes bias and scale” are false. It punishes some scale/ranking errors, but not constant bias. Likewise, EV = 0 does not specifically mean “no better than predicting the average”; every constant predictor has EV = 0, including a badly biased one.

The code already reports the necessary complementary fields. Required wording and gate rule:

```text
EV: residual-variance / ranking-and-scale consistency, invariant to constant bias
bias: mean offset
RMSE/MAE: absolute calibration error
slope/intercept: affine calibration
```

Add the decisive test:

```python
realized = [-1, 0, 1, 2]
predicted = realized + 10
assert explained_variance == 1
assert bias == 10
assert rmse == 10
```

No single calibration verdict may be based on EV alone.

## Blocker 2: Monte Carlo residual is not PPO's trained advantage

The runbook states:

> The advantage PPO trains on is `realized - predicted`.

That is not the current trainer. PPO uses 32-mini-step, lambda-0.95 **truncated GAE**, with a critic bootstrap at the rollout edge. The calibration script uses a complete-episode Monte Carlo return with no bootstrap.

Thus:

```text
Monte Carlo return - prediction
```

is an independent critic-calibration residual. It is not the policy advantage used by the historical runs. A positive bias in a slice does not prove that every historical policy advantage in that slice pointed the same way.

Required wording:

> This residual measures error against the realized complete-episode return. Compare it with, but do not rename it as, the trainer's truncated bootstrapped GAE advantage.

The final Gate 0 note should join this output with Codex's raw-GAE/bootstrap telemetry rather than substitute one for the other.

## Blocker 3: same seed does not produce the same episode population

The collector stops when the first `N` episodes across a vector of environments have completed:

```python
while len(episodes) < N:
    ...
    for slot in done_slots:
        episodes.append(...)
```

Slots that are still playing are discarded when the quota is reached. Different policies and decoding modes have different episode lengths, so the first 96 completed games need not be the same 96 episode seeds. Simultaneous completions can also make the count exceed 96. A common initial RNG seed does not fix this asynchronous first-finisher selection.

This matters for every requested comparison:

- clone versus I@1000;
- I@1000 argmax versus I@1000 scope decoding;
- seat, map-size and turn-bucket mixtures.

The per-episode output currently records map index and seat but not the load-bearing `episode_seed`; initial inventories also depend on that seed, so `(map_index, seat)` is insufficient for a join.

Required repair:

1. record `episode_seed` in every episode row;
2. define a fixed episode-seed population before evaluation;
3. ensure each requested seed contributes exactly one complete game to every arm;
4. fail if the seed sets differ.

The simplest slow reference is `num_envs=1, episodes=N` with the same starting seed. A faster implementation may keep vectorization, but it must collect a declared seed list rather than the first N finishers. Add a test with deliberately different episode lengths proving two policies still return the same seed set and exactly N games.

The already-running outputs remain useful as exploratory within-policy calibration, but they are not a controlled cross-checkpoint population unless their episode identities can be recovered and joined.

## Blocker 4: row-weighted metrics confound critic quality with roster and episode length

The overall calibration treats every mini-step as an independent row. Consequently:

- a turn with four trolls receives five times the weight of a one-row decision event;
- long episodes receive more weight than short episodes;
- all mini-steps of a turn share the same realized return;
- policies that buy different numbers of trolls induce different weighting schemes.

Row weighting is relevant to “what distribution the trainer optimized,” but it is not sufficient for “is this critic true across games?” and it weakens cross-policy comparison.

Report three populations separately:

1. `by_ministep` — current row-weighted view, matching optimizer exposure;
2. `by_turn` — one canonical row per game turn, preferably the PLAN row;
3. `by_episode_start` — one row per fixed episode seed at the initial PLAN decision.

At minimum add aggregate calibration for the existing per-episode `predicted_value_at_start` and `realized_return_at_start`. Use the fixed seed population from Blocker 3.

## Interpretation boundary for the current runs

The current clone / I@1000 argmax / I@1000 scope runs may answer qualitative questions such as:

- are predictions grossly off-scale?
- is realized-return correlation near zero?
- do early-turn predictions look worse than late-turn predictions?

They cannot yet establish a controlled difference between checkpoints or decoding modes unless the exact episode populations match. Their EV must be read together with bias, RMSE, slope and intercept, and their Monte Carlo residual must not be called the PPO advantage.

## Gate 0 acceptance amendment

The critic-calibration half passes only when:

- return-to-go tests remain green;
- the EV wording/test is corrected;
- Monte Carlo residual and GAE advantage are explicitly separated;
- every compared arm uses exactly the same declared episode seeds;
- `episode_seed` is present and seed-set equality is checked;
- mini-step, turn-balanced and episode-start calibrations are all reported;
- the final note joins these results with the rollout bootstrap/raw-advantage telemetry.

No training run, checkpoint, dataset, YT operation, platform call or Arena state was changed by this review.
