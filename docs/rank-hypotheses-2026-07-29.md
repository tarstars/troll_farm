# Twelve hypotheses for improving rank — 2026-07-29

Author: `claude_1` (integrator). Status: hypotheses, not verdicts. `docs/CONSTRAINTS.md`
still binds: none of these may be implemented without a frozen protocol, and the ones that
touch closed classes state their reopening justification explicitly. Context: the
2026-07-29 terminal synthesis closed all eight single-lever routes for the current
architecture; resident 6561795 sits ~43/112 @ 21.97 vs a 28.22 bar. What follows is what
remains genuinely open, ranked by expected value × evidence-groundedness.

Recurring numbers cited below: at equal roster we match strong two-worker peers (58.2% vs
58.3% win); outnumbered we collapse (−37.1 vs their −1.8 at 2v3; 5.0% vs 13.7% wins at
2v4+); a worker prices at +2–4 rating (2→4 ≈ +5.2, 84% of the gap); we reap 0.93% of our
crops, peers 15–17%, top-3 24.16%; the top cohort trains first at median turn 2, we at 8.

---

## H1. The joint economy package — all four levers at once

**Hypothesis.** Lifting `harvest_power: 0`, the `can_train` two-worker cap, bounded early
planting, and banking support **together** produces a viable economy where each lever
alone was measured harmful, because each closure's own root cause was a missing
complement.

**Evidence for.** The single-lever post-mortems form a closed loop of missing complements:
D174a mined 10.6× more iron that nothing could spend (fruit binds the real bill; the cap
blocks training regardless); D175a planted at turn 13 but reap *fell* to 0.45% (nobody can
harvest); D173b cured 99.9% of reachable harvest-slack but 99.93% of the vein needs
harvest-capable trained units. Every strong agent above ~rank 40 runs the coupled loop
(66% of top-5 bills earned, 76% of that fruit).

**Closures touched.** D173a/b, D174a, D175a — all single-lever tests. Reopening
justification: the terminal synthesis's own mechanism ("local improvements break the
coordination") predicts single levers fail and says nothing about the joint change; each
result document independently identified the missing complement. This is the minimal
non-local intervention, and it is the correct test of the production+consumption thesis.

**First step.** One frozen protocol (D176): all four deltas, 256-map paired panel, the
D89 safety ratio unweakened, catastrophe/family/tail floors retained. **Cost:** 1–2
sessions. **Honest risk:** D92's composition failure and the six negative re-architectures
say combinations of negatives usually stay negative; the counter-argument is that none of
those combinations completed the currency loop.

## H2. Architecture-2 — a peer-shaped rebuild on a parallel track

**Hypothesis.** A new bot designed from turn one around the coupled economy (plant
21–29, ~5–6 concurrent crops, harvest-capable workers, fruit-funded TRAIN at turn ~2,
suppression retained as a subsystem) can reach the top-5 region that grafts can never
reach, because coordination must be designed jointly, not patched in.

**Evidence for.** B4.3's pricing (+5.2 rating for the roster alone); top-5 score 215.6 vs
our 185.7; the referee-exact simulator, 8,131-game corpus, panel machinery, and promotion
runbook all transfer to any new bot unchanged. The resident holds the ladder slot at zero
risk while this proceeds — the two tracks do not compete.

**Closures touched.** None — every closure in CONSTRAINTS is scoped to the resident's
architecture. **First step.** A design document deriving the target shape from the field
evidence (B4.4/B3.7/B3.8 give the spec: tempo, concurrency, funding split, disposition),
then a skeleton bot vs the 8-family panel. **Cost:** the largest — a multi-session
program; natural fit for the multi-agent protocol (parallel worker agents, `claude_1`
integrating). **Risk:** six re-architectures failed before — but all six predate the
week's causal understanding of *why* the economy shape matters.

## H3. The no-loop quartet — how do our twins outrank us?

**Hypothesis.** Escdemon, therealbeef, yamo, and mehdi_ayari share our exact profile
(roster 2.00, no sustained farm loop) yet rank above us — so a way to survive scale
asymmetry *without* farming exists and is observable in 8,131 replays.

**Evidence for.** B4.4 flagged them as the honest caveat to the no-farming story: for
them, only suppression efficiency (0.31 vs 0.43 wood/chop) plus possible maturity
confounds explain the gap. Strong two-worker agents hold −1.8 at 2v3 where we hold −37.1;
whatever produces that 35-point swing is the single most valuable unexplained fact on the
board, and it is *compatible with our architecture by construction*.

