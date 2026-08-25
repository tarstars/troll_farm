---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/local_claude_1/20260815T194221Z-20260815-banana-farm-two-specs-v3-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: e5319a307d728e71a67f0557086172e41920e61b
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md"]
created_utc: 2026-08-15T19:42:21Z
---

- To: codex_1 (re-review request — this supersedes the held v2 re-review scope)
- CC: user, claude_1
- Task: 20260815-banana-farm-two-specs

# handoff: Spec A/B v3 — rewritten to the five owner rulings; re-review requested

**Transport disclosure first:** my ack of 20260815 stamped `20260815T154500Z` was
written while the clock read ~18:14Z — a stamp-drift slip of mine (the drift rule's exact
failure class). Ordering vs its acked messages is unaffected; noted for the record.

## What v3 is

Both specs now implement the owner session's rulings verbatim: **Spec A** = four states,
three latched transitions — COLLECT → (own 2nd troll) → DENY → **(enemy 3rd troll OR
species_gone OR futility_reached)** → FARM → score-delta abort → WOOD; futility = the
simple selected-species counter, K_futility=10 (frozen; justified by the lemon/plum
regrowth cycle of 8), no ownership inference. **Spec B** = the same file with the single
third-troll doorway. Shared §3–§8 byte-identical — I re-verified independently, SHA
`493894a8b5ab86ac…`. S-1: score-delta is the built sensor (anchors :64/:289/:120–121
verified), provenance preserved as the named future variant. M-1 measurement section:
paired 95% CI, 1.96·SE(Δ) winner, 1.0 materiality floor, max two extensions, night-1 =
A vs resident. The old overlap design survives only as the demoted **Spec A0 appendix**.

## What your review should attack hardest

1. **The three reconciliation notes** — (i) COLLECT and DENY are behaviorally
   resident-identical (the denial bonus is live from turn one); the COLLECT→DENY edge
   only scopes doorway sensors — is that note sufficient or does it hide a gate defect?
   (ii) `enemy_third_troll` can latch during COLLECT, diverging from the resident's
   live gate on a drop-back before our 2nd troll trains — carved out in §4/§5(a)/GB; is
   the carve-out sound? (iii) denial-during-FARM removed to A0 per the doorways ruling —
   check no live-spec text still assumes it.
2. **K_futility=10** — frozen with a growth-cycle argument; attack the justification
   (counter resets on any decrease; zero routes to species_gone).
3. **Byte-identity discipline** — verify the diff really reduces to the doorway
   predicate.
4. **M-1 arithmetic** as written into §12.

Open owner items at spec approval: B-1 (no-floor recommendation stands) and K_futility
confirm-or-reset. No implementation before the oscillation gate and owner approval; no
Arena action.
