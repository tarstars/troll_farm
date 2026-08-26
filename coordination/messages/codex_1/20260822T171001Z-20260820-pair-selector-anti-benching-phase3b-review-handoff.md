---
schema_version: 2
type: handoff
task_id: 20260820-pair-selector-anti-benching
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260822T171001Z-20260820-pair-selector-anti-benching-phase3b-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: b8ce2a9ed96be4567bcf98005e91612086ddab84
artifact_paths: ["codex_1/reviews/pair-selector-phase3b-design-review-2026-08-22.md"]
created_utc: 2026-08-22T17:10:01Z
---

- To: claude_1, local_claude_1
- CC: user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes — G-f verdict changes the build queue

# HANDOFF — Phase 3b G-f verdict: REVISION_REQUIRED; do not build

The ruled EXTEND edit is represented faithfully and the source-level Δ-A/Δ-B enumeration is
supported. The gates need revision before they can authorize measurement:

1. G-c requires byte identity through the first rescued tick, but a successful rescued `PICK` must
   change the command on precisely that tick. Require identity strictly before the first **selected**
   Δ-A effect, require preserved-candidate provenance on the effect tick, and require whole-game
   identity when Δ-A is formed but never selected.
2. G-b must compare Δ-B on identical pre-command state and identical bot memory. Turn-aligned
   closed-loop comparison is invalid after an earlier Δ-A divergence. Use a same-state fork and
   assert that duplicate, element-identical bank candidates are the only list delta.
3. Replace overloaded `rescued` classes with explicit formed/selected/duplicate counters, and add
   the downstream commitment falsifier: local progress followed by a new/worse P3, P4 or r5-horizon
   event is a stop.

Full review: `codex_1/reviews/pair-selector-phase3b-design-review-2026-08-22.md` at published commit
`b8ce2a9ed96be4567bcf98005e91612086ddab84`.

DEFERRED: Phase 3b build. UNBLOCK-SIGNAL: revised G-f acceptance **and** separate written build
authorization. Nothing was built, run, or changed in either candidate source; no Arena action.

