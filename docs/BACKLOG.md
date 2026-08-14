# BACKLOG — Troll Farm priorities

Created 2026-07-27; **reprioritized 2026-07-29 (post-terminal, post-review)**. Evidence
citations: `Dnnn`/`Phase n`/`B*` = ledger; classes/closures = `docs/CONSTRAINTS.md`.
Re-rank only from written evidence. One experiment in flight at a time; read-only audits
may run in parallel and are claimable by any agent under
`coordination/multi-agent-protocol.md`.

## P0 operational safety — coordination transport hardening

- **DONE / PHASE 3 MANDATORY.** The 2026-08-05 banana handoff exposed incomplete canonical delivery,
  a missed pushed review, a 188-message stale inbox, clock-skew-sensitive ACK matching, and an
  inbox implementation that can silently accept failed fetches or count an unpushed working-tree
  ACK. Replace it with remote-only authoritative state, exact-path `ack_for`, canonical handoff
  artifact validation, exact-path seen state, corrections as new immutable messages, loud errors,
  filters, and backward-compatible migration. The bounded revision passes 41/41 tests and a
  701-message remote-only live scan with zero collisions/delivery errors; it is integrated and
  schema v2 is mandatory for new messages. Per-agent seen-state migration remains operational
  rollout, not a code blocker. Task:
  `coordination/tasks/20260805-coordination-transport-hardening.md`.

## P0 operational safety — Arena submission registry

- **R1 DONE / INTEGRATED — categorized submission-history registry and query tool.** The
  2026-08-02 selection mistake considered only the recent owner-directed lineage and one
  22.99 far-denial maximum, omitting repeated stronger preseed-resident evidence. The repeated
  far-denial source has now terminated at 19.37, rank 73/130. Build a deterministic JSON
  projection plus query/preflight tool, categorized independently by strategy/architecture,
  deployment purpose, evidence maturity, disposition, comparison type, and authority. Default
  source ranking must aggregate repeated mature runs and expose cross-era comparability; it
  must never select by a single maximum. Task and acceptance contract:
  `coordination/tasks/20260802-arena-submission-history-registry.md`. Run
  `python3 cgauto/submission_history.py preflight <candidate-source>` before selection;
  deterministic build/validation pass and the maintained real pytest suite is 45/45. The live
  registry is current through rejected no-orchard `41085842` and active exact E7a restore
  `41086057` / agent `6592131`; deterministic validation passes with 45 observations.

## Position summary (2026-08-02)

Active resident is exact E7a restore agent `6592131` / submission `41086057`, source SHA
`97bfe71e3f2f...`. Its complete identity-clean checkpoint has 162/162 finished, score 23.56/rank
32/137, 93W/3T/66L, and zero runtime signals. The preceding exact deployment read 25.3/rank 12;
the exact source now has two mature runs at median 24.41. The owner-directed no-orchard ablation
terminated at 23.27/rank 34 and was rejected. E7a remains a consumed-panel owner override, not
prospective validation.

**P0 BANANA RESTORATION R2 — assigned to Claude; round 4 implementation-invalid.** The unbounded factory
`6590083`/`41081195` and bounded ring `6590136`/`41081465` are implementation-invalid trials, not
evidence rejecting banana production. The ring bot has exact long period-2 movement in live game
`897829265`; the unbounded bot violated the intended geometry/collection lifecycle. Claude retries
from stable parent `a8eb3b2b...` under `coordination/tasks/20260802-banana-restoration-r2.md`.
Implementation validity, broad inactive-state equality, and exact counterexample liveness precede
any value test. Round-4 SHA `9f5ef833...` repairs the conversion oracle/flip response but a broad
host task has a full wood carrier oscillating for 225 turns; a new hash and red/green banking gate
are required.
The displaced b100/e6 resident finished at 23.12/160; repeated exact E7a evidence is now the
registry leader at median 24.41. Corpus catch-up is complete at 10,470 games / 513 agents / zero parse
failures, +282 in the manual run and +1,388 over the stale STATE count. **Goal
re-scoped 2026-07-30: mature score ≥ 25.40, interim checkpoint 24.70 = yamo; rank ≤3
superseded. H2 is optional upside, not goal-required.** **The TERMINAL SYNTHESIS closed all eight improvement
routes for this architecture** (ledger vol 2; atlas). The decisive structural facts: at
equal roster we are at parity with strong two-worker peers (58.2/58.3) — the whole
deficit is scale-asymmetry survival; a worker prices at +2–4 rating (2→4 ≈ 84% of the
gap) but scale is unaffordable because we cannot harvest what we produce, and production
grafts are structurally negative (three independent confirmations). Corpus 9,082,
compounding daily. Direction menu: `docs/rank-hypotheses-2026-07-29.md` + its integrated
review `docs/reviews/2026-07-29-chatgpt_1-rank-hypotheses-critique.md`.

> **2026-07-30 — SUPERSEDED BY BREADTH STRATEGY.** Owner directive: at a plateau, enumerate
> every feasible approach and roll it rather than filter by judgment. The complete register
> is **`docs/APPROACH-REGISTER-2026-07-30.md`** (35 items across measurement, execution,
> search, learning, economy, opponent interaction, and mechanics). Rolling rule: **no value
> bar on audits** — cheap measurement is the filter; the ≥+1.0 rating bar still applies to
> experiments; programmes stay owner-gated. Keep 2–3 audits in flight. The iteration-2
> section below remains valid as the subset that was already prioritized.

> **A2-1 CLOSED — FAILED K1.** The first new economy scheduler passed development narrowly
> (206/512 = 40.23%) but reached only **582/2,048 = 28.42%** fruit-funded worker 3 by
> turn 110 on locked confirmation. Own reap/banking, scaled mining, referee quality,
> thread parity, and detectors pass; transfer does not. The A2 programme stops before
> Phase 2. **M1 is DONE / DESCRIPTIVE_ONLY; N2 is DONE / B4_4_CORRECTED; M2 is
> DONE / NO_ACTIONABLE_MATCHUP; M3 is DONE / NO_ACTIONABLE_SEAT_ASYMMETRY; M4 is
> DONE / NO_MATERIAL_MATCHMAKING_DRIFT; M5 is DONE /
> NO_MATERIAL_LENGTH_ASSOCIATION; N5 correction preserves NO_MATERIAL_CONTEST_OPPORTUNITY
> and awaits narrow re-review; N6 is independently accepted / CLOSED_AT_DEVELOPMENT. Next: peer corrections,
> then remaining execution/search audits. E2 is DONE / ROUTE_RESIDUAL_OBSERVED but not
> experiment-justified (0.335 hindsight movement turn per side-game). E3 is
> VOID_PREMISE_DUPLICATE under the exact-resident repeated job oracle. E4 is DONE /
> KEEP_LEXICOGRAPHIC: the secure-orchard tie is active but reversing it loses −0.0855
> exact-1,000-map-weighted margin. E5 is DONE / KEEP_RIPENESS_WAIT: +0.1056 overall,
> but seat 0 is negative and magnitude is below +1. E6 is VOID_PREMISE_DUPLICATE under
> D167/D168's acquisition/pre-carry/species/terminal-value coverage. E7 is DONE /
> HINDSIGHT_RESIDUAL_ONLY: blanket inversion −12.174, but a seed-level binary hindsight
> ceiling is +10.510 with 24/60 flips and 6/6 positive leave-one-family-out evaluations.
> Keep the default; E7a is a peer-review-gated prospective-selector decision. S1 is DONE /
> FULL_EXACT_INFEASIBLE: 589 late roots show a manageable first ply but not a 10–50-turn
> full simultaneous stochastic game under 50 ms. S2 is
> DEPENDENCY_GATED_REPRESENTATION_BLOCKED on N4→E1 value and a new map representation.
> S3 is DISTINCT_MULTI_GATED: genuinely new as a combination, but under-specified,
> unsupported by a transferable opponent/value model, and not timed under 50 ms.
> L1 readiness is DISTINCT_PRIMITIVE_ONLY: 199 exact delineate games expose 145,448
> final per-unit labels, while internal train-plan/logit/beam targets remain latent;
> L1a extractor work is peer-gated and teacher accuracy is never a value gate. L2 is
> N4_DEPENDENCY_GATED: the exact compatible two-worker pair sum-max is the sole
> non-closed material live ranker, so no L2a precedes accepted N4 coverage and value.
> L3 is likewise N4_DEPENDENCY_GATED: fixed grammar does not bound repeated score
> authority; imitation and single-state/broad value learners are already consumed.
> H4 is NO_MATERIAL_DENIABLE_BILL: B3.1 timing replicates in 17/20 catastrophes and
> all 17 bills need post-start supply; 73 batches are individually load-bearing, but
> 43 are non-deniable IRON and the 30 fruit batches yield 0 legal one-command blocks.**
> **H3′ is TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY:** matched contact-hazard DiD
> is 0.606 (CI [0.410,0.895]) and the entirely pre-loss result is 0.510
> (CI [0.293,0.841]). H3a source reconstruction is exact and accepted: only the archived
> treatment, conditioned versus identical-always-on versus unchanged control, can
> establish value.**

