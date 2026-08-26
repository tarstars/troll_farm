---
schema_version: 2
type: policy
task_id: 20260825-dance-cure-candidate-1-hold
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260825T075500Z-20260825-dance-cure-candidate-1-hold-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: bfdbfccdd1b4e5e3685c610d6032937ba50a869f
artifact_paths: ["local_claude_1/dance-cure-proposal-2026-08-24.md", "local_claude_1/dance-mechanism-map-2026-08-25.md"]
created_utc: 2026-08-25T07:55:00Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes — a new build charter; G-0 is codex_1's first, before any code

# policy: CHARTERED — Candidate 1: a blocked troll holds (≤ 2 turns) instead of stepping backwards, with the resolver branch printed per turn (NARRATE v4). Owner: "do it".

Card: `coordination/tasks/20260825-dance-cure-candidate-1-hold.md` — read it whole. The mechanism
it targets is read from the champion's code (`local_claude_1/dance-mechanism-map-2026-08-25.md`)
and matched by 75 of 77 real episodes being forward/back along the path with the teammate on the
forward step in 32 of 34 (`local_claude_1/dance-cure-proposal-2026-08-24.md`, §1).

## The change, in one paragraph

In `resolve_move_conflicts_with_priority_and_forbidden` (`:720-772` of `547fa706…`): when a
mover's landing is blocked and every free neighbour is **farther** from the target than the cell it
stands on, emit `WAIT` and count it — up to **two** turns per block — instead of taking the
regressive detour; a lateral or improving detour is taken as today; after two holds the old
behaviour returns for a turn so nothing can park. One new field on `YamoBot`
(`blocked_turns`), reset whenever the landing is free or the unit does something other than MOVE.
No swap, no re-targeting, no score change.

## Order

1. **codex_1 — G-0 first, before any code:** rule `DESIGN_ACCEPTED` / `REVISION_REQUIRED` on the
   predicate, `W = 2`, the reset rule, the v4 grammar (`r=P|L|H|R|W|N`, `b=<n>`, refusal both ways
   with v3) and the parity plan. Publish it `requires_ack: true` toward claude_1.
2. **claude_1 — build three arms from one source and a flag:** instrument (hold + v4), candidate
   (hold, no `MSG`), rule-off (v4, hold disabled). Transplant the `MSG` hunk from
   `claude_1/narrate3/instrument-swap-r1-narrate-v3.rs` **without the swap rule** (retired). G-1 as
   the card lists: rule-off byte-identical in play on the 34 fixtures + the 240 panel; rule-on
   panel with blocking not above the base's 35, P3 clean, P4 not above base, every changed game
   named; the 11 reproduced fixtures with `progress_restored`; the positive control, the poison
   arm, the v4 decode controls. Hand off with the full commit and paths; codex_1 re-runs from a
   fresh archive.
3. **local_claude_1 — G-2 read and G-3 block** (pre-authorized by the owner for this task, surfaced
   before each starts), then the owner rules KEEP or not.

## What this is not

Not Candidate 2 (swap or route-around for the blocker that never moves — the owner's ruling is
open), not Candidate 3 (score smoothing), not chatgpt_1's pair-level step check (step 4, queued
after this read). No change to candidate generation, `compatible`, or `select`. Anti-benching r2
stays rejected; the swap cure stays retired.

Deferrals: none.
