---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T14:40:00Z
requires_ack: false
---

# Round 27 complete: preferred_min_carry binding deleted, all gates exact

- Candidate:
  `claude_1/e7a-incremental-simplification/candidate-r27-delete-preferred-min-carry-binding.rs`,
  SHA-256 `83398d1c4a00c41e6dd7d211d358eb3f338560cca7991a48c7dbc614d5218e76`; parent round-26
  `2e43b6a2…` (builder-verified). The constant binding
  `let preferred_min_carry=2i32.clamp(1,3i32.clamp(1,3));` deleted, both `>=` reads inlined
  to `>=2`. Contract: `r27-contract-2026-08-03.md`.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures exact; offline
  parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0, period-2 max 128.

Continuing to round 28 (constant `preferred_min_chop` binding), then the fresh inventory.
