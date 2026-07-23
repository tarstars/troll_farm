# Alternative-approaches roadmap — 2026-07-16

## Why this pivot exists

The current loop has saturated.  Narrow changes are selected on exact-live mirror self-play,
rare blowouts can dominate their mean, and the degraded arena cannot currently provide a valid
A/B control.  This iteration changes the unit of search from a single scoring knob to evaluation
diversity, complete-policy selection, real-position evidence, and provable critical decisions.

No arena write is part of this roadmap.  Exact live source remains the safe resident artifact.

## Approach matrix

| Rank | Approach | First executable discriminator | Gate |
|---:|---|---|---|
| 1 | Diverse offline opponent league | Four current policies versus six frozen, behaviorally distinct opponents on common maps and both seats | Report per-opponent delta, robust aggregate, and worst opponent |
| 2 | Map-conditioned policy portfolio | Fit a shallow turn-1 map-feature selector on one seed split and evaluate it on unseen seeds | Test split must beat both live and the best global policy |
| 3 | Top-player behavioral archaeology | Census train count/timing/spec, action mix, planting, and wood conversion for top Legend agents | Identify a repeated macro role absent from live |
| 4 | Position-level counterfactuals | Replay official commands through the simulator and compare every next state before trusting forks | Quantify exact and RNG-only transition coverage |
| 5 | Critical-state solver | Run the forced-outcome etude oracle and price its usable domain against terminal fixtures | Retain only positions small enough for a checkable proof |
| 6 | New macro architecture | Derive a 3–4-worker role sequence from top-player evidence, never from an invented role | Build only if #3 shows a stable, affordable role pattern |
| 7 | Minimax policy mixture | Solve the four-policy versus opponent payoff matrix for a robust mixture | Worst-opponent delta must improve over live |

## Execution checklist

- [x] Freeze the list and its gates in this document.
- [x] Add turn-by-turn replay/simulator conformance analysis.
- [x] Build a multithreaded black-box opponent-league runner with robust statistics.
- [x] Run live, pre-seed, orchard-coverage, and the composed stack against the frozen zoo.
- [x] Fit and cross-validate a shallow map-conditioned portfolio.
- [x] Compute the maximin policy mixture from the same payoff matrix.
- [x] Produce a top-Legend macro-role census from the collected replay corpus.
- [x] Run the existing exact etude oracle and state its honest coverage limit.
- [x] Select one next architecture and record explicit kill rules.

## Fixed policies

| Label | Artifact |
|---|---|
| live | `agent-6553250-yamo-orchard-live.min.rs` |
| preseed | `candidate-agent6553250-preseed-low-supply.min.rs` |
| geometry | `candidate-agent6553250-secure-orchard-coverage.min.rs` |
| stack | `candidate-agent6553250-preseed-orchard-coverage.min.rs` |

## Fixed opponent zoo

The initial zoo deliberately spans distinct historical architectures rather than six adjacent
versions: motion-only, task-layer, race-aware, yield-aware, ring-farm, and the exact current
policy.  The four-policy comparison excludes exact live as an opponent because live is already
the common policy control; the frozen zoo is:

- `v1.20.0-motion.min.rs`;
- `v1.27.0-taskplan.min.rs`;
- `v1.36.0-race.min.rs`;
- `v1.43.0-yield.min.rs`;
- `v1.59.0-ringfix3.min.rs`;
- `v1.61.0-chopharvest.min.rs`.

## Selection rules

- Common seeds and both seats are mandatory.
- Policy deltas are computed against live on the same opponent/seed, not from absolute scores.
- Report mean, median, 5%-trimmed mean, win/tie/loss, standard error, and worst-decile result.
- A rare positive mean with non-positive trimmed/test-split evidence is not a winner.
- Portfolio features must exist at turn 1; outcome-derived features are forbidden.
- The test split is never used to select a feature, threshold, leaf policy, or mixture weight.
- An offline winner is a research candidate, not an arena promotion signal.

## Completed gates so far

- Replay conformance: 361,752 comparable transitions across 1,302 games; 333,336 exact,
  28,416 position-only referee-RNG differences, zero material mismatches, and three malformed
  historical command strings excluded.