## P0 — TOOLING INTEGRITY: guards that cannot fail (opened 2026-08-10)

- ★★★ **OWNER-DIRECTED.** `coordination/tasks/20260810-guards-that-cannot-fail.md`. **Seven
  instances in one week of a check that passes regardless of what it checks** — four of them the
  integrator's. Classes: no precondition, unreachable guard, wrong code path, disarmed harness
  (×2), no negative control, no fixture. The sharpest: `lint_outbox` was run as
  `lint | tail -3 && commit && push`, so `&&` gated on `tail` and the guard was **never armed for
  a whole session**; it printed `errors (1)` and the push proceeded, publishing an invalid
  immutable message.
  **Measured surface:** 426 test files, 1,587 test functions; **6** with no check of any kind,
  **6** with an assertion that cannot fail. *(A naive bare-`assert` scan says 83 — 92% false
  positive, because it misses `self.assertX` and `pytest.raises`. Do not re-run the naive
  version.)*
  **Sub-items:** G1 twelve known vacuous checks → `codex_1`; G2 negative controls for the 96
  transport tests → `claude_1` (integrator authored both tests and subject, so the reviewer must
  not be the integrator); G3 precondition audit → unassigned; G4 unreachable guards → unassigned;
  G5 disarmed harnesses incl. shell invocation patterns → `local_claude_1`; **G6 the 22 of 47
  detector branches with no fixture → `claude_1`, OWNER GO-AHEAD REQUIRED FIRST** (real work, no
  score attached, competes with σ and the banana question).
  **Standing rule established:** *a new test is not finished until it has been observed failing.*
  Break the subject, watch it fail, restore, and say in the commit what you broke.
  **STATUS 2026-08-12: G1 ✅ (codex_1, integrated, gate 1679/0). G5 ✅ (11 findings F1–F11;
  publish now ONLY via `scripts/publish_outbox.sh` — lint unpiped is the gate — plus a pre-push
  hook backstop; mutation runner refuses vacuous/unacknowledged-partial drives). G3 ✅ / G4 ✅
  (bounded first passes; residuals enumerated in
  `local_claude_1/verification/g3-g4-guard-audit-2026-08-12.md`; key instrument fact: the 96
  transport tests run via subprocess, so in-process coverage cannot vouch for them — mutation
  drives are the honest instrument for G2). G2 ✅ **CLOSED/INTEGRATED same day** (claude_1's 13-mutant targeted pass, codex_1 independent
  reproduction, provenance revision `6fbacca4` merged; doer/reviewer/integrator all distinct).
  G6 ✅ **COMPLETE 2026-08-13** — all 19 actionable branches resolved (17 pinned with both
  halves; 2 proven untestable-equivalent, excluded by ruling with proofs); kill rate
  21/64 → **51/62**; codex_1's review is the last gate on the whole guards task.
  Guards scoreboard: **G1–G6 ✅ (G6 review pending) · now: claude_1 → c5 instrument ruling.**

## P0 — OWNER RULE 2026-08-10: no banana before the second troll

- ★★★ **STRICT, BINDING, INTERIM.** *"no banana manipulation before train the second troll"* —
  threshold 0, no exemption. This is detector **D-9 branch (a)** `banana_before_train`. It
  **dissolves** the D-9 affordability question that had blocked bite-test blocker 3 and had been
  unowned since `local_codex_1` went dormant: there is no affordable delay to price when the
  permitted count is zero. Recorded in `docs/CONSTRAINTS.md` §(h).
  **Still open:** D-9 paired branches (b) `train_late`, (c) `train_missing`,
  (d) `train_stats_differ` carry a stale pre-c5 `INSTRUMENT_UNSUPPORTED` label and need
  recalibration; they guard TRAIN displacement by non-banana routes.
  ~~⚠ **New top item in the bite-test audit:** the rule rests on the *least-verified* of the four
  branches — row (a) is `UNPINNED` with **D9-M1/M2/M3 all SURVIVED**.~~ **RESOLVED 2026-08-12:
  row (a) was already pinned by claude_1 on 2026-08-10 (`80c3dd63`, 4/4 mutants caught, zero
  survivors) — the handoff was filed under the phase1-work-allocation task id and sat
  unintegrated for two days; integrated to trunk 2026-08-12. The rule is now policed by a
  detector that demonstrably fires.** Caveat kept explicit: (a) is pinned on *implementation
  validity*; its *applicability* still reads `INSTRUMENT_UNSUPPORTED` (proxy retired) — whether
  the c5 instrument can observe the policed behaviour is a separate open question, and **(b)–(d)
  recalibration is parked on that same c5 instrument ruling — OWNER-ASSIGNED 2026-08-12 to
  `claude_1`, sequenced after G6** (message `20260812T073000Z…-c5-instrument-ruling-assignment
  -policy.md`; fixturing them before the ruling would test a measurement the instrument cannot
  make).
  **Consequence for CBF:** any banana farm that plants while `own_units == 1` is rejected
  outright, regardless of later score. Check the `DENY → FARM → WOOD` machine's entry condition
  against this before implementing.

## P0 — MEASUREMENT: the noise band (opened 2026-08-10)

- **σ MEASUREMENT ✅ DELIVERED 2026-08-13 — pooled within-source SD = 1.501, CI
  [1.049, 2.634] (14 mature obs / 10 d.o.f.; resident family n=6 spans 5.13).** The
  ±0.5–1 band is dead; a ≥+1.0 gate now needs 5 runs/arm. Campaign: 4 runs executed
  (runs 3–4 under claude_1's VM lease, ended on handoff), registry appended via
  manifest, integrated to trunk; **codex_1 review DELIVERED 2026-08-13 — repair accepted, numbers
  reproduced, one wording correction applied (1.501 = combined operational variability;
  no variance/drift inequality established). TASK CLOSED.**
  Full statement: `docs/STATE.md` §3; review
  `codex_1/reviews/arena-noise-band-measurement-review-2026-08-13.md`.
  `coordination/tasks/20260810-arena-noise-band-measurement.md`. Original framing (kept for
  the record; the blocking question below was answered before spending, as demanded): The owner removed the
  noise-band gate on candidates 2026-08-12, which makes measurement throughput the binding
  constraint and σ the number every promotion argument rests on. Already measured from existing
  data by `cgauto/arena_noise_band.py`: **pooled within-source SD 1.098, CI [0.707, 2.418]**,
  4 families / **10 deployments** (corrected 2026-08-10 from a first pass that counted 13
  observation rows, three being second checkpoints of one run — a unit error in the tool written
  to quantify unit errors). The ±0.5–1 band was understated, modestly. **Question 1 answered at
  zero Arena cost: 10 distinct deployments of 4 byte-identical sources produced zero duplicate
  scores, so the platform does not seed from the source hash and re-submission draws a real
  sample.** **What is still unknown is the decision-relevant part:** all
  13 observations are *blocked in time*, so within-source variance and ladder drift are
  permanently confounded and no number of additional blocked runs separates them. Only
  interleaved A/B/A/B does. A mature read now costs **~2 h**, not days. At σ ≈ 0.96 an A-vs-B
  difference needs 10 runs per arm for SE 0.5. **Blocking question before spending anything:
  does re-submitting an identical source draw an independent sample, or does the platform seed
  from the source hash?** If the latter, Phase 1 measures nothing. No Arena action authorized.
  **Consequence for everything below:** every closed experiment here was judged against a gate
  in score points (±0.5, ≥+1.0, ≥+2). At σ ≈ 1.10 a single mature read cannot resolve any of
  them (difference SD 1.55 at n=1 per arm). This does not reopen past calls; it determines whether future ones are decidable.

## LIVE PRIORITIES — iteration 2 (formed 2026-07-29, post-audit-sweep)

Iteration 1 (H1/H3/H5/H8/H13 + the review cycle) closed five hypotheses in a day and
produced one experiment (D176a, subsequently closed at mechanism/value). Its most
consequential output was not a
candidate but a **re-baselining**: H13 found that at most ~1 point of our 2.94-point gap to
yamo is attributable to code, while the documented fresh-vs-mature score effect is 3–4
points. **If that holds, our true code gap to the 28.22 bar is roughly 2.5–3.5, not 6.46** —
which changed what was worth measuring. **N1 has now settled the premise against passive
maturity:** remaining uplift −0.1612 with CI [−0.7525,+0.4567]. Iteration 2 therefore
continues with construction and rating-dynamics measurement, not waiting.

### P0 — re-baseline (cheap, read-only, and everything downstream depends on it)

- **N1 ✅ DONE — PARTIAL / IMMATERIAL.** Seven snapshots provide 41 within-agent age-bin
  crossings with stable exact identities and snapshot/agent fixed effects, but lifetime
  battle accumulation remains censored. Resident remaining uplift is −0.1612, CI
  [−0.7525,+0.4567], projected mature score 21.3088. The upper edge is only 0.0433 below
  the frozen +0.500 cutoff: close passive maturity as a planning lever, but do not claim a
  high-margin negative aging effect.
- **M1 ✅ DONE — PARTIAL / DESCRIPTIVE_ONLY.** Source coverage is broad (8,014
  hash-verified games; 307/329 complete score transitions across 45 agents), but the best
  held-agent Elo-like update model has MAE 0.477313 versus a 0.478583 zero-change
  baseline. No wins-per-+1 or terminal-margin-to-rating conversion is defensible.
- **N2 ✅ DONE — B4_4_CORRECTED.** The original report/manifest is absent; the tracked
  8,131 cut fails its anchors, while a unique inferred 8,395 prefix matches 25 peers/2,787
  occurrences. Group medians 191.5/29/21 and pooled reap 0.928%/15.322%/17.198% reproduce,
  but per-agent first-plant spans 3–254 and four peers do not exceed the resident's reap
  rate. Every group has a near-universal self-plant→self-chop wood loop. Crop outcomes
  directly confirm the owner's distinction: early crops can be repeatedly harvested,
  while post-250 crops are predominantly fruit-to-wood conversions. Cite only the N2
  corrected result, not B4.4's “all/every peer,” no-loop, or causal-survival wording.
- **M2 ✅ DONE — NO_ACTIONABLE_MATCHUP.** Of 72 exact opponents, only R1FA,
  BoatBuilder, and a76a44 clear current-identity, games, seats, and matched-control
  support. R1FA's stable −31.62 matched-margin hint is imprecise (CI
  [−81.02,+22.24], Holm p 0.229) and has only −0.087 win residual. BoatBuilder reverses
  by seat; a76a44 is positive. Do not build identity-specific behavior; retain R1FA only
  as a surveillance hint pending more exact games.
