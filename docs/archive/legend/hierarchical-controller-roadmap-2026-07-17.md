# Hierarchical policy-selection and Monte Carlo roadmap — 2026-07-17

## Decision

The next program is a **hierarchical controller**, not another isolated policy constant and not a
revival of primitive-action RHEA:

```text
top-replay and causal analysis
            |
            v
coherent opening-option library
            |
            v
turn-one contextual strategy selection
            |
            v
baseline-preserving residual rollout control
            |
            v
paired prospective evidence -> controlled arena A/A
```

The promoted 62,725-byte pre-seed/secure-orchard Yamo policy remains the exact control, safe
branch, and recovery default.  No part of this roadmap authorizes an arena write.

Phases 1--14 are now complete. Static turn-one distillation, the locally qualified rollout
candidate's arena transfer, online terminal Monte Carlo, generic trajectory value distillation,
post-funding repair, and a complete native Norxondor reconstruction have each been measured and
closed. Phase 15 is a final discovery-scale test of the remaining map-geometry signal; no part of
this roadmap authorizes an arena write.

## Corrected interpretation of the workforce evidence

The compact-workforce experiment established a conditional result:

> After the promoted policy buys its normal second worker and follows its normal trajectory, a
> third worker is not passively affordable, and the tested starter-funding detours do not repay.

It did **not** establish that worker-rich play is globally unaffordable or unprofitable.  The
promoted policy spends its opening stock and then fails to replenish PLUM, LEMON, and IRON.  The
result therefore describes the state distribution created by that policy.

The stronger-bot corpus supplies the complementary observation:

- top-five agents average 1.915 successful `TRAIN`s and first train at median turn 2;
- the promoted ancestor always trains exactly once and first trains at median turn 8;
- top-five agents plant about 35 trees per appearance, versus about 11 for live;
- top-five mean final wood is 75.1, versus 48.2 for live;
- successful agents are heterogeneous: some commonly reach four workers, while one top-five
  agent consistently uses only two.

Worker count, worker specification, funding, renewable supply, geometry, and later role
assignment are therefore a coupled architecture.  The repaired three-worker transplant proved
the distinction directly: it reached worker three in 356/360 paired cells but lost -28.349 mean
margin.  Affordability was solved; the transplanted architecture and opportunity cost were not.

Consequences:

1. Keep late/opportunistic third-worker expansion closed inside the current promoted trajectory.
2. Reopen worker-rich play only as a complete opening architecture with funding, supply, roles,
   abort rules, and a midgame handoff.
3. Retain a two-worker architecture as a first-class option; more workers are not monotonically
   better.
4. Measure marginal lifetime production after all funding, displacement, crowding, and supply
   costs.  Worker count alone is not an objective.

## Controller levels

| Level | Decision | Candidate representation | Evaluation horizon | Fallback |
|---|---|---|---|---|
| Opening strategy | Which economic basin should this map enter? | Complete stateful macro option | Actual terminal/stall horizon | Promoted policy |
| Opening supervision | Continue, abort, or hand off the chosen option | Option-specific state transition | Until option terminates | Promoted policy |
| Residual control | Is one immediate baseline decision locally wrong? | Small role-preserving deviation | Four-turn screen, then bounded long rollout | Byte-identical baseline command |
| Terminal control | Cash out, deplete, or extend? | Exact short compound sequence | Remaining legal turns/grace | Promoted terminal behavior |

The opening decision is strategically irreversible and receives the platform's 1,000 ms first-
turn budget.  Later turns have only 50 ms and should use selective residual search, not rebuild an
entire strategy tree.

## Monte Carlo design

### What to search

Do not search arbitrary primitive command strings or randomly mutated three-task plans.  Search
bounded **options** with explicit termination and abort conditions, for example:

- execute a complete funding-and-training sequence for a specified role;
- preserve and exploit an exclusive renewable cluster;
- assign one worker to a bounded target or compound work sequence;
- retain the promoted baseline unchanged.

An opening option must include the work displaced while funding, not just the final `TRAIN`.
Residual candidates initially change at most one worker's selected option and never interrupt
immediate `CHOP`, `HARVEST`, `DROP`, `PICK`, or `PLANT` work without modeling the full compound
alternative.

### How to evaluate

1. Compare every candidate against the promoted baseline from the same root state.
2. Use common movement/opponent samples for candidate and control so the estimate is a paired
   delta rather than two noisy absolute values.
3. Use the corrected referee end condition; opening investments must be rolled to actual stall or
   termination whenever feasible.
4. Continue our side with the selected stateful option followed by the actual promoted policy.
   GoldElite is an architecture reference, not a valid live continuation.
5. Evaluate against a small opponent-policy ensemble and sampled movement ties.  Exact mechanics
   do not make one opponent continuation predictive.
6. Prefer a candidate only when expected delta is positive, downside is bounded, and the sign is
   stable across continuation scenarios.  Pure mean and pure maximin are both insufficient.
7. Commit an accepted option for a bounded interval.  Suppress expired or disproven options so
   receding-horizon search cannot rediscover the same failure indefinitely.
8. On timeout, uncertainty, invalid state, or insufficient margin, emit the exact baseline.

### Offline before live

The exact minified engine costs about 23,257 bytes.  With the 62,725-byte resident, that leaves
roughly 14 KB for a live controller.  The existing GoldElite residual controller alone is about
23,210 bytes and cannot be transplanted.

