# HANDOVER 2026-08-28 06:1xZ — the third troll is on the ladder; the ladder queue runs on the VM for the owner's 8 offline hours

Delta since `coordination/HANDOVER-2026-08-28-third-troll.md` (04:40Z) through 06:1xZ, written by
`local_claude_1` before the owner takes this computer offline ("I'm going to go offline for 8 hours
with this computer. So I propose to move ladder queue to VM. let's put three_heroes to the start and
other tasks later. I want to submit (a)"). Trunk at writing: `origin/main` == `agent/local_claude_1`
== the checkout `/home/tarstars/prj/troll_farm`.

## Resume here

- **On the ladder: the third troll (a)** — `cgauto/submissions/candidate-third-troll-v6-instrument.rs`,
  sha `89493fa0…`, submission `41206542`, 05:49:18Z, agent `6670021`. The champion of record plus one
  change: after the second troll, both trolls collect the bill of a 2/3/0/3 lumberjack (6 plums,
  11 lemons, 2 apples, 11 iron) and train it the turn it is affordable, while ≥ 100 turns remain.
  Card `coordination/tasks/20260828-third-troll.md` (design accepted "ok ×4" + the owner's fifth
  point audited); diff `readable/diffs/third-troll.diff` +123/−29; generator
  `local_claude_1/third-troll/make_third_troll.py` (nine replacements, seven edits).
- **The ladder queue runs unattended on the VM**: `local_claude_1/ladder-queue/` — `runner.py` by
  the VM user's cron every 5 minutes (`ssh troll-vm crontab -l`, the `# ladder-queue` line; log
  `/home/tarstars/ladder-queue-cron.log` and `local_claude_1/ladder-queue/runner.log`), in the VM
  checkout `/home/tarstars/prj/troll_farm` (on `main`, pulled to `3ec821b8`+). It reads each item
  at 62 min (arena-room rank/score — the site's number; `cg_rank.arena_room`, urllib only, the
  `codingame` package is not installable on the VM), collects the 160 games into
  `local_claude_1/ladder-queue/games-<submission id>/` (waits for a complete batch until 110 min),
  appends `readings.jsonl`, commits and pushes to `origin/main`, submits the next. **Queue
  (`queue.json`):** (a) 2/3/0/3 r1 [up] → (b) the 2/2/0/2 variant (`…-2202-…`, sha `684104f1…`)
  → (a) r2 → (b) r2 → the apple farm r5 → r6 → the champion of record restored (the last bot stays
  up). A submission not accepted HALTS the queue (`state.json: halted`). Verified on the VM before
  leaving: one tick by hand (early look), the collector on the live window (58/58 packaged), a push
  dry-run through the VM's pre-push hook. **Next session: read `readings.jsonl` and the packages
  (`local_claude_1/the-floor/ladder_read.py <package.jsonl.gz> <agent id> <label>` — it lists every
  TRAIN, so the third troll's turn and share are visible), write the ledger rows `TTR-…` and the
  board, and report to the owner: (a)'s reading vs the champion's 21.2/42, (b)'s, and the second
  rounds.** The owner's prediction for (a) was not stated.
- **codex_1's reproduction** of the third-troll build/bed/smoke/select-equivalence is chartered
  (row 0-7, `coordination/tasks/20260828-third-troll-verify.md`) in parallel with the ladder round;
  a NOT REPRODUCED removes (a)'s second round from the queue and goes to the owner.
- **The floor is closed**: three readings 19.2 / 19.1 / 17.3 (mean 18.5) vs the champion's 21.2/42;
  its three packages are collected and read (ledger rows FLR-r1…r3). No round 4.
- **First command of the next session:** `cd /home/tarstars/prj/troll_farm-local_claude_1 && git pull --ff-only origin main` — the VM runner pushes to `origin/main` directly, so `main` will be ahead of `agent/local_claude_1`; fast-forward the branch before anything else (then `git push origin agent/local_claude_1`). The VM checkout is on `main` too; if the runner's push was refused it retries with `git pull --rebase` on the next tick.
- Ritual unchanged (sweep → read whole → `--mark` → commit; every shell command carries its own `cd`;
  `git pull` for the checkout in a separate call).

## What the smoke taught (the science, for the owner's reading)

- The bill is slow for the starter: speed 1 / carry 1 → one fruit per 10–14-turn round trip, 19
  fruits → a third troll in 5/24 local games at median turn 158 (the top four: 56–84 %, turn
  95–118). The iron half is fast (the trained troll, ~30 turns). A 2/2/0/2 third troll (14 fruits):
  12/24 at turn 116. The top four pay with an orchard planted next to the shack (README idea #2) —
  not built (the owner had rejected it for this card); it is the next card if the owner wants it.
- No stall by the change; the idle runs are bare maps (both bots idle). One interaction found: the
  champion's late replant rule (PICK + PLANT at turn ≥ 100 with ≤ 2 trees) can spend the bill's
  fruits (`c84154d2`).
- `select` (the joint choice of the trolls' commands) fell to a greedy pass at three trolls; now a
  joint search for any number, proven inert at two (58/58 identical games).
- Own score vs the resident on the bench: +497 (2/3/0/3), +252 (2/2/0/2) over 24 games — a fact;
  the bench has been wrong by ten points on a real bot.

## Operational notes (new)

- Cron lines for the VM must use absolute paths (cron starts in `$HOME`); the runner resolves the
  repo from its own path, so no `cd` is needed. I wrote the line without the absolute path three
  times before getting it right — check `crontab -l` after every install.
- The VM checkout `/home/tarstars/prj/troll_farm` was 3,848 commits behind `main` (nobody had pulled
  it since the branch switch); pulled 06:0xZ. The VM's `cg_session.txt` is identical to the host's.
- The VM has no `codingame` package (pip blocked) and no rustfmt; `rustc` is at `~/.cargo/bin`.
