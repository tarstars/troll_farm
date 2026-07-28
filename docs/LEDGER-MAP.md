# Troll Farm — The D-Series Atlas

Snapshot date: 2026-07-29. A reader's guide to every numbered experiment of the Legend
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

## 14. Arc L — The resident-native pivot (D159–D175a, 07-23 → 07-29)

| ID | Question | Verdict |
|---|---|---|
| D159 | Refresh the loss mechanism on 200 games | Catastrophe tail replicated (11% of games, 58% of negative mass); attack angles ranked |
| D160 | Does the resident ever afford worker 3? | Never — zero affordability windows in 195 games; funding is policy, not luck |
| D161 | Same-panel dominance arithmetic | Full q6 oracle only +3.4 (n.s.) vs resident — substrate closed; resident-anchoring becomes law |
| D162 | Bounded reserve/route/commit options | Can't fund worker 3 (5/128 best) — but the crop-safe option envelope is +12.7 with zero regressions |
| D163 | Do fixed components transport? | No — fruit/iron/protection all nonpositive on a disjoint panel |
| D164 | Current-field macro-transition audit | New motif: producer→suppressor→producer cycling, 72% of top-5 games as sampled, resident 11% (population rate later corrected to 49.7% by B3.3; the breadth+gap gate still passes) |
| D165 | Return to the remembered crop? | Zero support in 1,024 tasks — the old crop is always gone |
| D166 | Is the return one command? | No: multi-step acquisition journeys, median 16 turns; single-verb controllers closed |
| D167 | Are the journeys regular? | **Yes: BANK_SEED frozen-eligible** (135/135 local, 71.4% top-5 field); field agents pre-carry seeds through suppression 45%, resident 0% |
| D168 | Does executing the return causally help? | **No — hand-written successor controllers close** (post-return −6.73, pre-carry −8.21; integrity clean); the motif becomes a rollout-valued option for B2.1 |
| D169 | Does a unified resident-option envelope clear the +10 gate? | **Yes — PASS**: +10.671 mean, CI [+9.42,+11.92], 65% improved, 0 regressions, tails better than control (100% coverage; every option negative always-on). Opens D170 (Fable-authored closed-loop training design) |
| D170a | Can a policy learn WHEN to invoke the options? | Invalidated by an implementation bug (3 trig arms structurally unreachable; caught by the Stage-A gate, byte-identical reruns; superb root-cause) — repaired as D170b |
| D170b | Same question, repaired mechanics | **CLOSED-AT-PHASE-2**: 8/8 fits trained, all 13 arms live — and all four objectives converged to always-KEEP (0/8 admitted). The envelope's rare positive contexts are unlearnable from ~200 samples/arm vs ±26 terminal noise; objective choice irrelevant. Tier-2 closes per its kill rule |
| D171a | Does a hard-forbid breaker cure the B3.4 same-two-cell oscillation? | **No — mechanism fails**: ≥10-turn runs cut only 45.7% (floor 80%); 5–9-turn runs increase +117% (displacement); 72 previously clean tasks acquire brand-new oscillations (worst 88 turns) — a stale-arm design hole in the disarm rule. Value neutral overall (+0.053) but activated subset only +0.53 <+1.0 gate. No candidate; successor requirements recorded (bounded arm lifetime, echo-stop disarm) |
| D172a | With exact, zero-noise counterfactual labels instead of on-policy reward, is the +10.671 envelope's value learnable? | **No — definitive closure.** Signal is abundant (40.4% of 27,392 states carry a ≥+2 option, floor 8%, both seats, 8/8 families) yet both linear and MLP fits fail LOBO admission (+0.14–+0.26 held vs the +1.5 gate). Not label noise, not capacity, not covariate shift — the positive contexts are unidentifiable from the 64-field+affordance observables. The Tier-2 learning route closes on the cleanest possible instrument; only spatial-plane observation remains untried |
| D173a | Does a narrow harvest-before-chop fix recover B3.5's 9.62-pt/game lost fruit? | Trigger fired broader than the frozen spec (any CHOP-candidate at the cell, not the unit's *assigned* action) — 41/60 sampled activations were diverted transit units. All three mechanism gates fail, though raw value was strongly positive (+2.935, activated +5.763) with a worst-family/catastrophe/tail cost. **Implementation-fidelity invalidation** (D170a precedent) — repaired as D173b; broad variant closed as tested, kept only as hypothesis material |
| D173b | With trigger fidelity repaired (64/64 verified), does harvest-before-chop transfer? | **Mixed, and capped.** 99.9% elimination among harvest-capable choppers, but 99.93% of surviving waste is trained units hardcoded `harvest_power: 0` — untouchable by the frozen scope. Value passes the mean gate (+1.063) but fails worst family (−1.391), catastrophes (52 vs 49), and tail mass (1.081). Closed as an execution-class fix; reframed as a strategic worker-capability question gated on B3.8 |
| D174a | Does an opportunistic-mining fix (B3.9) unlock worker-3 funding? | Iron acquisition worked exactly as designed (0.51→5.40 iron/game, 10.6×) — but worker-3 TRAIN stayed **0.0%** even with the `can_train` cap clause deleted, an 84.4-point shortfall against the counterfactual. Exposed instead: an unconditional `if n>=2{return false}` hard cap, and — correcting B3.8/B3.9's synthetic-spec counterfactual — the real `TUNED_CARRY` bill is **fruit**-bound (PLUM/LEMON short in 100.0%/99.5% of games), not iron. Value −10.76, all 8 families negative — opportunistic mining closed as harmful; fix order becomes planting (D175) → cap → mining (probably never) |
| D175a | Does bounded early planting (B4.5's priority-targeted design) recover the plant-reap loop? | **CLOSED — severely harmful.** Trigger fidelity 100% (153/153); works exactly as designed (median first plant turn 13.0 vs control 199.0, peak concurrent crops 1.98) — but reap rate *fell* (0.68%→0.45%, D87's wood-conversion grammar unchanged) and the safety ratio failed decisively: Δown −5.41 vs Δopponent +21.09. Value −26.44 (CI [−28.96,−23.92]), worst family −51.31, catastrophes 229 vs 130 — all six sub-gates fail. Third independent confirmation, with D89 and B4.5, that production trades away more denial than it gains; the harvest→mining→scaling→planting chain now closes at every link |

## 15. Arc M — The maintenance-era audits (B3.x/B4.x, 2026-07-27→29)

