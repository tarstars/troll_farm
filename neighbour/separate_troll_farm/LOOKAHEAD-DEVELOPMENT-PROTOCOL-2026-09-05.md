# V439 sequence-planning development experiment

Mechanism: compare complete short action sequences instead of only V439's existing joint
immediate-action scores. Each root owns a clone of the entire controller before its decision;
commit the chosen root's post-decision memory, never a simulated leaf or a losing branch.
Rank zero retains the exact original selector. Neither canonical production file is modified.

Initial configuration (frozen before gameplay inspection): start turn 220, eight-turn horizon,
three distinct roots from ranks 0 through 6, V439 continuations for both players, minimum
estimated improvement one point. Terminal value is official banked score difference; nonterminal
value also credits carried fruit/wood at 0.9/(1+0.04*banking turns), only if bankable by turn 300.
Physical player order and original IDs are preserved, including simultaneous TRAIN allocation.
The opponent continuation is a hypothesis, not an assertion about the actual opponent.

An 18 ms soft search budget includes the root controller. Any incomplete rollout, unsupported
MOVE or critical legality issue returns the exact rank-zero branch; never compare unequal-depth
values. The soft budget is checked between decisions, not a hard execution guarantee. Full
protocol/startup timing and packaged/readable equivalence remain mandatory before publication.

Development budget: rank-zero A/A on all 160 restored V439 replays, behavioral adapter/branch
fixtures, timing and observed-state diagnostics, then at most the existing eight-map/12-family
panel once for this frozen configuration. Replayed actions do not adapt and are not competitive
evidence. The panel is consumed development data, not a rank predictor. Reject a configuration
that fails correctness/source/runtime gates; report timeouts and all game failures explicitly.
No unranked platform requests or publication follow automatically: a separate fresh, fixed-agent
paired protocol must be frozen after development results support a finalist.

Source-size work may shorten identifiers without changing literals or gameplay. Compilation,
token/literal invariants and exact command audits are required; lexical rewriting alone is not
a semantic proof. The weaker `next_bot` is not selected merely because it leaves more room.

Runtime amendment after the first eight-stream diagnostic (no competitive games opened):
18 ms deadline fallback occurred on 197/391 readable searches, and one packaged/readable
decision differed at the deadline. This is a failed deployment-equivalence gate, not a strength
result. Add an exact, bounded terrain/source-keyed distance cache to reduce repeated policy
BFS work; compare cached and uncached distances plus all 160 rank-zero streams. No horizon,
root, value or start-turn coefficient is changed. Retest timing/equivalence before any panel.

Second runtime amendment: the cache reduced fallback to 1/391 searches and observed packaged
differences to zero in those eight streams. However deadline-dependent output remains inherently
sensitive to scheduling. Remove clock-dependent selection; bound work deterministically at the
same three roots/eight turns/six candidate ranks, skip simulation when only one distinct root
exists, and retain the unsupported/critical-issue baseline fallback. Profile all 160 streams
and exact packaged/readable outputs with no overlapping CPU-heavy job before opening the panel.
The earlier 18 ms mode is preserved in exported artifacts, not the current development source.
This is not a guarantee that the fixed-work planner meets the platform's 50 ms limit.

Full fixed-work diagnostic: 43,263 turns across 160 games, zero readable/packaged differences,
but 42 over-budget turns in each build, worst about 9.25 seconds. This configuration fails the
runtime gate and cannot enter competitive tests. The 846 changed root selections establish
only that the mechanism executes. Investigate per-phase timing; do not hide these failures in
the mean or restore a nondeterministic timer as a purported semantic-equivalence proof.

Pre-panel advancement decision (still no competitive games opened): require positive paired
match-point delta versus V439, negative point deltas on no more than four of the eight shared
maps, complete 192-game arms and zero critical/unclassified issues. Also require the complete
observed-state timing/equivalence gate and no panel turn exceeding 50 ms. Positive margins alone
do not qualify. These criteria can justify only a new frozen real-agent screen, not publication.
The local runner applies the same new-plant row-major repair to both arms and counts repairs;
do not compare its scores as exact reproductions of older, uncorrected panel executables.

Runtime gate now passes on the same 160 complete streams: after exact streaming top-k selection,
43,263 turns per build, zero decisions over 50 ms, maxima 28.579/28.747 ms, zero readable/packaged
differences and zero command differences versus the preserved slow full-sort planner. Both select
846 changed roots in 9,635 searches with zero fallbacks. This supports opening the frozen local
panel, not a platform publication or a strength claim. The panel uses one worker thread to avoid
introducing self-inflicted timing contention. Full process-start checks remain outstanding.

## Second mechanism, frozen after closing the first panel

The eight-turn policy did not earn advancement: 175.5 points equals V439, with one gained and
one lost win and lower mean margin. See `LOOKAHEAD-RESULTS-2026-09-05.md`. Its one-root loss
reproducer shows the selected advantage reversing at sixteen turns under the same opponent
hypothesis. An actual-opponent diagnostic also contradicts the original eight-turn advantage.

New mechanism: **persistent-horizon benefit**. Simulate each of the same three roots to turn
eight and sixteen; require an alternative to improve the baseline by at least one estimated
point at both checkpoints. Select the largest minimum gain, preserving baseline on ties or
failure. When a game ends before a checkpoint, use the exact terminal banked value for that and
later checkpoints. Keep start turn 220, ranks 0..6, continuation policies and leaf formula unchanged.
This is not a claim that two checkpoints remove opponent-model error or all horizon effects.

Budget: rerun the executable branch/terminal fixtures and full 160-stream timing/packaging
check, then at most one more 192-game development panel against V439. These maps remain consumed
development data. Apply the same positive-point, map-regression, failure and timing advancement
rule above. No platform requests follow a tie or a runtime failure; any prospective real-agent
screen still needs its own frozen plan. Preserve the first policy's exports and results.
