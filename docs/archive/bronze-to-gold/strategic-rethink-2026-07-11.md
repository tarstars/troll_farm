# Strategic rethink & ranked roadmap — 2026-07-11 (flush-safe)

Full critical re-analysis of the project (user request 2026-07-11, done inline by the
controller, no subagents). COMPLEMENTS `docs/session-handoff-2026-07-11.md` (state/process —
still authoritative for champion/pipeline); this doc = WHERE TO SPEND EFFORT and why.
Verdict log: `docs/silver-experiment-log.md` (chopharvest gate entry appended same day).

## The two goals, priced (measured 2026-07-11)
- Live: **118/530 @ 18.8** (ringfix3, healthy). `field_targets.py 90 130`: rank 99 = 19.9,
  ranks 90-104 hold 19.9-20.1. **Goal A (user goal, rank ≤99) = +1.1 = ONE more
  ringfix3-class win.**
- **Goal B (Legend) = beat Boss 5, bar ~25.8-26.2 = +7.** The ENTIRE 19.9+ tier plays
  3-4 trolls / ms3/cc4-class builds (Tchoubidouwa123, nmahoude, ra5anchor; Boss 5 same
  shape). +7 is NOT reachable by ±1 execution cuts on the 2-troll build — it is a different
  build class or nothing. Goals A and B need DIFFERENT strategies; don't conflate.
- ⚠ UNKNOWN that gates everything: **contest end date** — check the CG contest page. Days
  left → Goal A only (directions 1,2,4). Weeks → Goal B becomes the only non-asymptoting play.

## v1.61.0-chopharvest — GATE VERDICT (2026-07-11): FLAG-FAIL as-tuned, NOT arena'd
Builder (a4a28cc4, branch worktree-agent-a4a28cc4b0708f40c) finished: built, TDD 6/6, frozen
(`cgauto/submissions/v1.61.0-chopharvest.{rs,min.rs,debug-probe.min.rs}`, 78,250 B), live-validated.
- ★ **CRITICAL CATCH (durable lesson):** `GE_SPEC` const bump alone was an ARENA NO-OP —
  `tactics.rs`'s turn-1 adaptive spec selector (`GE_CHOSEN_SPEC`) hardcoded hp as literal `0`.
  Caught only by LIVE smoke (mybuilds showed 2.2.0.2). Fixed (wires `super::GE_SPEC.2`) +
  regression test `chopharvest_live_adaptive_spec_wires_ge_spec_hp`. ANY future spec change
  must verify the LIVE build string, not the const. (Same class as "don't trust VERSION labels".)
- Paired boss gate, n=8 vs n=8 sequential UNPAIRED (random maps), controller-computed stats
  from `data/candidates/v1.61.0-chopharvest/gate/` + @TFSUM finals:
  - Mechanism FIRES: 26 chopper harvests/game; ring alive t≥150 at 6.8× baseline (1.96 vs
    0.29 ring_planted); train NOT delayed (t39 vs t53.5); win rate tied 1/8 vs 1/8.
  - **WOOD inv 38.75 vs 47.5 (−8.75; Welch t≈1.65, p≈0.06-0.13 — marginal but directional).**
    Brief's kill criterion ("wood must NOT drop") FIRED → per process, not submitted.
  - **FINAL SCORE 183.3 vs 198.0 (−14.7; t≈0.72, n.s. at n=8).** Decomposition: fruit
    +20.25 pts, wood −35 pts — **the trade is ~1 fruit-pt per ~1.7 wood-pts because wood=4×;
    adverse arithmetic even though the farm-sustainability thesis CONFIRMED** (ring stays
    alive) — the aliveness did NOT buy late wood (t225→300 slope +14.3 vs +13.5, ~equal).