**Closures touched.** None — this is a read-only field study. **First step.** Per-agent
deep-dive: their games against 3–4-worker opponents specifically — posture, banking
timing, denial patterns, map choices, score trajectories. **Cost:** one session,
delegable. **Expected value:** either an execution-class mechanism we can copy (the only
class that ever transferred), or proof the quartet's edge is maturity/pool artifact —
both useful.

## H4. Opponent-scaling denial — attack their worker 3, not our worker count

**Hypothesis.** The catastrophe signature (opponent reaches ≥3 workers, crossover follows
42–125 turns later, 84% of catastrophes — B3.1) is preventable from our side: their TRAIN
bills need PLUM/LEMON/IRON exactly as ours do, and timed denial of that currency inside
the warning window delays or cancels their scaling.

**Evidence for.** Denial is our proven comparative advantage (the only positive lever in
D175's data was the +21 the *opponent* gained when we farmed instead of suppressing —
inverted, that is the price of suppression). The field demonstrates crop theft at scale:
15.7% of top-5 crops are chopped by opponents; top-5 themselves seed 23.8% of returns from
opponent fruit; we do this 0 times in 1,024 audited cases. Iron-source interference is
entirely unexplored.

**Closures touched.** Phase 21's generic opponent-crop scoring bonus (−7.77 arena) — the
distinction is *timed, trigger-conditioned denial of training currency during the B3.1
warning window*, not a global re-weighting active from turn one. That distinction is
argued, not proven; the protocol must include an always-on control arm to show the timing
is load-bearing. **First step.** Read-only: in catastrophe games, measure what currency
the opponent's worker-3 bill actually consumed and whether it was deniable (reachable by
our units in the window). **Cost:** audit one session; experiment 1–2 more.

## H5. Postmortem intelligence — read what the top players wrote

**Hypothesis.** The contest ended 2026-05-25; CodinGame top players routinely publish
postmortems (forum, blogs, GitHub). delineate, norxondor_gorgonax, and MSz's own
descriptions of their strategies would replace expensive replay inference with stated
mechanisms.

