---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T114128Z-20260815-banana-farm-two-specs-v9-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260817T111725Z-20260815-banana-farm-two-specs-v8-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: d83a66f2828585cd9869cb4398dd6c8a70367b3f
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md"]
created_utc: 2026-08-17T11:41:28Z
---

- To: codex_1 (review v9 — v8's round is superseded before it began), claude_1 (informational)
- CC: user
- Task: 20260815-banana-farm-two-specs (v9 — FIFTH owner ruling)
- Requires acknowledgement: yes (codex_1)

# handoff: Spec v9 — the suppression-corner question is RULED (log-and-defer); the C1/C2/C3 analysis is written into the spec

Supersedes the v8 handoff (whose named review surface — the commitment pipeline
under suppression — was taken up directly with the owner instead). Artifact
`d83a66f2`; shared skeleton §3–§8 re-verified byte-identical.

## The session's joint code-walk, now in the spec

The owner challenged my claim that planting during DENY was reachable; we walked the
code together. Result, written into §4: planting during DENY is reachable ONLY
through the conversion pipeline's two PICK sites —

- main planner :1177, score **7500** (beats every chop's ≤~2900): needs turn ≥ 100,
  board ≤ 2 plants, WINNING (else the endgame router bypasses main);
- endgame planner :1287, score **7000 after turn 250** (~83 before): reachable when
  losing on a ≤ 4-plant board, or ANY TIME after turn 250.

Three corners: C1 (mid-game winning bare board), C2 (mid-game losing bare-ish),
C3 (late game, any board). The suppressed pipeline can strand a committed troll —
manufactured dance (8000−distance hops) or manufactured park (all-WAIT at 0).

## The ruling (fifth of the session)

**Owner: the corners are rare — LOG AND DEFER.** No prevention machinery (no PICK
suppression, no commitment clearing). Every suppression event is logged with full
context (turn, plant count, score sign, banked fruits, suppressed command, the
unit's next 5 emitted commands); the implementation's mandatory 240-game panel is
the empirical backstop (a manufactured dance = de-novo D-1 = panel failure); the
question RETURNS to the owner if logs show real occurrences. My "C3 is common"
claim is recorded in the spec as a mechanism argument that this log will test — not
assumed.

## For codex_1

v9's review surfaces: the corner analysis as written (check the score and routing
claims against :1177, :1287, :1396–1403 — they are now spec text and must be
exact); whether the log-event schema is sufficient to adjudicate the deferred
question later; and whether the panel-backstop claim (manufactured dance ⇒ de-novo
D-1) holds for the park variant too (all-WAIT strands would surface as P4
liveness, not D-1 — if you agree, the spec should name P4 as the second backstop;
flag it and I will add the one line).

## For the owner, in plain words

Your decision is in the books: we don't build defenses against the three rare
corners now — we count them. Every time the no-planting rule actually blocks
something, the bot writes down the full story of that moment, and the big
240-game safety test would catch any real damage. If the counts ever show it
matters, the question comes back to you with data instead of speculation.

## Boundaries

No implementation, no resident mutation, no Arena action. After codex_1's pass the
books return to the owner for final confirmation only.
