# Legend top-3 experiment cycle — volume 2 (opened 2026-07-23)

Objective, persistent cycle, and completion rule: see volume 1
(`legend-top3-experiment-cycle-2026-07-18.md`, frozen at D166). Live state:
`docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` — check before proposing.

Per-experiment obligations: one entry here (same style as volume 1); a CONSTRAINTS bullet
for anything closed; a STATE.md §4 update. The first session ending with this file over
100 KB freezes it with one appended note and opens volume 3.

<!-- entries below -->

## 2026-07-27: authorized passive refresh + operational cleanup (no experiments)

Passive read (read-only, D61p collector): resident `6561795` rank 43/110 @ 21.97 with 203
listed battles. The score is bit-identical to the 2026-07-23 read and the leaderboard's own
updateTime shows no recomputation since 2026-07-23T02:45:38Z — fresh-agent scores freeze
between rare ladder recomputes, so passive maturity recovery is materially slower than the
fresh-vs-mature analysis assumed. League 107→110. Bar: delineate 31.00 /
norxondor_gorgonax 29.52 / MSz 28.22. 198 new public replays collected (195 cached
skipped; 220/220 requests clean), QA 393/393 parsed with zero failures; snapshot
`data/raw/snapshots/20260727T130712Z-d61p/` (gitignored raw). No arena write.

## 2026-07-27: B3.1 catastrophe-tail endgame coverage audit (read-only; no candidate)

