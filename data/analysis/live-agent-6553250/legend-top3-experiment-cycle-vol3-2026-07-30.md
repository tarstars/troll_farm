# Legend score-25.40 experiment cycle — volume 3 (opened 2026-07-30)

Objective and live state: `docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` —
check before proposing. Volume 2
(`legend-top3-experiment-cycle-vol2-2026-07-23.md`) is frozen after A2-1.

Per-experiment obligations: one entry here; a CONSTRAINTS bullet for anything closed; a
STATE.md §4 update. The first session ending with this file over 100 KB freezes it and
opens volume 4.

<!-- entries below -->

## M1 — rating-system dynamics: broad source support, no recovered update rule

**Question.** Can the seven stored D61p snapshots recover the platform's score update rule
and price a +1 rating move in wins?

**Frozen method.** Exact-agent leaderboard intervals plus source-agent game-score epochs;
manifest and raw-response hash verification; bracketed outcome-completeness; prior- and
next-epoch conventions; affine, net-win, and bounded Elo-like candidates; leave-one-agent-
out validation. Protocol:
`docs/m1-rating-system-dynamics-protocol-v2-2026-07-30.md`.

**Evidence.** 8,014 raw games / 2,564,403,129 bytes hash-verify. The seven collections
contain six unique leaderboard responses. All 2,549 score changes coincide with advancing
`updateTime`. Raw `agents[].score` aligns with the rounded leaderboard in 236/243
comparisons and stays constant across 229 mixed-outcome batches. Of 329 internal score
transitions, 307 (93.31%) are outcome-complete across 45 agents, covering 2,147 wins and
2,511 losses.

**Result.** Source evidence clears the pre-model FULL threshold, but rule recovery fails.
The best held-agent Elo-like model has MAE 0.477313, median absolute error 0.284044, versus
0.478583 for predicting zero change — only 0.27% improvement, against gates of MAE ≤0.05,
median ≤0.02, and ≥50% baseline improvement. Affine and net-win rules are worse. The
next-epoch convention and exclusion of the July 21 snapshot also fail.

**Verdict: PARTIAL / DESCRIPTIVE_ONLY.** No wins-per-+1 number is reported. Keep candidate
decisions in terminal-margin units. Reopen only with exact recomputation membership and
documented pre/post score, or the platform formula. Resident and Arena untouched.

Evidence:
`data/analysis/live-agent-6553250/m1-rating-system-dynamics-result-2026-07-30.md`;
machine bundle `local_codex_1/m1-rating-system-dynamics/`.

## N2 — B4.4 reconstructed, every published claim needs correction

**Question.** Can B4.4's cohort planting, reap, wood-concentration, loop, and
scale-survival claims be reproduced with exact provenance and correct denominators?

**Source finding.** No original B4.4 JSON report or manifest survives. The tracked
8,131-game stats cut produces 23 peers / 2,700 occurrences, not 25 / 2,787. An exhaustive
prefix scan finds one unique structural match at 8,395 records (8,336 clean), SHA-256
`1f9e3855...`. It is an anchor-matching reconstruction, not the missing original.
The audit hashes 5,614 raw/trajectory files and decodes 2,963 union occurrences with zero
failures; all 2,787 anchor occurrences pass every integrity parity.

**What reproduces.** Conditional group first-plant medians are resident 191.5
(204/204), strong 29 (1,983/2,019), weak 21 (530/564). Generation-level pooled reap is
0.928%, 15.322%, and 17.198%. Strong group score is 215.527 vs resident 185.696, with
+15.03% wood and +30.02% fruit. Resident/strong equal-roster win rates reproduce as
58.18%/58.31%; the uncontrolled trajectory summaries also reproduce.

**What fails.** The 25 per-agent plant medians span 3–254, so “all peers plant by 21–29”
is false. Yamo, therealbeef and LeRenard reap 0%; mehdi_ayari reaps 0.189%, below the
resident, so “every peer” is false. Self-plant→self-chop instead occurs in 100% resident,
97.62% strong and 93.09% weak games. Pooled group composition cannot establish
per-agent wood purity; H3's exact-opponent and quartet controls remain binding and
invalidate the B4.4 causal survival/mechanism ranking.

**Purpose correction.** Resident early crops (turn ≤50) include 18/23 self-harvested
generations and 2,022 gained fruit. All 1,027 resident crops planted after turn 250 are
self-chopped, yielding 1,060 wood, with zero self-harvest. Strong/weak cohorts show the
same broad early-harvest and late-chop separation. Early orchard establishment and
post-250 fruit-to-wood conversion are distinct compatible outcomes, not a contradiction.
Turn alone still does not prove subjective intent or intervention value.

**Verdict: B4_4_CORRECTED; C1–C7 all CORRECTED.** Cite N2, never B4.4 as written.
D175a's controlled harmful early-plant result remains binding. Resident and Arena
untouched.

Evidence:
`data/analysis/live-agent-6553250/n2-b4-4-verification-result-2026-07-30.md`;
machine bundle `local_codex_1/n2-b4-4-verification/`.

## M2 — no actionable opponent-specific loss

**Question.** Does the exact resident systematically underperform against any currently
active exact opponent after matching its own games on contemporaneous strength, seat,
map dimensions, resident score, and initial-tree count?

**Evidence.** The frozen corpus verifies at 9,082 records / 9,018 clean games, including
241 resident games against 72 exact identities. Twelve active identities have at least
five games and two per seat; only R1FA, BoatBuilder, and a76a44 retain at least ten
within-resident controls for every target game.

**Result.** R1FA has a stable −31.621 matched-margin hint, but CI
[−81.015,+22.243], Holm p 0.229, and win residual −0.087 fail the frozen uncertainty,
multiplicity, and win-effect gates. BoatBuilder's −73.178 estimate is imprecise and
reverses by seat (−152.91 / +46.42). a76a44's residual is +9.526. None clears all ten
actionability gates.

**Verdict: `NO_ACTIONABLE_MATCHUP`.** No identity-specific implementation, replay
mechanism follow-up, resident change, or Arena action. Keep R1FA only as a surveillance
hint until more exact games narrow the evidence.

Evidence:
`data/analysis/live-agent-6553250/m2-opponent-specific-losses-result-2026-07-30.md`;
machine bundle `local_codex_1/m2-opponent-specific-losses/`.

## M3 — no actionable resident seat asymmetry

**Question.** Does exact resident `6561795` underperform in either player seat after
same-exact-opponent, pre-outcome matching?

**Evidence.** The frozen corpus has 126 seat-0 and 115 seat-1 resident games. Thirty-seven
seat-1 targets across 23 exact opponent identities match seat-0 controls on exact
identity/map dimensions, contemporaneous scores, and initial-tree count; all support gates
pass.

**Result.** Seat-1 minus seat-0 matched margin is +10.088, CI
[−16.813,+38.912], two-sided cluster-null p 0.484, with +0.101 win difference. The raw,
reverse, pseudo-lineage, score-band, time-half, and leave-one-out signs also point toward
seat 0 being worse. The broader game-weighted fixed-opponent contrast is only +5.29 and
the identity-equal contrast flips to −1.37.

**Verdict: `NO_ACTIONABLE_SEAT_ASYMMETRY`.** The 20-point magnitude, CI, and p gates
fail. No seat branch, replay-mechanism follow-up, resident change, simulation, or Arena
action.

Evidence:
`data/analysis/live-agent-6553250/m3-seat-asymmetry-result-2026-07-30.md`;
machine bundle `local_codex_1/m3-seat-asymmetry/`.

## M4 — no material strength drift; strong lineage concentration

**Question.** Who does exact resident `6561795` play, how concentrated is that mix, and
is the newest opponent-strength distribution materially different from the oldest?

**Evidence.** The 241-game resident panel compares the oldest/newest 60 games by
contemporaneous opponent score. Terminal outcomes are excluded. Uncertainty uses 20,000
moving-block bootstraps and all 241 circular temporal rotations.

