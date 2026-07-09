# v1.56.0-ringfarm builder brief — structured 8-cell tent-ring farm with per-cell roles

**Origin:** user design directive (2026-07-09) after reviewing champion games. Three verified
observations (turn-by-turn @TFASSIGN telemetry, game 895585792): the bot FORAGES distant natural
fruit instead of building a local farm (gatherer trekked ~20 steps to a far banana tree, planted
ZERO bananas in 38 turns), the chopper gets pulled off wood to distant anti-starvation fruit, and
the farm geometry is ad-hoc. The user specifies an explicit farm scheme to replace it.

## The scheme (user, confirmed)
An 8-cell ring around the tent at (0,0) (Chebyshev distance 1), TWO roles:
- **Diagonals** (-1,-1),(1,-1),(-1,1),(1,1) = **RIPE bananas** (fruit/seed engine): plant, keep
  standing, AGGRESSIVELY harvest their fruit (retain some bananas as SEED to replant, bank the
  rest into the tent as points). Fell a diagonal ONLY when (a) the endgame "chop down all" phase
  (turns_rem <= GE_LIQ_T) or (b) an enemy is actively foraging/raiding our farm (a hostile troll
  near our half/farm).
- **Orthogonals** (0,1),(0,-1),(1,0),(-1,0) = **BANANAS TO CUT** (wood cycle): plant, grow to
  fell-size, the chopper fells them for WOOD (it stands adjacent to the tent to bank anyway =
  zero extra travel), then REPLANT the cell and repeat.

This resolves the old nanaflow banking-congestion worry (orthogonal cells were penalized +3
because a persistent banana blocks the DROP path): the orthogonal bananas are TRANSIENT (cut
fast), so they don't persist to block banking; the diagonals sit off the traffic path.

## Current state (what to replace) — planner.rs:307-328
`plant_cell` picks ONE cell by `min(d[c] + water_pen + geo)` where `geo = (bank_adj? +3) +
(diag? -1)` — so it PREFERS diagonals but AVOIDS orthogonals (the +3), plants one-at-a-time up
to `farm_cap=12`, with NO role notion. Fell logic (GE_FARM_FELL=3, GE_SEED_RESERVE=2 most-mature)
has no position/role awareness. And early game the distant-forage bands (harvest 75, seed 52,
fund 58, anti-starv 30) outrank building the ring, so the ring never gets built.

## Implementation (coordinated change; keep it in the existing band/Plan structure)

### A. Ring definition (tactics.rs, on the Plan)
Compute the ring once/turn: the up-to-8 Chebyshev-1 cells around the shack, filtered to
walkable + reachable + **front-door-eligible** (reuse `farm_eligible`/`door_d` so on chokepoint
maps only the reachable-side ring cells count — composes with v1.54.0-frontdoor). Tag each ring
cell's role: DIAGONAL (`|dx|==1 && |dy|==1`) = ripe, ORTHOGONAL (`farm_d==1`) = cut. Expose on the
Plan (e.g. `ring: Vec<(Cell, Role)>` or two cell-sets `ripe_cells`/`cut_cells`).

### B. Placement — build the ring EARLY (planner.rs candidates)
- The plant target = an EMPTY ring cell (no tree, reachable). Prefer filling the ring before any
  beyond-ring cell. The ring IS the farm: set the effective farm to the ring (do not spread to
  farm_cap=12 cells scattered; keep it the tight 8-ring, or fewer on chokepoint maps).
- **Priority so the ring gets built before foraging:** while the ring has empty cells AND a
  banana is available (in carry, or PICK-able from the tent), the pick->plant sequence must
  outrank the distant-forage bands. Concretely raise the PICK-to-stock-the-ring band above
  harvest(75)/seed(52)/fund(58) EARLY / while ring incomplete (propose: a "build-ring" pick band
  ~78 and keep plant at 88, both gated on `ring has an empty cell`). Do NOT raise it so high it
  beats a full-bank(80)/endgame(95); keep the ordering plant(88) > build-ring-pick(78) >
  harvest(75) > ... Prove the ordering (band arithmetic) like the idle-fruit/taskfloor reviews.