Where Arc L's D-experiments are bounded, frozen-protocol causal tests, a parallel run of
**B-numbered audits** used the (now quadrupled) replay corpus to find and price leads by
read-only measurement — no code change, no candidate, no preregistered pass/fail
threshold. They ran under the owner's 2026-07-28 maintenance-mode decision, alongside
rather than instead of the Tier-2 program. Several fed directly into Arc L's later
experiments: B3.4 diagnosed the oscillation that D171a then tried and failed to fix; B3.5
diagnosed the missing HARVEST action class that D173a/D173b then partially fixed; B3.9
diagnosed the mining gate that D174a then fixed and, in fixing, corrected.

| ID | Question | Verdict |
|---|---|---|
| B0.4 | Does the per-agent battle-window sample undercount the visible field? | **Yes** — the old 10-per-agent lens left ~85% of the visible stream uncollected. Full top-20 windows plus ranks 21–50, fetched for the first time: **1,891 → 8,122 games** (+6,231 in one run), 469 unique agents, 99.7% exact score reproduction, zero permanent losses. Standing daily collection cron installed the same day |
| B3.1 | Is the D159 catastrophe signature real, and does the endgame switch just need retuning? | Replicates independently: 19/192 games (9.9%) are catastrophes carrying 57.9% of negative-margin mass. The switch has no coverage bug — an AND-of-behind design cannot structurally fire before the crossover (median +46.5 turns late). Switch retuning closed. Surviving signal: opponent workforce scaling past two workers precedes the crossover by 42–125 turns in 84% of catastrophes — an observable trigger the resident never conditions on |
| B3.2/B3.3 | At 4× corpus scale, does the motion audit stay clean and do the small-sample field rates hold? | Motion: zero failures across 49,977 real moves. One new lead found: sustained same-two-cell oscillation (18/194 games, worst 131 turns) → opened as B3.4. Field rates mostly stable (BANK_SEED 71.4%→67.5%, pre-carry 44.9%→40.5%, catastrophe rate 9.9%→9.8%); one correction: **D164's top-5 P→S→P motif rate 72.0%→49.7%** (sampling-completeness artifact — the frozen breadth+gap gate still passes, 5/5 agents) |
| B3.4 | What causes the two-cell oscillation, and can a bounded fix cure it? | Root-caused to a memoryless detour tie-break with zero cross-turn memory — ties regenerate indefinitely; `force_unique_door_clear` has a genuine coverage gap (all 18 games have 2–4 doors). Causality modest (2/18 causally suspicious). Bounded fix frozen as **D171a — closed** (Arc L): 45.7% cure vs an 80% floor, +117% displacement |
| B3.5 | Why does the resident leave fruit unharvested near its own choppers? | Root cause: the busy-unit candidate generators build no HARVEST candidate at all, and trained units are hardcoded `harvest_power: 0`. Net genuinely-lost value **1,972 pts / 9.62 per game** — the richest execution vein assayed to date, 33.4% of it destroyed by the worker's own chop. Fix frozen as **D173a/D173b — both closed** (Arc L): recovers the addressable slice, capped by the same harvest-incapability design |
| B3.6 | Is the `idle_with_work` signature (7,782 episodes corpus-wide) a real waste vein? | **No — ~78% benign/correct/detector-artifact.** 945 episodes were a detector bug (CHOP legality ungated on free capacity); round 2's "wood-race" flagship falsifies on fate-tracing (only 11% clean losses, ≤68 pts corpus-wide). Genuine ceiling ≤130 pts corpus-wide (≤0.6/game). Closed — no cycle warranted |
| B3.8 | Is worker-3 scaling fruit-limited or iron-limited (owner-thesis test)? | Crediting all uncollected own+opponent fruit opens the cheap-helper window in only 10.2% of games, balanced spec never (0/205) — iron limits 97.3–100% of remaining failures. 90% of the own-territory fruit haul is destroyed by the resident's own CHOP. Confirms the owner's near-camp hypothesis. Verdict: iron-limited — **later corrected by D174a** (Arc L; see the synthesis below) |
| B3.9 | Is mining itself gated off, and would fixing it unlock scaling? | **Yes, decisively — the strongest lead in the project's history at the time.** Mining is reachable only while `own_units < 2`; 0.68 iron/game vs the top-5's 13.02 (19.2×); 98.3–98.6% of reachable iron never converted. Fruit+iron combined counterfactual: cheap-helper affordability 8.8%→84.4%. Opened D174 — **closed at mechanism** (Arc L): the affordability figure does not survive contact with the resident's real bill |
| B4.3 | What is a worker actually worth, and where does the resident's gap concentrate? | First field pricing (8,073 games): **within-agent fixed effect +48.2 margin/worker** (CI [44.1, 52.7]), non-diminishing through worker 4. **Scaling 2→4 ≈ +5.2 rating points = 84% of the resident's 6.25-point gap** to the rank-3 bar. Prices the destination only |
| B4.4 | 25 Legend agents share the resident's near-exact roster and outrank it — what differs? | **Tempo, not conversion style.** Median first PLANT: resident turn 191.5 vs 21–29 for the cohort. Reap rate: resident 0.93%, strong peers 15.3%, peer/weak 17.2%. **At equal roster (2v2) the resident is at exact parity with strong peers (58.2% vs 58.3%)** — the deficit is downstream scale-asymmetry survival. The plant-reap loop's code exists but defaults off behind a rarely-firing selector |
| B4.5 | Is the dormant `banana_factory_*` machinery a disabled-but-present subsystem, or is planting structurally deprioritized? | Two corrections to B4.4: the *deployed* slim artifact contains **zero** occurrences of `banana_factory`/`ScarceIntent` (pruned as dead code in the 07-17 slimming) — the real mechanism is two other live paths where **chopping always outranks planting**, and the bot farms only once idle. The dead selector would have fired in only 12/204 = 5.9% of games; timing is not the constraint (roster 2 arrives turn 7, long before peers plant at 21–29). Peers differ from D89's rejected full factory by *bound*, not kind (~5–6 concurrent own crops vs an uncapped 100%-of-bank dump); field-confirmed risk: a high-vs-low planting split correlates with +20.8 opponent score, CI [1.8,38.0]. Sets D175's design: bounded-concurrency planting with a reinstated Δopponent ≤ 40%·Δown safety ratio |
| B4.6 | Is the 0.31-vs-0.43 wood/chop suppression-efficiency gap (B4.4 finding 3) a real, fixable lead? | **CLOSED — real, but its fix class already failed twice.** Capacity-blocked chops, target contention, and travel overhead are all ruled out (the resident's move:chop ratio is actually *better* than peers': 1.52 vs 1.96); the gap is tree size at felling plus kind mix (Oaxaca 51% rate effect / 33% mix effect), root-caused to `chop_candidates` scoring pure throughput (`1000·wood/turns`) blind to crop origin by design — confirmed reconstructing 86.4% of real decisions. Despite a ≈54–73 pt/game addressable-looking residual, this exact intervention class already lost on the byte-identical binary twice (Phase 21 opponent-crop bonus −7.77 arena; harvest-before-chop −2.325 grid) plus a −61.7 chop-layer transplant against an adaptive opponent — closes the execution-class prospecting track |
| Baseline | Is execution-waste minimisation the ladder differentiator? | **No — the opposite.** On all six waste signatures the resident is cleaner than top-5 and ranks 6–20, including per-worker (`harvest_slack` 74.8 turns/game vs top-5's 615.9, 8.2×). Interpretation: "the hygiene of poverty" — little to waste with 2 workers and ~12 crops. Execution-waste minimisation is not the differentiator, downgrading remaining Tier-3 prospecting |

These are read-only field measurements, not frozen-protocol causal tests — no threshold is
declared in advance and nothing here changes the resident's code directly; each audit finds
and prices a lead, and where a lead was actionable it was handed to a proper D-numbered
experiment under the usual integrity discipline (B3.4→D171a, B3.5→D173a/D173b,
B3.9→D174a). Together they assembled the causal chain the next section synthesizes: the
resident's problem was never suppression, and — despite B3.8's first read — not iron
either; it is that the plant-reap loop the rest of the field runs from turn ~25 never
starts.

## 16. The terminal synthesis — where this architecture's ceiling is and why

By 2026-07-29 the maintenance-era program (Arc M) had traced the resident's scaling gap
to a single causal chain, and every link in that chain has now been tested and closed.
B4.4 found that the resident makes its first successful PLANT at a median turn of 191.5,
against turns 21–29 across a cohort of 25 Legend agents whose roster averages within ±0.2
of the resident's own exact two workers — not a resource constraint (every agent's
starting unit has the same hp=1 endowment), but a policy choice. The downstream
consequence is the reap-rate gap the project has confirmed independently: the resident
converts 0.93% of the crops it creates into score, against 15.3–17.2% for those same
two-worker peers and 24.16% for the top of the ladder (D101). Crucially, B4.4 also showed
this is *not* a two-worker skill gap: at equal roster (2v2) the resident is at exact
parity with the strong cohort, 58.2% wins to 58.3%. The entire deficit to those peers is
downstream of scale-asymmetry survival — losing badly once outnumbered (−37.1 average
margin vs 3-worker opponents, where the strong cohort loses only −1.8) — which is itself
downstream of never running the plant-reap loop that would let the resident afford a
third worker at all.

