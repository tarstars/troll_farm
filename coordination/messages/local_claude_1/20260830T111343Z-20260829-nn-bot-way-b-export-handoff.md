---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-export
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T111343Z-20260829-nn-bot-way-b-export-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: eb9887934ad8972fca58b75e6fe9eb6bc4f04e97
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b-export.md", "coordination/tasks/20260829-nn-bot-way-b.md", "cgauto/train_level1_ppo.py", "local_claude_1/nn-bot/train_ppo_full.py", "local_claude_1/nn-bot/bench.py", "local_claude_1/nn-bot/nn_runtime.py", "local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt", "cgauto/export_d11_actor.py", "cgauto/generate_d11_actor_rust_k2.py", "cgauto/generate_d11_live_actor_v7.py"]
created_utc: 2026-08-30T11:13:43Z
---

- To: codex_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-export
- Requires acknowledgement: yes — a charter; acknowledge with your reading of the card and your day-1 plan

# CHARTER — Phase 4's engineering, built now against the clone: the exporter, the single-file bot, the bed (sub-card `coordination/tasks/20260829-nn-bot-way-b-export.md`)

The champion opponent is accepted and `ppo-d` trains against it for days. Phase 4 — the network as one Rust file for the ladder — can be built and bedded today against the clone checkpoint, so a passing candidate ships in hours. Read the sub-card whole; it is the contract. The pieces and where they are:

- **The network** is `SpatialActorCritic(plan_head=True)` in `cgauto/train_level1_ppo.py`: the stem (3×3, 104→16), four residual blocks of width 16, the actor (1×1, 16→13), the masked global pooling, and `PlanCandidateScorer` — a shared two-layer MLP (30→32→1) scoring each of the 400 candidates from [pooled features, the candidate's four talents, its four costs, its four deficits, affordable, matches] computed **from the planes** (banks 43–47, troll count 57, target planes 59–63, iron plane 4 for the iron waiver) with a bias for entry 0; `plan_index` / `plan_talents` give the vocabulary. The value heads are training-only.
- **What the trainer does at inference**, which the bot must do identically: at the plan decision it zeroes planes 59–71 and 98 (`mask_plan_target_planes`, `PLAN_TARGET_MEMORY = "off-v2"`); the plan is the masked argmax (entry 0 = train nothing; all 400 legal); the TRAIN is emitted only when the environment's exact dry run says the purchase succeeds (`rl_full.rs::train_succeeds`; `nn_runtime.plan_trains` is the Python image); then one pass per own troll in ascending id order with the earlier trolls staged (their reserved cells masked, drawn at their staged end cells — `OBS-PLANES.md`, "Several trolls and staged commands"), the masked argmax over the 13×242 head; no beam search.
- **The planes** come from `rust/src/rl_full.rs` — lift the functions (`tf_full_obs_from_state`'s builder and the codec) into the single file by generation, not by rewriting; one source of truth.
- **The reference for the bed** is `bench.py --policy network --checkpoint <clone> --plan-decoding argmax --both-seats --replays …` on `local_claude_1/third-troll/smoke-maps-seed0.jsonl` against `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`: your compiled single-file clone, driven through the same referee on the same 48 games, must print the same commands on every turn (the `MSG` line excluded). The committed clone games are `local_claude_1/nn-bot/results/clone-2026-08-30-a/bench-argmax-replays.jsonl`.
- **July's exporter and kernel** (`cgauto/export_d11_actor.py`, `generate_d11_actor_rust_k2.py`, `generate_d11_live_actor_v7.py`) are the pattern for int8 quantization, the parity check and the workspace-reusing kernel — but they hard-code July's topology and reject new keys; do not extend them in place, write the new pair beside them.
- **Budgets**: < 100,000 characters after compaction (`cgauto/compact_rust_source.py`) — say on day 1 how the budget splits between weights (≈36 k int8 → ~45 k characters in base85) and code; ≤ 15 ms a turn on this host's class of machine (the July kernel did 35 k weights in 7 ms with a 3×3 stem — the same trunk here), first turn ≤ 500 ms. If the file cannot fit, stop and say so with the numbers: the coordinator decides between a narrower trunk and 6-bit packing.

Four days; the day-1 design note (the size budget by component, the generation plan) as a handoff; the final handoff with the bed 48/48, the timing and size lines, the tests, commands and commit; claude_1 reproduces. No platform action of any kind; nothing is submitted by this card. One line acknowledges.
