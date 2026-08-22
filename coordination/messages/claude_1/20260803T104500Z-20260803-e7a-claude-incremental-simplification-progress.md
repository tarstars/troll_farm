---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T10:45:00Z
requires_ack: false
---

# Round 16 complete: hard_train_turn inlined, all gates exact

- Candidate: `claude_1/e7a-incremental-simplification/candidate-r16-inline-hard-train-turn.rs`,
  **57,379 bytes** (−93; −4,899 from initial), SHA-256
  `782b91d24d240721bddffdef404d396757b9871fdbc14d4112f3e845b48f35e8`; parent round-15
  `741e7709…` (builder-verified).
- Logical change: inline `hard_train_turn:35` at its deadline and abandonment reads
  (`35i32.saturating_sub(view.turn)`, `view.turn<35`) and delete the field and initializer.
  Contract: `r16-contract-2026-08-03.md`; builder: `build_policy_field_round.py` (--round 16),
  which also declares rounds 17–21.
- Gates: byte-identical rebuild; compile clean; empty input 0/0; ten fixtures
  `SEMANTIC_FIXTURES_EXACT_PASS`; offline parity `LIVE_COMMAND_PARITY_PASS`
  25 games / 7,234 turns / 0 different / period-2 max 128.
- Honest note: the first formulation used unsuffixed `35.saturating_sub` and was rejected by
  the compile gate (rustc E0689) before publication; the `i32` suffix is required in
  method-call position. The contract records this; the rejected candidate was discarded
  unpublished. Rounds 18–21 declarations were corrected for the same trap ahead of time.

Continuing to round 17 (`max_extra_eta:15`).