On the fresh snapshot's 192 open resident games (11 sealed-confirmation games excluded per
the D61p holdout protocol), the D159 signature replicates independently: 19/192 = 9.9%
catastrophes (margin ≤ −100) carrying 57.9% of negative-margin mass across 14 opponents;
ahead-at-t100 reversals match D159a's own `catastrophic_reversals` computation 16/16. The
resident's score-aware endgame switch (`endgame = turn>250 || (plants≤4 &&
my_score<opp_score)`) fired in 10/19 catastrophes but always at or after the score
crossover (median +46.5 turns late, minimum gap 0) — an AND-of-behind design structurally
cannot fire earlier, and the four worst catastrophes never triggered it before the trivial
turn-250 clock (never-fired games hold 57.6% of catastrophic mass). Verdict: **no coverage
bug; switch retuning is closed.** The bounded surviving signal: opponent workforce scaling
past the resident's two-worker ceiling precedes the crossover by 42–125 turns in 84% of
catastrophes (79% jointly with ahead-at-t100), covering 83% of catastrophic mass — an
observable trigger the resident never conditions on. This independently confirms D159's
top-ranked attack angle and feeds the B2.1 option-interface design (activation
conditioning), not a retuned switch. Report:
`scratchpad/b31-endgame-audit-report.md` (session scratch; numbers preserved here).

## 2026-07-27: D167a successor-job acquisition-path recovery — BANK_SEED frozen-eligible

D167a extends D166 byte-for-byte (new Rust runner reproduces D166's audit logic; D161/D166
reference inputs reverified by hash) and classifies the acquisition path behind every
successor PLANT return. Local: all 135/135 natural returns are **BANK_SEED** (PICK a
deposited shack seed → walk → PLANT); 96/135 returning workers have harvest power 0, making
BANK_SEED mechanically forced for 71% and chosen anyway by the rest. Field: top-5 PLANT
returns split BANK_SEED 15/21 = 71.4% (4/5 agents — all but MSz — both seats),
OPPONENT_DERIVED 5/21, FIELD_FRUIT 1/21; ranks 6–20 descriptively 25/28 BANK_SEED. Frozen
gates: **BANK_SEED passes both** (field ≥60% + ≥4/5 agents + both seats; local ≥90/135);
every other class fails both. OPPONENT_DERIVED is closed as a distinct successor class
(23.8% field, 0/135 local). Verdict: **BANK_SEED is FROZEN-ELIGIBLE** — the hand-written
successor branch stays alive; a D168 causal option test (exact resident KEEP, activation
breadth, value, own-score protection, family/seat breadth, tail safety) is authorized to be
*designed*, not assumed.

Methodological discovery during integrity verification: 22/49 field cycles carry the
eventually-planted seed *through* suppression (acquired before suppressing; e.g. gaha game
896636060 harvests an opponent PLUM, chops, then plants it) versus **0/1,024** for the
resident — the extractor was repaired to walk the full acquisition ledger (completeness
fix; gates untouched). Top agents pre-stage seeds before suppressing; the resident never
does. D168's design must weigh a pre-carry variant, and note the shack pool is fungible
(BANK_SEED does not identify which teammate produced the seed).

Determinism: all three products byte-identical 1-vs-20 workers (SHAs in the result doc).
Rust 10/10, D164–D166 Python suite unaffected 10/10. Bulk rows on the external
`artifacts/experiments/d167a-...` root per storage policy. No candidate, platform, YT-write,
sealed-map, resident, or Arena action. Full record:
`d167a-successor-acquisition-path-{protocol,lock,result}-2026-07-27.*`.

## 2026-07-27: D168a bounded BANK_SEED successor option — hand-written successor controllers CLOSE

D168a implemented the frozen-eligible BANK_SEED return as two bounded options over exact
resident KEEP (ARM_A post-suppression return, horizon 24; ARM_B pre-carry detour, horizon
32) and ran all three policies on the 1,024 consumed D148/D161 tasks. Every integrity gate
passed: CONTROL reproduces D161 and D166/D167's entry facts exactly; 1,720 inactive
(task,arm) pairs byte-exact; command/vocabulary purity zero violations; jobs1/jobs20
byte-identical; frozen D162/D166/D167 modules untouched; 13/13 Rust tests. Mechanism
passed for both arms: 164/1,024 activations (16.0%), both seats, 7/8 families (absent only
vs script_boss). Notably, worker carry is empty at 100% of entries, so the field's
pre-carry precondition never differentiates ARM_B from ARM_A on resident trajectories —
the resident's economy never stages a seed before suppressing.

Value failed decisively for both arms under the preregistered gates: ARM_A **−6.73**
paired margin, CI [−8.40, −4.08], own −3.61, worst family −17.11 (gold_adaptive),
catastrophes 24 vs 22 (1/5 gates pass); ARM_B **−8.21** [−10.53, −5.71], own −3.95, worst
family −15.56 (2/5 pass). Verdict per the frozen kill rule: **hand-written successor
controllers close.** The motif (D164) and its path regularity (D167) stand, but forcing
the return is worse than the resident's natural scheduling — the value lives in WHEN, not
WHAT. BANK_SEED survives only as an option inside the rollout-valued B2.1 interface. No
tuning, no rescue, no candidate, no platform/Arena/YT action. Full record:
`d168a-bank-seed-successor-option-{protocol,lock,result}-2026-07-27.*`; bulk rows on the
external `artifacts/experiments/d168a-...` root.

## 2026-07-27: D169a resident-native option-interface envelope — PASS, Tier-2 gate cleared

D169a ran the unified crop-safe option envelope (OPT_RETURN from D168's ARM_A + the three
D163 resource components at fixed and B3.1-TRIG-armed starts, 13 arms + control, 14,336
episodes) on the full 1,024-task consumed panel, reusing the D161/D162/D163/D167/D168
frozen modules without modification. Coverage 100% (1,024/1,024 armable). All 17
integrity gates passed: CONTROL exactly reproduces D161; every inactive (task,arm) pair
byte-exact; zero purity/vocabulary/provenance violations; 1-thread vs 20-thread
byte-identical (SHA `a51a64119a14...`); all frozen modules hash-verified unmodified;
Rust suite 16/16. Every individual arm is negative alone (−0.06 to −12.07 mean) — value
is entirely a selection effect.

**Envelope: mean +10.671, clustered 95% CI [+9.420, +11.922], 65.0% of tasks improved, 0
regressions, worst family +5.14 (all 8 positive).** Tails improved vs control: 14
catastrophes vs 22, negative-margin mass 3,622 vs 5,001. **All six frozen PASS conditions
hold** (mean ≥ +10.0; CI floor ≥ +5.0; ≥30% improved; no negative family; catastrophes
and negative mass ≤ control) — no BORDERLINE extension (D169b) needed. Diagnostic-only
subset (TRIG+RETURN, the deployability-realistic slice): +1.80 [1.23, 2.37] — an order of
magnitude below the full hindsight ceiling, confirming the gap is genuinely a *selection*
problem, not just an activation-breadth one.

**Verdict: PASS. Opens D170 authoring (family-robust closed-loop objective over this
vocabulary, per D108/D109's unanswered question) — reserved for Fable-tier design per
`docs/RUNBOOK.md`. Session STOPS here on Tier-2 work.** No candidate, tuning, fresh maps,
or platform/Arena/YT action. Full record:
`d169a-resident-option-interface-envelope-{protocol,lock,result}-2026-07-27.*`; bulk rows
on external `artifacts/experiments/d169a-resident-option-envelope/`.

## 2026-07-28: D170a CLOSED-AT-PHASE-1 (implementation invalidation) → D170b repair frozen

D170a's Phase 1 (8 fits, 4 objectives × 2 seeds) completed before the USB-pause
interruption; the resume validation then found all 8 fits deterministically failing their
preregistered Stage-A mechanics gate — and root-caused it to a structural off-by-one in
the NEW D170a composition code: the three resource `_trig` arms compared a stored trigger
turn against an already-advanced turn counter, making them unreachable on any trajectory
(offered 0/2,880 decision points while the underlying opponent-≥3-workers event fired in
15.7%; D169's frozen reference shows the same arms winning 25+13 envelope tasks). Reruns
of all 8 fits reproduced byte-identical checkpoints and identical zero counts — fully
deterministic, not interruption damage. The frozen inherited vocabulary block is
hash-verified untouched; `OPT_RETURN` avoided the bug via its sticky-flag pattern. No
value field was ever computed (Stage-A stops precede training summaries), so no outcome
contamination exists. The resume agent correctly refused to patch locked code, recorded
CLOSED-AT-PHASE-1 per the decision tree, built and smoke-tested the Phase 2/3 analyzer,
and escalated. Full record: `d170a-family-robust-option-policy-result-2026-07-28.{md,json}`.

**Fable adjudication: implementation invalidation, not scientific closure** (house
precedent D112→D113, D133b, D75b, D158). The D170 question remains open. **D170b frozen**
(`d170b-family-robust-option-policy-repair-protocol-2026-07-28.md`): mechanics-only
repair (sticky-flag arming for the trig arms), a pre-training all-KEEP activation
verification with frozen floors, and one definitional correction made pre-outcome (the
2% exploration floor computed conditional on offered decisions, unconditional share
reported alongside). Everything else — objectives, seeds, budgets, ranges, gates, phases
— inherited from D170a unchanged. Engineering constraint recorded: post-step event
arming must use the sticky-flag pattern, never turn-equality against a live counter.

## 2026-07-28: D172a CLOSED-AT-SELECTION — the Tier-2 learning route is closed with a definitive mechanism

Phase 0 byte-exact (256/256 vs D169 bulk; two real feature-timing bugs caught and fixed
pre-corpus — the features were correct this run). Phase 1: 79,997 exact zero-noise labels
over 27,392 decision states (512 fresh maps, ~24 min at 20 threads). Phase 2: **signal
floor passed 5× over** — 40.4% of states carry a ≥+2 option (floor 8%), both seats, 8/8
families. Phase 3: **0/4 admitted** — pooled LOBO means +0.139/+0.229 (linear) and
+0.178/+0.262 (MLP) against the +1.5 gate, activation 4–10%, worst blocks slightly
negative; crop/catastrophe safety clean. Phase 4 correctly never run; veto panel and
sealed block 9,862,000–063 untouched.

**Adjudication (Fable): this is the definitive closure.** Every alternative explanation
is excluded by construction: not label noise (exact counterfactuals), not capacity
(linear ≈ MLP), not covariate shift (budget-1, on-distribution states), not absent signal
(40.4% of states ≥+2). The positive contexts are **not identifiable from the 64-field +
affordance observables** — D100b's trajectory-specificity warning, now proven at the
mechanistic level with the cleanest possible instrument. The Tier-2 learning route is
closed per the protocol's own decision tree ("any CLOSED = final closure"). For the
record only: the one untried observation class is spatial planes at decision states on
the official substrate (the D29 spatial option-critic died of the pre-D33 map-domain
artifact and was never retried); reopening on that basis would be a new owner decision
against this entry's evidence. The owner's Tier-2 reopening is hereby consumed with a
clean answer. Full record: `d172a-dense-counterfactual-option-policy-*` (lock, phase
results, corpus manifest, result docs); new machinery committed
(`d172a_dense_counterfactual_corpus.rs`, train/analyze scripts).

## 2026-07-29: H3 CLOSED (C) — the quartet's "survival edge" does not survive controls; B4.4 corrected on four counts

**Verdict (C) mixed/underdetermined; no transferable mechanism confirmed.** Cohort
(fresh snapshot, rank/games/roster/crop-level own-reap): Escdemon 11/180/2.00/2.4%;
therealbeef 12/236/2.00/0.0%; yamo 15/140/2.00/0.0%; mehdi_ayari 32/144/1.99/0.2%;
resident 45/219/2.00/0.9%. All four still satisfy B4.4's STRONG rule.

**The headline gap largely dissolves under control.** Restricting to own-roster = 2, the
raw pooled 2v3 comparison is resident **−34.2 (n=67)** vs quartet **−14.6 (n=200)** (win
34% vs 30%) — a real difference. But under the tightest control, **identical opponent
identity** (19 shared 3-worker bots), it vanishes: resident **−16.3 (n=47)** vs quartet
**−17.1 (n=63)**. An OLS adjustment for opponent arenaScore + duration points the other
way (+56.4 quartet advantage, CI [+14, +274], n=48). **The two rigorous controls disagree
and the audit correctly declined to adjudicate.** At **2v4+ there is no edge at all**:
resident −71.5 (n=21) vs quartet **−74.4 (n=56), numerically worse**, with the resident
winning more often (9.5% vs 3.6%).

**Four corrections to B4.4, all adopted.** (1) Its −1.8-vs-−37.1 headline was not
own-roster-controlled; the controlled figures are above, and the vs4+ claim inverts.
(2) **"No-loop" is a misnomer** — all five agents, resident included, run a 92–99%
self-plant → self-**chop-for-wood** cycle. Everyone has a loop; it is a wood loop, and it
is not a differentiator. (3) The own-reap rates are tighter than reported: 0–2.4%
crop-level for the quartet (B4.4's "0–14.5%" was a looser game-level indicator).
(4) **The resident harvests 2–9× MORE fruit than every quartet member** (12.6 vs 2.2–6.4
pts/game), reversing B4.4's pooled "resident is the most wood-concentrated" claim — we are
the *least* pure wood economy of the five. Additionally, wood/chop efficiency, tree size
at felling, unit specs, and banking latency are **statistically indistinguishable across
all five**, refuting B4.4's own hedge that chop efficiency explained the gap (a class
B4.6 had already closed on other grounds).

**Residual signal, recorded as a gated lead, not a candidate.** Opponent-crop contact
coverage degrades **41.3% → 35.3%** for the resident under numeric pressure (−14.5%
relative) while every quartet member holds flat or improves, and a duration-tercile split
places the entire margin gap in full-300-turn games. The audit's proposed test — bias
chop-target selection toward opponent-origin crops when roster-behind and past ~turn 150 —
is **Phase-21-adjacent** (exact 1:1 dual-value opponent-crop scoring: all pre-arena gates
passed, −7.77 rating live) and rests on a comparison whose headline dissolved under the
tightest control. Adjudication: it is gated by the same standard the H4 review imposed —
before any implementation, (i) establish causality (is coverage degradation a cause or a
symptom of already losing? the 300-turn concentration is consistent with either), and
(ii) demonstrate that the *conditioning* is load-bearing via an always-on control arm.
Folded into the H4/H7-rewritten preflight bucket, all three being "opponent interaction
under pressure". Script `cgauto/no_loop_quartet_audit.py`; report in session scratch
`h3-no-loop-quartet-report.md`.

**Process note (integrator error, recorded).** A `git add -A` during the H8 commit swept
this audit's in-progress script into an unrelated commit while its author was still
working. The protocol forbids staging another worker's files; with concurrent agents,
commits must name explicit paths. No content was harmed (verified byte-identical), but the
provenance is now wrong in the history and the rule is restated in the protocol.

## 2026-07-29: H8 CLOSED — worker-2 timing is already optimal; the premise was wrong and a shared method bug is fixed

**Verdict (B) forced — no execution-class candidate; H8 closes.** The resident trains its
second worker on **the exact turn its bill first becomes legal in 219 of 220 games
(99.5%, gap = 0)**. Median actual TRAIN turn 7 (mean 7.42) against median
first-affordable-and-legal turn 6 (mean 7.29). The single exception (game 896350706, gap
29) lands precisely on the documented `hard_train_turn = 35` deadline downgrade — the
policy held out for a better spec and was forced to settle, which is deliberate design,
not a defect. Explanation split: execution defect **0/220**, forced/floor **219/220**,
deliberate hold-out **1/220**. No PLANT is ever issued before worker 2 in any game, so
there is no competing "opening economy" claim on that currency either.

**The real bill, established rather than assumed** (the D174a trap avoided): there is no
fixed worker-2 spec. `choose_second_troll` — live path `SecureOrchardBot::new()` →
`YamoBot::tuned_carry_regeneration_transit_idle_harvest()` → `TUNED_CARRY` —
ETA-optimizes (ms, cc, chop) ∈ {1,2,3}³ per map at turn 1. Read from each game's own
revealed TRAIN command text: 26 distinct talent vectors, most common `2/2/0/2` (13.6%),
pooled median cost PLUM 5 / LEMON 5 / APPLE 1 / IRON 5.

**The H8 premise itself was false.** "Top cohort trains at median turn 2, we at 8" traces
to a stale 2026-07-16 census. Re-verified field-wide: resident median 7–8, field median
8, and **B4.4's own same-architecture cohorts are SLOWER than us — STRONG median 14,
PEER/WEAK median 20**. The literal top-5-by-rank do train at median 1, but they run a
structurally different economy (98.7% harvest-capable specialist/hybrid/generalist roles
vs the resident's 79% wood specialists), so that comparison never licensed an inference
about our scheduler.

**Independent pricing of scaling *timing*** (field natural experiment, early vs late per
ordinal, n=16,872): worker-2 timing is worth **+1.31 margin, CI [−2.80, +5.42] — not
significant**, whereas worker-3 timing is **+42.6** and worker-4 **+60.1**, both
significant. Consistent in direction with B4.3's existence-effect pricing (2→3 = +22.7,
3→4 = +38.9) by a different method: value lives in workers 3–4, not 2.

**Method bug found and fixed — it affects prior audits' convention.** The referee resolves
MOVE before TRAIN within a turn (`sim/engine.py:step`), so the pre-turn shack-occupancy
check used by D160/B3.8/B3.9 wrongly flags a same-turn `TRAIN;MOVE` vacate as blocked.
Corrected here by testing post-move position; cross-checked with two independent decoders,
0 mismatches over 219 games. This does **not** overturn those audits' conclusions —
worker-3 is blocked by `can_train`'s unconditional `if n >= 2 { return false }` (D174a
Phase 0, 0/64 with a fully credited bank) and by the real-bill correction, both of which
dominate any occupancy accounting — but every future affordability computation must use
the post-move convention. Script: `cgauto/worker2_timing_audit.py`; report in session
scratch `h8-worker2-timing-report.md`.

## 2026-07-29: first multi-agent review cycle — H7 falsified, H1 demoted, portfolio re-taxonomized

The icfpc2026 coordination protocol was ported (`coordination/multi-agent-protocol.md`;
`claude_1` = integrator + arena controller) and immediately exercised by a second agent,
`chatgpt_1`. Its first contribution was wrong in an instructive way: it identified
`v1.59.0-ringfix3` as the champion and analysed that bot's lexicographic band system in
detail — accurate archaeology of the **retired Gold-era lineage**, which has not played a
ladder game since 07-13. Two of its three cited evidences failed on the session branch
(`api_submit.py:12` defaults to the slim Yamo/Orchard source; `docs/STATE.md` names agent
6561795). Root causes, recorded because they are this repository's three standard traps:
in-tree relics were trusted over `docs/STATE.md`; no liveness check preceded a deep dive;
and `docs/CONSTRAINTS.md` was not consulted before proposing a direction (fruit
re-weighting — the most-closed class here: Phase 21 −7.77 arena, D173a/b, D175a −26.44,
B4.6, B3.7). Corrected by policy message with a mechanical 60-second pre-task checklist.

The same agent then reviewed `docs/rank-hypotheses-2026-07-29.md` competently, and the
review is integrated (`docs/reviews/2026-07-29-chatgpt_1-rank-hypotheses-critique.md`).
Three findings accepted, one of them decisive: **H7's premise is mechanically impossible**
— no cross-player blocking exists (`docs/mechanics.md:42-45`, independently verified by
claude_1 against `sim/engine.py:134-150`), so body-blocking/door-camping/path-denial
cannot be built; rewritten as an action-contention audit. **H1's four-lever bundle is
rejected** as a first experiment (destroys attribution; re-creates the graft pattern the
terminal synthesis rejects) and reduced to a read-only joint upper bound feeding H2.
**H11 misclassified** an opponent family (`compact_gold`) as map evidence and is
near-closed given D63 (AUC 0.830 → 0.479) and D91's missing cluster support. H9/H12
reclassified as operations. One reviewer error corrected in the integrated message: the
H1 panel was misread as a power reduction (256 maps × 8 families × 2 seats = 4,096 paired
episodes, equal to D175a's). All three findings are now CONSTRAINTS bullets so they cannot
be re-proposed.

Resulting portfolio taxonomy (now the head of `docs/BACKLOG.md`): **P0 audit-ready** H5,
H3, H8; **P1 preflight-gated** H1-upper-bound, H4, H6, H7-rewritten; **P2 owner
programme** H2 Architecture-2 (primary, with five milestone gates) and H10; **P3**
H11; **operations** H9, H12. Process note: the cycle worked as designed — claim →
handoff → independent verification → integration with corrections flowing both
directions — and it caught an integrator error that solo auditing had missed.

## 2026-07-29: B3.7 crop-fate census — conversion-by-design, and the pacing hypothesis answered

The owner-originated census of what actually happens to every crop, completed on the full
corpus. **Resident (220 games, 2,433 crops): chopped by us 98.97%, harvested by us 0.90%
(matching D101's 0.94%), taken by the opponent 0.12%, alive at end 0%** — and **96.8% of
our self-chopped crops never bore fruit at all** before we converted them. **Top-5 (200
games, 8,913 crops): harvested by owner 29.81%, self-chopped 42.98%, chopped by opponent
15.71%, alive at end 11.28%.**

Servicing ratio (live crops ÷ harvest-capable workers): **resident ≈0 throughout**
(0.08→0.40 across turns 25–300) versus **top-5 ≈2.5–3.0**; empirically **100% of 220
resident trained workers have `harvest_power = 0`** — only the starter, effectively glued
to one orchard-mother tree, ever harvests — against just 9.5% for the top cohort. Expiry
analysis: when our ripe fruit does go unserviced a capable worker is in reach 87.4% of the
time (73.2% excluding the orchard-mother reserve), but there are only **41 true residual
episodes, median 2 turns**; the top-5 have 3,922 such episodes at median 19 turns with
1,010 crops still ripening at game end (we have 1, in 220 games).

**Verdict: conversion-by-design, decisively, for the resident.** We are not racing our own
orchard and we are not capacity-limited (true capacity waste ≈1.6% of ripe episodes);
theft is real but secondary (18.2% opponent wood-share on contested self-chopped trees,
2.60 wood/game, matching CONSTRAINTS' 2.32). We have **architecturally opted out** of
farming: trees are wood, and only one designated tree per game is ever treated otherwise.
For the top-5 the picture is genuinely mixed — conversion 43%, capacity-limitation 39.3%
despite near-universal reachability, theft 15.7% — with none dominant. This settles the
owner's plant-pacing hypothesis precisely: **it fits the top cohort's ceiling and does not
apply to us at all**, and it is the fate-level confirmation of what D175a proved causally.

## 2026-07-29: B4.6 CLOSED — suppression efficiency is real but its fix class already failed twice

Decomposition of the 0.31-vs-0.43 wood/chop gap. **Ruled out entirely:** capacity-blocked
chops (0% — `chop_candidates` structurally refuses to chop at zero free capacity), target
contention (0 occurrences — `select()`'s uniqueness constraint), abandoned chops (0.34%),
and travel overhead — the resident's move:chop ratio is actually **better** than the strong
cohort's (1.52 vs 1.96). **What remains:** tree size at felling (we fell 37.8% size-1 trees
vs 22.9%) and kind mix (more APPLE, less BANANA at near-identical map availability); an
Oaxaca decomposition splits it 51% rate effect / 33% mix effect. Notably the single largest
loss channel — the capacity ceiling against tree size, ~35–37 wood/game — is **identical in
absolute terms across all three cohorts**, so it is a shared architectural tax rather than
our gap; it traces to our `cc=1` unit performing 38.5% of fells versus a sampled peer's
13.0%. Contact rate is **pure selection, not reachability**: >99% of opponent crops are
reachable within 20 turns for every cohort (median ETA 3–4 turns, the peers' if anything
faster), and restricting to reachable targets barely moves the gap (41.5% vs 46.0%).

**Root cause pinned:** `MoisanBot::chop_candidates` (`:1050-1118`, via
`SecureOrchardBot::new()` → `YamoBot::main_candidates` → `yamo_chop_candidates`) scores
`1000·wood/turns` with `wood = final_size.min(free_capacity)` — pure throughput, **blind to
crop origin by design**. Confirmed by reconstructing 445/515 = 86.4% of real decisions with
a Python port of the scorer. Two dead-code families sit alongside it: `opponent_eta_penalty`
(traced to a literal 0, matching B3.6) and a newly documented
`opponent_crop_bonus`/`opponent_crop_dual_value` pair — the Phase-21 machinery left inert
after its arena rejection.

**Why no cycle is warranted despite a ≈54–73 point/game addressable-looking residual:**
this exact intervention class has already been built and tested against the byte-identical
resident binary (SHA-verified) **twice** — the opponent-crop scoring bonus lost **−7.77
rating in the real arena** (Phase 21), and harvest-before-chop lost −2.325 margin on a
960-cell grid (−7.108 against adaptive Gold). A third, closely analogous experiment
(transplanting the resident's chop layer onto another bot) produced positive mean value and
then failed catastrophically at **−61.7** against an adaptive opponent. The documented
reason is the same each time: **isolated local-metric improvements break the resident's
coordinated schedule against adaptive opponents.** B4.6 closes, and with it the
execution-class prospecting track.

## 2026-07-29: ★★★ TERMINAL SYNTHESIS — the improvement space for this architecture is closed

Every route is now closed by measurement, each with its own frozen protocol and verdict:

| Route | Closed by | Decisive number |
|---|---|---|
| Learned option selection | D172a | 40.4% of states carry ≥+2 value; held policy +0.14–0.26 vs +1.5 gate — unlearnable from observables |
| On-policy closed-loop | D170b | All four objectives converge to always-KEEP; 0/8 admitted |
| Production / farming | D89, D175a | Early planting works (turn 199→13) and costs −26.44; Δown −5.41 vs Δopponent +21.09 |
| Scaling | D174a | `can_train` hard-caps at 2; real bill unaffordable in 100% of games (fruit, not iron, binds) |
| Mining | D174a | Iron ×10.6 delivered, value −10.76, all 8 families negative |
| Harvest capability | D173a/b | 99.9% cure among capable units; 99.93% of the vein needs `harvest_power:0` lifted; family/tail costs both times |
| Oscillation / execution waste | D171a, B3.6, baseline | We waste LESS than the top cohorts on all six signatures, even per-worker |
| Suppression efficiency | B4.6 | Mechanism real; the fix class already failed twice on this binary (−7.77 arena, −2.325 grid) |

The unifying finding: **this architecture's shape is its advantage, and local improvements
to any one component break the coordination that makes it work.** At equal roster we are at
parity with strong two-worker peers (58.2% vs 58.3%); our deficit is entirely
scale-asymmetry survival, and every attempt to acquire scale costs more than it returns
because we cannot harvest what we produce. Further gains require a different bot, not a
better-tuned one — a project-scale decision for the owner, not a next experiment.

## 2026-07-29: ★★★ D175a CLOSED — early planting is severely harmful; the production leak is structural

Execution was exemplary: trigger fidelity **100%** (153/153; an initial 75.7% reading was
correctly diagnosed as a verification-methodology artifact — `select()`'s joint pairwise
optimisation can shift a collateral untouched unit's command — fixed and re-verified rather
than explained away), 32/32 tests, dev copy restored byte-exact and re-verified, activation
99.8% on 4,096 paired episodes.

**The intervention worked and the outcome was catastrophic.** Median first plant **turn
13.0 vs control 199.0** (gate ≤60, PASS); peak concurrent crops 1.98 (gate ≤8, PASS); no
detector worsened and `idle_with_work` improved 58.7% (PASS). But **reap rate FELL to 0.45%
from 0.68%** (gate ≥5%, FAIL) — planting earlier changes only *when* a plant appears, not
what our grammar does with it afterwards, which is convert it to wood (D87's exact finding:
+3.866 plants, zero additional own-crop harvests). And the safety ratio failed decisively:
**Δown −5.41 while Δopponent +21.09** — our own score *fell* while the opponent's rose. (The
analyzer caught and fixed a sign-flip that would have let the naive ratio false-pass.)
Value: **−26.44 overall** (CI [−28.96, −23.92]), activated −26.50, worst family −51.31,
catastrophes **229 vs 130**, negative-mass ratio 1.97 — all six sub-gates fail.

**The structural conclusion, now backed by three independent tests.** D89 (full factory:
+82.9 opponent, of which +76.5 from the opponent's own crops), B4.5 (field correlation:
+20.8 opponent score for higher-planting peers, CI [1.8,38.0]), and D175 (Δopponent +21.09
against Δown −5.41) all say the same thing: **for this bot, production trades away more
denial than it gains.** Turns spent farming are turns not spent suppressing, and the
opponent's loop compounds faster than ours because we cannot harvest what we plant
(B3.5/D173: no HARVEST candidate for busy units, trained units hardcoded `harvest_power:
0`). Our wood-dominant, suppression-led shape is not an accident or an oversight — it is
this architecture's comparative advantage, and every attempt to add production on top of it
has been net negative.

**Consequences for the programme.** Early/bounded planting is CLOSED; do not retune its
window, concurrency cap, or distance bound. The full chain is now closed at every link:
harvest capability (D173, capped by hp:0 plus family/tail costs), mining (D174a, wrong
resource and harmful), scaling (D174a, hard-capped and unaffordable under the real bill),
early planting (D175a, harmful). The one unexplored lead that plays *to* the architecture
rather than against it is B4.4's finding 3 — suppression efficiency, 0.31 vs 0.43 wood per
chop and 41.1% vs 46.6% opponent-crop contact — execution-class, aligned with our actual
strength, and incapable of feeding the opponent. Opened as B4.6.

## 2026-07-29: B4.5 — "chopping always wins": the planting gate is priority, not a disabled subsystem

Two corrections to B4.4's reading. **(1) The live artifact does not contain the factory.**
`banana_factory_enabled` is hardcoded `false` in the only constructor chain `main()` uses
(`:4077` via `new()`→`with_policy()` `:3824-3832`, called unconditionally at `:6016`), so
its one-shot selector (`:5216-5234`: `live_plants ≤ 20 && fruits ≥ 27 && banana_plants ≥ 6`,
evaluated once at roster 2) is dead code — and the deployed slim artifact, SHA-verified
against STATE.md, contains **zero occurrences of `banana_factory`/`ScarceIntent`**,
consistent with the 07-17 slimming pruning provably-dead families. **(2) The real
mechanism** producing turn-191.5 is two other live paths: a rare map-gated single-mother
orchard (`:4394-4443`, `:5242-5429`) and an idle-regeneration fallback that permits PLANT
only once a worker has nothing left to CHOP (`:3084-3145`, `:3200-3253`). **Chopping always
outranks planting**; we farm only when idle.

Measurements: the dead selector would fire in **12/204 = 5.9%** of games (evaluated on
decoded state at each game's own roster-2 turn, median turn 7); fruit and banana floors
each block ~70%, the plants cap binds only 13%; halving the floors reaches ~10–20%
coverage. Timing is not the constraint — we reach roster 2 at turn 7, long before peers
begin planting at 21–29. Peer design vs D89: **not structurally different** (peers are
~50/50 bank/harvest-seeded and self-chop 76% of their own crops vs 16% harvested — the same
wood-dominant pattern D88 found inside D89) — the difference is **bound**: D89 dumps 100%
of its bank at once with no cap, peers hold **~5–6 concurrent own crops**.

**Risk, field-confirmed:** D89's leak mechanism is visible in real games — a within-agent
high-vs-low planting split shows **opponent score +20.8, CI [1.8, 38.0]**, surviving a
game-length confound check, and **11/16 peer agents exceed D89/D91's 0.40 safety ratio**.
Peers appear to absorb the leak through the suppression efficiency we lack (B4.4 finding
3: 0.31 vs 0.43 wood/chop). Note also that D91's real failure was **map-cluster support**
(CI [−1.74, +63.76]), not the efficiency ratio, which it passed at 0.337.

Design consequence for D175: do not resurrect the pruned factory or tune its dead selector.
Target the priority defect directly with a **bounded-concurrency early planting rule**
matching the peers' measured shape, and reinstate the Δopponent ≤ 40%·Δown safety ratio
unweakened on a wider map panel than D91's.

## 2026-07-29: D174a CLOSED-AT-MECHANISM — and it corrects B3.9 while exposing a hard 2-worker cap

**Phase-0 preflight, before any code change: 0/64 (0.0%).** With the bank synthetically
credited to exactly cover a cheap-helper bill at workforce 2, the unmodified resident never
issues TRAIN within 10 turns. Root cause: `MoisanBot::can_train` contains
`if n >= 2 { return false }` — **unconditional, evaluated before affordability**. The bot
is hard-capped at two workers no matter what it can pay for. Per the protocol's own
branch, scope became Variant B (mining fix + deletion of that single clause), declared in
the lock.

Execution was clean: trigger fidelity **100.0%** (211/211 emissions satisfy all four frozen
conditions), 34/34 unit tests, diff confined, dev copy restored and SHA-verified twice,
activation 77.9%.

**Mechanism 1/4.** Iron acquisition works exactly as designed: **0.51 → 5.40 iron/game
(10.6×, PASS)**. But unmined-reachable episodes fall only 4.6% (need ≥50%), detector
displacement fails (`door_queue` +16.8%, `unbanked_carry` +13.7%), and decisively
**worker-3 TRAIN remains 0.0% in both arms** — a full 84.4-point shortfall against the
counterfactual prediction, *even with the cap clause deleted*.

**The correction this forces (binding).** B3.8/B3.9's counterfactuals priced a *synthetic*
cheap-helper spec (3 PLUM / 3 LEMON / 2 APPLE / 3 IRON). The live resident's `TUNED_CARRY`
policy actually requests a bill averaging **PLUM 6.23 / LEMON 5.87** at n=2 — roughly
double. Under the real bill the post-workforce-2 bank never reaches the PLUM requirement in
**100.0%** of games and LEMON in **99.5%**: **fruit, not iron, is the binding constraint.**
B3.9's headline 84.4% affordability figure must not be quoted for the real policy.

**Value 0/6, and badly:** overall **−10.76** (CI [−13.16, −8.36]), activated −13.82, worst
family −21.96 with **all eight families negative**, catastrophes 95 vs 71, mass 1.363.
Diverting workers to mine iron they don't need is strictly harmful. Opportunistic mining is
CLOSED; no candidate built; dev copy byte-exact.

**Convergence.** Three independent audits and one causal experiment now point at the same
root: B3.8 (fruit short), B3.9 (iron gated — but the wrong constraint), B4.4 (we plant at
turn 191 and reap 0.93%), D174 (fruit binding, and a hard cap behind it). **We do not farm,
therefore we cannot pay fruit bills, therefore we never scale — and a single unconditional
clause would block scaling even if we could pay.** The fix ordering follows: planting first
(D175, diagnostic B4.5 running), then the cap, then — only if ever needed — mining.

## 2026-07-28: ★★ B4.4 — we plant at turn 191; every two-worker peer plants by turn 21–29

Cohort (corrected from the earlier preview): 25 Legend agents with mean roster within ±0.2
of the resident's exact 2.000, ranks **7–104**; STRONG = 12 (ranks 7–38, above our 43),
PEER/WEAK = 13 (46–104). 2,787 occurrences, 100% decode integrity.

**The dominant difference is tempo, not conversion style.** Median first successful PLANT:
**resident turn 191.5 vs 21–29 for all 25 peers** — a 6.6–9× delay, and not a resource
constraint (starter `hp=1` universally). Reap rate, recomputed independently on the full
corpus: **resident 0.93%** (matching D101's 0.94%), **STRONG 15.3%, PEER/WEAK 17.2%**,
top-3 24.16% — i.e. the reap gap separates the resident from *every other two-worker
agent*, not the strong from the weak. Score composition confirms it is "convert more", not
"convert differently": STRONG 215.6 vs our 185.7 with both wood (+15%) and fruit (+30%)
up, and the resident the most wood-concentrated of all three groups (94.7% of score).

**Code grounding:** the live planner already contains a tested `banana_factory_*`
self-planting/reaping subsystem that defaults to `enabled: false` and is gated by a
one-shot board-richness selector evaluated once at 2-worker roster — consistent with (not
proven identical to) the observed delay. Note the lineage: this is D89/D91 machinery, and
D89's *full* factory was rejected for safety (+162 own but +82.9 opponent) while D91's
selector fired on only 5/16 maps. The field now shows 25 two-worker agents planting early
at moderate volume and holding leads — **the middle ground between "off" and "plant
everything immediately" has never been tested.**

**The crux, quantified.** Trajectory shape: resident leads **+33.4 at t150** then fades to
**−3.0 at t300** (D159's anti-compounding tail, field-confirmed); STRONG builds a smaller
lead that **holds at +18.2**. Head-to-head we go 38.7% / −12.9 vs the STRONG cohort
(n=31). **At equal roster (2v2) we are at exact parity: 58.2% vs 58.3%.** Outnumbered we
collapse where they do not: vs 3-worker opponents **−37.1 (us, n=60) vs −1.8 (STRONG,
n=700)**; vs 4+-worker **5.0% wins (us, n=20) vs 13.7% (STRONG, n=190)**.

**Ranked verdict:** (1) no sustained plant-then-reap loop — largest, and
policy/parameter-class: a gating threshold in existing tested code, not missing
capability; (2) the scale-asymmetry survival gap — the crux, mostly downstream of (1);
(3) suppression efficiency — smaller, execution-class (0.31 vs 0.43 wood/chop; 41.1% vs
46.6% opponent-crop contact). Honest caveat: 4 of the 12 STRONG agents (Escdemon,
therealbeef, yamo, mehdi_ayari) share our no-loop profile and still outrank us, so the
pattern is dominant but not uniform; for that minority only (3) plus ladder-maturity
confounds apply. Opened as B4.5 (diagnostic) → D175 (fix), sequenced after D174 to avoid
concurrent edits to the resident source.

## 2026-07-28: ★ B3.9 — the bot stops mining at worker two; the scaling bootstrap is a one-site gate

**Root cause, confirmed with zero exceptions.** `iron_candidates()`
(`yamo_orchard_live.rs:936–961`) is the only MINE-candidate constructor in ~6,024 lines,
called from exactly one site (`early_candidates:887`), reachable only while
`own_units < 2` (`:1560`/`:3486`, dispatch `:1581`/`:3545`). Empirically: **100% of our
139 lifetime MINE actions occurred at unit-count 1**, and across 4,090 real legal-but-idle
turns at workforce ≥2 in 171/205 games, mining was chosen **0 times**. The instant worker
two exists, iron acquisition ends permanently.

**Scale of the loss.** We mine 139 iron across 205 games (**0.68/game**, median 0); the
top-5 mine **13.02/game** — 19.2× — with mining spread across worker ordinals 0–4 and no
dedicated miners (every miner-worker is <30% MINE share, i.e. opportunistic). Unmined
reachable iron: **8,051 credit-iron (strict) / 10,211 (generous)**, 98.1–98.5% of it at
workforce ≥2 — meaning **98.3–98.6% of the opportunity is never converted**, with a median
trajectory approach distance of **0** (units stand on the source).

**Crucially, no second capability wall.** Unlike the harvest defect (trained units
hardcoded `harvest_power: 0`, which capped D173), `opening_options:1887` gives every
trained unit `chop_power ≥ 1` — the stat mining uses. The defect is purely
candidate-generation, and an inactive prototype already exists in-source
(`SecureOrchardBot::banana_seed_factory_worker_three_bridge:3871`).

**Combined counterfactual (upper bound, stated as such).** Fruit-only reproduces B3.8
exactly (8.8% cheap / 0% balanced). Iron-only barely moves (1.5%/0%). **Both together:
cheap helper affordable in 173/205 = 84.4% of games (median turn 37), balanced chopper in
87/205 = 42.4% (median turn 71)** — nearly identical under strict and generous
definitions. The residual bottleneck flips from IRON (97–100% of fruit-only failures) to
LEMON/PLUM (65–88% of combined failures).

**Verdict (A): mining slack is large and the fix is warranted** — the top execution-class
candidate the project has ever had, because for the first time a mechanically-identified
one-site defect connects to a priced outcome (B4.3: 2→4 workers ≈ +5.2 rating = 84% of our
gap) with no known capability blocker. Cautions carried into the design: this is stock
accounting, not causal simulation; D94's funding *bridge* trained worker three in 147
tasks and still lost 91.6 margin, so the fix must be **opportunistic** (mine what you are
standing on) rather than a dedicated funding detour; and both D173 variants paid a
trigger-independent family/tail cost for diverting work, which any successor must budget
for. Opened as D174.

## 2026-07-28: B4.3 — the field price of a worker: +2–4 rating points each, 2→4 ≈ 84% of our gap

First field pricing of the scaling direction, over 8,073 clean games (boss and
crash/timeout games excluded). **Head-to-head roster asymmetry** (the natural experiment):
roster difference +1 → **+30.4 mean margin, 66.4% win rate (n=3,415)**; +2 → +81.2, 79.0%
(n=775); +3 → +135.1, 92.9% (n=56). It survives skill-matching (≤2-point arenaScore gap:
+46.2 at n=228) and — decisively for the confounding worry — the **within-agent fixed
effect is LARGER, not smaller: +48.2 margin per worker, 95% CI [44.1, 52.7]** across 169
agents / 15,424 games. Per-worker increments are **not** diminishing where it matters:
2→3 = +22.7 margin (+1.9 rating), 3→4 = +38.9 (+3.3 rating), 4→5 = −18.5 with a CI
crossing zero (no benefit; cap the ambition at four).

**The resident's own exposure**: win rate **100% / 58.2% / 30.0% / 5.0%** against
opponents ending with 1 / 2 / 3 / 4+ workers, margins +101 / +21 / −37 / −76. Our overall
field margin is ≈ 0 (+0.19) — a break-even blend of winning at our own scale and being
crushed by larger armies.

**Two honest qualifications.** (1) Field-wide, roster does NOT proxy rank: the rank-band
table is non-monotonic (top-5 3.55, ranks 6–20 2.50, ranks 21–50 2.90, Gold 2.64) and the
agent-level correlation is ≈0 — which cuts both ways: it weakens "big rosters = strong
bots" as a confound (good for the causal reading) while proving roster is not destiny.
(2) **25 Legend agents run the resident's exact 2.00 roster and rank 7–54** — i.e. a
two-worker architecture can reach rank 7, so a non-scaling path to improvement provably
exists; opened as B4.4.

Verdict: a worker is worth ≈ +25–50 margin (+2–4 rating), concentrated in workers 3–4;
**scaling 2→4 ≈ +5.2 rating points, 84% of the resident's 6.25-point gap to the rank-3
bar.** This prices the destination only — B3.8 showed our path there is iron-limited, so
the whole direction remains gated on B3.9's affordability answer.

## 2026-07-28: comparative waste baseline — the resident is CLEANER than the top cohort on every signature

Detector correctness first: three capacity/precondition bugs found and fixed in the
standing tool (CHOP legality ungated on free capacity — the B3.6 artifact; harvest_slack's
capable-worker annotation; late_train_window's affordability missing `training_blocked`).
Resident `idle_with_work` falls **7,782 → 6,759 episodes (−13.1%)**, corroborating B3.6's
~945-episode diagnosis. Tool now sweeps any agent (46 tests).

First cross-cohort measurement in the project's history: top-5 (875 games) and ranks 6–20
(2,412 games) vs the resident (205), pooled and roster-adjusted (rosters are exact:
workers never die, so final roster = 1 + TRAINs; resident **2.00**, top-5 **3.55**, ranks
6–20 **2.50**). **On all six signatures the resident shows LESS waste than both cohorts,
including per-worker.** The separator is `harvest_slack`: **74.8 turns/game (resident) vs
615.9 (top-5, 8.2×) vs 330.0 (ranks 6–20, 4.4×)** — and in the opposite direction to the
"we are uniquely sloppy" hypothesis. Top-5 episodes are 96% genuinely-capable-worker-in-
range versus our 40.5%; restricted to capable episodes and roster-adjusted, top-5 still
run **9.9×** our rate. `idle_with_work` is near-identical in character everywhere (~80%
single-turn blips), consistent with B3.6.

**Interpretation, recorded as binding:** our execution hygiene is the hygiene of poverty —
with 2 workers and ~12 crops there is little to waste, while the top cohort leaves fruit
lying everywhere and wins anyway on economy size. **Execution-waste minimisation is not
the differentiator**; this is strong independent support for the architectural reading
(D101, D170b, D172a) and it materially downgrades the remaining Tier-3 prospecting.
Execution-class fixes retain their perfect transfer record and stay worth taking when
cheap and positive — but no large execution vein should be expected to exist.

## 2026-07-28: B3.8 — the scaling bootstrap is IRON-limited, not fruit-limited (owner-thesis test)

Counterfactual currency audit over all 205 resident games (0 integrity anomalies). Haul:
**4,880 uncollected reachable own-territory fruit events (23.8/game**; PLUM 1,248 / LEMON
1,154 / APPLE 1,429 / BANANA 1,049), plus an 11,244-event opponent-territory increment.
**90% of the own-territory haul is destroyed by our own CHOP** (84% by us specifically) —
independent confirmation of the B3.5 chop-shadow mechanism from a broader definition.
Bill costs source-verified: cheap helper (1,1,0,1) = 3 PLUM / 3 LEMON / 2 APPLE / 3 IRON;
balanced chopper (2,2,0,2) = 6/6/2/6. The real-bank baseline reproduces D160a exactly:
**0/205 windows** for both specs.

Stock-accounting counterfactual (upper bound — ignores that harvesting costs turns):
crediting all own uncollected fruit opens a cheap-helper window in **18/205 games (8.8%,
median turn 43.5)** and the balanced chopper in **0/205, never**; adding opponent fruit
moves it only to 21/205 (10.2%, median turn 30), balanced still 0. **IRON limits
97.3–100% of all remaining failures in every scenario**, on maps that all contain iron.
Fruit credit essentially closes the PLUM/LEMON side; iron never moves, because iron is
MINE-only and no harvest change touches it.

Top-5 contrast: 34% of their bill currency comes from the starting endowment and 66% is
earned; of the earned share, **76% is fruit and 24% iron** (71–78% fruit consistently per
agent) — they do fund scaling from the orchard, while their later workers' 91% CHOP/DROP
share is wood logistics, not bill funding.

Spatial section (owner hypothesis, confirmed): **1,144 near-camp events (≤2 BFS from our
own door), 956 bill-relevant; only 28.2% fall inside D173b's chop-shadow scope and 71.8%
lie outside it**; 43.4% (496 events, 425 bill-relevant) are capturable within a ≤2-turn
walking detour.

**Verdict (c) NO:** harvest capability is not the bootstrap for worker-3 scaling. The
binding constraint is IRON acquisition. This redirects the owner's production+consumption
thesis rather than refuting it — the coupling the top cohort runs is real, but its funding
path for us must pass through mining, which has never been audited. Opened as B3.9.

## 2026-07-28: D173b CLOSED — the fix works where it can; `harvest_power: 0` is the real cap

Trigger fidelity repaired and verified: **64/64 activations** show CHOP as control's issued
action at the divergence turn (D173a scored 19/60). Implementation is a post-selection
rewrite called once from `commands()`; 32/32 tests; dev copy restored byte-exact (SHA
`fff6669b…`) and re-verified three times. Activation 805/2,048 = 39.3% (vs D173a's 50.9%,
as predicted).

**The decisive finding:** the mechanism gate fails at 21.3% sub-class reduction — but the
population splits cleanly. Among **addressable** episodes (chopper with `harvest_power ≥ 1`,
i.e. the starter) the fix achieves **99.9% elimination (1,002 → 1)**. Among **inaddressable**
episodes (`harvest_power = 0` trained choppers — the constraint the protocol froze as
untouchable) the count *rises* 25.2% (1,092 → 1,367) through downstream cascades, and
**99.93% of all surviving episodes are of that kind**. The fix is not weak; the vein is
capped by trained-unit harvest incapability. Total slack +8.3%; door_queue +21.2% and
idle_with_work +11.9% worsen (unbanked_carry improves, two flat).

**Value, and a pattern across both variants:** overall **+1.063 [−0.056, +2.181]**
(passes ≥0), activated **+2.703** over 805 tasks (passes ≥+1.0) — but worst family
`compact_gold` **−1.391**, catastrophes **52 vs 49**, negative-mass ratio **1.081** all
fail. D173a failed the same three (−2.06 / 54 vs 49 / 1.096). Harvest-before-chop
consistently buys mean value while delaying wood in ways that cost specific opponents and
fatten the tail — that cost is a property of the intervention, not of either trigger.

**Verdict: harvest-before-chop is CLOSED as an execution-class fix.** The residual
question is strategic and now sharply posed: should trained units be harvest-capable at
all (`opening_options:1878–1900`)? That is a worker-capability change, gated on whether
the fruit would actually fund anything — which B3.8's counterfactual currency audit is
measuring right now. No candidate built; no arena action; the owner's D173a promotion
authorization never triggered and does not carry to any successor.

## 2026-07-28: standing collection cron installed and first run

The wide-lens collector is now productionized and scheduled (`data/scripts/collect_wide.py`
+ `collect_wide_cron.sh`, daily 05:17, crontab marker `# troll-farm-wide-collect`, commit
`b15a75f`; six offline failure-path tests plus the live suites ran before any network
call). Its first live run: **+9 new games, corpus 8,122 → 8,131**, snapshot
`20260728T110709Z-d61p-wide`, 50 players enumerated (resident once — the earlier
duplicate-source tag is fixed by construction), all 11 QA gates true. Corpus figures
quoted after this date should use 8,131; the 8,122 figure in the wide-collection entry
above is correct as of that entry.

