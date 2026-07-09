# Candidate v1.43.0-yield - Builder Report

**Task:** D2 yield-to-urgent. A stationary friendly troll can be a hard landing blocker for a
higher-value mover. Implement one bounded L2/L3 feedback pass: detect that exact blocker,
rematch only the blocker to an existing moving alternative, then re-run the joint move solve once.

## What changed

- `rust/src/botmain.rs`
  - `VERSION` bumped to `1.43.0-yield`.
  - Live decider now calls `planner::assign_resolved(...)`; the anti-stall watchdog remains after
    assignment/motion resolution.
- `rust/src/botmain/planner.rs`
  - Split joint assignment into selected candidate metadata plus rendering.
  - Added `assign_resolved(...)`: assignment -> first `motion::solve_moves` -> one yield pass ->
    optional second solve -> final MOVE landing pinning.
  - Yield fires only when:
    - the mover's first-solve landing is its current cell,
    - a same-team stationary troll's current cell is the mover's positive-progress landing,
    - the mover assignment value is strictly greater than the blocker assignment value,
    - the blocker has a valid moving alternative from its existing candidate list.
  - The pass is deterministic and single-round; it emits `@TFYIELD t=<turn> blocker=<id>
    mover=<id>` under `DEBUG`.
- `rust/tests/yield_pass.rs`
  - Added three focused tests: yield corridor, no-yield when blocker outranks, and single-round
    bound across two independent corridors.

No D4/tent walkability changes were made.

## Gates

- Focused yield suite:
  - `cargo test --manifest-path rust/Cargo.toml --release --test yield_pass`
  - Result: `3 passed`.
- Full Rust release suite:
  - `cargo test --manifest-path rust/Cargo.toml --release`
  - Result: all tests passed, including `58 passed / 7 ignored` integration-test baseline plus
    the new `yield_pass` suite.
- Self-determinism:
  - `./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Bundle/minify:
  - `python3 tools/bundle.py`
  - bundled source compiled with `rustc --edition 2021 -O`.
  - `python3 tools/minify.py target/refactor/bundled.rs target/refactor/v1430_yield_min.rs`
  - minified source size: `56861` bytes; minified source compiled with `rustc --edition 2021 -O`.
- Bundled equality:
  - `./target/release/equality target/refactor/v1430_yield_bundled_bin target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Minified equality:
  - `./target/release/equality target/refactor/v1430_yield_min_bin target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.

`cargo fmt --manifest-path rust/Cargo.toml` was run after installing `rustfmt`. It initially
formatted the whole crate; formatter-only churn outside this candidate was reverted, leaving the
candidate source files formatted.

## Frozen Artifacts

- `data/candidates/v1.43.0-yield/v1.43.0-yield.rs`
- `data/candidates/v1.43.0-yield/v1.43.0-yield.min.rs`
- `cgauto/submissions/v1.43.0-yield.rs`
- `cgauto/submissions/v1.43.0-yield.min.rs`

No arena submission or online mini-gate was run in this builder pass.

## Gatekeeper Mini-Gate - 2026-07-08 20:46 MSK

DEBUG probe:

- Built from `data/candidates/v1.43.0-yield/v1.43.0-yield.rs` by flipping
  `const DEBUG: bool = false;` to `true`.
- Minified to `data/candidates/v1.43.0-yield/v1.43.0-yield.debug.min.rs`.
- Compile-check passed with explicit crate name:
  `rustc --crate-name v1430_yield_debug_probe --edition 2021 -O ...`.
- DEBUG minified size: `56860` bytes.

Boss pool:

- Command: `uv run --no-sync python cgauto/collect_debug_games.py data/candidates/v1.43.0-yield/v1.43.0-yield.debug.min.rs boss 8`
- Result: `1/8 wins | our wood 42 | opp wood 53`.
- Formal ramp (`uv run --no-sync python cgauto/ramp.py --last 8`):
  - `t75 delta +2.8`
  - `t150 delta +0.9`
  - `t225 delta -2.6`
  - `t300 delta -10.2`
  - aggregate: `wins 1/8 (12%)`, `our avg final wood 42.5`, late gain `+10.2` vs boss `+17.9`.

Field probes:

- `6480966` / plcc, rank 95 score 20.1: `0/2 wins | our wood 48 | opp wood 92`.
- `6480914` / mikdiet, rank 113 score 19.4: `1/2 wins | our wood 61 | opp wood 54`.

Telemetry:

- Boss: `@TFYIELD` 21 times across 8 games.
- Field: `@TFYIELD` 1 time vs plcc, 3 times vs mikdiet.
- Invariant check: no game had more than one `@TFYIELD` line on the same turn.

Verdict: **PASS-WATCHLIST**. Boss wood missed the preferred `wood >=45` readout, but it stayed
above the hard `wood <40` fail bar, t300 delta was not a crater (`-10.2`, better than the
`-15.3` baseline), there were no crashes, and the one-yield-per-turn invariant held. Watchlist:
plcc field games were both heavy losses.

## Arena Estimate - submitted 2026-07-08 20:47 MSK

Baseline / bracket read immediately before submit:

- Command: `uv run --no-sync python cgauto/cg_rank.py`
- Result: `ARENA-ROOM: tass rank 127/527 Gold score 17.4 | promotable=False | agentId=6543636`
- Interpreted as chained baseline from `v1.42.0-idlefruit`.

Submit:

- Command: `uv run --no-sync python cgauto/api_submit.py cgauto/submissions/v1.43.0-yield.min.rs`
- Result: `SUBMIT-OK via TestSession submit`
- Submit id: `40969224`

Read plan: +20m, +35m, +50m arena reads from 20:47:20 MSK.

Reads:

- +20m read at `2026-07-08 21:07:49 MSK`:
  `ARENA-ROOM: tass rank 139/527 Gold score 16.9 | promotable=False | agentId=6543753`.
  Delta vs bracket `17.4`: `-0.5`. Candidate landing confirmed by new agent id.
- +35m read at `2026-07-08 21:23:15 MSK`:
  `ARENA-ROOM: tass rank 116/527 Gold score 18.6 | promotable=False | agentId=6543753`.
  Delta vs bracket `17.4`: `+1.2`. Same candidate agent id; early dip rebounded.
- +50m read at `2026-07-08 21:38:53 MSK`:
  `ARENA-ROOM: tass rank 116/527 Gold score 18.4 | promotable=False | agentId=6543753`.
  Delta vs bracket `17.4`: `+1.0`.

Verdict: **KEEP / PROMOTE**. v1.43.0-yield is estimated at Gold score `18.4` and rank
`116/527` at the policy read. It beats the chained bracket by `+1.0`, meeting the v2
single-convergence promotion bar. `cgauto/api_submit.py` default was updated to
`cgauto/submissions/v1.43.0-yield.min.rs`. Goal gate did not fire (`116 > 99`).
