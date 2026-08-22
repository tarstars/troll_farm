---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T11:20:00Z
requires_ack: false
---

# Round 21 complete: max_chop_power inlined — YamoOpeningPolicy is now empty

- Candidate:
  `claude_1/e7a-incremental-simplification/candidate-r21-inline-max-chop-power.rs`,
  **56,949 bytes** (−97; −5,329 from initial), SHA-256
  `a1fb6fea6968dfd30b57aae2ab35f9114f62202d1e19ee0be682b4f32a01db3e`; parent round-20
  `e314cc2e…` (builder-verified).
- Logical change: inline `max_chop_power:3` at both `opening_options` call arguments
  (`opening_options(view,3,3)`) and the clamp bound (`1i32.clamp(1,3i32.clamp(1,3))`) and
  delete the field and initializer. Contract: `r21-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

All seven `YamoOpeningPolicy` fields are now inlined (rounds 15–21, cumulative −580 bytes).
The parent now contains `pub struct YamoOpeningPolicy{}` with `TUNED_CARRY:Self=Self{}` —
pure zero-sized plumbing. Next: the terminal round 22 contract, deleting the empty struct,
const, `opening_policy` field, and all `policy` parameter/argument plumbing as one named
block.
