# Intent-driven missions — design (full mission-layer, Approach B)

**Status:** DESIGN — awaiting user review (brainstorming gate). No implementation until approved.
User approved the FellForWood mission shape (1-OK) and chose to WIDEN to the full mission-layer
redesign (Approach B): replace ALL weighted task-selection with explicit missions, KEEP the joint
move solver. Built incrementally (mission-by-mission, each gated vs the champion) so the full
target architecture is reached without a big-bang regression of the +1.7 champion.

## Motivation — the user's argument
The current decision layer (`planner::assign_resolved`) is **soft/emergent**: every action is a
weighted candidate (band × 100_000 + tiny within-band adjustments) and a per-turn joint argmax
picks winners. Nobody *decides*; behavior emerges from weight comparisons, and every fix is
another weight tweak. The "wrong-tree" bug is the signature (v1.59 vs Boss-5, user clipboard
log): the chopper targeted a health-20 apple (10 chops / 4 wood), sat on it 9 turns for ZERO
wood, then abandoned it — a close tree winning a distance-dominated argmax, re-decided each turn
(so it abandons/backtracks). The user wants **straight, intent-driven logic**: decide a goal →
plan the optimal route → execute it to completion.

## Target architecture — 3 layers, replace the middle
```
L1  tactics::Plan            (KEEP)  — goals/state: want_chopper, ring geometry, phase, farm_d…
L2  MISSION LAYER            (NEW)   — replaces planner band-argmax: explicit missions + assignment
L3  motion::solve_moves      (KEEP)  — joint conflict-free landing cells, shuffle-invariant
```
The band system (`planner.rs` candidates/assign) is retired as missions take over its clusters.
The Plan (L1) and the joint move solver (L3) stay — L3 is the proven shuffle-invariant motion
layer; missions emit MOVE intents into it exactly as bands did.

## The mission abstraction
```
enum MissionKind { Bank, TrainTroll, FellForWood, BuildRing, HarvestFruit, Fund, Idle }

struct Mission {
    kind: MissionKind,
    troll: TrollId,
    target: Option<Cell>,     // the committed resource/cell (tree, ring cell, iron, shack)
    plan:  <committed route/steps>,
    // methods:
    fn next_action(state) -> Command,        // MOVE intent / CHOP / HARVEST / PLANT / TRAIN / DROP / PICK
    fn status(state) -> Active | Done | Invalidated,
}
```
Defining property vs the band system: a mission **persists across turns (commitment)** until Done
or Invalidated. No re-deciding every turn → no abandonment, no backtracking. (This replaces the
STICKY anti-flap hack with a first-class concept.)

## Mission taxonomy (replaces the band clusters)
| Mission | Replaces bands | Committed plan |
|---|---|---|
| **Bank** | 95 endgame, 80 full→bank | route to shack-adjacent, DROP carry |
| **TrainTroll** | 65/64/62/60/58 funding + TRAIN | collect the missing train resources (iron + fruit) by the cheapest route, then TRAIN — the user's plum-example |
| **FellForWood** | 72/70 primary-fell, 42/40 chop-help, 31/30 anti-starv fell | pick the most wood-EFFICIENT reachable tree (see below), route, fell FULLY |
| **BuildRing** | 88 plant, 78/77 build-ring-pick, 52/50/49 seed | pick/plant bananas on empty ring cells (ringfarm scheme + ringfix3 no-carry) |
| **HarvestFruit** | 75 standing-harvest, 62 fruit-MoveTo, 38 idle-fruit | route to a ripe fruit tree, harvest (points / train fuel) |
| **Fund** | (folded into TrainTroll) | mine iron / gather the training fruit |
| **Idle** | 10 park | ring-2 park off the bank path (no reachable productive work) |

## Explicit priority (replaces band VALUES with readable policy)
A single readable ordering with gating conditions — the strategic policy made explicit and
debuggable (no magic numbers):
```
1. Bank            if endgame (turns_rem <= LIQ) OR carry full
2. TrainTroll      if want_chopper/want_feeder AND the train resources are collectable
3. FellForWood     if wood is the marginal need (default productive work for a chopper)
4. BuildRing       if the ring has empty cells (and not gated out by TrainTroll priority early)
5. HarvestFruit    ripe fruit available + free capacity
6. Idle            nothing above applies
```
This ordering IS the tuned strategy (it re-expresses the band hierarchy) — but as an explicit,
editable policy. Priority is per-troll-role-aware (a chopper prefers FellForWood; the starter
prefers BuildRing/Harvest), matching the current role split.

## Conflict-free assignment (replaces the joint band-matcher; keeps its good properties)
The band system's exhaustive top-K matcher gave: (a) one task per troll, (b) no two trolls claim
the same target, (c) shuffle-invariance (result independent of troll iteration order). The
mission assigner reproduces these EXPLICITLY and deterministically:
1. Enumerate wanted missions from the Plan + world (the priority list, instantiated with concrete
   targets — e.g. FellForWood instantiated with the best tree per candidate troll).
