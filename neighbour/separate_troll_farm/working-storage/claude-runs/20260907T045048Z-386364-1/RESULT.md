# RESULT — marginal investment ledger: -31.0, gate FAILS

**Verdict: PARK.** Legality passes (0 candidate issues, 192/192); points fail,
**139.0 vs 170.0, delta -31.0** (prior dispatch -39.0). Second, independent
blocker: exact compact export **102,712 UTF-16 > 100,000**. Source frozen
before the panel; no tuning after.

**Changed files** (dispatch family + run artifacts only):
`claude_candidate_dispatch_core.rs` `0990ebba`,
`test_claude_candidate_dispatch.rs` `7b60e160`; regenerated
`_a.rs` `5af6d9c5`, `_a_module.rs` `37eb8752`, `_a_tests.rs` `50c1f380`.
Unchanged: generator `57362ad8`, control `526cd9cc`, parent `95ee691e`,
`bot.rs` `44e3daca`, `submission.rs` `7f61a6cd`.

**Mechanism (one).** `budget[i]=bill[i]-bank[i]`; every `Job` carries the
quantities it would deliver and assignment is a re-priced greedy that *spends*
that budget, so two workers on two trees cannot both be paid for the same last
unit and a `cc > deficit` load is capped. `hire_plan` became a marginal ledger:
funding elapsed time from the roster's real harvest/mine cycles, displaced
worker-turns priced at its own best income rate, bill fruit charged as banked
score, post-spawn income capped by spare wood/fruit (standing + regrowth) after
the existing roster's take. Six predeclared specs incl. hp0 foresters.

**Tests: 25 run, 25 pass** (`rustc` 1.90 absolute path, `--test-threads=1`).
New: shared-bill double-claim; bonus capped when cc>bill; hp0 forester never
HARVEST/PICK/PLANT yet banks wood; a long funding trip declines a hire the same
board funds when near (near net **+47.27**/45 turns; far `None`); a referee run
that fetches, banks, pays, spawns `2 2 0 3` then `1 1 1 1`, ends **+56**.
Movement/seed/TRAIN-PICK fixtures kept.

**Panel** (9947500..07, 12 opponents, both seats, `ALLOW_ANY_MAP_SEED=1`,
runner `bc944990`). Baseline 167/6/19=170.0; candidate **139/0/53=139.0**; own
149.87 vs 231.35, opp 108.42 vs 116.92; issues **0 vs 1**. All **192** baseline
streams match the `20260906T210944Z-3184968-1` controls. Wood 33.36 vs 42.45;
workers 2.28 vs 2.00; first TRAIN median turn 14; every hire an hp0 specialist
(89/82/68/6 of `2 2 0 2`, `1 1 0 1`, `2 2 0 3`, `1 2 0 2`).

**Export/latency (corrected).** ORIGINAL readable == pruned == exact compact,
**16 archived official streams / 4,312 turns, 0 mismatches**; interactive
per-turn max **1.023 ms** (compact 0.919); zero diagnostics.

**Evidence** (this run dir): `summary.txt`, `panel.tsv`, `stats.txt`,
`tests-full.log`, `stream-equality.json`, `export.txt`, `hashes.txt`.

**Limitations.** Economy still loses 31 points; export size and panel gate both
fail. No real-known-map *referee* fixture (16-stream check is command-level).
Lint prelude quiets warnings in all three binaries.

**Next action.** Restore export headroom: declare `SearchBot` and parent
`policy::base::bot::moisan` a new `DEAD_REGION` (`DispatchBot` never constructs
them), then re-run `measure_dispatch_export.py` and `exact_stream_latency.py 16`
to prove the cut changes no command.
