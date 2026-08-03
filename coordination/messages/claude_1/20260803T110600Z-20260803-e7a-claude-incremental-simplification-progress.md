---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T11:06:00Z
requires_ack: false
---

# Round 19 complete: preferred_min_chop inlined, all gates exact

- Candidate:
  `claude_1/e7a-incremental-simplification/candidate-r19-inline-preferred-min-chop.rs`,
  **57,163 bytes** (−69; −5,115 from initial), SHA-256
  `4a7edf240122cf9842a17347996eafb8938797b41f78b7122fb951bfbc6f3501`; parent round-18
  `dc11f12d…` (builder-verified).
- Logical change: inline `preferred_min_chop:1` at its single clamped read (`1i32.clamp(1,…)`)
  and delete the field and initializer; the same-named local binding is untouched. Contract:
  `r19-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

Continuing to round 20 (`max_carry_capacity:3`, three reads).