B4.3 priced what that loop is worth: a worker prices at roughly +2–4 rating points,
concentrated in workers three and four and not diminishing through worker four (2→3 =
+1.9 rating, 3→4 = +3.3); scaling from two workers to four is worth ≈ +5.2 rating points —
about 84% of the resident's 6.25-point gap to the rank-3 bar. B3.8 and B3.9 then tried to
explain why that scaling never happens, and first pinned it on iron: mining is gated off
entirely once a second worker exists (one call site, reachable only while `own_units < 2`),
and crediting all uncollected fruit *plus* reachable iron opened a cheap-helper
affordability window in 84.4% of games, against 8.8% for fruit alone. D174a then ran that
fix for real and found the opposite of what the counterfactual promised: iron acquisition
worked exactly as designed (0.51 → 5.40 iron/game, a 10.6× increase), yet worker-3 TRAIN
stayed at 0.0% in both arms regardless — an 84.4-point shortfall against the
counterfactual's own prediction. The reason is a correction to B3.8/B3.9's own method:
their counterfactual priced a synthetic cheap-helper spec (3 PLUM/3 LEMON/2 APPLE/3 IRON),
while the resident's actual `TUNED_CARRY` policy requests roughly double the fruit (PLUM
6.23, LEMON 5.87 at two workers) — a bill the post-workforce-2 bank never reaches in 100.0%
of games for PLUM and 99.5% for LEMON. Fruit, not iron, is the binding bill constraint, and
B3.9's 84.4% affordability figure must not be quoted for the real policy.

D174a also exposed a second, independent defect while testing the first:
`MoisanBot::can_train` contains an unconditional `if n >= 2 { return false }`, evaluated
*before* any affordability check — the bot is hard-capped at two workers no matter what it
can pay for. B4.4 had grounded the 191-turn planting delay in a tested `banana_factory_*`
self-planting/reaping subsystem it read as present in the live planner but defaulting to
`enabled: false`; B4.5 corrected this directly against the deployed binary — the shipped
slim artifact contains **zero** occurrences of `banana_factory`/`ScarceIntent` (pruned as
dead code in the 2026-07-17 slimming), so that machinery cannot be the mechanism. The real
cause is two other live paths: a rare map-gated single-mother orchard, and an
idle-regeneration fallback that permits PLANT only once a worker has nothing left to CHOP.
Chopping always outranks planting by construction, and the bot farms only when it runs out
of things to suppress; the dead selector, even if it were live, would only have fired in
5.9% of games.

The fix ordering this chain implied played out to the end, and closed at its very first
link. D175a built exactly the bounded-concurrency planting rule B4.5's diagnosis
specified and ran it for real: trigger fidelity 100% (153/153), and the intervention
worked precisely as designed — median first plant moved from turn 199.0 to 13.0, peak
concurrent crops held at 1.98, both frozen gates passed clean. The outcome was the
opposite of helpful. Reap rate *fell*, from 0.68% to 0.45%, because planting earlier
changes only *when* a plant appears, not what the resident's grammar does with it
afterwards — which is convert it to wood, exactly as D87 found in the full-factory
experiment years earlier. The safety ratio failed decisively: the resident's own score
fell (Δown −5.41) while the opponent's rose more (Δopponent +21.09), for an overall value
of −26.44 (CI [−28.96, −23.92]) with all six sub-gates failing, including catastrophes
rising from 130 to 229. This is the third independent confirmation of the same mechanism
— D89's full factory (+82.9 opponent score, of which +76.5 came from the opponent's own
crops), B4.5's field correlation (+20.8 opponent score for higher-planting peers, CI
[1.8, 38.0]), and now D175a's controlled experiment: for this architecture, production
trades away more denial than it gains. Turns spent farming are turns not spent
suppressing, and the resident cannot harvest what it plants (B3.5/D173: no HARVEST
candidate for busy units, trained units hardcoded `harvest_power: 0`), so the opponent's
own plant-reap loop compounds faster than the resident's ever could.

