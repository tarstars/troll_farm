---
schema_version: 2
type: handoff
task_id: 20260826-p4b-narrator-param
from: codex_1
to: ["claude_1"]
cc: ["local_claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T112323Z-20260826-p4b-narrator-param-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: f1be99dabcc16060289e1fa21cc88cc55909ada5
artifact_paths: ["codex_1/p4b/p4b_gate.py", "codex_1/p4b/test_p4b_gate.py", "codex_1/p4b/reproduce_v5.py", "codex_1/p4b/verify_v5_counts.py", "codex_1/p4b/narrator-param-report-2026-08-26.md"]
created_utc: 2026-08-26T11:23:23Z
---

- To: claude_1
- CC: local_claude_1, user
- Task: 20260826-p4b-narrator-param
- Requires acknowledgement: yes — G-1 review requested

# P4b narrator parameter delivered for G-1 review

The parked-troll gate now requires an explicit `v4`, `v5`, `v6`, or `none` dialect per arm. It
delegates applicable grammar to the mutually-refusing narrator decoder; a wrong dialect is counted
as a hard error. An explicitly narrator-less arm is scanned in full and returns
`NOT_APPLICABLE` with a reason, never `NOT_EVALUABLE`, a silent zero, or `PASS`.

Fresh Candidate 2 v5 panels reproduce the accepted row exactly in every compared count field:
**16 instrument versus 27 rule-off failed units**, 7,137 versus 8,839 all-available windows, 277
versus 268 blind unit lives, and `PASS` with no added unit key. The verifier returns true for both
arms. The unchanged v4 path remains 25 versus 27 and `PASS`. Two real narrator-less 240-game
archives return `NOT_APPLICABLE`; deliberately declaring the same files v5 produces exactly
172,364 decoder errors per arm. Ten tests pass, including the r5 v6 `/k=2` decoder contract.

Review boundary: P4b consumes only the decoded `available` target and resolver branch; it does not
duplicate v6's complete grammar. The Candidate 3 build's `narrate6` module remains responsible for
the full required-field census and mutual refusal, so a v4 archive under `v6` fails through that
decoder and cannot fall back inside P4b.

Reproduction commands, hashes, complete counts, and the one remaining integration boundary are in
`codex_1/p4b/narrator-param-report-2026-08-26.md`. No bot source, arm, champion/resident, resolver,
raw game archive, bulk root, or Arena state was changed.
