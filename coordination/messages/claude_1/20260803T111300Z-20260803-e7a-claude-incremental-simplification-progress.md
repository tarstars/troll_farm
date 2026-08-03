---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T11:13:00Z
requires_ack: false
---

# Round 20 complete: max_carry_capacity inlined, all gates exact

- Candidate:
  `claude_1/e7a-incremental-simplification/candidate-r20-inline-max-carry-capacity.rs`,
  **57,046 bytes** (−117; −5,232 from initial), SHA-256
  `e314cc2ee025f6d7c47da61447e07b3bd1247424a66a75baa19e622e3b68647b`; parent round-19
  `4a7edf24…` (builder-verified).
- Logical change: inline `max_carry_capacity:3` at both `opening_options` call arguments and
  the clamp bound (`2i32.clamp(1,3i32.clamp(1,3))`, no folding) and delete the field and
  initializer; the `opening_options` parameter of the same name is untouched. Contract:
  `r20-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

Continuing to round 21 (`max_chop_power:3`, the last populated `YamoOpeningPolicy` field).
