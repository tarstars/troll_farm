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
