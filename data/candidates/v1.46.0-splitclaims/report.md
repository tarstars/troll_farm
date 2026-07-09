# Candidate v1.46.0-splitclaims - Builder Report

**Task:** implement split fruit-vs-wood tree claims. User replay diagnosis: in a gatherer +
chopper pair, the gatherer can ignore a nearby ripe apple and walk to a farther apple because
the chopper claims the nearby tree cell for wood. The old matcher treated every tree-cell target
as one exclusive resource, so `HARVEST tree` and `CHOP/MOVE tree` could not coexist.

## What changed

- `rust/src/botmain.rs`
  - `VERSION` bumped to `1.46.0-splitclaims`.
- `rust/src/botmain/planner.rs`
  - Added semantic claim classes for assigned targets:
    - `Fruit` for harvest and fruit-travel tree claims,
    - `Wood` for fell/chop tree claims,
    - `Cell` for ordinary mutually exclusive cells.
  - Same-class claims on the same cell still conflict.
  - `Fruit` and `Wood` claims on the same tree are compatible only when the fruit worker's ETA
    is strictly smaller than the wood worker's ETA.
  - This is intentionally narrower than v1.44.0-harvest-before-fell: it does not hide wood
    candidates, and it does not allow equal-ETA movement fights.
- `rust/tests/split_tree_claims.rs`
  - RED/GREEN pin: a nearby apple gatherer can claim the same tree the chopper wants for wood.
  - Guard pin: equal-ETA fruit/wood claims still conflict.
  - Guard pin: wood/wood claims remain exclusive.

## Gates

- Focused suite:
  - `cargo test --release --test split_tree_claims`
  - Result: `3 passed`.
- Full Rust release suite:
  - `cargo test --release`
  - Result: all active tests passed, including `split_tree_claims` and `yield_pass`.
- Self-determinism:
  - `./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Bundle/minify:
  - `python3 tools/bundle.py src/botmain.rs target/refactor/v1460_splitclaims.rs`
  - Bundled source: `96747` chars (`98160` bytes); compiled with `rustc --edition 2021 -O`.
  - `python3 tools/minify.py target/refactor/v1460_splitclaims.rs
    target/refactor/v1460_splitclaims_min.rs`
  - Minified source size: `58814` bytes; compiled with explicit crate name.
- Bundled equality:
  - `./target/release/equality target/refactor/v1460_splitclaims_bin target/release/bot
    8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Minified equality:
  - `./target/release/equality target/refactor/v1460_splitclaims_min_bin target/release/bot
    8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.

## Frozen Artifacts

- `data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.rs`
- `data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.min.rs`
- `data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.debug.rs`
- `data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.debug.min.rs`
- `cgauto/submissions/v1.46.0-splitclaims.rs`
- `cgauto/submissions/v1.46.0-splitclaims.min.rs`

## Mini-Gate

DEBUG probe:

- Built from `data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.rs` by flipping
  `const DEBUG: bool = false;` to `true`.
- Minified to `data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.debug.min.rs`.
- Compile-check passed with explicit crate name:
  `rustc --crate-name v1460_splitclaims_debug --edition 2021 -O ...`.
- DEBUG minified size: `58813` bytes.

Boss pool:

- Command: `uv run --no-sync python cgauto/collect_debug_games.py
  data/candidates/v1.46.0-splitclaims/v1.46.0-splitclaims.debug.min.rs boss 8`
- Result: `1/8 wins | our wood 44 | opp wood 60`.
- Formal ramp (`uv run --no-sync python cgauto/ramp.py --last 8`):
  - `t75 delta +2.8`
  - `t150 delta +1.5`
  - `t225 delta -6.5`
  - `t300 delta -15.9`
  - aggregate: `wins 1/8 (12%)`, our avg final wood `44.0`, late gain `+11.5`
    vs boss `+20.9`.

Field probes:

- `plcc` (`6480966`):
  - `0/2 wins | our wood 62 | opp wood 92`.
  - Still loses, but our wood improved versus the v1.43 watchlist probe (`48`) while opponent
    wood stayed around `92`.
- `mikdiet` (`6480914`):
  - `2/2 wins | our wood 72 | opp wood 26`.

Mini-gate verdict: **PASS-WATCHLIST**. Boss result is not a clean pass, but it is not a local
crater; field probes are acceptable and the candidate directly fixes the user-observed
near-apple contention without repeating v1.44's fell suppression.

## Arena

Bracket before submit:

- `2026-07-08 23:55 MSK`: `ARENA-ROOM: tass rank 151/527 Gold score 16.5 | agentId=6543791`
  (`v1.43.0-yield` restored after v1.44 rejection).

Submission:

- Command: `uv run --no-sync python cgauto/api_submit.py
  cgauto/submissions/v1.46.0-splitclaims.min.rs`
- Time: `2026-07-08 23:56 MSK`.
- Submit id: `40969964`.
- Result: `SUBMIT-OK via TestSession submit`.

Landing / reads:

- Immediate read after submit still showed restored v1.43 agent `6543791`; v1.46 had not landed
  yet.
- Landing check (`2026-07-09 00:04:22 MSK`): `ARENA-ROOM: tass rank 371/527 Gold score 11.7 |
  agentId=6543815`. Delta vs bracket `16.5`: `-4.8`. This is a severe early dip; wait for the
  scheduled +20m policy read before formal revert.
- +20m (`2026-07-09 00:16 MSK`): `ARENA-ROOM: tass rank 169/527 Gold score 16.3 |
  agentId=6543815`. Delta vs bracket `16.5`: `-0.2`, inside the v2 inconclusive band. Continue
  to +35m.
- +35m (`2026-07-09 00:31 MSK`): `ARENA-ROOM: tass rank 127/527 Gold score 17.4 |
  agentId=6543815`. Delta vs bracket `16.5`: `+0.9`, a KEEP signal. Continue to +50m policy
  read; goal gate did not fire (`127 > 99`).
- +50m (`2026-07-09 00:47 MSK`): `ARENA-ROOM: tass rank 127/527 Gold score 17.4 |
  agentId=6543815`. Delta vs bracket `16.5`: `+0.9`.

Verdict: **KEEP / NOT PROMOTED**. v1.46.0-splitclaims beat the bracket by `+0.9`, crossing the
v2 KEEP bar but missing the single-read promotion bar (`+1.0`). It remains live as the chained
baseline for the next candidate; `cgauto/api_submit.py` default stays on
`cgauto/submissions/v1.43.0-yield.min.rs`. Goal gate did not fire (`127 > 99`).