- Mechanism hypotheses for the wood drop (undiscriminated; telemetry logs only [t,cmd]):
  (1) stolen chopper turns: 26 harvests × ~0.35 wood/turn ≈ −9 — matches exactly;
  (2) **fruit-in-carry shrinks free carry → engine caps wood-per-fell by FREE CARRY**
  (verified `engine.rs apply_chop` ~:595-611) — recreates the FIX3 waste class in fruit form;
  (3) map luck (unpaired; candidate batch's boss scored higher, 266 vs 226).
- IF PURSUED, cheapest discriminator first (extend @TFHARVEST to log carry+cell; count fells
  where wood_gained < size), then ONE variant: (a) RING-ONLY harvest (1-2-step detours,
  preserves the un-cap thesis), or (b) harvest only when free carry ≥ next fell size /
  bank-first, or (c) builder's ablation: band 38 → below anti-starvation 30. OTHERWISE reject;
  the wiring fix + its regression test are cherry-pickable correctness assets regardless.

## Critical findings (what the project narrative gets wrong/incomplete)
1. **The binding constraint is the MEASUREMENT INSTRUMENT, not the bot.** Decision bands ±0.5
   vs single-convergence noise ±1 (same code read 17.6/19.3/19.9 in 12h). Several of the six
   "cleaner-but-negative" reverts (taskfloor −1.0, fellmission −1.0) are ~1σ events; some
   meta-lessons ("commitment hurts") may partly be measurement artifacts. Any verdict-fidelity
   gain multiplies every future experiment.
2. **The better instrument is already 90% built and unassembled:** the equality harness
   (`src/bin/equality.rs`) already runs two bot BINARIES over the real protocol/engine.
   Extend "assert identical" → "paired score-diff over 300-500 seeded maps" = a high-powered
   champion-vs-candidate A/B. Framing (transfer-wall-honest): a REJECT filter, not an accept
   oracle — ringtune (−2.4 after 4/6 local) would likely have died locally at n=500; field-
   interaction effects (seedloop class) still need the arena. Prune locally, confirm in arena.
   Also scale field probes: fixed panel of 5 opponents @ ranks 95-115 × 4-6 games ≥ 20-30
   games/verdict (n=4-6 provably can't see ±1.0).
3. **Etudes, as built (H≤16, ~1 troll/side, forced-only), CANNOT answer backlog #1** (protect-
   wild-banana = 100+-turn payoff → Unresolved/TooLarge or myopic). Their honest domain =
   micro-execution PROOFS: race margins → proven `race()` constants, contested-fell duels,
   harvest duels w/ last-fruit duplication, block/swap skirmishes — conveniently the only class
   that transfers. Farm-sustainability questions → long-horizon paired self-play (finding 2).
4. **We study our losses exhaustively and our betters not at all.** Every player between us and
   Legend runs 3-4 trolls; that's an existence proof the marginal troll PAYS. The lemon-wall /
   farmhand-doesn't-pay conclusions are conditional on OUR farm architecture, not laws. D9 even
   trained a 3rd troll 7/8 (affordability solved; role failed). Their replays are PUBLIC:
   decode how the 19.9-20.1 cluster + Boss 5 use trolls 3-4 (train timing/specs, farm shape,
   fell sizes, wood/fruit split). Cheapest untapped information in the project; zero arena cost.
5. **Stale-assumption audit (engine-verified 2026-07-11): wood-per-fell = tree SIZE capped by
   FREE CARRY at fell time** (`apply_chop`). The dead-end "fell at size 3 pointless" was
   derived under cc2 (min(3,2)=2 — true THEN). Champion chopper is now **cc3**: ring fell-at-3
   = 3 wood/trip vs 2 (+50% wood per chopper trip & bank run, same wood/chop, same
   wood/growth-tick) = the tightfarm/ringfarm travel-reduction shape. Caveats: slower first
   wood (early tempo was load-bearing per ringtune E1), grazes the ring freeze → must go
   through the finding-2 gate first. Related cheap sweeps: water-adjacent banana cooldown 6→4
   (+50% growth) → ring plant ORDER could prefer water-adjacent cells; endgame LIQUIDATION
   audit (census losses of −1/−3 flip on "fell/bank/drop everything convertible by t300" —
   verify a terminal pass exists at all).
6. **Process:** don't draw new meta-lessons from single ±1.0 arena convergences (see 1).

## RANKED DIRECTIONS (profit ÷ effort, desc)
1. **Chopharvest decision** (small): discriminate the wood-drop mechanism + at most ONE
   variant (ring-only is the thesis-preserving one), gated by #2 once it exists; else reject
   + cherry-pick the wiring fix. Do not arena as-tuned.
2. **★ BUILD THE PAIRED SELF-PLAY GATE** (1-2 days): equality harness → paired score-diff,
   300-500 seeds + widened fixed field panel (20-30 games/verdict). Top single investment;
   also retro-tests borderline reverts (taskfloor, fellmission) cheaply.
3. **Top-tier replay intelligence** (2-3 days, no arena cost): decode 10-20 games of the
   19.9-20.1 cluster + Boss 5 → "what does their marginal troll do that ours didn't."
   Feeds 5/6 with evidence instead of invention.
4. **Small in-framework execution/arithmetic candidates** (finding 5), one at a time, pruned
   by #2 first: ring fell-at-3 under cc3; endgame liquidation pass; water-preferring ring
   plant order; re-isolated FIX2 diagonal-first.
5. **Etudes redirected** to provable micro-questions whose outputs become proven band
   CONSTANTS (race margins first — race() is the biggest historical winner, +1.3).
6. **Scale (3rd troll) reopened ONLY from #3's evidence** and only if Goal B/time justify —
   copy the demonstrated top-tier marginal-troll role; never invent one again (T-hand, D9).
   Only direction whose ceiling exceeds ~20.
7. **Map-class adaptivity** (water-collapsed ring, chokepoints) — real documented waste, but
   unmeasurable per-class until #2 exists. Waits.

**STOP DOING:** band/knob tuning & anti-flap variants (swept; finding 1); mission-layer
increment 2 (until a measurement story exists); pie/protection family; meta-lessons from
single convergences; farm-economy refinements inside the ring (ringtune/trainfruit graveyard).

**Decision needed from the user:** Goal A (≤99 before the clock) → order 2→1→4. Goal B
(Legend attempt) → 2→3→6, accepting arena rank may stall meanwhile. Check the contest end
date first — it may decide this unilaterally.
