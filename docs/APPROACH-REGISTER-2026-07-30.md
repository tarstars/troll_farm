# Approach register — every feasible direction, 2026-07-30

Owner directive: *"We are at a plateau and at this stage every idea is worth considering.
Make a backlog of all approaches which seem somehow feasible and just roll this backlog."*

This register is deliberately **inclusive rather than filtered**. The justification is
empirical: the integrator's value estimates were wrong four times in the 2026-07-29 sweep
(H7 proposed a mechanic that does not exist; H8's premise came from a stale census; H13's
headline deflated to score maturity; D176a's own gates were mis-specified). At a plateau,
cheap measurement is a better filter than judgment with that error rate.

## The rolling rule

**No value bar on audits.** Any read-only audit here may be claimed and run at any time.
Cheap measurement is the filter; it is not itself filtered.

**The ≥ +1.0 rating bar still applies to experiments.** Anything that modifies code, burns a
seed range, and consumes a panel cycle must be justified by an audit's honest value estimate
first. Evidence for keeping it: D175a −26.44, D174a −10.76, H1 −2.49, D176a +0.045 — four
cycles spent below the bar, none of which mattered.

**Programmes stay owner-gated.** A2 is authorized; further programmes are decisions, not
items.

**Discipline is unchanged.** Breadth means more items, not lower standards: frozen
protocols, preregistered gates, calibrated on the panel's own population, honest verdicts,
kill rules are successes. Every closed item gets a ledger entry and a CONSTRAINTS bullet.

Keep **2–3 audits in flight** at all times; integrate as they land; promote to experiment
only on a cleared bar. Status legend: `open` / `running` / `done` / `closed` / `gated`.

---

## A. Measurement and re-baselining — cheap, and they price everything else

| id | approach | cost | status |
|---|---|---|---|
| **N1** | Maturity-curve measurement | 1 session | **✅ DONE — PARTIAL / IMMATERIAL:** remaining uplift −0.1612, CI [−0.7525,+0.4567], projected mature score 21.3088; boundary-sensitive but closes passive maturity as a planning lever |
| **N2** | B4.4 verification sweep — its figures corrected twice already; verify or retire the rest | 1 session | **✅ DONE — B4_4_CORRECTED:** unique inferred 8,395 cut matches anchors; group rates reproduce, all/every-peer and no-loop claims fail; early orchard and late wood conversion separated |
| **M1** | **Rating-system dynamics** — how does the score actually update per win/loss? Recover the update rule from the snapshot series. If it is Elo-like, quantify how many wins a +1 move costs, which prices *every* candidate in wins rather than margin | ~1 session | **✅ DONE — PARTIAL / DESCRIPTIVE_ONLY:** 307/329 complete transitions; best held-agent MAE 0.4773 vs 0.4786 zero baseline; no wins-per-+1 |
| **M2** | **Opponent-specific systematic losses** — are there agents we lose to far more than our score predicts? A single exploitable matchup is worth more than a broad 1% gain | ~1 session | **✅ DONE — NO_ACTIONABLE_MATCHUP:** 3/72 exact identities clear support; R1FA is a stable negative hint but CI, Holm, and win-effect gates fail; BoatBuilder reverses by seat |
| **M3** | **Seat asymmetry** — do we underperform in one seat? Never audited; if real it is a targeted fix | hours | **✅ DONE — NO_ACTIONABLE_SEAT_ASYMMETRY:** matched seat-1−seat-0 +10.09, CI [−16.81,+38.91], p 0.484; identity-equal contrast −1.37 |
| **M4** | **Matchmaking composition** — who do we actually play, how often, and is the mix drifting? Bears on N1 and on whether score drift is pool or us | hours | **✅ DONE — NO_MATERIAL_MATCHMAKING_DRIFT:** mean +0.438, CI [−0.865,+1.867], p 0.884; late mix is 4 pseudonym lineages across 16 version IDs |
| **M5** | **Game-length / turn-limit effects** — the whole margin gap sat in 300-turn games (H3); characterise how outcome depends on length | ~1 session | **✅ DONE — NO_MATERIAL_LENGTH_ASSOCIATION:** matched cap residual −1.44, CI [−26.25,+25.11], p 0.710; win and stability checks reverse |

## B. Execution-class — the only family with a perfect arena-transfer record

| id | approach | cost | status |
|---|---|---|---|
| **N5** | Endgame opponent-plant contest — a mechanic the source design specifies and our code lacks | 1 session audit | **CORRECTED / RE-REVIEW PENDING:** 12 semantic tests pass; literal post-birth ETA leaves ceiling 11.99, CI [8.73,15.76] < 20 unchanged |
| **N6** | Denial-weight sweep — `900/(1+dist)` was never swept though the reproduction plan required it | 1 session | **✅ INDEPENDENTLY ACCEPTED / CLOSED_AT_DEVELOPMENT:** LOW −0.754; HIGH +0.559 but only 12/77 directional and 4/8 positive families; confirmation unused; keep 900 |
| **E1** | **Opening micro-optimality (first 3–5 turns)** — highest-leverage turns in the game; never audited for optimality against an exhaustive short-horizon search | ~1 session | **✅ CLOSED WITH N4 RUNTIME:** only the resident-pair prefix oracle survived scope review; N4's exhaustive publication is 210/333 ms p95 vs 5 ms, so no authorized surface remains |
| **E2** | **Banking-route efficiency** — round-trip path choice, door selection, and whether carry is ever wasted on a suboptimal return | ~1 session | **✅ DONE — ROUTE_RESIDUAL_OBSERVED / NO EXPERIMENT:** immediate and joint ETA regret 0; no door switches; hindsight alternate door saves 134 one-turn wood legs = 0.335 turn/side-game, future-conditioned with no causal/rating estimate |
| **E3** | **Chop-order within a tree cluster** — given several candidates, does order matter for total yield (growth during travel is modelled, but ordering may not be) | ~1 session | **✅ VOID_PREMISE_DUPLICATE:** exact-resident one-job and D36 repeated completion-boundary terminal oracles already include multi-tree ordering; D36 +10.633 vs +25 and explicitly closes further resident target/overlay iterations |
| **E4** | **Pathfinding tie-breaks** — BFS ties are broken by incidental cell order (this caused the oscillation family); audit whether other decisions inherit the same arbitrariness | ~1 session | **✅ DONE — KEEP_LEXICOGRAPHIC:** the distinct secure-orchard mother tie is active on 10/10 reused tied seeds and all six families, but reverse order loses −8.55 tied-map margin / −0.0855 exact-census-weighted; both seats and every family are negative |
| **E5** | **Ripeness-wait decisions** — when the bot waits for fruit, is the wait ever longer than the alternative work? (B3.6 found 20 benign cases; a targeted audit could find costly ones) | hours | **✅ DONE — KEEP_RIPENESS_WAIT:** next-best-task replanning activates 33/360 cells across both seats/all families, but gains only +0.1056; seat 0 −0.200, motion/race negative, 346/360 unchanged |
| **E6** | **Seed-carry decisions** — which seed to carry and when to drop it; never examined as a decision class | ~1 session | **✅ VOID_PREMISE_DUPLICATE:** D167 covers acquisition and field pre-carry; D168 covers post/pre timing, species tie-break, destination, and terminal displacement (−6.732/−8.207; all active families negative); DROP is generic banking |
| **E7** | **`typeToCut` rule optimality** — the first-turn species choice is one rule applied all game; test it against per-map hindsight | ~1 session | **✅ DONE — HINDSIGHT_RESIDUAL_ONLY:** blanket inversion loses −12.174, both seats/all families negative; seed-level hindsight gains +10.510, 24/60 seeds prefer FLIP, and 6/6 leave-one-family-out evaluations are positive; keep default |
| **E7a** | **Prospective `typeToCut` selector decision** — determine whether the E7 hindsight residual warrants a disjoint-map, predecision-feature selector protocol | hours audit | **gated on E7 peer acceptance:** specialized H11/L2 instance; no fitting, source edit, fresh panel, or candidate until transfer/substrate constraints are resolved |

## C. Search and lookahead — putibuzu reached #2 with depth-12 rollout + 3-ply beam

| id | approach | cost | status |
|---|---|---|---|
| **N4** | H6 residual: intertemporal choice among the resident's *existing* candidate pairs (value bound first) | 1 session | **✅ RUNTIME_CLOSE:** exact reconstruction/parity pass, but exhaustive pair export + one-tick boundaries is 210/333 ms p95 vs 5 ms and 83.3 MB for one root; no Phase B |
| **S1** | **Endgame exact solver** — the last N turns have a small reachable state space; solve them exactly instead of greedily | 1–2 sessions | **✅ DONE — FULL_EXACT_INFEASIBLE:** 34.17% reach t251 and 21.53% reach t291; movement-only simultaneous one-ply outcomes are median 600/max 6,400, but full exactness spans 10–50 turns plus opponent/chance/non-MOVE branches; known-policy processes cannot clone and candidate restriction duplicates N4/D36/S3 |
| **S2** | **Opening book per map class** — precompute strong first-K-turn sequences offline, look them up at runtime for ~0 ms | 1–2 sessions | **DEPENDENCY_GATED_REPRESENTATION_BLOCKED:** N4→E1 is now runtime-closed, every implemented library is closed, and D63/D91/Phase 15/D153 supply no transferable pre-action map representation |
| **S3** | **putibuzu-shaped rollout+beam, scoped precisely** — several MC/rollout families are closed; determine exactly which and whether his specific combination is outside them before proposing | 1 session audit | **✅ DONE — DISTINCT_MULTI_GATED:** the combination is outside every strict closure, but the public specification is incomplete, local opponent/value models fail transfer, and exact-resident subsets miss 50 ms |
| **S3a** | **Search-kernel specification and latency preflight** — choose resident-pair overlap versus a clean-room broad greedy controller, freeze every omitted semantic, then test legality/timing before value | hours audit | **gated on S3 peer acceptance and N4 Phase A ownership fork; no implementation or panel authorized** |

## D. Learning — delineate reached #1 with a trained network and no search

| id | approach | cost | status |
|---|---|---|---|
| **H10a** | Spatial-planes probe: swap D172's feature extractor for the 104-channel board, all gates frozen. The one reopening CONSTRAINTS sanctions | readiness audit | **✅ NARROWED_TO_GENERIC_SPATIAL_AUGMENTATION:** literal 104 is invalid (32 Level-1-specific channels); D172's exact official substrate supports a 72-channel current-state tensor plus its 17-field decision block |
| **H10a-r1** | **Generic spatial-state option scorer** — compose-only state export, then one 6,541-parameter spatial fit with every D172 gate frozen | 1–2 sessions | **gated on H10a peer acceptance; no exporter, fit, or range authorized yet** |
| **H10b** | Whole-policy self-play network over primitives — the delineate-shaped route; never attempted (our closures cover option-selection and imitation, not this) | multi-session programme | **gated** (owner) |
| **L1** | **Behaviour cloning from delineate specifically** — exact-agent replay imitation at the current corpus scale | 1–2 sessions | **✅ READINESS DONE — DISTINCT_PRIMITIVE_ONLY:** 199 games / 145,448 decision rows decode exactly; final primitive commands and actual TRAINs are labels, but hidden train-plan/logit/beam targets are not; L1a extractor is peer-gated and any fit remains closed-loop-gated |
| **L2** | **Learned tie-break / target ranking inside the existing architecture** — narrow learning at one decision point rather than whole-policy or option selection; a third target neither closure covers | 1–2 sessions | **✅ CLOSED BY N4 RUNTIME:** the sole unconsumed pair surface cannot be published within its frozen budget; no L2a |
| **L3** | **Learned evaluation function for the existing scheduler** — replace the hand-tuned score with a fitted one, same action space | 1–2 sessions | **✅ CLOSED BY N4 RUNTIME:** imitation/broad value remain consumed and the sole pair-continuation target cannot be published within budget; no L3a |

## E. Economy and architecture

| id | approach | cost | status |
|---|---|---|---|
| **A2-0a** | Renewable-base feasibility (= N3) | 1 session | **✅ DONE — feasibility qualified; base sub-critical and LABOR-limited (R≈0.75; 0.40 fruit/turn realized vs 2.5–6.8 ceiling); partial renewal is useful but reliable self-replacement is not assumed** |
| **A2-0b** | Referee/evaluation parity harness for a new bot | 1 session | **✅ QUALIFIED AND PROTOCOL-CLOSED — exact legacy reproduction; locked referee RNG/validation path; four Phase-1 conditions carried forward** |
| **A2-1** | Economy skeleton: early orchard establishment/reap → bank + opportunistic mine → fruit-funded worker 3; late fruit-to-wood conversion is distinct | 1–2 sessions to first gate | **CLOSED / FAILED K1 — 582/2,048 = 28.42% by t≤110 vs 40%; mechanics and integrity pass, transfer does not** |
| **A2-2…5** | Equal-roster parity → scale survival → same-panel dominance/deployability → Arena | programme | **CLOSED by A2-1 K1; new owner-authorized programme required to reopen** |
| **N7** | Dead-accretion removal plan (`ScarceIntent`, `banana_factory`, `task_market`, opponent-crop scoring are unreachable) | 1 session plan | **✅ DONE — DEPLOYMENT_ALREADY_SLIM:** all four are absent from the 62,725-byte live deploy, so its additional deletion ceiling is 0 bytes; sacred source/snapshot and research APIs stay byte-exact |

## F. Opponent interaction — deflated by H5 but not closed

| id | approach | cost | status |
|---|---|---|---|
| **H4** | Deniability census: what currency paid the opponent's worker-3 bill, and was it contestable in the B3.1 window | 1 session | **✅ DONE — NO_MATERIAL_DENIABLE_BILL:** all 17 scale-linked catastrophe bills need post-start supply; 73 batches are individually mandatory, but 43 are non-deniable IRON and 30 fruit yield 0 legal already-positioned HARVEST/lethal-CHOP blocks; reachability alone fires misleadingly in 17/17 |
| **H7′** | Action-contention audit (races, duplication, target disappearance — **not** body-blocking, which is mechanically impossible) | 1 session | **✅ DONE — NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE:** exact contention is ubiquitous (180/200 games; 3,662 dual CHOP turns), but top-20 prevalence is only +5.76 pp versus rank-41+ with identity-cluster CI [−1.64,+14.49], and its turn rate is lower (47.87 vs 78.93/1k); no controller |
| **H3′** | Contact-coverage stability under numeric pressure — causality first, then a load-bearing-conditioning control arm | 1 session | **✅ DONE — TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY:** exact matched DiD hazard ratio 0.606, CI [0.410,0.895]; entirely pre-loss ratio 0.510, CI [0.293,0.841]; observational only |
| **H3a** | Three-arm numeric-pressure value preflight: conditioned change vs identical always-on change vs unchanged control | 1 session after protocol | **SOURCE RECONSTRUCTION ✅ TREATMENT_REPRODUCIBLE:** exact fallback↔treatment and archived generator equality pass across seven classified edits; separate three-arm protocol still required, no runner/panel |
| **B3.11** | Relative fruit control: early recurring-orchard denial + unsafe-production restraint + controlled ripe harvest | read-only precheck | **REVIEW-BLOCKED:** game 896352129 has 83 opponent door-apple HARVEST commands and 22 resident ripe-chop commands; command/unit-flow and decisive-state appendix require correction; one-game only, no policy/panel |
| **B3.12** | Denial-feasibility accounting: liquid target currency + renewable supply versus travel/chop burden and bill timing | owner-directed Arena trial | **IN FLIGHT:** exact game motivated a BFS-distance-3 exception; full trolls keep chopping far focus trees and discard overflow instead of returning. Candidate agent 6585578 / submission 41070584; no scientific qualification inferred |
| **F1** | **In-game opponent-archetype detection** — identify who we are playing and adapt. Endgame-switch retuning is closed; *archetype detection itself* was never tried | 1–2 sessions | **READINESS PROPOSAL ACCEPTED / QUEUED:** legal state history, whole-map-root folds, command/label deletion, static/permutation controls; no adaptation |

## G. Mechanics and platform

| id | approach | cost | status |
|---|---|---|---|
| **X1** | **Systematic mechanics re-derivation — PROMOTED 2026-07-30.** No longer speculative: A2 Phase 0a found an **undocumented per-player starting bank of ~24 fruit / ~6 iron**, verified in `official_mapgen.rs` and absent from `docs/mechanics.md` — an input to *every* affordability calculation this project has run. If one rule was missing, others may be. Differential-test the simulator against the referee across edge cases | 1–2 sessions | **✅ DONE — core match; starting bank was documentation-only; movement RNG + strict command validation become A2-0b obligations** |
| **H9** | Submission timing | owner | passive-maturity timing closed by N1; ordinary qualified-candidate promotion discipline remains |
| **H11** | Map-conditioned configuration as a controlled decomposition only (D63/D91 stand) | 1 session | **✅ DONE — DECOMPOSED_NO_GENERIC_TASK:** D63/D64 and D91 close the umbrella; E7a and S2 remain separately gated children |
| **H12** | Standing surveillance — cron plus weekly comparative refresh | automatic | running |
| **B5.3** | Cold-file migration | hours | ripens ~08-03 |

---

## Immediate roll

**Done 2026-07-30:** N1 (PARTIAL/IMMATERIAL); M1 (PARTIAL/DESCRIPTIVE_ONLY);
N2 (B4_4_CORRECTED); M2 (NO_ACTIONABLE_MATCHUP);
M3 (NO_ACTIONABLE_SEAT_ASYMMETRY);
M4 (NO_MATERIAL_MATCHMAKING_DRIFT);
M5 (NO_MATERIAL_LENGTH_ASSOCIATION);
N5 (NO_MATERIAL_CONTEST_OPPORTUNITY);
N6 (CLOSED_AT_DEVELOPMENT);
E2 (ROUTE_RESIDUAL_OBSERVED / NO EXPERIMENT);
E3 (VOID_PREMISE_DUPLICATE);
E4 (KEEP_LEXICOGRAPHIC);
E5 (KEEP_RIPENESS_WAIT);
E6 (VOID_PREMISE_DUPLICATE);
E7 (HINDSIGHT_RESIDUAL_ONLY);
S1 (FULL_EXACT_INFEASIBLE);
S2 (DEPENDENCY_GATED_REPRESENTATION_BLOCKED);
S3 (DISTINCT_MULTI_GATED);
H10a readiness (NARROWED_TO_GENERIC_SPATIAL_AUGMENTATION);
L1 readiness (DISTINCT_PRIMITIVE_ONLY);
A2-0a (feasibility qualified); X1
(core match, reviewed); A2-0b (QUALIFIED and protocol-closed); A2-1
(FAILED K1, programme stopped). **Held by `chatgpt_1`:** N4 Phase A; the evidence-index
pilot is in correction after its semantic line-locator blocker.

Priority order as of 2026-07-31: E7/S1/S2/S3/H10a/L1 peer review / E7a, S3a,
H10a-r1, and L1a decisions → evidence-index acceptance after correction → remaining D-tier
learning audits. N4 Phase A runs separately.
