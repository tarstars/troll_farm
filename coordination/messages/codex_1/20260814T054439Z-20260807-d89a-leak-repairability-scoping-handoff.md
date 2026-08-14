---
schema_version: 2
type: handoff
task_id: 20260807-d89a-leak-repairability-scoping
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260814T054439Z-20260807-d89a-leak-repairability-scoping-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 088d798eb009f5b7942e492ca3cfa880b4d71800
artifact_paths: ["codex_1/reviews/d89a-leak-repairability-second-review-2026-08-14.md"]
created_utc: 2026-08-14T05:44:39Z
---

# Handoff: dissent from structural closure of D89a

Plain-language result: D89a is unsafe and the evidence makes further investment unattractive,
but the committed record does not prove its leak structurally impossible to repair. My verdict is
**`UNRESOLVED`, strongly leaning `NOT_REPAIRABLE`**.

I independently reproduced the 256-task aggregate (`+82.863281` opponent score), the
`gold_adaptive` family result (`+208.78125`), the 70-task oracle core (`+0.828571` opponent,
`+129.957143` margin), and the disputed map calculation. The restoration's `+8.002` is an upper
confidence endpoint after reweighting the 15 contributing maps; it is not the frozen `<= +1`
task-weighted gate and is not a performance ceiling. D92's 5.4-times nominal denial dose is strong
negative evidence, but its own result says the trained worker was too late or low-leverage, so it
closes that exact policy rather than every timing/throttle repair.

Owner implication: it is defensible to stop funding Route B because the prior is poor and the
missing measurements are expensive. Record that economic decision honestly rather than claiming
structural proof. The conditional-banana-farm design remains an exposure limiter, not a measured
leak repair, and its banana-only abort may or may not observe the dominant harm because the
theft-versus-own-production split is still unavailable.

No implementation, new experiment, source edit, data mutation, TestSession, submission, or Arena
action was performed or authorized.
