# Runbook — the value-gradient measurement (`grad_decompose.py`), revision 4

Card: `coordination/tasks/20260829-nn-bot-way-b.md`.
Charters: `coordination/messages/local_claude_1/20260830T210000Z-...-gradient-handoff.md` (the
instrument) and `.../20260831T074500Z-...-gate0-handoff.md` (Gate 0) and
`.../20260831T113500Z-...-gate0-closing2-handoff.md` (closing round two: this revision).
Review folded in: `agent/chatgpt_1@c50b2185`,
`chatgpt_1/nn-way-b/grad-decompose-instrument-review-2026-08-30.md`.
Instrument: `local_claude_1/nn-bot/grad_decompose.py`; tests `tests/test_grad_decompose.py` (50).

The instrument is written; the host is the coordinator's, so the runs below are his to execute.
Each writes one JSON file, and run 1 also writes one census file that runs 2, 3 and 4 read. Sending
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

## The four runs

Interpreter `/home/tarstars/venvs/nn-bot/bin/python` (the host's `/home/tarstars/nn-venv/bin/python`
is the same torch; use whichever the other Gate 0 scripts use), from the repo root, `PYTHONPATH=.`.

```bash
OUT=/home/tarstars/nn-data/grad-decompose          # any writable directory
CLONE=<the clone .pt>                              # run G's --initial-checkpoint
PY=/home/tarstars/venvs/nn-bot/bin/python

# 1. THE CLONE — a HYPOTHETICAL NO-WARM-UP FIRST UPDATE. The coefficients below are run G's,
#    spelled out in full (the clone carries no training config of its own, so nothing may be
#    left to parser defaults), but this is NOT G's first update and NOT G's clone->PPO handoff:
#    G ran --critic-warmup-updates 300, so for its first 300 updates every policy-side tensor
#    including the shared trunk was bit-frozen and there was no critic-to-policy trunk path at
#    all. This row is path-existence evidence only (chatgpt_1, 10:13Z). It is also the run that
#    writes the census the other three read.
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
    --num-envs 128 --rollout-steps 32 --minibatch-size 1024 \
    --counterfactual-observations 512 \
    --next-update-variants adam-resumed,adam-fresh,adam-resumed+common-clip \
    --minibatch-seeds 2 \
    --census-out $OUT/census-clone-512-v2.npz \
    --seed 20260831 --label clone-no-warmup-hypothetical --out $OUT/grad-clone.json

# 2. ppo-g at update 500 (gamma 0.999), judged on the clone's census
PYTHONPATH=. $PY local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-g-update000500.pt> --from-checkpoint-config \
    --anchor-checkpoint $CLONE \
    --minibatch-size 1024 --census-in $OUT/census-clone-512-v2.npz \
    --next-update-variants adam-resumed,adam-fresh,adam-resumed+common-clip \
    --minibatch-seeds 2 \
    --seed 20260831 --label ppo-g-500 --out $OUT/grad-ppo-g-500.json

# 3. ppo-h at update 500 (gamma 1.0), the same census
PYTHONPATH=. $PY local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-h-update000500.pt> --from-checkpoint-config \
    --anchor-checkpoint $CLONE \
    --minibatch-size 1024 --census-in $OUT/census-clone-512-v2.npz \
    --next-update-variants adam-resumed,adam-fresh,adam-resumed+common-clip \
    --minibatch-seeds 2 \
    --seed 20260831 --label ppo-h-500 --out $OUT/grad-ppo-h-500.json

# 4. ppo-g at update 250 — the warm-up tail, the nearest real state to the handoff G saved.
#    Its own saved optimizer state, its own config (including its real turn_steps, which sets
#    the decayed anchor coefficient), the same census. Read as "50 updates before the unfreeze",
#    never as the handoff itself.
PYTHONPATH=. $PY local_claude_1/nn-bot/grad_decompose.py \
    --initial-checkpoint <ppo-g-update000250.pt> --from-checkpoint-config \
    --anchor-checkpoint $CLONE \
    --minibatch-size 1024 --census-in $OUT/census-clone-512-v2.npz \
    --next-update-variants adam-resumed,adam-fresh,adam-resumed+common-clip \
    --minibatch-seeds 2 \
    --seed 20260831 --label ppo-g-250-warmup-tail --out $OUT/grad-ppo-g-250.json
```

### What changed in revision 3, and why the runs must be repeated

* **The geometry.** Runs G and H trained at `--num-envs 128 --rollout-steps 32`; revision 2's clone
  command said `32 x 128`. Both are 4,096 rows and they are not the same measurement — the number
  of distinct games and the length of each trace differ (chatgpt_1, 08:35Z). The clone command
  above is corrected, and because the census is drawn from the clone's rollout, the census changes
  with it: revision 3 writes `census-clone-512-v2.npz` and runs 2 and 3 read that. Runs 2 and 3 take
  their own geometry from `--from-checkpoint-config` and were always right.
* **The optimizer state was being consumed.** Every arm's `optimizer.step()` was advancing the
  caller's saved Adam moments in place, so the arms ran from states one, two and three updates
  apart. Fixed; every `adam-resumed` number in the revision-2 outputs is void and this is the
  reason the runs must be repeated rather than merely extended.
* **`adam-resumed+common-clip`** gives every arm the FULL arm's clip multiplier. The plain variant
  is what the trainer would do; this one closes the shared-clip channel between the arms so the
  trunk path can be read on its own. It costs one extra arm per report.
* **`--minibatch-seeds 2`** runs the whole next-update counterfactual again on a second shuffle of
  the same rollout, under `next_update_replications`. No second rollout is collected; the cost is
  one more set of arms.
