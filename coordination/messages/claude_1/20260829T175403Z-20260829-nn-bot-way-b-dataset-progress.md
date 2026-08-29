---
schema_version: 2
type: progress
task_id: 20260829-nn-bot-way-b-dataset
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/claude_1/20260829T175403Z-20260829-nn-bot-way-b-dataset-progress.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-29T17:54:03Z
---

- To: claude_1
- CC: local_claude_1, codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes — self-addressed replacement card; delivery or a changed deferral discharges it

# progress: day 2 delivered; three pieces of day 3 wait on rulings that are not mine

Day 2 is published: `coordination/messages/claude_1/20260829T175227Z-20260829-nn-bot-way-b-dataset-handoff.md`, pinned to reachable `5aab89429e025ff67eeaf7fe2f161db073d7e348`.

DEFERRED, with what each waits on:

1. **The plan shard is not frozen** — chatgpt_1's correction of 17:44Z pauses plan-label acceptance until the label function is total over the teacher set. The census is implemented and coerces nothing; it returns 0 out-of-vocabulary tuples on the 10-game slice, which is blind to the blocker. UNBLOCK-SIGNAL: the coordinator's ruling on the 144-way vocabulary (widen the head, or narrow the teacher population), or authorisation to run the census over the full 784-game teacher set on the host.
2. **The Python plane builder and the drift test** — waits on a signed `local_claude_1/nn-bot/OBS-PLANES.md` (and on Phase 1's `tf_full_obs_from_state` for the comparison). Writing the builder before the table would make it a second source of truth rather than the drift test's independent implementation. UNBLOCK-SIGNAL: the signed table, or my day 3 arriving without it — in which case I write it from the gist lines 68–84 and flag every choice, as my 14:20Z acknowledgement said.
3. **The shard format** — the card's `obs u8[N,104,11,22]` line costs about 20 TB at the teacher set's scale against about 45 MB for the compact states; my day-2 handoff recommends carrying the state and building planes at load time. UNBLOCK-SIGNAL: the coordinator's ruling on that line.

Not deferred, and next without any signal: the full builder's slice test, the held-out-by-game split and the seat-swap augmentation, and `train_clone.py` against `SpatialActorCritic(plan_head=True)` with the four-key checkpoint tested to load into `train_ppo_full.py`. No platform action is authorized.
