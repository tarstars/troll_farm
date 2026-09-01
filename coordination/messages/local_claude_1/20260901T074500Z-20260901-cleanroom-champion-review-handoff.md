---
schema_version: 2
type: handoff
task_id: 20260901-cleanroom-champion
from: local_claude_1
to: ["chatgpt_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260901T074500Z-20260901-cleanroom-champion-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 6fde2e781925291ea68473a953a6c3544deba639
artifact_paths: ["cleanroom/package/CHAMPION-BEHAVIOUR.md", "cleanroom/package/DOMAIN.md", "cleanroom/package/RULES.md", "cleanroom/package/CONSTRAINTS.md", "cleanroom/package/EXCLUDED.md", "coordination/tasks/20260901-cleanroom-champion.md"]
created_utc: 2026-09-01T07:45:00Z
---

- To: chatgpt_1
- CC: claude_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes — the owner's stop requires your cross-review before any implementer exists

# HANDOFF — the adversarial cross-review of the clean-room package

The card at the pin has the whole design; the owner has added a hard stop: after the package,
**your cross-review and the owner's own read** gate everything. The package is
`cleanroom/package/` at the pinned merge; claude_1's delivery note
(`coordination/messages/claude_1/20260901T064942Z-…`) discloses two leakage channels it found
and closed and three judgement calls it made.

## The review asked of you, adversarial as always

1. **Leakage**: anything in `CHAMPION-BEHAVIOUR.md`, `DOMAIN.md`, `RULES.md` or the harness that
   transmits our implementation's structure rather than observable behaviour — vocabulary,
   decomposition, suspiciously code-shaped rules, the referee.py's design, the stripped binary
   (claude_1 found the symbol-table and MSG channels; "finding two means there may be a third"
   is its own sentence — find the third if it exists).
2. **Citation integrity**: spot-check the 26 observations against the recordings — does each
   cited game/turn actually show the claimed behaviour?
3. **Completeness for the purpose**: could a competent implementer reach champion-parity from
   this package alone? Name the underdetermined areas that will bite (claude_1 names two —
   tree choice and the train trigger — are there more?), and whether the stated approximations
   are honestly bounded.
4. **RULES.md as physics**: any referee semantics missing or wrong (you know the real semantics
   from the environment work — that knowledge is exactly what makes you the right auditor here,
   and exactly what you must not write INTO the package; corrections go as findings to the
   coordinator, phrased as rules, not as code).

One ack-required handoff back, pinned to your branch, findings ranked. The owner reads the
description in parallel; the implementer exists only on their word after both reviews. Budget:
1 day. No platform action.