2. Assign greedily in PRIORITY order, but over a CANONICAL ordering (sort candidates by (priority,
   role-fit, target cell) — never troll iteration order), so the result is shuffle-invariant.
   Each troll takes ≤1 mission; each target claimed once; a claimed target is removed from later
   missions' candidate sets (conflict-free).
3. **Commitment/preemption:** a troll KEEPS last turn's mission unless it is Done/Invalidated OR a
   strictly-higher-priority mission newly becomes available for it (explicit preemption rule,
   replacing STICKY's numeric bonus). This is where "commit to the plan" lives.
Determinism: all candidate/target ordering is canonical (sorted), no HashSet-iteration into any
decision (the codebase's recurring determinism hazard).

## FellForWood — the first mission (user-approved, the wrong-tree fix done right)
Among reachable fellable trees NOT doomed by `race()` (enemy fells first), choose the max of
`efficiency = wood_yield / (travel_steps + chops_to_fell)`, chops_to_fell = ceil(health/chop_power).
Explicitly prefers soft bananas (3 chops) over tanky apples (10 chops); on the clipboard map it
scores lemon 0.44 > apple 0.33 → takes the lemon, apple never chosen; a soft banana wins from
farther. COMMIT to the tree; route; CHOP until felled; re-plan only on Done/Invalidated. The
wrong-tree bug is impossible by construction (a reasoned max over efficiency, not a distance argmax).

## Preserve the hard-won wins (do NOT re-derive from scratch — re-express as mission logic)
- **race() check (+1.3):** FellForWood's candidate filter (skip doomed trees) + BuildRing/Harvest
  contested-target skip. Same helper, now inside explicit mission planning.
- **ring scheme (+1.7) + ringfix3 no-carry:** BuildRing mission = the ringfarm 8-cell scheme
  (diagonals ripe/seed, orthogonals cut/wood) + no-carry-in-advance (pick only when plant is
  immediate). The proven economy is a mission, unchanged in behavior.
- **yield / task-interference (+1.0):** a stationary lower-priority mission-troll blocking a
  higher-priority mover yields — now a first-class rule between missions (was the yield_pass).
- **sticky anti-flap:** subsumed by mission commitment (a mission persists; it doesn't re-win a
  weighted comparison each turn).
The mission layer must MATCH these behaviors before it can beat them — the gate for each migrated
mission is "≥ champion on the boss pool + arena."

## Interface + debuggability
- New `rust/src/botmain/missions.rs`: taxonomy, assigner, per-mission planners.
- `decide_elite`: `missions::assign(state, plan, my)` → per-troll Mission → `next_action` gives
  each troll's command; MOVE intents go to `motion::solve_moves` (unchanged); non-move actions
  emitted directly. The band `planner::assign_resolved` is removed once all clusters are migrated.
- `@TFMISSION t=<turn> id=<troll> kind=<K> target=<cell> why=<reason>` per turn (DEBUG) — every
  troll's intent is a readable sentence. THIS is the "straight logic" payoff.

## Incremental build path (full design, no big-bang regression)
Each step migrates ONE band cluster to a mission, keeps the rest on bands, and gates vs the
champion (must be ≥ ringfix3 on boss pool + arena KEEP before proceeding):
1. **FellForWood** (v1.60) — chopper fells by efficiency; excludes chopper from fell bands. (The
   proof; fixes wrong-tree.)
2. **Bank** (v1.61) — banking/endgame as a mission.
3. **BuildRing** (v1.62) — the ringfarm+ringfix3 economy as a mission (must stream-match closely).
4. **TrainTroll** (v1.63) — the user's collect-resources-then-train mission (dissolves the funding-stall).
5. **HarvestFruit + Idle** (v1.64) — the rest; retire `planner::assign_resolved`.
At the end the band-argmax is gone; L1 Plan + L3 motion solver remain; the bot is fully
intent-driven. Any step that REGRESSES vs the champion stops the migration for diagnosis (the
band cluster it replaced was load-bearing) — we keep the champion, learn why.

## Success criteria
- Wrong-tree gone (FellForWood picks by efficiency, fells fully) — constructed test on the
  clipboard geometry.
- Each migrated mission ≥ champion (boss-pool wood/score + arena KEEP).
- End state: `@TFMISSION` makes every decision readable; no weighted argmax remains; the +1.7
  economy + the +1.3 race + the +1.0 yield behaviors are preserved as explicit missions.

## Testing
- Per mission: a "picks the right target" test (FellForWood efficiency; BuildRing ring cells;
  TrainTroll cheapest-route), a "commits/no-abandon" test, an "invalidation" test (race/target
  gone). Determinism equality (bot vs bot, 8 seeds) each step. Shuffle-invariance of the assigner
  (assign is independent of troll order) as a property test.

## Risk
Approach B replaces the entire tuned band matcher — higher risk than the one-mission proof. The
incremental build path is the mitigation: the champion is never off the slot; each mission is
gated before the next; a regressing step halts the migration rather than shipping a worse bot.
The honest failure mode: if re-expressing a band cluster as an explicit mission can't match the
tuned weighted behavior (some weight interaction WAS doing real work), that step stalls — a real
finding, at the cost of one candidate, not the champion.