## 2026-07-28: B3.6 CLOSED — idle_with_work is ~78% benign; no fix candidate, and round 2 partly self-corrected

Full-corpus sub-classification of all 7,782 episodes / 10,279 turns (reproduces round 2's
totals exactly): `short_transit_blip` 4,852 (median 1 turn, benign), `harvest_gap` 1,086
(set aside — already B3.5/D173's vein), `capacity_full_correct_transit` 945 (**detector
artifact**: `waste_sweep.py:371-372` doesn't gate CHOP legality on free capacity, while
the bot and the engine both correctly refuse wood to a full chopper), `closed_oscillation
_vein` 539, `late_game_no_time` 160, `contested_colocation` 107, `opening_ripeness_wait`
20 (100% fate-verified benign), residual 73. **Round 2's flagship "wood-race" finding does
not survive**: all 107 contested episodes fate-traced — 52% ripen normally, 29% the
resident shares the kill, only 11% (12 episodes, ≤68 pts corpus-wide) are clean losses;
the named exemplar did receive its wood share. Also traced `opponent_eta_penalty` to dead
code (0 through the full construction chain) and falsified an orchard-mother hypothesis
via `opp_doors` geometry; NEEDS_CONTEXT on the exact per-turn contested mechanism, which
does not change the value conclusion.

