---
schema_version: 2
type: handoff
task_id: 20260826-candidate-3b-stuck-holder-release
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T144201Z-20260826-candidate-3b-stuck-holder-release-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 674afb1aca8b69ca7e4e5bebab56a0122cc1a56e
artifact_paths: ["coordination/tasks/20260826-candidate-3b-stuck-holder-release.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T14:42:01Z
---

- To: claude_1
- CC: codex_1, user, chatgpt_1
- Task: 20260826-candidate-3b-stuck-holder-release
- Requires acknowledgement: yes — new bounded candidate, board row D-4, owner "A"

# handoff: Candidate 3b — Candidate 3 as built plus your D-3 rule iii (holder on ≤ 2 cells for 20 turns with no work command → release, `rs=`); one build, one panel, pre-commitments in the card, stop pass or fail

Card: `coordination/tasks/20260826-candidate-3b-stuck-holder-release.md`. The owner chose A (build now, bounded) over waiting for Track T. Rule text: Candidate 3 unchanged + one release cause from `claude_1/cure3/m061-stale-goal-read-2026-08-26.md` §4 (iii); no margin, no cap, nothing else. **Pre-commitments, written in the card before the run:** containment; `xc = 0` on the six loop games; own-score outside `m061` ≥ +20; `m061` both seats within 10 of the champion (75 / 82); no Candidate-3-won game lost; `ka` max < 60; determinism; every changed game named. Any failure = CLOSED, obituary, no r2. codex_1 reproduces once; slot 2 only on a pass; diff `readable/diffs/candidate-3b-stuck-holder-release.diff` on `main` at the gate. **Build may start now; no panel number is read before codex_1's D3-G1 verdict on the read** — if the review breaks rule iii, stop. After 0-3a.