- **M3 ✅ DONE — NO_ACTIONABLE_SEAT_ASYMMETRY.** Raw and same-opponent matching both
  point toward seat 0 being worse, but the matched seat-1-minus-seat-0 margin is only
  +10.09, CI [−16.81,+38.91], p 0.484. The identity-equal fixed-opponent contrast flips
  to −1.37. No seat-specific mechanism or branch; repeat only with a larger exact panel.
- **M4 ✅ DONE — NO_MATERIAL_MATCHMAKING_DRIFT.** Newest-minus-oldest-60 mean opponent
  score is +0.438, CI [−0.865,+1.867], p 0.884; median is −0.155. Strength drift is not
  established. Composition is highly concentrated: newest 60 = 47 FreZzz, 7 Bubaptik,
  5 goq, 1 IlyaPol, represented by 16 exact IDs but four pseudonyms. Surveillance must
  report both exact-ID versions and pseudonym lineages.
- **M5 ✅ DONE — NO_MATERIAL_LENGTH_ASSOCIATION.** Turn-300 games are 125/241. The
  97-target matched cap residual is −1.44, CI [−26.25,+25.11], p 0.710, while win
  residual is +0.184. Seats, time halves, exact/pseudo sensitivities, and lineage
  omissions reverse signs. H3's narrow cause-versus-symptom gate remains; there is no
  resident-wide duration-conditioned policy lead.

### P1 — next build and bounded audits with a decision attached

- **A2-1. Economy skeleton — ✅ CLOSED / FAILED K1.** The policy creates and reaps an
  early orchard, banks 127,614 unambiguous own bill-fruit units, and mines without iron
  detours, but locked confirmation reaches fruit-funded worker 3 by t≤110 in only
  **28.42%** of tasks versus the frozen 40% floor. Development's 40.23% did not transfer.
  All integrity gates pass; no retune and no A2-2. Canonical record:
  `coordination/tasks/20260730-a2-1-economy-skeleton.md`.
- **N3 / A2-0a ✅ DONE.** The corpus found a sub-critical, labor-limited crop base rather
  than reliable population-level self-replacement. That does not kill A2: top-5 converts
  the depleting endowment into worker 3 in 75.6% of games by median turn 106 and worker 4
  in 41.6% by turn 137; self-planted currency supplies 37%/50% of the bills. Those numbers
  define A2-1's gate above.
- **N4 ✅ RUNTIME_CLOSE.** Exact resident pair reconstruction, generated Cargo, frozen
  commands, and 1/20-thread normalized parity pass on the one-root pre-lock diagnostic.
  Exhaustive candidate export plus one-tick boundary reconstruction costs 210.408 ms p95
  single-thread and 333.157 ms under 20-thread contention versus the frozen 5 ms close;
  one root emits 268,168 rows / 83.3 MB. The full projected 10.7 GB census was stopped.
  No Phase B, compact-format retune, pair pruning, or alternate boundary definition.
- **N5 CORRECTED / RE-REVIEW PENDING — NO_MATERIAL_CONTEST_OPPORTUNITY.** Exact lineage reproduces H13:
  388 resident targets in 78/170 endgame-reaching games versus yamo's 205 in 37/103.
  Opponents extract 1,487 carried score-equivalent units versus our 241, and we contact
  only 51/388 targets. But even the generous deny-plus-capture factor-two ceiling is
  **11.99 per all resident games, CI [8.73,15.76]**, below the frozen 20-margin gate.
  Enemy units can share cells; this cannot body-block. Twelve semantic tests pass and
  literal post-birth ETA leaves the primary value unchanged; await narrow re-review.
- **N6 ✅ INDEPENDENTLY ACCEPTED / CLOSED_AT_DEVELOPMENT.** The exact 450/900/1800 sweep completed G1 once.
  LOW is −0.754 margin and negative in both seats; HIGH is only +0.559 with four positive
  families. Both fail the directional mechanism sharply (15/97 and 12/77 versus 60%).
  Confirmation maps remain unused. Keep 900 and do not retune the scalar.
- **H3′ ✅ DONE — TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY.** Exact D159
  contains 77 scaled and 123 no-scale games. Same-seat pregame matching supplies 70
  complete 50-turn pairs over 29 identities: contact-hazard DiD ratio 0.606,
  CI [0.410,0.895]. Sixty-nine pairs remain entirely before permanent loss and give
  0.510, CI [0.293,0.841]. Every support, balance, and materiality gate passes, but the
  event is observational and may proxy broader opponent state.
- **H3a — SOURCE RECONSTRUCTION ✅ TREATMENT_REPRODUCIBLE.** The exact archived Phase-21
  dual-value treatment `083107f5...` is a deterministic seven-edit transform of fallback
  `a8eb3b2b...`; inverse and archived-generator equality pass, total delta +1,811 bytes,
  and both exact sources compile. A separate protocol must preserve three arms:
  workforce-pressure-conditioned treatment, the identical treatment always on, and
  unchanged control. No runner arm, range, panel, candidate, or Arena action yet.
  **All-agent full review completed:** H3a is the sole surviving ranked route, but the
  conditioned source, equality bridge, value runner, and multi-game trigger-preflight
  package did not exist at review time. The exact 17-game public-frame and 5,100-decision
  reconstruction packages now exist; Claude accepts them for retrospective Phase A2 only.
  Literal gate-4 analyzer/tests remain pending. The locked substrate's 213 numeric-fruit alias
  crashes, continued-RNG divergence, and empty `MSG ;` incompatibility block Phase B/C until
  fixed. Endgame
  removal race and WAIT are rejected from the ranking; B3.14 remains measurement-only.
  Reconciled PDF: `docs/reports/2026-08-02-top-player-all-agent-analysis.pdf`.
  **Owner-priority unblock assigned to `claude_1`:** cheap exact-17-game trigger preflight
  first; on pass only, freeze/build C1, equality bridge and three-arm runner, then one
  6,144-task development panel. Estimated 4–8 hours to the stop gate, 3–5 working days for
  the full path. Task: `coordination/tasks/20260802-h3a-conditioned-value-unblock.md`.
