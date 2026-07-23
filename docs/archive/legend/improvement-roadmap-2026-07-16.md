# Legend improvement roadmap — 2026-07-16

This is the execution record for improving exact live practice-ladder agent `6553250`.
The recovered source remains immutable.  The first user-authorized arena trial of the local stack
was inconclusive under degraded platform capacity and conservatively reverted.  On 2026-07-17 a
same-code A/A reset reconverged, and the controlled retry promoted the stack at 24.1 versus a
fresh 20.8-21.1 bracket.  A later behavior-identical source-slimming A/A closed at 24.2 versus
the full-size source's frozen 24.5 bracket, so the 62,725-byte encoding is now live and leaves
37,275 bytes of submission headroom.
Every candidate starts from the recovered source and must pass a mechanism-specific local gate
before any controlled platform evidence is considered.

## Next program — hierarchical policy selection

The completed ten-direction sweep is followed by the executable program in
`docs/hierarchical-controller-roadmap-2026-07-17.md`.  The project now treats opening strategy,
online search, and statistical validation as one hierarchy:

1. reconstruct coherent per-agent opening architectures from top replays;
2. build a small complete-policy option library with exact promoted live as the safe branch;
3. learn a turn-one contextual selector and measure its gap to the hindsight oracle;
4. test option-level Monte Carlo offline;
5. port a compact live search layer only if it adds robust value beyond a distilled selector.

Conditional, event-aligned top-player archaeology is now complete over 427 games and 618 selected
occurrences.  It reconstructs two candidates: a farm-first orchard scale option whose turn-one
worker rule matches 29/29 rank-2 appearances, and an adaptive max-bank hybrid option whose first
spec matches 22/26 rank-1 appearances.  Funding roles, phased supply, lifetime work, observed
recovery, conditional signals, and causal limits are recorded in
`data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.md`.

Phase 2 is complete.  Farm-first orchard scale and explicit adaptive funding are rejected.  A
sparse controller-compatible mechanism survives discovery: replace a delayed promoted
`1/3/0/*` target with an immediate `1/2/0/chop-max` worker only inside the turn-one `1/2/2/*`
affordability cell.  It activated on two of 60 reused maps, won all ten selected deterministic
opponent cells, and preserved exact fallback on the other 116/120 seed/seat streams.  The result
and its strong discovery-selection caveat are recorded in
`data/analysis/live-agent-6553250/phase2-macro-option-study-2026-07-17.md`.

Phases 3--5 are complete.  Static selector distillation failed, but a direct CompactGold
terminal-margin guard passed its frozen seeds 120--179 protocol: +2.717 seed-balanced margin,
3W/56T/1L, minimum -2.6, and every deterministic-opponent mean positive.  The standalone
two-worker rollout candidate is 90,643 bytes, matched 120/120 frozen decisions and 10/10 complete
dynamic streams, and measured 184 ms p95 against the 1,000 ms first-turn limit.  It is locally
qualified but not submitted.  Further local tuning is closed; a controlled platform bracket is
the next informative step and requires explicit authorization.  Full record:
`data/analysis/live-agent-6553250/phase3-phase5-rollout-study-2026-07-17.md`.

## Current diagnosis

The live bot is not short of chop actions.  In the repeated-loss sample it lands 138.3 chops
against 117.1, but banks only 53.3 wood against 81.2.  The weak starter converts at 0.135
wood/chop while trained workers reach 0.349.  The shared tree population normally collapses
around turn 82, and opponents combine renewable planting, harvesting, and additional trained
workers to reverse our early lead.

The objective is therefore to improve **privately captured value per action**, deny the
opponent's compounding loop, create truly exclusive supply, or exploit terminal mechanics.
Generic activity, shared production, and isolated parameter tuning are not objectives.

The evaluator correction materially changes the terminal picture: 58/60 exact-live local
self-play matches now stop by the referee's stall rule, at median turn 129.  The old fixed
300-turn renewable verdicts remain useful as mechanism screens, but are not authoritative for
timing changes.

The compact-workforce result is conditional on this promoted trajectory.  It rejects a late or
passively funded third worker bolted onto the existing two-worker policy.  It does not reject a
complete worker-rich opening with different funding, planting, worker roles, and abort rules.
Top-player evidence makes those coupled architectures an explicit next research class.

## Attack-angle matrix

The rows move from outcome-level choices down to implementation and evidence.  The numbered
references point to the ranked directions below.

