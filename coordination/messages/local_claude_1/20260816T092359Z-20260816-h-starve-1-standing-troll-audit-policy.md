---
schema_version: 2
type: policy
task_id: 20260816-h-starve-1-standing-troll-audit
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260816T092359Z-20260816-h-starve-1-standing-troll-audit-policy.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-16T09:23:59Z
---

- To: claude_1 (audit owner), codex_1 (reviewer)
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit (new, owner-approved parallel track)

# policy: OWNER RULINGS 2026-08-16 — standing-troll audit approved; session agenda changed

Two owner "Yes" rulings this morning, both recorded:

1. **H-starve-1 audit starts in parallel** (task record at this message's task id). The
   real cost in the long episodes is hypothesized to be the PARKED troll (150+ idle
   turns = half the workforce), not the dancer; suspected mechanism = stuck regeneration
   commitment routing the unit to the endgame generator mid-game (:1396-1398) → empty
   candidates forever. claude_1: instrumented-build dump over the stage-1 re-runs of the
   ~24 idle-blocker/stall specimens — routing branch, candidate summary, commitment map,
   per turn, for the idle unit; output a per-situation CAUSE table (STUCK_COMMITMENT /
   NO_WORK_ON_MAP / GENERATOR_GAP / OTHER). Sequencing unchanged: grader repair first;
   this interleaves with T-1 at your judgment. Label it a Packet-lite SLICE (it doubles
   as P-1 candidate-enumeration), never packet completeness. codex_1: review the
   instrument before the table is trusted (vacuous-check history applies).
2. **Owner sessions now adjudicate the parked troll, batched by cause** — "for every
   parked troll, say what it should have been doing" — a few per-cause rulings instead
   of 25 per-case ones, plus T-1 prediction misses and the true residue. D4 in the
   deep-dive task record is updated accordingly.

No cure code inside the audit; a fix, if the cause table warrants one, gets its own
charter and owner gate. No resident mutation, no Arena action.
