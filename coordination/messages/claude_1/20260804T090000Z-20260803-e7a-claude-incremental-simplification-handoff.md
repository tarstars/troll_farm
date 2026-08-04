---
type: HANDOFF
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-04T09:00:00Z
requires_ack: true
---

# Rounds 29–36 handoff: 55,799 bytes, scan-backed stop analysis, checkpoint requested

Owner-directed continuation on 2026-08-04, sequential to the completed orchard code-cost
task, under your standing per-round delegation and cascade-continuation clause.

## Accumulated result

| Round | Deleted block | Bytes | Result |
|---:|---|---:|---:|
| 29 | constant `max_carry_capacity` clamp local | 56 | 56,258 |
| 30 | constant `max_chop_power` clamp local | 48 | 56,210 |
| 31 | `main_candidates` single-valued `safe_regeneration` parameter | 84 | 56,126 |
| 32 | `endgame_candidates` `safe_regeneration` parameter (unlocked by 31) | 77 | 56,049 |
| 33 | `worker_can_use_alternate` `minimum_speed` parameter | 34 | 56,015 |
| 34 | never-read `GameState.scores` field + its now-unused import | 98 | 55,917 |
| 35 | duplicate `carrying_any` helper (reimplemented `Unit::total_carried`) | 62 | 55,855 |
| 36 | orphaned duplicate `carry_total` helper (unlocked by 35) | 56 | 55,799 |

Head: `candidate-r36-delete-orphaned-carry-total.rs`, **55,799 bytes**, SHA-256
`2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`. Cumulative **−6,479
bytes (−10.4 %)** from the initial 62,278; −7,021 vs exact live E7a.

Every round: immutable pre-generation contract, anchor-checked builder (now with post-round
survivor-count assertions for the chained parameters), byte-identical rebuild, clean
optimized compile, empty input 0/0, ten fixtures `SEMANTIC_FIXTURES_EXACT_PASS`, offline
parity `LIVE_COMMAND_PARITY_PASS` 25 games / 7,234 lines / 0 different / period-2 max 128.

## Two findings worth your attention

1. **My round-28 "terminal" claim was wrong** — six further blocks existed. It was built by
   structural reading. Replacement: `cascade_scan.py`, committed and re-runnable, whose
   classes are stated in `r36-stop-analysis-2026-08-04.md`.
2. **Round 34 is a class the compiler cannot flag.** `GameState.scores` was computed from the
   parsed inventories every turn and never read; constructing a field in a struct literal
   counts as a use for rustc's dead-code lint, so every prior zero-warning compile was
   consistent with it being dead. Worth noting for other agents' audits: zero rustc warnings
   is not evidence of no dead code. Before deleting I verified no whole-`GameState` equality
   comparison exists (the struct derives `Eq`), so narrowing the field list cannot change
   behavior.

Two scan hits were rejected on manual verification and recorded as non-candidates:
`fallback_second_troll` (passed as a function value to `unwrap_or_else`) and the four
"constant" locals (all `let mut` accumulators).

## Requested disposition

All deletion classes are now empty; the only non-empty class, single-call function inlining
(~38 sites), I recommend leaving closed — it relocates logic rather than deleting it and
would hurt readability of the largest routines. Rationale in the stop analysis.

I propose round 36 as the next accumulated checkpoint: please run the 516-task development
equality panel as you did for round 22, then decide the deferred untouched-range
qualification. No host request is outstanding and I will not generate round 37 without a
pushed disposition.
