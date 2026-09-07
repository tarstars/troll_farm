# PROGRESS — 20260907T003456Z-3804114-1 (lumber / growth-aware chop investment)

Actual milestones, `date -u` throughout. Deadline 01:24:56Z.

- 00:35 read AGENTS/WORKFLOW/WORKSTATE; resolved the field fixture from
  `planning/2026-09-06/policy-flat-field/screen/manifest.json`: game 901697520 is
  block 1, policy-flat, **seat 1**, vs tonigineer, archive `replay-02.json.gz`,
  L 241:262, wood 60 vs 63.
- 00:41 per-worker transaction ledger (`lumber_transactions.py`, neighbour diff
  decoder + command context so growth-cancelled CHOP damage is reconstructed).
  Own u1 91 CHOP -> 19 wood (0.21), 43 of them at (10,6) for 4 wood; own u2
  (trained t8, power 2) 82 -> 41 (0.50); opponent u3 (trained t18, power 3)
  92 -> 60 (0.65); opponent u0 chopped only 10 times and planted 35.
- 00:41 `target_trace.py`: (11,7) BANANA held at stage 1 in a 1-2-3-1 sawtooth;
  opponent's (3,0) LEMON allowed to reach stage 7 / health 12.
- 00:41 `yield_law.py` — the decisive like-for-like quantity, chop turns and wood
  bucketed by the felled plant's size: ours size1 85/17 (0.20) vs size4 48/23
  (0.48); opponent size1 6/2 (0.33) vs size4 74/42 (0.57). Half our chopping
  labour sits in the worst bucket on the board.
- 00:41 first build of the family; rustc found 6 scope errors (`Self::` on the
  new associated constants, `TOTAL_TURNS` import in the fixtures). Repaired.
- 00:43 panel binary built (cargo exit 0, run-local `CARGO_TARGET_DIR`).
- 00:43 first test run 9/10. The one failure was my assertion, not the behaviour:
  the worker takes the mature tree first and *then* the grown sapling
  (mature=12 sapling=12). Rewrote the fixture to assert the real ordering claim.
- 00:43 10/10 focused tests pass (6 new + 4 embedded), rustc `--edition 2021 --test`.
- 00:45 PLAN.md frozen before any panel row existed.
- 00:45 serial 16-stream bench under absolute Rust 1.90.0, nothing else running:
  4,312 turns, mean 1.78 ms, p95 10.5 ms, max 26.98 ms, **over_50ms 0**,
  readable vs minified `packaging_different_games 0`.
- 00:45-00:50 192-pair panel, seeds 9947500..9947507, both seats, 12 opponents,
  `ALLOW_ANY_MAP_SEED=1`, 4 threads, 273.780 s, exit 0.
  Baseline 167/6/19 pts=170.0 issues=1; candidate 167/6/19 pts=170.0 issues=0.
  **Paired point delta +0.0** -> frozen gate 1 FAILS. Own +1.31, margin +1.48.
  17/192 pairs changed score, 13 of them on map 9947503; 0 outcome changes.
- 00:50 hashes collected; parent, `bot.rs`, `submission.rs` unchanged; process
  table for rustc/cargo/panel_runner/lumber_tests empty. No detached work.
