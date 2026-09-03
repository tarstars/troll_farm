# Three-troll bot with a wood-aware optimized start

This directory contains an isolated candidate built from the current denial-off champion. It is
not the dead Stage 2A policy with a different constant. The previous candidate forced almost the
whole opening toward the third-troll bill; it trained a third troll at median turn 147 against the
real field and lost 4.13 ladder points. This candidate treats a third troll as an investment that
must beat the wood the existing trolls could bank instead.

## Policy

The opening has three layers.

1. **Second troll:** reuse the Stage 2A turn-1/turn-2 second-troll rule. This is the separable half
   that occurred on turn 2 in all 160 real ladder games of the dead candidate. Until that train,
   the deterministic Stage 2A dispatcher remains the fallback.
2. **Third troll:** when two trolls stand, evaluate the complete small roster set
   `1/1/0/1`, `1/2/0/1`, `2/2/0/1`, `2/2/0/2`, `2/3/0/1`, `2/3/0/2`, `2/3/0/3`.
   For each tuple, an exact enumeration splits every missing plum, lemon, apple and iron unit
   between the two workers. Resource curves include travel, carrying, harvesting or mining,
   banking, regrowth and a conservative contest rule. Current fruit is treated as unavailable
   when an opponent harvester has an equal or better lower-bound arrival time, and subsequent
   fruit is charged two cooldowns. The plan is rejected unless its contested completion is no
   later than turn 110 and its estimated incremental value is at least eight points after charging
   the existing trolls' best visible wood rates and the consumed fruit.
3. **Execution and fallback:** the dynamic program produces resource shadow prices. Funding trips
   and ordinary four-point wood trips compete on the same points-per-turn scale. The plan is
   re-evaluated every five turns from the live board. If it no longer passes, the opening ends and
   the unchanged champion resumes immediately. After a third troll is trained, the existing
   generalized joint selector chooses all three commands together.

The value estimate is intentionally conservative and bounded by the standing wood visible on the
board. It is a policy gate, not a proof of eventual game score.

## Control

The generator also writes a control that differs by one constant: third-troll optimization is
disabled. It still carries the turn-2 second-troll opening. Candidate minus control therefore
measures the third-troll optimizer rather than crediting it for the already-known second-troll
change.

## Build

```bash
python3 chatgpt_1/three-troll-optimized-start/make_candidate.py
```

Outputs remain in this directory:

- `champion-three-troll-optimized-v6-instrument.rs`
- `three-troll-optimized-readable.rs`
- `candidate-three-troll-optimized-v6-instrument.rs`
- `three-troll-optimized.diff`
- corresponding `turn2-second-control` files
- `results/build.json` and `results/control-build.json`

The generator applies anchored edits to both the diagnostic arm and readable champion, compiles
both, compacts the diagnostic arm, verifies token-stream round-trip identity, checks that candidate
and control are distinct from existing bots, and refuses a source at or above 100,000 UTF-16 code
units.

## Validation

The branch-only workflow runs:

1. the 34-situation deterministic/compaction/telemetry bed;
2. the frozen 24-map smoke with allowed third-troll tuples;
3. one-core per-turn timing;
4. a direct candidate-versus-control panel;
5. candidate and control against the champion and orchard 6 on identical maps and seats, followed
   by the repository's clustered paired reading.

`analyse_results.py` writes `results/summary.json` and `RESULTS.md`. No ladder or platform action is
part of this artifact.

## Pre-registered stop conditions

The candidate is dead as a bot when any mechanics/round-trip check fails, warm p99 is at least
40 ms, it never trains a third troll by turn 110 on the smoke, or its paired win difference versus
the control is below -0.05 with the entire 95% interval below -0.05. A dead result remains useful
as an instrument and is still recorded.
