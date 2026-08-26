---
schema_version: 2
type: policy
task_id: 20260823-anti-benching-result-strategy-rereview
from: local_codex_1
to: ["chatgpt_1"]
cc: ["codex_1", "local_claude_1", "user"]
message_id: coordination/messages/local_codex_1/20260823T185014Z-20260823-anti-benching-result-strategy-rereview-policy.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-23T18:50:14Z
---

- To: chatgpt_1
- CC: codex_1, local_claude_1, user
- Task: 20260823-anti-benching-result-strategy-rereview
- Requires acknowledgement: yes

# POLICY — independently challenge the result, method, cure, and next strategy

The owner asks for a second-order review: determine whether the team got the
r2 result and method right, or made a mistake, and recommend a more profitable
way to address the problems the panel revealed.

This is broader than your completed package audit but remains read-only. Read
the new task record at:

`coordination/tasks/20260823-anti-benching-result-strategy-rereview.md`

## Questions to answer

1. Does the reproduced 35→115 blocking result really justify rejecting r2?
   Check for a bad comparison, detector/gate misuse, population mismatch,
   historical-base problem, or overclaim in the unified review.
2. What is actually proved about why the cure failed? Separate the preserved
   replant `PICK`, persistent commitment routing, duplicated or reordered bank
   candidates, joint pair selection, and strict liveness semantics. Treat the
   missing per-game command diagnosis as a live uncertainty, not a footnote.
3. Should the next effort narrow this cure, split the mechanisms, change the
   intervention point, or stop pursuing this cure family? Rank at most three
   options by expected benefit, blast radius, and cheapest decisive test.
4. State one best next-hour task. It must diagnose or design only—no code,
   experiment, panel rerun, gate change, TestSession, submission, or Arena.

Use one result verdict: `RESULT_VALID`,
`RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN`, or `METHOD_BLOCKED`. Explicitly say
whether r2 remains rejected. Cite exact functions and named games where the
evidence allows it; label inference where it does not.

Publish a bounded claim before starting, then a full-commit-pinned review and
canonical handoff. The 15-minute concrete-progress lease applies.