| Abstraction | Capture / conversion | Opponent denial / races | Renewable control | Terminal / score state | Reliability / evidence |
|---|---|---|---|---|---|
| Economic objective | Raise private value per action (#5, #6) | Break the opponent's next compounding step (#4) | Own supply whose value cannot be recaptured (#7) | Preserve a lead or buy variance when behind (#8) | Optimize the real referee outcome (#1) |
| Strategic policy | Specialize workers by comparative advantage (#5, #6) | Reject races the opponent completes first (#3, #4) | Activate only defensible geometry (#7) | Switch deplete/extend behavior by score (#2, #8) | Use causal activation before outcome tests (#1) |
| Tactical sequence | Price short harvest/bank/fell bundles (#9) | Remove unsafe focus bonuses and contested commitments (#3) | Pre-seed before the supply cliff (#2, executed) | Choose last-fell, cashout, reserve, or replant (#2) | Audit target flaps and blocking before routing edits (#10) |
| Planner mechanism | Joint unit-task assignment (#5) | Opponent fell-and-bank ETA filter (#3) | Exclusive-cell and enemy-ETA constraints (#7) | Stall/grace-aware terminal value (#2, #8) | Equality, fixtures, and behavior-neutral telemetry (#1) |
| Measurement | Wood/chop, cargo cashout, opportunity cost | Unique losing commitments and train deficits | Replant survival and captured wood | End reason, implied grace, projected outcome | Exact-source equality and paired confidence interval |

## Ranked directions

| Rank | Direction | First discriminator | Status |
|---:|---|---|---|
| 1 | Correct evaluator semantics and causal gate | Port the referee grace/stuck/mercy end rule into every active local runner and validate it | **DONE** — Rust/Python parity and tests |
| 2 | Stall-aware terminal controller | Replay close losses and value last-tree, reserve, replant, bank, and final-fell choices | **LOCAL PASS** — low-supply pre-seed candidate |
| 3 | Opponent completion-race filter | Measure selected trees where opponent bankable completion ETA beats ours | **PARKED** — soft filter inert; hard reject harmful |
| 4 | Dynamic training-resource denial | Price lemon/plum/iron denial by opponent inventory, next-train deficit, and race outcome | **PARKED** — candidate mean is one-outlier driven |
| 5 | Comparative-advantage joint assignment | Assign efficient/private targets and denial targets by worker opportunity cost | **BASELINE CONFIRMED** — greedy ablation loses -6.48 |
| 6 | Evidence-derived workforce sequence | Test a cheap harvest/seed hand followed by a dedicated wood worker, only where it repays | **REJECTED** — loses all 60 seeds |
| 7 | Exclusive renewable geometry | Generalize the secure orchard only where opponent capture is provably uneconomic | **LOCAL PASS** — broader safe coverage boundary |
| 8 | Score-state asymmetric policy | Ahead: deplete/terminate; behind: reserve/extend; equal: exact baseline | **BASELINE CONFIRMED** — score-blind ablation is negative |
| 9 | Zero-commitment compound candidates | Prove and price bundles such as harvest -> bank -> fell without persistent commitment | **MEASURED / CLOSED** — only two new harvest episodes |
| 10 | Current-live motion/interference audit | Measure blocks, reversals, door conflicts, and target flaps before changing routing | **AUDITED / KEEP** — no execution defect; bonus neutral |

## Execution order

- [x] Port the real end condition from `abgate-selfplay-gate` commit `e7354d5` into the active
  Rust engine/equality harness.
- [x] Port the same rule into the Python simulator and all current exact-live study loops.
- [x] Add independent Rust and Python tests for grace countdown, stuck resources, mercy, and
  carried-iron exclusion.
- [x] Rerun the low-supply pre-seed control.  Its old fixed-300-turn verdict is not authoritative
  for a timing mechanism.
- [x] Recompute the renewable-supply baseline with actual terminal turns and record how often a
  seed is planted inside the legal grace window.
- [x] Add behavior-neutral terminal telemetry: score gap, tree count, implied grace, banked and
  carried seed, and selected command around the last-tree transition.
- [x] Add behavior-neutral race telemetry: our arrival/fell/bank ETA, opponent completion ETA,
  selected focus kind, and whether the `opponent_trolls <= 2` focus gate is active.
- [x] Materialize terminal fixtures from the 13 historical losses within 20 points and matched
  close wins.
- [x] Select exactly one first candidate from activation evidence; default order is terminal
  control, then completion-race filtering.
- [x] Run the exact-source equality, mechanism, regression, and full test gates; record a verdict.
- [x] Execute the remaining eight strategic directions with telemetry, a causal ablation, or a
  narrowly scoped candidate as appropriate.
- [x] Compose the two surviving mechanisms and run a 1,000-seed corrected-semantic gate.
- [x] Verify probe neutrality, inactive-region equality, deterministic generation, checksums,
  standalone compilation, and full regressions.

## Completed ten-direction sweep

The first survivor is `candidate-agent6553250-preseed-low-supply.min.rs`.  It offers a
high-priority `PICK` only from turn 100 onward when supply is at most two plants, the unit is
empty and adjacent to its shack, at least two own units exist, banked fruit is available, and
the current cell is plantable.  It does not add a persistent farmer or protect a shared mother.

Across 1,000 paired seeds under corrected stall semantics it gains **+0.259 mean margin** and
**+0.115 wood**, with 221 wins / 655 ties / 124 losses.  The paired-margin standard error is
0.0623; a normal-approximation 95% interval is **[+0.137, +0.381]**.  Before its turn-100 gate,
baseline and candidate are byte-identical in 200/200 equality games.  Of 19 historical streams
whose baseline commands reproduce exactly, the candidate activates in 14 (seven close losses
and seven matched close wins); every first divergence satisfies the intended gate.

The second survivor is the broader existing secure-orchard boundary: minimum coverage 8,
enemy-door distance 11, and worker speed 1.  It changes commands on only 27/1,000 seeds, but
goes 26 wins / 973 ties / 1 loss for **+3.7625 mean margin** and **+0.4525 wood**.  The result is
heavy-tailed (range -0.5 to +276.5), so its sign pattern and private-wood gain—not the raw mean
magnitude—are the useful evidence.

The composed candidate is
`candidate-agent6553250-preseed-orchard-coverage.min.rs` (90,547 bytes, SHA-256
`da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`).  Across 1,000 paired
seeds it gains **+4.025 mean margin** and **+0.5715 wood**, with 244 wins / 632 ties / 124 losses
and normal-approximation 95% interval **[+2.405,+5.645]**.  On 996/1,000 seeds the composed
margin and wood deltas equal the sum of the isolated branches; mean interaction is only +0.0035
margin and +0.004 wood.

Local verdict: the stack qualified for controlled field evidence.  Its first arena window was
inconclusive under a failed same-code capacity control and was conservatively reverted.  The
2026-07-17 retry used a healthy control, then **PROMOTED** the stack at 24.1 versus a fresh
20.8-21.1 bracket.  Its behavior-identical slim encoding subsequently passed a 24.2 versus 24.5
arena A/A and is now the submission baseline.  Full evidence is in
`direction-execution-2026-07-16.md`, `arena-verdict-2026-07-16.md`, and
`arena-retry-2026-07-17.md`.

## 2026-07-18 direct-rollout arena transfer: rejected

The locally qualified CompactGold `delta > 30` first-turn controller did not transfer.  A fresh
same-source control passed capacity and converged to 24.1; the rollout candidate was 21.7 after
120 games, with all 123 audited games valid and no timeout signal.  The exact slim resident was
restored as submission `41009991`, agent `6559583`.

Two frozen recent-30 windows permitted exact replay reconstruction.  The probe reproduced 60/60
arena first commands and identified three option activations, all losses (-26, -18, -27).
CompactGold/Gold predicted +197, +38, and +176 option deltas on those maps, while every map had a
negative alternative continuation and two were negative under all three alternatives.  Do not
raise the threshold or submit a bolt-on ensemble.  Close the single-model controller and move to
offline robust first-move option search with heterogeneous continuations, resident abstention,
and a new holdout frozen only after the option library and selector are fixed.

## 2026-07-18 robust first-option follow-up: closed

Phase 7 enumerated exact resident, dynamic max-bank, and all 27 fixed harvest-0 first workers.
Across 60 consumed discovery seeds, both seats, and eight continuations, the strict expanded
selector was inert and relaxed forms failed leave-one-model-out.  A 9,280-row repeat proved every
opening action exact but exposed five process-sensitive continuation models.  Six independent
process realizations on 20 consumed seeds then selected zero cells under empirical minimax,
all-model positive mean, and per-model one-sided 90% lower bounds.

A pooled-model diagnostic selected two cells only by averaging large gains over stable losses; it
produced 48 held model-seed losses under leave-one-repetition-out.  The discovery gate failed.
The untouched holdout remains sealed, and no packaging or arena action follows.  Next diagnosis is
arena-opponent action calibration of the continuation zoo, recorded in
`data/analysis/live-agent-6553250/robust-first-option-discovery-2026-07-18.md`.

## 2026-07-18 arena-opponent calibration: current zoo unsupported

The preserved 60 arena replays were used only for turn-one behavioral support.  Opponents trained
immediately in 22 games with 11 distinct specs.  Seven local continuations never trained on turn
one in those states; BossReal trained but matched none of the 22 specs.  Adaptive Gold had the
best exact full opening agreement at only 8/60, and no model matched the first target of any of
the three failed rollout activations.  The third activation's opponent issued `PICK` while every
model issued `MOVE`.

Global weights would therefore favor the same Gold family that already failed while omitting the
worker-rich branch.  Per-game weighting cannot inform a simultaneous turn-one decision.  Phase 8
is closed without a weighted rerun.  First-move Monte Carlo is retired for this library; next work
is held-game/held-agent learning of complete high-level objectives from top-agent replays.  Full
report: `data/analysis/live-agent-6553250/arena-opponent-opening-calibration-known60-2026-07-18.md`.

## 2026-07-18 complete-policy learning: coherent target selected

A state-only objective dataset now covers 91,427 worker-turns from 129 clean top-five replays.
The pooled lookup fails its frozen gate: 59.886% held-game accuracy / 0.347 macro F1 and 39.132%
worst held-agent accuracy.  The failure is architectural heterogeneity, not lack of signal.

Within-agent held-game validation identifies Escdemon as the strongest coherent target at
77.682% accuracy, 0.541 macro F1, and 74.760% worst-fold accuracy.  Norxondor also passes, but at a
lower level.  Escdemon trains one max-affordable harvest-0 worker in 26/26 games; the resident's
existing opening planner already predicts 14/26 exact specs with mean talent L1 error 0.538.
Therefore do not reopen worker-stat search.  Next work is held-game learning of Escdemon's train
trigger, exact targets, and assignment policy before any research bot is built.  Full report:
`data/analysis/live-agent-6553250/top-policy-objective-study-2026-07-18.md`.

## 2026-07-18 Escdemon complete-policy gate: branch parked

The conditional TRAIN trigger is recovered (25/26 exact first-affordability turns), and the
trained worker is a pure wood converter, but target-spec selection does not generalize: nested
leave-one-game-out policy selection reaches only 8/26 exact specs versus the resident plan's
14/26. A conditional held-game tree ranker reaches 56.08%, yet complete autoregressive MOVE
accuracy is only 52.12% with a 46.92% worst fold. Existing local policies also fail as shortcuts.

No candidate follows. Retain first-affordability and two-role separation as architecture evidence.
Next analyze Norxondor's joint worker-rich controller (0–4 trains, mean 2.07, median first turn 6)
at workforce-count/timing/role level before exact command imitation. Full report:
`data/analysis/live-agent-6553250/escdemon-complete-policy-gate-2026-07-18.md`.

## Kill rules

- A candidate that directly reduces banked wood without a larger measured opponent-value denial
  is rejected locally.
- A branch that activates too rarely to affect at least several corpus games is parked.
- Local paired play is a self-harm filter, not an arena promotion oracle.
- No platform burst is justified without behavior-neutral activation evidence.
- No candidate may change the live artifact, submit helper default, or arena state without an
  explicit controlled-arena authorization and recorded bracket.

## Closed unless a new mechanism appears

- Shared-mother renewal, generic seed protection, seed reserve widening, and broad farm loops.
- Early banking, global or role-limited focus removal, and isolated opening/training constants.
- Opportunistic chopper harvest that reduces fell capacity or steals chop turns.
- Forced far work, taskfloor activity filling, and persistent fell/plant commitment.
- Static map-density switching and full RHEA rollout search.
- Bolt-on third-worker expansion from the promoted trajectory: surplus never funds even
  `(1,1,0,1)`, while bounded starter funding loses value and still never trains the worker.
  This closure does not include coherent worker-rich opening architectures.

## Evidence

- `data/analysis/live-agent-6553250/report.md`
- `data/analysis/live-agent-6553250/renewable-supply-study.md`
- `data/analysis/live-agent-6553250/terminal-iteration-2026-07-16.md`
- `data/analysis/live-agent-6553250/direction-execution-2026-07-16.md`
- `data/analysis/live-agent-6553250/arena-verdict-2026-07-16.md`
- `data/analysis/live-agent-6553250/arena-retry-2026-07-17.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-arena-verdict-2026-07-18.md`
- `data/analysis/live-agent-6553250/preseed-orchard-coverage-stall-corrected-1000.json`
- `data/analysis/live-agent-6553250/secure-orchard-coverage-stall-corrected-1000.json`
- `data/analysis/live-agent-6553250/preseed-low-supply-stall-corrected-1000.json`
- `data/analysis/live-agent-6553250/preseed-historical-stream-gate.json`
- `data/analysis/live-agent-6553250/terminal-race-telemetry-2026-07-16.json`
- `data/analysis/live-agent-6553250/training-policy-sweep.md`
- `data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.md`
- `data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.json`
- `docs/hierarchical-controller-roadmap-2026-07-17.md`
- `docs/session-handoff-2026-07-16.md`
- `docs/silver-experiment-log.md`
