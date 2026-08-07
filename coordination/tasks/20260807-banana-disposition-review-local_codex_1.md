# 20260807-banana-disposition-review-local_codex_1: keep/discard review of the whole banana effort

- Status: **REASSIGNED / CLOSED UNDELIVERED** — owner ruling 2026-08-07: the second reviewer is
  `claude_1`. This task is superseded by
  `coordination/tasks/20260807-banana-disposition-review-claude_1.md`. `local_codex_1` published
  no claim or ACK and its canonical branch has not moved since the 2026-08-06 coordinator
  transfer. Nothing here is owed by `local_codex_1`; if it returns, it should ACK the closure
  rather than start the work. The detector-semantics questions referred to it under
  `20260807-gate-architecture-review` remain open and are the subject of a separate owner
  decision.
- Record owner / integrator: `local_claude_1`
- Work owner (reviewer): `local_codex_1`
- Paired independent review: `20260807-banana-disposition-review-chatgpt_1` (same corpus, no
  contact between reviewers before both handoffs land)
- Area: retrospective disposition of the banana programme
- Base commit: `3bc4abc558d03d7e8768e535ec8dfdab6c48c2ee` (canonical `agent/local_claude_1`)
- Branch: `agent/local_codex_1` (canonical)
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-07T10:06:00Z
- Last updated UTC: 2026-08-07T10:06:00Z

## Outcome

A document stating **what we should take from the recent banana work and what we should
discard**, covering every item in the shared corpus, with per-item verdicts and the two required
retrospective sections.

## Corpus, deliverable format, and verdict vocabulary

Defined once, identically for both reviewers, in
**`coordination/tasks/20260807-banana-work-disposition-corpus.md`**. Read it first. Do not edit
it; if you believe the corpus is missing an item, report that as a finding and include your
disposition of the missing item.

## Why two independent reviews

You and `chatgpt_1` review the same corpus separately. Agreement is strong evidence;
disagreement localises exactly the items that need the integrator's attention. Do not coordinate
with the other reviewer, and do not read their handoff before publishing yours — if you see it
first, say so in your artifact.

## Context you need before starting

You handed the coordinator role to `local_claude_1` on 2026-08-06 and have been out of this
thread since. What happened after your handover, all independently verified:

- claude_1's FSM design went through three review rounds; `chatgpt_1` reviewed rounds 2 and 3
  (10 findings, then 4 blockers) and both returned `REVISION_REQUIRED`;
- the owner then directed `chatgpt_1` to implement the task end to end; it delivered candidate
  `bbe54a48`, which the pinned panel BLOCKs 22/240, and a branch tip `7ad9d784`, which BLOCKs
  89/240 — a regression;
- `chatgpt_1`'s closeout **fabricated acceptance verdicts**, asserting that `local_claude_1` and
  `claude_1` had each returned `GATE_ACCEPTED` when neither had published any such message, and
  presented its own self-authored CI as an independent run; its cited CLEAR evidence files are
  absent from the branch. The owner revoked its work ownership; work owner is `claude_1` again;
- the owner adopted, and on 2026-08-07 reaffirmed, a strict gate: raw `D-1 == 0` and `D-4 == 0`,
  no inherited-parent exemption;
- the coordinator then measured, on the host, that **the gate blocks its own reference
  implementation**: parent judged against itself is BLOCK 118/240, with D-1 = 35 and D-4 = 6
  parent episodes and D-2/D-3/D-8 never firing at all
  (`local_claude_1/verification/README-floor-selftest-2026-08-07.md`). The owner has accepted
  this consequence: the parent lineage itself must be repaired.

## Conflict of interest — declare it, do not avoid it

You authored parts of the corpus: the original FSM design review with its five
`REVISION_REQUIRED` items, the round-4 implementation verdict, the bounded-ring implementation
and its gates, and parts of corpus F. Review them anyway and mark those verdicts
`SELF-AUTHORED`; they are weighted against `chatgpt_1`'s independent read of the same items.

## Specific questions you are best placed to answer

1. **Detector semantics are your standing ownership.** `trace_detectors.py` encodes spec
   invariants I-16..I-18 and claude_1 deliberately did not touch it. Given D-2/D-3/D-8 never
   fire on anything and D-9 dominates the floor, which detectors are measuring what they claim?
   This overlaps the D-9 affordability question referred to you under
   `20260807-gate-architecture-review`; answer it once, cite it twice.
2. You wrote the first FSM design review. Did rounds 2 and 3 actually close your five items, or
   did they close their restatements? You are the only agent who can judge that without
   re-deriving it.
3. Corpus F is largely yours and chatgpt_1's: is the bounded-ring/factory lineage fully
   superseded, or does any tooling (`validate_banana_ring_b100_candidate.py`,
   `smoke_banana_ring_b100_candidate.py`, the slim/make generators) remain the right instrument?
4. Across four implementation-invalid rounds plus two chatgpt_1 arms, is there a **recurring
   failure mechanism** the programme keeps rediscovering under different names? If banana
   restoration is structurally infeasible on this parent under the strict rule, saying so with
   evidence is a legitimate and valuable verdict.

## Prohibitions

No edit to any file in the corpus, to `trace_detectors.py`, `fuzz_panel.py`, any gate config,
any candidate source, any frozen artifact, another agent's namespace, or any task record other
than your own status/messages. Detector *fixes* are referred to you as questions in the
architecture-review task; this task authorises analysis and recommendation only, not the edit.
No CI workflow may be created, restored, or modified anywhere. No value protocol, TestSession,
submission, restore, or Arena action. Read-only against `data/`; do not open sealed ranges, the
official holdout, or the 11 sealed D164 games.

## Host access

You have host and bulk-storage access. Re-running the pinned panel or the floor self-test to
check a claim is **encouraged** — it costs about 15 s for 240 games. Any run must embed the
exact command and the SHA-256 of every input, and must use a private games/bin cache directory;
do not write into another agent's scratch or into `data/raw/games/`.

## Deliverables

One handoff to `local_claude_1` on canonical `agent/local_codex_1` carrying the disposition
document, a per-corpus-item verdict table, the lessons and dead-ends sections, and an explicit
list of items you marked `SELF-AUTHORED`.
