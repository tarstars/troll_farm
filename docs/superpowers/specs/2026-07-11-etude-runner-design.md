# Etude terminal runner/renderer — design (the "editor", terminal version A)

**Status:** DESIGN approved (user chose A: terminal). Small tool on the merged etudes library.

## Goal
A CLI that makes the forced-outcome oracle USABLE: load a situation (text), render it as a
readable ASCII board + entity table, run `forced_verdict`, print the verdict, and step through
the proof (the forcing line) showing the board after each ply. Authoring = edit the situation
text file in any editor and re-run (no interactive placement in v1 — YAGNI).

## Scope (this sub-project)
Library reuse only — NO changes to `rust/src/etudes/*` (the oracle) or `botmain`. Add ONE binary
`rust/src/bin/etude.rs`. The etude DATABASE and a VISUAL browser editor (B) are separate later
sub-projects.

## CLI
`etude <situation-file.txt> [--step]`
- Loads via `troll_farm::etudes::situation::from_text(&read)`.
- **Render** the board: a grid where each cell shows shack (`0`/`1`), iron (`+`), water (`~`),
  a tree by its type initial (`B`/`P`/`L`/`A`), a troll by its id digit (trolls drawn over
  terrain; if a troll stands on a tree, show the troll). Below the grid, an ENTITY TABLE: each
  troll (id, player, pos, ms/cc/hp/chop, carry), each tree (type, pos, size, health, fruits),
  inventories[2], scores, turn, horizon.
- **Solve**: call `forced_verdict(&sit)`. Print the verdict:
  - `ForcedWin(side=P)` — plus, if a proof exists, the forcing LINE: for each ply, the side-P
    joint command + the resulting min score-diff (from `Proof.line`). Also call `replay_proof`
    and print `proof validated: true/false` (the independent check).
  - `Unresolved` / `TooLarge` — print as-is.
- **`--step`**: additionally, replay the proof line one ply at a time, re-rendering the board
  after each ply (apply the forcing side's command + a fixed opponent response — WAIT is fine for
  a readable walkthrough, or the proof's recorded principal-variation opponent response if
  available), so the user SEES how the win is forced. Pause between plies with a printed
  `--- ply N ---` separator (no interactive input needed; just print all plies in sequence).

## Testing
- `rust/tests/etude_bin.rs` or an inline `#[test]` in the bin: build a Situation in text, render
  it, assert the ASCII contains the expected glyphs at the expected cells (troll id at its pos,
  `B` at the banana, `0`/`1` at shacks). Assert the runner prints `ForcedWin` for the known
  forced-win fixture (reuse the oracle's fixture) and `Unresolved` for the contested one.
- Determinism: render + verdict are pure functions of the input file.
- Full `cargo test --release` green; `cargo build --release --bin etude` compiles.

## Success criteria
`etude some.txt` prints a readable board + the proven verdict + the forcing line, and
`etude some.txt --step` walks the proof visually — so authoring/inspecting etudes no longer means
reading raw text. This unblocks writing the first real etudes (the farm-sustainability questions).
