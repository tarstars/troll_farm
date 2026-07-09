# Candidate v1.44.0-harvest-before-fell - Builder Report

**Task:** protect nearby high-value fruit harvests from being displaced by wood claims on the
same ripe tree. User replay diagnosis: a pure gatherer can ignore a nearby ripe apple because a
chopper claims that tree cell for felling; the joint matcher treats harvest and fell as the same
exclusive `target: Some(cell)`.

## What changed

- `rust/src/botmain.rs`
  - `VERSION` bumped to `1.44.0-harvest-before-fell`.
- `rust/src/botmain/planner.rs`
  - Added a harvest-before-fell guard for wood-capable trolls.
  - Wood claims skip a ripe tree only when a free-capacity gatherer can harvest it within two
    turns and the fruit is non-idle work: funding fruit, seed/printer fruit, or Hoard wallet
    fruit.
  - Exceptions preserve urgent wood behavior:
    - no protection in liquidation,
    - no protection under nearby enemy chopper pressure,
    - no protection when the wood worker already stands on the tree,
    - ordinary idle fruit remains unprotected, preserving the v1.24 fruitbank lesson.
- `rust/tests/harvest_before_fell.rs`
  - RED/GREEN pin: pure gatherer gets the nearby water-apple before the chopper's fell claim.
  - Enemy-threat pin: adjacent enemy chopper keeps the ripe tree fellable.
  - Narrowing pin: ordinary idle fruit does not suppress a valuable wood claim.

## Gates

- Focused suite:
  - `cargo test --release --test harvest_before_fell`
  - Result: `3 passed`.
- Regression invariant:
  - `cargo test --release --test idlefruit fruit_never_displaces_chop_help`
  - Result: `1 passed`.
- Full Rust release suite:
  - `cargo test --release`
  - Result: all active tests passed, including `harvest_before_fell` and `yield_pass`
    (`61 passed / 7 ignored` integration-test baseline).
- Self-determinism:
  - `./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Bundle/minify:
  - `python3 tools/bundle.py src/botmain.rs target/refactor/v1440_harvest_before_fell.rs`
  - Bundled source: `98691` chars (`100104` bytes); compiled with `rustc --edition 2021 -O`.
  - `python3 tools/minify.py target/refactor/v1440_harvest_before_fell.rs
    target/refactor/v1440_harvest_before_fell.min.rs`
  - Minified source size: `59684` bytes; compiled with explicit crate name because the filename
    contains `.min.rs`.
- Bundled equality:
  - `./target/release/equality target/refactor/v1440_harvest_before_fell_bin target/release/bot
    8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Minified equality:
  - `./target/release/equality target/refactor/v1440_harvest_before_fell_min_bin
    target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.

## Frozen Artifacts

- `data/candidates/v1.44.0-harvest-before-fell/v1.44.0-harvest-before-fell.rs`
- `data/candidates/v1.44.0-harvest-before-fell/v1.44.0-harvest-before-fell.min.rs`
- `cgauto/submissions/v1.44.0-harvest-before-fell.rs`
- `cgauto/submissions/v1.44.0-harvest-before-fell.min.rs`

## Mini-Gate

First implementation was too broad: it protected all nearby ripe fruit, including ordinary
idle-fruit band 38. Boss 8 failed:

- Result: `0/8 wins | our wood 40 | opp wood 58`.
- Ramp: t75 `+3.2`, t150 `-0.4`, t225 `-6.9`, t300 `-17.8`.
- Diagnosis: late wood fell behind; narrowed the rule to funding/printer/Hoard fruit only.

Narrowed implementation:

- Boss 8:
  - `2/8 wins | our wood 42 | opp wood 51`.
  - Ramp: t75 `+2.2`, t150 `+0.2`, t225 `-3.4`, t300 `-9.8`.
  - Formal ramp aggregate: wins `2/8 (25%)`, our avg final wood `41.6`, late gain us `+9.6`
    vs opponent `+16.0`.
- Field `plcc` (`6480966`):
  - `1/2 wins | our wood 50 | opp wood 38`.
- Field `mikdiet` (`6480914`):
  - `0/2 wins | our wood 84 | opp wood 96`.
  - Mixed, not a wood crater; one loss had us ahead on wood (`93-86`).

Mini-gate verdict: **PASS-WATCHLIST**. The broad rule was rejected locally; the narrowed rule
cleared Boss and plcc enough to submit, with mikdiet left as watchlist risk.

## Arena

Bracket before submit:

- `2026-07-08 22:13 MSK`: `ARENA-ROOM: tass rank 116/527 Gold score 18.4 | agentId=6543753`
  (`v1.43.0-yield`).

Submission:

- Command: `uv run --no-sync python cgauto/api_submit.py
  cgauto/submissions/v1.44.0-harvest-before-fell.min.rs`
- Time: `2026-07-08 22:13 MSK`.
- Submit id: `40969606`.
- Result: `SUBMIT-OK via TestSession submit`.

Reads:

- +20m (`2026-07-08 22:34:04 MSK`):
  `ARENA-ROOM: tass rank 136/527 Gold score 16.9 | promotable=False | agentId=6543779`.
  Delta vs bracket `18.4`: `-1.5`.
- +35m (`2026-07-08 22:48:44 MSK`):
  `ARENA-ROOM: tass rank 182/527 Gold score 15.8 | promotable=False | agentId=6543779`.
  Delta vs bracket `18.4`: `-2.6`.

Verdict: **REJECT / REVERTED**. v1.44.0-harvest-before-fell did not improve the Gold arena
rating; it fell from the v1.43 bracket `18.4` to `15.8` by the +35m read. The local narrowing
fixed the Boss mini-gate crater, but the arena signal says the feature damages the live field.

Restore:

- Command: `uv run --no-sync python cgauto/api_submit.py cgauto/submissions/v1.43.0-yield.min.rs`
- Time: `2026-07-08 22:49 MSK`.
- Submit id: `40969730`.
- Result: `SUBMIT-OK via TestSession submit`.
- Restore confirmation read (`2026-07-08 23:11:18 MSK`):
  `ARENA-ROOM: tass rank 180/527 Gold score 16.0 | promotable=False | agentId=6543791`.
  This confirms the arena slot moved off rejected v1.44 agentId `6543779`; the restored v1.43
  artifact was still in early reconvergence at this read.