Net: ~78% of non-harvest_gap turn-mass is benign/correct/artifact, ~8% zero-value
late-game, ~8% closed vein; genuine ceiling **≤130 pts corpus-wide (≤0.6/game)** across
~20 unrelated single-turn incidents with no shared mechanism, and every class is flat or
inverted across wins/losses. **Verdict: no cycle warranted — B3.6 closes negative.**
Follow-up recorded: gate the `idle_with_work` detector on free capacity (deferred while
D173b uses `waste_sweep.py` for its mechanism gates).

## 2026-07-28: D173a CLOSED (trigger infidelity) → D173b repair frozen; the broad variant's signal recorded

D173a ran cleanly (3-hunk fix, 30/30 tests, compile-then-restore kept the tree byte-exact
throughout, 2,048-task panel, 1,005/1,005 inactive tasks byte-exact) but the implemented
trigger was broader than the frozen spec: it fired on CHOP-candidate *existence* at the
unit's cell rather than CHOP being the unit's *assigned action* — 41/60 sampled
activations were transit units diverted mid-plan. All three mechanism gates failed
(sub-class −23.6% vs −70%; total slack +7.8%; door_queue +30%, idle_with_work +15.3%
worsened) and value failed family/tails (worst family compact_gold −2.06; catastrophes
54 vs 49; mass 1.096) — **while overall value was strongly positive: +2.935
[+1.346, +4.524], activated subset +5.763 over 1,043 tasks (50.9% activation).**
Adjudication: implementation-fidelity invalidation (D170a precedent) — the frozen narrow
fix was never tested. **D173b frozen** (trigger reads the actual assignment; ≥90%
pre-panel fidelity check; all else inherited, same seeds rerun from scratch). The broad
variant is CLOSED as tested and may not be tuned; its +2.9/+5.8-with-regressions signal
is recorded as hypothesis material for a future, separately-designed transit-unit
opportunistic-harvest experiment (guards for family/tails would be the design core).

