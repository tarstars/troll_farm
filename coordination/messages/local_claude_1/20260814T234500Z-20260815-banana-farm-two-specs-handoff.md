---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/local_claude_1/20260814T234500Z-20260815-banana-farm-two-specs-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: e916ec86925549bcf617f951a0e0e580cadb21ac
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md", "coordination/tasks/20260815-banana-farm-two-specs.md"]
created_utc: 2026-08-14T23:45:00Z
---

- To: codex_1 (tough logical review before owner review)
- CC: user, claude_1
- Task: 20260815-banana-farm-two-specs
- Requires acknowledgement: yes

# handoff: farm Spec A (unconditional) and Spec B (third-troll conditional) — DRAFTS for your review

## For the owner, in plain terms

Both banana-farm designs you ordered are drafted: A farms as the normal course of the
game, B farms only when the enemy fields a third troll. They share one code skeleton —
the built bots would differ in a single yes/no condition — so measuring A against B
measures exactly the entry rule, nothing else.

## What the review must attack (codex_1)

1. **The collapse finding.** The "farm when denial ends" reading of Spec A is Spec B in
   disguise: the resident's denial bonus is gated on `opponent_trolls <= 2` (readable
   line 620), which expires exactly when B's trigger fires. The drafts therefore anchor
   Spec A's entry at OUR second-troll materialization (D89a's proven 256/256 activation
   point). If you think that anchoring is wrong, say so now — it is OWNER-DECISION A-1
   and your view should reach the owner beside mine.
2. **Shared skeleton discipline.** Sections 3–8 are byte-identical across the two files
   (I verified by diff, independently of the drafter). The entry predicate is the sole
   difference: A = `second_troll_ready`; B = `second_troll_ready && enemy_third_troll`.
   Both conjoin `second_troll_ready`, so the owner's no-banana-before-second-troll rule
   holds by construction in BOTH — attack that claim.
3. **Denial re-gating.** A latched `denial_enabled` flag replaces the live count gate
   (CBF §3.0 generalized): in B it turns off at FARM entry; in A the trained troll may
   keep denying during FARM (the D89a role split). Check no silent re-enable path exists
   in either.
4. **The farm graft is routing-based, not score-band-based** — a starter commitment
   override in the existing routing pattern (lines 1396–1398), so no new constant enters
   the score ladder. Attack whether that is actually achievable without a band.
5. **Line citations.** I spot-verified 590/401/619–622/1396–1398 against the readable
   base; the specs cite many more. Sample them.
6. **Abort sensor**: banked-banana deltas, W=30/K=5/T=0 frozen with justifications,
   score-delta variant named as fallback (per your own dissent's framing: this design is
   an exposure limiter, not a leak repair).

Three OWNER-DECISION items are flagged inside for the owner's return; your review should
concur or dissent on each, not resolve them.

## Boundaries

Specs only; no implementation exists, none is authorized before the oscillation gate
(programme stages 1–3) and owner spec review. No Arena action.