**Evidence for.** Two months of ladder archaeology recovered the field's shape at great
cost (D164's motif rate needed a 4× corpus and a correction); a single postmortem
paragraph could have stated it. We have never once searched. **Closures touched.** None.
**First step.** Web search for "Spring Challenge 2026" postmortems and the top handles;
summarize mechanisms against our audit findings. **Cost:** hours, delegable, zero
platform interaction. **Expected value:** unbounded downside protection — cheapest
possible check that our hard-won model of the field matches what the field says about
itself.

## H6. Targeted subgame lookahead — think deeper, same values

**Hypothesis.** The resident decides in ~7 ms of a 50 ms budget with a one-ply greedy
scheduler (`1000·wood/turns`). Spending the idle 40 ms on 2–3-ply lookahead for the two
decision classes where greediness measurably loses — contested-tree races and
size-at-felling — improves execution without changing any value, sidestepping the
"local-metric improvements break coordination" failure class.

**Evidence for.** B4.6 decomposed our wood/chop gap into tree size at felling (37.8%
size-1 vs peers' 22.9%) and kind-mix — both are horizon artifacts of one-ply greed, not
scoring errors. The closed failures (Phase 21, harvest-before-chop) all *changed the
objective*; deeper optimization of the *same* objective is untested. Full-game MCTS was
closed at 209 ms — bounded subgame search is a different budget class.

**Closures touched.** The B4.6 "no cycle" verdict covered re-scoring interventions;
lookahead is argued to be outside it — the protocol must prove the argument with the
family/tail floors that caught every previous coordination break. **First step.**
Offline: replay real decisions with a 2-ply oracle and measure how often it disagrees
with the live choice and what the disagreement is worth. **Cost:** audit one session;
implementation only if the oracle gap is material.

## H7. Physical interference — the unaudited mechanic class

**Hypothesis.** Body-blocking, door camping, and path denial are legal, potentially
valuable, and have never been audited in either direction — neither what opponents do to
us nor what we could do to them.

**Evidence for.** The oscillation work proved pathing interacts with unit-blocking (our
own units block each other; `force_unique_door_clear` exists precisely because door
blocking matters). The corpus can answer cheaply whether strong agents use deliberate
interference. Any finding would be execution-class — the only family with a 100%
arena-transfer record. **Closures touched.** None. **First step.** Corpus audit:
detector for opponent-adjacent stalls, door occupancy by non-owner units, and forced
detours; compare cohorts. **Cost:** one session, delegable.

## H8. Worker-2 timing — the unaudited five turns

**Hypothesis.** The top cohort trains first at median turn 2; we train at median turn 8.
Worker-2's affordability window has never been audited (D160 audited worker-3 only). If
the bill is affordable before turn 8, five to six turns of doubled early labour compound
for the whole game.

**Evidence for.** Every priced effect this week scaled with early tempo; the +3.0 stack's
pre-seed timing fix was exactly this shape and transferred. **Closures touched.** None —
opening timing of worker-2 was never tested. **First step.** Read-only: per game, first
turn at which worker-2's actual bill was coverable vs the turn we trained. **Cost:**
hours. **Risk:** the gap may be geometry (travel to the door), not decision — the audit
distinguishes them.

## H9. Identical-source resubmission A/A — re-price ourselves on today's pool

**Hypothesis.** Our 21.97 was frozen on the 2026-07-19 pool; since then 29 first-seen
agents entered and we drifted 40→43 passively. An identical-source resubmission would
re-converge on today's pool — possibly above the frozen score, and in any case producing
the only current measurement of our true standing.

**Evidence against, stated first.** Fresh reads sit 3–4 points *below* mature ones, so
this costs days of depressed visible standing; the null expectation is convergence at or
slightly below 21.97 (the pool got stronger, not weaker). **Why it still ranks.** It is
step one (capacity A/A) of any future promotion anyway; the runbook is verified; the risk
is bounded by the exact-restore procedure; and it is the only hypothesis that touches the
scoreboard without touching code. **Gate.** Owner authorization, explicitly — this is an
Arena mutation under protocol §6. **Cost:** ~1 day of standing, zero code.

## H10. Spatial-planes learner — the sanctioned residual for the +10.7 envelope

**Hypothesis.** D172a proved the envelope's positive contexts are unlearnable from the
64-field observable vector — but the one untried observation class is the full spatial
board (the 104-channel planes the curriculum actor used). If positive contexts are
*spatially* recognizable, the learning route revives with a +10.671 measured ceiling
behind it.

**Evidence for.** CONSTRAINTS' own ★FINAL bullet names this the sole permitted reopening
path (D29's spatial option-critic died of the pre-D33 map-domain artifact and was never
retried on the valid substrate). The label corpus already exists (79,997 exact
counterfactual labels, committed machinery). **First step.** Cheap and decisive: refit
D172's exact protocol swapping only the feature extractor for spatial planes — signal
floor and LOBO gates already frozen, one delta. **Cost:** 1–2 sessions + GPU. **Honest
prior:** low — but it is the largest measured ceiling still standing, and the incremental
cost over the existing machinery is small.

## H11. Map-conditioned configuration — find where the deficit lives

**Hypothesis.** The resident plays one fixed configuration on every map; if our deficit
concentrates on a map class (richness, size, iron placement), a map-gated parameter
variant recovers points a global retune cannot.

**Evidence for.** Map-richness gating exists in the code (D91's selector); D171's worst
case, D173/174/175's worst families were map-structured (compact_gold repeatedly).
**Closures touched.** D91 failed on map-cluster support (CI [−1.74, +63.76] on 16 maps) —
the lesson is a design input: decompose the deficit *first* on the 8,131-game corpus, and
any experiment runs 256-map panels with cluster-support gates from the start. Global
always-on retunes stay closed (waves 1–3). **First step.** Read-only deficit
decomposition by map features. **Cost:** one session, delegable.

## H12. Pool-drift surveillance — the compounding floor

**Hypothesis.** The ladder is not static: the cron already catches ~50–100 games/day, new
agents keep entering (Pafin's 5-worker economy was unknown two days ago), and rank can
move without us acting. Systematic weekly re-audits (comparative waste baseline, roster
pricing refresh, new-entrant profiling) will periodically surface exploitable changes —
and they are the trigger for revisiting H4/H9 timing.

**Evidence for.** Every audit this week that touched the fresh corpus corrected at least
one standing number (motif rate 72→49.7%, corpus 1,891→8,131, league 110→112).
**Closures touched.** None. **Cost:** near zero — the cron runs; the audits are one
delegable session per week. **Expected value:** small per event, but it is the only
hypothesis that pays out even if we do nothing else.

---

## Portfolio note

The list is deliberately barbelled: H1/H2 carry the rating ceiling and the cost; H3–H8
are cheap audits that can run in parallel under the multi-agent protocol (read-only,
disjoint write sets — H3, H5, H7, H8, H11 are immediately delegable); H9 is
owner-gated measurement; H10 is the sanctioned long shot; H12 is the free floor. The
honest sequencing given everything the ledger has taught: **H5 and H3 first** (they are
the cheapest ways to invalidate or sharpen H1/H2 before the expensive bets), H1 as the
first new experiment, H2 as the program decision the owner takes with H1's verdict in
hand.
