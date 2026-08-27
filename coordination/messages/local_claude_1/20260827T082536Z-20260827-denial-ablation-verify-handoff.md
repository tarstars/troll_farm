---
schema_version: 2
type: handoff
task_id: 20260827-denial-ablation-verify
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260827T082536Z-20260827-denial-ablation-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: fffa3093b75fdf04600eb6f5c780503d089b74c8
artifact_paths: ["coordination/tasks/20260827-denial-ablation-verify.md", "local_claude_1/denial-ablation/make_denial_off.py", "local_claude_1/denial-ablation/fixtures_diff.py", "local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs.sha256", "cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs", "cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs.sha256", "readable/diffs/denial-bonus-off.diff", "readable/reports/candidate-champion-denial-off-v6-instrument.round-trip.json", "coordination/BOARD.md"]
created_utc: 2026-08-27T08:25:36Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260827-denial-ablation-verify
- Requires acknowledgement: yes — a charter (board row 0-4)

# handoff: 0-4 — re-run the denial-ablation build and its bed on `main`, and say whether the bytes on the ladder are the bytes the diff says

Card: `coordination/tasks/20260827-denial-ablation-verify.md`. Context in one line: the owner's one-variable experiment — the diagnostics champion (bot A) with its plum/lemon denial bonus removed — is on the ladder as submission `41202036` (08:21:51Z) for one hour; the owner predicts a drastic drop. I built it myself, so it has only agreed with itself. The ladder reading (~09:24Z) does not wait for you.

**What to run**, on a clean checkout of `main` at `fffa3093` or later:

1. `python3 local_claude_1/denial-ablation/make_denial_off.py` — it regenerates bot A's arm from the one source (`claude_1/cure3/cure3-keep-v6.rs`, flag line KEEP=false NARRATE=true), removes the four-line bonus hunk exactly once, compiles, compacts, round-trips. Expected: arm sha256 `321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f`, submission sha256 `0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c` (63,808 bytes). It overwrites the tracked files; `git status` must be clean afterwards.
2. `python3 local_claude_1/denial-ablation/fixtures_diff.py` — expected: plays 34/34, differs from the champion on 5/34 (OSC-008, -009, -010, -028, -029; first divergence turns 1, 5, 24, 5, 9), compacted == arm 34/34, deterministic 34/34, telemetry errors 0.
3. Read `readable/diffs/denial-bonus-off.diff` and say in one sentence whether the removed lines are the whole of the champion's targeted denial (the focus-species bonus in `chop_candidates`) — or name what else in the champion you would call denial.

**Return** one verdict message: REPRODUCED or NOT REPRODUCED, with the two hashes, the five counts, and your one sentence. No edits to the generator; if something differs, the first differing line and stop. Budget: one run, one message, today. No Arena, no builds of your own.
