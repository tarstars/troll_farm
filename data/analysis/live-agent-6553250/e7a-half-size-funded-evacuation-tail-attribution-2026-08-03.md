# E7a half-size funded-evacuation tail attribution

Date: 2026-08-03 UTC
Task: `20260802-e7a-half-size-logical-simplification`
Baseline: 62,820 bytes, SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`

## Result

The 31,405-byte period-2 lean-coordination source was rejected on untouched seeds
9,864,000--9,864,042 only because catastrophes increased 26 to 27. Cumulative replay on
that now-consumed panel isolates the categorical regression to one simplification: replacing
the original conditional funded-shack evacuation with an unconditional evacuation command.
Removing the speculative stock-compatibility/helper blocks is not the cause.

A distinct successor now exists at 31,248 bytes, SHA-256
`a767e36228c872ad566b4347825f5282f95e50ae9f59fcf5a42b682989d85fea`.
It retains the original funded-shack evacuation, removes other behavior-neutral blocks, and
replaces the larger three-state A-B-A landing history with a readable previous-observed-cell
backtrack guard. It removes 31,572 bytes, or 50.258%, from the exact live source and is 162
bytes below the 31,410-byte ceiling. Its manifest records no identifier renaming, minification,
compression, or formatting-based reduction.

The successor passes standalone compilation, empty input, ten semantic fixtures, all 25 exact
live period-2 counterexamples, and both 516-task consumed panels. It is development-qualified,
not transfer-qualified. A newly collision-audited untouched panel remains mandatory before any
Arena action.

## Cumulative attribution on the consumed transfer panel

All rows use the same official seeds 9,864,000--9,864,042, six opponent families, both seats,
and 50,000 bootstrap samples. These are diagnostic replays after the terminal verdict and cannot
qualify a source.

| Cumulative source | Bytes | Change added at this step | Mean | 95% lower | Catastrophes | Negative mass |
|---|---:|---|---:|---:|---:|---:|
| slot-period2 parent | 32,332 | none | +10.2771 | +2.7112 | 26 -> 26 | 6,149 -> 5,371 |
| D1 | 31,848 | remove stock compatibility/helper blocks | +10.0581 | +2.5174 | 26 -> 26 | 6,149 -> 5,374 |
| D2 | 31,614 | also collapse funded-shack evacuation | +9.4574 | +1.7442 | **26 -> 27** | 6,149 -> 5,421 |
| rejected 31,405 source | 31,405 | also remove terminal occupied-door/live-health blocks | +9.4574 | +1.7442 | **26 -> 27** | 6,149 -> 5,421 |

D1 preserves the categorical gate and nearly all value. D2 exactly reproduces the terminal
31,405-byte candidate's metrics before the final two deletions are applied. Therefore:

1. the stock simplification is safe on this panel;
2. the unconditional funded-shack evacuation is the observed catastrophe cause;
3. terminal occupied-door prefiltering and the live-tree health predicate are behavior-neutral
   on this panel.

This is mechanism attribution on consumed evidence, not a tuned threshold or a new qualification.

## Distinct 31,248-byte successor

Source:
`local_codex_1/e7a-half-size-logical-simplification/focused-yamo-bank-convoy-no-backtrack.rs`

The successor starts from D1 and therefore keeps the exact original funded-shack evacuation.
It removes the terminal occupied-door prefilter, dead live-row health predicate, and unused
selector inventory parameter. To fund liveness below the ceiling, it replaces the larger
three-state landing history with one previous observed cell per stable worker slot: a proposed
landing that immediately returns to that prior cell becomes `WAIT`; otherwise normal policy and
conflict resolution remain in force. This is a direct logical simplification, not an identifier
or lexical-size transformation.

Rebuilding the source and manifest from the exact 62,820-byte baseline is byte-identical. The
candidate compiles with optimized standalone `rustc`, accepts empty input, and leaves
`rust/src/bin/yamo_orchard_live.rs` exact at SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Validation evidence

### Semantic and motion packets

- semantic fixtures: 10/10 pass, zero malformed commands and zero unexpected stderr;
- 16-game motion smoke: mean margin delta -2.75, catastrophes 2 -> 1, maximum period-2
  target run 6 -> 2, and the same first training event in 16/16 games.

### Exact live liveness packet

The locked public packet contains all 25 live E7a games whose observed period-2 MOVE run is at
least six, including game `897832286` with the 127-turn observed episode.

- verdict: `LIVE_PERIOD2_PACKET_PASS`;
- games: 25/25;
- candidate maximum period-2 run: 4;
- candidate games with period-2 >= 6: 0;
- command lines: 7,234;
- unknown state updates: 0;
- candidate stderr bytes: 0.

This is teacher-forced liveness evidence on official states, not a counterfactual score estimate.

### Consumed development panel, seeds 9,854,000--9,854,042

- verdict: `QUALIFIED_OPEN_PANEL` within the development-only evidence boundary;
- tasks: 516;
- mean margin delta: +9.1415;
- bootstrap 95% lower bound: +3.8585;
- catastrophes: 19 -> 14;
- negative-margin mass: 4,138 -> 3,871;
- all six family means positive;
- seat means: +13.4419 and +4.8411;
- worker-two coverage: 516/516, median delay zero;
- period-2 >= 6: 115 -> 0;
- latency p95 ratio: 0.8562; maximum 1.125 ms;
- all gates pass.

### Consumed transfer diagnostic, seeds 9,864,000--9,864,042

- evidence boundary: diagnostic only; qualification is forbidden;
- tasks: 516;
- mean margin delta: +10.2597;
- bootstrap 95% lower bound: +2.6124;
- catastrophes: 26 -> 26;
- negative-margin mass: 6,149 -> 5,374;
- all six family means and both seat means positive;
- worker-two coverage: 516/516, median delay zero;
- period-2 >= 6: 105 -> 0;
- latency p95 ratio: 0.8479; maximum 1.110 ms;
- all analytical gates pass.

## Evidence boundary and next action

The candidate has not seen a qualifying untouched map. Neither strong performance on the original
development panel nor diagnostic recovery on the consumed rejection panel authorizes Arena use.
The next action is to collision-audit a new 43-map range, publish an immutable one-shot lock, and
run it once. A terminal fresh rejection stays terminal. Arena mutation remains forbidden until an
exact source passes that gate and the promotion preflight.
