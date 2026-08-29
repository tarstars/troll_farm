---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260829T134500Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: d20ca3561d248d4b4f2d1f63bfb03cdba0ff8f90
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b-dataset.md", "coordination/tasks/20260829-nn-bot-way-b.md", "local_claude_1/nn-bot/ANALYSIS-2026-08-29.md", "local_claude_1/nn-bot/maps-slice-1000.jsonl", "local_claude_1/reconstructions/fits/player_games.json", "local_claude_1/nn-bot/replays-slice-10/index.json", "local_claude_1/reconstructions/sources/delineate-gist.github.com-2026-05-25.md"]
created_utc: 2026-08-29T13:45:00Z
---

- To: claude_1
- CC: codex_1, user, chatgpt_1
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes — a charter; acknowledge with your reading of both cards and your first-day plan

# CHARTER — Phase 2 of the neural-network bot: the dataset, the bench, the clone's trainer (board row N-2; sub-card `coordination/tasks/20260829-nn-bot-way-b-dataset.md`, parent `20260829-nn-bot-way-b.md`)

The owner opened the line today ("1) open line 2) B 3) I'll check"): a bot whose commands come from a network over the board — clone the top four's moves first, then PPO. You build **what the clone is trained on, the bench that judges it, and the trainer**. Read the parent card whole first — its "Fixed design" (the dataset, the bench, the network) is the specification; the sub-card is your contract (done, dead, budget); this message orders the work and points at the code. codex_1 builds the environment in parallel (Phase 1) and sends `local_claude_1/nn-bot/OBS-PLANES.md` on day 1 — you build your plane builder from that table, independently, so the two implementations can be checked against each other.

**Order of work (7 days, two messages).**
1. **Day 1 — the runtime on the VM and the bench's plumbing.** Python 3.11 + CPU PyTorch via `uv` on the VM (its network is free; report versions and the command). Then the bench `local_claude_1/nn-bot/bench.py`: one seat played by a Python policy, the other by a compiled single-file bot, over the July Python referee harness (`claude_1/pipeline/fuzz_panel.py:828–868` `FuzzReferee`; `claude_1/banana-restoration-r2/semantic_harness.py:97–118` compiles a candidate with `rustc --edition=2021 -O -Awarnings -`; `regression_tests.py:822–848` drives it over pipes). Prove it with a **random-legal policy** against the champion's file `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` on the 24 maps of `local_claude_1/third-troll/smoke-maps-seed0.jsonl` (the map records `smoke.py` uses). Output per game: own/opponent score, win, every TRAIN (talents, turn), timeouts, illegal commands, loops (a troll on one cell 30 turns with cargo it could deposit); a summary table; the games saved as replays the owner can read turn by turn (the `local_claude_1/third-troll/dance_read.py` style). The random policy will lose every game — the point is the pipeline.
2. **Day 2 — the dataset pilot, sent to me as a handoff:** `local_claude_1/nn-bot/build_dataset.py` run on the 10 games of `local_claude_1/nn-bot/replays-slice-10/` (raw replays of the top four; `index.json` names them). The exact reconstruction is `local_claude_1/reconstructions/fits/reconstruct.py` (`snapshot()` schema at 136–145; both seats' commands via `Reconstructor.commands(t)`; re-point `decision_tables.py:32` `GAMES_INDEX` to `local_claude_1/reconstructions/fits/player_games.json`, now in the repo; the `train` field in `fits/tables/<player>_turns.jsonl.gz` is the plan label's source, or recompute it). Rows exactly as the parent card says: one plan row per turn per seat (label = the talents of the next TRAIN that player actually issues, 0 if none), one row per own troll (label = the flat 13×242 index of its command; a MOVE label is the cell the troll **actually reached** in the next snapshot). The pilot handoff prints five sample rows with their planes summarized, the label histogram per verb, the row counts, and the bytes per 1,000 rows — I check the labels before you build at scale.
3. **Days 3–6 — the full builder, the drift test, the trainer.** The builder sharded `.npz` (`obs u8[N,104,11,22]`, `mask`/`plan_mask`, `label i64`, `meta`), seat-swap augmentation by the 180° rotation, held-out split by game, Bubaptik's latest version tagged; **the full build runs on the host** (the 7.1 GB raw corpus lives only there) — you deliver the script and its test on the slice, I run it. The drift test: your Python plane builder against codex_1's `tf_full_obs_from_state` on 1,000 states, byte-equal, once Phase 1 lands (write the test now, run it then). The trainer `local_claude_1/nn-bot/train_clone.py`: `SpatialActorCritic` from `cgauto/train_level1_ppo.py:140` with the 144-way plan head as an **opt-in constructor flag** (the exporter `cgauto/export_d11_actor.py:19–57` compares state-dict keys against the default constructor — July's checkpoints must keep exporting), two masked cross-entropies (`pretrain_level1_bc.py:47–58` is the pattern), Adam, cosine schedule, held-out by game, per-verb accuracy reported **and never used as a gate**, the checkpoint in the four-key format (`model, optimizer, config, evaluation`). A smoke of the trainer on the pilot rows on the VM (minutes).
4. **Day 7 — the final handoff:** the scripts, the tests, the pilot numbers, the bench run with the random policy, the commands and the commit for every number. codex_1 reproduces the bench and the pilot before I accept.

**Rules.** No platform action of any kind (codex — the owner's own run outside this repository — holds the ladder; the bench is local). No generated maps anywhere. Do not copy the raw corpus to the VM (the host's network is metered; the 10-game slice is the VM's data). Stop at the first real blocker and write; do not widen the card. Pinned at the sub-cards' commit above.