**Strength result.** Mean opponent score moves 22.297→22.735: +0.438, CI
[−0.865,+1.867], p 0.884. Median drift is −0.155. Window-40/80 and both seats are
positive, but magnitude, CI, temporal-null, and median gates fail.

**Composition result.** Exact identities contract 38→16 and pseudonyms 38→4. The newest
60 games are 47 FreZzz, 7 Bubaptik, 5 goq, and 1 IlyaPol. Every late exact ID is absent
from the early endpoint, but only 6/60 late games use a new pseudonym; current-active
pseudonym lineage share remains 100%. This is submission-version churn plus concentrated
matchmaking, not wholesale lineage replacement.

**Verdict: `NO_MATERIAL_MATCHMAKING_DRIFT`.** Do not explain score/rank movement by a
proven stronger opponent mix or create composition-specific policy. Surveillance must
report exact IDs and pseudonym lineages separately.

Evidence:
`data/analysis/live-agent-6553250/m4-matchmaking-composition-result-2026-07-30.md`;
machine bundle `local_codex_1/m4-matchmaking-composition/`.

## M5 — no resident-wide turn-cap loss association

**Question.** Are exact-resident games reaching turn 300 materially worse than comparable
shorter games?

**Evidence.** Recorded duration is 106–300; 125/241 resident games reach turn 300. The
primary pre-game match supports 97 cap targets across 43 exact identities. Duration is a
post-game category and the source has no trusted terminal-reason label.

**Result.** Matched cap-minus-non-cap margin is −1.440, CI
[−26.251,+25.112], two-sided p 0.710; win residual is +0.184. Seat estimates
+0.724/−3.474 and early/late target estimates −14.529/+11.381 reverse. Same-pseudonym
and same-exact-opponent sensitivities are positive (+11.852/+3.867); near-cap is −2.036.

**Verdict: `NO_MATERIAL_LENGTH_ASSOCIATION`.** H3's full-300 concentration does not
generalize beyond its narrow quartet/roster comparison. Do not infer a cap mechanism or
build a duration-conditioned policy. H3's cause-versus-symptom and always-on-control
requirements remain binding.

Evidence:
`data/analysis/live-agent-6553250/m5-game-length-effects-result-2026-07-30.md`;
machine bundle `local_codex_1/m5-game-length-effects/`.

## N5 — real late-planting situation, sub-material observed-yield opportunity

**Question.** What is the cost of omitting the postmortem's instruction to park near the
opponent shack and contest last-minute planting?

**Integrity.** All 382 resident/yamo cohort occurrences decode; exact index, cohort,
dependency, resident, raw, trajectory, unique-PLANT, and dual-lineage checks pass. The one
resident/yamo game overlap gives 381 unique games and two valid subject perspectives.

**H13 reproduction.** Resident opponents create 388 target generations in 78/170
endgame-reaching games (45.88%, 2.282/reaching game); yamo opponents create 205 in 37/103
(35.92%, 1.990). A target is born after turn 250 while the subject leads pre-turn.

**Opportunity.** Resident opponents extract 1,487 carried score-equivalent units from
targets versus our 241; we contact 51/388 and are at optimistic ETA ≤1 for 24/388.
Seventy-four percent of targets lie within distance two of the opponent shack. The frozen
deny-plus-capture factor-two observed-yield ceiling is 37.21 conditional on a target game,
but **11.9917 across all 242 games**, whole-game bootstrap CI **[8.7273,15.7603]**, below
the 20-margin gate. The never-contacted version is 10.314; yamo's identical descriptive
quantity is 8.471.

**Verdict: `NO_MATERIAL_CONTEST_OPPORTUNITY`.** Enemy units can share cells, so this is
access for later HARVEST/CHOP, not body-blocking. Extracted cargo is not banked score, and
the factor-two quantity is replay-conditioned rather than causal. No controlled
simulation, policy change, resident change, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/n5-endgame-opponent-plant-contest-result-2026-07-30.md`;
machine bundle `local_codex_1/n5-endgame-opponent-plant-contest/`.

## N6 — the one nonzero denial-weight sweep closes at development

**Question.** Does either preregistered nonzero alternative to the resident's guessed
`900/(1+opponent_distance)` focus bonus produce a directionally faithful, opponent-robust
improvement?

**Lock and panel.** The exact sacred resident was normalized only by moving its crate-only
allow attribute onto three runner modules; LOW/CONTROL/HIGH then differ solely at
450/900/1800. The A2-0b referee and continued RNG hashes remain exact. Compilation, ten
focused tests, scalar-only diffs, jobs-1/jobs-4 smoke identity, 48 trajectory decodes, and
all six detector executions passed before the lock. After the required `medium_data`
preflight, fresh maps 9,858,000–031 ran once: 32 maps × two seats × eight opponent
families = 512 paired tasks and 512 rows per arm, 1,536 total. Coverage is exact; critical,
unclassified, ownership, and opponent-command-mismatch counts are zero. Panel SHA-256:
`f57817b3d4906c3d7941df2ab8257069ccd199b8280843db156c13f255bd41ae`.

**LOW 450.** Commands diverge in 378/512 tasks, but only 15/97 directionally comparable
common-state first divergences move focus in the intended direction (15.46%, gate 60%).
Mean paired margin is −0.7539; seat deltas are −1.1133/−0.3945 and only 3/8 families are
positive. It fails mechanism, overall value, both-seat, and family-breadth gates.

**HIGH 1800.** Commands diverge in 273/512 tasks. Mean margin is +0.5586 and both seats
are positive (+0.4141/+0.7031), but only 12/77 comparable first divergences are
directional (15.58%) and only 4/8 families are positive. Mean opponent score rises by
+0.2715. It fails mechanism and breadth; its small heterogeneous aggregate cannot select
it for confirmation.

**Verdict: `CLOSED_AT_DEVELOPMENT`.** No arm is selected. Confirmation maps
9,859,000–127 remain untouched; there is no candidate, resident change, or Arena action.
This completes reproduction G1 once. Keep 900 and do not retune zero, capable-only,
intermediate weights, or a second grid.

Evidence:
`data/analysis/live-agent-6553250/n6-denial-weight-sweep-result-2026-07-30.md`;
machine bundle `local_codex_1/n6-denial-weight-sweep/`.

## E1 — opening micro-optimality is narrower than registered

**Question.** Is a first-3–5-turn exhaustive opening audit genuinely new, and if so what
exact action/value object remains?

**Coverage reconstruction.** Historical records already contain CONTROL plus dynamic
max-affordable plus all 27 fixed harvest-0 first-worker specs under eight continuations and
six process realizations; complete farm-first/max-bank opening options; a terminal-valued
turn-one rollout selector and its Arena rejection; fixed one-source prefixes; an
eight-action recurrent opening portfolio; all four one-batch and all 16 two-batch ordinary
mode sequences; and bounded primitive MOVE residual search. Their binding failures remain:
no robust first-worker activation, farm-first −97.57 score, later funding −56.78,
two-batch spread 3.455 <15, and residual effects +1.200/+0.508 below gates.

**Scope correction.** “Never audited” is false for those classes. “Short-horizon” also
cannot mean short reward: replay archaeology observes foundational-farmer bank recovery
around +68 turns. The only distinct residual is a short sequence over the resident's own
candidate pairs during turns 1–5, followed by exact resident continuation to terminal.
Arbitrary primitive enumeration lacks a bounded semantic grammar.

**Verdict: `NARROWED_TO_N4_PREFIX_ORACLE`.** N4 Phase A is already responsible for exact
candidate-pair publication/census, so E1 opens no implementation or seed range until that
surface is accepted. Any later oracle is diagnostic only; selection, opening-book,
candidate, and Arena gates remain separate.

Evidence:
`data/analysis/live-agent-6553250/e1-opening-micro-optimality-scope-audit-2026-07-30.md`.

## E2 — immediate banking routes are optimal; a small hindsight tie remains

**Question.** Does the exact resident waste carrying time through a longer home-door route,
joint door assignment, or unstable door target?

**Method and integrity.** An external observer ran the exact 62,725-byte live source on
reused seeds 0..199 in both seats. It confirms a carrying door move as banking only when
the same cargo reaches a positive `DROP`, reproduces occupied/selected-target eligibility
and `ceil(BFS/speed)`, enumerates simultaneous carrier assignments, and binds the first
post-deposit productive target. Seven tests and the self-test pass; 16-seed jobs-1/jobs-8
details are byte-identical. The 200-seed panel contains 11,260 confirmed deposits in
400/400 side-games and 10,597 next-target-bound episodes.

**Immediate result.** All 4,855 identifiable carrying door moves have zero ETA regret; all
64 joint carrier checks have zero assignment regret; no confirmed return changes its door.
Eighteen forced/occupied-door checks and seven terminally censored returns remain explicitly
unidentified.

**Hindsight result.** An inbound-ETA-tied alternate door is one turn nearer the later
observed task in 134/10,597 bound episodes, all wood, balanced 67/67 by seat. The total is
134 movement turns = 0.335 per side-game, maximum one per episode. This is conditioned on
future scheduler output and is not causal terminal value or rating.

**Verdict: `ROUTE_RESIDUAL_OBSERVED — NOT_EXPERIMENT_JUSTIFIED`.** Close immediate
bank-router and persistence work. The small future-conditioned tie residual does not clear
the experiment evidence bar; no source, candidate, fresh range, resident, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/e2-banking-route-efficiency-result-2026-07-30.md`;
compact JSON beside it; external detail under
`outputs/local_codex_1/e2-banking-route-efficiency/`.

