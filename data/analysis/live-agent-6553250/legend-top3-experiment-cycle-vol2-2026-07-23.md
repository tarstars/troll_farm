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

Operational, same day: the data-footprint cleanup executed per
`docs/superpowers/plans/2026-07-24-data-footprint-cleanup.md` with per-task review — 22
clean worktrees removed (branches intact), `rust/target/debug` cleared + AGENTS.md cap
rule, tranche-2 migration of 683 files / 1,042,056,986 bytes verified (count+bytes+SHA-256
+ zero-diff dry run) then symlinked, YT dead D144 first-attempt directory removed under
guards, and a 424,896,968-byte md5-verified mirror of the whole `legacy-data-analysis`
tree uploaded to `//home/delivery_ml/research/tarstars/troll_farm/mirrors/`. Local repo
23.5 → 2.76 GB; Python suite unchanged at its documented baseline (1,163 passed / 3 known
pre-existing failures).
