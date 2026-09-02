---
schema_version: 2
type: handoff
task_id: 20260901-cleanroom-champion
from: local_claude_1
to: ["chatgpt_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260901T095136Z-20260901-cleanroom-champion-review-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260901T094349Z-20260901-cleanroom-champion-review-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 1286af7571c4f50bb10fe534fc2e9811bdd3a8b0
artifact_paths: ["cleanroom/package/CHAMPION-BEHAVIOUR.md", "cleanroom/package/README.md", "cleanroom/package/RULES.md", "cleanroom/package/CONSTRAINTS.md", "cleanroom/package/DOMAIN.md", "cleanroom/package/EXCLUDED.md", "cleanroom/package/harness/referee.py", "cleanroom/package/harness/README.md", "cleanroom/package/champion-purchases.json", "local_claude_1/cleanroom-review/review-2026-09-01.md", "coordination/tasks/20260901-cleanroom-champion.md"]
created_utc: 2026-09-01T09:51:36Z
---

- To: chatgpt_1
- CC: claude_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes — the owner's word: "send this new version to chatgpt_1 for review"

# HANDOFF — the adversarial cross-review of the clean-room package, third pin: the restructured behaviour document

This supersedes the 09:43Z charter (which superseded the 07:45Z one); same review, newer pin.
Two things happened since the package was delivered:

1. **The coordinator's review by execution** (`local_claude_1/cleanroom-review/review-2026-09-01.md`)
   found seven defects; at the owner's word they were fixed in the package (the substitute train
   rule that matched only 63/160; referee.py chopping same-turn seeds; the time rule = third
   strike; the harness baseline; the apple-farm line; a citation; numeric item codes) — see the
   review's "Fixes applied".
2. **The owner's read**: the behaviour document had too fine details for its purpose — a compact,
   logical reimplementation — and details like the seed order pushed the implementer toward
   copying habits. `CHAMPION-BEHAVIOUR.md` is now **Part I**: one page, ten principles, each
   with its reason and a mark ESSENTIAL / HABIT / NOT DETERMINED; **Part II**: the whole evidence
   base as an appendix (no number changed). The README says habits are not the specification.

## The review asked of you, adversarial as always

1. **Leakage**: anything in `CHAMPION-BEHAVIOUR.md`, `DOMAIN.md`, `RULES.md` or the harness
   that transmits our implementation's structure rather than observable behaviour — vocabulary,
   decomposition, suspiciously code-shaped rules, the stripped binary (the symbol-table and MSG
   channels are closed; find the third if it exists). **New question:** do the ESSENTIAL / HABIT
   marks in Part I leak design judgement that a spectator could not have made, or are they
   supported by the cited evidence?
2. **Citation integrity**: spot-check the observations in Part II against the recordings.
3. **Completeness for the purpose**: could a competent implementer reach the reference's
   strength from Part I alone? Are the ten principles the right ten — anything essential
   missing, anything marked ESSENTIAL that is really a habit, or the reverse?
4. **RULES.md as physics**: any referee semantics missing or wrong. Corrections go as findings
   to the coordinator, phrased as rules, not as code.

One ack-required handoff back, pinned to your branch, findings ranked. The card stays halted:
your review and the owner's own read gate the implementer. Budget: 1 day. No platform action.
