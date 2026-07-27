# Troll Farm — The D-Series Atlas

Snapshot date: 2026-07-27. A reader's guide to every numbered experiment of the Legend
top-3 research cycle. Chronology lives in the ledger volumes
(`data/analysis/live-agent-6553250/legend-top3-experiment-cycle-*.md`); topic-sorted
conclusions in `docs/CONSTRAINTS.md`; live state in `docs/STATE.md`. This atlas is a
navigation snapshot, not a living record.

## 1. What a D-experiment is

Each `Dnnn` is one frozen-protocol experiment in the project's laboratory notebook. A
letter suffix (`D133b`, `D41c`) is a protocol revision or repair of the same experiment.
Every experiment leaves the same artifacts in `data/analysis/live-agent-6553250/`: a
**protocol** (question, method, and pass/fail thresholds written before running), a
**lock** (checksums of protocol, code, and inputs), the run products (bulk rows on the
external `artifacts/` root), and a **result** document ending in an explicit verdict.
The discipline that holds it together: thresholds are never adjusted after seeing data,
consumed seed ranges are never reused for selection, and negative results are retained as
binding constraints. Numbering makes conclusions citable ("remembered-crop returns are
closed — D165") and prevents re-running dead ends.

**The goal** (set 2026-07-18): rank 3 or better in the Legend practice ladder, on a mature
read plus confirmation. As of 2026-07-27 the resident (agent 6561795, exact slim
Yamo/Orchard, two workers) reads 43/110 at 21.97 against a rank-3 bar of 28.22. The
measured disease: the resident leads at turn 100 in most eventual losses and is
out-compounded late by opponents who scale to three-plus workers while keeping production
alive; top agents reap 24.16% of the crops they create, the resident 0.94% (D101).

## 2. Prelude — Phases 1–21 (2026-07-16 → 07-18)

Before the D-series, a phase-numbered program recovered the live bot and made the first
candidate attempts. Highlights:

| Phase | Question | Verdict |
|---|---|---|
| Recovery | What is actually live? | Exact source recovered (rank 6/104 @ 26.31), checksummed, made submit default |
| 1–5 | Do micro-edits help? | Idle-harvest KEEP; focus bonus KEEP; training constants closed; renewable mothers closed |
| Terminal fix | Are local verdicts valid? | Referee stall/mercy semantics adopted; one verdict flipped (pre-seed neutral → +0.259) |
| Stack | Pre-seed + orchard geometry | Arena **+3.0 — PROMOTED** 2026-07-17; slim A/A passed; still the only arena win |
| 3–5 | First-turn rollout controller | Local +2.7 → arena reject (21.7 vs 24.1 control) |
| 6–8 | 29-option first-move library | No opponent-robust activation; turn-one Monte Carlo closed |
| 9 | Imitate Escdemon | Passes observationally; collapses at autoregressive integration (52% MOVE) |
| 10 | Norxondor's workforce ladder | Reproduces all 8,738 triggers; observable-signature switch fails prospectively (−6.2) |
| 11 | Online shared-state Monte Carlo | Teacher +26.1 but 209 ms vs 50 ms budget — undeployable |
| 12–15 | Distill trajectory value | Fails held-opponent-family precision every time; native imitation −172.7 |
| 16 | Resident MOVE residual | Prospective +0.508 at 93 ms p95 — closed |
| 21 | Dual-value opponent-crop scoring | All local gates pass → arena **−7.77 REJECT**; b100_e6 evolved candidate +0.12, closed |

Lesson carried forward: local gates were not predicting arena outcomes; the cycle moved to
architecture research with much harder transfer discipline.

## 3. Arc A — Curriculum and the deployment bridge (≈D1–D28, 07-19 → 07-20)

Can a neural policy learn this game at all, and can it ship inside CodinGame's limits? A
training curriculum was built in five levels; numbering here is partly internal to the
rolling narrative (headered experiments begin at D29).

| Item | Question | Verdict |
|---|---|---|
| PPO from scratch | Learn the debug task raw | 12.4% — closed at readiness |
| BC + teacher-auxiliary | Bootstrap from a scripted teacher | Pure PPO argmax-collapses (18.2%); a 0.10 teacher anchor rescues it (99.3%) |
| Level 1 | Execute one worker's resource plan | Accepted, independently replicated (99.65%) |
| Level 2 | All 8 worker recipes | Accepted (98.6%), discovery + confirmation |
| Level 3 | Two-role renewable loop | Accepted (99.45%); illegal-label mask repaired |
| Level 4 | Recipes × roles jointly | Accepted (99.70%) |
| L5 D1–D5 | Isolated opponent mechanisms | Forager, planter, reaper, funded 2-worker: all accepted |
| L5 D6–D8 | Paid third worker, horizons | Teacher-censoring artifacts; closed at controls |
| L5 D9 | Crop before scale | Accepted — "secure renewable supply before scaling" |
| L5 D10–D11 | Repeated pressure; seed reacquisition | D11 = first task to beat the actor (79.4%); clone+PPO accepted at 97.65% prospective |
| K1–K2 | int8 deployment | K2 accepted: 7.04 ms median inference |
| V1–V5 | Live-protocol integration | Four observation-parity defects fixed; V5 accepted (68,988 B, 17.6 ms warm p95) |
| YT benchmark | Train remotely? | 9.8× throughput but CUDA/CPU parity fail → local training chosen |

Surviving assets: the environment/actor infrastructure, the deployment pattern (int8 +
persistent buffers), the teacher-auxiliary recipe — and a deployable curriculum actor
whose *field* value was still unproven.

## 4. Arc B — The domain-shift reckoning (D29–D34, 07-20)

| ID | Question | Verdict |
|---|---|---|
| D29a/b | Turn-75 spatial option-critic (farm vs resident) | +36.5 on generated maps; int8 candidate built |
| D29c | Does it activate on real arena states? | 8.75% vs 17–67% corridor — closed unsubmitted |
| D30 | Why the −78 shift? | Generator artifact: 6 water cells vs official 12–104; all roots out of support |
| D31 | Replay recorded commands as continuations? | Invalid — only 86.85% command match |
| D32a | TestSession forced-farm A/B | Mean −29; permanent farming and threshold repair closed |
| D33a/b | Port the referee's real map generator | Accepted — SHA1PRNG + plant-order subtleties; 120/120 exact |
| D34 | Census: 9 complete architectures on official maps | None passes production+suppression; worker count alone ≠ strength |

This arc invalidated the old evaluation world and replaced it with the authoritative
official-map substrate. Everything after D33 runs on real map geometry.

## 5. Arc C — Job grammars and bounded overlays (D35–D36, 07-20 → 07-21)

| ID | Question | Verdict |
|---|---|---|
| D35a | Decode rich players' persistent jobs | Vocabulary strong (94% RENEW+FELL); flat categorical head fails |
| D35b | One-shot factorized two-worker bundles | Oracle +34.99 but suppression far short |
| D35c | Add crop-creator provenance to targets | Causal +7.8 — provenance retained as a factor; one-shot closed |
| D35d | Repeat allocation at job boundaries | +23.1 beyond one-shot; opponent excess still +76 vs +65 ceiling |
| D36 | Same overlays anchored on the resident | +19.6 own / +10.6 margin vs +68/+25 floors — closed |

Conclusion recorded: no wrapper composition reaches the field gap; one coherent policy
must own opening, supply, funding, production, and suppression end to end.

## 6. Arc D — Complete-macro teachers (D37–D40, 07-21)

| ID | Question | Verdict |
|---|---|---|
| D37 | Complete factorized macro environment | Environment clean and deterministic; rate initializer fails; transactional semantics invalidation found and fixed |
| D38 | Value jobs by exact TRAIN-bill reduction | Rejected (loses to random); spawn-shack blocker isolated |
| D39 | Add shack evacuation | Narrow reject (+38.2 vs +50); insight: 1→3 promotions gain +295, 1→2 gain −1.3 |
| D40 | Deficit-first, else work-conserving rates | **PASSES** +94.6 over D39, all families — frozen as THE teacher |

## 7. Arc E — Learning on D40 (D41–D62, 07-21)

The graveyard of straightforward learning ideas, and two validated interfaces.

| ID | Question | Verdict |
|---|---|---|
| D41a | Behavior-clone D40 | 85% vs 99% floor; a parameter-free decoder gets 100% — MLPs can't do lexicographic filters |
| D41b | Exact-prior + zero residual | Byte-exact reproduction — validated interface |
| D41c | Residual PPO (temp 4) | Max residual +0.33 vs +4 prior gap → 0/85,128 changed decisions |
| D41d–f | One-deviation labels, branch selectors, thresholds | 46–58% positive vs 55–60% floors — all fail |
| D41g/h | Linear / tiny-ReLU value filters | Fail the 65%/27% precision pair |
| D42 | 194-feature context selector | Fails; one-deviation supervision closed |
| D43/D44 | Sparse binary closed-loop PPO | Learns a uniform bias (probe SD 0.0012); its scores uncorrelated with value |
| D45/D48 | Rate-formula surfaces | Saturated/discontinuous — not locally searchable; CEM blocked |
| D46/D47 | Hard chopper / producer roles | Chopper already implicit in D40; producer role −12.0 |
| D49 | Chopper-first reservation order | 12 deposit-prediction violations — transactional revalidation required |
| D50 | Population of phase-recombined opponents | Support improves; rich-cohort gates still missed |
| D51 | Workforce-relative whole-controller switching | Only 27.5% ever reach the trigger — funding is the upstream problem |
| D52a/b | Procedural job market; why TRAIN fails | All 5,142 failures = a PICK spends the bill after the decision |
| D53a/b | Atomic bill reservation | Fixes worker-2; 168 residuals = shared-surplus oversubscription |
| D54 | Shared per-turn PICK ledger | Transactions fully clean; reach still 25.3% — problem moves to acquisition |
| D55 | Terminal stock-flow diagnostic | 91% of blocked bills source-unresolved; LEMON dominates |
| D56/D57 | LEMON source; exact deficit-vector sources | Sources get built; worker-3 reach *falls* (23.8%, 21.3%) |
| D58 | Labor/progress diagnostic | Source planting regresses bills; mining converts — conversion layer is causal |
| D59 | Materialization-only lease | Better per-turn progress, 56% idle labor — entire hand-designed source branch closed |
| D60 | Fixed invest/materialize/liquidate per phase | Oracle +47.4 but violates the crop floor — fixed modes rejected |
| D61 | Options at natural job-batch boundaries | Oracle +57.6, crop-safe, sequencing carries value — **validated interface** |
| D62 | Feed-forward batch-option PPO | Argmax never moves (0/512) — recipe closed; passive field refresh (D61p) readied |

## 8. Arc F — Field evidence, round two (D63–D71, 07-21)

| ID | Question | Verdict |
|---|---|---|
| D63a/b | What predicts who scales? | Turn-100 economy state (0.97 AUC), not opening geometry (0.48); prediction ≠ value |
| D64a/i | Gate late scale by the field model | Run invalid via a worker-two tail; oracle only +1.9; diagnosis: missing bill species |
| D65–D67 | Rescue via deposited-seed sources | Planted sources die before payback; lease fails; zero viable cells — closed |
| D68 | Bill-level source portfolio | 2/4 recovery; reusable hostile pressure taxes each generation — late rescue closed |
| D69/D70 | Scaler lifecycle archaeology | Universal order establish→receipt→reinvest→worker-3; no minimal opening transaction reproduces it |
| D71 | Closed-loop opening-portfolio environment | Mechanics pass — infrastructure only |

## 9. Arc G — Recurrent search era (D72–D78, 07-21)

| ID | Question | Verdict |
|---|---|---|
| D72 | Recurrent opening portfolios (8 actions) | Oracle +64.1 headroom; explicit seed-action breadth misses by one task |
| D73 | Four-mode recurrent PPO | −1.76 prospective; sacrifices own score symmetrically |
| D74/D75 | One- and two-batch option sequences | Too coarse: 38.5% strict; 16 sequences span 3.5 points |
| D76/D77 | CEM; full-parameter lineage search | Both converge to the balanced plateau (≤1% non-balanced choices) |
| D78a/b | Is opponent attack imminence observable? | Yes — 0.9307 AUC from spatial features; history adds nothing |

Recorded pattern: with four coarse modes and a snapshot state, every optimizer retreats to
"do what the resident does." The action space, not the optimizer, was the constraint.

## 10. Arc H — Spatial and target interventions (D79–D85, 07-21)

| ID | Question | Verdict |
|---|---|---|
| D79 | Unconstrained all-Rate spatial scorer | Global trajectory replacement (every policy changes every hash) — closed |
| D80/D81 | One-shot contested-crop promotions | Ubiquity/support failures; lesson: measure authority by decisions, not hashes |
| D82 | Semantic responses to threatened crops | Oracle +11.2 but value is state-specific — no deployable fixed arm |
| D83 | Snapshot value model over D82 | Captures 10.6% of oracle — closed |
| D84 | Truncated counterfactual Monte Carlo | Best +3.2 vs +5.6 needed, at 210 ms — online MC closed |
| D85 | One-turn defensive salvage on real replays | The resident already makes every lethal joint chop; salvage +0.05 — closed |

## 11. Arc I — The yaichi seed-factory (D86–D95, 07-21)

| ID | Question | Verdict |
|---|---|---|
| D86 | Is renewable mode opening-selectable? | No — 0.58 validation accuracy |
| D87 | Commit to regeneration after fresh harvests | −51.2 active margin; new plants become wood, not an orchard |
| D88a–c | Decode yaichi's task states | Bank-bootstrap seed-factory architecture confirmed 10/10 |
| D89 | Reproduce the factory on the resident | Production spectacular (+79.4) but opponent +82.9 — safety reject |
| D90 | Lineage boundaries; ATTACK state | Ablation inert; ATTACK is an endgame bank blockade |
| D91 | Select factory activation by map | Development +31 but 5/16 maps — transfer fail |
| D92 | Factory + dual-value denial | Trained-role denial arrives too late (−5.6) |
| D93 | Can the factory fund worker 3? | Zero legal TRAIN turns in 256 tasks — it's a wood economy, not a funding economy |
| D94 | Late existing-stock funding bridge | Trains in 147 tasks and loses 91.6 — late grafts closed |
| D95 | Rank-one scaler archaeology | Coordinated funding is shared; no universal hand-written grammar — learned-representation requirements recorded |

## 12. Arc J — Joint assignments and the q6 program (D96–D147, 07-21 → 07-23)

The largest arc: a validated coordination interface, a compact action bank, and roughly
thirty supervised selectors that all failed the same way.

| ID | Question | Verdict |
|---|---|---|
| D96 | Worker-factorized four modes | +0.8 incremental vs +5 — worker context isn't the missing piece |
| D97 | Concrete collision-safe JOINT assignments | Oracle +36.9; joint adds +9.2 beyond best-single — **validated interface** |
| D98–D100 | Pair scorers, replacements, residuals | Near-misses and activity failures; static selection over the bank is dead (rank correlations 0.10–0.22) |
| D101 | Production/suppression role archaeology | ★ The gap: top-3 reap 24.16% of created crops, resident 0.94%; suppression already competitive |
| D102/D103 | Transfer D40 wholesale; phase decomposition | −48.4; opponent excess accrues 14/39/47% across phases — duration matters |
| D104–D106 | Expert-proposal union; q4/q6 quantization | Union keeps 86–88% of the joint oracle; q6 bank frozen at 9,180 bytes with fresh-map replication (+32.0) |
| D107 | Bounded online controller preflight | Four-use oracle +35.2, crops/workforce exact — interface ready |
| D108/D109 | Recurrent masked q6 PPO; 4× duration | −0.74 then −0.15; family patterns rotate across panels — the family-robust objective question is posed (and skipped) |
| D110/D111 | Random linear one-use policies; lineage search | Abstention calibration is the frontier; fitness doesn't transfer |
| D112/D113 | Dense exact-continuation teacher | Coverage semantics fixed; teacher +36.8, all families positive |
| D114–D118 | Ridge, MLP, WAIT-softmax, factorized gates, soft targets | All fail; ranking (not timing) is the bottleneck |
| D119–D127 | Long fits, info floors, calibration, tail attribution | First fit+validation pass appears; held support protocol fails; 82/98 losses are ranking errors with +891 recoverable |
| D128/D129 | Absolute anchors; safety heads | Ranking and safety must not share a scalar; compositions 0/60 |
| D130/D131 | Pairwise loss; all-seed audit | Fit statistics *anti-predict* transfer (r = +0.89 wrong way) |
| D132/D133/D139 | YT distributed corpora | Byte-exact parity; eight independent 16-map blocks built |
| D134–D138 | Out-of-fit block selection; gates; calibration | Selection design validated; every learner still fails the veto |
| D140–D143 | 8-block selection, balanced losses, dual gates | Best ever: +3.06 at 39.65% strict vs 40% floor — **one-use gate tuning closed** |
| D144–D146 | Offline two-intervention Monte Carlo | +4.15 incremental; winning pairs genuinely joint (second action +27.3); early-immediate schedules carry it |
| D147 | Live-interface feature replay | Byte-exact — safe to scale |

## 13. Arc K — Exact-value teachers and the substrate verdict (D148–D158, 07-22 → 07-23)

| ID | Question | Verdict |
|---|---|---|
| D148a/b | Fresh-map priority joint teacher (YT) | Hidden two-use transfer +4.11, robust in all families |
| D149a/b | Imitate its best pairs | 9.5–9.8% rank accuracy — hard-argmax entropy, closed |
| D150 | Is near-tie supervision available? | 16.5% vs 20% — collect counterfactuals instead |
| D151/D152 | Exact conditional-second values (YT) | +36.8 on active states — the strongest teacher signal of the program |
| D153–D156 | Fitted value, abstention, slices, memory, lookup | Everything fails map-fold transfer (+2 held vs +14–17 train); confidence anti-correlates |
| D157 | Frontier audit | The skipped D109 family-robust objective is the one open branch; D158 frozen |
| D158 | Recurrent q6 PPO relaunch | **Stopped by the baseline-dominance audit** — the whole D40/q6 world can't beat the resident |

## 14. Arc L — The resident-native pivot (D159–D168, 07-23 → now)

| ID | Question | Verdict |
|---|---|---|
| D159 | Refresh the loss mechanism on 200 games | Catastrophe tail replicated (11% of games, 58% of negative mass); attack angles ranked |
| D160 | Does the resident ever afford worker 3? | Never — zero affordability windows in 195 games; funding is policy, not luck |
| D161 | Same-panel dominance arithmetic | Full q6 oracle only +3.4 (n.s.) vs resident — substrate closed; resident-anchoring becomes law |
| D162 | Bounded reserve/route/commit options | Can't fund worker 3 (5/128 best) — but the crop-safe option envelope is +12.7 with zero regressions |
| D163 | Do fixed components transport? | No — fruit/iron/protection all nonpositive on a disjoint panel |
| D164 | Current-field macro-transition audit | New motif: producer→suppressor→producer cycling, 72% of top-5 games, resident 11% |
| D165 | Return to the remembered crop? | Zero support in 1,024 tasks — the old crop is always gone |
| D166 | Is the return one command? | No: multi-step acquisition journeys, median 16 turns; single-verb controllers closed |
| D167 | Are the journeys regular? | **Yes: BANK_SEED frozen-eligible** (135/135 local, 71.4% top-5 field); field agents pre-carry seeds through suppression 45%, resident 0% |
| D168 | Does executing the return causally help? | *Running now* — bounded option vs exact resident, preregistered value/tail gates |

## 15. Inflection points

- **D30** — our generated maps were unlike real maps; weeks of results invalidated, honest substrate built (D33).
- **D40** — a teacher economy good enough to learn from.
- **D97** — joint two-worker coordination has real, measured value.
- **D101** — the gap is production *persistence*, not suppression.
- **D161** — the alternative-economy substrate is weaker than the bot we already have; everything pivots resident-native.
- **D164→D167** — the missing field behavior distilled into one frozen-eligible option.

## 16. Glossary — mother, crop, orchard

Terms that recur throughout the ledger, grounded in the game's mechanics and the
resident's own source code.

- **Mother** — a tree the bot deliberately plants (or adopts) and then *keeps alive as a
  renewable seed source* instead of chopping it. Mechanically: a living tree bears
  species-typed fruit; a picked fruit can be replanted as a seed of that species; chopping
  the tree instead yields one-time wood. A mother is therefore reproductive capital — its
  recurring fruit income funds new plantings — where an ordinary tree is harvestable
  capital. The concept is first-class in the live resident: its scarce-map planner runs
  the intent chain `NeedSeed → HarvestSeed → PlantMother → TendMother → PlantCrop{mother,
  target}` (see `rust/src/bin/yamo_orchard_live.rs`).
- **Crop** — a tree planted for *conversion*: grown, then felled for wood/score. In the
  mother/crop loop, the mother's fruit becomes the seeds; the crops are her children.
  A **lineage** is the family of trees descending from one seed source; "lineage
  extinction" (a denial concept, class d) means no living tree of that family remains.
- **The mother/crop loop** — the self-renewing economy: protect one mature parent,
  harvest her fruit, plant children, fell the children at maturity, repeat. On
  tree-sparse maps this loop is the lifeline (the Gold-era deforestation stall was fixed
  by a seed reserve for exactly this reason). Its cost side: tending a mother consumes
  worker turns, and a mature *shared* mother's fruit can be captured by the opponent —
  the Phase 1–5 verdict that closed six aggressive mother/crop variants was precisely
  "action cost plus opponent capture exceed private crop value."
- **Orchard / secure orchard** — the resident's wrapper that runs this loop on favorable
  geometry: cells where the mother and her crops sit in resident-controlled territory
  (the promoted 07-17 stack's "secure-orchard coverage" widened exactly this geometry).
  "Releasing" the mother — treating her as a spare resource for other tasks — is closed:
  the ledger's verdict is that **the mother is a saturated producer, not an idle
  reservation** — her fruit throughput is already fully consumed by the loop, so
  liquidating or re-tasking her trades recurring apples for less wood than they are worth.
- **Where this touches the current thread** — the D164–D168 successor returns are the
  same economics seen from the worker's side: a producer leaves to suppress, and comes
  back by planting a *new crop generation* from a banked seed (D167's BANK_SEED). The
  deposited bank those seeds come from is fed by harvests — including mother fruit — so
  the mother/crop loop is the upstream supply of the very returns D168 is now testing.

## 17. Where the records live

- Ledger vol 1 (Phases + D1–D166, frozen): `legend-top3-experiment-cycle-2026-07-18.md`.
- Ledger vol 2 (live): `legend-top3-experiment-cycle-vol2-2026-07-23.md`.
- Per-experiment records: `data/analysis/live-agent-6553250/dNNNa-*-{protocol,lock,result}*`.
- Closed branches by topic: `docs/CONSTRAINTS.md` (classes a–h). Live state: `docs/STATE.md`.
- Priorities and gates: `docs/BACKLOG.md`.