- **F1 — READINESS AUDIT REASSIGNED TO `codex_1` 2026-08-12** (released to `chatgpt_1`
  2026-07-31, never claimed; that agent is out of reach). Use only legal public state history,
  whole-map-root folds, turn 40 as primary, fixed linear/centroid models, and
  command/label deletion plus static/permutation/seat controls. N4 is closed, H3a is
  integrated, and the exact A2-0b artifact hash was reverified before release. A
  classifier alone never authorizes adaptation.
- **H11 ✅ DONE — DECOMPOSED_NO_GENERIC_TASK.** Generic map-conditioned configuration is
  closed by D63/D64 and D91. E7a and S2 preserve the only named map-conditioned children
  under their own representation/value gates; F1/H3a/H10a/N4 are behavior or current-state
  tasks, not map classes.
- **H11a PARTIAL / PAUSED — OWNER-DIRECTED INITIAL-STATE SECTOR PREFLIGHT.** All three protocol
  agents will independently test whether the joint starting-resource vector and
  pre-command map configuration can identify a sector where one exact finite behavior
  change has incremental terminal value. This does not reopen generic “rich map → train”
  selection: D63/D64, Phase 15, D91, H1, A2-1, and H11 remain binding. A positive audit
  must compare unchanged, identical-always-on, and sector-conditioned arms; use
  outcome-blind features and root-grouped held validation; beat the best static arm; and
  price displacement/opponent leakage. Task:
  `coordination/tasks/20260802-initial-state-sector-policy-audit.md`. ChatGPT's early
  improved E7a handoff is measurement-only. Exact jobs-1/jobs-8 payloads were recovered into a
  trace-free 360-row delta table; ChatGPT owns no-fit pricing of the frozen rule. Claude/local
  work remains paused behind the owner-priority H3a unblock.
- **E1 ✅ CLOSED WITH N4 RUNTIME.** “Opening never audited” was false: the complete
  first-worker grid, fixed prefixes, terminal turn-one rollout, recurrent portfolio, and
  one/two-batch sequences already exist. Only a terminal-valued multi-turn sequence over
  exact resident candidate pairs survived scope review; N4's exhaustive surface is
  runtime-closed, so no authorized prefix oracle remains. A future compact publisher would
  be a new reviewed protocol, not an N4 retune.
- **E2 ✅ DONE — ROUTE_RESIDUAL_OBSERVED / NO EXPERIMENT.** Across 11,260 confirmed
  deposits, immediate door ETA, joint two-carrier assignment, and door persistence are
  clean. A future-conditioned alternate door saves exactly one movement turn in 134/10,597
  next-target-bound wood returns: 0.335 turn per side-game, maximum one per episode. This
  is not causal score/rating evidence and does not justify a policy cycle.
- **E3 ✅ VOID_PREMISE_DUPLICATE.** The resident has no stored tree sequence, but this
  question was already tested at a stronger level: exact-resident `FELL_BANK` terminal jobs
  and D36's repeated joint completion-boundary oracle enumerate tree targets, let other
  trees grow under exact continuation, and execute multiple bundles in 87/128 tasks.
  D36 gains +10.633 margin versus its +25 upper-bound gate and explicitly closes further
  resident target/overlay iterations. Do not reopen with cluster or depth definitions.
- **E4 ✅ DONE — KEEP_LEXICOGRAPHIC.** A comparator-only audit exhausts all ten reused
  equal-best secure-orchard mother seeds against all six frozen opponents in both seats.
  The tie is active on 10/10 seeds and all families, but reversing it loses −8.55 margin
  conditional on tied maps and −0.0855 across the exact 1,000-map census. Both seats and
  all six family means are negative. Keep the current comparator; no candidate or Arena.
- **E5 ✅ DONE — KEEP_RIPENESS_WAIT.** Removing only the on-site zero-fruit candidate
  activates in 33/360 cells across both seats and all six families. It gains only +0.1056
  whole-panel margin; seat 0 is −0.200, motion/race are negative, and 346/360 cells are
  unchanged. The +1 magnitude and both-seat gates fail. Keep the current wait.
- **E6 ✅ VOID_PREMISE_DUPLICATE.** D167 classifies seed acquisition (135/135 local
  BANK_SEED; field 67.5%; pre-carry 40.5%), and D168 causally tests post-return/pre-carry
  with a frozen species rule: −6.732/−8.207, all active families negative. `DROP` is
  generic banking, not selective seed disposal. Do not retune species, horizons, or carry.
- **E7 ✅ DONE — HINDSIGHT_RESIDUAL_ONLY.** The exact one-site LEMON/PLUM inversion
  activates all 360 reused cells but loses −12.174 margin, with both seats and all six
  families negative. Choosing once per seed after six-opponent averaging gains +10.510;
  24/60 seeds prefer FLIP, both selected-policy seats are positive, and every
  leave-one-family-out evaluation remains positive. Keep the current default. **E7a is
  MEASUREMENT_ONLY:** the exploratory sign rule marks 13/60 roots (10 TP / 3 FP), while the
  primary ridge gate fails at 55% precision. The original exact delta magnitudes are now
  compactly recovered; price only the already frozen rule without fitting or retuning. Do not
  confuse mechanical readiness with value: exact candidate `97bfe71e...` now compiles, passes
  4/4 construction tests and a 16/16 inside-FLIP/outside-control bridge, but remains unqualified
  and `arena_authorized: false`. Do not touch Arena without a separate owner/controller decision.
- **S1 ✅ DONE — FULL_EXACT_INFEASIBLE.** In 720 reused control games, 34.17% reach
  turn 251 and 21.53% reach 291. Exact movement-only simultaneous one-ply outcomes are
  median 600/max 6,400 overall and median 450 at t291, so first-ply size is not the sole
  blocker. Full exactness still spans 10–50 turns and adds opponent, chance, plant,
  resource, and non-MOVE branches. Known-policy `BotSession` processes cannot clone;
  restricting to resident candidates duplicates N4/D36/S3. Close S1 under the current
  representation; reopen only with proof-preserving full-game state reduction and an
  exact referee chance model.
- **S2 DEPENDENCY_GATED_REPRESENTATION_BLOCKED.** The complete first-worker grid,
  opening macros, terminal turn-one rollout, fixed source prefixes, recurrent portfolio,
  and one/two-batch sequences are all closed. The only surviving action/value object is
  E1's multi-turn resident candidate-pair prefix, which is not enumerable until N4 Phase A
  is accepted and has no terminal value until a separate E1 oracle runs. Independently,
  D63 (AUC 0.830→0.479), D91 (5/16 map support), Phase 15 (best map-only forest 47.059%
  precision / −0.277), and D153 (+14–17 train→+1.820 held, 44.44% harmful) supply no
  accepted pre-action map representation. Keep S2 gated; no sequence enumeration, feature
  fit, panel, book, candidate, or Arena action.
- **S3 ✅ DONE — DISTINCT_MULTI_GATED.** Putibuzu's public shape combines about 30 joint
  task/local-action candidates, values averaged at depths 3/5/7/9/12, a three-ply
  `5→3→all` beam on large maps, and explicit-opponent maximin on small maps. That full
  combination is outside Phases 3–8/11/16, D36, and D84, although its individual pieces
  overlap them. It is not reproducible from the prose: evaluator weights, candidate/tie
  rules, beam semantics, map cutoff, opponent breadth, and chance handling are missing.
  Our model substrate also fails transfer (rollout candidate 21.7 vs 24.1 control; robust
  29-option selection inert), while exact-resident subsets cost 92.852–130.047 ms p95.
  Runtime remains only provisional for a new lightweight policy because the GoldElite
  subset reached 28.53 ms p95. **S3a is peer/N4-gated:** first choose exact resident-pair
  overlap versus a clean-room new controller and qualify specification/latency before
  value. No simulator, source, panel, candidate, or Arena action now.

### P2 — hygiene and consequences of iteration 1

- **N7 ✅ DONE — DEPLOYMENT_ALREADY_SLIM.** Independent constructor tracing confirms
  `ScarceIntent`, banana factory, task market, and opponent-crop scoring are unreachable
  from `main()`. All four already have zero occurrences in the 62,725-byte live deploy,
  making the additional deletion ceiling exactly 0 bytes. Do not edit the sacred source:
  it is byte-identical with the D171a snapshot, library-visible as `resident_policy`, and
  retained by direct experiment callers/tests. No cleanup patch or successor.
- **H7′ ✅ DONE — NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE.** Mechanically exact
  contention occurs in 180/200 D159 games, including 3,662 dual CHOP turns and 598
  duplicated wood units. Top-20 event prevalence is only +5.76 pp over rank-41+, with
  opponent-identity-cluster CI [−1.64,+14.49], and the strong turn rate is lower
  (47.87 vs 78.93/1k). Close without a controller; body-blocking remains impossible.
