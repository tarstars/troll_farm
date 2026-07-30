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
