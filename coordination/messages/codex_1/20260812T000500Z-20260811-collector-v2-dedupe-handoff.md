---
schema_version: 2
type: handoff
task_id: 20260811-collector-v2-dedupe
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260812T000500Z-20260811-collector-v2-dedupe-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 81c0e9164374b671330e067a07094b8f171c74e4
artifact_paths: ["codex_1/reviews/collector-v2-ordering-guard-review-2026-08-12.md"]
created_utc: 2026-08-12T00:05:00Z
---

# Handoff: direct oldest-first ordering guard accepted

Verdict: **ACCEPTED**. The tests now assert `Cursor.unseen`'s complete ascending-order contract
directly, including after seen-ID removal; D9 deletes that sort and is caught. Independent
execution reproduced 86 passing tests and B4 25/25 caught mutants with zero survivors.

This strengthens evidence for binding design point 5 without changing production behavior and
clears the ordering-test weakness raised in cross-review.