- Top-player census: 618 selected-agent appearances.  Top five average 1.915 successful trains
  versus exact live's fixed one; their median first train is turn 2 versus live turn 8.  Hybrid
  choppers occur in 52.7% of top-five appearances across four agents and 0% of live appearances.
- Exact oracle: the sample four-ply wood cash-out is independently validated, but none of 416
  terminal-fixture positions fit its documented one-troll-per-side envelope.  Eighty-five fit a
  relaxed probe envelope; TRAIN omission and referee movement RNG prevent calling those full-game
  arena proofs.
- Opponent league: the complete stack has the strongest aggregate (+2.069 seed-balanced mean,
  +0.276 5%-trimmed mean), but its interval crosses zero and its motion-opponent delta is
  -0.092.  Pre-seed is negative; geometry is outlier-sensitive.
- Portfolio: the even-seed fit selects stack when initial banana fruit is at most five and exact
  live otherwise.  On untouched odd seeds the analytical selector is +4.350 mean / +1.354
  trimmed; its interval and worst decile remain negative.  The maximin fit therefore selects
  100% live.
- Deployable portfolio: `candidate-agent6553250-banana5-stack-portfolio.min.rs` implements the
  stump in one source and matches the selected branch in 300/300 deterministic map-opponent
  cells.  The historical motion bot is excluded from exact repeat-run equivalence because its
  `HashMap`/`HashSet` iteration is process-randomized.  A fresh portfolio run remains positive
  on the odd holdout (+3.686 mean / +0.821 trimmed) but is not promotion-ready.
- Macro transfer: the corrected funded three-worker candidate reaches the third worker in both
  seat games in 356/360 cells, then loses -28.349 mean / -27.364 trimmed and loses against all
  six opponents.  The top-player role correlation does not transfer into the live architecture.
- First prospective gate: on 300 untouched seeds the stack passes every deterministic research
  rule (+1.934 mean / +0.492 trimmed; CI lower +0.497; all opponent means positive) but fails the
  promotion worst-decile rule at -4.952. Repeated `motion` evaluation supplies no stochastic
  support (adjusted low-minus-null mean -0.039).
- Component diagnosis: every one of the 21 deterministic tail losses is exactly a pre-seed loss;
  secure orchard is 11/197/0 seed-balanced W/T/L. The packaged stack matches its parent in
  1,040/1,040 new cells.
- Geometry-only prospective gate: on a second untouched 300-seed block the candidate is 5/204/0,
  with +1.474 mean, positive CI lower bound, nonnegative worst decile, positive means against all
  opponents, and exact references in 1,500/1,500 branch cells. Its frozen five-percent-trimmed
  rule is exactly 0, so the formal decision is reject.

## Selected architecture and kill rules

There is no retained promotion candidate. Exact live remains the resident and maximin choice.
The stack is archived as a deterministic research pass with tail and stochastic failures. The
only retained mechanism is secure-orchard geometry: it is non-losing but too sparse under the
frozen gate. Any next iteration must broaden geometry itself, freeze one source, and validate on
seeds starting at 10,600; neither consumed prospective block may be reused as a holdout.

Kill it if any of the following occurs:

- deterministic branch equivalence falls below 100%;
- a larger untouched seed block has non-positive mean or 5%-trimmed delta versus live;
- any deterministic frozen opponent has a negative mean delta;
- an eventual promotion sample still has a non-positive lower confidence bound or negative
  worst decile;
- the arena cannot first pass a same-code A/A reconvergence control.

Full execution synthesis:
`data/analysis/live-agent-6553250/alternative-approaches-execution-2026-07-16.md`.

## 2026-07-18 architecture update

The original fixed-policy portfolio program has now produced a stronger structural option.
Norxondor's staged workforce ladder is recovered, and a temporary two-funder coalition reliably
builds a productive third worker. The exact-three-worker option has large complementary cells
against the current resident, but neither opponent-label selection nor a late observable-signature
switch is deployable: the prospective common-prefix implementation lost −6.169 margin.

The active discriminator is therefore a one-shot shared-state Monte Carlo macro selector. It must
compare the frozen resident and frozen three-worker policies from the same early state over an
observable-conditioned opponent ambiguity set. Exact resident remains the only retained artifact;
the sealed holdout and arena remain untouched. Full Phase-10 evidence is in
`data/analysis/live-agent-6553250/norxondor-controller-iteration-2026-07-18.md`.