The research implementation may therefore be large and explicit.  It must first measure:

- oracle gain over the best static policy and over a compact contextual selector;
- decisions whose value depends on post-turn-one information;
- rollout count and latency with the real continuation cost, not bare-engine throughput;
- sensitivity to opponent continuations and movement samples;
- how much oracle behavior can be distilled into small deterministic rules.

If a distilled selector captures nearly all robust oracle value, omit the live engine and spend
the 37,275-byte headroom on coherent policy options.  If online search adds material value on
ambiguous states, port only the smallest candidate generator, evaluator, and commitment guard.

## Opening-option library

The first library contains three roles, but only evidence may determine their final mechanics:

1. **Safe control:** the exact promoted pre-seed/secure-orchard Yamo policy.
2. **Early scale:** a coherent worker-rich architecture reconstructed from one stable top-agent
   archetype, including its funding and planting system.
3. **Adaptive scale:** an architecture that remains small on poor starts and expands only when
   map resources, renewable geometry, and projected payback support the next worker.

Do not create a synthetic "top bot" by combining the most common isolated specification, plant,
and worker role across unrelated agents.  First reconstruct per-agent archetypes and the
within-agent conditions under which they vary.

Every non-control option must define:

- entry conditions visible at selection time;
- ordered training specifications and affordability rules;
- which existing worker funds each missing resource;
- exclusive or defensible supply creation;
- roles and target priorities after each successful train;
- shack/door congestion handling;
- funding timeout and abort conditions;
- state-based handoff into the promoted midgame controller.

Candidate turn-one features include starting inventory and exact affordable specs, per-kind
fruit/health/size, private and contested reachable supply, water-adjacent planting geometry,
shack distance and congestion, opponent-relative resource access, and projected train/payback
time.  A single optional update on turns 2--4 may use the opponent's observed first
`TRAIN`/specification, but switching carries an explicit cost.

## Statistical design

### Units and estimands

- The independent unit is the **map seed**.  Average both seats and all cells sharing a seed
  before confidence calculations.
- The primary estimand is paired final score-margin delta versus the promoted policy.
- Wood, action counts, worker output, and inventory are mechanism diagnostics, not replacement
  objectives.
- For strategy selection, optimize expected regret/value, not raw classification accuracy.  A
  harmless near-tie and a catastrophic wrong branch are not equivalent mistakes.

### Required summaries

Every mechanism and policy report includes:

- paired mean and a seed-clustered interval;
- five-percent trimmed mean;
- leave-one-seed-out minimum mean or without-largest result;
- worst-decile mean/CVaR;
- wins, ties, losses, minimum, maximum, and largest influences;
- activation rate and activated-only outcome;
- mean by opponent and by relevant predeclared map strata.

### Sparse mechanisms

The old symmetric trimming gate is unsuitable as the only test for a mechanism that is exactly
neutral when inactive and rarely positive when active.  Future sparse-option protocols must
predeclare a three-part analysis:

1. verify exact inactive-region equality and estimate activation probability;
2. estimate activated benefit, activated-loss probability, and activated downside;
3. combine those quantities into overall expected contribution.

This does not retroactively change any frozen verdict.  It prevents future safe sparse effects
from being erased mechanically by trimming hundreds of structural zeros.

### Discovery, validation, and arena

1. Reused seeds and historical replays are discovery data only.
2. Selector fitting uses nested or blocked cross-validation.  Opponent robustness includes a
   leave-one-opponent-out diagnostic.
3. Freeze source, feature set, thresholds, opponents, seed manifest, and rules before opening a
   prospective block.
4. Do not reuse consumed portfolio blocks as holdouts.
5. Treat paired local play as a self-harm and mechanism filter, not an arena acceptance oracle.
6. Require a healthy same-code A/A bracket before candidate arena evidence.
7. Arena promotion remains a separately authorized external action.

## Analysis program

### Phase 1 — conditional top-player archaeology

- [x] Extend each replay occurrence with turn-one inventory, map/supply/geometry features, and
  opponent identity/opening.
- [x] Record every successful train's turn, spec, exact cost, pre-train deficit trajectory, and
  the workers/actions that funded it.
- [x] Attribute post-train lifetime work: moves, chops, harvested resources, plants, drops,
  carried/banked wood, idle/block time, and last productive turn.
- [x] Align games around each `TRAIN` and measure the whole-policy payback trajectory rather than
  assigning all later output mechanically to the new worker.
- [x] Report per-agent, not only pooled, training-count and sequence distributions.
- [x] Test whether each agent's worker count/spec sequence varies with turn-one conditions.
- [x] Examine near-affordability boundaries within a fixed agent as a quasi-experiment; label
  causal conclusions cautiously because replay opponents are not paired.
- [x] Cluster coherent opening archetypes and nominate at most two non-control options.

**Phase-1 exit:** two reconstructable archetypes with explicit funding, supply, role, and abort
mechanisms.  If the corpus cannot support them, collect more replays before writing a candidate.

