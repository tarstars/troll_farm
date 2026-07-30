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
| **M5** | **Game-length / turn-limit effects** — the whole margin gap sat in 300-turn games (H3); characterise how outcome depends on length | ~1 session | open |

## B. Execution-class — the only family with a perfect arena-transfer record

| id | approach | cost | status |
|---|---|---|---|
| **N5** | Endgame opponent-plant contest — a mechanic the source design specifies and our code lacks | 1 session audit | open |
| **N6** | Denial-weight sweep — `900/(1+dist)` was never swept though the reproduction plan required it | 1 session | open |
| **E1** | **Opening micro-optimality (first 3–5 turns)** — highest-leverage turns in the game; never audited for optimality against an exhaustive short-horizon search | ~1 session | open |
| **E2** | **Banking-route efficiency** — round-trip path choice, door selection, and whether carry is ever wasted on a suboptimal return | ~1 session | open |
| **E3** | **Chop-order within a tree cluster** — given several candidates, does order matter for total yield (growth during travel is modelled, but ordering may not be) | ~1 session | open |
| **E4** | **Pathfinding tie-breaks** — BFS ties are broken by incidental cell order (this caused the oscillation family); audit whether other decisions inherit the same arbitrariness | ~1 session | open |
| **E5** | **Ripeness-wait decisions** — when the bot waits for fruit, is the wait ever longer than the alternative work? (B3.6 found 20 benign cases; a targeted audit could find costly ones) | hours | open |
| **E6** | **Seed-carry decisions** — which seed to carry and when to drop it; never examined as a decision class | ~1 session | open |
| **E7** | **`typeToCut` rule optimality** — the first-turn species choice is one rule applied all game; test it against per-map hindsight | ~1 session | open |

## C. Search and lookahead — putibuzu reached #2 with depth-12 rollout + 3-ply beam

| id | approach | cost | status |
|---|---|---|---|
| **N4** | H6 residual: intertemporal choice among the resident's *existing* candidate pairs (value bound first) | 1 session | open — **reserved for `chatgpt_1`** |
| **S1** | **Endgame exact solver** — the last N turns have a small reachable state space; solve them exactly instead of greedily | 1–2 sessions | open |
| **S2** | **Opening book per map class** — precompute strong first-K-turn sequences offline, look them up at runtime for ~0 ms | 1–2 sessions | open |
| **S3** | **putibuzu-shaped rollout+beam, scoped precisely** — several MC/rollout families are closed; determine exactly which and whether his specific combination is outside them before proposing | 1 session audit | open |

## D. Learning — delineate reached #1 with a trained network and no search

| id | approach | cost | status |
|---|---|---|---|
| **H10a** | Spatial-planes probe: swap D172's feature extractor for the 104-channel board, all gates frozen. The one reopening CONSTRAINTS sanctions | 1–2 sessions + GPU | open |
| **H10b** | Whole-policy self-play network over primitives — the delineate-shaped route; never attempted (our closures cover option-selection and imitation, not this) | multi-session programme | **gated** (owner) |
| **L1** | **Behaviour cloning from delineate specifically** — it is on our ladder and in the corpus; imitation failed before on covariate shift, but never from the #1 agent with today's corpus size | 1–2 sessions | open |
| **L2** | **Learned tie-break / target ranking inside the existing architecture** — narrow learning at one decision point rather than whole-policy or option selection; a third target neither closure covers | 1–2 sessions | open |
| **L3** | **Learned evaluation function for the existing scheduler** — replace the hand-tuned score with a fitted one, same action space | 1–2 sessions | open |

## E. Economy and architecture

| id | approach | cost | status |
|---|---|---|---|
| **A2-0a** | Renewable-base feasibility (= N3) | 1 session | **✅ DONE — feasibility qualified; base sub-critical and LABOR-limited (R≈0.75; 0.40 fruit/turn realized vs 2.5–6.8 ceiling); partial renewal is useful but reliable self-replacement is not assumed** |
| **A2-0b** | Referee/evaluation parity harness for a new bot | 1 session | **✅ QUALIFIED AND PROTOCOL-CLOSED — exact legacy reproduction; locked referee RNG/validation path; four Phase-1 conditions carried forward** |
| **A2-1** | Economy skeleton: early orchard establishment/reap → bank + opportunistic mine → fruit-funded worker 3; late fruit-to-wood conversion is distinct | 1–2 sessions to first gate | **CLOSED / FAILED K1 — 582/2,048 = 28.42% by t≤110 vs 40%; mechanics and integrity pass, transfer does not** |
| **A2-2…5** | Equal-roster parity → scale survival → same-panel dominance/deployability → Arena | programme | **CLOSED by A2-1 K1; new owner-authorized programme required to reopen** |
| **N7** | Dead-accretion removal plan (`ScarceIntent`, `banana_factory`, `task_market`, opponent-crop scoring are unreachable) | 1 session plan | open |

## F. Opponent interaction — deflated by H5 but not closed

| id | approach | cost | status |
|---|---|---|---|
| **H4** | Deniability census: what currency paid the opponent's worker-3 bill, and was it contestable in the B3.1 window | 1 session | open |
| **H7′** | Action-contention audit (races, duplication, target disappearance — **not** body-blocking, which is mechanically impossible) | 1 session | open |
| **H3′** | Contact-coverage stability under numeric pressure — causality first, then a load-bearing-conditioning control arm | 1 session | open |
| **F1** | **In-game opponent-archetype detection** — identify who we are playing and adapt. Endgame-switch retuning is closed; *archetype detection itself* was never tried | 1–2 sessions | open |

## G. Mechanics and platform

| id | approach | cost | status |
|---|---|---|---|
| **X1** | **Systematic mechanics re-derivation — PROMOTED 2026-07-30.** No longer speculative: A2 Phase 0a found an **undocumented per-player starting bank of ~24 fruit / ~6 iron**, verified in `official_mapgen.rs` and absent from `docs/mechanics.md` — an input to *every* affordability calculation this project has run. If one rule was missing, others may be. Differential-test the simulator against the referee across edge cases | 1–2 sessions | **✅ DONE — core match; starting bank was documentation-only; movement RNG + strict command validation become A2-0b obligations** |
| **H9** | Submission timing | owner | passive-maturity timing closed by N1; ordinary qualified-candidate promotion discipline remains |
| **H11** | Map-conditioned configuration as a controlled decomposition only (D63/D91 stand) | 1 session | open, low |
| **H12** | Standing surveillance — cron plus weekly comparative refresh | automatic | running |
| **B5.3** | Cold-file migration | hours | ripens ~08-03 |

---

## Immediate roll

**Done 2026-07-30:** N1 (PARTIAL/IMMATERIAL); M1 (PARTIAL/DESCRIPTIVE_ONLY);
N2 (B4_4_CORRECTED); M2 (NO_ACTIONABLE_MATCHUP);
M3 (NO_ACTIONABLE_SEAT_ASYMMETRY);
M4 (NO_MATERIAL_MATCHMAKING_DRIFT);
A2-0a (feasibility qualified); X1
(core match, reviewed); A2-0b (QUALIFIED and protocol-closed); A2-1
(FAILED K1, programme stopped). **Held by `chatgpt_1`:** N4 Phase A; the evidence-index
pilot is in correction after its host generator/output-parity blocker.

Priority order as of 2026-07-30, highest unassigned first: **M5** (game-length /
turn-limit effects) → evidence-index acceptance after correction
→ then B-tier execution and C/D-tier search/learning audits in id order. N4 Phase A runs
separately.