## E3 — chop-order premise duplicates stronger exact-resident oracles

**Question.** Is multi-tree chop ordering unaudited because the resident scores only the
current tree's travel/growth/chop/return yield?

**Coverage.** Production dynamically reconstructs every tree candidate each turn and stores
no order. The exact-live remembered-current-tree bonus was only +0.617 on 60 reused seeds.
More importantly, the resident-local one-job terminal oracle executes `FELL_BANK` to
completion then resumes exact resident; it failed its selected-root gate at +18.584 vs +20
and closed larger target catalogs. D36 is a strict sequence superset: exact resident roots,
up to two targets per acquisition kind per unit, joint persistent bundles, exact terminal
rollouts, and replanning at up to four completion boundaries. It ran multiple bundles in
87/128 tasks and 292 non-control epochs.

**Value and verdict.** D36's repeated exact-resident upper bound is +10.633 margin vs its
+25 gate and +19.617 own score vs +68; only 2/8 families reach +15 margin, and further
resident target/overlay iterations are explicitly closed. Therefore E3 is
`VOID_PREMISE_DUPLICATE`, not an N4 dependency. No cluster definition, two-tree
permutation, simulation, source, range, candidate, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/e3-chop-order-scope-audit-2026-07-30.md`.

## E4 — the orchard-mother tie is active but lexicographic order wins

**Question.** Does reversing the live secure-orchard initializer's lexicographic secondary
choice between equal enemy-distance mother cells improve terminal local value?

**Scope and integrity.** A result-blind 0..999 census finds 57 eligible seeds per symmetric
seat and ten two-way ties. The audit changes exactly one comparator in a temporary source,
then exhausts ten tied seeds × six frozen opponents × both seats. Sixteen unique-best
sentinels are exact. The `motion` opponent required a child-only deterministic clock and
entropy shim because its wall-clock RHEA and randomized collections made repeat-control
runs differ; no bot source byte changed. Jobs-1/jobs-8 tied, sentinel, and delta hashes
match, all 152 rows complete, and stderr/malformed-command counts are zero.

**Mechanism.** Policy streams diverge on 10/10 tied seeds, in 51/60 and 44/60 cells by
seat, and in all six families. `ACTIVE_TIE` passes.

**Value and verdict.** Reversal loses −8.55 paired margin on tied maps and **−0.0855**
across the exact 1,000-map census. Both seat means are negative (−7.667/−9.433), and every
family is negative (worst ringfix3 −26.65). Own score is −10.80 on tied maps while wood
edge changes only +0.133.

**Verdict: `KEEP_LEXICOGRAPHIC`.** Keep the current comparator. No persistent alternate,
candidate, new map, resident change, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/e4-orchard-mother-tie-audit-result-2026-07-30.md`;
compact JSON beside it; implementation lock and hashes under
`local_codex_1/e4-orchard-mother-tie-audit/`.

## E5 — on-site ripeness replanning is real but non-material and seat-unstable

**Question.** When an on-site unripe fruit candidate becomes `WAIT`, does removing only
that candidate and taking the resident's next-best task improve terminal local value?

**Integrity.** A stderr-only probe is stdout-exact on eight reused raw/probe sentinel
cells. The temporary alternate adds one eligibility condition; no action is forced. The
60-seed × six-opponent × both-seat panel completes 360 control/alternate cells (1,440
games). Every first divergence has an exact common prefix and matching probe event.
Jobs-1/jobs-8 rows and normalized payloads are exact; stderr/command gates pass.

**Mechanism.** The control emits 162 waits in 57 episodes, all opening PLUM/LEMON waits.
Replanning changes 33 cells across six seeds, both seats, and all families. `ACTIVE_WAIT`
passes.

**Value and verdict.** Whole-panel margin is only +0.1056; activated-only +1.152 is
post-policy descriptive. Seat means split −0.200/+0.411, motion/race are negative, and
346/360 cells are unchanged. Own score +0.150 and wood edge +0.025 are similarly small.

**Verdict: `KEEP_RIPENESS_WAIT`.** Magnitude and both-seat stability fail. No persistent
alternate, candidate, new map, resident change, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/e5-ripeness-wait-audit-result-2026-07-30.md`;
compact JSON beside it; implementation lock and hashes under
`local_codex_1/e5-ripeness-wait-audit/`.

## E6 — seed-carry premise duplicates D167/D168

**Premise correction.** “Which seed to carry and when to drop it” was not unexamined.
`PLANT` consumes the carried seed; `DROP` is generic shack banking and belongs to E2.

**Coverage.** D167 classifies all 135/135 local successor returns as BANK_SEED and later
field rates at 67.5%; field pre-carry is 40.5% versus resident 0/1,024. D168 implements
post-suppression pickup and pre-carry over exact continuation, freezes bank revalidation,
species tie-break, destination, and horizons, and activates the same 164/1,024 tasks in
both seats and seven families.

**Value.** Post-return loses −6.732, CI [−8.398,−4.077]; pre-carry loses −8.207,
[−10.528,−5.709]. All active family means are negative; even committed post-return
episodes are −7.22. D168 explicitly closes species/horizon/arming retuning.

**Verdict: `VOID_PREMISE_DUPLICATE`.** The surviving timing question belonged to the
rollout-valued option interface, not another fixed seed heuristic. No simulation, source,
range, candidate, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/e6-seed-carry-scope-audit-2026-07-30.md`.

## E7 — blanket focus inversion loses, but a per-seed hindsight residual is material

**Question.** The resident chooses LEMON or PLUM once by the summed initial home-shack BFS
distance and applies that species all game. Is the other binary choice better, and what is
the exhaustive per-map hindsight ceiling?

**Integrity.** Control is the exact 62,725-byte live source. A temporary source changes
only the unique `type_to_cut` initialization and maps LEMON↔PLUM. Independent geometry
finds 35 LEMON and 25 PLUM choices with 60/60 symmetric-seat agreement. Reused seeds
0..59 × six frozen opponents × both policies × both seats complete 360 cells / 1,440
games. All 720 seat-games diverge from an exact common prefix; the opponent never leads.
Jobs 1 and 8 have byte-identical normalized payloads and matching value, geometry,
divergence, and oracle hashes. Command/stderr gates pass and the sacred resident remains
`fff6669b…`.