**Phase-1 verdict — passed 2026-07-17.**  The 427-game / 618-occurrence reconstruction has exact
turn alignment and zero unknown replay updates.  It nominates a rank-2 farm-first orchard option
and a rank-1 adaptive max-bank hybrid option.  The first farmer spec is reconstructed in 29/29
appearances; the adaptive first spec matches a maximum-affordable generator in 22/26.  Funding,
supply, lifetime roles, recovery horizons, conditional signals, and causal limitations are in
`data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.md`.

Expected Phase-1 artifacts:

- `cgauto/top_player_opening_analysis.py`;
- `tests/test_top_player_opening_analysis.py`;
- `data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.json`;
- `data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.md`.

### Phase 2 — complete offline macro options

- [x] Implement the two options outside the live submission first.
- [x] Add activation and state-transition telemetry for every option stage.
- [x] Prove that the baseline option is command-identical to the promoted artifact.
- [x] Run mechanism discovery on reused seeds against the fixed opponent zoo, both seats.
- [x] Reject an option that fails to train, funds by merely deleting productive work, has no
  post-train role, or creates supply primarily captured by the opponent.

**Phase-2 exit:** at least one non-control option activates as intended and has plausible robust
payback.  No untouched holdout is consumed merely to prove activation.

**Phase-2 verdict — passed narrowly 2026-07-17.**  The complete farm-first architecture loses
-97.57 score and -27.46 wood against the promoted stack on deterministic discovery cells despite
creating almost entirely private supply; funding and displaced work do not repay.  Explicit
adaptive funding loses -56.78 and the globally applied first max-bank worker also loses.  The
surviving mechanism is sparse: when turn-one affordability is `1/2/2/*` and promoted Yamo would
wait for `1/3/0/*`, train an immediate `1/2/0/chop-max` worker and hand control back to Yamo.
It activates on two of 60 discovery maps, wins all ten activated deterministic-opponent cells,
and is command-identical on the other 116/120 seed/seat streams.  Full/slim candidate parity is
120/120.  Because the entry rule was derived on the same block, this is mechanism evidence only.
Full results: `data/analysis/live-agent-6553250/phase2-macro-option-study-2026-07-17.md`.

### Phase 3 — full-information policy league and selector

- [x] Run every complete option and the control on identical map/opponent/seat cells.
- [x] Compute the per-map hindsight oracle and the gain available from selection.
- [x] Fit a small cost-sensitive selector using only information available at its decision turn.
- [x] Reject the optional turn-2--4 update: the only surviving decision is made on turn one and
  the direct rollout already fits the first-turn budget.
- [x] Use blocked validation and report the oracle-to-selector value gap.
- [x] Freeze a prospective protocol only after the option library and selector are fixed.

**Phase-3 exit:** positive robust selector delta, bounded tail, nonnegative deterministic-opponent
means, and a meaningful fraction of the oracle advantage captured on untouched data.

**Phase-3 verdict — static branch failed, rollout branch advanced 2026-07-17.**  The globally
applied option loses -9.57 on the independent block despite positive hindsight value.  Four-model
ensemble selection retained too many losses; unanimous selection was nearly inert.  A single
Gold continuation with a `>30` margin guard was the smallest discovery threshold with zero
losing seeds and positive means against all opponents.  Static tree distillation later missed
all four held-out activations, closing the compact-feature branch.

### Phase 4 — offline option-level Monte Carlo

- [x] Use the exact fast engine with terminal/stall-correct rollouts and common states.
- [x] Use the actual selected option plus promoted policy as our continuation.
- [x] Compare static selector, turn-one rollout selector, and hindsight oracle on the same cells.
- [x] Measure latency and decision stability under the 1,000 ms first-turn budget.
- [x] Defer later 50 ms residual decisions; they are unnecessary for the chosen first-turn
  architecture and remain a separate future experiment.
- [x] Distill stable rollout decisions and quantify the value lost by distillation.

**Phase-4 exit:** choose one deployment architecture by measured value per byte:

- compact selector/options without a live engine;
- turn-one live rollout selector plus compact options;
- selector plus compact later residual;
- or no deployment if none robustly beats the control.

**Phase-4 verdict — direct rollout passed 2026-07-17.**  The frozen `CompactGold delta >30`
rule selected four of 120 independent seat cells and scored +2.717 seed-balanced margin,
3W/56T/1L, minimum -2.6, with every opponent mean positive and worst opponent +1.375.  The
predeclared protocol passed.  CompactGold is command-identical to default GoldElite, but only
9,256 compacted bytes.

### Phase 5 — compact deployment candidate

- [x] Freeze the exact 62,725-byte promoted artifact as parent.
- [x] Generate a standalone source below 100,000 bytes and record checksum/size breakdown.
- [x] Verify fallback command identity, selected-branch equivalence, historical streams, and
  dynamic both-seat games.
- [x] Measure release timing, including per-game timeout concentration; no decision may exceed
  the official loss conditions.
- [x] Run a new prospective local block under the frozen statistical protocol.
- [x] Stop after the local verdict.  Do not submit without explicit arena authorization.

**Phase-5 local verdict — qualified 2026-07-17; arena-rejected 2026-07-18.**  Candidate
`candidate-agent6553250-compact-gold-rollout30.min.rs` is 90,643 bytes, SHA-256
`f5df1f760791a21ad0193469c132fea02ebaa2856b33f62213765205b3b59370`.  Its deployment gate
matched 120/120 frozen decisions and 10/10 complete dynamic streams.  First-turn p95 was
184.07 ms and maximum 193.96 ms; a shared 700 ms deadline and worker-panic handling fall back to
control.  Later turns are the selected normal policy with no rollout cost.  A healthy live
capacity control later converged to 24.1, while this candidate reached only 21.7 at 120 games;
all 123 audited games were valid.  The exact resident was restored.  The local qualification did
not transfer.

