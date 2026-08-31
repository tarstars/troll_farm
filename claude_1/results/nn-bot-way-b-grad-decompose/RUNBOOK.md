# Runbook — the value-gradient measurement (`grad_decompose.py`), revision 2

Card: `coordination/tasks/20260829-nn-bot-way-b.md`.
Charters: `coordination/messages/local_claude_1/20260830T210000Z-...-gradient-handoff.md` (the
instrument) and `.../20260831T074500Z-...-gate0-handoff.md` (Gate 0: this revision).
Review folded in: `agent/chatgpt_1@c50b2185`,
`chatgpt_1/nn-way-b/grad-decompose-instrument-review-2026-08-30.md`.
Instrument: `local_claude_1/nn-bot/grad_decompose.py`; tests `tests/test_grad_decompose.py` (31).

The instrument is written; the host is the coordinator's, so the runs below are his to execute.
Each writes one JSON file, and run 1 also writes one census file that runs 2 and 3 read. Sending
those files back is all I need for the write-up.

## What changed in revision 2 (and why the old commands are superseded)

chatgpt_1's review found three things, all repaired:

1. **The clone's optimizer state cannot be resumed at all.** The behaviour-cloning trainer saves
   `Adam(model.parameters())` — one parameter group; the PPO trainer builds two (actor and
   critic, at different learning rates). Loading one into the other raises, and the old clone
   command would have died before writing any JSON. Now the layouts are compared first and the
   mismatch is a structured `{"available": false, "reason": "optimizer layout incompatible…"}`
   while every other variant is measured as usual. The moments are **not** remapped: they were
   accumulated from a different loss under a different grouping. **Quote `adam-resumed` only for
   g and h; the clone has no resumed row and that is correct, not a failure.**
2. **A value-only step under restored Adam is not a value-only *cause*.** The restored moments
   carry the historical *combined* gradient, so momentum from the policy, entropy and anchor
   terms rides along. The causal question is now answered by a new section, `next_update`: from
   one checkpoint, one optimizer state and one minibatch, two copies take one step each —
   **FULL** (policy + entropy + value + anchor) and **NO-V** (the same without the value term) —
   and are then compared on the same fixed positions. A third arm, **FULL-detached-V**, keeps the
   value term but cuts its route into the shared trunk (`pooled.detach()`), which separates "V
   moves the policy through the trunk" from "V moves the policy at all". The old value-only
   numbers stay as `counterfactual`, labelled as diagnostics.
3. **Two checkpoints do not visit the same positions**, so reading g against h on their own
   rollouts mixes the mechanism with where each policy walks. Every before/after network is now
   judged on **one common census** — a saved file of observations, masks and phases
   (`--census-out` once, `--census-in` thereafter), stratified deterministically over the whole
   rollout's PLAN and TROLL rows, with its own content SHA-256 recorded in every report that used
   it. Each checkpoint still takes its honest local step on its own on-policy minibatch: the step
   is on-policy, the judging is common.

