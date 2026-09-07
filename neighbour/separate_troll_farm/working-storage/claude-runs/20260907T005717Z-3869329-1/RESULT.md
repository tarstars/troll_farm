# RESULT — hirewood / first-hire wood investment

**Verdict: PARK — the frozen gate fails decisively.** Runnable, high-activation
candidate; 192 pairs: 163.5 points vs baseline 170.0 (**-6.5**), own -16.06. The mechanism works and is wrong: pricing the first hire in
banked wood alone systematically stops buying movement speed.

**Changed investment rule.** `opening_key`'s leading component was the raw stat
sum `ms+cc+chop`. It is now `hire_value`: the hire's net points — wood it can
fell, carry and bank in the turns it will really have (shack-door BFS /
`movement_speed` out and back, `predict_tree(delay+travel)` so free growth during
the bill counts, `chop_outcome`, `min(final_size, carry_capacity)`, one drop
turn, greedy fill over *distinct* plants because `apply_chop` deletes them, and
the standing forest first claimed by the trolls already on the board) at
`WOOD_POINTS`, minus the bill's fruit. Iron is priced only through its delay.
`strongest_affordable` re-prices at eta 0. Filters, deadline and the single
`ensure_opening` decision are untouched. New files only (sha256):
`claude_candidate_hirewood.py` 0f23f649, `test_…hirewood.rs` 80fd343f,
`_a.rs` 53fd2d69, `_a_module.rs` a4fb8199, `_a.pruned.rs` d1e095e2,
`_a.min.rs` cded8a6d (**90,365** UTF-16, guarded `DEAD_REGIONS` pruning),
`_a_tests.rs` b7cfff52, `_control_module.rs` 526cd9cc (parent verbatim).
Parent 95ee691e, `bot.rs`, `submission.rs` unchanged.

**Checks.** 15 tests pass (7 new + 8 embedded), rustc 1.90.0 `--test`; the test
export carries the parent as `mod baseline`, so both arms play one referee: exact
bill paid from a part-funded bank after collecting missing iron/fruit, referee
spawns the requested stats, wood really banked, barren board buys the fast cheap
hire, late/barren openings legal, 0 issues, 0 blocked moves, one stable spec.
Bench first: 16 streams, 4,312 turns, max **27.3 ms**, over_50ms 0,
readable-vs-compact `packaging_different_games 0`. Panel: 9947500..9947507, both
seats, 12 opponents, `ALLOW_ANY_MAP_SEED=1`, 286.2 s. Baseline 167/6/19
pts=170.0 own=231.35 margin=114.43 issues=1 (matches gap 210944Z); candidate
163/1/28 pts=163.5 own=215.29 margin=85.69 **issues=0**. Activation is real:
**168/192** pairs changed the hire, almost all dropping `ms` 2→1
(e.g. `2 2 0 3 → 1 2 0 2`, 24 pairs). No opponent improved.

**Evidence** (run dir): `PLAN.md` (frozen 01:07Z), `tests.log`, `bench/report.json`,
`panel.tsv`, `summary.txt`, `activation.txt`, `hashes.txt`, `PROGRESS.md`.

**Limitations.** Wood-only value, as the ticket allowed — speed also moves fruit,
which the panel says dominates. One synthetic fixture board; my own paired
fixture already showed the parent banking more (24 vs 22 wood). Bench measured
the pruned source only. Local pool; no ladder claim.

**Next action.** Do not re-tune this rule. Re-run it with `hire_value` extended
to fruit-hauling throughput (speed's real payoff), or park the family.