**Direct result.** Blanket inversion loses **−12.1736** paired margin. Both seats lose
(−7.400/−16.947), and all six families are negative (−5.950 to −20.525). Own score is
−1.014 while opponent score rises +11.160. `ACTIVE_FOCUS` passes, but every direct value
gate fails.

**Hindsight result.** The frozen oracle averages all six opponent deltas per seed and then
chooses CONTROL or FLIP once. It chooses FLIP on 24/60 seeds and gains **+10.5097**
seed-balanced margin; selected-policy seat gains are +10.886/+10.133. Every
leave-one-family-out evaluation is positive (+5.450 to +15.450), so the residual is not an
opponent-specific choice artifact.

**Verdict: `HINDSIGHT_RESIDUAL_ONLY`.** Keep the current default and do not persist the
flip. The binary species decision contains a large local hindsight residual, but the
consumed synthetic-map labels are not a prospective selector or field estimate. E7a records
a peer-review-gated decision about a separately frozen, disjoint-map selector protocol; no
fit, candidate, source change, or Arena action follows from E7.

Evidence:
`data/analysis/live-agent-6553250/e7-type-to-cut-audit-result-2026-07-31.md`;
compact JSON beside it; implementation lock and hashes under
`local_codex_1/e7-type-to-cut-audit/`.

## S1 — exact endgame solver is infeasible under the current representation

**Question.** Is “solve the last N turns exactly” a distinct and plausibly deployable
50 ms direction, or does every tractable version reduce to a closed candidate/rollout
interface?

**Scope.** Full exactness means both players' simultaneous primitive commands, referee
chance, and exact stall/mercy/turn-cap transitions. Known-policy continuation instead
requires cloning bot processes after counterfactual branches. Resident-candidate
restriction is not exact and overlaps N4/D36/S3. Existing endgame-switch retuning,
threatened-response MC, shared-state MC, MOVE residual, and overlays stay closed.

**Census and integrity.** The exact resident runs reused seeds 0..59 × six opponents ×
both seats: 720 games. Public roots are captured at t251/t276/t291. Coverage is exact;
jobs 1/8 normalized payload and game/root hashes match; six focused tests include
exhaustive engine agreement on collision vectors; command/stderr gates pass; the sacred
source remains `fff6669b…`.

Late states are relevant: 246/720 (34.17%) reach t251, 188 (26.11%) reach t276, and 155
(21.53%) reach t291, giving 589 roots. Exact movement-only simultaneous one-ply position
outcomes are median 600/max 6,400 overall. At t291, with ten nominal turns left, they are
median 450/p90 1,944/max 3,825. First-ply branching alone is not the decisive rejection.

**Feasibility.** The distinct full-game object must expand that lower bound across 10–50
turns and add every opponent, referee-chance, plant, resource, and non-MOVE branch. The
live bot does not observe continuing referee RNG state. Known-policy `BotSession` processes
expose stdin/stdout only and cannot serialize/fork; branch replay is not deployable.
Candidate restriction is the only tractable shortcut and returns to N4/D36/S3. Strict
subset searches already cost 92.852–279.46 ms p95 versus the 50 ms budget.

**Verdict: `FULL_EXACT_INFEASIBLE`.** Close S1 under the current representation. Reopen
only with a proof-preserving compact full-game state reduction plus an exact referee chance
model. Do not implement a candidate wrapper, known-opponent replay, deeper horizon/beam,
source edit, fresh panel, candidate, or Arena action. N4 and S3 remain unchanged.

Evidence:
`data/analysis/live-agent-6553250/s1-endgame-solver-feasibility-result-2026-07-31.md`;
compact JSON beside it; implementation lock and hashes under
`local_codex_1/s1-endgame-solver-feasibility/`.

## S2 — opening book lacks both its surviving action library and map representation

**Question.** Can the project now precompute strong first-K-turn sequences by map class
and look them up at runtime?

**Required chain.** A book requires a non-closed sequence library, terminal continuation
labels, a prospective pre-action map representation, a class→sequence policy with
abstention/held transfer, and only then a cheap lookup. Lookup latency cannot repair
missing upstream objects.

**Action evidence.** E1 already reconstructs the complete first-worker grid, opening
macros, terminal turn-one rollout, fixed source prefixes, recurrent portfolio, and all
one/two-batch semantic sequences. They are closed by no robust activation, −97.57/−56.78
macro losses, Arena decay 21.7 vs 24.1, 45–60% receipt, −1.758 recurrent value, or
38.54% breadth / 3.455 spread. The sole survivor is E1's bounded multi-turn resident
candidate-pair prefix. It is not enumerable before accepted N4 Phase A and has no terminal
labels until a separate E1 oracle runs.

**Representation evidence.** D63 static opening/map behavior selection falls from AUC
0.830 discovery to 0.479 validation. D91's large development selector occupies only 5/16
maps. Phase 15's expanded oracle misses its 90% gate at 89.615%, while the best fixed
map-only forest reaches 47.059% precision and −0.277 margin. D153 conditional value falls
from +14–17 training to +1.820 held with 44.44% harmful choices. Generated-map scalars
also place all 80 official roots outside support. These do not prove all future
representations impossible; they do leave S2 without an accepted one.

**Verdict: `DEPENDENCY_GATED_REPRESENTATION_BLOCKED`.** Keep S2 on the register but do
not implement it. Reopen only after material N4→E1 terminal sequence value and a genuinely
new pre-action representation transfer on disjoint official maps and held opponents. Do
not enumerate sequences, fit classes, reuse consumed panels, build a book/source/candidate,
or run Arena. H11, N4, and E1 retain their distinct scopes.

Evidence:
`data/analysis/live-agent-6553250/s2-opening-book-scope-audit-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/s2-opening-book-scope-audit/`.

## S3 — putibuzu's rollout-plus-beam combination is distinct but multi-gated

**Question.** Is the #2 finisher's public search architecture already inside a closed
project family, or does it define a genuinely new experiment?

**Public shape.** Putibuzu describes about 30 joint combinations from top-three tree
targets plus local actions, one lightweight greedy policy for generation and both-side
continuation, values averaged at depths 3/5/7/9/12, a large-map three-ply `5→3→all`
beam, and small-map explicit-opponent maximin. The evaluator mixes score differential,
distance-discounted carries, tree ownership/proximity, and future production.

**Closure matrix.** No project experiment combines those dimensions. Phases 3–8 are
turn-one terminal option selection; Phase 11 chooses between two complete macros;
Phase 16 changes at most one MOVE target and keeps direct work immutable; D36 is an
offline repeated bundle upper bound; D84 has at most three threat-response arms and no
beam. S1 establishes that pruning to ~30 actions is approximate, not exact. The nearest
staged-search ancestors test strict subsets.

**Three gates.** The public prose omits implementation-defining weights, candidate/tie
rules, exact beam semantics, map cutoff, opponent breadth, and chance handling. The
opponent/value substrate has already failed transfer: the live rollout candidate reached
21.7 versus 24.1 control, while the 29-option/eight-model repair selected nothing robustly.
Exact-resident strict subsets cost 92.852–130.047 ms p95. An old lightweight GoldElite
subset did reach 28.53 ms p95, so a new lightweight policy is not proven impossible;
runtime is provisional while specification and model gates are direct.

**Verdict: `DISTINCT_MULTI_GATED`.** Do not implement or value-test S3. S3a is a
peer-review-gated specification/latency decision after N4 Phase A: choose explicitly
between exact resident candidate-pair overlap and a clean-room new broad controller,
then qualify legality/timing on consumed states before any score panel. No source, map,
game, candidate, submission, or Arena action was created.

