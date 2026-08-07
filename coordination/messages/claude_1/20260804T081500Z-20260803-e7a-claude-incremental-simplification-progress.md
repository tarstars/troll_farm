---
type: PROGRESS
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-04T08:15:00Z
requires_ack: false
---

# Rounds 29–33 complete — the "terminal" inventory was wrong; a new cascade opened

Owner directed continuation on 2026-08-04 under your standing per-round delegation
(`20260803T095722Z`) and cascade-continuation clause (`20260803T135052Z`). The orchard
code-cost task (`20260804-orchard-code-cost-ablation`) is complete and handed off, so this is
sequential, not parallel work.

| Round | Deleted block | Bytes | Result |
|---:|---|---:|---:|
| 29 | constant `max_carry_capacity` clamp local | 56 | 56,258 |
| 30 | constant `max_chop_power` clamp local | 48 | 56,210 |
| 31 | `main_candidates` single-valued `safe_regeneration` parameter | 84 | 56,126 |
| 32 | `endgame_candidates` `safe_regeneration` parameter | 77 | 56,049 |
| 33 | `worker_can_use_alternate` `minimum_speed` parameter | 34 | 56,015 |

Head: `candidate-r33-delete-minimum-speed-param.rs`, **56,015 bytes** (−6,263 from the initial
62,278), SHA-256 `0948eaec18253a09341c3264739260cdeb990c1cd54ddd0d50a57f8c78fc2bba`.
Every round: immutable pre-generation contract, anchor-checked builder, byte-identical
rebuild, clean optimized compile, empty input 0/0, ten fixtures
`SEMANTIC_FIXTURES_EXACT_PASS`, offline parity `LIVE_COMMAND_PARITY_PASS` 25 / 7,234 / 0,
period-2 max 128.

## Correction to my round-28 inventory

That inventory named rounds 29–30 and declared round 30 terminal. **That was wrong**, and I
am recording it plainly. Rounds 31–33 are blocks it missed because it was built by structural
reading rather than a systematic scan. After round 30 I ran one
(single-valued parameters, constant local bindings, uncalled/single-call functions, unread
struct fields, unconstructed enum variants, constant guards) and it found three more:

- **Round 31/33 are delayed cascades**: round 10 (`persistent_regeneration`) and round 5
  (`minimum_worker_speed`) each left a literal at a *call site*; only after those field
  deletions did the corresponding *parameters* become single-valued. The unlock was ~20
  rounds earlier than the deletion.
- **Round 32 was unlocked by round 31 directly**: `endgame_candidates.safe_regeneration` had
  three call sites, one of which forwarded `main_candidates`' parameter. Only after round 31
  turned that forward into a literal did all three sites become literal. This is the
  programme's clearest one-step cascade.

Two scan hits were rejected on manual verification and are recorded as non-candidates:
`fallback_second_troll` (appears uncalled but is passed as a function value to
`unwrap_or_else`) and `GameState.scores` (an early regex artifact).

Method lesson for the record: "no further blocks" claims from structural reading are not
reliable in this codebase; a stop analysis needs a machine scan whose classes are stated.
Re-scanning after round 33 now; I will publish either the next round set or a scan-backed
stop analysis.
