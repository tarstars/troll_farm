---
schema_version: 2
type: policy
task_id: 20260823-narrate-real-game-telemetry
from: local_claude_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260823T065200Z-20260823-narrate-real-game-telemetry-update.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-23T06:52:00Z
---

- To: myself (the queue items)
- CC: claude_1, codex_1, user
- Task: 20260823-narrate-real-game-telemetry
- Requires acknowledgement: yes (self-addressed queue anchor; a bystander ack must not discharge it)

# CARDS — my two NARRATE items, self-addressed

Both are mine and neither may be discharged by a peer's receipt. Policy carrying the full charter:
`coordination/messages/local_claude_1/20260823T065100Z-20260823-narrate-real-game-telemetry-policy.md`.

DEFERRED: 20260823-narrate-real-game-telemetry — the AAAAA Arena block on instrumented swap R-1.
Five reads of one arm, no pairing, submitted through `cgauto/api_submit_once.py` with hash
verification and matured reads between, one cycle in flight, NOT through `night_runner.py`'s paired
decision tree. Owner-directed 2026-08-23; surfaced under the standing authorization because swap
R-1 has not passed its frozen gate and an instrumented bot can never be the champion. Restore
target after the run is unchanged: `cgauto/submissions/candidate-door1-pure-deletion.rs`, sha
`547fa706…`.
UNBLOCK-SIGNAL: gate G-P (instrument plays swap R-1's game, `MSG` stripped, byte-identical over the
34 fixtures) delivered by claude_1 AND reviewed by codex_1, plus my own published `MSG` length
figure. Both are required; neither alone starts a submission.

DEFERRED: 20260823-narrate-real-game-telemetry — the off-ladder `MSG` length probe. NOT BLOCKED;
mine to start and it is the next thing I do. `TestSession/play` via `cgauto/field_panel.py`, from
`project_host` which holds the session cookie (verified alive 2026-08-23T06:40Z), hard cap 12
games, stop on HTTP 422 or a degenerate result, never an Arena submission. Deliverables: the
largest surviving payload; the failure mode at the boundary (silent truncation / dropped command /
rejected turn / timeout, each implying a different safety margin); and whether two `MSG` tokens in
one turn are accepted.
UNBLOCK-SIGNAL: none.
