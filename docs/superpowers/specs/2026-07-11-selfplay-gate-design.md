# Paired self-play A/B gate (`abgate`) — design

**Status: DRAFT — pending user approval** (user AFK at decision time; head-to-head opponent
model chosen per controller recommendation, revisit on review). Origin: rethink finding #1/#2
(docs/strategic-rethink-2026-07-11.md) — the measurement instrument is the binding constraint;
this gate is the enabler for everything else (macro-candidates, salvage protocol, scale
experiments).

## Purpose (one sentence)
A cheap, high-n, paired REJECT filter that kills arena-loser candidates locally before they
cost an arena slot — it does NOT accept candidates (the arena remains the judge).

## What it is
New bin `rust/src/bin/abgate.rs`:

```
cargo run --release --bin abgate -- <candidate_bin> <champion_bin> [seeds=200] [max_turns=300]
```

- For each seed: TWO games on the same `generate_bronze(seed)` map (real Gold-class: h 8-11,
  mirror-symmetric, iron/water, ~18 trees) — candidate in seat 0 vs champion in seat 1, then
  seats swapped. Driven over the real CG protocol + `engine::step`, exactly like equality.rs.
- **Pair delta** = mean of (candidate_score − champion_score) over the two seatings. Same map
  + both seats cancels map luck and side bias. Deterministic bots ⇒ reproducible runs.
- Output per run: mean pair delta, SD, 95% CI (t-based over seeds), W/D/L, wood-delta and
  fruit-delta decomposition (score = fruits + 4·wood), crash count. Verdict line:
  - `GATE: REJECT` — CI entirely below 0 (candidate provably worse vs champion locally), or
    any candidate crash.
  - `GATE: PASS-TO-ARENA` — otherwise (including CI containing 0). PASS ≠ good; it means
    "not provably worse locally."
  - Numeric thresholds beyond the sign test are set AFTER calibration (below), not guessed.

## Architecture
Extract the game-driving loop (`Bot`, `grid_rows`, `turn_block`, `read_cmds`, `play`) from
`equality.rs` into a shared lib module `src/game/driver.rs`; `equality.rs` and `abgate.rs`
both consume it. Alternatives considered: (a) `--score` mode inside equality.rs — rejected,
entangles an exactness-assertion tool with a statistics tool; (b) copy the ~80 driver lines —
rejected, the driver is exactly what later tools (pool sparring, etude-vs-bot) will reuse.
Refactor safety: equality.rs is re-validated after extraction by a self-equality run
(bot vs itself, 50 seeds — must print EQUAL) plus the existing test suite.

Differences from equality's `play`: return final `GameState` (scores via recompute) instead
of command lines; on bot crash/EOF, that side plays WAIT for the remainder and the game is
flagged. Crash semantics: CANDIDATE crash ⇒ automatic REJECT; CHAMPION crash ⇒ the run is
INVALID (harness/environment problem — fix and rerun, no verdict). Flagged games are always
reported separately, never silently pooled.

## Exact self-test invariant (the plumbing proof)
Self vs self (same binary both roles): for every seed, game(swap) is the SAME matchup with
labels exchanged, so pair delta ≡ 0 exactly. This is the integration smoke test (5 seeds) and
validates the seat-swap plumbing end to end. Unit tests cover the paired-stats math on
synthetic data (mean/CI/W-D-L, crash flagging).

## Calibration study — the gate's own acceptance test (run BEFORE trusting it)
Compile the frozen artifacts (rustc each .min.rs) and run n=200 seeds each, candidate vs its
historical base:

| pair | arena verdict (known) | gate must show |
|---|---|---|
| ringfix3 vs ringfarm | +1.1 KEEP | delta > 0 |
| ringtune vs ringfarm | −2.4 REVERT | delta < 0 |
| trainfruit vs ringfarm | −3.2 REVERT | delta < 0 |
| fellmission vs ringfix3 | −1.0 REVERT | delta < 0 |
| chopharvest vs ringfix3 | −5.0 REVERT | delta < 0 |

Acceptance: sign agreement ≥4/5 AND all three big losers (ringtune, trainfruit, chopharvest)
caught. Then set the REJECT threshold from the observed spread. If a known loser slips
through, escalate the design (frozen-pool sparring variant) before adopting; the head-to-head
blind spot (field-strategy interactions, e.g. seedloop's gifts-to-cc3) is accepted and is why
PASS still goes to the arena.

## Process integration
Pipeline becomes: build → review → **abgate (REJECT filter)** → boss/field probes as needed →
arena (judge). Verdict log records gate deltas next to arena deltas — every future candidate
extends the calibration corpus for free.

## Not in v1 (YAGNI)
Field-panel play-API games (separate existing tooling), per-map-class breakdown, parallel
execution (sequential 400 games is minutes; add rayon only if painful), telemetry parsing.

## Success criteria
1. equality.rs still EQUAL post-refactor; suite green. 2. Self-vs-self pair delta exactly 0
per seed. 3. Calibration acceptance met. 4. One documented run wired into the candidate
process docs (arena-queue policy note).