## 2026-07-28: B3.5 diagnosis — HARVEST is a missing action class; D173 fix frozen

Root cause, confirmed by two independent source reads cross-checked against all 1,014
capable-worker episodes: the busy-unit candidate generators (`main_candidates:3084–3145`,
`endgame_candidates:3200–3339`) construct **no HARVEST candidate at all** — the only
fruit-aware fallback (`idle_harvest_candidates:3340–3387`) is gated behind endgame AND
no-other-target, structurally unreachable; and `opening_options:1878–1900` hardcodes
`harvest_power: 0` for every trained unit, so only the starter is ever harvest-capable
(the same fact D167 measured from the trajectory side: 96/135 returning workers hp=0).
Sub-classes: 58.7% transit passthrough, **33.4% chop-shadows-harvest** (the worker
destroys the fruit with the tree it chops), 6.3% second-task, 0% deliberate reserve (two
independent checks). Net value after deduplication (a triple-count bug caught before
trusting the number): deliberate 0; delayed-but-banked 16 pts; **genuinely lost 688
events / 1,972 pts = 9.62/game mean**, +23% in losses (~19% of an average losing margin).
The richest execution vein assayed to date.

**D173a frozen** (`d173a-harvest-before-chop-protocol-2026-07-28.md`), scoped narrowly
per the diagnosis's honest recommendation (cc=1 makes blanket fixes force costly bank
detours): one stateless candidate class — harvest-capable unit chopping a ripe-fruited
tree at shack-distance ≤2 harvests the fruit first, then resumes the chop. Reuses the
`fruit_candidates:910–919` sibling pattern; no new state machine (D171a lesson);
`opening_options` and the orchard reserve untouched. Panel 2,048 fresh paired episodes
(seeds 9,854,000–127); mechanism gate = sub-class slack −70% with no displacement across
all six waste detectors; value gates = non-regression + activated ≥ +1.0. QUALIFIED
builds a candidate that stops at the arena gate (new owner authorization required).