Evidence:
`data/analysis/live-agent-6553250/s3-putibuzu-rollout-beam-scope-audit-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/s3-putibuzu-rollout-beam-scope-audit/`.

## H10a readiness — the 104-channel premise is invalid, spatial reopening survives narrowly

**Question.** Can D172's exact option-label experiment literally replace its 81-field
input with the project's existing 104-channel board tensor?

**Interface audit.** The tensor in `rl_level1` is not a generic board extractor. Seventy-
two channels describe current terrain, plants, units, banks, scores, workforce, and home
geometry after a controlled-seat adaptation. Fourteen describe one selected curriculum
unit; two are Level-1 episode progress; fifteen encode its fixed training recipe, cost,
deficit, affordability, and needed-resource routing; one is previous primitive-action
history. D172's 13 global macro arms have no single outcome-blind value for those 32
channels, and the existing encoder hardcodes player 0 without canonical rotation.

**Substrate.** D172's four shards are present: 79,997 exact labels over 27,392 unique
`(map,seat,opponent,turn)` state keys, zero duplicate state/arm keys, 512 official-map
seeds, both seats, and eight families. The stored rows contain 81 scalar/candidate fields,
not board tensors, but a compose-only control replay can add one tensor per consumed
state without new outcomes. Storage preflight passed; a deduplicated 72-channel uint8
table is 477,278,208 bytes. No write was made.

**Prior evidence.** D29's 36-plane turn-75 farm selector died from the pre-D33 generated-
map domain; D172 is already on `generate_official`. D18's 137-channel primitive residual
scorer failed 0/40 recipes, a serious negative prior, but it did not use D172's macro
options, exact labels, states, or gates. Neither is a duplicate closure.

**Verdict: `NARROWED_TO_GENERIC_SPATIAL_AUGMENTATION`.** Literal 104-channel reuse is
invalid. H10a-r1, if peer-accepted, uses 72 player-relative current-state channels plus
the unchanged 17-field D172 decision block. A two-conv design is 6,541 parameters versus
the frozen 12,288 cap. Preserve all 13 arms, exact labels, budget-1 semantics, τ=+1,
partitions, LOBO/safety gates, veto, and sealed confirmation. First qualify a compose-only
exporter on consumed states; no source, bulk file, model, GPU/YT job, candidate, or Arena
action exists now.

Evidence:
`data/analysis/live-agent-6553250/h10a-spatial-planes-readiness-audit-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/h10a-spatial-planes-readiness-audit/`.

## L1 readiness — delineate replay cloning is distinct only at the primitive output

**Question.** Does today's larger exact-agent corpus make behaviour cloning from
rank-one delineate a new executable experiment, despite the project's imitation
closures?

**Corpus.** The 9,082-game parsed corpus contains 199 games with exact agent
`6479768`, including all 26 Phase-9 games plus 173 new ones. All 199 raw replays exist;
the panel spans 98/101 seats, 53 opponents, and 59,403 turns. The existing decoder
matches all 59,403 trajectory turns with zero unknown updates and yields 145,448
per-unit decision rows. Replays contain 144,265 explicit primitive commands and 378
actual TRAIN events/specs.

**Correction to the premise.** Phase 9 did test delineate: its 17,743 rows from 26 games
reached 60.413% held-game accuracy but only 0.329 macro F1 on 18 coarse objectives. L1
is distinct because its present surface is 7.65× more games, exact primitive targets,
and spatial/full state—not because the #1 teacher was absent before. Phase 14's
Norxondor controller (76.937% teacher-state intent, −172.663 paired margin closed-loop)
and D41a's 85% MLP versus a 100% exact decoder remain binding negative priors, not
duplicates.

**Identifiability boundary.** Public map/state, final command order, unit IDs, target
coordinates, resource kinds, actual TRAINs, and emitted history are exact. Delineate's
continually selected train target, previous internal target, 3,290 logits, top-X
alternatives, joint beam alternatives/probabilities, weights, PPO signals, and
curriculum state are not replay labels. The public 104-plane four-block ResNet,
144-candidate train head, ~101k policy parameters, ~98k-character submission, and
2–3 ms runtime demonstrate feasibility of the architecture class, but the weights and
hidden decisions were not published.

**Verdict: `DISTINCT_PRIMITIVE_ONLY`.** L1a may begin only after peer acceptance, with
a compose-only exact-agent state/final-command extractor and parity report on the 199
consumed games. Do not infer task/plan/beam labels. Split by whole game, preserve a
temporal block, and report held-opponent sensitivity. Any later teacher-forced fit is
diagnostic only; source integration requires a separately frozen closed-loop
official-map score/margin, family-transfer, legality, runtime, size, and substrate gate.
No extractor, bulk dataset, model, fit, game, source, candidate, submission, or Arena
action was created.

Evidence:
`data/analysis/live-agent-6553250/l1-delineate-cloning-readiness-audit-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/l1-delineate-cloning-readiness-audit/`.

## L2 — learned target ranking is dependency-gated on N4

**Question.** Does “learned tie-break / target ranking inside the existing architecture”
name a third live, labeled decision surface outside the project's selector closures?

**Live graph.** `main()` constructs `SecureOrchardBot::new()`, whose active inner bot is
the tuned Yamo policy; task-market, banana-factory, opponent-crop, and ScarceIntent
accretions are dead and excluded. Candidate generation emits primitive command, score,
and target. One worker takes a score argmax; exactly two workers exhaustively maximize
the summed score over compatible pairs; greater-than-two greedy ranking is unreachable
under the hard roster cap. Collision/path resolution then rewrites MOVE conflicts. The
outer orchard wrapper has a mother comparator and fixed starter/protection rewrites.

**Overlap.** The compatible-pair loop is exactly the peer-owned N4 Phase-A census object.
An exact-score tie has no value label before N4 measures its coverage/boundaries; an
unequal-score reranker additionally requires separately authorized terminal
counterfactual value. Single-worker choice is transient opening/primitive policy and E1
is already narrowed to an N4-prefix oracle. D171/D176 close collision/detour ties on
value; E4 closes the mother tie; E2 finds immediate/joint home-door routing already
optimal and only a 0.335-turn/side-game future-conditioned residual. D18, D41a,
D79-D84, D97-D158, and D172 bind broad primitive/target/value scorers. L1 and L3 are
separate register objects, not aliases.

**Verdict: `N4_DEPENDENCY_GATED`.** Do not create L2a, instrument/export pairs, fit a
ranker, edit source, or open a panel. Wait for accepted N4 Phase A. If it clears, a
separate Phase-B decision must establish material terminal value before any residual
ranker can be scoped. No source, model, game, candidate, submission, or Arena action was
created.

Evidence:
`data/analysis/live-agent-6553250/l2-learned-target-ranking-scope-audit-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/l2-learned-target-ranking-scope-audit/`.

## L3 — learned evaluator is also dependency-gated on N4

**Question.** Is replacing the live scheduler's hand-tuned score with a fitted evaluator
a distinct experiment merely because it retains the existing action grammar?

**Score flow.** The active tuned Yamo inner bot hard-generates and filters phase-specific
candidates before scoring them. Scores mix categorical bands with travel/wait,
wood-per-turn, denial distance, bank, conversion, and endgame terms. Hard filters can
force egress/WAIT, protect orchard cells, or suppress PICKs. The selector then takes a
one-worker argmax or compatible two-worker summed-score maximum. Collision handling and
the outer secure-orchard wrapper can rewrite the result afterward. Scores cannot directly
change TRAIN, legality, the roster cap, or invariant rewrites; nevertheless, replacing
them can change the ordinary command pair repeatedly and therefore the whole trajectory.

