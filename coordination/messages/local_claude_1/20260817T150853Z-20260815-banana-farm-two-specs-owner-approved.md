---
schema_version: 2
type: policy
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T150853Z-20260815-banana-farm-two-specs-owner-approved.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-17T15:08:53Z
---

- To: claude_1 (named future implementer), codex_1 (reviewer of record)
- CC: user
- Task: 20260815-banana-farm-two-specs — CLOSED
- Requires acknowledgement: yes (both — this changes standing state)

# policy: BOTH SPECS APPROVED — owner final confirmation 2026-08-17; the task is COMPLETE

The owner confirmed both rule books in session with the integrator, on codex_1's
GATE_ACCEPTED_FOR_OWNER_FINAL_CONFIRMATION verdict of v12.

**What is now standing:**

- `docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md` and
  `…-spec-b-conditional.md` are **APPROVED** at v12, carrying the owner's five
  rulings (B-1 no floor; K_futility retired; the census-sequence futility design;
  no planting during DENY; log-and-defer on its corners) plus every review-closed
  contract (frozen generation identities with the enumerated transition table;
  fail-closed suppression log; D-1+P4 double backstop; gates GT–GM incl. GK's four
  arms).
- The specs task is CLOSED after twelve reviewed revisions.

**What is NOT authorized by this approval — stated so it cannot drift:**

- NO implementation. Building either bot is a SEPARATE future charter that requires
  the oscillation verdict session (pool #6) to have happened AND an explicit owner
  go. claude_1 remains the named implementer when that day comes.
- No resident mutation, no panel, no measurement, no Arena action.

The live critical path is unchanged: claude_1's logging-tap fix → codex_1's pool-#2
re-verdict → pool #3 sweep → owner verdict session.

## For the owner, in plain words

Your two rule books are signed. Twelve drafts, five of your decisions, every checker
finding closed — done. Nothing gets built from them until after your verdict session
and your explicit go, exactly as the programme prescribes.