### Phase 6 — arena transfer and opponent-model audit

- [x] Freeze and run a same-source capacity bracket before the candidate.
- [x] Enforce the 120-game promotion/rejection gate without tuning during the run.
- [x] Restore the exact resident after a clear rejection and confirm the arena agent change.
- [x] Reconstruct the selector from immutable live replays and prove command parity.
- [x] Re-evaluate selected live maps under diverse continuation models.

**Phase-6 verdict — single-model controller rejected 2026-07-18.**  The control passed at 24.1;
the candidate reached 21.7 at 120 games, -2.4 versus control.  A replay probe matched 60/60 known
arena commands and found three option activations, all losses (-26, -18, -27).  Gold/Compact
predicted those options at +197, +38, and +176, but every selected map had a negative alternative
continuation; two were negative under all three alternatives.  CompactGold and GoldElite matched
in 120/120 reconstructed seat cells.  The defect is opponent-model overconfidence, not runtime
failure or a threshold that should be increased post hoc.

### Phase 7 — robust first-move option search

- [x] Freeze a small library of complete first-train options plus exact resident.
- [x] Evaluate every option under multiple heterogeneous opponent continuations.
- [x] Use lower-confidence/minimax selection with exact-resident abstention.
- [x] Reject the inert selector and options whose value depends on one continuation.
- [x] Keep the new untouched map block sealed after the discovery gate failed.
- [x] Skip distillation and byte/time packaging because no prospective robust value exists.

The 60 reconstructed arena maps are diagnosis data, not a new acceptance holdout.  Do not tune
the next selector to their three observed losses.

**Phase-7 verdict — isolated first-worker search closed 2026-07-18.**  The complete library had
29 options and was evaluated in 27,840 discovery rows against eight continuations.  Strict
expanded selection was inert; permissive rules failed leave-one-model-out.  An identical 9,280-row
repeat kept every opening action exact but changed 502 deltas because five models were
process-sensitive.  Six fresh-process realizations on 20 consumed seeds still produced zero
empirical-minimax, all-model-mean, or per-model-90%-LCB selections.  A pooled diagnostic selected
two cells but incurred 48 held model-seed losses.  The gate failed, and no holdout, candidate, or
arena action followed.

### Phase 8 — opponent-model calibration

- [x] Measure turn-one action agreement for each local continuation on the known arena opponent
  trajectories; keep these 60 replays diagnosis-only.
- [x] Separate repeatable turn-one actions from process-sensitive terminal continuations.
- [x] Reject model weighting because the zoo lacks field-opening support; do not manufacture an
  ambiguity set from coarse agreement.
- [x] Skip a weighted grid rerun because its weights are not identifiable.
- [x] Retire first-move Monte Carlo and scope a learned complete-policy continuation.
- [x] Keep the map holdout sealed and perform no arena write.

**Phase-8 verdict — calibration cannot rescue the controller.**  Arena opponents train on turn
one in 22/60 diagnosis games with 11 distinct specs.  Seven local models never train in those
states; BossReal trains but matches none of the 22 specs.  Adaptive Gold is the best complete
opening match at only 8/60 and belongs to the same continuation family that overpredicted the
rejected choices.  None of the eight models matches the first target in any of the three failed
activations, and all miss a76a44's `PICK` action family.  A simultaneous turn-one controller also
cannot condition on the unseen opponent command.  No defensible weights exist.

### Phase 9 — learned complete-policy continuation

- [x] Extract per-turn, per-worker objective labels from top-agent replays.
- [x] Use state features available at decision time; exclude agent identity and outcome leakage.
- [x] Validate objective prediction by held game and held agent; reject the pooled top-five model.
- [x] Select Escdemon as the first coherent architecture target by within-agent held-game gate.
- [x] Add held-game TRAIN-trigger, exact-target, and multi-worker assignment learning.
- [x] Apply the complete-policy gate: reject the integrated Escdemon tree skeleton and all local
  policy shortcuts; retain exact resident as the local league control.
- [ ] Evaluate complete policies, not isolated worker transplants, under diverse continuations.
- [ ] Freeze any eventual selector before opening a prospective block; no arena work is implied.

**Phase-9 first discriminator — pooled imitation rejected, coherent target found.**  The clean
dataset has 91,427 unit-turns from 129 top-five games.  A state-only lookup reaches 59.886%
held-game accuracy / 0.347 macro F1 but falls to a 39.132% worst held-agent accuracy, proving that
the top five cannot be averaged into one policy.  Escdemon passes its within-agent gate at
77.682% accuracy / 0.541 macro F1 / 74.760% worst fold; norxondor also passes at a lower level.
Escdemon's trained spec is max-affordable harvest-0 in 26/26 games, while the resident planner
already predicts 14/26 exact specs with mean talent L1 error 0.538.  The remaining work is its
training trigger and complete tree/bank target continuation, not another stat formula.

