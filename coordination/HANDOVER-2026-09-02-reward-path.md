# Handover — 2026-09-02 06:3xZ — the reward path confirmed, the stack rising, s22L queued

Written at the owner's request ("prepare for context flush"). Everything below is on `main`.
Read `coordination/GOAL.md` (its step-4/5 status blocks are current), then the tail of
`coordination/tasks/20260829-nn-bot-way-b.md` (the chronological log), then this.

## Where the work stands in one paragraph

For the first time in the programme, **training improves the bot, and a frozen gate says so**.
The chain of 09-01: the entropy bonus was acquitted twice (cluster and host pairs, the frozen
`gate1.py`); the credit path was measured (the planner's signal was 97.7 % the critic's opinion
because wood's whole value lands on the final turn); the fix — pay half of wood's value on
delivery, `wood_shaping 2 + end_wood 2` — was **CONFIRMED**: r22 won 31/29 of 144 on the locked
panel against 23/22, net +11 cells over the clone, the first trained artefact above its own
starting point. Overnight: the host replication reproduced the effect's size (+0.049, interval
touching zero exactly — the frozen letter calls that not confirmed; the pair of results carries
it); the 128-step rollout **alone** is not confirmed (+0.017); the environment's default split
0.5+3.5 is **no different** from 2+2 (−0.017) so **2+2 stays the recipe**; and **the stack**
(2+2 + rollout 128, `s22`) posts the campaign's best numbers — **29 → 33 of 144** at ages
1,500 → 2,500, **the first arm that rises with age instead of decaying** (its gain *over the
split alone* is not separable from noise: +0.007 [−0.021, +0.035]). The exploratory bench of
s22's final checkpoint (update 2,709) was landing as this was written — the number is in
`local_claude_1/nn-bot/results/entropy-gate-0901/bench-s22-locked-u2709.json` and in the report.

## The ledger (locked 144-cell panel, wins at updates 1,500 / 2,500; parity = 72)

clone **26** · E00 24/21 · E01 23/22 · h00 18/20 · h01 23/22 · hl128 21/29 · r0535 27/27 ·
hr22 28/31 · **r22 31/29** · **s22 29/33 (u2,709 exploratory: see the JSON)**. All verdict JSONs
and every bench: `local_claude_1/nn-bot/results/entropy-gate-0901/`; the plain-words verdicts:
`local_claude_1/nn-bot/GATE1-VERDICT-2026-09-01.md` (entropy) and `GATE-R22-VERDICT-2026-09-01.md`
(the reward path).

## In flight right now

- **`ppo-yt-s22L`** — the stack at a **doubled budget** (22,200,000 turn-steps = 5,420 updates),
  the one changed field (verified by config diff); operation `5f5afe7-4ade45ef-42e03e8-24076e87`;
  at 06:05Z it was **pending a cluster slot** (queued, not running — check first). ~4 h once
  running; a preemption restarts it from scratch and the salvage keeps every checkpoint
  (`mid-run-…` names under `//home/delivery_ml/research/tarstars/troll_farm/runs/ppo-yt-s22L/outputs`).
  **Its read is pre-registered as EXPLORATORY**: retrieve (`yt_ppo_launcher.py retrieve
  --run-name ppo-yt-s22L --output-dir yt_work/ppo/ppo-yt-s22L-output`, math-venv python), then
  `bench_ages.py` on the locked panel at ages 3000,3500,4000,4500,5000,5400. **Any promotion
  claim needs a fresh frozen gate written BEFORE those numbers are seen** — the card says so.
- The report (`docs/reports/2026-08-30-neural-network-line-progress.pdf`) is at its **seventh
  edition** (the campaign-ledger figure); rebuilt and pushed with this flush.

## The recipe for any new arm (hard-won, follow exactly)

1. Cluster: `yt_ppo_launcher.py prepare` with the FULL flag set of the arm it must match, then
   **diff `yt_work/ppo/<run>/yt_run_config.json` trainer_args against the control's** — expect
   only the intended fields + the run name. The launcher's silent defaults have bitten twice:
   `--opponent-weights` (defaults to a mixed pool; pin `'{"champion_exact":1}'`) and threads
   (follow `--cpu-limit`; prepare with 64). Then `start … --cpu-limit 32 --gpu-limit 1
   --pool-tree gpu_starfield_24g_cloud --pool research_gpu --job-time-limit-hours 6+ --async`.
2. Host: launch `train_ppo_full.py` with h01's start-event flags (read them from
   `/home/tarstars/nn-data/ppo-host-h01-0901/train.log` first line), 7 threads, nice 15, ≤14
   threads total on the host; verify the start event in `<out>/stderr.log` diffs from the
   control's in the intended fields only.
3. Benches: **always `--python /home/tarstars/prj/math_through_eml/.venv/bin/python`** (the
   system python has no torch); nice 19; the 48-cell scout panel is ±5 noise, the locked
   144-cell panel (`local_claude_1/nn-bot/locked-panel-seed1.jsonl`) is the judge; the clone's
   locked bench for the gate's non-inferiority term is `bench-clone-locked.json`.
   **Never start a second `bench_ages` driver for an age whose JSON does not exist yet** — it
   truncates the shared replays file (one corrupt replays file exists: `hr22-locked-u1500`; its
   JSON is fine). Launch missing ages with `--ages <that age>` only.
4. The gate: `gate1.py --treatment 1500=… 2500=… --control … --clone bench-clone-locked.json`.
   Its four outcome names are frozen from the entropy era (`ENTROPY_*`); the rule is
   variable-agnostic and printed with every verdict. Renaming the labels was offered to
   chatgpt_1 for ack — do not touch the file without it.

## Track C — the clean room (halted, waiting)

The package was reviewed by execution and corrected twice on 09-01 (my review: seven defects;
then the owner's restructuring into principles + evidence; then chatgpt_1's BLOCKED review — its
five findings applied the same day, its own "behind in score" rule refuted by the recordings
58/44). The corrected pin went back to chatgpt_1 (gate 7) and **the owner's own read still gates
the implementer**. `root_codex` (the owner's new agent) was ruled to **reproduce** the five
proofs, not edit the package — its ack was pending at the flush. The review instruments:
`local_claude_1/cleanroom-review/`; the reference executable now lives in `cleanroom/reference/`
(outside the package) and is handed over only after version 0's source hash is on the card.

## Open, not mine to do

- The owner runs chatgpt_1; it holds: the clean-room re-review (corrected pin `c0db18ab`+), the
  two-gate-verdicts handoff (`…two-gate-verdicts…`, which supersedes the earlier single-verdict
  one), and the question of when to stack levers / rename the gate labels.
- The owner's read of `cleanroom/package/`; the implementer's mechanism (recommendation:
  `fresh_1` in the package directory).
- root_codex's reproduction handoff, when it comes — verify the five numbers against the card.

## Standing constraints (verbatim force)

No platform action (the ladder is codex's); no deleting or moving data; no cloud spend beyond
the pool in use; never touch the owner's codex process or `~/.codex`; host training ≤14 threads
at low priority; consistent cluster budgets (step budget vs wall-clock); benches at nice 19; the
owner is not to be woken. The WIP rule: one open ack-required handoff per task — supersede or
wait; **push the pinned commit before committing the message** (park the message file if needed).