## 2026-07-28: waste-sweep round 2 — standing tool committed; harvest_slack is the new top lead

The execution-waste detector library is now a committed tool (`cgauto/waste_sweep.py` +
41 tests, commit 31b3ef0; two real detector bugs caught and regression-tested during
development). Round 2 over all 205 resident games (98W/106L/1T, 20 catastrophes), six new
signatures: `repeated_failed_command` 0 (clean, verified non-vacuous);
`late_train_window` 1/205 (resident trains immediately when affordable — policy healthy);
`door_queue` and `unbanked_carry` residuals are closed-vein re-detections or scattered
single turns; `idle_with_work` large (7,782 episodes, ~38/game) but flat across outcomes
and heterogeneous — needs sub-classification before any cycle (one confirmed genuine
pattern: contested-tree wood race; one confirmed NON-waste: the deliberately idled
orchard reserve unit — any future fix must exclude it). **Top candidate:
`harvest_slack`** — 2,163 episodes / 15,326 turns in 204/205 games, ~536 points gross
foregone value (~2.6/game ceiling), +15–20% loss/catastrophe enrichment, 91% independent
of the oscillation vein, and 46.9% of episodes have a verified-capable worker nearby;
plausible target-reassignment root cause. Ranked worth a diagnosis+fix cycle (opened as
B3.5). Report: session scratch `waste-sweep-round2-report.md` (numbers preserved here).

