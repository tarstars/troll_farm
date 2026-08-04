# How much source code does the apple orchard cost?

**Answer: 15,013 bytes — 23.9 % of the 62,820-byte program, or 15.0 % of the platform's
100,000-character submission allowance.** (The file is ASCII, so bytes and Unicode characters
are the same number.)

## What was measured

The bot contains an optional "orchard" strategy: early in a game it can send one worker to
plant an apple tree in a spot the opponent cannot easily reach, then keep that worker camped
there harvesting the tree's fruit for the rest of the game, while the main policy is told not
to disturb the tree or reassign the worker. This audit measures how much of the program's
source code exists only to implement that strategy.

Method (two artifacts from the same frozen original):

1. **Reference** (`activation-disabled-reference.rs`): one minimal edit — the orchard's
   activation test is replaced by "do nothing", so the strategy can never start. Everything
   else is untouched. 62,581 bytes, SHA-256 `8fc1b7f3…`.
2. **Stripped** (`e7a-without-orchard-code.rs`): starting from the reference, every piece of
   code that is unreachable once the orchard cannot start was physically deleted. 47,807
   bytes, SHA-256 `102caecd…`.

Both were produced by a deterministic builder (`build_orchard_code_cost.py`) that verifies
the original's hash, checks every deletion anchor occurs exactly the expected number of
times, and confirms no orchard identifier survives.

## Safety proof — deletion changed nothing beyond disabling the orchard

- **Stripped vs reference: identical commands on the entire open test panel** — all 25
  replayed real ladder games, 7,234 command lines, zero differences
  (`stripped-vs-reference-panel.json`).
- Reference vs the original: identical on 24 of the 25 games; the single difference is the
  one game where the orchard actually activated in real play — exactly the intended semantic
  change and nothing else (`reference-vs-baseline-panel.json`).
- Both artifacts compile with the standard optimized Rust gate and exit cleanly on empty
  input; both pass all ten behavioral test fixtures exactly
  (`reference-semantic-fixtures.json`, `stripped-semantic-fixtures.json`).
- No sealed data was opened; the frozen original file was read-only throughout.

## Itemized inventory of the removed code (measured against the original)

| Component | Bytes |
|---|---:|
| Orchard phase state machine (4-state enum) | 97 |
| Orchard site geometry record (mother cell, doors, alternates) | 124 |
| Orchard timing record (first-chop / cycle estimates) | 98 |
| Orchard wrapper state (starter id, geometry, phase, natural-plant snapshot, config) | 298 |
| Orchard wrapper implementation: site selection, activation economics, seed carrying, planting, camping/maintenance, abandonment | 10,241 |
| Orchard turn-loop driver (the wrapper's command hook, incl. the activation branch) | 3,373 |
| Reservation channel through the main policy (worker hold + protected-tree fields, filters, parameter threading) and the main()/import switch | 782 |
| **Total** | **15,013** |

## What was kept as shared infrastructure (counted, not estimated)

Generic apple parsing/planting/picking/harvesting, chopping, banking, opponent denial, the
tree-growth predictor (used by general chop scoring), the bot trait, and the main policy's
own opponent-risk penalty. None of these could be removed: each has live uses outside
orchard management.

## Secondary metrics (labelled secondary because the source is one minified line)

- gzip-compressed size: 13,980 → 11,058 bytes (−2,922, −20.9 %).
- Lexical tokens: 20,788 → 16,132 (−4,656, −22.4 %).

## Context

Combined with the live ladder ablation of 2026-08-03 (−2.03 rating without the orchard),
both sides of the trade are now measured: **the orchard costs 23.9 % of the source budget
and buys about 2 rating points.**
