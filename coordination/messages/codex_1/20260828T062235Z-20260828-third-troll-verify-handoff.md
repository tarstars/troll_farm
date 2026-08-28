---
schema_version: 2
type: handoff
task_id: 20260828-third-troll-verify
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/codex_1/20260828T062235Z-20260828-third-troll-verify-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260828T061320Z-20260828-third-troll-verify-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: ac4960ae7ed114f6bb167a48f026c2bf5e96c386
artifact_paths: ["codex_1/third-troll/reproduction-2026-08-28.md"]
created_utc: 2026-08-28T06:22:35Z
---

- To: local_claude_1
- CC: claude_1, user, chatgpt_1
- Task: 20260828-third-troll-verify
- Requires acknowledgement: yes

# 0-7 verdict: REPRODUCED

The third-troll build and all four independent gates reproduce. The 2/3/0/3 arm SHA-256 is `30bf84226f26b82b8121fcf7605bc28104dff2daf0ed4595d90fcc1b53b2fbbe`; its compacted submission is `89493fa0d68e1dea1079c35ca4b0a8ed9b36273ccb25f5663d51c1a9e48ded33` (65,342 bytes). The 2/2/0/2 variant submission is `684104f136f93ac620447dadf95e9d491b467ac68eef8e4180f8081b114c00bf` (65,342 bytes). Both diffs are +123 / -29, and regeneration left generated tracked files byte-identical.

The bed plays 34/34, differs from the champion on 27/34, is deterministic 34/34, and has compacted == arm 34/34 with zero telemetry errors. Arm and champion each train in 1/34; third-troll, wrong-specification and more-than-three lists are all empty. The selection-only change is identical on 58/58 games.

The smoke run matches: mechanics okay 23/24, with only expected bare map `c84154d29ea19fbc`; a third troll in 5/24, median turn 158, median funding 144 turns, and 19 `bill never paid by turn 200` cases. Own-score delta is +497 over all 24 and +82 on the five third-troll maps.

Diff verdict: nothing in `readable/diffs/third-troll.diff` can train a fourth troll, train the third before the second, train it in the last 100 turns, or leave a troll without a command list.

Evidence: `codex_1/third-troll/reproduction-2026-08-28.md` at pushed commit `ac4960ae7ed114f6bb167a48f026c2bf5e96c386`. No queue removal is required. No Arena action was taken.
