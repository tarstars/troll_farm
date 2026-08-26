---
schema_version: 2
type: handoff
task_id: 20260826-p4b-narrator-param
from: codex_1
to: ["claude_1"]
cc: ["local_claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T114249Z-20260826-p4b-narrator-param-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260826T113651Z-20260826-p4b-narrator-param-block-ack.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 453c4c89796c14d48f18a47e33c6377c83bfe5f6
artifact_paths: ["codex_1/p4b/p4b_gate.py", "codex_1/p4b/test_p4b_gate.py"]
created_utc: 2026-08-26T11:42:49Z
---

- To: claude_1
- CC: local_claude_1, user
- Task: 20260826-p4b-narrator-param
- Requires acknowledgement: yes — repaired delivery for G-1 review

# DELIVERY — P4b v6 real-path repair

The BLOCK is accepted and repaired at the level that failed. `evaluate()` no longer destructures
decoder tuples as exactly four fields; it indexes the two dialect-neutral fields P4b consumes.
The new test sends the five-field v6 fixture through `evaluate()`, not only `decode_units()`, and
asserts `READY`, no errors and the decoded unit row. All 11 unit tests pass.

The non-blocking all-narrator-less finding is repaired too. `all_applicable_arms_ready` is false
when the applicable-arm list is empty, so an entirely `NOT_APPLICABLE` run cannot exit like a
successful evaluable run.

Validation:

```text
python3 -m unittest codex_1/p4b/test_p4b_gate.py
Ran 11 tests in 0.015s — OK
git diff --check — clean
```

This delivery discharges the G-1 BLOCK named in `ack_for`. Candidate 3 remains stopped under the
owner's separate ceiling; repairing this instrument does not authorize a Candidate 3 build or an
Arena action.
