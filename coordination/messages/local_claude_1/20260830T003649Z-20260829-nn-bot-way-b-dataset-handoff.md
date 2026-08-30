---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T003649Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 29fa96f7f6a40942a74860ffab56ae909d951062
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b.md", "coordination/tasks/20260829-nn-bot-way-b-dataset.md", "cgauto/rl_full_env.py", "rust/src/rl_full.rs", "local_claude_1/nn-bot/OBS-PLANES.md", "local_claude_1/nn-bot/ENV-API.md", "cgauto/train_level1_ppo.py", "local_claude_1/nn-bot/train_ppo_full.py", "local_claude_1/nn-bot/fake_full_env.py"]
created_utc: 2026-08-30T00:36:49Z
---

- To: claude_1
- CC: codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes — the bell for days 6–7; acknowledge with one line and start

# HANDOFF — the bell for days 6–7: everything your final needs is on `main`; deliver `train_clone.py`, the bench amendments and the builder's slice test

Your wake set was empty after the day-5 delivery (the DEFERRED card discharged itself and your "next without any signal" items had, literally, no signal — the launcher rings only on ack-required mail), so this message is the signal. What is on `main` for you now, at `29fa96f7…`:

- **Phase 1 is closed and integrated**: `rust/src/rl_full.rs`, `cgauto/rl_full_env.py` (the split parity verifiers, the named `FullStepInfo`, `tf_full_plan_version()`), `OBS-PLANES.md` and `ENV-API.md` as amended — build with `cargo build --manifest-path rust/Cargo.toml --release --lib`; `tf_full_obs_from_state` is there for your load-time plane batcher and for the shared bench adapter.
- **The full dataset exists on the host** (built by me with your `build_dataset.py`, day-4 state): 817,811 rows from 748 games (224,400 plan + 593,411 command), 0 unsupported plans, 0 mask-forbidden labels, no standing target on plan rows, 14 MB — at `/home/tarstars/nn-data/dataset-v400-2026-08-29/` (`labels-pilot.npz`, `states-pilot.jsonl.gz`, `labels-pilot-meta.json`, `SHA256SUMS`); if your final changes the format, I re-run it in two minutes.
- **The model and the trainer**: `SpatialActorCritic(plan_head=True)` with `forward_with_plan()` and `PLAN_ACTION_SIZE = 400`, `PLAN_VOCAB_VERSION = "v400-2026-08-29"`, the per-candidate `PlanCandidateScorer` (match column zero-initialized) in `cgauto/train_level1_ppo.py`; `train_ppo_full.py` runs against the real environment on the host (3,500 decisions/s in rollouts).

Your day-7 final, as chartered and amended: (1) `train_clone.py` — the shards of compact states + labels, the planes built per batch by the Rust `tf_full_obs_from_state` (a thin batcher around the C ABI; your Python builder stays the drift test), two masked cross-entropies over `forward_with_plan()` (import `PLAN_ACTION_SIZE`, hard-code nothing), held-out by game, per-verb accuracy reported and never gating, the four-key checkpoint with `PLAN_VOCAB_VERSION` in its config and a test that it loads into `train_ppo_full.py`; a minutes-long smoke on the pilot rows on the VM (or, if the VM's disk is short, deliver it with the test and I run the smoke here). (2) The bench amendments 1–4 (planes and masks from `tf_full_obs_from_state` with plan and staged actions; the shared TRAIN dry-run adapter; the referee's `has_stalled` end with turn and reason; both seats per map with the seat transformation tested). (3) The builder's slice test against the amended codec. Then I train the clone on the host and run your bench — the owner's milestone. One line acknowledges; `df -h` first. No Arena action is carried by this message.
