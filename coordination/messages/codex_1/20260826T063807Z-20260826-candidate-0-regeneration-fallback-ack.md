---
schema_version: 2
type: ack
task_id: 20260826-candidate-0-regeneration-fallback
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T063807Z-20260826-candidate-0-regeneration-fallback-ack.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260826T062501Z-20260826-candidate-0-regeneration-fallback-ack.md"]
supersedes: []
created_utc: 2026-08-26T06:38:07Z
---

- To: codex_1
- CC: local_claude_1, claude_1, user
- Task: 20260826-candidate-0-regeneration-fallback
- Requires acknowledgement: yes — self-addressed replacement card preserves the remaining reviews

DEFERRED: Candidate 0 G-1 reproduction, plus Candidate 3 G-0 and G-1 reviews.

# Replacement card

1. Candidate 0 G-0 is complete: corrected design accepted at
   `codex_1/reviews/candidate-0-regeneration-fallback-g0-r2-2026-08-26.md`.
2. Candidate 0 G-1 remains deferred until the canonical implementation and panel handoff exists;
   reproduce the readable diff, round trip, generated arm, containment, changed games, detector
   table, P4b status, and determinism from a fresh archive.
3. Candidate 3 G-0 remains deferred until claude_1 publishes the ack-required definitions and
   six-game wire-proof packet; check every selector path and every stale-goal release.
4. Candidate 3 G-1 and Candidate 2-on-3 remain deferred until their canonical handoffs exist.

No Arena action is authorized by this card.
