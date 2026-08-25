---
schema_version: 2
type: progress
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260820T202851Z-20260820-pair-selector-anti-benching-progress.md
created_utc: 2026-08-20T20:28:51Z
---

- To: claude_1
- CC: local_claude_1, codex_1, user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes

# cards: two open deferrals carried past wake #11

Self-addressed so my own next sweep surfaces them as queue items rather than as prose in a status
file. Neither is started; neither is authorized to be started by anyone else without saying so.

DEFERRED: measure, on the P1+P2 candidate, why the anchor unit's candidate list is empty on the
detector-quiet-but-stalled turns (cure-C OSC-013: the unit is offered no work at all on 170 of
187 window turns). This is a generator question, not a selector question, and it is the reason
three of four cure-C fixtures go detector-quiet without `progress_restored`. Do NOT extend P1/P2
to cover it before that measurement exists — a selector patch aimed at an unmeasured generator gap
is exactly the shape that produced the withdrawn `GENERATOR_GAP` claims of 2026-08-17.

DEFERRED: sentinel build (card 2), unchanged, still blocked on the single ruling I cannot make for
myself — may `actionable_set()` be extracted into `scripts/inbox_sweep.py` so `main()` and the
sentinel share ONE code path? Until that is ruled, a sentinel would be a second implementation of
the actionability predicate, and a sentinel that disagrees with the sweep is worse than none.
