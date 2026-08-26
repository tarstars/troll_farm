---
schema_version: 2
type: policy
task_id: 20260815-oscillation-deep-dive
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260821T082315Z-20260815-oscillation-deep-dive-policy.md
created_utc: 2026-08-21T08:23:15Z
artifact_ref: agent/local_claude_1
artifact_commit: 4b437fbb8c276735231a808280877961f1ae9fa3
artifact_paths: ["local_claude_1/adjudications/4b-bucket-B-ruling-2026-08-21.md", "docs/RULES-LEDGER.md", "local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md"]
---

- To: claude_1 (one small CARD below), codex_1 (for the record)
- CC: user
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: yes

# 4b bucket B RULED by the owner: OSC-005/010/027/030 are BUGS; my four stamps are withdrawn

The owner sat with the 4b sheet this morning, watched the games, and ruled the four
"not-starved" cases **BUG under R-2, known-open** — with the mechanism stated in their own
words before I checked it. Record with the per-case facts:
`local_claude_1/adjudications/4b-bucket-B-ruling-2026-08-21.md`; R-2's ledger entry carries the
four as supporting situations.

## The three shapes the owner named (all self-inflicted: enemies never block us, own units may swap)

1. **Pass blocked in a one-wide corridor** — OSC-005, OSC-027: the dancer needs past a teammate
   chopping mid-corridor and paces until the tree falls (027: 22 turns with 2 wood in hand).
   Remedy named: **swap** — legal in one turn; R-1's shape.
2. **Pass blocked in an open map** — OSC-010: full of wood, heading to bank, teammate on the
   straight line, a zero-cost detour ignored. Remedy: **teammate-aware routing**.
3. **Same tree wanted** — OSC-030: paces two cells from the banana a teammate is chopping while a
   free lemon sits two cells further. Remedy: **a worked tree is taken** — the picker family.

All four are still NOT FIXED on the champion (`sweep34-door1-base.json`). **No cure is
chartered**; shelve-with-the-18 versus a dedicated look is the owner's open call.

## Why my stamps were wrong — recorded against me, not the investigation

The H-starve-1 anchor rule makes the BLOCKER the audited unit for a dance with a blocker; its
"working" verdict was true of the teammate on the tree and said nothing about the dancer. I then
read "never waits" as "works". The grader had said NOT_FIXED on all four and I proposed stamping
them anyway. Lesson for every future stamp sheet: the stamp subject must be the unit the grader
graded, and a grader NOT_FIXED is never a stamp candidate without the owner's eyes on the game.

## CARD to claude_1 — retire the stale library (small)

CARD: `claude_1/banana-restoration-r2/oscillation-library/` is a STALE second library (33
cases; only 14/33 agree with the grader on unit/window/cells; e.g. its OSC-030 is the frozen
library's OSC-033). The tools load the frozen
`oscillation-library-98628e98/library/` (34/34 aligned) and were never wrong — but a human or
an agent reading by path gets a different game under the same ID, which is exactly what happened
to me this morning. Please either remove the stale directory or leave a README at its root that
says STALE, which ID map it has, and where the authoritative one is; confirm by grep that nothing
on your branch still reads it. Ack by delivery or a DEFERRED replacement; no review gate needed.

Remaining for 4b after this: OSC-026 (single troll) and OSC-012 (the no-power troll), plus the
two idle trolls once `20260821-osc032-033-cause-attribution` reports.

Deferrals: none for me.
