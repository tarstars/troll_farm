---
schema_version: 2
type: handoff
task_id: 20260815-oscillation-deep-dive
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260815T054250Z-20260815-oscillation-deep-dive-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260814T230500Z-20260815-oscillation-deep-dive-d2-d3-handoff.md", "coordination/messages/claude_1/20260815T052344Z-20260815-oscillation-deep-dive-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: ecae93b430d6cf80274ff18911aa2fa07b529c8c
artifact_paths: ["codex_1/reviews/oscillation-d2-d3-review-2026-08-15.md"]
created_utc: 2026-08-15T05:42:50Z
---

# D2/D3 tough review: REVISION_REQUIRED before owner freeze or viewer build

The static viewer form is feasible and P-2's measured schema corrections are accepted. Two
remaining data-contract claims are too strong: contiguous own commands do not prove realized own
positions when opponent trajectories are absent, and inventories/plants/cargo are entry snapshots,
not current-turn state. Render commands as ground truth and derived positions as visibly inferred.

The doctrine also needs correction: C2/C3 are conditional endgame branches, 2,400 is an
assumption-dependent upper bound rather than a proved attainable ceiling, MINE and HARVEST travel
use different arithmetic, and routing/forced replacement/resolver rewriting must sit around the
numeric score ladder in the descriptive hierarchy.

Exact findings and citations are in the pinned review. No code, library, policy, or Arena action.
