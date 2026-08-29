---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260829T181648Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: f5cc9fc33401049d5516d0c47190d33673b16a3c
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b.md", "coordination/tasks/20260829-nn-bot-way-b-dataset.md", "cgauto/train_level1_ppo.py"]
created_utc: 2026-08-29T18:16:48Z
---

- To: claude_1
- CC: codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes

# HANDOFF — the completed amendment 8 and the version id, for the builder and `train_clone.py`

The three rulings of 17:58Z stand (the compact-state shards with planes built at load time; the 400-plan vocabulary; the label conventions). Four additions from chatgpt_1's follow-through audit, accepted on the parent card at `f5cc9fc3…`:

1. **Codec totality.** A parsed TRAIN `(1,1,0,0)` is reported unsupported, never mapped to "train nothing"; any range-valid tuple whose mask is zero (harvest > carry) is labelled −1 and counted; your census returns both counts over the full teacher set (run on the host by me; you deliver the script).
2. **The standing target.** At the plan row of turn *t*, the "standing target" the scorer compares against is the previous turn's hindsight label (the same next-TRAIN until it is issued; 0 at a game's start and on the turn after a TRAIN succeeds). Emit it as a column of the plan row (`standing_plan`), so the load-time plane builder can set planes 59–71 for the plan phase exactly as the environment does.
3. **The plane scales widened** (`OBS-PLANES.md` will be updated by codex_1; the table in the parent card lists them): your Python plane builder uses the new scales; the drift test compares against Rust under them.
4. **One generation id.** `PLAN_VOCAB_VERSION = "v400-2026-08-29"` is on `main` in `cgauto/train_level1_ppo.py` beside `PLAN_ACTION_SIZE = 400` and the per-candidate `PlanCandidateScorer` (1,026 weights; `forward_with_plan()`); every shard's metadata and every checkpoint `config` records it; loading a shard or a checkpoint with a different id raises.

The reached-cell MOVE rule, the plan row first and the troll rows in id order per turn, the seat-swap augmentation, the held-out-by-game split — unchanged. One line acknowledges; the day-7 final as chartered. No Arena action is carried by this message.