**Phase-9 complete-policy gate — Escdemon parked.** Conditional first-affordability timing is
exact in 25/26 games, but a 2,750-policy opening grid falls from the resident plan's 14/26 exact
specs to 8/26 under nested leave-one-game-out selection. The trained worker is a pure wood
converter over all 5,341 observed turns. A held-game tree ranker beats minimum-cycle choice
56.08% to 45.97%, yet the complete autoregressive renderer reaches only 52.12% MOVE-target
accuracy and fails its gate (9.0-point gain; 46.92% worst fold). Twelve local policy skeletons
also fail; SilverBoss is closest at only 61.16% objective agreement and matches no actual TRAIN
spec. No Escdemon candidate follows.

### Phase 10 — worker-rich Norxondor controller

- [x] Extract planned workforce-count, train-stage, and role-transition labels from Norxondor's
  30 games; treat 0–4 workers as one controller rather than independent purchases.
- [x] Validate workforce count, first/subsequent TRAIN timing, and spec family by held game.
- [x] Measure worker-role persistence, assignment, utilization, and direct banking contribution.
- [x] Implement a research controller only if the joint macro layer generalizes; do not transplant
  workers into the resident continuation.
- [x] Test a confidence-buffered resident/three-worker information portfolio and an observable
  opening signature on disjoint generated-map blocks.
- [x] Reject the actual delayed common-prefix selector after its prospective −6.169 margin result.
- [x] Preserve the sealed map block and exact resident; build no candidate.

**Phase-10 verdict — architecture recovered, late switching rejected.** The four-stage
max-affordable ladder reproduces all 8,738 trigger decisions and all 62 observed TRAIN specs,
with 57/62 held-game specs. A temporary two-funder coalition makes three to five workers
affordable and productive. The exact-three-worker plateau beats resident overall but has sharp
Adaptive Gold and ScriptBoss regressions. A confidence-buffered opponent-label portfolio passes
an untouched block at +6.213 margin, and a safe observable signature has +7.546 cross-validated
information value. The actual resident-prefix implementation loses −6.169 margin because the
signal and funding path are policy-dependent. No submission follows.

### Phase 11 — shared-state Monte Carlo macro selector

- [x] Freeze resident and exact-three-worker branches; make no schedule changes during selector
  development.
- [x] Capture one shared early state before the continuations diverge and condition the opponent
  ambiguity set using only observable transitions.
- [x] Roll out both complete macro options from that same state over compatible opponent models;
  use a repayment-length horizon and forbid invented short-horizon asset bonuses.
- [x] Compare mean, minimax, lower-tail, and oracle decisions with the resident default.
- [x] Validate the actual selector on nested generated-map blocks with paired score,
  margin, per-opponent, and worst-opponent gates.
- [x] Profile inner-parallel p95 decision time; skip source integration after the 50 ms gate fails.
- [x] Keep the sealed map holdout and arena untouched.

**Phase-11 verdict — teacher validated, online search rejected.** The frozen turn-three terminal
teacher repeats at +26.081 margin / +15.194 score, with all eight opponent means positive and no
selected losing cell. A 240-turn liquid-value proxy retains 89.19% of the margin gain, but its
unchanged validation precision is 88.33% versus the frozen 90% requirement. Inner parallelism
still takes 209.487 ms median / 279.460 ms p95, with 0/80 decisions under 50 ms. Single-tree,
deployable-forest, and raw-signature distillation also fail their safety gates. No candidate or
holdout follows.

### Phase 12 — offline value distillation with trajectory features

- [x] Generate a larger direct-outcome training set using only the two actual terminal branches
  per cell; this is training/discovery data, not a new holdout.
- [x] Encode generic observable prefix trajectories without opponent identity or embedded models.
- [x] Evaluate precision-first compact classifiers under both blocked-seed and
  leave-one-opponent-out folds.
- [x] Require at least 90% precision, at least 5% selection, positive paired score and margin,
  five of eight nonnegative opponent means, and worst opponent mean at least -5.
- [x] Freeze the expression before opening a fresh validation block; only an unchanged pass may
  authorize resident integration, byte profiling, or timing profiling.
- [x] Preserve the sealed holdout, resident artifact, submit default, and arena throughout
  discovery.

**Phase-12 verdict — opponent transfer rejected; map-only oracle retained.** Turn-three and
turn-five classifiers fail precision. Turn ten reaches 91.43% blocked-seed precision and a
positive complete policy, but only 73.08% leave-one-opponent-family-out precision. No trajectory
configuration passes both fold families. A map-only lower-quartile oracle selects 19/160 groups
at 90.789% expanded precision and +7.697 margin, but the learner has only 19 positive examples and
0/10 configurations pass. No expression or validation block follows.

### Phase 13 — post-funding roles and funding profiles

- [x] Test fixed, denial-oriented, and adaptive role assignments after the recovered funding
  ladder.
- [x] Factor funding coalition, start turn, and resident-versus-repaired continuation.
- [x] Record actual second/third-worker timing and require robust opponent gates.
- [x] Stop after the consumed discovery smoke screen when no policy qualifies.

**Phase-13 verdict — affordability is not the missing variable.** None of 26 post-funding role
policies or 20 funding/continuation profiles passes. The best profile gains +48.213 margin overall
and reaches 2.613 workers, but loses -44.300 against Adaptive Gold. Worker three arrives at median
turn 92, close to the replay architecture, so another timing constant is not justified.