With production closed at every link it touches — harvest capability capped by
`harvest_power: 0` (D173a/b), mining wrong-resourced and harmful (D174a), scaling
hard-capped and unaffordable under the real bill (D174a), and now early planting itself
harmful (D175a) — the one remaining lead played *to* the architecture rather than against
it: B4.4's finding that the resident nets 0.31 wood per chop against 0.43 for strong
peers. B4.6 diagnosed it cleanly and closed it in the same session. Capacity limits,
target contention, and travel overhead are all ruled out (the resident's move:chop ratio
is actually *better* than peers', 1.52 vs 1.96); the gap is tree size at felling and
species mix (Oaxaca: 51% rate effect, 33% mix effect), root-caused to `chop_candidates`
scoring raw throughput (`1000·wood/turns`) with no awareness of who planted the crop —
confirmed by reconstructing 86.4% of real decisions with a port of the scorer. But the fix
class was not new: an opponent-crop-aware scoring bonus had already been tried and lost
−7.77 rating in the real arena (Phase 21), harvest-before-chop had already cost −2.325
margin on a 960-cell grid, and a third, structurally similar transplant of the chop layer
onto another bot went −61.7 against an adaptive opponent. The pattern repeats too
consistently to bet on a fourth attempt: isolated local-metric improvements break the
resident's coordinated schedule against adaptive opponents. B4.6 closed with no cycle
warranted, and with it the whole execution-class prospecting track.

By 2026-07-29 every route this programme ever identified had therefore been tried and
closed, each under its own frozen protocol:

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

The unifying finding is not eight unrelated dead ends; it is one shape. This
architecture's coordination — a hand-written two-worker policy that already chops what it
can reach, already suppresses competitively, and already wastes less than the agents
beating it — *is* its advantage, and every local improvement tried against any one
component broke the coordination that makes the whole work: production leaked more to the
opponent than it kept (D89, B4.5, D175a); a targeted execution fix that should have been a
free lunch lost in the real arena or on the evaluation grid, twice over, plus a
catastrophic transplant (B4.6); and even a perfect-information hindsight learner could
find no way to time the one intervention class that ever cleared a positive envelope,
because its positive contexts are not identifiable from the resident's own observables
(D172a). At equal roster the resident is not behind at all: B4.4 measured exact parity
with strong two-worker peers, 58.2% wins to 58.3%. The entire gap to the rank-3 bar is
downstream of scale-asymmetry survival — losing badly once outnumbered, never once
outnumbering. And scale itself is what this synthesis shows to be unaffordable: not
because the resident cannot mechanically mine or plant (D174a and D175a both prove it
can, exactly as specified), but because it cannot harvest what it produces (B3.5/D173: no
HARVEST candidate for busy units, `harvest_power: 0` for every trained one) — so every
turn spent producing pays the opponent more than it pays the resident itself. Further
gains are not available to this architecture; they require a differently-shaped one. That
is a project-scale decision for the owner, not a next experiment — see "The road ahead"
below for what actually remains.

## 17. Inflection points

- **D30** — our generated maps were unlike real maps; weeks of results invalidated, honest substrate built (D33).
- **D40** — a teacher economy good enough to learn from.
- **D97** — joint two-worker coordination has real, measured value.
- **D101** — the gap is production *persistence*, not suppression.
- **D161** — the alternative-economy substrate is weaker than the bot we already have; everything pivots resident-native.
- **D164→D167** — the missing field behavior distilled into one frozen-eligible option.
- **D172a** — exact zero-noise counterfactual labels prove the +10.671 envelope's value is real yet unlearnable from the resident's own observables; the definitive, method-agnostic closure of the Tier-2 learning route.
- **B4.4→D174a** — the scaling gap gets a mechanism: no plant-reap loop, a fruit-bound (not iron-bound) bill, and a single unconditional clause capping the bot at two workers.
- **D175a** — production is structurally negative for this architecture: the bounded-concurrency planting fix works exactly as designed (turn 199→13) and still costs −26.44 (Δown −5.41 vs Δopponent +21.09), the third confirmation after D89 and B4.5.
- **B4.6 → terminal synthesis** — the one lead that played to the architecture's own strength closes on its own history (this exact fix class already lost twice on the byte-identical binary); every route the programme ever found is now closed by measurement, and further gains require a different bot.

## 18. Lesson learnt — what rich players' persistent jobs taught us (D35a and descendants)

D35a decoded two frozen partitions of rich-player replays (a 12-game discovery and a
9-game confirmation split) into **persistent worker jobs**: multi-turn units of intent —
"this worker is renewing the farm", "this worker is felling and banking wood" — rather
than per-turn commands. It is one of the program's foundational results because both the
*finding* and the *representation failure* shaped everything after it.

**What the decode found.** The job vocabulary explains essentially all of what strong
players do: direct productive coverage 100% in both partitions, all-unit coverage
98.1%/99.5%, and 96.4%/99.0% of MOVE commands resolvable as travel *for* a job rather
than wandering. The median job runs six-to-seven turns — strong play is *committed*, not
per-turn reactive. In 62.7%/63.5% of multi-worker turns the workers hold **distinct
roles**, and just two job types — RENEW (renewable farm work) and FELL (chop-and-bank) —
account for **~94% of all non-idle activity**: the producer/producer/chopper field
mechanism in its rawest form.

**The representation lesson.** The obvious encoding — one flat categorical over whole-team
job signatures — failed its own gate: the top 32 team signatures covered only 86.56% of
discovery turns against a 90% floor, because teams of one to seven workers generate 176
signatures and a flat head would have to encode *team size* into *class identity*.
The verdict distinguished abstraction from representation: **keep the job abstraction,
discard the flat joint head, and factorize per worker** — centralized assignment,
collision-aware targets, deterministic banking/completion, and a separate global TRAIN
decision. That factorized interface became D35b–d (bundles, provenance, repetition), then
D97's validated joint assignments, and ultimately the q6 proposal ABI.

**What the lesson did *not* license.** Hard-coding the observed roles failed both ways:
a forced persistent chopper was inert (D46 — the D40 teacher already chooses FELL_BANK
whenever legal) and a forced persistent producer lost 12 points (D47) — the roles strong
players exhibit are *emergent from scheduling*, not rules you can bolt on. And the later
field audits sharpened the picture: what actually separates the top cohort is not holding
roles but **cycling** them — the same worker produces, suppresses, then produces again
(D164, 72% of top-5 games as sampled — 49.7% at population scale after B3.3), with
production *persistence* through interruptions as the
real differentiator (D101: they reap 24% of what they plant; the resident 0.94%). The
D-series' current thread — successor jobs, BANK_SEED returns, D168's bounded option — is
the direct descendant of D35a's job abstraction applied to that cycling.

## 19. Model architectures and situation encodings

Three encoding families and half a dozen model families recur across the arcs. This
section describes them concretely.

**The raw situation.** Every encoding starts from the same game state: a rectangular
board (up to 22×11 cells) of terrain (soil/water), trees (species PLUM/LEMON/APPLE/
BANANA/IRON-ore analogues, growth stage, hit points, ripe fruit), units (per-troll move
speed, carry capacity, hp, chop power, cargo), both players' banked inventories and
scores, and the turn number. The referee reveals all of it every turn — the encodings
differ in what they make *learnable*, not in what is visible.

**Family 1 — spatial planes (the curriculum actor, Arc A).** The Rust environment
serializes the situation as a **104-channel × 11 × 22 uint8 tensor**. Per-cell planes
encode validity (channel 0 doubles as the board mask), terrain, tree species/stage/fruit,
and unit positions; scalar facts are *broadcast* as constant planes — e.g. channels 56–61
own inventory and 62–67 opponent inventory (values quantized to uint8 at a ≈1/30 scale),
channels
74–78 the selected unit's move/carry/hp/chop/free-capacity stats — and explicit BFS
*distance planes* give the network pathfinding for free (added after pure PPO failed to
learn it). Actions are likewise spatial: **13 action planes × 11 × 22** — a masked
categorical over (action-type, cell), with the legality mask computed by the referee-exact
environment.

**The curriculum actor architecture** (`SpatialActorCritic`): a 3×3 conv stem
104→16 channels → **four residual blocks** (width 16, two 3×3 convs each) → an actor head
(1×1 conv to the 13 action planes, logits flattened and masked) and a critic head
(validity-masked global average pool → Linear 16→64 → tanh → Linear→1). Roughly 35k
parameters — deliberately tiny, because deployment must fit CodinGame: the accepted
pipeline quantizes it to **int8 inside a generated Rust kernel** (max logit drift
0.0000687, 512/512 identical masked choices) and, after the K2/V5 pattern of persistent
workspaces and reused buffers, runs a two-worker inference in **7.04 ms median /
17.6 ms warm p95** within a 68,988-byte single-file source. Training used PPO with a
0.10-weight teacher-auxiliary loss (pure PPO deterministically argmax-collapses) and
legal-action masking throughout.

**Family 2 — scalar situation vectors (selector era).** Where a decision attaches to a
*moment* rather than a cell, situations are flat feature vectors, always built from
observable state only (opponent identity is deliberately excluded — the submitted agent
cannot see it): the 56-feature deployable state of D61's option probes, the **64-field
state vector** of the q6 program (global economy, workforce, phase, remaining
intervention budget, previous-intervention kind), the 139/62/44-feature turn-100 economy
models of D63, and D78's spatial-relational add-ons (target condition, worker-to-crop
distance, occupancy) that lifted opponent-attack prediction to 0.9307 AUC. The recurring
finding: these snapshots *predict behavior* well and *transfer value* poorly — every
fitted value model on them collapsed one map-fold away (D153: +14–17 in fit, +1.8 held).

