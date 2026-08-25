---
schema_version: 2
type: policy
task_id: 20260825-dance-cure-candidate-1-hold
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260825T104301Z-20260825-dance-cure-candidate-1-hold-policy.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-25T10:43:01Z
---

- To: codex_1 (replacement queue card)
- CC: local_claude_1, claude_1, user
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes — discharge when the grading handoff is checked or superseded

# DEFERRED replacement card — execute-check the G-2 grading package after handoff

G-1 is closed and the coordinator has ordered the v4 instrument read. codex_1 has no work before
the coordinator collects the mature games and claude_1 grades the resulting package.

On claude_1's grading handoff, perform exactly one execution check from a fresh archive and verify
the collected package identity against the shipping manifest. Do not rerun G-1. Check the grading
against the coordinator's `20260825T103500Z` policy, including the read's own scope-active share,
v4 branch counts, progress after holds, reconstructed v3 regressive-detour baseline, D-3, F7,
idle-with-work by troll, and all named acceptance and kill rules.

UNBLOCK-SIGNAL: a valid claude_1 handoff of the G-2 grading package, or an ack-required coordinator
ruling that cancels or changes this assignment. Do not reissue this card on a bare wake.

Write set while deferred: none. codex_1 has no Arena authority for this task. No submission,
TestSession, sealed-data access, resident mutation, or speculative grading before the handoff.
