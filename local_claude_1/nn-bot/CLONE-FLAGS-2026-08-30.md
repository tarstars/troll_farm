# The two flags the coordinator asked for, and what the second one measured

Task `20260829-nn-bot-way-b-dataset`, 2026-08-30, claude_1.  Two acknowledgements asked me for
one flag each — a held-out split the trainer can draw itself (03:15Z) and a plan-head decoding
switch on the bench (02:11Z).  Both are here, both are tested, and the bench switch turned out to
measure something the report could not previously say.

## 1. `train_clone.py --holdout PERCENT` — a held-out split without rebuilding the dataset

The dataset on the host (`/home/tarstars/nn-data/dataset-v400-2026-08-30/`) was built without
`--holdout`, so every row carries `split = 0` and the 02:2xZ run holds nothing out: its accuracies
are training accuracies.  Rebuilding is 1 min 24 s of work but a different dataset directory and a
different set of checksums, so the flag draws the line at load time instead:

    train_clone.py --shard <dir> --name <name> --holdout 20 ...

* The line is drawn by **`build_dataset.held_out`** — the builder's own function, imported, not a
  second implementation — so a trainer-side split and a builder-side split agree game for game.
  Verified on the pilot shard, which *was* built at `--holdout 20`: the builder's stored `split`
  column and `held_out(game_id, 20)` are identical over all ten games, and both hold out the same
  single game `893255096`.
* It is **by game**, never by row: a held-out number is never a turn of a game the network trained
  on.
* It **refuses** a shard that already carries a holdout, naming both percentages, rather than
  re-splitting silently — a re-split would move games across the line the shard drew.
* The checkpoint's `config` records `holdout_percent` and a new `holdout_drawn_by`
  (`trainer` or `builder`), so a checkpoint says which split it was judged against.

Measured end to end on a copy of the pilot shard with the split zeroed (the host dataset's shape):
2,000 training rows over 9 games, 500 held-out rows over 1 game, disjoint, `holdout_drawn_by:
trainer`.

**A second fix in the same file, the one the coordinator named:** a check that needs `--shard` and
was not given it now prints `skip`, not `FAIL`, and the summary line counts skips separately.  The
self-test without a shard is now `PASS (0 failures, 1 skipped)`; with `--shard … --name pilot` it
is `PASS (0 failures, 0 skipped)`.  It was never a defect, only an output that read like one.

The self-test grew a seventh check: `--holdout` puts every game on exactly one side, holds out
15–25 % at 20, holds nothing out at 0, and is stable across calls.

## 2. `bench.py --plan-decoding {argmax,sample}` (and `--plan-temperature`)

The bench lacked it; it has it now.  `sample` draws the plan from the masked soft-max of the plan
head at `--plan-temperature` (default 1.0); commands stay argmax — only the plan call was in
question.  The generator is reseeded per game from `--seed`, so one seed is one run.  The report
records `plan_decoding` and `plan_temperature`; the policy's name carries the decoding.

**The argmax path is unchanged.**  Re-run against the committed day-7 smoke
(`results/bench-clone-smoke.json`, same checkpoint, same 4 maps, both seats, seed 0): 0 of 8
per-game rows differ once `policy_seconds` is deleted.

A seventh bench check covers the sampler without needing a checkpoint: an illegal index carrying
by far the largest logit is never drawn, the same seed repeats a 300-draw run exactly, temperature
0.01 collapses to the best legal index, and an empty mask raises.

### What the switch measured, and why the report now carries two more counts

Run on the **4,000-row smoke checkpoint** (`results/clone-smoke/clone-pilot.pt`), 4 maps, both
seats, seed 0:

| decoding | plans drawn | refused by the dry run | TRAINs emitted | policy score (mean) |
|---|---|---|---|---|
| argmax | 0 | 0 | 0 | 19.4 |
| sample (T=1) | 568 | 568 | 0 | 19.4 |
| *reference:* random-mask | 38 | 37 | 1 | — |

Sampling does fire — a probe inside one game drew plan 0 on 162 of 300 turns and a wide spread of
non-zero plans on the rest — but the game is byte-identical to the argmax game, because a plan is
only a *target*: `nn_runtime.plan_trains` runs the environment's own dry run and emits the TRAIN
only if it would succeed.  Every one of the 568 plans the smoke clone asked for was refused there,
while a uniform draw from the same 400-entry mask passed roughly one time in 38.

The plan mask is no help in reading this: it marked all 400 plans legal on all 300 turns of the
probed game, so affordability is decided by the dry run alone and nowhere else.

Two facts follow, and they matter for the coordinator's decision:

* **Sampling alone did not make the smoke clone buy.**  Whether the full 817,811-row clone behaves
  the same is exactly what the switch is for; the smoke checkpoint cannot answer it.
* **A refused plan used to leave no trace.**  `policy_trains_requested` records only purchases the
  dry run allowed, so a report that bought nothing could not say whether the head never asked or
  whether everything it asked for was unaffordable.  Each row now carries `policy_plans_drawn` and
  `policy_plans_refused`, and the report their totals.  Note for a reproducer: this adds two keys
  to every per-game row, so a row-for-row comparison against a report written before today differs
  in exactly those two keys and nothing else.

No Arena action, no platform action, no dependency installed.  Everything above ran in
`/home/tarstars/venvs/nn-bot` against `rust/target/release/libtroll_farm.so`, plan vocabulary
`v400-2026-08-29`.

## Commands

    # the trainer, both ways
    python3 local_claude_1/nn-bot/train_clone.py --self-test
    python3 local_claude_1/nn-bot/train_clone.py --self-test \
        --shard local_claude_1/nn-bot/results/pilot --name pilot
    python3 local_claude_1/nn-bot/train_clone.py --shard <a shard built without --holdout> \
        --name pilot --epochs 1 --batch 64 --limit 2000 --holdout 20 --out <dir>

    # the bench, both decodings
    python3 local_claude_1/nn-bot/bench.py --self-test
    python3 local_claude_1/nn-bot/bench.py --policy network \
        --checkpoint local_claude_1/nn-bot/results/clone-smoke/clone-pilot.pt \
        --games 4 --both-seats --plan-decoding argmax --out <a.json> --no-replays
    python3 local_claude_1/nn-bot/bench.py --policy network \
        --checkpoint local_claude_1/nn-bot/results/clone-smoke/clone-pilot.pt \
        --games 4 --both-seats --plan-decoding sample --out <b.json> --no-replays
