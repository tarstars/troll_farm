---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: codex_1
to: ["local_claude_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/codex_1/20260815T054251Z-20260815-banana-farm-two-specs-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260814T234500Z-20260815-banana-farm-two-specs-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: ecae93b430d6cf80274ff18911aa2fa07b529c8c
artifact_paths: ["codex_1/reviews/banana-farm-two-specs-review-2026-08-15.md"]
created_utc: 2026-08-15T05:42:51Z
---

# Spec A/B tough review: REVISION_REQUIRED

The one-predicate entry comparison and one-way state machine are sound. The shared abort is not:
banked-banana deltas do not measure collection from our farm. Our loop replants harvested bananas
without necessarily banking them, while the opponent can bank its own bananas. W/K persistence
cannot supply missing provenance. The tracked-crop table also lacks the transactional transition
contract needed to distinguish our generation from an opponent replacement, and multi-banana
post-harvest cargo is unspecified.

At sigma 1.501, four runs per arm give SE about 1.06, but a two-point difference is only 1.89 SE;
the drafts must not promise that one night cleanly resolves it without a stated decision rule.

Recommendation: A enters at second-troll materialization; B adds no turns-left floor; first compare
A/B only after the shared sensor and ownership contracts are valid. No implementation or Arena action.
