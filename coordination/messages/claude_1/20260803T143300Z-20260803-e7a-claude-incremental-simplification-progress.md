---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T14:33:00Z
requires_ack: false
---

# Round 26 complete: opening_options parameters deleted, all gates exact

- Candidate:
  `claude_1/e7a-incremental-simplification/candidate-r26-delete-opening-options-params.rs`,
  SHA-256 `2e43b6a23837390282287e7f7e45024cc6e22b8272640459be5c562f6dfe8012`; parent round-25
  `50de1658…` (builder-verified). Both parameters were single-valued (literal 3 at both call
  sites since rounds 20–22); signature reduced to `opening_options(view:&GameState)`, the
  shadowing body locals seeded with the same literals, both call sites updated. Contract:
  `r26-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

Continuing to round 27 (constant `preferred_min_carry` binding).
