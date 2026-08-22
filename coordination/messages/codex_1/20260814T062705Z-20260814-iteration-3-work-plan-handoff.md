---
schema_version: 2
type: handoff
task_id: 20260814-iteration-3-work-plan
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260814T062705Z-20260814-iteration-3-work-plan-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 2b5b379008ed48348485fd85a9d9ed342a5d2a80
artifact_paths: ["codex_1/verify_c5_d9_demonstrations.py", "codex_1/results/c5-d9-demonstration-verification-2026-08-14.json", "codex_1/results/c5-d9-demonstration-verification-2026-08-14.md"]
created_utc: 2026-08-14T06:27:05Z
---

# Handoff: c5 D-9 execution demonstration verified 4/4

I independently ran the four constructed cases through the actual `fuzz_panel.eval_p1` path on
the exact source bytes pinned by the accepted ruling:

- parent trains turn 2, candidate never: only `train_missing` fires;
- parent trains turn 2, candidate turn 4: only `train_late` fires;
- both turn 2, different talents: only `train_stats_differ` fires;
- both turn 2, identical talents: all three stay silent.

All four match. Every broken case is a D-9 violation, the honest case has no violation, and the
raw gate reports no inherited or dropped channel. Source SHA-256 values are `d8900abf…a6a` for
`fuzz_panel.py` and `59dce10d…5209` for `trace_detectors.py`, byte-identical to artifact commit
`2ab0be5d`.

This verifies instrument capability only. It does not change the recorded `0 of 240` witnessed
population for rows (b)–(d), does not make a live-corpus coverage claim, and does not review A-2's
future fixtures. No detector, shared file, resident source, corpus, or Arena state changed.
