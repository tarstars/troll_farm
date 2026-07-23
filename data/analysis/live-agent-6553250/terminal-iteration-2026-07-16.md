# Terminal iteration — 2026-07-16

## Outcome

Low-supply pre-seeding is the first candidate in this roadmap to clear the corrected local
evidence ladder.  It gains **+0.259 paired margin** and **+0.115 wood** over 1,000 seeds, with
221 wins / 655 ties / 124 losses.  The live artifact was not modified and nothing was submitted.

Candidate:
`cgauto/submissions/candidate-agent6553250-preseed-low-supply.min.rs`
(90,548 bytes, SHA-256
`6bc52f199f79cf891fcd3a0a3745b43dbf67485581c7baa6194505f9a36e7397`).

## Evaluator correction

The active Rust and Python evaluators now reproduce the referee's persistent no-tree grace,
resource-based stuck test, and mercy termination.  Carried iron does not keep a player alive;
carried fruit or wood does.  The correction is covered independently in both languages and is
used by the active equality, tournament, telemetry, renewable, and live-variant runners.

This invalidates the old fixed-300 timing verdict.  In corrected exact-live self-play, 58/60
matches end by stall at median turn 129.  The live bot already replants successfully from an empty
board in 45/60 matches, for 148 replant episodes.  The mechanism worth testing was therefore not
a persistent mother loop, but advancing a normal seed pickup before the terminal supply cliff.

## Behavior-neutral evidence

The 200-game terminal panel records:

- 196 stall endings and 180 games within 20 points;
- 0.948 mean final cargo value per side that is statically cashable inside implied grace;
- only one game where that cargo changes the projected result;
- 809 last-tree removals, 612 empty-board replants, and 155 games with a replant;
- 422 unique selected-tree commitments where the opponent's static bank ETA is lower;
- 45 such commitments with the live focus gate active, spread over 30 games.

The ETA model is deliberately static: one worker, no future growth, and no shared chopping.  It
is activation telemetry for the next candidate, not a causal estimate of its benefit.

Historical coverage contains 13 live losses within 20 points and 13 unique matched close wins.
All 26 decoded fixtures match official diff updates, turn counts, final inventories, final
scores, and early-end timing.  Nineteen reconstructed input streams also reproduce every
baseline command and are admissible for the causal selection check; the other seven are retained
with their first mismatch but excluded from that gate.

## Candidate mechanism

From turn 100 onward, the candidate adds a high-priority `PICK` only when all of these are true:

- at most two plants remain;
- at least two own units exist;
- the unit is empty and orthogonally adjacent to its shack;
- banked fruit is available;
- the unit's cell has no plant and the regeneration safety gate is open.

It adds no farmer role, shared-mother protection, far travel, or persistent commitment.  The
existing planner remains responsible for the subsequent plant action.

## Gates

| Gate | Result |
|---|---|
| Inactive region | 200/200 command streams byte-identical through turn 99 |
| Historical causal selection | activates in 14/19 admissible streams: 7 close losses and 7 matched wins |
| First-divergence integrity | 14/14 eligible; median turn 113; none before turn 100 |
| Paired local outcome | +0.259 margin, +0.115 wood, 221/655/124 over seeds 0–999 |
| Sampling uncertainty | SD 1.969, SE 0.0623, normal 95% interval [+0.137, +0.381] |
| Behavioral displacement | −0.069 CHOP, −0.773 MOVE, +0.209 PICK, +0.246 PLANT per seed |
| Artifact | standalone `rustc` compile passes; 90,548 bytes; deterministic SHA recorded |
| Regression | 195 Python tests pass; full release Rust test suite passes |

The paired simulator is a self-harm gate, not an arena predictor.  The candidate therefore
qualifies for a small controlled field test, but this iteration does not authorize one.

## Initial decision

Preserve exact live source
`cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs` and retain pre-seeding as a locally
qualified branch.  The subsequent sweep started with the 45 focus-gated losing commitments
rather than applying a global focus change.

Machine-readable evidence:

- `preseed-low-supply-stall-corrected-1000.json`;
- `preseed-historical-stream-gate.json`;
- `renewable-supply-stall-corrected-2026-07-16.json`;
- `terminal-race-telemetry-2026-07-16.json`;
- `terminal-fixtures/manifest.json`.

## Ten-direction follow-on

The remaining roadmap directions were executed after this initial gate.  Static opponent ETA
filtering, dynamic training denial, a three-worker sequence, score-state extensions, terminal
harvest bundles, and a remembered-tree motion bonus did not qualify.  Two ablations confirmed
that the live exhaustive two-worker assignment and behind/low-supply endgame switch should be
kept.  The motion audit found no block, landing, or door-stall defect.

Broader safe secure-orchard geometry is the second local survivor: +3.7625 margin and +0.4525
wood, with 26 wins / 973 ties / 1 loss across 1,000 seeds.  Composed with pre-seeding, the result
is +4.025 margin and +0.5715 wood, 244/632/124, with 95% interval [+2.405,+5.645].  The two
effects are exactly additive in both margin and wood on 996/1,000 seeds.  The combined artifact
is `candidate-agent6553250-preseed-orchard-coverage.min.rs`; no platform game or submission was
performed.  Full evidence and caveats are in `direction-execution-2026-07-16.md`.