## 2026-07-28 (later): OWNER DECISION — Tier-2 REOPENED (option a)

The owner reopened Tier-2: "Let's reopen Tier-2." The dense-counterfactual-credit
successor program is authorized as **D172** (protocol frozen same day). Maintenance-mode
items (collection cron, sweeps, no-churn) continue unchanged; the earlier hold decision
is superseded only for Tier-2. Arena/promotion for any D172 product would require its
own explicit authorization at that gate.

## 2026-07-28: OWNER DECISION — hold (option b)

Presented with (a) authorize a new dense-counterfactual-credit successor program, (b)
hold at maintenance, (c) re-scope the goal, the owner chose **(b) hold**. Maintenance
mode is now active: standing wide-lens passive collection (authorized under this
decision's "let the corpus compound" clause; installed as a daily system cron —
token-free, trivially removable), occasional execution-class sweeps (B3.2) and field
re-powering audits (B3.3), housekeeping (B5.1/B5.3), and the absolute no-churn rule. No
Tier-2 successor is authorized; the dense-credit design remains on the shelf, documented
in STATE §4, available for a future (a) decision. The rank-≤3 goal remains formally
standing but has no evidence-permitted active program; re-scoping stays open to the
owner.

## 2026-07-28: B3.3 field re-powering + B3.2 waste sweep on the 8,1xx-game corpus

