# Candidate v1.45.0-earlyroam - Builder Report

**Task:** widen the opening tree pool for the real chopper only. The idea came from the
champion loss taxonomy's burst-chopper bucket: some opponents show near-zero chop through
turns 1-75, then convert into a large wood burst. The hypothesis was that our existing chopper
could bank extra early wood by claiming one more safe roam ring before that burst starts.

## What changed

- `rust/src/botmain.rs`
  - `VERSION` bumped to `1.45.0-earlyroam`.
- `rust/src/botmain/planner.rs`
  - Added an opening-only chopper roam flag:
    - true chopper only,
    - `Phase::Tempo` only,
    - turns `<=75`,
    - disabled in liquidation.
  - When active, primary fell candidates get:
    - one extra farm-distance roam ring,
    - one-cell tolerance past the raw own-half split.
  - Starter chop-help and anti-starvation fallback remain champion behavior.
- `rust/tests/early_roam.rs`
  - Pinned the one-ring opening upgrade.
  - Pinned late-game champion behavior.
  - Pinned that starter chop-help is not upgraded.

## Gates

- Focused suite:
  - `cargo test --release --test early_roam`
  - Result: `3 passed`.
- Full Rust release suite:
  - `cargo test --release`
  - Result: all active tests passed, including `early_roam` and `yield_pass`.
- Self-determinism:
  - `./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Bundle/minify:
  - `python3 tools/bundle.py src/botmain.rs target/refactor/v1450_earlyroam.rs`
  - Bundled source: `95623` chars (`97036` bytes); compiled with `rustc --edition 2021 -O`.
  - `python3 tools/minify.py target/refactor/v1450_earlyroam.rs
    target/refactor/v1450_earlyroam_min.rs`
  - Minified source size: `57515` bytes; compiled with explicit crate name.
- Bundled equality:
  - `./target/release/equality target/refactor/v1450_earlyroam_bin target/release/bot
    8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Minified equality:
  - `./target/release/equality target/refactor/v1450_earlyroam_min_bin target/release/bot
    8 300 target/release/bot`
  - Result: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.

## Frozen Artifacts

- `data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.rs`
- `data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.min.rs`
- `data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.debug.rs`
- `data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.debug.min.rs`
- `cgauto/submissions/v1.45.0-earlyroam.rs`
- `cgauto/submissions/v1.45.0-earlyroam.min.rs`

## Mini-Gate

DEBUG probe:

- Built from `data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.rs` by flipping
  `const DEBUG: bool = false;` to `true`.
- Minified to `data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.debug.min.rs`.
- Compile-check passed with explicit crate name:
  `rustc --crate-name v1450_earlyroam_debug --edition 2021 -O ...`.
- DEBUG minified size: `57514` bytes.

Boss pool:

- Command: `uv run --no-sync python cgauto/collect_debug_games.py
  data/candidates/v1.45.0-earlyroam/v1.45.0-earlyroam.debug.min.rs boss 8`
- Result: `0/8 wins | our wood 40 | opp wood 53`.
- Formal ramp (`uv run --no-sync python cgauto/ramp.py --last 8`):
  - `t75 delta +3.2`
  - `t150 delta +1.8`
  - `t225 delta -4.6`
  - `t300 delta -13.4`
  - aggregate: `wins 0/8 (0%)`, our avg final wood `39.9`, late gain `+11.6`
    vs boss `+20.4`.

Mini-gate verdict: **LOCAL REJECT / NOT SUBMITTED**. The feature gives the expected early wood
lead through t150 but does not solve the burst shape; by t225 the opponent has recovered and by
t300 the candidate is clearly losing. No arena submission was made. Active source was restored
to the promoted v1.43 behavior before continuing.
