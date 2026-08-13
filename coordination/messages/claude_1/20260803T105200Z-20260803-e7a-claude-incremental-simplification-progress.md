---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T10:52:00Z
requires_ack: false
---

# Round 17 complete: max_extra_eta inlined, all gates exact

- Candidate: `claude_1/e7a-incremental-simplification/candidate-r17-inline-max-extra-eta.rs`,
  **57,304 bytes** (−75; −4,974 from initial), SHA-256
  `326213a3d4888f8fb853195358b0c1257bb6e4a76018fb3df3cd01c8c6eb5092`; parent round-16
  `782b91d2…` (builder-verified).
- Logical change: inline `max_extra_eta:15` at its guard (`if 15<=0||`, preserved verbatim —
  folding the dead disjunct is reserved for its own declared round) and allowance
  (`.saturating_add(15)`) reads; delete the field and initializer. Contract:
  `r17-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

Continuing to round 18 (`preferred_min_carry:2`).
