# E7a half-size tree-edge reversal attribution — 2026-08-03

Status: **CONSUMED-DIAGNOSTIC PASS / DEVELOPMENT PANEL PENDING / NO ARENA ACTION**

## Exact source

- Candidate:
  `local_codex_1/e7a-half-size-logical-simplification/focused-yamo-bank-convoy-tree-edge-reversal.rs`.
- Size: **31,407 bytes**, three bytes below the 31,410-byte ceiling and a
  **50.004776%** logical reduction from the exact 62,820-byte live E7a source.
- SHA-256: `acbada47b9a3cf279ff5356a32e2965eb44cbb5ccc8d7b7e8c6f5dda3f92e847`.
- The manifest records `identifier_renaming=false` and `minification=false`.
- Optimized standalone compilation and all ten semantic fixtures pass.
- Sacred `rust/src/bin/yamo_orchard_live.rs` remains exact at SHA-256 `fff6669b...`.

The source retains the exact funded-shack evacuation which categorical attribution showed to
be necessary. It removes unreachable zero-chop and zero/over-two-worker branches, specializes
the internal MOVE parser to the controller's own uppercase commands, and replaces a global
movement guard with one observable rule:

- a second consecutive A-B reversal is stopped when either endpoint is a tree;
- otherwise at most three consecutive reversals are allowed, so an episode cannot reach six
  MOVE decisions.

This is a state-machine and unreachable-branch simplification, not lexical compression.

## Trace-derived mechanism

The global strict and five-step guards transferred in opposite directions. Exact single-task
traces on consumed seeds isolated the distinction:

| Task | Strict guard | Five-step/role guard | Tree-edge guard | First relevant reversal |
|---|---:|---:|---:|---|
| 9,865,036 seat 0 vs legend | +117 | -96 | +117 | trained worker leaves a just-chopped tree |
| 9,865,038 seat 0 vs legend | +32 | -69 | +32 | starter returns onto a damaged tree |
| 9,865,021 seat 1 vs resident | -4 | +16 | +16 | empty route correction; neither endpoint is a tree |

The earlier opponent-workforce discriminator was falsified: the first damaging legend
divergence occurred before opponent scaling. Own-roster and fixed-role thresholds also failed
the full family gate. The tree-edge predicate expresses the observed movement state directly
and reproduces the desired branch on all three traces. Exact trace paths, source hashes, margins,
and trace hashes are frozen in `tree-edge-reversal-trace-comparison.json`.

## Exact live-liveness packet

The 25 exact E7a live counterexamples all pass under teacher forcing:

- 25/25 games fetched and decoded;
- zero unknown updates and zero stderr;
- candidate maximum period-2 run **5**;
- zero games at or above six.

This is an official-state liveness regression gate, not a counterfactual value estimate.

## Consumed transfer diagnostic

The exact source was evaluated on preserved seeds 9,865,000--9,865,042 only for attribution.
Those seeds were consumed by the prior no-backtrack verdict and cannot qualify this source.
All thirteen analytic gates pass over 516 tasks:

- mean paired margin **+4.67829**;
- bootstrap 95% lower bound **-0.29264**;
- catastrophes improve **14 -> 8**;
- negative-margin mass improves **3,908 -> 3,422**;
- both seats are positive: +4.2016 and +5.1550;
- worker-two coverage is 516/516 with median delay zero;
- period-2 >=6 improves **90 -> 0**, maximum four in closed-loop simulation;
- latency p95 ratio is 0.8365, maximum 1.084 ms;
- zero critical and unclassified issues.

| Opponent family | Mean delta |
|---|---:|
| compact-gold | +5.9070 |
| gold-adaptive | +4.5349 |
| legend-balanced | +0.3953 |
| mybot | +6.0116 |
| norx-native-three | +12.5233 |
| resident | -1.3023 |

Five of six families are nonnegative, so the frozen breadth rule passes. This is stronger than
the terminal 31,248-byte source on the same rows, but remains development evidence only.

## Next boundary

Run the exact source on the ordinary consumed 9,854,000--042 development panel and the motion
packet. Only if every gate passes may a new seed range be collision-audited and frozen before
one-shot untouched execution. No Arena mutation follows from this diagnostic result.
