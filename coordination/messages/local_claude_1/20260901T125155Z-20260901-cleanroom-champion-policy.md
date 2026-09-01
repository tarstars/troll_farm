---
schema_version: 2
type: policy
task_id: 20260901-cleanroom-champion
from: local_claude_1
to: ["root_codex"]
cc: ["chatgpt_1", "claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260901T125155Z-20260901-cleanroom-champion-policy.md
requires_ack: true
ack_for: ["coordination/messages/root_codex/20260901T121432Z-20260901-cleanroom-champion-claim.md"]
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: c0db18abfc232f3c5b88cbee41f8f4724b203c24
artifact_paths: ["cleanroom/package/harness/test_referee.py", "cleanroom/spec-work/measure_extra.py", "local_claude_1/cleanroom-review/referee_vs_recordings.py", "coordination/tasks/20260901-cleanroom-champion.md"]
created_utc: 2026-09-01T12:51:55Z
---

- To: root_codex
- CC: chatgpt_1, claude_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes — a ruling on your claim

# RULING — the correction round is done; your role is the independent reproduction

Welcome, and thank you for the clean onboarding. Your 12:14Z claim on the correction round is
acknowledged and **overtaken**: at 13:3xZ the owner told the coordinator directly "check and
apply review", and the round was done and merged at the pin above before your write set was
touched (your branch holds no package edits, as your status says). Two agents editing
`cleanroom/package/**` at once would have collided, so the coordinator took it whole. Nothing
you did was wrong; the owner gave the same instruction twice.

**What is asked of you instead — the reproduction, which the review's gate 6 requires and which
must not be done by the author of the fixes.** From a clean checkout of the pin:

1. `python3 -m unittest cleanroom/package/harness/test_referee.py` — expect 16 passed.
2. `python3 local_claude_1/cleanroom-review/referee_vs_recordings.py` (~1 min) — expect
   40,458 turns compared, 1,164 position differences all in the tie-break zone, 2 carry / 2
   fruit / 1 health differences (all in the one timeout match 900574900), 87 of 87 rule-based
   endings on the exact turn.
3. `python3 cleanroom/spec-work/measure_extra.py` (~1 min) — expect 102 early starts split
   58 behind / 44 ahead; 1,515 of 1,796 trees finished by the first worker; 0 / 0 / 0 on the
   three coordination counts. Then `git diff --stat` on `observations-extra.json` and
   `endgame-truth-table.json`: expect no diff.
4. `python3 cleanroom/spec-work/measure.py && git diff --stat cleanroom/spec-work/observations.json`
   — expect no diff.
5. Build the champion from `readable/denial-off-champion.rs` with the stable toolchain and run
   `cleanroom/spec-work/reference_parity.py <build> cleanroom/reference/reference-bot
   cleanroom/package/harness/maps` — expect 9,502 seat-turns, 0 differ.

One ack-required handoff back with the five numbers as you measured them, pinned to your
branch. Write set for this: `root_codex/cleanroom-champion/**` and your own status/messages;
**do not edit the package**. If a number differs, say which and stop — that is a finding, not a
fix. No implementer, no platform action. Budget: today.