Also: the **effective** learning rates are now read off the optimizer's own parameter groups after
the state is loaded (a resumed step uses the checkpoint's saved, annealed rates), and reported
next to the configured ones.

## The three runs

Interpreter `/home/tarstars/venvs/nn-bot/bin/python` (the host's `/home/tarstars/nn-venv/bin/python`
is the same torch; use whichever the other Gate 0 scripts use), from the repo root, `PYTHONPATH=.`.

```bash
OUT=/home/tarstars/nn-data/grad-decompose          # any writable directory
CLONE=<the clone .pt>                              # run G's --initial-checkpoint
PY=/home/tarstars/venvs/nn-bot/bin/python

# 1. THE CLONE — measured under run G's recipe, spelled out in full (the clone carries no
#    training config of its own, so nothing may be left to parser defaults), and the run that
#    writes the census the other two read.
PYTHONPATH=. $PY local_claude_1/nn-bot/grad_decompose.py \
    --env full --maps data/processed/maps.jsonl \
    --initial-checkpoint $CLONE --anchor-checkpoint $CLONE --frozen-checkpoint $CLONE \
    --opponent-weights '{"champion_exact":1}' \
    --gamma 0.999 --gae-lambda 0.95 \
    --wood-shaping 0.0 --end-wood 4.0 \
    --actor-lr-scale 0.3 --learning-rate 0.00025 \
    --anchor-coef 0.1 --anchor-coef-final 0.05 --anchor-decay-steps 100000000 \
    --anchor-turn-steps 0 \
    --entropy-coef 0.01 --value-coef 0.5 --clip-coef 0.2 --max-grad-norm 0.5 \
    --num-envs 32 --rollout-steps 128 --minibatch-size 1024 \
    --counterfactual-observations 512 \
    --census-out $OUT/census-clone-512.npz \
    --seed 20260831 --label clone-under-g-recipe --out $OUT/grad-clone.json

# 2. ppo-g at update 500 (gamma 0.999), judged on the clone's census
PYTHONPATH=. $PY local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-g-update000500.pt> --from-checkpoint-config \
    --anchor-checkpoint $CLONE \
    --minibatch-size 1024 --census-in $OUT/census-clone-512.npz \
    --seed 20260831 --label ppo-g-500 --out $OUT/grad-ppo-g-500.json

# 3. ppo-h at update 500 (gamma 1.0), the same census
PYTHONPATH=. $PY local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-h-update000500.pt> --from-checkpoint-config \
    --anchor-checkpoint $CLONE \
    --minibatch-size 1024 --census-in $OUT/census-clone-512.npz \
    --seed 20260831 --label ppo-h-500 --out $OUT/grad-ppo-h-500.json
```

Notes on the flags:

* **Run 1 must run first** — runs 2 and 3 read the census it writes. If the clone command fails
  for any reason, say so rather than letting 2 and 3 draw their own censuses; a report whose
  `census.loaded_from` is absent is not comparable with one whose is.
* Run 1's flags are run G's recipe **written out literally**, per the review: with the clone
  carrying no Phase-3 config, anything omitted would silently be a parser default and the clone
  row would not be comparable with runs 2 and 3. If any G value below differs from the run's own
  `start` record, the record wins — please correct the command and say what you changed.
  (`--anchor-turn-steps 0` sets the anchor coefficient to its undecayed 0.1: the clone is at the
  start of training, which is where run G's anchor was.)
* `--from-checkpoint-config` in runs 2 and 3 takes every training coefficient out of that
  checkpoint's own saved config, so each is measured under the settings it actually ran with.
  `--census-in`, `--label`, `--out` and `--seed` are measurement flags and are never taken from a
  checkpoint.
* Keep `--seed` identical across the three. It aligns the environments; the checkpoints still
  play differently, which is exactly why the census exists.
* A second seed costs one more pass and is the cheapest check available if any headline number
  lands near a boundary.
* `--env fake` runs the whole thing with no Rust library and no data file. It exercises the code,
  not the runs; **no number from a fake-environment run may be quoted.**
* The clone's `next_update.adam-resumed` and `counterfactual.adam-resumed` will both come back
  `available: false` with the layout reason. Expected. Its `adam-fresh` rows are the readable ones.

## What comes back

| section | what to read in it |
| --- | --- |
| `objectives.{policy,entropy,value,anchor}` | each term's gradient norm per part of the network (`stem`, `tower`, `actor`, `plan`, `critic`), its trunk share, and `trunk_cosine_with_policy` — 1.0 means it pushes the trunk the same way the policy does, negative means against |
| `combined` | the gradient the update actually takes, and `clip_scale`, the factor `--max-grad-norm` shrinks it by |
| `linearity_check` | the four terms summed against the gradient of the summed loss; must be ~0 or the decomposition is not one |
| `by_row_class` | the same numbers computed on the PLAN rows and the TROLL rows separately |
| **`next_update.<variant>.comparisons.full_vs_no_value`** | **the causal number**: the same update with and without the value term, judged on the common census — commands changed, plan choices changed, mean logit shift |
| `next_update.<variant>.comparisons.full_vs_full_detached_value` | the structural control: the value term kept, its route into the shared trunk cut |
| `next_update.<variant>.arms.*` | each arm's own pre-clip gradient norm, clip scale, and **effective** (saved) learning rates against the configured ones |
| `counterfactual.adam-fresh` / `.sgd` | the value gradient in isolation: upper (scale-free) and lower (proportional) readings of a value-only step |
| `counterfactual.adam-resumed` | a **mixed-momentum diagnostic**, not a pure value effect — the restored moments carry the historical combined gradient |
| `census` | the positions everything was judged on: rows, PLAN/TROLL split, coverage, content `sha256`, and `loaded_from` when it came from a file |
| `resumed_optimizer` | whether this checkpoint's saved optimizer state fits the PPO optimizer at all, and why not if it does not |
| `minibatch`, `diagnostics` | the rows the step was taken on, and the run's own loss values on them |

The three JSON files, plus the census file, are what I need. If the host's run prints anything on
stderr, send that too — an empty `next_update` is a fact worth seeing.

## The verdict I will write from them

1. **Does the value term move the action heads materially through the trunk?** — the trunk share
   of the value gradient and its cosine against the policy gradient (mechanism), then
   `full_vs_no_value` on the common census (effect), with `full_vs_full_detached_value` deciding
   whether the effect travels through the trunk or only through the value head.
2. **Is it worse under the harder value target (γ = 1.0)?** — runs 2 and 3, judged on the *same*
   positions, so the comparison is between policies rather than between trajectories. This remains
   an observational comparison of two runs, not a controlled γ experiment: the two checkpoints
   also differ in their optimizer moments and their history. I will say so in the verdict.
3. **What it implies for the staged plan** — whether freezing the trunk and the spatial head
   (`--train-scope plan-critic`) is enough on its own, or whether a later joint fine-tune also
   needs `value_coef` lowered or the value path detached.

A negative result is a result: if FULL and NO-V decide the same commands on the census and the
trunk cosine is near zero, the value gradient is not the cause of the erosion, and the note will
say so in as many words.
