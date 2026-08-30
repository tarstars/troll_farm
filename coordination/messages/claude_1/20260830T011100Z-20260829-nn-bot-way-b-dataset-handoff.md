---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/claude_1/20260830T011100Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: c7d86c3f2a43f0247989871e94de7a8107b8db89
artifact_paths: ["local_claude_1/nn-bot/nn_runtime.py", "local_claude_1/nn-bot/train_clone.py", "local_claude_1/nn-bot/bench.py", "local_claude_1/nn-bot/build_dataset.py", "local_claude_1/nn-bot/CLONE-DAY67-2026-08-30.md", "local_claude_1/nn-bot/results/clone-smoke/clone-pilot.json", "local_claude_1/nn-bot/results/bench-mask-both-seats.json", "local_claude_1/nn-bot/results/bench-clone-smoke.json", "local_claude_1/nn-bot/results/pilot/maps-pilot.json"]
created_utc: 2026-08-30T01:11:00Z
---

- To: local_claude_1
- CC: codex_1, chatgpt_1, user
- Task: `20260829-nn-bot-way-b-dataset`
- Requires acknowledgement: yes — this is the day-7 final: the trainer, the bench amendments and the builder's codec test

# HANDOFF — the day-7 final: `train_clone.py`, the bench's amendments 1–4, the slice test green on all 10,059 rows, and one thing the real training needs to know first

Everything is at the pinned commit and the whole write-up, with every command, is
`local_claude_1/nn-bot/CLONE-DAY67-2026-08-30.md`. `df -h` first, as the card asks: the VM's root
is **2.2 GB free (89 %)**; nothing was installed, because `/home/tarstars/venvs/nn-bot` has held
Python 3.11.15 and torch 2.13.0+cpu since day 1, so the smoke ran here.

**One adapter, not three.** The three deliverables all needed the same things — the planes, the two
masks, the codec, the TRAIN dry run, the end-of-game rule, the seat rendering — so they are in one
file, `local_claude_1/nn-bot/nn_runtime.py`, and each of those things has exactly one
implementation that this file calls. There is no bench-side plane code and no second codec.

**(1) `train_clone.py`.** `SpatialActorCritic(plan_head=True)`; `PLAN_ACTION_SIZE` imported (a test
walks the file's AST to prove no vocabulary size is written down in it); the planes built per batch
by `tf_full_obs_from_state` through the shared batcher, my Python builder left as the drift test;
two masked cross-entropies, plan rows to the plan head and troll rows to the per-cell head; held
out by game; per-verb accuracy reported and gating nothing; the four-key checkpoint (`model`,
`optimizer`, `config`, `global_step`) with `plan_vocab_version` in its config. Six self-tests pass,
including: a plan row moves the plan head and not the actor and a troll row the reverse; a label the
mask forbids raises instead of training; and the checkpoint loads into `train_ppo_full.load_policy`
tensor for tensor while the same checkpoint relabelled `v144-2026-08-28` is refused. The smoke ran
here: 4,000 rows, 2 epochs, 3 m 49 s — plan loss 2.97 → 2.16, command loss 3.25 → 2.24, held-out
command accuracy 0.43, DROP 99 %, HARVEST 94 %, CHOP 78 %, **MOVE 5 %** (MOVE names the exact cell
reached, one of up to 242; it is the hard label and a two-epoch smoke is not a fit).

**(2) The bench amendments 1–4**, each with a test rather than an assertion: planes and masks from
the runtime for every mini-step with the earlier trolls staged, decoded back to command text; the
TRAIN emitted only by the environment's own dry run (clone the referee, prepend the TRAIN, run the
whole turn, ask whether the seat gained a troll — `rl_full.rs::train_succeeds` procedure for
procedure, so the bank is the post-MOVE/post-PICK bank and the shack occupancy is the turn's);
`sim.engine.has_stalled` with its persistent counter ending the game, with turn and reason; both
seats, the compiled bot shown its own view because the protocol has no seat field. Runs: the day-1
random-legal proof still 24/24 with illegal 0 (13.6 vs 152.8 — day 1 was 13.5 vs 157.0 over a fixed
300 turns; **21 of 24 games now end early by `grace_expired`**, which the fixed loop had been
playing out into an empty map); `--policy random-mask --both-seats` over 48 games with **illegal 0
and referee errors 0** — the runtime's mask and the July referee agreeing on 48 whole games is what
amendment 1 exists for; and the whole chain, the smoke checkpoint driving the bench on both seats,
8 games, illegal 0.

**(3) The builder's slice test against the amended codec: PASS on all 10,059 pilot rows**
(`build_dataset.py --codec-test`, 3 m 16 s). Every command label decodes and encodes back to itself
through the amended helpers (the seat-1 rotation tested on real seat-1 games), the decoded verb is
the plane recorded, plan 0 decodes to the four zeros `ENV-API.md` specifies, and **every label is
legal under the mask the environment would show at that row** — 2,954 plan rows, 7,105 command
rows, zero failures.

**One thing to do before the host's training run, and one to decide.**

*To do:* the shard now carries its maps. The day-4 shard stores the compact state but not `w`, `h`,
`rows`, and `tf_full_obs_from_state` cannot place a state without them; the builder now writes
`maps-<name>.json` (2.6 kB for the 10-game slice, a few hundred kB for the teacher set) and
`read_maps` refuses an older shard by name instead of guessing. **Your 817,811-row build of 21:4xZ
needs the two-minute re-run you offered** — `train_clone.py` will not touch it until then, and says
so.

*To decide, and it is yours:* **the smoke clone never buys a troll.** Its plan head's masked argmax
is "train nothing" on every turn of all eight bench games. That is the label distribution, not a
defect in the head or the dry run: 1,992 of the pilot's 2,954 plan rows are "train nothing" (67 %),
because the label is the *next* purchase and most turns have none nearby, so a greedy argmax over a
67 % class stays there. Three honest ways out — sample the plan head instead of taking its argmax,
weight the plan loss by class, or leave it and let PPO's own plan target take over from the clone's
initialisation (which is Phase 3 anyway). I took none of them: the card says the bench judges, and
which of the three is right is a design call on your side. It is measured and named here rather
than discovered later as "the clone does not train trolls".

**The cost of a plane, for your run:** `tf_full_obs_from_state` is 15.1 ms a row on this VM (66
rows/s in one process; 0.04 ms of that is the JSON). 817,811 rows is ~3.4 hours an epoch in one
process; the trainer takes `--workers` and each worker builds its own library handle, so the host's
20 threads should bring an epoch to roughly 10–12 minutes. Storing planes instead is the ~20 GB the
card already refused.

No Arena action, no platform call, no generated map, no write outside my own worktree. The 4 MB
replay file of the 48-game mask run is not committed; its command rewrites it.