B3.3 recomputed the small-n field measurements on the quadrupled corpus (read-only; frozen
verdicts stand). Stable within old CIs: D167 BANK_SEED top-5 share 71.4% (n=21) → 67.5%
(n=243); pre-carry 44.9% (n=49) → 40.5% (n=635); B3.1 catastrophe rate 9.9% → 9.8% with
scaling lead time mean 74.4 turns CI [63.9, 85.8] (the resident's own game set was already
exhaustive — re-confirmation, not re-powering). One material mover: **D164's top-5 P→S→P
motif rate 72.0% (36/50) → 49.7% (435/875), CIs non-overlapping** — diagnosed as sampling
completeness, not regime change: the old recent-10-per-agent windows over-sampled peer
matchups, while the full windows are 91.7% non-peer opponents. D164's actual frozen gate
(breadth + gap) still passes cleanly on the new data (5/5 agents, +38.9pp over the
resident's 10.8%); the *population* motif rate is hereby corrected to ≈50% for future
reference.

B3.2: the motion audit replicates its zero-failure result at 4× scale (49,977 real arena
moves: zero target-landing, teammate-block, or door-stall failures). **One concrete
execution-class candidate found: sustained same-two-cell target oscillation** — ≥10-turn
runs in 18/194 resident games, worst 131 consecutive turns with frozen unbanked carry,
~2.8× enriched in catastrophes (causality unestablished; losing-game pathology is a
plausible confounder). Logged as open lead B3.4: diagnose the planner standoff, test a
bounded fix under the usual causal protocol — execution-class, the only family with a
perfect arena-transfer record. Context notes from the 29 first-seen agents: Pafin reaches
five workers in 48% of its games (resident 0/194); persistent-denial styles exist that the
local 8-family panel does not exhibit. Report: session scratch
`b32-b33-field-audits-report.md` (numbers preserved here).

## 2026-07-28: OWNER STANDING AUTHORIZATION — D171 promotion on QUALIFIED

The owner pre-authorized the arena trial: "when new solution passes internal gates, send
it to platform." Scope recorded in STATE §3: if D171a returns QUALIFIED, protocol B4.1
executes without a further ask (capacity A/A, candidate submit, timed reads, frozen
bands, exact-resident restore on failure or inconclusive). This one candidate only;
no-churn rule otherwise unchanged.

## 2026-07-28: D171a CLOSED — the hard-forbid oscillation breaker fails its mechanism gate

The fix was implemented exactly per spec (28/28 tests, diff confined, purity safety net)
and run on 2,048 fresh paired tasks with clean integrity. **Mechanism failed decisively:**
≥10-turn runs reduced only 45.7% (floor 80%); 5–9-turn runs +117% (displacement); 72
zero-oscillation tasks acquired NEW runs (worst de-novo 88 turns). Root cause: the frozen
disarm rule misses "echo stopped on its own" — a coincidental 3-reversal blip arms the
unit permanently against a stale cell, and the stale prohibition manufactures new
oscillations. Value neutral overall (+0.053 [−0.04,+0.15], tails tied) but activated
subset +0.53 < +1.0. No tuning attempted; no candidate built; the dev copy restored
byte-exact (SHA matches the frozen control snapshot); the owner's promotion authorization
never triggered. Successor requirements recorded: bounded arm lifetime + echo-stop disarm
+ ≤2 forced choices per arming, or preference-based (not hard-forbid) tie-breaking.
Infrastructure constraint discovered: `lib.rs` re-exports the dev copy as
`troll_farm::resident_policy` — controls must snapshot it; working-tree diffs to it
contaminate all concurrent runners. Full record:
`d171a-oscillation-breaker-{protocol,result-2026-07-28.md,result.json}` +
`d171a-fix-as-tested.patch`.

## 2026-07-28: B3.4 diagnosis — oscillation root-caused; D171 bounded fix frozen

The same-two-cell oscillation is a **memoryless detour tie-break**: in
`resolve_move_conflicts_with_priority_and_forbidden` (dev copy `yamo_orchard_live.rs:
1440–1520`, tie-break :1505–1519), a unit blocked by a parked teammate resolves its detour
by `min_by_key((BFS_dist, Cell))`; ties break on incidental lexicographic cell order and,
with zero cross-turn memory, the identical choice regenerates indefinitely. All 18
episodes re-derived exactly (worst 131 turns, game 896350846); both cells always plain
ground; 17/18 involve a teammate parked ≥85% of the run (11/18 at the own shack door on
the wood loop). The resident's existing `force_unique_door_clear` defense never fires —
gated on `unique_shack_door()`, but all 18 games have 2–4 doors: a genuine coverage gap.
Two byte-exact turn-by-turn reconstructions confirm the mechanism (predicted-vs-actual
command traces match perfectly).

Causality split is modest and honestly recorded: 2/18 causally suspicious, 4/18
symptomatic-but-compounding, 12/18 benign (several wins); none of the 5 catastrophes in
the set shows clean causal evidence (r=−0.116). This is a waste-cut, not a catastrophe
cure. **D171a frozen accordingly** (`d171a-oscillation-breaker-protocol-2026-07-28.md`):
wire per-unit t−2 memory into the existing unwired `forbidden_for_non_priority`
parameter, arm after 3 confirmed reversals (the corpus histogram's elbow), disarm on
progress; 2,048 fresh paired episodes (seeds 9,853,000–127) + ≥14/18 historical run-break
confirmation; primary gate = mechanism elimination ≥80% without displacement; value gate
= non-regression (CI ≥ −0.5) + activated-subset ≥ +1. QUALIFIED builds a checksummed
candidate that STOPS at the owner's arena gate.

## 2026-07-28: D170b CLOSED-AT-PHASE-2 — the closed-loop option program closes on valid mechanics

The repaired re-run is mechanically flawless: frozen inherited block byte-identical (all
repair hunks ≥ line 998), 12/12 env tests, activation diagnostic field-identical on
rerun, new lock frozen. Delta-3 required a standalone D170b trainer/analyzer (D170a files
left byte-unmodified; hashes locked). **Phase 1: 8/8 fits reach `trained`** — reversing
D170a's 8/8 mechanics-fail — with every one of the 13 arms (including the three repaired
trig arms) offered and invoked in every fit; minimum conditional exploration share
0.034–0.108. Fit-side mean margins of sampled invocations: **−0.96 to −2.26 across all
objectives.**

**Phase 2: 0/8 admitted.** Every deterministic policy chose KEEP on literally all 2,048
of its held LOBO decisions (`chosen_arm_counts: {control: 2048}`), all statistics exactly
0.0; verified by direct logit inspection (P(invoke) 0–3.27%, logit gap ≥3.39) — a learned
conclusion, not an evaluation bug. 1-vs-20-thread byte identity held. Phase 3 not
executed per the decision tree; the veto panel and sealed confirmation block
9,852,000–063 remain untouched.

**Adjudication (Fable): the closure is valid and informative.** All four objectives —
including group-DRO + own-score protection — converged to the same always-KEEP answer,
so the skipped-D109 objective question resolves as: *objective choice cannot rescue
learning when the per-context signal is too sparse to find.* The mechanism: the +10.671
envelope is a per-game hindsight max; unconditional invocation value is negative (D163),
realistic trigger-armed density thin (+1.80, D169 diagnostic), and budget-1 training
yields only ~200 invoke samples per arm against SD≈26 terminal-reward noise — orders of
magnitude short of resolving the rare positive contexts. On-policy terminal-reward
policy gradient over this option space is closed. Per the frozen kill rule ("no fit
admitted → the closed-loop program CLOSES"), **Tier-2 closes and the project holds at
Tier 0/3**; any successor (e.g., dense counterfactual credit over the same options)
is a NEW program requiring its own authorization, and re-scoping the goal is an owner
decision. Full record: `d170b-family-robust-option-policy-{lock,result-2026-07-28.md,
result.json}` + per-fit JSONs; checkpoints external.

## 2026-07-28: authorized wide-lens passive collection — corpus 1,891 → 8,122 games

User-authorized read-only collection with a deliberately widened lens: resident full
window + top-20 FULL visible windows (previously sampled at 10/agent) + ranks 21–50
(previously never fetched). Yield: 2,345 new top-20 games + 3,838 new rank-21–50 games
(29 agents new to the corpus) = **6,231 new games in one run**; cumulative store
1,891 → **8,122 games / 2.4 GB**, 469 unique agents. The old sampling lens had been
leaving ~85% of the visible stream uncollected — per-agent "last battles" windows rotate,
so unharvested games are lost permanently; regular wide collection converts the stream
into a compounding archive. QA: primary snapshot 11/11 gates; wide snapshot content-clean
(0 parse failures across 6,841 games, all 10 integrity gates) with pass=false solely on
acquisition-completeness from 105 transient DNS/timeouts — all recovered by retry, zero
permanent losses, zero 422/429. Cumulative rebuild: 8,122/8,122 parsed, 99.7% exact
scores, 0 unexpected mismatches. Standings bit-identical to 07-27 (resident 43/110 @
21.97, 203 battles; bar delineate 31.00 / norxondor 29.52 / MSz 28.22); no roster
changes. Disclosed anomaly, zero data impact: the wide snapshot's audit manifest mislabels
the resident's 203 records' provenance tag (`legend_21_50` — its rank 43 fell in that
slice); content, cache, and stats unaffected; manifest left immutable per design.
Snapshots: `data/raw/snapshots/20260728T050038Z-d61p{,-wide21to50}/`. The games store
(2.4 GB, gitignored raw) is now a future external-migration candidate per storage policy.
No arena write; no submission.

Operational, same day: the data-footprint cleanup executed per
`docs/superpowers/plans/2026-07-24-data-footprint-cleanup.md` with per-task review — 22
clean worktrees removed (branches intact), `rust/target/debug` cleared + AGENTS.md cap
rule, tranche-2 migration of 683 files / 1,042,056,986 bytes verified (count+bytes+SHA-256
+ zero-diff dry run) then symlinked, YT dead D144 first-attempt directory removed under
guards, and a 424,896,968-byte md5-verified mirror of the whole `legacy-data-analysis`
tree uploaded to `//home/delivery_ml/research/tarstars/troll_farm/mirrors/`. Local repo
23.5 → 2.76 GB; Python suite unchanged at its documented baseline (1,163 passed / 3 known
pre-existing failures).
