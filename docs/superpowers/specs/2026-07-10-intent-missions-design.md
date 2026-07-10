# Intent-driven missions — design (proof-on-one-mission)

**Status:** DESIGN — awaiting user review (brainstorming gate). No implementation until approved.
Sequencing chosen by the assistant while user AFK: **Approach A (prove on one mission first)** —
lowest risk to the +1.7 champion, and it fixes the user-flagged "wrong-tree" bug with EXPLICIT
reasoning rather than the weight-tweak the user rejected. User may redirect to B (mission layer
over the motion solver) or C (full rewrite).

## Motivation — the user's argument
The decision layer is **soft/emergent**: every possible action becomes a weighted candidate
(band × 100_000 + small within-band adjustments) and a per-turn argmax picks the winner. Nobody
*decides* anything; behaviors emerge from how the weights compare, and every fix is another
weight tweak. The "wrong-tree" bug is the pure signature (v1.59 vs Boss-5, user clipboard log):
the chopper targeted a health-20 APPLE (10 chops for 4 wood), sat on it 9 turns for ZERO wood,
then abandoned it — because it was *close* and won a weighted comparison, re-decided each turn
(so it can abandon/backtrack). The user wants **straight, intent-driven logic**: "decide to
collect plums to train a troll → plan the optimal route → collect → train."

## Goal
Introduce explicit, committed, debuggable **missions**: a goal + a concrete multi-step plan
(route + actions) that a troll commits to and executes to completion. Prove the pattern on ONE
mission (FellForWood) that fixes the wrong-tree bug with explicit reasoning, keeping the rest of
the proven bot untouched.

## The mission abstraction (minimal)
```
Mission {
    goal: MissionKind,              // e.g. FellForWood
    target: committed plan,         // the chosen tree + intended route
    fn next_action(state, troll) -> Command,   // MOVE toward target / CHOP / ...
    fn status(state) -> Active | Done | Invalidated,
}
```
The defining property vs the current system: a mission **persists across turns (commitment)**
until Done or Invalidated. No re-deciding every turn → no abandonment, no backtracking. This is
the whole point of "straight logic."

## The first mission: FellForWood (the wrong-tree fix, done right)
- **Trigger:** the chopper has no Active fell-mission and wants wood.
- **Plan (EXPLICIT reasoning — not weights):** among reachable fellable trees NOT doomed by the
  race() check, choose the one maximizing wood EFFICIENCY:
  `efficiency = wood_yield / (travel_steps + chops_to_fell)`,
  where chops_to_fell = ceil(health / chop_power). This explicitly prefers soft bananas
  (3 chops) over tanky apples (10 chops); the wrong-tree bug becomes impossible because the
  decision is a reasoned max over efficiency, not a distance-dominated argmax. Pick the best;
  COMMIT to it.
- **Execute:** route to the tree (optimal path), then CHOP until felled. Do NOT abandon mid-fell
  unless Invalidated (tree gone, or race() now says an enemy fells it before our ETA).
- **Re-plan** when the tree is felled (Done) or the plan is Invalidated.

This REPLACES the chopper's weighted fell candidates (the 70/72 primary-fell + 40/42 chop-help
+ 31/30 anti-starv fell bands, for the chopper only). Everything else — ring-build, banking,
harvest, the starter troll, the second-troll funding — stays on the current band system. This is
a PROOF of the pattern, not the full migration.

## How it coexists with the champion (isolation)
- New module `rust/src/botmain/missions.rs`: Mission types + the FellForWood planner + a
  per-turn `assign_missions(state, my) -> HashMap<troll_id, Mission>` that reads/updates
  persisted mission state (thread_local, like LAST_TGT/FLAPS).
- In `decide_elite`, BEFORE `planner::assign_resolved`: compute missions. For any troll with an
  Active mission, its command comes from `mission.next_action(...)` and that troll is EXCLUDED
  from the band candidate pool (so no double-assignment). All other trolls flow through the
  unchanged band system.
- The joint MOVE solver (`motion::solve_moves`) still resolves movement — a mission emits a MOVE
  intent, the solver handles conflict-free landing. So we keep the proven shuffle-invariant
  motion layer.
- Determinism preserved: mission target selection sorts candidates canonically (efficiency, then
  cell) — no HashSet-iteration leak.

## Debuggability (the user's core ask)
- `@TFMISSION t=<turn> id=<troll> goal=<kind> target=<cell> eff=<x> chops_left=<n>` per turn
  (DEBUG-gated). Every troll's intent is now readable as an explicit sentence, not inferred from
  weight comparisons. This is the concrete payoff of "straight logic."

## Success criteria
1. **Wrong-tree gone:** on the clipboard game's map, the chopper explicitly picks the most
   wood-efficient reachable tree (a soft banana/lemon, never the health-20 apple) and fells it
   fully. Verify via a constructed test on that geometry.
2. **Conversion up:** boss-pool wood output ≥ ringfix3 (this is the Boss-5 "same chops, more
   score" lever — felling soft trees = more wood/chop).
3. **Arena:** KEEP vs ringfix3 (execution/conversion class — should transfer).
4. **Readable:** @TFMISSION makes the chopper's decisions self-explanatory.

## Testing
- Unit: `missions_fellforwood_picks_efficient_tree` (the clipboard geometry: apple h20 at (7,1),
  lemon h12 at (7,0), banana at (7,4) → mission picks by efficiency, NOT distance; apple never
  chosen while a softer tree is reachable). `missions_commits_no_abandon` (once committed to a
  tree, stays until felled/invalidated — no mid-fell switch on a small ETA jitter).
  `missions_race_invalidates` (enemy-about-to-fell → mission drops the target).
- Determinism equality (bot vs bot, 8 seeds).
- The chopper-excluded-from-bands change must NOT alter the STARTER's or banking behavior —
  a targeted check that non-chopper assignments are unchanged.

## Risk / why Approach A
A full rewrite risks the +1.7 champion (the band/joint-solver IS the champion). Proving one
mission: (a) validates the intent-driven pattern is debuggable + non-regressing before betting
the bot on it; (b) fixes the user-flagged bug the way the user asked (explicit, not weighted);
(c) if it wins the arena, it's the template to migrate the rest mission-by-mission
(TrainTroll = collect-resources-then-train; BuildRing; HarvestFruit; Bank). If it LOSES, we've
learned the committed-plan style doesn't beat the reactive argmax at this game cheaply — a real
finding — at the cost of one candidate, not the champion.

## Migration path (post-proof, if FellForWood wins)
Mission-by-mission, each replacing a band cluster with an explicit committed mission, measured
against the champion each step: TrainTroll (the user's plum-collect-then-train example) →
BuildRing → HarvestFruit → Bank. The band system shrinks as missions take over; the joint move
solver stays throughout. Full intent-driven bot emerges incrementally, never risking a big-bang
regression.
