---
schema_version: 2
type: handoff
task_id: 20260826-p4b-narrator-param
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260826T134113Z-20260826-p4b-narrator-param-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260826T133202Z-20260826-candidate-3-keep-your-goal-policy.md", "coordination/messages/codex_1/20260826T132718Z-20260826-p4b-pipeline-integration-deferred.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: cafb020405b71811ce78255e733010fda2c6ed94
artifact_paths: ["claude_1/pipeline/p4b_gate.py", "claude_1/pipeline/test_p4b_gate.py", "claude_1/pipeline/fuzz_panel.py", "codex_1/p4b/pipeline-integration-report-2026-08-26.md"]
created_utc: 2026-08-26T13:41:13Z
---

- To: claude_1, local_claude_1
- CC: user
- Task: 20260826-p4b-narrator-param
- Requires acknowledgement: yes — Claude owns the one budgeted re-review
- cross-task: the Candidate 3 closure policy assigned this D-2 last mile, and the pipeline-integration card held the same work until that assignment and write-set transfer arrived

# HANDOFF — the parked-troll gate now runs behind the panel API for v4, v5, v6, or no narrator

The coordinator's ruling 4 is delivered, and my deferred card is discharged by delivery. The
panel keeps its existing row-taking `evaluate_rows` API and gains an explicit
`--p4b-dialect v4|v5|v6|none` parameter. v4 remains the default. A narrator-less arm reports
`NOT_APPLICABLE`; declaring `none` while NARRATE payloads exist fails closed.

## Differential proof

- `python3 -m unittest claude_1/pipeline/test_p4b_gate.py` — 10 passed.
- `python3 -m unittest codex_1/p4b/test_p4b_gate.py` — 11 passed.
- Candidate 3's real v6 instrument archive: 240 games, `READY`, **0 decode errors**, 15 episodes
  on 15 units.
- Candidate 2's regenerated v5 instrument and rule-off archives: both accepted count projections
  match `c12-idle-with-work.json` exactly.

Claude: please perform the one re-review against those two frozen proofs. Candidate 3 remains
closed; this instrument delivery does not reopen it. No Arena or bot-source action occurred.
