# Runbook — the independent critic calibration (`critic_calibration.py`)

Card: `coordination/tasks/20260829-nn-bot-way-b.md`.
Charter: `coordination/messages/local_claude_1/20260831T074500Z-20260829-nn-bot-way-b-gate0-handoff.md`
(Gate 0, claude_1's half, delivery 2). Asked for by chatgpt_1's review of 2026-08-31, §5.
Script: `local_claude_1/nn-bot/critic_calibration.py`; tests `tests/test_critic_calibration.py` (16).

## The question it answers

The trainer logs `explained_variance` against **its own bootstrapped returns** — the critic marked
against a target that already contains the critic's opinion. A high number there means
"self-consistent", not "true". This plays complete games and marks the critic's prediction against
**what actually happened**: the realized return-to-go, under training's own reward definition,
scale and per-turn discount, with nothing bootstrapped, because every episode is played to its
real end.

## The two runs

Interpreter and library as for the other Gate 0 scripts, from the repo root, `PYTHONPATH=.`.

```bash
OUT=/home/tarstars/nn-data/critic-calibration     # any writable directory
CLONE=<the clone .pt>
PY=/home/tarstars/venvs/nn-bot/bin/python

# 1. the clone — the baseline critic, before any PPO
PYTHONPATH=. $PY local_claude_1/nn-bot/critic_calibration.py \
    --env full --maps data/processed/maps.jsonl \
    --initial-checkpoint $CLONE --frozen-checkpoint $CLONE \
    --opponent-weights '{"champion_exact":1}' \
    --gamma 0.999 --wood-shaping 0.0 --end-wood 4.0 \
    --num-envs 32 --episodes 96 --decoding argmax --per-episode \
    --cells-out $OUT/cells.json \
    --seed 20260831 --label clone --out $OUT/calibration-clone.json

# 2. run I at update 1000 — the run whose bench read 10 wins and then drifted
PYTHONPATH=. $PY local_claude_1/nn-bot/critic_calibration.py \
    --initial-checkpoint <ppo-i-update001000.pt> --frozen-checkpoint $CLONE \
    --env full --maps data/processed/maps.jsonl \
    --opponent-weights '{"champion_exact":1}' \
    --gamma 0.999 --wood-shaping 0.0 --end-wood 4.0 --train-scope plan-critic \
    --num-envs 32 --episodes 160 --decoding argmax --per-episode \
    --restrict-to-cells $OUT/cells.json \
    --seed 20260831 --label ppo-i-1000 --out $OUT/calibration-ppo-i-1000.json
```

Notes on the flags:

* **`--gamma`, `--reward-scale`, `--reward-credit`, `--wood-shaping`, `--end-wood`, the pool and
  the maps must match the run being judged.** The realized return is computed under exactly these:
  a calibration measured under the wrong reward definition is a calibration of a run nobody made.
  If run I's own `start` record differs from the values above, the record wins — change the
  command and say what you changed.
* **`--decoding`** decides how the games are played. `argmax` (above) is the shipped bot's
  decoding and the one the bench measures, so it answers "is the critic true about the games we
  are scored on". `scope` plays exactly as the run trains (under `plan-critic`, sampled plan rows
  and argmax troll rows) and answers "is the critic true about the games it learns from". They are
  different questions and both are cheap; if the host hour allows, run **both** on run I — the gap
  between them is itself a finding.
* `--episodes` counts **complete** games. Slots still mid-game when the last one finishes are
  discarded, and the report says how many rows that was. 96 games at 32 slots is three waves.
* `--max-mini-steps` is a safety cap; `collection.hit_mini_step_cap: true` means it stopped early
  and the numbers are on fewer games than asked for.
* `--per-episode` adds one row per game (margin, turns, win, seat, map, the value predicted at the
  first decision against the return that actually followed). Small, and worth having.
* `--env fake` runs the whole thing with no Rust library and no checkpoint. It exercises the code,
  not the runs; **no number from a fake-environment run may be quoted.**

## What comes back

| section | what to read in it |
| --- | --- |
| `calibration.overall` | slope, intercept, correlation, explained variance, bias, RMSE — the critic against the realized discounted return |
| `calibration.overall_undiscounted` | the same against the plain sum of future rewards |
| `calibration.slices.game_turn` | by turn band (0-9, 10-24, 25-49, 50-99, 100-149, 150-199, 200-299, 300+) — is it blind early and sharp late? |
| `calibration.slices.map_size_valid_cells` | by board size, counted as the valid cells in observation plane 0 — the four real sizes come out as four groups |
| `calibration.slices.seat` | seat 0 against seat 1 |
| `calibration.slices.row_class` | plan rows against troll rows. A turn's rows share their realized return, so a difference here is a difference in the critic's *predictions* |
| `collection` | games completed, rows, rows discarded, decoding, the reward settings used, win rate, mean margin, illegal commands (must be 0) |
| `episodes` (with `--per-episode`) | one row per game |

## How to read the numbers

* **slope 1, intercept 0** is a true critic. **Slope < 1** means the critic exaggerates how much
  positions differ; **slope > 1** means it is too timid. The intercept is its bias in reward units.
* **correlation** is the ranking question alone — it can be high while the scale is wrong.
* **explained variance** punishes bias and scale as well as ranking. **0 means no better than
  predicting the average outcome**, and it can be negative. This is the number to compare with the
  trainer's own logged `explained_variance`: if the trainer's is high and this one is near zero,
  the critic is self-consistent and not true, which is exactly the review's §5 suspicion.
* The **advantage** PPO trains on is `realized - predicted`. A critic with a bias makes every
  advantage in a slice point the same way, which is a systematic push, not noise. So the bias
  column of the `game_turn` and `row_class` slices is where a plan-head drift story would show up.

A negative result is a result: if the clone's and run I's calibrations are both decent and alike,
the critic is not the weak link and the note will say so.


## Revision 3 — the matched population, and the three weightings

Every arm must be scored over **the same games**, or a difference between arms can be a difference
in which games each one happened to finish (chatgpt_1, 08:10Z, point 3). The collector keeps the
first `--episodes` games to finish and drops the slots still in flight, so it does not give that
for free.

* The **first** arm writes the games it played with `--cells-out`. A game is identified by its
  `(map index, seat)` cell — the environment chooses its own maps, so there is no seed to
  predeclare from here; predeclaring the seeds themselves needs the environment to accept a
  map/seat schedule, which is environment-side work and is not pretended to be done here.
* Every **later** arm passes `--restrict-to-cells` and is cut to exactly one complete game per
  declared cell. A declared cell that never came up is a **failure** — the run stops and names the
  missing cells — not a quietly smaller sample. `--allow-unmatched-population` waives that
  knowingly and records the shortfall in `collection.population`.
* Give the later arms **more** `--episodes` than the first (160 against 96 above): they need to
  keep playing until every declared cell has come up, and the surplus games are dropped.
* The scope arm, if it is run, takes the same `--restrict-to-cells` as the argmax arm.

`calibration.weightings` now reports the same statistics over three populations side by side —
every mini-step, one PLAN row per turn, and one initial PLAN row per game — because a mini-step
weighting lets long games and large rosters dominate and repeats each turn's single common target
once per troll. `calibration.reading` states plainly that `realized` is the complete-episode
Monte-Carlo return and **not** the truncated lambda-0.95 GAE target the trainer fitted, so the two
are read side by side rather than one in place of the other. And `explained_variance` now carries
its own note: it is blind to a constant bias, so it is never quoted without bias, RMSE and slope.