### Phase 14 — compact complete Norxondor reconstruction

- [x] Distill a compact held-game intent classifier and compact CHOP/HARVEST goal rankers.
- [x] Join the workforce ladder, persistent goals, equivalent endpoints, planting, and direct work
  into a native research controller.
- [x] Diagnose closed-loop action, inventory, and workforce drift on consumed smoke seeds.
- [x] Stop after bounded mechanism repairs fail every opponent family.

**Phase-14 verdict — teacher-state imitation does not close the loop.** The 107-node intent tree
passes at 76.937% held-game accuracy, and the goal rankers fit in 128 + 32 weights. The repaired
native controller nevertheless loses -172.663 paired margin / -97.263 score and produces roughly
38 CHOP / 68 PICK actions instead of the replay target's 159 / 17. This is autoregressive state-
distribution failure, not a byte-budget failure. Direct native imitation is closed.

### Phase 15 — scaled map-geometry discovery

- [x] Predeclare seeds 1000--1299 as discovery/training only, never validation or holdout.
- [x] Generate 4,800 exact turn-three terminal opponent cells / 600 seed-seat groups.
- [x] Reuse the fixed lower-quartile label, map-only features, forest grid, and blocked-seed gates.
- [x] Close the representation if no configuration passes; otherwise freeze the exact expression
  before designating any fresh validation data.
- [x] Preserve seeds 402--999, the sealed official-map holdout, resident artifact, submit default,
  and arena.

**Phase-15 verdict — map-only representation closed.** The 3.75× larger group sample contains 65
positive groups. Its oracle remains positive at +4.591 margin / +3.993 score with all eight
opponent means positive, but expanded precision is 89.615%, below the frozen 90% bar. None of ten
forests passes; the best reaches only 47.059% actual precision and -0.277 margin. Do not widen the
model grid or designate validation data.

### Phase 16 — resident-backed residual MOVE search

- [x] Predeclare the existing GoldElite residual profile around the actual Yamo/Orchard resident.
- [x] Restrict the first smoke to consumed seeds 0--4, both seats, and eight opponents.
- [x] Implement exact resident continuation, one-target commitment, failed-target suppression,
  and release timing telemetry in a research-only runner.
- [x] Require +2 margin/+2 score, five nonnegative opponent means, worst at least -5, nonzero
  activation, p95 at most 45 ms, and no decision above 50 ms.
- [x] If the algorithmic gate passes but online execution fails, generate labels only from states
  visited by the resident/residual policy; do not return to teacher replay states.
- [x] Preserve the resident artifact, submit default, sealed holdout, and arena.

**Phase-16a verdict — broad MOVE residual rejected.** On consumed seeds 0--4 it gains +1.200
margin / +0.913 score with all eight opponent margin means nonnegative, but misses both +2 effect
gates. Decision p95 is 130.047 ms and maximum 224.449 ms. A behavior-neutral audit separates 48
accepted events: singleton banana and apple retargets mostly lose, while shack/bank redirects are
the only class positive in both margin and score.

- [x] Predeclare a bank-only replication on historically consumed, audit-disjoint seeds 5--19.
- [x] Keep only resident control and shack-target candidates; change no horizon, value floor, or
  commitment setting.
- [x] Require at least 20 activations plus the same effect, opponent, and timing gates.
- [x] Continue to own-state distillation only if effect/opponent gates pass and timing alone fails.
- [x] Preserve the resident artifact, submit default, sealed holdout, and arena.

**Phase-16b verdict — bank-only residual rejected; residual branch closed.** The fixed replication
accepts 103 redirects in 240 cells but gains only +0.508 margin / +0.554 score. Seven opponent
means are nonnegative, ScriptBoss is -0.300, p95 is 92.852 ms, and maximum is 229.508 ms. It fails
both algorithmic effect gates and both timing gates, so no own-state distillation follows. Do not
tune another residual class, horizon, threshold, or commitment.

### Phase 17 — provenance-aware opponent-crop suppression

- [x] Refresh the current resident rank and recent finished-battle census with read-only calls.
- [x] Attribute successful opponent plants, crop fruit, crop wood, and resident interception from
  exact official replay states.
- [x] Predeclare ten bounded priority profiles and discovery seeds 1300--1329.
- [x] Run all profiles against both seats and eight heterogeneous continuations.
- [x] Replicate the only qualifying profile unchanged on seeds 1330--1359.
- [x] Require both fixed blocks to pass before opening a separate candidateization phase.
- [x] Preserve seeds 402--999, the sealed official holdout, resident artifact, submit default, and
  arena.

**Phase-17 field discriminator.** The current resident is rank 45/107 at score 22.1. In its latest
80 finished battles, 12 catastrophic losses (margin at most -100) contribute 76.3% of all
negative margin. Opponents collect 100.67 wood from their own planted trees in those losses,
76.42 more than outside the catastrophic tail and almost the entire 80.31 final-wood gap. The
resident contacts only 26.84% of those crops versus 60.33% in wins even though essentially every
crop is within a current-worker ETA of 20 at birth (median 5.13). This opens crop suppression as a
new scheduling objective; it does not reopen broad renewable farming, isolated training, or
online rollout search. Frozen protocol and full field evidence are in
`data/analysis/live-agent-6553250/opponent-crop-suppression-2026-07-18.md`.