- Seed bootstrap: the first bananas come from the tent inventory (PICK) or the nearest banana
  tree; prefer the NEAREST banana source, never a 20-step trek when a nearer one or tent stock
  exists (this is the "don't forage distant" fix).

### C. Fell / keep policy by role (planner.rs fell bands + seed-reserve)
- ORTHOGONAL (cut) ring bananas: fell at size `GE_FARM_FELL=3` for wood, HIGH priority for the
  chopper (adjacent), then the cell becomes an empty ring cell -> replanted (the cycle). Chopper
  prefers a ripe cut-banana over trekking to a distant native tree.
- DIAGONAL (ripe) ring bananas: NEVER a fell candidate EXCEPT when `turns_rem <= GE_LIQ_T`
  (endgame liquidation) OR an enemy troll is near our farm (raid threat — define a simple
  trigger: an opponent troll within map-distance R of the shack, propose R=4; do NOT reuse the
  parked ownership governor). Replace/augment GE_SEED_RESERVE with "diagonal ring bananas are the
  protected seed/fruit engine."

### D. Harvest / seed management (planner.rs harvest bands)
- Harvest diagonal ripe bananas' fruit aggressively (they regrow fruit). Retain enough bananas in
  reserve to replant empty ring cells (cut cells after felling, and any lost diagonal); bank the
  surplus fruit into the tent as points ("some seed, some into tent").

## What NOT to do
- Do not spread the farm beyond the ring (the scheme is the tight 8-ring — this also keeps the
  chopper's bank trips shortest, the proven throughput lever).
- Do not reuse the parked ownership/pressure governor for the raid trigger (keep it simple/local).
- Keep it OUT-PRODUCE: the raid-threat fell of diagonals is defensive liquidation of OUR farm,
  not attacking the enemy.

## Tests (TDD, RED first)
1. `ring_placement_diag_and_ortho`: on an open map, empty ring, banana available -> plant targets
   are ring cells; both diagonal and orthogonal ring cells become plant targets (orthogonals are
   NO LONGER avoided). Assert a specific orthogonal ring cell is a valid plant target.
2. `ring_built_before_distant_forage`: a state with an empty ring + a distant harvestable native
   fruit. Assert the gatherer's top task is build-ring (pick/plant), NOT the distant harvest.
   RED pre-fix (forage wins).
3. `cut_orthogonal_keep_diagonal`: a grown ring (diagonals + orthogonals at fell-size, no endgame,
   no enemy near). Assert the chopper's fell candidate is an ORTHOGONAL cell; assert a DIAGONAL
   ring banana is NOT a fell candidate.
4. `diagonal_felled_in_endgame`: same but `turns_rem <= GE_LIQ_T` -> diagonal IS a fell candidate.
5. `diagonal_felled_under_raid`: same but an enemy troll within R of the shack -> diagonal IS a
   fell candidate.
6. `ring_respects_frontdoor`: chokepoint map -> the ring is only the reachable-side cells (far-side
   ring cells excluded via farm_eligible). No straddle.
7. Band-ordering proof: build-ring-pick(78) < plant(88), > harvest(75); diagonal-keep can't be
   felled outside endgame/raid. Numeric, like idle-fruit/taskfloor.
8. Full suite green + self-determinism equality 8 seeds + bundle/minify gates + artifacts frozen.

## Gates & risk (for later stages)
- ECONOMY-CLASS RISK: farm/economy redesigns are the historical graveyard (pie 0-for-5, taskfloor
  −1.0). BUT this is framed as travel-reduction + tight-farm (the ONE proven economy lever,
  v1.13.0-tightfarm) + the user's explicit design addressing verified waste. Temper arena
  expectations; validate carefully.
- Candidate gate: play vs boss + Crouistiti with a DEBUG probe; confirm (a) the ring gets BUILT
  early (bananas planted near tent by ~turn 15-20, vs the current 0), (b) gatherer distant-trek
  turns DROP, (c) wood does not crater. VERSION -> "1.56.0-ringfarm". Base = current session HEAD
  (1.54.0-frontdoor, post-taskfloor-revert). Preserve champion consts. Standard freeze + trailer.