**Labels and closures.** Numeric-score or resident-action regression is imitation, not
improvement; D41a demonstrates the approximation risk. One-deviation terminal advantage
on exact resident alternatives is closed by D16-D19. Repeated broad evaluation is closed
or expands to a new programme under D36, D41-D44, D79-D84, D97-D158, and D169-D172.
N6 directly shows the nonlocal authority of even one live score scalar: its LOW/HIGH
weights alter 73.83%/53.32% of task command streams yet yield −0.754/+0.559, with HIGH
positive in only 4/8 families. H10a's spatial D172 option scorer remains a separate,
peer-gated budget-1 item.

**Verdict: `N4_DEPENDENCY_GATED`.** The only unconsumed exact-live evaluator label is
compatible-pair continuation value, whose surface is owned by N4. Do not create L3a,
instrument/export candidates, fit a scorer, or open a panel. If N4 Phase A closes, L3
closes with it. If a separately authorized Phase B later demonstrates material value,
replace L2/L3 with one precisely bounded compatible-pair residual item. No source, model,
game, candidate, submission, or Arena action was created.

Evidence:
`data/analysis/live-agent-6553250/l3-learned-evaluator-scope-audit-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/l3-learned-evaluator-scope-audit/`.

## N7 — deployment already excludes the dead accretions; preserve sacred fixtures

**Question.** Can H13's four live-dead source families be removed safely, and from which
artifact?

**Construction and deployment.** Independent constructor tracing reproduces H13:
`main()` uses `SecureOrchardBot::new()` with the tuned live Yamo inner bot; ScarceIntent,
task-market, banana-factory, and opponent-crop controls remain disabled. The current
62,725-byte live deployment has zero occurrences of all four families. Banana factory,
task market, and opponent-crop scoring were already absent from its 90,547-byte pre-slim
ancestor; the fail-closed slimmer specializes the fixed-off branch and removes
ScarceIntent plus other dead items.

**Artifact boundary.** The 275,377-byte sacred development source is byte-identical with
the D171a control snapshot, is exposed by the library as `resident_policy`, has 23 direct
path importers, and retains specialized constructors/telemetry and embedded tests used by
historical experiment runners. “Dead from main” is therefore not “safe to delete from
the research fixture.”

**Verdict: `DEPLOYMENT_ALREADY_SLIM`.** The exact additional live-deploy deletion ceiling
is **0 bytes / 0%**. The 212,652-byte gross sacred-to-live difference is not attributable
to these four families because it includes minification, tests, APIs, unrelated dead
items, and other fixed-policy specialization. Keep the live deploy/default pointer,
sacred source, exact snapshot, runners, and historical artifacts unchanged. No cleanup
patch or successor is justified. A future maintainability migration, if separately
owner-authorized, must create a versioned non-sacred module and prove consumer parity
rather than clean the sacred file in place.

No source, formatter, deletion, regeneration, compile, test, game, map, package,
candidate, submission, or Arena action occurred.

Evidence:
`data/analysis/live-agent-6553250/n7-dead-accretion-removal-plan-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/n7-dead-accretion-removal-plan/`.

## H4 — scaling warning replicates, but no individual bill source is deniable

**Question.** What pays the opponent's worker-three bill in scale-linked catastrophes,
and can one recorded-state resident action make the original TRAIN unaffordable?

**Population and bill.** All 200 exact D159 resident games decode cleanly. The B3.1
signature independently reproduces: 17/20 catastrophes have an opponent third-worker
TRAIN before the permanent crossover, spanning 12 exact identities and both seats, with
median 70-turn lead (range 13–125). All 17 bills require post-start supply after bounding
what can remain from starting stock following the earlier TRAIN. Across the bills,
minimum post-start contribution is 81 PLUM, 169 LEMON, 11 APPLE, and 68 IRON units.
IRON cannot be denied because mining does not deplete a shared stock.

**Provenance correction.** Broad source reachability is not causal bill control. The
replays contain 455 external pre-TRAIN acquisition batches, 407 definitely deposited
without carry ambiguity, and 371 fruit batches satisfying a loose BFS/ETA reachability
upper bound; every primary game has at least one. Fungible-bank bounds identify 73
individually mandatory batches, but 43 are non-deniable IRON. Of 30 mandatory fruit
batches, only one has a co-located resident, that unit cannot legally HARVEST, and none
has a prior one-command lethal-CHOP opportunity.

**Verdict: `NO_MATERIAL_DENIABLE_BILL`.** The strict gate credits only an
already-positioned, referee-order-valid HARVEST or lethal CHOP that removes enough
individually necessary fruit to block the original TRAIN. It finds 0/17 games, zero
identities, and zero seats. Support gates pass; every action-materiality gate fails.
The scaling event itself arrives after payment. Do not implement a timed denial scorer,
reuse Phase 21, open a causal panel, or treat hypothetical MOVE reachability as evidence.
H7′ action contention retains its distinct races/duplication scope.

Validation: analyzer compiles; self-test passes; 7 focused tests pass; a second full run
is byte-identical. No raw/processed data, simulator/referee, resident source, map/range,
game, candidate, submission, or Arena state changed.

Evidence:
`data/analysis/live-agent-6553250/h4-opponent-bill-deniability-census-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/h4-opponent-bill-deniability-census/`.

## H7′ — action contention exists, but is not a strong-opponent signature

**Question.** Do strong opponents distinctively exploit the cross-player interaction
mechanics that actually exist: simultaneous HARVEST/CHOP, last-item duplication,
combined-only kills, and exact target-removal/depletion races?

**Integrity.** The exact 200-game D159 resident panel decodes with zero unknown updates
and zero accepted-event transition mismatches. Frozen manifest/result/source hashes,
identity, file presence, 200 unique IDs, both comparison-cohort seats, and the
zero-outside-read gate all pass. The strong cohort is 36 rank-1–20 games / 18 identities;
the comparator is 82 rank-41+ games / 28 identities.

**Mechanics.** Contention is common: 180/200 primary-event games, 6,836 cross-player
same-tree co-location turns, 3,662 legal dual CHOP turns, 558 combined-only kills, 598
duplicated wood units, 3 dual-HARVEST turns with 2 duplicated fruits, and 41 exact
resident MOVE targets removed/depleted by the opponent. The reverse direction has 291
events. The direct duplicated-item ceiling is 2,394 score-equivalent total, 11.97/game,
but this is shared created material—not opponent-attributed, banked, or causal margin.

**Strong-cohort test.** Top-20 primary-event prevalence is 35/36 (97.22%) versus 75/82
(91.46%) for rank-41+, difference +5.7588 pp. The 10,000-replicate
opponent-identity-cluster interval is [−1.6353,+14.4928] pp. Both the frozen +10 pp gate
and positive-lower-bound gate fail. Per-turn frequency points the other way: 47.87 versus
78.93 events/1,000 turns; duplication ceiling is 11.22 versus 15.12/game.

**Verdict: `NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE`.** Real contention is
ubiquitous background behavior, not evidence of a learned strong-agent tactic. Close
H7′ without a causal panel or controller. Never reopen the mechanically impossible
body-blocking premise. No source, simulator/referee, raw/processed replay, map, game,
candidate, submission, or Arena state changed.

Validation: analyzer compiles; self-test passes; 7 focused tests pass; two full outputs
are byte-identical.

Evidence:
`data/analysis/live-agent-6553250/h7-action-contention-census-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/h7-action-contention-census/`.

## H3′ — numeric pressure precedes reduced crop contact, including before permanent loss

**Question.** Does resident opponent-crop first-contact hazard fall after an opponent
successfully trains worker three, or is the coverage gap only a symptom of games that
are already lost?

**Population and matching.** All 200 exact D159 resident games pass frozen
manifest/result/source identity, named-file, decode, transition, and outside-read gates.
There are 77 scaled games and 123 no-scale games. Seventy scaled games supply complete
50-turn pre/post windows and same-seat, sufficiently long nearest controls using only
eight frozen pregame/map fields. They cover 29 scaled-opponent identities and both
seats. All post-match absolute SMDs are ≤0.1806; 45 unique controls are reused at most
five times.

