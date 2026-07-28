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