- **D176a ✅ CLOSED-AT-MECHANISM 2026-07-29 — oscillation line closed permanently.** The fix
  largely worked (incidence 8.50%→2.88%, below yamo's 2.9%; zero de-novo; all six value gates
  pass) and is worth **+0.045 overall** — not a promotion cycle. Two of the four mechanism
  sub-gates were mis-specified by the integrator (worst-case anchored to a real-corpus figure
  the panel control misses by 12×; displacement gate cannot distinguish fragmentation from
  manufacture) — recorded in CONSTRAINTS as gate-design rules.

### P3 — owner programmes

- **H2 / A2 Architecture-2 — ✅ STOPPED AT PHASE-1 K1.** A2-0a established the target,
  A2-0b qualified the referee substrate, and A2-1 built the first new policy. Its clean
  28.42% confirmation misses the 40% workforce-conversion floor, so the charter stops the
  programme. A2-2…5 are not backlog items without a new owner authorization.
- **H10a readiness ✅ NARROWED_TO_GENERIC_SPATIAL_AUGMENTATION.** The existing
  104-channel Level-1 tensor is not a generic board extractor: 32 channels require one
  selected curriculum unit, target recipe/deficits, episode progress, or previous
  primitive action, none uniquely defined for D172's 13 global macro options. The exact
  substrate is usable: 79,997 labels / 27,392 official-map state keys, zero duplicate
  state/arm keys, and a deduplicated 72-channel table would be 477 MB. **H10a-r1 is
  peer-gated:** player-relative 72-channel current state plus the unchanged D172
  17-field decision block, example model 6,541 params, all D172 arms/τ/partitions/gates
  frozen. Exporter parity must pass before fitting; no bulk/model/job exists yet.
- **H10b whole-policy learner** remains a larger owner programme. H5's #1 finisher
  (delineate) used a trained NN with no search, but that does not turn H10a's narrow
  option selector into authorization for self-play over primitives.
- **H10b-r1 search-teacher distillation — OWNER-REQUESTED PROGRAMME CONCEPT;
  CHARTER NOT YET FROZEN.** Adapt AlphaZero-style expert iteration rather than copying it
  literally: an expensive offline search teacher produces dense policy, expected-margin,
  and catastrophe targets against a population of opponents; the student is evaluated
  closed-loop, and search relabels states that the student itself visits. Pure symmetric
  self-play and one-pass teacher-state imitation are excluded because ladder transfer and
  autoregressive covariate shift are already demonstrated risks. The Arena artifact is a
  compact, search-free int8 network; training-time search does not inherit the 50 ms turn
  budget.

  This is distinct from H10a-r1's 13-option spatial scorer, L1's replay-only primitive
  labels, D170b's sparse terminal-reward option training, and S3's proposed online
  rollout-plus-beam controller. It directly instantiates the new dense-counterfactual-credit
  plus new-representation route left open by D170b/D172a. Positive priors are D169a's
  +10.671 hindsight envelope, the field evidence for both neural policy and lookahead, and
  the solved sub-100-kB int8 deployment pattern. Main risks are opponent-model transfer,
  combinatorial simultaneous joint actions, search cost, and loss of value during
  distillation.

  **Planning prior only, not an empirical result or acceptance gate:** 50–70% chance that a
  bounded search teacher shows material local improvement; 25–35% that a compact student
  clears closed-loop local gates; 10–20% that the first programme yields an Arena-worthy
  candidate. This makes a bounded feasibility phase worth doing, not a large training run
  worth starting blindly.

  Before any fit, range, or bulk job, freeze a charter with: (1) exact referee/search
  determinism, legality, chance, and joint-action semantics; (2) a warm start and
  population-conditioned opponent protocol; (3) fresh unsealed official-map development
  and held-family teacher-value gates; (4) iterative student-state relabelling and a
  closed-loop student value-retention/tail-safety gate; and (5) deterministic int8 source
  at ≤100 kB and warm p95 <50 ms. No model, compute job, candidate, TestSession,
  submission, or Arena action is authorized by this backlog entry. [owner direction,
  2026-08-01]

### Designed, not started — carried forward (iteration 2 closed 2026-08-07)

