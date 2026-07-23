# Discussion summary — 2026-07-11: the ceiling, chopharvest, and the expressiveness diagnosis

High-level record of the strategy discussion (user + controller, one session). Detail lives in:
`docs/strategic-rethink-2026-07-11.md` (ranked roadmap), `docs/silver-experiment-log.md`
(chopharvest gate verdict), `docs/session-handoff-2026-07-11.md` (state/process). This doc is
the conceptual arc — what we concluded and why.

## 1. Where we stand
- Champion **v1.59.0-ringfix3**, 118/530 @ 18.8. **Goal A (rank ≤99)**: bar measured at 19.9 →
  gap +1.1 ≈ one champion-class win. **Goal B (Legend)**: bar ~25.8+ → gap +7 — unreachable by
  ±1 execution cuts; the entire 19.9+ tier plays 3-4-troll builds. Different goals ⇒ different
  strategies; the contest end date (unchecked) decides which governs.
- The tuned band system sat at a "practical ceiling": 6 consecutive cleaner-but-arena-negative
  reverts; only execution waste-cuts ever transferred.

## 2. Critical-rethink findings (see rethink doc for full detail)
1. The binding constraint is the **measurement instrument** (arena noise ±1 vs decision bands
   ±0.5; several reverts were ~1σ events). Fix: a **paired self-play A/B gate** built from the
   existing equality harness (reject-filter, arena confirms) + a widened fixed field panel.
2. **Etudes** (H≤16 forced-outcome oracle) cannot answer the farm-sustainability questions
   queued for it; its honest domain is micro-execution proofs (races, duels, salvage protocols).
3. We had never studied **how the tier above us plays** (their marginal trolls); their replays
   are public and free.
4. Stale-assumption audit: wood-per-fell = tree size capped by FREE CARRY (engine-verified);
   "fell-at-3 pointless" was a cc2-era verdict, stale under the cc3 chopper; endgame
   liquidation unaudited; water-adjacency unexploited in ring plant order.

## 3. The chopharvest arc (one day, full loop)
- **Idea (user):** ring bananas cap at 3 fruits and stall; give the chopper hp1 (+~1 apple) and
  let it harvest opportunistically below all chopping — un-cap the ring, bank the fruit.
- **Build:** clean; ★ caught that bumping `GE_SPEC` was a live NO-OP (tactics.rs adaptive spec
  hardcoded hp) — verify the LIVE build string on any spec change, never the const.
- **Boss gate (8v8): FLAG-FAIL as-tuned.** Thesis CONFIRMED (ring alive 6.8× at t≥150) but
  wood −8.75 and score decomposition adverse: +20 fruit pts bought with −35 wood pts (wood=4×).
- **Arena (user-directed, "I want to see how it plays"):** submitted vs bracket 118/530 @18.8;
  cold-start climb-then-fade (12.2 → 14.5 → 13.9 @+35m), trending to revert at +50m.
- **User game-watching (clipboard, vs a 4-troll field bot):** three observations checked
  against telemetry —
  (a) "fruit gathering delays training": training WAS late (t74) but the funding trace shows
  lemon/plum were binding; the hp-apple cost was covered by starting inventory from t1.
  (b) "chopper fells fruited trees without picking": CONFIRMED — worse: the chopper never
  harvested at all in this game (all 48 harvests were the starter's) because band 38 only fires
  when idle and the chopper always had chop work. Felled fruit is DESTROYED by the engine.
  (c) "never saw chopper deliver fruit to tent": correct here (see b); on sparse gate maps it
  did (26/game). Ring bananas mostly recycle into replants (seeds), not banked points.
- **Bonus finding from the same game:** training cost per stat ≈ `n + stat² − 1` (opponent's
  t3 clone cost exactly 2/2/2/2) — the remembered `n + stat²` was off by one; a minimal
  1/1/1/1 hand is affordable AT T3 from starting inventory. The "lemon wall" blocks expensive
  specs, not cheap hands.

## 4. The decisive game: perfect farm, still lost
The clipboard game is the day's most valuable artifact: our farm NEVER died (ring 5-6/8
planted through t280, seeds→10, 82 wood — best on record, zero flaps), we led 96-38 at t150 —
and lost 337-362. The opponent: cheap 1.1.1.1 clone at t3, hp2 fruit-harvester at t89, chopper
LAST at t132 → 66 wood + **92 banked bananas** vs our 82 wood + 9. **A perfected 2-troll wood
engine caps below a 4-troll wood+fruit economy.** This is the Goal-B mechanism live in one
replay, and the concrete research brief for "decode the top tier."

## 5. ★ The expressiveness diagnosis (user's insight — the session's centerpiece)
From "the current mechanism physically cannot express *spend one turn saving the fruits on the
tree I'm about to destroy*," generalized: **the bot's policy representation truncates the
hypothesis space — we cannot even TEST whole classes of ideas.**
- The band system's expressiveness class = preferences over what to do NOW. Outside it:
  (1) **sequences** whose steps aren't individually argmax (harvest → bank → return → fell —
  the bank detour crosses band territory and defeats predicate hacks); (2) **cardinal
  cross-type comparisons** (bands are ordinal; no common points-per-turn currency);
  (3) **temporally extended value** (a seed source alive for 100 turns).
- **Reinterpretation of the record:** the wins (race, yield, ringfarm, ringfix3, joint solver/
  matcher) were expressible ideas; the six reverts were mostly INEXPRESSIBLE ideas forced
  through the wrong doors — band hacks (v1.44, taskfloor) or full commitment (fellmission).
  "The candidate well is dry" → wrong. The well of *band-expressible* ideas is dry.
- **Design consequence — disentangle what missions bundled:** multi-step VALUE ATTRIBUTION
  (good) vs COMMITMENT (bad, killed load-bearing flexibility). Keep only the first:
  **macro-candidates / bundle valuation, zero commitment** — the producer emits compound
  candidates (e.g. `FellWithSalvage(tree)` = harvest + bank-detour + chops, priced as a bundle
  with carry-feasibility), the matcher compares them cardinally, and the bundle RE-PROPOSES
  itself each turn from current state (no state machine; flexibility untouched). Same shape as
  the two prior expressiveness upgrades that WON (joint move solver, joint matcher): widen
  what's considered, keep the flexible per-turn selector.
- **Pipeline: prove → express → verify.** Etudes prove which protocols are forced-better
  (first: fruited tree, tent ≤2, salvage-bank-fell vs fell-now, H=12); proven protocols become
  macro-candidates (strictly additive, behind a flag, champion-equality when off); the paired
  self-play gate checks transfer at n≈500; the arena confirms. Later, if hand protocols
  transfer: shallow rollout search (H=4-8 over the real engine, tuned valuation as leaf eval,
  50ms budget) subsumes hand authoring — held back until then (RHEA-class risks).

## 6. Agreed next steps (order)
1. **Paired self-play gate** (from `src/bin/equality.rs`) — the enabler for everything.
2. **Salvage etude** — the first real etude with decision value.
3. **`FellWithSalvage` macro-candidate** — first zero-commitment expressiveness test.
4. Chopharvest verdict per poller (+50m); revert to ringfix3 if ≤ −0.5 (expected).
5. Open user decisions: Goal A vs Goal B; check the contest end date.
6. (Goal-B track when chosen: decode top-tier replays — §4 is the brief.)
