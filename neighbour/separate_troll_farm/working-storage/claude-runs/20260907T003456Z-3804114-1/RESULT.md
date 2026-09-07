# RESULT — lumber / growth-aware chop investment

**Verdict: PARK.** Runnable candidate, real changed behaviour, 0 candidate
issues — but the frozen gate needs strictly greater whole-panel points and the
192-pair delta is **+0.0** (170.0 vs 170.0).

**Causal evidence** (field game 901697520, policy-flat **seat 1** vs tonigineer;
neighbour diff decoder + command context). Chop turns/wood by felled **size**:
ours size1 85/17 = **0.20**, size4 48/23 = 0.48; opponent size1 6/2 =
0.33, size4 74/42 = 0.57. Half our chopping labour sat in the worst bucket; the
opponent spent 6 of 102 turns there. Felling pays `size` wood for
`base + slope*size` damage, so wood per point of damage strictly rises with size
and growth is free. The prior "0.28 vs 0.58 wood/chop" claim is superseded: u1
0.21, u2 0.50, opponent u3 0.65 — a power *and target-maturity* gap.

**Change** (new files only; parent, `bot.rs`, `submission.rs` untouched). In
`chop_candidates`, price the same plant chopped after it grows to size 4; if the
plan is immature, no opponent chopper is predicted on it, the ripe plan scores
higher, and it still finishes inside `TOTAL_TURNS`, multiply the premature plan
by 0.25 — demotion, not deletion.
New files, sha256: `claude_candidate_lumber.py` fd7d0fcf,
`test_claude_candidate_lumber.rs` 6a323a0d, `_a.rs` a6b6f94b, `_a_module.rs`
edf69e8a, `_a.min.rs` 6f1cf2d3 (99,140 UTF-16, unpruned), `_a_tests.rs` 87273c62,
`_control_module.rs` 526cd9cc (parent verbatim); full `hashes.txt`.

**Tests/timing.** 10/10 pass (6 new + 4 embedded), rustc 1.90 `--test`.
Behaviour shown before the panel: the power-1 worker takes standing timber first
and returns to the bank-side plot only once it grows past size 1; with no
alternative, and late-game, it still chops; 0 blocked moves. Serial
16-stream bench, Rust 1.90.0, nothing else running: 4,312 turns, max **26.98 ms**,
over_50ms 0, readable-vs-minified `packaging_different_games 0`.

**Panel.** 192 pairs, 9947500..9947507, both seats, 12 opponents, 273.8 s.
Baseline 167/6/19 pts=170.0 own=231.35
margin=114.43 **issues=1**; candidate 167/6/19 pts=170.0 own=232.66 margin=115.92
**issues=0**. Own +1.31, margin +1.48; every per-opponent dpts +0.0. Thin
activation: 17/192 pairs changed score, 13 on map 9947503, 0 outcome changes.

**Evidence** (this run dir): `PLAN.md`, `field-ledger.txt`,
`field-yield-by-size.txt`, `field-target-trace.txt`, `tests.log`, `bench.log`,
`panel.tsv`, `PROGRESS.md`.

**Limitations.** Offline local pool; no ladder, deployment or publication claim.
One field game analysed. Local maps rarely present the field condition, so the
panel barely exercises the mechanism — +0.0 is weak evidence, not refutation.
`0.25` unswept. No detached work; process table empty 00:51Z.


**Next action.** Instrument activation — count demotion firings per game on the
192 panel and the stored field maps — before re-tuning anything.