**Family 3 — proposal/action vectors (the q6 ABI).** Interventions are encoded per
*candidate action*: a **379-field proposal vector** (job kind, target class and crop
provenance, ETA, predicted deposit and rate, ownership, encoded cell geometry, and the
64-expert endorsement pattern) concatenated with the 64-field state = the 443-feature
rows of the D148/D151 corpora. The proposal *generator* is itself a model: the bank of
64 frozen D98 linear scorers, quantized to 6 bits per coefficient (**9,792 coefficients
in 9,180 base85 bytes**), whose per-root proposal union retains 86–88% of the exact joint
oracle — a compact action basis rather than a policy.

**Model families tried on these encodings**, smallest to largest: linear probes (224 and
379 weights — D61/D110), a 12-unit echo reservoir with a 52-parameter trained readout
(D76), a fully-trained 1,072-parameter recurrent controller (D77), tiny MLPs of 6–7k
parameters (D115 ReLU classifier; D153's state64+action379→16→1 value net), the
factorized 6,626-parameter proposal-ranker + 689-parameter act/wait gate (D117–D143), and
the 10,725-parameter recurrent shared-proposal policy of D108/D109/D158. The pattern
across all of them: capacity was never the binding constraint — representation and
objective were. What survived: dense exact-value *teachers* over these encodings (D113,
D152), the proposal-union action basis, and the rule that value must be computed at
decision time (rollouts) rather than fitted into a snapshot scorer.

## 20. Why the models kept failing — representation and objective, unpacked

Section 19 ends with a compressed claim: *capacity was never the binding constraint —
representation and objective were.* That sentence summarizes roughly sixty failed
learning experiments. This section unpacks it.

**How we know capacity was not the problem.** Models from 52 parameters to 10,725 failed
in the *same way*, and adding capacity never moved held-out performance: the
7,121-parameter value net fit its training folds at +14–17 and scored +1.8 one map-fold
away (D153); adding feature slices (D154), history memory (D155), or hierarchical lookup
(D156) changed nothing. Meanwhile a *parameter-free* hand decoder reproduced all 85,047
of the teacher decisions that a trained MLP captured only 85% of (D41a). The information
was present and representable — the models were being asked the wrong question in the
wrong language.

**Four representation diseases.**

- **Wrong function shape for the target.** The teacher's decision rule is lexicographic —
  strict priority tiers resolved by exact integer comparisons. Small MLPs express smooth
  blends of features and approximate hard nested precedence badly at any practical size
  (D41a: 85% vs the decoder's 100%). No amount of width fixes a primitive mismatch.
- **Snapshots don't carry causes.** A feature vector of the current moment encodes
  *correlates* of value on the training distribution, not the causal game-tree structure
  that produces value. Hence the sharpest split in the ledger: behavior prediction from
  snapshots worked beautifully (0.97 AUC for "who will scale", D63) while value
  prediction from the same kind of snapshot collapsed under any distribution shift —
  and model confidence *anti-correlated* with realized value (the top decile predicted
  +18.07 and realized −1.51; D153b). Same inputs, different question, opposite outcome:
  a representation boundary, not a data-volume problem.
- **Action spaces too coarse to contain the strategy.** With four semantic modes
  (balanced/harvest/renew/fell), every optimizer — PPO, CEM, evolutionary lineage
  search — converged to "always balanced" (≤1% deviations; D73–D77), because the choices
  that matter (*which* crop, *which* worker, *when exactly*) were not expressible in the
  vocabulary. The moment actions became concrete jobs (D97), +36.9 of oracle value
  appeared in the very same games. The state encoding was never the bottleneck there;
  the *action* encoding was.
- **One scalar forced to mean two things.** The proposal-ranking logit was implicitly
  asked to encode both relative preference and absolute safety. A translation-invariant
  ranking loss cannot calibrate absolutes: 82 of 98 losing interventions were ranking
  errors with a positive arm available at the same decision (D127), and bolting on a
  separate safety head failed because per-arm false positives compound across many
  proposals (D129).

**Four objective diseases.**

- **Pooled margin doesn't pin down the trade-offs.** Optimizing mean margin over a
  heterogeneous opponent population lets the learner buy points against one family by
  selling another — and *which* trade it makes is undetermined by the loss, so it rotated
  across independent panels (per-family correlation −0.014; D109). Nothing in the
  objective said "don't sacrifice anyone."
- **Margin permits self-harm.** Margin = own − opponent, so suppressing both scores
  nearly symmetrically looks acceptable to the gradient. Observed literally: −39.98
  opponent score bought with −41.74 own (D73, again in D109). The fix — an explicit
  own-score protection term — was proposed in D109's closing paragraph and never tested
  until D170.
- **Hard-argmax targets punish equally good actions.** The teacher picks one of several
  near-tied moves (70% of states had another action within five points; D152);
  cross-entropy against the single winner turns near-ties into hard negatives, capping
  even *training* accuracy near 20% (D149). The objective fought the structure of the
  task itself.
- **Grading on the wrong distribution.** Supervised imitation grades the policy on the
  teacher's states; deployment happens on the policy's *own* states, which drift
  immediately — −172.7 paired margin from autoregressive covariate shift (Phases 12–14).
  Even the *selection* objective had this disease for a while: fit-side regret
  anti-predicted transfer (r = +0.89 in the wrong direction; D131) until selection moved
  to held-out blocks (D134).

**Why D170 is shaped the way it is.** Each clause of the current experiment answers one
of these diseases: concrete validated options instead of coarse modes (action
representation); observable features with recurrent context, and value obtained from
actual rollouts rather than fitted snapshots (causal state); a single clean output —
invoke or keep (no dual-meaning scalar); paired-control reward to strip map-difficulty
variance; closed-loop training so the policy is graded on its own states; and the
four-way objective comparison whose whole point is the first two objective diseases —
group-DRO against family rotation, an explicit own-score protection term against
self-harm — under strictly out-of-fit selection. It is the first experiment in the
program where every previously identified failure mode has a specific countermeasure in
the design.

## 21. Why CPU and GPU training never agreed

The YT benchmark that decided where training runs (Arc A, D11 era) found the GPU path
**9.8× faster** (9,769 vs 995 transitions/s) — and rejected it anyway: the same frozen
hybrid-chopper evaluation scored **52/61 on CUDA versus 56/61 on CPU**, a 6.557-point gap
against the preregistered 5-point parity cap, while every other parity metric passed.
This is not a bug in either backend; it is the expected physics of the situation:

- **Floating-point addition is not associative.** GPU kernels (cuDNN convolutions,
  parallel reductions, tensor-core matmuls) sum in different orders than CPU BLAS, and
  may use different intermediate precisions (TF32, fused multiply-adds), so identical
  models on identical inputs produce logits differing in the last bits.
- **Reinforcement learning amplifies last-bit noise.** A last-bit logit difference flips
  an occasional near-tie action; a flipped action changes the trajectory; the changed
  trajectory changes the training data for every subsequent update. Unlike supervised
  learning — where the same noise stays bounded — the RL feedback loop compounds it into
  *macroscopically different policies*. That is exactly the observed signature: bitwise
  parity on static metrics, divergence only in rolled-out policy outcomes.
- **The same mechanism appears CPU-side with threads.** A 20-thread fit was not
  byte-stable for one seed (D117), and one threaded model hash differed at 2.4e-5 drift
  (D153) — parallel summation order again. Hence the house rules: **one deterministic
  training thread** for anything selected by byte-identity, thread-parallelism only for
  *evaluation* whose outputs are compared field-by-field, and byte-identical 1-vs-20
  repeats as a standing integrity gate.

The project chose reproducibility over throughput: the sole D11 training run went to
local CPU, and the frozen local/YT parity gate remains a precondition before any GPU
result may be *selected* (YT stayed in use for exactly-replayable map/reduce simulation,
where byte-parity was achieved and verified per shard).

## 22. The saved-games database

Everything field-related — loss diagnoses, archaeology, motif audits, opponent models —
runs on a locally saved corpus of real arena replays. Its shape as of 2026-07-27:

**What we have.**

- **8,122 raw replays, 2.4 GB**, in `data/raw/games/` — one JSON per finished arena game,
  containing the referee's full record: per-turn frames, both players' commands and
  stdout, map layout, and final scores. Every game sits on a distinct map (8,122 unique
  layouts); **469 distinct agents** appear, including 32 boss games. All 8,122 parse with
  0 failures (99.7% exact score reproduction, 0 unexpected mismatches). The 2026-07-28
  wide-lens collection quadrupled the corpus in one run (+6,231 games) by fetching the
  top-20's FULL visible battle windows and ranks 21–50 for the first time — the earlier
  10-per-agent sampling had been leaving ~85% of the rotating stream uncollected.
- **Two immutable D61p snapshots** (`data/raw/snapshots/20260721T105508Z-d61p/`,
  `.../20260727T130712Z-d61p/`) — 33 index/manifest files each: leaderboard state at
  collection time, request and source hashes for every fetch, and the open/sealed
  partition manifests. Snapshots are append-only; the collector refuses cache overwrite.
- **47 legacy battle records** in `data/raw/battles/` from the Gold-era collector — the
  previous tooling generation, kept for the historical corpus.
- Derived layers: decoded state streams validated turn-by-turn against the simulator
  (361,755 transitions, **zero material mismatches**; 28,416 position-only RNG
  differences), aggregate statistics (`data/processed/stats.json`), and per-experiment
  extracts (e.g. the D164 field-cycle tables).

**How we got them.** CodinGame exposes finished games through public replay endpoints:
a last-battles list per agent, and one replay JSON per game id. Collection is strictly
read-only (GETs only, throttled, hard-stop on HTTP 422/429) and each run is individually
authorized, the same discipline as arena writes. Two tool generations: the Gold-era
`collect.py` (fetch-log bookkeeping into `battles/`), superseded by the **D61p immutable
collector** (`data/scripts/collect_snapshot.py` + `parse_snapshot.py`), which hashes every
request and source body, refuses to overwrite cached games, deduplicates into the shared
`games/` store (2026-07-27 run: 198 fetched new, 195 skipped as cached, 220/220 requests
clean), and physically separates a **sealed confirmation partition** (currently 11 games)
that no analysis may open — it is reserved as untouched holdout for future candidate
confirmation. Every rebuild passes a QA gate: exact final-score reproduction (1,685
exact + 8 known penalty-only endings), tree invariants, and point-symmetry of every map.

**How we group them.** The groupings the experiments actually use:

- **By partition discipline** — OPEN vs SEALED-confirmation. The single most important
  split: sealed games are never decoded by exploratory analyses.
- **By subject** — resident appearances (203 in the current snapshot, 192 open) vs the
  top-source stratum (exactly 10 appearances per current top-20 agent — a deliberate
  stratified sample) vs boss games vs the long tail of the 345-agent population.
- **By rank cohort** — top-5 / ranks 6–20 / resident: the standard field split of
  D164–D167 (e.g. P→S→P cycles: 72% / 27% / 11% of appearances as sampled; the top-5
  figure is 49.7% at population scale after B3.3's re-powering).
- **By outcome** — wins vs losses; within losses, **catastrophes** (margin ≤ −100;
  19/192 open resident games, carrying 58% of negative-margin mass) vs ordinary losses;
  early-lead reversals (ahead at turn 100) as their own diagnostic cohort.
- **By matchup** — per-opponent records against the resident (historically the weakest:
  wala, delineate, norxondor — the 07-16 loss-analysis trio).
- **By behavioral motif** — analysis-derived labels: scaler vs non-scaler appearances
  (46/104 in D63), renewable-mode games (the yaichi study), worker-rich vs two-worker
  cohorts, pre-carry vs post-acquisition successor returns (D167).
- **By collection generation and era** — legacy Gold-era battles vs the Legend-era
  cumulative store vs dated immutable snapshots (which make "the field as of date X"
  a well-defined, hash-frozen object).

## 23. Glossary — mother, crop, orchard

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

## 24. Deep dive — D169, the option-envelope gate (standalone reading)

This chapter explains experiment D169 from scratch, including every experiment it builds
on. It assumes no other context. **Update (2026-07-29, full arc): D169 PASSED** — mean
envelope +10.671, CI [+9.420, +11.922], 65% of tasks improved, zero regressions, tails
better than control, on 100% panel coverage; every option was negative when always-on, so
all value is per-game selection. This cleared every frozen gate on the first pass and
authorized designing D170. D170a then hit an implementation bug (three trigger arms
structurally unreachable) and closed at Phase 1 as an implementation invalidation, not a
scientific closure; its mechanics-only repair, D170b, trained cleanly — 8/8 fits, all 13
arms live — but every one of the four objectives converged to always-KEEP on held
decisions (0/8 admitted): CLOSED-AT-PHASE-2, on-policy terminal-reward training cannot
find the envelope's rare positive contexts at any sane budget. The owner then reopened
Tier 2 for one further, differently-shaped attempt: D172a replaced on-policy reward with
exact, zero-noise counterfactual labels over 27,392 decision states and found signal 5×
the required floor (40.4% of states carry a ≥+2 option) — yet both a linear and an MLP fit
still failed held-out admission (+0.14 to +0.26 against the +1.5 gate). CLOSED-AT-SELECTION:
the positive contexts are not identifiable from the resident's own observables at all,
independent of training method — the definitive closure of the Tier-2 learning route. The
rest of this chapter describes the experiment as it was frozen before any of these
results; its reasoning for *why* the gate exists and *why* the thresholds are what they
are remains the authoritative explanation.

**What D169 is.** The live bot ("the resident") is a hand-written two-worker policy that
cannot be beaten by any replacement we have built, yet loses to the top of the ladder in
one measured way. The remaining strategy is to keep the resident exactly as it is and add
a small vocabulary of bounded, abortable interventions ("options") on top of it — then
*learn when to invoke them*. D169 is the go/no-go measurement for that entire strategy:
it computes, on 1,024 replayed games, the **hindsight envelope** — how much better each
game could have gone if, with perfect hindsight, we had picked the single best option (or
no option) for that game. The envelope is a ceiling, not a policy: if even the ceiling is
low, the strategy dies before any training budget is spent on it.

**Why this is the remaining strategy (the four results that force it).**

- *D159 — the loss mechanism.* On 200 arena games: ~11% of the resident's games are
  "catastrophes" carrying ~58% of all lost margin, and in most of them the resident is
  *ahead at turn 100* before being out-compounded. Replicated independently on fresh data
  (19/192).
- *D101 — the root cause.* Top agents harvest 24.16% of the crops they plant; the
  resident harvests 0.94%. Its suppression (chopping enemy crops) is already
  competitive — what it lacks is production *persistence* while interrupted.
- *D160 — why "just add a third worker" fails.* In 195 decoded games the resident never
  once accumulates the resources to train a third worker; affordability is a multi-turn
  funding *policy*, not a windfall you can wait for.
- *D161 — why "switch to a better economy" fails.* The best alternative complete economy
  we ever built (the D40 teacher family) is 37.8 points *behind* the resident head-to-head,
  and even a perfect per-game oracle over interventions on that substrate nets only +3.4
  (statistically indistinguishable from zero). Verdict: everything must anchor on the
  exact resident.

**What an "option" is.** A bounded intervention with exact-resident fallback: it may
route *one* worker through a short scripted sequence, holds a horizon (24–32 turns),
aborts back to the exact resident on any failure, and leaves every other worker untouched
every turn. Options are safe by construction — a game where an option never arms is
byte-identical to the resident's game (verified, not assumed).

**The D169 vocabulary, option by option.**

- `OPT_RETURN` — the *successor return*. Lineage: D164 found that in 72% of sampled top-5 games (49.7% at population scale, B3.3)
  the same worker produces → suppresses → produces again, while the resident does this in
  11%. D165 tested "walk back to the crop you remember" — zero support in 1,024 games
  (the old crop is always gone). D166 showed the real return is a multi-step journey
  (median 16 turns) starting empty-handed. D167 proved the journey is regular: in
  135/135 resident cases and 71.4% of top-5 field cases it is **BANK_SEED** — pick a
  seed from the deposited bank, walk, plant a new generation. D168 then scripted exactly
  that as an always-on controller and *lost* (−6.7 to −8.2 paired): forcing the return
  everywhere is worse than the resident's own judgment. The surviving question — the one
  D169 asks — is the per-game one: *are there games where invoking it would have won?*
  The envelope selects it only where it helps.
- `OPT_FRUIT`, `OPT_IRON`, `OPT_PROTECT` — three *resource-control* options from D162/
  D163: temporarily route one worker to fruit harvesting/banking, iron mining/banking, or
  consumption protection, under a fixed shadow reserve, then return. D163 proved each is
  *negative on average* when always-on (−2.0 / −3.6 / −0.03) — but D162 measured that the
  per-task envelope over this family is **+12.7 (CI +9.0 to +16.3) with zero
  regressions** on a 128-task panel. That asymmetry — bad always, good when selected —
  is precisely the signature of a timing problem, and timing problems are what the
  closed-loop program (D170) would learn. D169 re-measures that envelope at full scale
  (1,024 tasks) with the unified vocabulary.
- `TRIG` arming — each resource option also gets a variant armed by the *B3.1 trigger*:
  the audit of catastrophe games showed the resident's existing endgame switch cannot
  fire until the collapse has begun (it requires already being behind), but that the
  opponent visibly scaling past two workers precedes the collapse by **42–125 turns in
  84% of catastrophes**. That observable early warning becomes an arming condition here —
  making part of the envelope deployability-realistic, not just hindsight.
- *Predeclared extension (D169b):* if the envelope lands between +5 and +10, one
  addition is authorized — joint two-worker assignments in the style of D97, which proved
  (on the old substrate) that coordinating both workers' concrete jobs adds +9.2 beyond
  the best single-worker action at two-thirds of decision points. It is excluded from
  D169a only because it must be rebuilt resident-anchored, which costs implementation
  risk the first measurement doesn't need.

**The panel and the integrity discipline.** The 1,024 tasks are the consumed D148
evaluation panel: 64 official-generator maps × both seats × eight opponent families,
already used by D161/D167/D168 — reusing consumed data is *correct* here because an
envelope is an upper-bound measurement, not a selection (nothing is fitted; the
prohibition on fitting anything to envelope winners is itself a lesson, from D100b, where
hindsight winners proved map- and seat-specific with rank correlations of 0.10–0.22).
Every run must: reproduce the resident's 1,024 control games bit-for-bit against D161's
frozen records; prove inactive arms byte-identical to control; produce byte-identical
results at 1 and 20 threads; and apply crop safety *relative to control* (D122's rule —
judging absolute crop counts penalizes games the resident itself fails).

**The gates, and why these numbers.** Coverage ≥ 60% of tasks armable (else the
vocabulary is too narrow to matter). **PASS** needs mean ≥ +10 with CI lower bound ≥ +5,
≥ 30% of tasks improved, no negative opponent family, and tails no worse than control.
The +10 bar is set against the actual goal arithmetic: the code gap to rank 3 is roughly
4–6 arena points, and every translation step — envelope → learned policy → arena — has
historically lost margin (thirty-odd selectors captured under a third of their teachers'
value; the one arena promotion came from +4 local). A ceiling below +10 leaves no room
for those losses; below +5 (**KILL**) the class cannot even theoretically close the gap,
and the honest move is to stop. **BORDERLINE** buys exactly one extension (D169b), never
tuning.

**What happens after.** PASS does not create a bot — it authorizes designing D170: a
closed-loop learner over this vocabulary, whose central open question was posed by
D108/D109 and never answered: a *family-robust objective with own-score protection*
(recurrent policies trained on pooled margin kept "rotating" which opponents they beat,
correlation −0.014 across panels, while suppressing their own score). KILL closes Tier 2
of the backlog and the project holds at maintenance. Either verdict is recorded under the
same rules as the 168 experiments before it.

**Cast of experiments referenced here:**

| ID | Role in D169 |
|---|---|
| D97 | Joint two-worker assignment value (+9.2 beyond best-single) — the D169b extension |
| D100b | Why nothing may be fitted to envelope winners (hindsight doesn't transfer) |
| D101 | The root-cause diagnosis (reap 24.16% vs 0.94%) motivating the option class |
| D108/D109 | The unanswered objective question D170 would tackle after a PASS |
| D122 | The relative crop-safety measurement rule |
| D148 | Origin of the 1,024-task consumed panel |
| D159/D160/D161 | Loss mechanism; funding proof; substrate verdict — why options-on-resident is the only path |
| D162 | The option machinery and the +12.7 envelope precedent |
| D163 | The three resource options; proof they fail always-on (the timing signature) |
| D164–D167 | The successor-return lineage ending in BANK_SEED |
| D168 | Proof that scripting the return always-on loses; per-game selection is the open question |
| B3.1 | The observable opponent-scaling trigger (42–125 turns of warning) used for arming |

## 25. The road ahead — backlog

What remains, now that every technical route this programme could find has run to a
verdict (the terminal synthesis, above). The operational source of truth is
`docs/BACKLOG.md` (with gates and kill rules); this chapter is its narrative snapshot as
of 2026-07-29.

**What remains is maintenance.** The standing wide-lens collector runs on a daily cron
(05:17, `# troll-farm-wide-collect`), so the corpus keeps compounding at zero attention
cost — 8,131 games at its first run (2026-07-28) and growing — without any decision
needed. The resident (`6561795`) stays exactly as it was promoted on 2026-07-17, the
programme's only arena win, and the no-churn rule remains absolute: no arena write
without fresh, explicit authorization. Two genuinely minor items stay technically open
but are not routes back into this chapter: an unbuilt oscillation-breaker successor
(D171b, redesigned after D171a's failed mechanism fix; expected value small, since the
baseline audit already shows the resident wastes *less* than the agents beating it) and a
cold-file storage migration not yet ripe (B5.3, ≈2026-08-03). Both are the kind of cheap
filler the project has always allowed alongside maintenance, nothing more.

**What does not remain is a technical path forward.** Learned option selection,
on-policy closed-loop training, production, scaling, mining, harvest capability,
execution waste, and suppression efficiency are all closed by their own frozen protocols
— the full route-closure table is above. No further experiment against the current
architecture is evidence-permitted.

**The one substantive open decision belongs to the owner, not the ledger:** whether to
scope a different bot. This architecture's shape is also its ceiling — at equal roster it
already matches strong two-worker peers, and every measured attempt to grow past that
roster cost more than it returned. Closing the remaining gap to rank 3 is not available to
this bot through any route this programme found; it would require a differently-shaped
one, and that choice is the owner's to make, not the next entry in this ledger.

## 26. Where the records live

- Ledger vol 1 (Phases + D1–D166, frozen): `legend-top3-experiment-cycle-2026-07-18.md`.
- Ledger vol 2 (live): `legend-top3-experiment-cycle-vol2-2026-07-23.md`.
- Per-experiment records: `data/analysis/live-agent-6553250/dNNNa-*-{protocol,lock,result}*`.
- Closed branches by topic: `docs/CONSTRAINTS.md` (classes a–h). Live state: `docs/STATE.md`.
- Priorities and gates: `docs/BACKLOG.md`.
