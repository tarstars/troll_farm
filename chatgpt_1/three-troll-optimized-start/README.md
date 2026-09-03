# Three-troll bot with a wood-aware optimized start

**Executed verdict: `DEAD_AS_BOT`.** The candidate is preserved as an instrument, not offered for
promotion. See `RESULTS.md` and `results/summary.json` for the executed evidence.

This directory contains an isolated candidate built from the denial-off champion. It is not the
dead Stage 2A policy with a different constant. The corrected replay reading shows that Stage 2A
trained its third troll at median game turn **74.5**, not 147; 147 was the replay frame index before
the frame-to-turn conversion was fixed. Stage 2A nevertheless lost 4.13 ladder-rating points.
Its second troll appeared on turn 2 in all 160 field games, which proves that the behavior occurred,
not that the second-troll change was independently beneficial.

## Policy tested

The opening has three layers.

1. **Second troll:** reuse the Stage 2A turn-1/turn-2 second-troll rule. Until that train, the
   deterministic Stage 2A dispatcher remains the fallback.
2. **Third troll:** when two trolls stand, evaluate the small roster set `1/1/0/1`, `1/2/0/1`,
   `2/2/0/1`, `2/2/0/2`, `2/3/0/1`, `2/3/0/2`, `2/3/0/3`. For each tuple, exact enumeration
   splits every missing plum, lemon, apple and iron unit between the two workers. Resource curves
   include travel, carrying, harvesting or mining, banking, regrowth and a conservative contest
   rule. A plan is rejected unless its contested completion is no later than turn 110 and its
   estimated incremental value is at least eight points after charging foregone wood and consumed
   fruit.
3. **Execution and fallback:** the optimizer emits resource shadow prices, so funding trips and
   ordinary four-point wood trips compete on one points-per-turn scale. The plan is re-evaluated
   every five turns from the live board. If it no longer passes, the opening ends and the unchanged
   champion resumes. After a third troll is trained, the generalized joint selector chooses all
   three commands together.

The value estimate is a bounded policy gate, not a proof of eventual game score.

## Matched control

The generator also writes a control that differs by one constant: third-troll optimization is
disabled. It still carries the turn-2 second-troll opening. Candidate minus control therefore
isolates the third-troll optimizer instead of crediting it for the shared opening change.

## Build

```bash
python3 chatgpt_1/three-troll-optimized-start/make_candidate.py
```

The generator writes the readable source, compacted candidate and control, diffs, hashes and build
reports. It compiles both forms, verifies exact token-stream round trips, checks distinctness from
existing bots, and refuses a source at or above 100,000 UTF-16 code units.

## Executed validation

- Both 34-situation deterministic/compaction/telemetry beds passed.
- Candidate smoke passed the stall/mechanics gate on 19/24 maps. Five maps entered long funding
  stalls, which is a pre-registered death condition.
- A third troll was trained in 14/24 smoke games, always by turn 110: p25 / median / p75 were
  turns 10 / 30 / 56. The chosen tuples were `1 1 0 1` ten times and `1 2 0 1` four times.
- Candidate source size was 90,070 UTF-16 units. Warm p99 turn time was 1.045 ms.
- In the direct 200-game matched-control duel, the candidate went 51 wins, 57 ties and 92 losses;
  score-margin difference was -0.97 with 95% interval [-1.81, -0.24].
- Against the two-opponent external panel, candidate minus control was +0.050 wins per game with
  95% interval [+0.005, +0.095]. This was opponent-specific: -0.015 versus the champion and
  +0.115 versus orchard 6. It does not override the smoke death or direct-control loss.

No ladder, platform, cluster or Arena action was taken.
