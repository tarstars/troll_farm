# PROGRESS — run 20260906T210944Z-3184968-1

All times UTC.

- 21:10 read CLAUDE.md/WORKSTATE.md/SCREEN-RESULT.md and the screen manifest rows.
- 21:14 gap fixed: every one of the 12 official screen games has own TRAIN count 1 and
  own workforce max 2. viewlagoon (rank 7) trained 3x (turns 1/108/163, 454-180) and
  5x (turns 1/86/115/152/197, 522-237). Mechanism: `can_train`/`training_affordable`
  return false at n>=2 and the funding branch `early` requires `my_units.len() < 2`, so
  the hiring pipeline fires exactly once. Block 5 ends with 137 banked APPLE and zero
  plum/lemon/iron: monoculture cannot pay a four-resource bill either.
- 21:16 claude_candidate_gap.py written; parent claude_candidate_policy_flat.rs.
- 21:17 builder emits readable/module/compact (99,673 UTF-16), +62 lines, 0 removed.
- 21:18 tests 7/7 pass under absolute Rust 1.90 (`--edition 2021 --test`). rustc exited.
- 21:18 panel built (cargo, exit 0), binary copied to run dir as panel_runner.
- 21:19-21:23 panel run, foreground, seeds 9947500-9947507, 192 pairs, 260.3 s, exit 0.
- 21:23 compact export compiled exactly, 6.46 s. No concurrent heavy job during it.
- 21:24 summary: candidate +1.0 paired points but 0.0 over the 22 games where the
  mechanism actually fires. Negative verdict written to the run RESULT.md.
- No detached work launched; process table for rustc/cargo/panel is empty.
