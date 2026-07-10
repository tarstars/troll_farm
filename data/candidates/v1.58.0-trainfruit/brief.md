# v1.58.0-trainfruit builder brief — a clustered training-fruit corner in the tent ring

**Base:** v1.57.0-ringtune (the tuned ring: fund-first, diagonal-priority, banana no-carry).
Build ON TOP of v1.57 (they touch the same ring/plant code — do NOT branch from v1.56).
Bump VERSION to "1.58.0-trainfruit". Preserve champion consts.

**Origin:** user directive (2026-07-10) — grow our OWN training fruit to speed heavy-troll
training. MECHANIC VERIFIED: the engine supports `PLANT PLUM/LEMON/APPLE` (they have cooldowns,
grow, bear their fruit — engine.rs plant_cooldown/tree_health_params); the bot has only ever
planted BANANA. Training a troll is paid in fruit (plum->movement, lemon->carry/cc, apple->hp,
iron->chop), so a local lemon/plum/apple supply directly attacks the documented FUNDING-STALL
(2nd troll trains late on fruit-poor draws) and the LEMON WALL (map's starting lemons run out;
we grow our own instead).

## The scheme (user, confirmed)
The 8-cell tent ring (Chebyshev-1, already computed by `compute_ring`, already gated by
`farm_eligible`/`door_d` so only compactly-reachable cells count) is split into two zones:

- **TRAINING CORNER (3 cells): lemon + plum + apple.** A compact quadrant = 2 orthogonals + the
  1 diagonal between them (user's example NE: (0,-1)=lemon, (1,-1)=plum, (1,0)=apple — all
  mutually Chebyshev-1 so a gatherer tends all three with ~2 steps). KEPT standing, harvested for
  training fuel. Assign one of lemon/plum/apple to each of the 3 corner cells (deterministic
  mapping; the exact cell-to-fruit within the corner doesn't matter much — keep it canonical).
- **REMAINING 5 cells: BANANA** (the v1.56/57 scheme): the 3 remaining diagonals = ripe/seed
  keepers, the 2 remaining orthogonals = cut/wood cycle.

## Corner selection (adaptive — the user's compactness constraint)
Do NOT hard-code the NE corner. Choose the corner whose 3 cells are ALL eligible (walkable,
reachable, `farm_eligible` true = compact in the door-based sense). Among fully-eligible corners,
pick deterministically — prefer the corner FARTHEST from the opponent shack (reuse opp_d / the
door logic's enemy-distance idea, consistent with frontdoor's farthest-from-enemy door), canonical
tie-break. If NO corner has all 3 cells eligible (tight/chokepoint map), degrade gracefully: place
as many training trees as there are compact eligible cells (2, or 1), never on a far cell; the
banana scheme takes the rest. Expose the corner assignment on the Plan (e.g. extend
`Plan.ring: Vec<(Cell, CellRole)>` where CellRole ∈ {TrainLemon, TrainPlum, TrainApple,
RipeBanana, CutBanana}).

## Timing — training corner FIRST, as funding (reconciles with v1.57 E1)
v1.57 suppresses the BANANA ring-build while `want_chopper` (fund first). Training fruit is
DIFFERENT — planting it IS funding (grow lemons to train). So:
- While `want_chopper` / funding: BUILD THE TRAINING CORNER (plant lemon/plum/apple from starting
  inventory; harvest them for training fuel). This is funding work — it should NOT be suppressed by
  the E1 gate; only the BANANA ring-build stays suppressed during funding.
- After the chopper is funded/trained: build the banana wood-ring as v1.57 does.
- Net order: training corner -> chopper -> banana ring.

## Investment validation (the bet must pay off — don't just plant and stall)
Planting a lemon COSTS a lemon from inventory to grow a lemon TREE. This only helps if the tree
ripens in time to fund training faster than just spending the starting fruit directly.
- Only plant a training-fruit tree if we can afford the seed (have the fruit in inventory) AND it
  won't starve an IMMINENT training payment (don't plant our last lemon if we could train NOW with
  it). Prefer: if training is affordable now, TRAIN; else plant the training fruit to grow more.
- The gate MUST measure this: does the 2nd heavy troll / chopper train EARLIER than the v1.57
  baseline (not later)? If planting training fruit DELAYS training (seed cost > payoff), that's a
  fail — investigate before freezing.

## Bands / task production (planner.rs candidates())
- Plant-training-fruit task: emitted when building the training corner is appropriate (funding
  phase, corner has an empty eligible cell, we hold/can-PICK the needed seed fruit). Band it so it
  participates in funding (comparable to the funding bands), NOT above banking/real-chop. Prove the
  ordering numerically (this class of change is scrutinized — a low task must never displace real
  work; the pie/taskfloor family died here).
- Harvest-training-fruit: harvest the corner trees' fruit (feeds the training wallet). Reuse the
  existing harvest/fruit bands.
- Respect the banana no-carry principle from v1.57 for training seeds too: prefer planting a seed
  you can plant immediately / pick-up-on-the-way, not carry-in-advance across the map.
- Determinism: canonical order for corner choice + cell-to-fruit mapping (no HashSet iteration leak).

## Tests (TDD, RED first)
1. `trainfruit_corner_planted`: funding phase, corner empty, seeds in inventory -> plant targets
   include a training-fruit cell with PLANT LEMON/PLUM/APPLE (not BANANA). RED (pre-fix banana-only).
2. `trainfruit_corner_is_compact`: obstructed ideal corner -> the chosen corner's 3 cells are all
   farm_eligible; a corner with a far/blocked cell is NOT chosen. (chokepoint/obstacle fixture.)
3. `trainfruit_corner_before_banana`: funding phase -> training corner builds; the banana ring-build
   stays suppressed (v1.57 E1) until !want_chopper. Assert training-fruit plant is available during
   want_chopper but banana ring-build is not.
4. `trainfruit_train_now_over_plant_last_seed`: training affordable now with our last lemon ->
   TRAIN (don't plant the last lemon). Guards the investment logic.
5. `trainfruit_5_banana_cells`: on an open map, exactly 3 cells are training fruit and the other 5
   ring cells are banana (3 ripe + 2 cut). Roles correct.
6. Band-ordering proof (numeric): plant-training-fruit < banking(80)/endgame(95)/real-chop; can't
   displace real work. Existing ringfarm/ringtune tests stay green (adjust with documented reason).
7. Full suite + self-determinism equality 8 seeds + bundle/minify gates + freeze + debug probe.

## Gate + validation
- ★ THE key validation: play >=4 vs boss + >=4 vs Crouistiti (6479836) with a DEBUG probe. REPORT:
  (a) are lemon/plum/apple trees planted early (turn ~10-25) and bearing fruit? (b) does the heavy
  chopper / 2nd troll train EARLIER than the v1.57 baseline (the whole point — funding accelerated)?
  (c) wood not cratered; (d) win-rate vs v1.57. If training does NOT come earlier, the investment
  isn't paying — flag before freezing.
- COMMIT PER SUB-PART (API has dropped subagents today): corner-definition, plant-training,
  timing/funding, investment-guard, tests, gates — separate commits with the trailer
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. If inference API errors, commit + stop.
- ECONOMY/SCALE RISK: this touches training/funding (the T-hand + lemon-wall graveyard). It's the
  user's explicit design and attacks a real measured stall, but temper arena expectations and let
  the gate's "trains earlier?" check be the go/no-go before arena.