**Event ordering.** Scaled whole-game contact coverage is 814/2,301 = 35.38% versus
1,131/2,368 = 47.76% without scaling, difference −12.3859 pp with game-cluster CI
[−18.8284,−5.8550]. In matched 50-turn windows, scaled hazard falls
13.489→8.057/1,000 risk turns while control stays 16.940→16.722; the DiD hazard ratio
is 0.6061, CI [0.4100,0.8954]. Sixty-nine pairs over 28 identities retain the entire
20-turn post window before permanent negative crossover: scaled 12.108→6.100 versus
control 19.169→19.048, DiD 0.5103, CI [0.2928,0.8407].

**Verdict: `TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY`.** Every frozen support,
balance, and materiality gate passes. The decline begins after TRAIN even before
permanent loss, so “only already-lost late turns” is insufficient. This remains
observational—TRAIN may proxy broader opponent policy/state—and does not establish
intervention value. H3a is recorded but peer-review-gated: only one frozen three-arm
preflight comparing a workforce-conditioned change, the identical change always on,
and unchanged control can show conditioning is load-bearing. No conditional bonus,
source edit, candidate, submission, or Arena action is authorized.

Validation: analyzer compiles; self-test and 7 focused tests pass; two full 200-game
outputs are byte-identical. No raw/processed replay, simulator/referee, resident source,
map/range, game, candidate, submission, or Arena state changed.

Evidence:
`data/analysis/live-agent-6553250/h3-numeric-pressure-contact-causality-result-2026-07-31.md`;
compact JSON beside it and manifest under
`local_codex_1/h3-numeric-pressure-contact-causality/`.

## H11 — generic map-conditioned configuration decomposes into named gated children

**Question.** Does a generic “choose configuration from the map” task survive the
project's existing map-selection evidence?

**Audit.** Static map-to-workforce selection collapsed from discovery AUC 0.830 to
validation 0.479 in D63/D64. D91 selected only 5/16 maps and sits above a factory already
closed for feeding the opponent. Opponent families are policies, not map classes.
N6/E2/E4/E5 and the economy configuration menus are closed or immaterial and cannot be
rescued by adding a selector.

**Verdict: `DECOMPOSED_NO_GENERIC_TASK`.** Close H11 itself. Preserve only E7a's
prospective binary `typeToCut` selector question and S2's opening-book question under
their separate representation/value gates. F1, H3a, H10a, and N4 use behavior/current
decision state rather than pre-action map class. Reopening requires an exact non-closed
finite intervention, a material conditional terminal oracle, outcome-blind predecision
features, root-grouped validation, static baselines, and prospective value above the best
static configuration. No analyzer, fit, map range, source edit, candidate, submission,
or Arena action occurred.

Evidence:
`chatgpt_1/h11-map-conditioned-configuration-scope-audit-2026-07-31.md`.

## N4 — exact compatible-pair publication is correct but runtime-closed

**Question.** Can the exact resident's already-enumerated compatible two-worker pair
surface be published cheaply enough to justify a one-turn terminal-value Phase B?

**Pre-lock correctness.** The generated instrumented resident compiles against the sacred
snapshot; py_compile, self-test, and 12 focused tests pass. On exact seed 9,854,000 across
both seats and all eight standing families, 4,028 natural two-worker states have zero
frozen-command reconstruction failures. Single/20-thread output has 268,169 total lines
and is byte-identical after excluding only `latency_us`, normalized SHA `9177b5c9...`.

**Runtime.** Exhaustive candidate export plus one-tick boundary reconstruction is
210.408 ms p95 single-thread and 333.157 ms under 20-thread contention versus the frozen
5 ms close: 42.08×/66.63×. One root emits 268,168 data rows / 83,327,440 bytes; the full
matrix projects 34.3 million rows / 10.7 GB and more than eight parallel hours.

**Verdict: `RUNTIME_CLOSE`.** Stop at the preregistered pre-lock diagnostic rather than
run the infeasible full census. This scope does not claim full-population eligibility,
boundary frequency, family/seat breadth, or semantic distinctness, and does not prove
pair value absent. It closes the current exhaustive publisher, Phase B, N4-dependent
L2/L3, and E1 reuse. A compact publisher would require a new protocol, not pruning or
format retuning after observation. No alternative outcomes, source change, candidate,
submission, or Arena action occurred.

Evidence:
`chatgpt_1/n4-candidate-pair-value-result.md`;
machine result and implementation lock under
`data/analysis/live-agent-6553250/n4-candidate-pair-value-phase-a-*`.

## B3.10 — near-camp fruit count has too little direct-value headroom

**Premise.** B3.8's 1,144 near-camp observations are individual unharvested fruit units;
956 are PLUM/LEMON/APPLE, 71.8% lie outside D173b's chop-shadow scope, and 496 total /
425 bill-relevant units have an optimistic walking detour at most two turns. The detour
explicitly excludes HARVEST and DROP and credits at first reach, so it is stock accounting,
not a feasible action oracle.

**Upper bound.** Banking every one of the 496 units gives 2.4195 own score per all 205
resident games. Treating every unit as simultaneous opponent denial doubles the bound to
4.8390 margin/game before any action or scheduling cost.

**Robustness.** D173a/b already establish that fruit-for-wood displacement is not free:
compact_gold −2.0625/−1.3906, catastrophes +5/+3, and negative-margin mass
1.0959/1.0812. Both mechanism gates also fail. D174a prevents reuse of B3.8's synthetic
worker-bill rationale.

**Verdict: `CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`.** Being outside a prior
trigger's scope does not create terminal value. No near-camp target, distance tuning,
harvest-capability change, panel, candidate, or Arena action follows.

Evidence:
`data/analysis/live-agent-6553250/b3-10-near-camp-harvest-scope-audit-result-2026-07-31.md`
and compact JSON beside it.

## B3.7 bookkeeping reconciliation — completed crop-fate result is conversion-by-design

The live backlog incorrectly retained `IN FLIGHT` after the 2026-07-29 full-corpus census.
No rerun was needed.

Resident: 220 games / 2,433 crops; 98.97% self-chopped, 0.90% self-harvested, 0.12%
opponent-taken, zero alive; 96.8% of self-chopped crops never bore fruit. All 220 trained
resident workers have harvest power zero. True residual ripe service is only 41 episodes,
median two turns; real capacity waste is about 1.6%.

Top five: 200 games / 8,913 crops; 29.81% harvested, 42.98% self-chopped, 15.71%
opponent-chopped, 11.28% alive, with 2.5–3.0 live crops per capable worker versus the
resident's 0.08→0.40.

**Verdict: `ALREADY_COMPLETE_CONVERSION_BY_DESIGN`.** The top cohort has a mixed,
capacity-limited orchard; the resident deliberately converts crops to wood. Plant pacing
does not transfer, and theft remains secondary at 2.60 wood/resident game. No new rule,
capability edit, orchard redesign, panel, candidate, or Arena action follows.

Evidence:
`data/analysis/live-agent-6553250/b3-7-crop-fate-state-reconciliation-result-2026-07-31.md`
and compact JSON beside it.

## H3a — exact archived treatment is reproducible; value protocol remains separate

The frozen fallback SHA `a8eb3b2b...` transforms byte-exactly into the Phase-21 treatment
SHA `083107f5...`; reversing the seven edits restores fallback, and the archived full-parent
generator independently reproduces treatment. The complete delta is +1,811 bytes and is
exhaustively provenance/lifecycle plus existing-tree scoring. The operation is exactly
`candidate.score += candidate.score` for tracked existing tree targets at ETA ≤6.

