---
schema_version: 2
type: policy
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260815T083000Z-20260815-owner-session-rulings-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 321a66001477a286df1dade5b83d6a396c977fa5
artifact_paths: ["coordination/tasks/20260815-banana-farm-two-specs.md", "coordination/tasks/20260815-oscillation-deep-dive.md", "docs/ADJUDICATION-TEMPLATE-2026-08-15.md", "docs/RULES-LEDGER.md"]
created_utc: 2026-08-15T08:30:00Z
---

- To: claude_1, codex_1
- CC: user
- Tasks: 20260815-banana-farm-two-specs (primary), 20260815-oscillation-deep-dive

# policy: owner five-decision session COMPLETE — rulings 3–5 (1–2 were messaged separately this morning)

## For the owner, in plain terms
This tells both agents your remaining three decisions so all work proceeds from them.

## Ruling 3 — Spec A REDEFINED (denial-preserving state machine)
The drafted "farm at second troll, overlapping denial" is DEMOTED to collection candidate
A0 (owner expects it poor: "it sounds like a bad bot" — denial is suspected load-bearing,
supported by N6's weak arm at −0.754). Real Spec A, all transitions latched one-way:
COLLECT → (own 2nd troll) → DENY → **(enemy 3rd troll OR no selected-species tree left OR
selected-species count sustainably non-decreasing over K turns)** → FARM → (abort sensor)
→ WOOD. Futility = the SIMPLE tracker (count selected-species trees; no ownership
inference; K-persistence absorbs our rare endgame conversion-plant blips). The two new
doorways are the owner's denial STOP conditions — first time in writing. Whether denial
should outlive the enemy's 3rd troll is an explicit LATER experiment. **Spec B = Spec A
with only the 3rd-troll doorway** — preserve the single-predicate diff in the rewrite.

## Ruling 4 — S-1: both-in-collection
Build the SCORE-DELTA abort sensor now (snapshot both scores at FARM entry; abort on K
consecutive enemy-faster turns after warmup W). The PROVENANCE sensor stays fully
specified as the named future variant.

## Ruling 5 — M-1: measurement protocol
Interleaved ABABABABAB at ~2 h per submission (~20 h/block). Verdict on the 95% CI of the
PAIRED difference (adjacent-pair averaging; never two separate CIs). Winner at
|Δ| ≥ 1.96·SE(Δ), SE(Δ)=1.501·√(2/n); materiality floor |Δ|<1.0 → stop as immaterial;
otherwise extend one block, max two extensions. Campaign reports its empirical paired
spread beside planning σ. **Night-1 pairing: Spec A vs current resident.** No campaign
runs before the oscillation gate, spec approval, and per-night owner go-ahead.

## Work consequences
- **local_claude_1**: one spec-rewrite pass to the full ruling set; then codex_1 re-review.
- **codex_1**: hold the Spec v2 re-review until the rewrite lands (supersedes §7/§9/§12);
  D2/D3-appendix re-review scope from the morning message unchanged.
- **claude_1**: no change — P-1 and D2 Phase 1 as authorized.
No Arena action from any of this.
