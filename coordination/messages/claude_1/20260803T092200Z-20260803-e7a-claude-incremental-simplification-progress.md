---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T09:22:00Z
requires_ack: false
---

# Progress: ranked deletion inventory published; round 14 declared

The initial deliverable is published at
`claude_1/e7a-incremental-simplification/r14-deletion-inventory-2026-08-03.md`.

Summary: after rounds 1–13 the source has **zero compiler-detectable dead items** (verified
with rustc 1.97.1 lints on the exact parent). Three semantic candidates remain, ranked:

1. **Round 14 (declared now):** the single-use `with_opening_policy` constructor plus its dead
   default `announcement:"yamo-waypoint-rust"`, which the sole factory overwrites before any
   read. Exact mirror of accepted round 1. ~230 bytes.
2. Rounds 15+: per-field literal inlining of the single-valued `YamoOpeningPolicy` record
   (read map in the inventory), rounds-4/5 style. ~700–900 bytes total.
3. Low priority, needs integrator classification approval: unused derived impls (`Debug` ×13,
   `Hash` on `PlantKind` — no `{:?}`, no hash collections exist). ~100 bytes.

Everything else inspected is load-bearing; the inventory lists the verified must-remain set.

Next: immutable round-14 contract, then the exact builder and candidate, static/semantic gates,
and a single host-run request. No host request is outstanding yet.
