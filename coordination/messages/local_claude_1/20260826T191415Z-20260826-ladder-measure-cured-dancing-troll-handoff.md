---
schema_version: 2
type: handoff
task_id: 20260826-ladder-measure-cured-dancing-troll
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T191415Z-20260826-ladder-measure-cured-dancing-troll-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: afbfc16ea43b6ea5c2e82e3da6a596124bcc2e33
artifact_paths: ["coordination/tasks/20260826-ladder-measure-cured-dancing-troll.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T19:14:15Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260826-ladder-measure-cured-dancing-troll
- Requires acknowledgement: yes — new charter, board row L-1, owner "measure"

# handoff: L-1 — the cured dancing troll goes on the real ladder as a MEASUREMENT against the champion (A-B-B-A, both with v6 diagnostics, 8 reads each, annotated games); claude_1 builds bot B's submission file today, codex_1 checks it once, the coordinator runs the reads

The owner chose to measure Candidate 3 on the platform rather than close the line or build another rule. Card: `coordination/tasks/20260826-ladder-measure-cured-dancing-troll.md` — done / dead / budget / pre-committed reading are in it. **Not a promotion:** the champion of record stays; no KEEP/REVERT comes out of this run.

**claude_1 (today):** bot B = the Candidate 3 instrument arm (`claude_1/cure3/arm-instrument.rs`: keep rule ON, v6 diagnostics ON — the arm whose probe parity was 240/240) compacted exactly as 0-3a was, as `cgauto/submissions/candidate-3-keep-v6-instrument.rs` + sha256 + round-trip report; handoff pinned on your **rebased** branch (rebase first, publish after). **codex_1 (one check):** with the diagnostic line stripped, B's command streams on the 240 local games are identical to the parity-gated arm's; one line back. **Coordinator:** A (`41198581`) is up now; its first read is being taken; then B, read at maturity (~2 h), B, A, … 16 submissions, ledger `local_claude_1/ladder-measure/`. **codex_1 (after the collector brings the games):** the four annotation measures on both bots by one script. Row 0-3 (fixture generator) slips ~1.5 days; B's games count for its data gate too.
