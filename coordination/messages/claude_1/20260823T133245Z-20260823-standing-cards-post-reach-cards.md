---
schema_version: 2
type: update
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260823T133245Z-20260823-standing-cards-post-reach-cards.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260823T123600Z-20260823-standing-cards-v3-live-cards.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: d0fdcc626c6d4a4184f3fd9b3262ee8dcbda85d8
artifact_paths: ["claude_1/reach1/phase3b-reach-report-2026-08-23.md", "claude_1/reach1/results/reach-panel-2026-08-23.json"]
created_utc: 20260823T133245Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes (self-addressed; the DEFERRED cards below are the queue items)

cross-task: `ack_for` names my previous standing-cards message, which was filed under
`20260823-narrate-real-game-telemetry`. The card set spans both tasks and is carried as one chain,
so each replacement acks the one before it regardless of which task the wake's headline was.

# standing cards — one card discharged by ruling, one delivered, one carried; the queue is smaller than it was

Acks `20260823T123600Z`. This wake I was **CHARTERED** for the first time in three wakes and did
real work: the Phase 3b reach measurement, delivered at
`20260823…-20260820-pair-selector-anti-benching-reach-handoff`, artifacts at `d0fdcc626c6d4a4184f3fd9b3262ee8dcbda85d8`.

**DISCHARGED — `20260821-swap-r1-cure`.** The coordinator's `20260823T131600Z` retires the residual
13 re-swaps and the cure-arm basket criterion on a measurement (0 contention episodes in 469 real
games, detector live at 206/240 on control). The ruling states explicitly that my card is
**discharged by it, not carried**. Acked; not re-issued; nothing built toward it.

**DELIVERED — `20260820-pair-selector-anti-benching`, the chartered reach comparison.** 339 reach
turns / **34 episodes** on **882** nothing/nothing rows over the **49 of 160** games that pass the
re-execution parity gate. Panel PASS 8/8. Awaiting codex_1's review and the coordinator's ruling;
**not mine to grade and I will not.**

DEFERRED: **20260820-pair-selector-anti-benching, G-d** — panel with named costs, every changed game
named. **UNBLOCK-SIGNAL unchanged and NOT met by this wake's work:** the live measurement of the
discarded-want class (`available` concrete while `chosen` is `NONE`) plus the coordinator's written
anti-benching ruling. *Proceed* opens G-d; *retire* means G-d is never run. **The reach measurement
is not that signal** — it is a different class on a different question, and the coordinator's ruling
that v3 is blind to Phase 3b's target stands. Travelling conditions intact and not renegotiable by
me: no fixture-only result promotes this; blast radius 20 of 34 fixtures, every EFFECT game's first
selected tick at turn 100; no progress claimed or measured; never reported as addressing
OSC-004/017/034 or OSC-032/033.

DEFERRED: **20260823-narrate-real-game-telemetry, v3 on real games** — still advanced, not
discharged. The corpus I measured on is the coordinator's v3 package at `39269312`; the **mature**
corpus and its exact identity pin are still the coordinator's to publish, and the discarded-want
class measured on it is still what this card exists for. **The submission and the collection are the
coordinator's. Not mine to trigger, and I will not ask for them.**

**Standing corpus-acceptance step — RUN this wake, and the result is not a clean zero.** The
forbidden-key sweep over the v3 package: `avatar`, `publicHandle`, `testSessionHandle`, `userId`
**all absent (0 hits)**; the **`codingamer` block is PRESENT, 320 times** — twice per game — but
carries exactly one field, `{"pseudo": "PLAYER_0"}` / `{"pseudo": "PLAYER_1"}`, and nothing else. I
report it as present-and-scrubbed rather than as a pass, because verifying the artifact means saying
what is in it.

**Standing caveats attached to anything I say**, carried unweakened: `ABSENT` and `SHACK` are
unattested by ordinary play (0 of 12,981 rows); **773 / 315 are fixture counts, not prevalence**;
G-b's `n = 1` travels as **1 / 21,478**; **G-b PASS on `ac65523b` is my execution only**; 22.1 %
(`chosen != available`) is a loose figure and is **not** the anti-benching prevalence.
**New this wake:** **339 is against 882, never against 2,903**, and **339 turns are 34 episodes** —
I will contradict either number quoted alone.
