# S1 endgame exact-solver scope audit

Date: 2026-07-31

Verdict: **`FULL_EXACT_INFEASIBLE`**

## Question

Is “solve the last N turns exactly” a distinct and plausibly deployable 50 ms direction,
or does every tractable version reduce to an already closed candidate/rollout interface?

## Scope boundary

Three objects must not be conflated:

1. A full exact solver branches both players' simultaneous primitive commands, referee
   chance outcomes, and exact stall/mercy/turn-cap semantics.
2. A known-policy counterfactual must clone both bot processes and their internal entropy
   after every branch.
3. A resident-candidate search branches only scheduler proposals and therefore is not an
   exact game solver; it overlaps N4, D36, and S3.

B3.1's endgame-switch retuning, D84's threatened-response MC, Phase 11's shared-state MC,
Phase 16's MOVE residual, and D36's overlays remain closed. S1 cannot rename them.

## Empirical census

The exact live source ran on reused seeds 0..59 against all six frozen opponents in both
seats: 720 control games. Public pre-turn states were captured at turns 251, 276, and 291.
All games complete with no malformed command or unexpected stderr.

Late states are common enough to be relevant: 246/720 games (34.17%) reach turn 251,
188 (26.11%) reach 276, and 155 (21.53%) reach 291. The panel yields 589 roots. Median
live plants are three at each checkpoint, and median total roster is four; observed roster
patterns are 1v2, 2v1, and 2v2.

For each player, the audit exhausts all direct within-speed MOVE endpoints, applies exact
same-side collision/swap resolution, and deduplicates position outcomes. Multiplying both
players' counts gives a strict lower bound on the full simultaneous one-ply state branching
because HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE, and their resource/tree effects are
all omitted.

The lower bound is not astronomical at one ply: median 600 and maximum 6,400 across all
roots. At turn 291, with ten nominal turns left, it is median 450, p90 1,944, maximum
3,825. At turn 251, with 50 nominal turns left, it is median 688, p90 2,304, maximum
6,400. First-ply size alone is therefore not the decisive rejection.

## Feasibility

The only genuinely distinct object is the full simultaneous stochastic game. Even the
movement-only lower bound must be expanded across 10–50 turns, while a full solver also
adds every non-MOVE transition, opponent choice, plant dynamics, collision/chance outcome,
and terminal branch. The live bot does not observe the referee's continuing RNG state.

The apparent shortcuts do not rescue exactness. Repository `BotSession` processes expose
only stdin/stdout and cannot be serialized or forked; exact known-policy counterfactuals
would restart and replay every prefix. Restricting to resident candidates or unchanged
opponent continuation is tractable only by dropping the full-game claim and returning to
N4/D36/S3.

The measured latency boundary is already adverse for strict subsets: online shared-state
MC is 279.46 ms p95 and primitive MOVE residual search 92.852 ms p95, both above the live
50 ms turn budget. S1 supplies no proof-preserving state reduction or exact chance model
that could reverse that boundary.

Jobs 1 and 8 produce byte-identical normalized payloads and exact game/root hashes. Six
focused tests, including exhaustive agreement with the engine on collision vectors, pass;
the sacred resident remains `fff6669b…`.

## Decision

Close S1 as **`FULL_EXACT_INFEASIBLE`** under the current representation and runtime
contract. Do not build an “exact” solver by restricting it to resident candidates or one
known opponent. N4 and S3 remain separate and unchanged.

Reopening requires a proof-preserving compact state reduction for the full simultaneous
game plus an exact referee chance model—not a deeper horizon, beam-width retune, candidate
wrapper, source edit, fresh panel, candidate, or Arena cycle.

Machine summary:
`data/analysis/live-agent-6553250/s1-endgame-solver-feasibility-result-2026-07-31.json`.
Analyzer: `cgauto/s1_endgame_solver_feasibility.py`.