* Every comparison now carries `decision_margin`: how far the census choices sat from flipping and
  what fraction came 10 %, 25 % and 50 % closer. Read it beside the argmax counts, which see
  nothing until a decision changes hands. Revision 4 restricts it to rows with a positive
  baseline margin and reports `tied_baseline_rows` separately; see below.

### What changed in revision 4, and why the numbers move

Two of chatgpt_1's five closing blockers land here; the coordinator upheld both (11:30Z).

* **Baseline ties are out of the margin population (10:04Z).** A row whose margin was exactly
  zero *before* the update was already on the boundary, so its non-positive end margin cannot be
  evidence that the update pushed it over. `decision_margin` now speaks about `start > 0` rows
  only — `rows`, `argmax_changed_rows`, the mean/median margins, the shrink fractions and
  `fraction_margin_crossed` all share that population — and reports the discarded rows beside
  them as `tied_baseline_rows`. The no-op falsifier that fixed this is a test: two rows,
  `[2,1] -> [2,1]` beside `[1,1] -> [1,1]`, nothing moved, revision 3 reported half the rows
  crossed. **Every `fraction_margin_crossed` from a revision-3 output is void**; that is the
  reason the three runs above are repeated once more, and it is a cheap repeat — the same rollout
  geometry, the same census file, no new training.
* **Run 4, the warm-up tail (10:13Z).** Run G's recorded configuration sets
  `--critic-warmup-updates 300`: for updates 1–300 only the critic head moves, so G's *actual*
  first update has no critic-to-policy trunk path by construction, and the policy first unfreezes
  at update 301 — after the critic head, the optimizer moments, the environment population and
  the value predictions have all changed for 300 updates. Run 1 is therefore relabelled and run 4
  is added. G saved no update-300 checkpoint; **250 is the closest saved state**, still inside the
  warm-up with the policy tensors bit-frozen and the critic 250 updates trained.
* **What run 4 is, exactly.** The instrument inherits the trainer's parser, so
  `--critic-warmup-updates` is accepted from the checkpoint's config and then *ignored* — nothing
  in `grad_decompose.py` reads it. Run 4 is thus the hypothetical **unfrozen** full-PPO update
  computed at the update-250 state: the gradients the first post-warm-up update would see if it
  arrived 50 updates early. It is the nearest measurable thing to the handoff and it is not the
  handoff. If the coordinator's host does hold an update-300 checkpoint after all, run it instead
  and say so — that one *is* update 301.

Notes on the flags:

* **Run 1 must run first** — runs 2, 3 and 4 read the census it writes. If the clone command fails
  for any reason, say so rather than letting the others draw their own censuses; a report whose
  `census.loaded_from` is absent is not comparable with one whose is.
* Run 1's flags are run G's recipe **written out literally**, per the review: with the clone
  carrying no Phase-3 config, anything omitted would silently be a parser default and the clone
  row would not be comparable with runs 2 and 3. If any G value below differs from the run's own
  `start` record, the record wins — please correct the command and say what you changed.
  (`--anchor-turn-steps 0` sets the anchor coefficient to its undecayed 0.1: the clone is at the
  start of training, which is where run G's anchor was.)
* `--from-checkpoint-config` in runs 2, 3 and 4 takes every training coefficient out of that
  checkpoint's own saved config, so each is measured under the settings it actually ran with.
  `--census-in`, `--label`, `--out` and `--seed` are measurement flags and are never taken from a
  checkpoint.
* Keep `--seed` identical across all four. It aligns the environments; the checkpoints still
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
| `decision_margin` (inside each comparison) | per row class: `rows` (positive-baseline-margin rows only), `tied_baseline_rows` (excluded boundary rows, kept visible), `argmax_changed_rows`, the mean/median starting margins, the 10/25/50 % shrink fractions and `fraction_margin_crossed`. `null` when the class has no analysable row |
| `census` | the positions everything was judged on: rows, PLAN/TROLL split, coverage, content `sha256`, and `loaded_from` when it came from a file |
| `resumed_optimizer` | whether this checkpoint's saved optimizer state fits the PPO optimizer at all, and why not if it does not |
| `minibatch`, `diagnostics` | the rows the step was taken on, and the run's own loss values on them |

The four JSON files, plus the census file, are what I need. If the host's run prints anything on
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
3. **What the warm-up tail says** — run 4 against run 1: the same hypothetical unfrozen update,
   one at the clone and one 250 critic-only updates later, judged on the same census. It is the
   nearest evidence available about whether the trunk path grows over the warm-up, and it is
   still not G's handoff update.
4. **What it implies for the staged plan** — whether freezing the trunk and the spatial head
   (`--train-scope plan-critic`) is enough on its own, or whether a later joint fine-tune also
   needs `value_coef` lowered or the value path detached.

**Two scope limits are carried verbatim into the verdict**, from chatgpt_1's upheld blockers:

* `EARLY_GAME_LOCAL_ONLY` (09:52Z) — every row here is measured on fresh-game populations, so the
  verdict is an early-game local counterfactual and decides nothing about the historical
  mid-training trajectory. The staggered/burned-in population measurement is deferred work.
* The clone row is a **hypothetical no-warm-up first update** (10:13Z) — path-existence evidence.
  Its magnitude is not attributed to G's or H's clone→PPO handoff, and run 4 is read as "50
  updates before the unfreeze", not as the handoff.

A negative result is a result: if FULL and NO-V decide the same commands on the census and the
trunk cosine is near zero, the value gradient is not the cause of the erosion, and the note will
say so in as many words.
