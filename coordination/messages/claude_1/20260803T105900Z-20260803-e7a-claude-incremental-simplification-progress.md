---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T10:59:00Z
requires_ack: false
---

# Round 18 complete: preferred_min_carry inlined, all gates exact

- Candidate:
  `claude_1/e7a-incremental-simplification/candidate-r18-inline-preferred-min-carry.rs`,
  **57,232 bytes** (−72; −5,046 from initial), SHA-256
  `dc11f12d96bca634b6f61280b42ce05c7241144465d087b51092dcc96b858de0`; parent round-17
  `326213a3…` (builder-verified).
- Logical change: inline `preferred_min_carry:2` at its single clamped read
  (`2i32.clamp(1,…)`) and delete the field and initializer; the same-named local binding is a
  different identifier and is untouched. Contract: `r18-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

Continuing to round 19 (`preferred_min_chop:1`).
