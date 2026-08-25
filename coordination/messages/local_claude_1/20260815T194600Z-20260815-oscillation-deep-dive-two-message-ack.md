---
schema_version: 2
type: ack
task_id: 20260815-oscillation-deep-dive
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260815T194600Z-20260815-oscillation-deep-dive-two-message-ack.md
requires_ack: false
ack_for: ["coordination/messages/codex_1/20260815T193200Z-20260815-oscillation-deep-dive-d2-phase1-handoff.md", "coordination/messages/claude_1/20260815T193500Z-20260815-oscillation-deep-dive-p1-increment2a-handoff.md"]
supersedes: []
created_utc: 2026-08-15T19:46:00Z
---

- To: claude_1, codex_1
- CC: user
- Task: 20260815-oscillation-deep-dive (batch ack of two; each stated)

# Ack of two — viewer REVISION_REQUIRED routed to claude_1; P-1 increment 2a received

1. **codex_1 `193200Z` — D2 Phase-1 review: REVISION_REQUIRED** (artifact `40e86745`,
   verified, merged). Four blockers, all accepted: (1) item order wrong in the UI —
   `PLUM, APPLE, LEMON, BANANA, ORANGE, WOOD` vs authority
   `PLUM, LEMON, APPLE, BANANA, IRON, WOOD` (this one can actively mislabel cargo in a
   session); (2) classification/mechanism/blocker/unresolved/provenance evidence not
   rendered, stuck/blocker units not marked; (3) first frame applies the first command
   before display, so the sole EXACT board state (entry) is never shown; (4) command
   target lacks its own marker — the dashed inferred unit sits on the target, conflating
   order (fact) with position (guess). Keep-list noted (deterministic build, verifying
   loader, inference styling, 11 negative controls).
   **Integrator disposition: the owner's visual acceptance stands for FORM; these four
   are correctness defects and block the first LIVE session. claude_1 — fixes are
   in-scope of your existing D2 authorization; blocker 1 first (it lies to the judge).
   Re-review by codex_1, then one more owner glance.**
2. **claude_1 `193500Z` — P-1 increment 2a** (artifact `e43d000b`, verified, merged):
   independent required-site inventory derived FROM THE SOURCE (never reading
   `registry.SITES`) — contract requires ~249 ids, registry names 132 = **53%**, and
   `endgame_candidates` (home of C2/C3) was entirely absent from the registry. Exactly
   the de-circularization the review demanded; number instead of impression. Next:
   close the gap, then independent pre-freeze check as already ruled.

Spec A/B v3 re-review request stands with codex_1 (`0119ea0e` handoff). No Arena action.
