---
schema_version: 2
type: handoff
task_id: 20260816-t1-transport-level
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260816T054716Z-20260816-t1-transport-level-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: e303513492791898ce228ddb2d1c1a4da5e181f4
artifact_paths: ["coordination/tasks/20260816-t1-transport-level.md", "local_claude_1/t1-prediction-registry-2026-08-16.md", "local_claude_1/adjudications/OSC-001-ruling-2026-08-16.md", "docs/RULES-LEDGER.md"]
created_utc: 2026-08-16T05:47:16Z
---

- To: claude_1 (implementation), codex_1 (review)
- CC: user
- Task: 20260816-t1-transport-level

# handoff: T-1 transport level — OWNER-DIRECTED implementation of swap/yield/visibility, with pre-registered per-case predictions

## For the owner, in plain terms

This dispatches your decision: build the troll right-of-way feature now, re-run all 34
recorded situations under it, and spend your personal review time only on the cases the
feature fails to cure. We wrote down IN ADVANCE which cases it should cure (25) and
which it should not (9), so the re-run also grades our understanding.

## claude_1 — build order

1. Viewer blocker 1 first (item-order mislabeling — minutes, it lies to the judge).
2. T-1 stage 1: the 34-fixture replay harness; must FAIL on the unmodified resident for
   all 34 (observed failing) before any fix code lands.
3. Then: Target::None visibility (:643-646) → idle-yield → swap (legal: mechanics.md:54-56
   "circular swaps allowed"; ledger rule R-1). Grading rule frozen in the prediction
   registry: FIXED = detector silent AND progress restored — quiet-but-stalled is NOT
   fixed (your own 20/20 finding from 08-09).
4. Acceptance: predictions graded with misses named; 240-game panel — zero de-novo
   oscillation, D-1 rate vs 8.50% baseline / 2.88% D176a reference; p95 < 50 ms; value
   expectation pre-written: ≈ +0.045, i.e. no score claim ever.
P-1 continues as your background thread — the residue sessions will need packets.

## codex_1

Review targets, in order of teeth: the fixture harness (it is the instrument everything
else is judged by — vacuous-check history applies), the swap implementation against the
referee rule, de-novo oscillation on the panel, and the prediction grading (misses
reported honestly, not reclassified).

## Boundaries

No resident mutation (candidate builds only), no Arena, no banana code, no D1-B
door-pricing fix smuggled in (OSC-026 stays in the residue). Owner reviews the residue
with the fixed viewer.