**Phase-17 verdict — bounded crop denial replicates.** Only the weakest/nearest profile,
`b100_e6`, passes discovery: +5.150 margin, +0.744 own score, -4.406 opponent score, six
nonnegative opponent families, and worst family -4.900 over 480 cells. The exact unchanged
profile passes the fresh 480-cell replication at +4.571 margin, -1.706 own score, -6.277 opponent
score, seven nonnegative families, and worst -0.217. Combined margin is +4.860 with +4.411 after
five-percent trimming. A descriptive tail audit reduces margin-at-most--100 cells from 132 to 103
and total negative-margin mass by 13.42%. Stronger/wider variants suppress more production but
over-divert the resident and fail own-score or opponent-family gates. Freeze `b100_e6`; do not
retune the treatment.

### Phase 18 — exact local candidateization

- [x] Freeze `b100_e6` without another parameter or seed search.
- [x] Predeclare an exact-parent, fail-closed source generator and standalone gates.
- [x] Reproduce the byte-identical resident slim parent, then insert only the fixed treatment.
- [x] Compile and size-gate the local standalone candidate below 100,000 bytes.
- [x] Prove turn-one resident parity and full dynamic-stream parity with the research controller.
- [x] Measure interactive latency and rerun full repository/integrity validation.
- [x] Keep the candidate local; do not play, submit, change the submit pointer, or inspect holdouts.

Protocol:
`data/analysis/live-agent-6553250/opponent-crop-candidateization-protocol-2026-07-18.md`.

**Phase-18 verdict — exact slim candidateization passes.** The fail-closed generator reproduces
the exact resident first, then emits a 64,522-byte fixed candidate (SHA-256
`6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`). It is exact on all 120
turn-one resident cells and all 16 dynamic research-controller streams; every dynamic stream
activates. Interactive latency is p95 0.970 ms and maximum 4.135 ms. The artifact remains local.
Before any controlled game, audit its activation on already downloaded official replay states;
open-loop field activation is not causal outcome evidence, but it can falsify mechanism transfer.

### Phase 19 — official-replay activation transfer

- [x] Freeze the exact 80-game current-resident corpus and first-divergence interpretation.
- [x] Predeclare reproduction, activation, catastrophic-coverage, and provenance gates.
- [x] Fetch only those fixed game results through read-only endpoints.
- [x] Replay resident and candidate on exact official pre-command state streams.
- [x] Attribute every admissible first candidate divergence to an active opponent crop.
- [x] Report cohort coverage and stop before any platform game or submission.

Protocol:
`data/analysis/live-agent-6553250/opponent-crop-field-activation-protocol-2026-07-18.md`.

**Phase-19 verdict — mechanism transfers, full-stream reconstruction gate fails.** All 80 games
fetch and decode; 64 admissible games activate at median turn 30.5, including 10/12 catastrophic
losses across seven opponents, and all 64 first divergences select an active ETA-at-most-six
opponent crop. Only 43/80 streams reproduce the resident through game end versus the frozen 60,
so the gate fails and no controlled protocol follows. The platform source is byte-identical to
the resident. Keep this formal fail; test a prefix-corrected estimand only on untouched games.

### Phase 20 — independent official-prefix replication

- [x] Define the causal prefix and fixed ten-turn continuation requirement before new results.
- [x] Split the untouched 82 older resident games into 40 discovery and 42 replication games.
- [x] Freeze exact IDs and hashes without fetching game results.
- [x] Run discovery with at least 24 stable-prefix activations and eight opponents.
- [x] Run the unchanged 42-game replication at 25 activations/eight opponents.
- [x] Keep all platform state read-only regardless of result.

Protocol:
`data/analysis/live-agent-6553250/opponent-crop-field-prefix-replication-protocol-2026-07-18.md`.

**Phase-20 verdict — corrected official-prefix mechanism replicates.** Discovery passes at 32/40
stable activations across 19 opponents; unchanged replication passes at 29/42 across 16. All 61
first divergences are active ETA-at-most-six opponent crops. Five of six catastrophic losses
activate. Across both official windows, 125/162 games activate across 56 opponents. This validates
mechanism transfer but not arena score. A capacity-controlled arena protocol is drafted and remains
unexecuted pending explicit authorization.

### Phase 21 — capacity-controlled arena transfer

- [x] Draft a same-source control, fixed candidate, checkpoint, tail, and restore protocol.
- [ ] Obtain explicit authorization before any submission or arena-state write.
- [ ] Run the same-source resident capacity control to 120 games and two stable reads.
- [ ] Only on capacity pass, run the exact candidate with fixed 60/120/possible-180 checkpoints.
- [ ] Promote or restore strictly from the frozen gates; do not retune `b100_e6`.

Draft:
`data/analysis/live-agent-6553250/opponent-crop-controlled-transfer-protocol-2026-07-18.md`.

## Kill rules

- Do not reopen isolated opening/training constants without a new measured structural mechanism.
- Do not call a worker architecture tested unless the intended additional train actually occurs.
- Do not infer causal worker value from pooled top-agent correlation.
- Do not accept an opening option whose benefit appears only through a hand-tuned short-horizon
  asset bonus.