- **CBF conditional banana farm — DESIGN COMPLETE, OWNER-SPECIFIED, NOT IMPLEMENTED.**
  Full spec: `docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`. A
  three-state machine `DENY → FARM → WOOD` with both transitions latched: farm the D89a
  seed factory once `opponent_trolls > 2` latches (the resident's existing denial abort,
  which today has no destination and falls back to undifferentiated wood), then abort to
  pure wood if the opponent out-collects our bananas. Acceptance is **behavioural per owner
  ruling 2026-08-07** — G1 trains worker two, G2 denies one of lemon/plum, G3 establishes a
  sustained orchard, G4 aborts on the banana test *and does not fire when it should not* —
  plus G5 byte-identity on non-triggering games and G6 monotonicity (including that the
  denial bonus never re-enables after DENY is left; it is gated inline on the live troll
  count today, §3.0 of the spec).
  - **Why it is shaped this way:** D89a is the only banana mechanism that ever worked at
    scale here (+79.441 margin, CI [+40.991,+117.892], 252/256 sustained loop, catastrophes
    26 → 11) and failed on **four** value gates, not one — worst opponent-family −6.938
    (bar −5), p10 −72 (bar −20), worst −235 (bar −60), opponent delta +82.863 (bar +1). The
    last is superseded by the owner's delta ruling. The design does not repair D89a's leak;
    it bounds exposure by farming only in games already being lost. If the opponent never
    reaches three trolls the bot is byte-identical to the resident.
  - **Recorded risk, owner-accepted, and CORRECTED 2026-08-07:** this entry originally said the
    banana-collection sensor watches theft (+12.453) rather than the dominant leak (+76.508 from
    the opponent's own crops). **That split is UNRESOLVED, not measured** — it is prose in the
    D89a result `.md` with no committed data behind it (`claude_1`'s scoping re-derivation;
    verified by me — the discovery JSON has no such fields and the per-task TSVs were never
    committed). `+82.863` itself stands. The residual risk is weaker: the test only sees
    bananas, so a farm could pass G4 and still lose as D89a did. A margin-based abort on
    `view.scores` costs the same and is the named variant.
  - **`claude_1` verdict 2026-08-07: `NOT_REPAIRABLE`** (second review reassigned to `codex_1`
    2026-08-12; `chatgpt_1` out of reach). D92's
    trained-only isolation ran 898 opponent-crop selections against D89's 166 — 5.4× the denial
    dose, starter unchanged — and opponent score moved **+0.188 upward**; `gold_adaptive` family
    delta is **208.78**. It recommends **neither** route enter Phase 3 before a read-only check
    and measurement repair. Does not block this design, which never assumed the leak was
    repairable, but weakens the case for entering FARM at all.
  - **Boundary:** behavioural gates deliver a bot, not a promotion. Mining hit 100% trigger
    fidelity at −10.76; B3.13 passed every local gate and scored 11.96/rank 111 live. Arena
    still requires a `QUALIFIED` frozen-protocol verdict and gain above the ±0.5–1 band
    (`docs/STATE.md` §3). Passing G1–G6 authorizes no submission.
  - **Reopens nothing:** N6 closed the denial weight ("keep 900"), H4 closed denial as bill
    prevention (`NO_MATERIAL_DENIABLE_BILL`, strict rate 0.0; 43/73 mandatory batches are
    IRON), D176a closed oscillation. Supporting audit:
    `data/analysis/live-agent-6553250/resident-denial-scoring-audit-2026-08-07.md`.
  - **Next step when resumed:** implementation plan, three stages — inert machine plus its
    byte-identity and monotonicity checks first (proves the plumbing changes nothing), then
    graft the farm, then the abort. Not started; no task record, no D-series id, no branch.

### Operations

- **H9 submission timing** — passive-maturity timing is closed by N1. Future timing is the
  ordinary qualified-candidate promotion problem and runs only inside
  `docs/PROMOTION-RUNBOOK.md`.
- **H12 surveillance** — cron 05:17 running; weekly comparative refresh with explicit
  triggers. **B5.3** cold-file migration ripens ~2026-08-03. **B0.3 no-churn** absolute.

### Closed — do not re-propose (see CONSTRAINTS for the decisive numbers)

H1 (economy package, −2.49 own-side-only), H2/A2 (Phase-1 K1, 28.42% vs 40%),
H3 (quartet edge dissolves), H5 (done), H6
generic rollout (narrowed to N4), H7/H7′ (body-blocking impossible; real contention is
ubiquitous but not a strong-cohort signature), H8 (worker-2
at the floor), H11 (near-closed, D63/D91), H13 (done → D176a), N6 scalar tuning, plus the
eight routes of the 2026-07-29 terminal synthesis.

*Everything below this line is the historical record (tiers as they were run, verdicts
inline). Do not re-rank it; it is the evidence base for the priorities above.*

## Tier 0 — free points and standing discipline (no code)

- **B0.1 ✅ DONE 2026-07-27** — passive read: resident 43/110 @ 21.97 (203 battles), bar
  MSz 28.22; 198 new replays, QA clean. **Key finding: the score is source-side frozen
  since 07-23 (no ladder recomputation; 6 battles in 4 days) — the passive-maturity lever
  is much weaker than assumed. Code strength must carry essentially the whole +6.25 gap.**
- **B0.2 ✅ DONE 2026-07-27** — cleanup executed (SDD, all reviews clean): 22 worktrees
  removed, debug cache cleared + cap rule, 683 files / 1.04 GB migrated + symlinked, YT
  dead dir removed, 425 MB mirror uploaded md5-verified. Repo 23.5 → 2.76 GB.
- **B0.3 No-churn rule stays absolute** — no arena write until a candidate passes the
  promotion protocol (B4.1). Every failed trial costs ~2–4 points of standing for days.
  [class (g), fresh-vs-mature]
- **B0.4 ✅ INSTALLED 2026-07-28** (authorized under owner decision (b)): daily cron
  05:17 → `data/scripts/collect_wide_cron.sh` (marker `# troll-farm-wide-collect`;
  removal = delete that line via `crontab -e`). Driver committed (`b15a75f`) with
  offline failure-path tests; live test run: +9 games → 8,131 cumulative, QA clean.

## Tier 1 — declared next experiments (cheap, bounded, evidence-backed)

- **B1.1 ✅ DONE 2026-07-27 (D167a)** — acquisition paths ARE regular: **BANK_SEED
  frozen-eligible** (135/135 local; 71.4% top-5 field, 4/5 agents, both seats; all frozen
  gates passed, no tuning). OPPONENT_DERIVED closed as a class. Bonus discovery: top agents
  pre-carry seeds through suppression (22/49 cycles) — the resident never does (0/1,024).
- **B1.2 ✅ DONE 2026-07-27 (D168a) — kill rule fired.** Both bounded BANK_SEED options
  failed value decisively (post-return −6.73 [−8.40,−4.08]; pre-carry −8.21; worst
  family −17.11) with mechanism and integrity fully clean. **Hand-written successor
  controllers are closed**; the motif enters B2.1 as a rollout-valued option only.
  Bonus fact for B2.1: carry is empty at 100% of P→S entries — pre-carry preconditions
  never arm on resident trajectories. Tier 1 is complete. [D168; vol 2]

## Tier 2 — the big bet: resident-native options + closed-loop learning

The only levers with measured headroom ≥ the gap are hindsight oracles over
option/joint-assignment spaces (D97 +36.9; D107 four-use +35.2; D144 combined +42.6;
D152 exact-second +36.8 on actives; D162 resident-native envelope **+12.7 [+9.0,+16.3]
with zero regressions**). Every *offline* selector over them failed (best D142b +3.06,
under bar); the never-executed branch is closed-loop optimization on the **resident**
substrate with a family-robust objective (skipped-D109 question, D157 audit; D158's
invalidation was substrate-only). Prereq chain, each gate preregistered:

- **B2.1 ✅ DONE 2026-07-27 (D169a) — PASS, gate cleared cleanly.** Envelope over
  {OPT_RETURN, 3× D163 resource options, all ± B3.1-trigger arming}: **+10.671 mean,
  CI [+9.420, +11.922], 65% improved, 0 regressions**, tails better than control, 100%
  coverage. Every option negative always-on — value is pure per-game selection. No
  D169b needed (all six PASS conditions held on the first pass). *(The one-time Fable
  STOP for D170 authoring was satisfied 2026-07-28; no pause is in force.)*
- **B2.2 / D170a history — IMPLEMENTATION-INVALIDATED; D170b COMPLETED BELOW.** D170a
  protocol frozen (Fable) → Phase 1 trained 8 fits → resume validation exposed a
  structural trig-arming bug in the new composition code → **CLOSED-AT-PHASE-1
  adjudicated as implementation invalidation** (no value ever computed; frozen vocabulary
  intact) → **D170b** mechanics-only repair protocol frozen and executed (repair +
  activation verification + offered-conditional exploration semantics; all science
  inherited). Chain: `d170a-...-protocol`, `d170a-...-result` (the invalidation record),
  `d170b-...-repair-protocol`; accepted D170b closure is the next bullet. Four-objective comparison (the skipped-D109 question) →
  LOBO admission/selection → veto → sealed confirmation → int8 deployability → 🛑 user
  arena gate.
  Recurrent policy over the B2.1 options with exact-resident action zero; objective =
  paired margin with group-DRO/worst-family term and own-score protection (D109's
  rotation, r=−0.014 across panels, is the failure this objective targets). Selection by
  independent-block leave-one-out only (D134 — fit statistics anti-predict transfer).
  **Gates:** same-panel dominance over exact resident (D158 rule); fresh-block +≥2 with
  all families ≥ −1; latency p95 < 50 ms in the deployable form (V5 buffer pattern);
  ≤100 kB source. **Kill:** two consecutive objective variants fail fresh-block → close
  the program and hold at Tier 0/3.
- **B2.2 ❌ CLOSED 2026-07-28 (D170b, kill rule fired on valid mechanics).** 8/8 fits
  trained; 0/8 admitted — all four objectives converged to always-KEEP (P(invoke) ≤3.3%);
  sampled-invoke value −1.0..−2.3. The envelope's positive contexts are unlearnable by
  on-policy terminal-reward training at this (or any sane) budget; objective choice
  irrelevant in this regime. Tier-2 CLOSED; project holds at Tier 0/3. Successor
  (dense counterfactual credit) = new program, owner authorization required. [D170b]
- **B2.3 — moot** (gated on B2.2, which closed).
- **B2.4 ❌ CLOSED-AT-SELECTION 2026-07-28 (D172a) — the definitive Tier-2 closure.**
  Signal abundant (40.4% of 27,392 states carry ≥+2), labels exact, states
  on-distribution — and held value only +0.14..+0.26 for both function classes. The
  positive contexts are not identifiable from current observables (CONSTRAINTS ★FINAL).
  Tier-2 is closed on the strongest possible evidence; sealed block 9,862,000–063 and
  the veto discipline preserved. Residual for any future owner decision: spatial-plane
  observations on the official substrate (never retried post-D33).

## Tier 3 — execution-class diagnostics (historically the only transferrers)

- **B3.1 ✅ DONE 2026-07-27** — signature replicates independently (19/192, 57.9% of
  negative mass); the endgame switch has NO coverage bug (fires at the earliest turn its
  behind-AND design permits; retuning closed — CONSTRAINTS §(f)). Surviving output: an
  observable early-warning trigger — opponent scaling past 2 workers precedes the
  crossover by 42–125 turns in 84% of catastrophes (83% of mass). **Feeds B2.1 as an
  activation-conditioning signal**, not a switch retune.
- **B3.2 ✅ DONE 2026-07-28** — motion audit clean at 4× scale (49,977 moves, zero
  failures, replicating 07-16). **One concrete candidate found → B3.4.** Context: 29
  first-seen agents include qualitatively new scaling (Pafin: 5 workers in 48% of games)
  and denial styles absent from the local panel.
- **B3.3 ✅ DONE 2026-07-28** — BANK_SEED (67.5%), pre-carry (40.5%), catastrophe
  signature (9.8%, lead 74.4 turns) all stable; **D164's top-5 motif population rate
  corrected 72% → 49.7%** (sampling-completeness artifact; the frozen breadth+gap gate
  still passes, 5/5 agents, +38.9pp vs resident). CONSTRAINTS updated.
- **B3.4 — diagnosis ✅ (root cause pinned: memoryless detour tie-break,
  `yamo_orchard_live.rs:1505-19`; coverage gap in `force_unique_door_clear`); fix v1
  (D171a) ❌ CLOSED** — hard-forbid breaker under-cured long runs (45.7% vs 80%) and
  manufactured short ones (+117%, stale-arm design hole). Causality was modest anyway
  (2/18 suspicious). **Open successor option — D171b** (redesigned semantics: bounded arm
  lifetime + echo-stop disarm + ≤2 forced choices, or preference-based tie-break); cheap
  (all machinery exists), expected value small; promotion of any qualified successor
  needs a NEW owner authorization (the D171a standing grant never triggered and does not
  carry over).
- **B3.5 ❌ CLOSED 2026-07-28 (D173a + D173b)** — diagnosis excellent (missing HARVEST
  action class, 1,972 pts/9.62 per game lost), fix works on what it can reach (99.9%
  elimination among harvest-capable choppers) but 99.93% of the vein needs trained-unit
  harvest capability (`opening_options` hp:0) — strategy, not execution. Both variants
  also failed worst-family/catastrophe/tail gates identically: delaying wood for fruit
  has a real cost. **Successor is strategic and gated on B3.8's funding verdict** (does
  the fruit pay TRAIN bills? if no, the whole vein closes; if yes, a worker-capability
  protocol becomes justified). Original entry:
  — ripe fruit unharvested ≥3 turns with a capable worker nearby: 2,163 episodes in
  204/205 games, ~536 pts gross ceiling (~2.6/game), loss-enriched +15–20%, 91%
  independent of the closed oscillation vein. Plausible target-reassignment root cause.
  Pipeline: diagnosis (in flight) → bounded fix protocol → gates. The waste-sweep tool
  is now standing (`cgauto/waste_sweep.py`, commit 31b3ef0).
