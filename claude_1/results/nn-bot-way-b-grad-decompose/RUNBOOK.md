# Runbook — the value-gradient measurement (`grad_decompose.py`)

Card: `coordination/tasks/20260829-nn-bot-way-b.md`.
Charter: `coordination/messages/local_claude_1/20260830T210000Z-20260829-nn-bot-way-b-gradient-handoff.md`.
Instrument: `local_claude_1/nn-bot/grad_decompose.py`; tests `tests/test_grad_decompose.py`.

The instrument is written; the host is the coordinator's, so the three runs below are his to
execute. Each writes one JSON file; sending those three files back is all I need for the write-up.

## What it answers

chatgpt_1's falsifier: after the critic warm-up, `value_coef · value_loss` backpropagates through
the shared `stem`/`tower` into both action heads at the actor's learning rate. The instrument
takes one honest minibatch, differentiates each of PPO's four terms separately on it, and then
takes one value-only optimizer step on a **copy** of the checkpoint to see what that alone does to
the commands. Nothing is trained, nothing is submitted, the checkpoint file is never written to.

## The three runs

The interpreter is the clone's: `/home/tarstars/venvs/nn-bot/bin/python`. `--from-checkpoint-config`
takes every training coefficient (`--gamma`, `--gae-lambda`, `--value-coef`, `--entropy-coef`,
`--actor-lr-scale`, `--learning-rate`, `--max-grad-norm`, `--reward-scale`, the opponent weights,
the maps, `--num-envs`, `--rollout-steps`, `--minibatch-size`) out of that checkpoint's own saved
config, so each run is measured under the settings it actually ran with. Anything typed on the
command line still wins over the checkpoint.

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1        # or wherever the host tree is
OUT=/home/tarstars/nn-data/grad-decompose             # any writable directory

# 1. the clone (no PPO has happened yet — the baseline reading)
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <clone.pt> \
    --anchor-checkpoint  <clone.pt> \
    --env full --minibatch-size 512 --counterfactual-observations 512 \
    --seed 20260830 --label clone --out $OUT/grad-clone.json

# 2. ppo-g at update 500 (gamma 0.999)
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-g-update000500.pt> --from-checkpoint-config \
    --anchor-checkpoint  <clone.pt> \
    --minibatch-size 512 --counterfactual-observations 512 \
    --seed 20260830 --label ppo-g-500 --out $OUT/grad-ppo-g-500.json

# 3. ppo-h at update 500 (gamma 1.0) — same seed, so the two are read side by side
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-h-update000500.pt> --from-checkpoint-config \
    --anchor-checkpoint  <clone.pt> \
    --minibatch-size 512 --counterfactual-observations 512 \
    --seed 20260830 --label ppo-h-500 --out $OUT/grad-ppo-h-500.json
```

Notes on the flags:

* The clone has no saved training config, so run 1 takes its coefficients from the command line;
  add the `ppo-g` run's flags to it if the clone is to be read under the same settings as run 2
  (recommended, and then say so in the report).
* Keep `--seed` identical across the three so the environments and the minibatch shuffle line up;
  the checkpoints differ, so the collected rows still differ — the seed removes one source of
  noise, it does not remove all of it.
* The same three commands can be repeated with a second seed at negligible cost. If any headline
  number is close to a boundary, that is the cheapest check available.
* `--env fake` runs the whole thing without the Rust library or a checkpoint; it exercises the
  code, not the runs, and no number from it may be quoted.

## What comes back

One JSON per run, with these sections:

| section | what to read in it |
| --- | --- |
| `objectives.{policy,entropy,value,anchor}` | each term's gradient norm per part of the network (`stem`, `tower`, `actor`, `plan`, `critic`), its trunk share, and `trunk_cosine_with_policy` — 1.0 means it pushes the trunk the same way the policy does, negative means against |
| `combined` | the gradient the update actually takes, and `clip_scale`, the factor `--max-grad-norm` shrinks it by |
| `linearity_check` | the four terms summed against the gradient of the summed loss; must be ~0 or the decomposition is not one |
| `by_row_class` | the same numbers computed on the PLAN rows and the TROLL rows separately |
| `counterfactual.adam-resumed` | **the honest counterfactual**: one value-only step with the checkpoint's own Adam moments — commands changed, plan choices changed, mean logit shift |
| `counterfactual.adam-fresh` / `.sgd` | the upper and lower readings of the same step (see the module docstring: fresh Adam is scale-free and overstates; SGD is proportional to the gradient and understates a mid-run step) |
| `minibatch`, `diagnostics` | the rows the measurement was made on, and the run's own loss values on them |

## The verdict I will write from them

1. Does the value term move the action heads materially through the trunk? — the trunk share of
   the value gradient, its size against the policy gradient's trunk push, the cosine between them,
   and `spatial_argmax_changed` / `plan_argmax_changed` under `adam-resumed`.
2. Is it worse under γ 1.0? — runs 2 and 3 side by side on the same seed.
3. If confirmed: whether the queued `ppo-i` (trunk and spatial actor frozen, plan + critic only)
   is enough on its own, or whether the later joint fine-tune also needs `value_coef` lowered.

A negative result is a result: if the value-only step changes no commands and the trunk cosine is
near zero, the mechanism is not the cause of the erosion and the note will say so.