- Do not use GoldElite as the deployed fallback or claim its residual result transfers to Yamo.
- Do not allow receding-horizon search to interrupt direct work or repeatedly rediscover an
  expired option without an explicit modeled benefit.
- Do not consume a new holdout while candidate generation, feature selection, or thresholds are
  still changing.
- Do not optimize the simulator harder after an arena-direction conflict; record the transfer
  failure and revisit the continuation/value model.

## Immediate next move

Retain restored slim resident agent `6559583` and keep `cgauto/api_submit.py` on the 62,725-byte
artifact. Phases 12--16 show that opponent-conditioned option value does not transfer, funding and
role timing are insufficient, compact teacher-state imitation does not regenerate the teacher
trajectory, and the map-only worker-three label remains unlearnable after a 3.75× group expansion.
The final baseline-preserving residual also fails: broad corrections are weak and too slow, while
the audit-selected bank class does not replicate. Do not reopen Norxondor or tune another residual
class. Phases 17--20 now provide the first fully replicated post-plateau candidate: `b100_e6`
passes generated-map discovery and unchanged replication, compiles into an exact 64,522-byte slim
artifact, and activates the intended crop mechanism on 125/162 official resident games across 56
opponents. The stronger priority variants confirm the displaced-work cost and are rejected. No
more local tuning, seed consumption, replay gate adjustment, or candidate regeneration is
justified. The next move is Phase 21 only after explicit authorization: fresh same-source capacity
control, then the exact candidate under the frozen 60/120/possible-180 arena checkpoints. Until
that authorization, retain the resident, submit default, seeds 402--999, official-map holdout, and
arena unchanged.

## Evidence base

- `data/analysis/live-agent-6553250/top-player-macro-census-2026-07-16.json`
- `data/analysis/live-agent-6553250/alternative-approaches-execution-2026-07-16.md`
- `data/analysis/live-agent-6553250/compact-workforce-iteration-2026-07-17.md`
- `data/analysis/live-agent-6553250/policy-portfolio-analysis-2026-07-16.json`
- `docs/portfolio-prospective-gate-2026-07-16.md`
- `docs/residual-search-iteration-2026-07-16.md`
- `data/analysis/live-agent-6553250/arena-retry-2026-07-17.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-gate-protocol-2026-07-17.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-validation-120-179.json`
- `data/analysis/live-agent-6553250/compact-gold-rollout-live-gate-2026-07-17.json`
- `data/analysis/live-agent-6553250/phase3-phase5-rollout-study-2026-07-17.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-arena-protocol-2026-07-18.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-arena-verdict-2026-07-18.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-arena-forensics-known60-2026-07-18.json`
- `data/analysis/live-agent-6553250/compact-gold-rollout-arena-model-audit-known60-2026-07-18.json`
- `data/analysis/live-agent-6553250/robust-first-option-discovery-2026-07-18.json`
- `data/analysis/live-agent-6553250/robust-first-option-repeat-audit-2026-07-18.json`
- `data/analysis/live-agent-6553250/norxondor-controller-iteration-2026-07-18.md`
- `data/analysis/live-agent-6553250/norxondor-portfolio-confirmation-2026-07-18.json`
- `data/analysis/live-agent-6553250/norxondor-opening-signature-study-2026-07-18.json`
- `data/analysis/live-agent-6553250/norxondor-signature-portfolio-study-2026-07-18.json`
- `data/analysis/live-agent-6553250/norxondor-shared-state-monte-carlo-2026-07-18.md`
- `data/analysis/live-agent-6553250/norxondor-partial-rollout-extended-study-2026-07-18.json`
- `data/analysis/live-agent-6553250/norxondor-parallel-latency-study-302-306-2026-07-18.json`
- `data/analysis/live-agent-6553250/norxondor-offline-distillation-and-native-controller-2026-07-18.md`
- `data/analysis/live-agent-6553250/replicated-first-option-study-2026-07-18.json`
- `data/analysis/live-agent-6553250/arena-opponent-opening-calibration-known60-2026-07-18.json`
- `data/analysis/live-agent-6553250/top-policy-objective-study-2026-07-18.json`
- `data/analysis/live-agent-6553250/escdemon-resident-opening-alignment-2026-07-18.json`
- `data/analysis/live-agent-6553250/recent-resident-field-census-2026-07-18.json`
- `data/analysis/live-agent-6553250/opponent-crop-suppression-2026-07-18.md`
- `data/analysis/live-agent-6553250/yamo-opponent-crop-priority-discovery-1300-1329.json`
- `data/analysis/live-agent-6553250/yamo-opponent-crop-priority-replication-1330-1359.json`
- `data/analysis/live-agent-6553250/opponent-crop-candidateization-protocol-2026-07-18.md`
- `data/analysis/live-agent-6553250/opponent-crop-candidate-local-gate-2026-07-18.json`
- `data/analysis/live-agent-6553250/opponent-crop-field-activation-2026-07-18.json`
- `data/analysis/live-agent-6553250/opponent-crop-field-prefix-manifest-2026-07-18.json`
- `data/analysis/live-agent-6553250/opponent-crop-field-prefix-discovery-2026-07-18.json`
- `data/analysis/live-agent-6553250/opponent-crop-field-prefix-replication-2026-07-18.json`
- `data/analysis/live-agent-6553250/opponent-crop-controlled-transfer-protocol-2026-07-18.md`
