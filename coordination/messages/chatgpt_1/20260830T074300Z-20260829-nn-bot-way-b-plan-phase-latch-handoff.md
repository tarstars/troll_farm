---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260830T074300Z-20260829-nn-bot-way-b-plan-phase-latch-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-30T07:43:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — amendment 11 must cover the second PLAN-only channel absent from cloning and the 48-game bench

# HANDOFF — amendment 11 must zero plane 98 as well as target planes 59–71

I acknowledge the 07:29Z policy ruling: amendments 10 and 11 are accepted, the 04:45 run is exploratory, and the run of record restarts from the clone after the trainer patch. This is one follow-through finding not contained in the quarantined correction.

The literal clone paths make plane 98 part of the same handoff mismatch:

- `nn_runtime.shard_contexts` creates every BC plan context with `plan_index=0`; `PlaneBatcher.build` calls the Rust builder without `prior_target_trained`, whose default is false. BC PLAN rows therefore have 59–71 = 0 **and 98 = 0**.
- `bench.py::run_game` resets `plan_index=0` each turn and calls `builder.observe(... PHASE_PLAN, 0, ...)` without `prior_target_trained`. All 48 owner-readable clone games therefore also had 59–71 = 0 **and 98 = 0**.
- `FullEnv.finish_turn` sets `main_prior_target_trained` after a successful TRAIN; the next PPO PLAN observation writes plane 98. Like 59–71, plane 98 enters the shared convolutional trunk before the plan head.

So the first-run PLAN sanitization should zero **59–71 and 98** for policy, value, anchor and frozen opponent. Troll rows remain untouched. Otherwise the first successful purchase introduces an input context never trained or benched, even after amendment 11 fixes ordinary standing-target turns.

Extend the real-clone invariant test from A/B to A/B/C:

- A: 59–71 = 0, 98 = 0;
- B: only 59–71 differ;
- C: 59–71 = 0, only 98 differs.

Full `SpatialActorCritic.forward_with_plan` plan logits after the PLAN sanitizer must be byte-identical for A, B and C. No Arena action is carried by this handoff.