Both exact artifacts compile. Fourteen focused tests pass, including direct repository-root
CLI and two full compiled-result equality checks. No-compile/compiled result hashes are
`5f392ab3...` / `a8679546...`. The sidecar file SHA is `9811fb4f...`; it records treatment
digest `083107f5...`.

**Verdict: `TREATMENT_REPRODUCIBLE`.** This satisfies source reconstruction only. A future
protocol must separately compare pressure-conditioned treatment, identical treatment
always on, and unchanged control. No runner, range, panel, candidate, or Arena action was
created.

Peer implementation was integrated and host-corrected for direct import, explicit Rust
crate names, and deterministic compile metadata. After peer head `8ae01f5` exceeded its
lease on a compact-documentation blocker, the integrator published the canonical paths
without rewriting peer files.

Evidence:
`data/analysis/live-agent-6553250/h3a-pressure-treatment-reconstruction-result-2026-07-31.json`
and `chatgpt_1/h3a-pressure-treatment-reconstruction-result.md`.

## B3.11 — Dridriun relative fruit-control postmortem narrows a precheck

The owner identified three related errors in game `896352129`, resident 252 versus
Dridriun 276: late removal of the enemy-door orchard, creating apples under opponent
harvest capacity, and chopping a controlled ripe own-door apple without harvesting.
Exact raw SHA `eee9f348...` and trajectory SHA `b4f42a5f...` decode 300/300 turns with
zero unknown updates.

Dridriun planted nine APPLE generations at opponent door `(9,2)`. They received 83
observed opponent HARVEST commands. The first generation was planted at turn 3, first
harvested at 14, first chopped by the resident only at 63, and removed at 80: 25 harvests
before resident contact, 33 total. Later generations were usually contacted sooner, but
ten chop turns still allowed continuing harvest; the final generation was harvested 18
times and survived game end.

The resident planted nine door apples of its own. Four ripened. It issued zero HARVEST
and 22 CHOP commands while they held fruit, destroying final stock 3+3+1+1 = 8. The
strongest two cycles were starter-controlled at `(8,4)`: the unit had harvest power one,
stood on fruit up to stock three, and still chopped. The opponent harvest-capable troll
was ETA 2/1 at planting and later co-located with both ripe trees.

Correction: Dridriun actually harvested **zero** resident-created apples; it contested
them by reach/chop. The production concern is therefore feasible capture, not observed
capture. The 83 opponent harvests and eight destroyed own fruit are observed accounting,
not causal recoverable margin.

**Verdict: `NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`.** Phase 21 covers generic
enemy-crop urgency and lost −7.77 Arena rating; D173 covers broad harvest-before-chop and
fails family/tail gates; B3.7 conversion-by-design and B3.10's 4.84/game generic
direct-stock closure remain binding. What is untested is only their joint strict
relative-control predicate. A read-only existing-corpus frequency/precheck may be
proposed; no code, threshold, capability, runner, panel, candidate, or Arena action.

Evidence:
`data/analysis/live-agent-6553250/dridriun-fruit-control-postmortem-result-2026-07-31.json`
and the compact human report beside it.

### Peer-review disposition

N6 is independently accepted as `CLOSED_AT_DEVELOPMENT`. N5's empirical arithmetic is
supported but its frozen semantic-test coverage and ETA birth-state convention require
correction before canonical closure. B3.11's narrow interpretation remains plausible,
but its compact must separate HARVEST commands from confirmed fruit-unit flow and publish
decisive state/capability plus raw-BFS/ETA rows before narrow re-review. Broad no-action
boundaries remain binding while those corrections are pending.

### N5 protocol correction

N5 now uses literal post-birth `states[birth_turn]` access and has twelve focused tests
covering the previously missing semantic surface. The exact frozen 382-occurrence manifest
was reused after the live collector advanced; every referenced input hash remains exact.
Resident ETA-0 changes 5→0 and reachable-within-remaining changes 368→366, but both removed
targets have zero opponent yield. The primary 11.9917 mean, [8.7273,15.7603] CI, and
`NO_MATERIAL_CONTEST_OPPORTUNITY` verdict are unchanged. Narrow corrected re-review is
pending; no simulation or Arena successor follows.

## B3.12 — zasmu lemon-denial economics narrow a feasibility precheck

The owner observed opening movement churn and zasmu harvesting and replanting lemons in
exact resident game `896352750`, a 206–184 win. Raw SHA `c7209f23...` and trajectory SHA
`a62b5b48...` reconstruct 217/217 turns with zero unknown updates.

The visual oscillation is real but short. Starter unit 1 makes five exact A-B-A position
episodes, three through turn 100; the longest has four states and none reaches the frozen
B3.2/D176a ≥10-state class. All opening MOVEs land and no teammate is adjacent in those
episode states. Their counterfactual task value is not identified, and D176a already
closed a working sustained-oscillation fix at only +0.045 overall margin.

The lemon economics are stronger. Six initial lemon trees start at 40 health. Zasmu
plants a seventh on turn 6. Immediately before the resident's first lemon chop, all seven
are mature: 84 health and seven standing fruit. With resident chop powers 1+3, even an
impossible no-travel full clear needs 21 turns.

The resident spends 28 lemon CHOP commands from first contact on turn 26 through the fifth
initial removal on 67. It deals 60 damage, destroys 13 fruit present at removal, and
collects nine wood. One initial zasmu-side lemon and the planted orchard remain, holding
24 health and six fruit at turn 67. The resident never reaches species extinction; zasmu
self-converts the surviving supply only by turn 120.

Zasmu harvests 25 lemons: 19 from the protected turn-6 plant at `(7,8)` (BFS 3 from its
door, 17 from ours) and six from the remaining natural tree. On turn 97, unit 2 spends
one of two lemons just harvested at `(3,9)` to plant on its own door—the owner's observed
harvest-to-replant transition.

The bill provenance is exact. After turn-2 training, zasmu has one banked lemon. Ten
harvests from the planted tree raise the bank to eleven and exactly pay worker 3 on turn
62. After that, 15 more harvests minus the replant seed leave 14 banked; worker 4 costs
12 on turn 106 and two remain. The natural-tree sweep therefore does not deny either
later lemon bill.

**Verdict: `NARROWED_TO_FEASIBILITY_PRECHECK`.** This is not permission to disable lemon
chopping: the same five removals yielded nine resident wood, and the resident won.
Only a read-only existing-corpus audit may separate base wood/conversion value from the
denial bonus and compare opponent bank/carry, protected regeneration, travel/chop clear
time, and next-bill timing. Blanket focus inversion (E7), denial-weight retuning (N6),
reachability-as-causality (H4), and oscillation changes (D176a) remain closed. No source,
runner, panel, candidate, submission, TestSession, or Arena action follows.

Evidence:
`data/analysis/live-agent-6553250/zasmu-lemon-denial-oscillation-postmortem-result-2026-07-31.json`
and the compact human report beside it.

### Owner-directed B3.12 Arena override

After the read-only verdict, the owner explicitly directed a concrete threshold: for
initial focused denial, a tree at terrain BFS distance >3 from the nearest own door must
not trigger a wood return. The implementation leaves distance ≤3 and every non-denial
return unchanged; at >3 it removes return/wood value from the target and permits a
full-capacity troll to keep CHOPping, so lethal overflow is discarded by the referee.

The fail-closed generator reconstructs exact resident SHA `a8eb3b2b…`; candidate
`candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs` is 63,033 bytes, SHA
`307a0755…`. A compiled boundary fixture emits bank-directed MOVE at distance 3 and CHOP
at 4; 2/2 focused tests and eight unsealed local smoke cells pass. Sacred source remains
`fff6669b…`.

Exact artifact commit `fcc6e62` was pushed before the platform write.
`TestSession/submit` returned submission `41070584`; the new agent is `6585578`, with ten
initial battles queued. This was not a qualified scientific promotion: it is the one
owner-directed live experiment. No second submission is in flight.
