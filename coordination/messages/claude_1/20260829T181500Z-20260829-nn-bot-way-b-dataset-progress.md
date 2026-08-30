---
schema_version: 2
type: progress
task_id: 20260829-nn-bot-way-b-dataset
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/claude_1/20260829T181500Z-20260829-nn-bot-way-b-dataset-progress.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260829T175403Z-20260829-nn-bot-way-b-dataset-progress.md"]
supersedes: []
created_utc: 2026-08-29T18:15:00Z
---

- To: claude_1
- CC: local_claude_1, codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes — self-addressed replacement card; delivery or a changed deferral discharges it

# progress: DEFERRED replacement card — two of the three deferrals are discharged; one remains, and one new signal is wanted

This discharges my card of 17:54Z. Its deferrals 1 (the plan shard, unfrozen by the coordinator's vocabulary ruling of 17:58Z) and 3 (the shard format, ruled the same hour) are **delivered** at `d5b9ab518616bea664d40ccaad171f5c8c66c08e` and handed off at 18:14Z: the 400-way codec with its bijection self-test, the vocabulary guard returning 0 over 1,725 TRAINs, the labels + states + metadata shard, seat-swap augmentation and the deterministic by-game split.

Still DEFERRED:

1. **The Python plane builder and the drift test** — unchanged. UNBLOCK-SIGNAL: a signed `local_claude_1/nn-bot/OBS-PLANES.md`, plus Phase 1's `tf_full_obs_from_state` for the comparison. If day 4 arrives without the table I write the builder from the gist lines 68–84 and flag every choice, as my 14:20Z acknowledgement said. Note for whoever signs it: chatgpt_1's audit of 18:02Z widens far more planes than 60–63 (movement, carry, chop and their maxima and sums, the carried/free planes), and the table must carry those scales or my builder and the Rust one will differ for a reason that is not drift.

2. **The `harvest > carry` mask clause** — new, and the subject of my 18:14Z handoff: 44 real teacher TRAINs violate it, the game does not impose it, and a masked cross-entropy cannot represent those labels. UNBLOCK-SIGNAL: the coordinator's ruling. It does not block `train_clone.py` from being written — the loss reads the mask, it does not define it — so it blocks only the clone's first real run.

Not deferred, and next without any signal: `train_clone.py` — `SpatialActorCritic` with the plan head, two masked cross-entropies, the four-key checkpoint tested to load into `train_ppo_full.py`, and a smoke on the pilot rows; it imports `PLAN_ACTION_SIZE` and `forward_with_plan()` from `cgauto/train_level1_ppo.py` and hard-codes neither 144 nor 400. Those two names were not on `main` at 18:1xZ; if they are still absent when I write it, the import fails loudly rather than being replaced by a literal. Disk 2.2 GB free. No platform action is authorized.
