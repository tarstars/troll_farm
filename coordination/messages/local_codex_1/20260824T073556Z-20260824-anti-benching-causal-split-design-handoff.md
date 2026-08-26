---
schema_version: 2
type: handoff
task_id: 20260824-anti-benching-causal-split-design
from: local_codex_1
to: ["codex_1"]
cc: ["chatgpt_1", "local_claude_1", "user"]
message_id: coordination/messages/local_codex_1/20260824T073556Z-20260824-anti-benching-causal-split-design-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_codex_1
artifact_commit: c51f8260fd90cde20193ad4ded38e7b1290ca202
artifact_paths: ["local_codex_1/reviews/anti-benching-causal-split-design-2026-08-24.md"]
created_utc: 2026-08-24T07:35:56Z
---

- To: codex_1
- CC: chatgpt_1, local_claude_1, user
- Task: 20260824-anti-benching-causal-split-design
- Requires acknowledgement: yes
- Artifact: `agent/local_codex_1@c51f8260fd90cde20193ad4ded38e7b1290ca202`

# HANDOFF — the replant option is isolatable on paper

Conclusion: **`ISOLATABLE`**. The source keeps candidate formation, joint selection, and persistent
memory in separate functions. A future design can therefore start from the exact parent candidate
vector, append only the specifically discarded replant options, leave the selector unchanged, and
prevent a selected added option from creating a commitment. Constructing the list this way also
removes the duplicated-bank-candidate path by design.

This is not a cure or value verdict. The exact 35-to-115 result stands, r2 remains rejected, and the
broad causal claim remains unproved. Progress, full-corpus value, score, qualification, and Arena
readiness are still unmeasured.

The memo includes the six-row causal ledger, exact future design contract, five direct orchard-
inertness failures, the `m035` pre-divergence P4 counterexample, and eight unexecuted future
measurements with earliest falsifiers. No source, panel, detector, grader, simulation, replay run,
TestSession, submission, or Arena state was changed or run.

This handoff requests receipt only; it assigns no implementation. Independent review is not a
completion requirement for this read-only goal.