- **B3.6 ❌ CLOSED 2026-07-28** — `idle_with_work` sub-classified: ~78% benign/correct/
  detector-artifact, genuine ceiling ≤0.6 pts/game with no shared mechanism, flat across
  outcomes; round 2's "wood-race" flagship falsified (11% clean loss, ≤68 pts). No fix
  candidate. **Deferred chore:** gate the detector on free capacity (blocked while D173b
  uses `waste_sweep.py`).
- **B3.7 ✅ DONE — CONVERSION_BY_DESIGN.** Full corpus: resident 220 games / 2,433 crops,
  98.97% self-chopped, 0.90% self-harvested, 0.12% opponent-taken, 0% alive; 96.8% of
  self-chopped crops never bore fruit. Top five 200 games / 8,913 crops: 29.81% harvested,
  42.98% self-chopped, 15.71% opponent-chopped, 11.28% alive. All 220 resident trained
  workers have harvest power zero. Pacing fits the top cohort, not this resident.
- **B3.8 ✅ DONE 2026-07-28 — verdict (c) NO: the bootstrap is IRON-limited.** All
  uncollected fruit (ours + opponent's) would open a cheap-helper window in ~10% of games,
  balanced spec 0/205 ever; IRON limits 97.3–100% of failures. Owner's near-camp
  hypothesis CONFIRMED (1,144 events ≤2 from our door; 71.8% outside D173b's scope; 43.4%
  capturable in a ≤2-turn detour). Top-5 fund 66% of bills from earned currency, 76% fruit.
- **B3.9 ✅ DONE 2026-07-28 — verdict (A), the strongest lead in the project's history.**
  Mining is gated off entirely at workforce ≥2 (one call site, `own_units < 2`); 0.68
  iron/game vs top-5's 13.02; 98%+ of reachable iron unconverted at approach distance 0;
  no capability wall. Fruit+iron together: cheap-helper affordability 8.8% → **84.4%**,
  balanced 0% → **42.4%**. → **D174a frozen** (`d174a-opportunistic-mining-protocol-
  2026-07-28.md`): TRAIN-trigger preflight, opportunistic MINE candidate at workforce ≥2,
  mechanism gates including **worker-3 TRAIN in ≥25% of tasks** (control 0%), value gates
  retaining the family/tail floors both D173 variants failed. QUALIFIED → candidate at the
  arena gate (new owner authorization required).
- **D174a ❌ CLOSED-AT-MECHANISM 2026-07-29** — mining fix worked (iron ×10.6, fidelity
  100%) but worker-3 TRAIN stayed 0.0% even with the cap clause deleted, and value was
  −10.76 with all 8 families negative. **Two structural findings:** the bot is hard-capped
  by `can_train`'s `if n >= 2 { return false }`, and the REAL bill (`TUNED_CARRY`: PLUM
  6.23/LEMON 5.87) makes **fruit** binding, not iron — correcting B3.8/B3.9's synthetic-spec
  counterfactuals. Fix ordering is now: **planting (D175) → cap → (mining probably never)**.
- *(original B3.9 scope)* IRON acquisition audit + combined
  counterfactual — mining has never been audited. Measure our MINE behaviour vs the top
  cohort (rate, timing, iron-source proximity, missed reachable iron), then re-run the
  affordability counterfactual crediting BOTH uncollected fruit AND missed iron. This is
  the decisive test of whether the production+consumption coupling has ANY viable bootstrap
  for us. If iron slack is large → an execution-class mining fix becomes the top candidate;
  if not → scaling is structurally out of reach and the orchard must be justified by direct
  fruit value alone.
- **B4.3 ✅ DONE 2026-07-28 — the scaling destination is priced**: within-agent +48.2
  margin/worker (CI [44.1,52.7]); 2→3 = +1.9 rating, 3→4 = +3.3, 4→5 = none; resident wins
  5.0% vs 4+-worker opponents. **2→4 ≈ +5.2 rating = 84% of the gap.** Gated on B3.9.
- **B4.4 ⚠ SUPERSEDED BY N2 2026-07-30.** Its group-level first-plant and reap rates
  reproduce on a uniquely inferred cut, but its exact original provenance is missing and
  its “all/every peer,” no-loop, wood-purity, causal-survival, and ranked-mechanism claims
  are false or over-scoped. Use
  `data/analysis/live-agent-6553250/n2-b4-4-verification-result-2026-07-30.md`.
- **B4.5 ✅ / D175a ❌ CLOSED-AT-MECHANISM 2026-07-29** — "chopping always wins" pinned as
  the real gate (factory is dead/pruned code); the bounded early-planting fix moved first
  plant 199 → 13 and cost **−26.44** with Δopponent +21.09 vs Δown −5.41 and catastrophes
  229 vs 130. Third confirmation that production feeds the opponent more than us. Early
  planting CLOSED; do not retune.
- **→ Post-terminal direction menu: `docs/rank-hypotheses-2026-07-29.md`**, reviewed by
  chatgpt_1 (`docs/reviews/2026-07-29-chatgpt_1-rank-hypotheses-critique.md`, integrated
  2026-07-29). Working taxonomy after review:
  **audit-ready (parallel, read-only):** H5 postmortems, H3 no-loop quartet, H8 worker-2
  timing; **completed after rewrite:** H4 bill deniability and H7′ action contention;
  **needs rewrite/preflight before any work:** H6 (oracle-gap audit first), H11
  (near-closed, D63); **owner programme
  decision:** H2 architecture-2 (primary), H1 only as read-only joint upper-bound audit
  → staged Architecture-2 prototype (never the four-lever resident bundle), H10 spatial
  learner (sanctioned long shot); **operations, not hypotheses:** H9 (promotion
  prerequisite only), H12 (already-running maintenance). H7's original body-blocking
  premise remains falsified at `docs/mechanics.md:42-44`.
