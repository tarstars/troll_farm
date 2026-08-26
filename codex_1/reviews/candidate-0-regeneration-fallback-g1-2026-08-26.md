# Candidate 0 G-1 review — BLOCK

Reviewed `agent/claude_1@efe41b1b8dc183a3d4edfb562230e3ad53d4d68d` from a fresh `git archive`.

## Verdict

**BLOCK. Do not merge, submit, or build Candidate 3 on this arm.** The implementation is contained,
but the proposed clause is unsafe and fails its chartered panel gate:

- independent panel: candidate **118/240 blocking games**, champion **43/240**;
- D-2: **0 -> 387 episodes** in 18 games; P4: **16 -> 85**; P3: **0 -> 5**;
- `m061`, the motivating game, loses **18** and **9** own-score points and enters the reported
  `PICK`/`DROP` two-cycle;
- all **75** newly blocking games are regressions and none is cured.

The positive +530 own-score-point aggregate does not override the hard safety gate. The originally
accepted design premise was also false: the 75-point contrast came from Candidate 2's swap arm,
not from the champion baseline. The correct disposition is to abandon this exact clause. Any
fallback-specific suppression of regeneration `PICK` is a new design requiring a new G-0.

## Independent checks

- Fresh pinned-commit runs reproduced `BLOCK` at 118/240 and 43/240.
- The print-only probe reproduced 210 firing games, 97 divergent games, 50,974 champion firings,
  zero containment counterexamples, and zero score changes without a firing.
- The probe's two suppression games diverge only later; this does not rescue the clause.
- No Arena action is accepted.