- **B4.6 ❌ CLOSED 2026-07-29 — no cycle warranted; the last lead is spent.** Mechanism
  pinned (`chop_candidates` is origin-blind throughput scoring; the gap is tree size +
  kind mix, with travel/contention/capacity all ruled out and our travel actually better
  than peers'), but the ≈54–73/game residual belongs to an intervention class that has
  already failed twice on this exact binary (−7.77 arena, −2.325 grid) plus a −61.7
  transplant against adaptive. **With this, the execution-class track and the whole
  improvement space for this architecture are closed** — see the ledger's TERMINAL
  SYNTHESIS. Remaining work is maintenance only; further gains need a different bot,
  which is an owner decision.
- *(original B4.6 scope)* suppression-efficiency diagnosis.
  B4.4 finding 3: we get **0.31 wood/chop vs peers' 0.43** and make opponent-crop contact
  on **41.1% vs 46.6%** of chops. Execution-class, aligned with the architecture's proven
  comparative advantage (denial), and structurally incapable of feeding the opponent —
  unlike every production route, now all closed. Diagnose target selection and chop
  sequencing; if a mechanism is pinned, a bounded fix protocol follows.
- *(original B4.5 scope)* planting-gate diagnostic → D175. Characterize
  the `banana_factory_*` enable condition and selector precisely; measure how often it
  fires in real games and what it would do at various thresholds; reconcile with D89's
  safety rejection (full factory, +82.9 opponent) and D91's 5/16-map selector failure, and
  determine what distinguishes the field's early-moderate planters from D89's
  plant-everything design. Read-only; sequenced after D174 to avoid concurrent edits to
  the resident source. Output: a frozen D175 protocol for the middle-ground planting loop. 25
  Legend agents run the resident's exact 2.00 roster yet rank 7–54 — a two-worker
  architecture demonstrably reaches rank 7, ~9 rating points above us, with no scaling at
  all. What do the strong two-worker agents do that we don't? Read-only field comparison
  of score composition, production, suppression, timing, and terminal behaviour. This is
  the only direction that is neither closed nor affordability-gated.
- **B3.10 ✅ CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE.** The 496 optimistically
  capturable observations are individual one-point fruit units across 205 games; all-credit
  own-score ceiling is 2.42/game and even factor-two deny-plus-capture is 4.84 margin/game.
  The detour estimate omits HARVEST/DROP and scheduling cost. D173a/b already expose the
  missing cost: compact_gold negative, catastrophes +5/+3, negative mass 1.096/1.081.
  Being outside D173b's chop-shadow is not value evidence. No target, threshold, capability
  change, panel, or scaling rationale.
- **B3.11 — CORRECTED / RE-REVIEW PENDING.** Owner postmortem game
  `896352129` (252–276 vs Dridriun) is exact: nine successive opponent-door APPLE
  generations yielded 83 opponent HARVEST commands; the first waited 60 turns for resident
  contact. The resident also issued 22 ripe CHOP commands over four own-door APPLE
  generations, including 20 by a starter already capable of HARVEST, and destroyed eight
  fruit at removal. Correction: the opponent harvested zero resident-created apples;
  capture was reachable, not realized. Only a read-only corpus precheck of the joint
  The 83 commands are 83 confirmed fruit units; removals are joint final CHOPs, and exact
  contact/ripe/BFS rows are published. Await narrow re-review; broad arms remain closed.
- **B3.12 — NARROWED_TO_FEASIBILITY_PRECHECK.** Owner postmortem game `896352750`
  (206–184 vs zasmu) is exact: at the first resident lemon chop, seven mature LEMON trees
  hold 84 health, so even a no-travel full clear needs 21 turns of combined chop power.
  The resident uses 28 CHOP commands over turns 26–67 to remove five initial trees,
  destroying 13 fruit but collecting nine wood. Zasmu harvests 25 lemons, including 19
  from a protected planted tree, replants one harvested seed, and exactly funds the
  eleven-/twelve-lemon bills for workers 3 and 4. Opening churn is three short A-B-A
  returns through turn 100, not a frozen ≥10-state oscillation. Only a read-only corpus
  audit may test whether the denial bonus can beat liquid stock, regeneration, clear
  burden, and bill timing; base wood value stays separate. E7/N6/D176a remain closed.
  **Owner override terminal 2026-07-31:** the explicitly directed threshold-3 candidate
  SHA `307a0755…` keeps full trolls chopping far focus trees and discards lethal overflow.
  Agent `6585578` / submission `41070584` completes 160/160 clean games at score 22.99,
  rank 34/113: +1.09 over the 21.9 pre-trial row, but below 24.70/25.40. This is now a
  restored active source as agent/submission `6589510`/`41079354`; its initial 9/9+1
  pending checkpoint is identity-clean with zero runtime signals. The uncontrolled live
  result is not scientific qualification or reopening of the broad closed arms.
- **B3.13 — TERMINAL FAIL / DISPLACED RESTORE.** Exact DoubtinGiyov game `897547554`
  exposes the requested enemy-tent orchard: 37 adjacent planted generations, with the
  opponent banking 24 adjacent-tree items before resident contact. The coordination
  layer now starts with the first cardinal-adjacent tree: at 1–2, one troll performs the
  ordinary chop/collect/bank path while the other denies an opponent-planted tree without
  a denial-driven return; above two, both trolls use full non-banking adjacent denial.
  Fail-closed candidate SHA `3bd42d5b…` passes 5 compiled boundary tests, exact 300-state
  open-loop validation, and eight unsealed both-seat smoke cells. This is mechanical
  coherence, not value qualification. Its exact live trial `6585739`/`41070944` failed
  cleanly after 101 games at score 11.96, rank 111/113, with 25 catastrophes and
  negative-margin mass 6,669. Exact far-denial restore `6585755`/`41071034` was clean
  at 41 games and 19.56 immediately before the owner displaced it.
- **B3.14 — OWNER-DIRECTED LIVE / MONITORING.** Adler3D game `897552551` identified an
  inherited deadlock: the productive worker forgot its bank role after target removal,
  while two full carriers entered a 42-WAIT/41-MOVE contention loop. Candidate SHA
  `f26e3781…` makes that productive bank commitment sticky until `DROP` or empty cargo;
  8 focused compiled tests, exact replay mechanism evidence, and 8 unsealed smokes pass.
  The owner explicitly directed submission instead of restoration. Agent
  `6585765`/`41071067` is identity-clean with zero runtime signals at 12 games, but the
  first score is only 9.64 (rank 111/113; four catastrophes). No automatic restore.
- **B3.15 — DISPLACED.** The same-tree occupancy fix removed the exact Elost assignment
  deadlock mechanically, but its first live row was only 11.53/14. It was superseded by
  owner direction; do not infer field value from the mechanism fix.
- **B3.16 — TERMINAL FAIL / BEST-SOURCE RESTORE.** Funding-first diagonal denial passed
  exact replay, compiled boundaries, and smoke checks and opened at 16.97/11, but matured
  to 16.37 over 265 clean parsed games with 40 catastrophes and negative mass 10,285.
  The owner directed restoration of the best bot; far-denial d3 SHA `307a0755…` was
  submitted exactly once as `6589510`/`41079354`. Initial health is clean but immature.
- **B3.17 — ENDGAME REMOVAL-RACE PREFLIGHT / NO SOURCE.** In the sole open direct
  current-vs-top20 game `897780884`, Astrobytes fells all five resident endgame APPLE
  conversions and captures seven wood; KEEP_BANK conservatively retains five resident
  points, while +33 margin is only a replay-conditioned optimistic ceiling. Run a read-only
  provenance census over the 153 exact open IDs. Stop unless recurrence across both seats
  and identities raises the frozen whole-corpus optimistic ceiling to 20 margin/game. Only
  then may a pre-PICK opponent-removal-race boundary be proposed; do not change turn 250,
  plant pacing, salvage, species, bonus, or focus.

## Tier 4 — arena protocol (standing, entered only by qualified candidates)

- **B4.1 Promotion protocol v3** — capacity A/A (control must reconverge within noise of
  its prior bracket) → candidate submit → mandatory +20/+35/+50-minute reads → delta vs
  same-window control with the frozen bands (≥ +0.5 KEEP, ≤ −0.5 revert) → restore exact
  resident on any failure. [arena-queue policy v2 + 07-16/07-18 Legend amendments]
- **B4.2 Bar tracking** — with each authorized read, record rank-3 score and top-3 battle
  counts (maturity context) in STATE §1.

## Tier 5 — infrastructure (pull in only when it blocks)

- **B5.1 ✅ DONE 2026-07-28** — TWO broken frozen bins found and feature-gated (d35c +
  the d36 oracle nested in its file; sources untouched, proof via identical error counts
  under the features). `cargo test --workspace`: **1,312 passed / 0 failed / 19
  ignored** — first green workspace in weeks. Commit `83bf5c0`; cap rule applied after
  the 29 GB test build (target back to 2.0 GB, release lib intact).
- **B5.2 ✅ YT tranche mirror** — done as part of B0.2 (plan Task 5, md5-verified).
- **B5.3 (re-scoped 2026-07-28): cold-file migration only; the LIVE games store stays
  local.** Rationale: the daily collection cron writes into `data/raw/games/` at 05:17 —
  symlinking the live store to the sometimes-detached USB drive would turn every
  drive-absent morning into a failed collection and permanently lost stream games
  (windows rotate). Instead: periodically migrate games older than ~30 days per-file
  (copy-verify-symlink), keeping the hot store and all indexes local. Low urgency at
  2.4 GB on a 900 GB NVMe. *(Ripeness checked 2026-07-28: oldest file is 07-03; zero
  files cross the 30-day threshold — first actionable window ≈ 2026-08-03.)*

## Recommended order

B0.1 → B1.1 → (B1.2 if warranted) → B2.1 gate → B2.2 → B2.3; B0.2 and B3.1 interleave as
fillers; B0.3/B4.x standing. Honest odds, **revised 2026-07-27 after B0.1**: the maturity
lever is largely dead — the ladder recomputes fresh-agent scores rarely (score frozen 4+
days), so visible-rank recovery cannot be assumed from waiting. Top-3 requires B2 to
succeed where thirty-odd offline selectors failed — the closed-loop objective is the one
untested lever the evidence still permits — and any promoted candidate must additionally
survive the same slow-recompute regime (mature reads will take days, reinforcing B0.3's
no-churn rule).
