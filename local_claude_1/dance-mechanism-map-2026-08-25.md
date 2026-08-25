# Mechanism map — where the champion produces a dance, in the code's own terms (2026-08-25)

Read-only map of `cgauto/submissions/candidate-door1-pure-deletion.rs` (`547fa706…`), produced by a
local Opus subagent on the coordinator's brief and checked by the coordinator against the source
(lines 700–778, 167–187, 1305–1332 read directly). Companion to
`local_claude_1/dance-cure-proposal-2026-08-24.md`; held with it until chatgpt_1's proposal lands.
Cite as `:line`.

## 1. Candidate generation (per troll)

- Router `:1394-1427`: `endgame_candidates` if a regeneration commitment exists or `endgame()`
  (`:1370`); `early_candidates` before the second troll; otherwise `main_candidates` `:1161-1199`,
  whose order is `wait()` first (`:1162`), bank if carrying and adjacent, PICK for regeneration,
  bank if full, then chops.
- `chop_candidates` `:576-631` iterates every plant with health > 0, **no exclusion for the other
  own troll**: `travel_turns` `:589` → `predict_tree(view, plant, travel_turns)` `:590` →
  `chop_outcome` `:601` → `turns = travel + chop + return + 1` `:605`, `wood = final_size.min(free)`
  `:609`, **`score = 1000·wood/turns`** `:613`; CHOP if on the cell else MOVE `:618`; target
  `Target::Tree(plant.cell)` `:626`. Gate `:578`: no chop power or no capacity → empty.
- Teammate awareness exists in exactly three places — `YamoBot::bank_candidates` `:941-949`
  (bank cells another own unit stands on), endgame PLANT `:1240-1243` and PICK `:1311-1316` cell
  filters — and nowhere else (`fruit_candidates` `:463-484`, `iron_candidates` `:485-508`,
  `idle_harvest_candidates` `:1347-1352`). Only enemies are modelled on trees (`predicted_opp_chop`
  `:509-515`, `player==1`).
- Dead code: `yamo_chop_candidates` `:1122-1160` never runs (`opponent_eta_penalty` is 0 at `:777`
  and never assigned).

## 2. Joint selection

- `select` `:659-706`: full cross product of the two trolls' lists, maximise `a.score + b.score`
  (`:677`) subject to `compatible` and `stock_compatible` (`:674`); strict `>` so the first pair in
  push order wins ties (`wait()` first). Greedy fallback `:688-705` can leave a troll with WAIT.
- `compatible` `:637-648`: `Target::None` is compatible with everything (`:638`); otherwise the two
  targets are incompatible **iff they name the same cell** (`:645`). Routes are not considered.
- A working troll's target is its **own cell** (CHOP `:618/:626`, PICK `:1174/:1298`, PLANT `:1266`,
  DROP `:376-388`) — so the other troll can never name the worker's cell as a target. This is the
  code reason the dancer's target is always elsewhere (34 of 34).
- `force_unique_door_clear` `:972-1087` (single-door shacks only, `:950-953`) can overwrite a troll's
  whole candidate list with one forced 20 000-score move; it constructs explicit swaps at
  `:1038-1041` and `:1067-1071`.

## 3. Movement

- The emitted MOVE is always the bot's **own next cell**, never the final target:
  `landing = next_cell(walkable, unit.cell, target, speed)` `:725`, `MOVE id landing` `:752`. The
  referee's random tie-break is bypassed.
- `next_cell` `:167-187` and `bfs_distances` `:147-166` take only `walkable`: **the teammate's cell is
  never an obstacle in planning**; deterministic lexicographic tie-break `:186`.
- Executor `resolve_move_conflicts_with_priority_and_forbidden` `:720-772`: `moving_ids` `:729`;
  `occupied_now` = all own cells `:730`; `reserved` = cells of own units **not moving** `:731` (a
  troll emitting CHOP/HARVEST/PICK/PLANT/DROP/WAIT is not a mover, so its cell is reserved); movers
  sorted by priority then **descending unit id** `:738-743`; a free landing is taken and reserved
  `:749-753`; otherwise the **detour** `:755-762`: orthogonal neighbours of the *current* cell that
  are walkable, not reserved, not occupied, minimising `(bfs distance to target, cell)`; WAIT only
  if that set is empty `:767-769`. **`unit.cell` is not in the detour set — the troll must move.**
  The detour is one cell even when `movement_speed` is 2–3 (`:846`), while `:725` may land up to
  `speed` away.
- `priority_ids` and `forbidden_for_non_priority` are empty at the live call site
  (`:1432 → :715 → :718`): `:749` never fires, `:757` is a no-op. An existing hook, unused.
- Swaps are emitted (a) accidentally — both trolls moving, each landing on the other's current
  cell, neither cell reserved (`:731`, `:750-752`); (b) deliberately by the door-clear code above.
- **No cross-turn movement memory of any kind.** State struct `:335`, init `:777`: announcement
  flags, `type_to_cut` (set once `:791-793`), opening fields, feature flags `:783-787`,
  `regeneration_commitments` (`:1088-1121`, read `:1395`), `opponent_eta_penalty` (dead). Absent:
  previous position, previous command, oscillation counter, waypoint commitment, forbidden set,
  teammate reservation table.

## 4. No work

`wait()` `:632-636` is pushed first in every generator; idle path `:1184-1191`
(`idle_regeneration && chops.is_empty()` → WAIT + `idle_harvest_candidates` + bank);
`idle_harvest_candidates` `:1339-1368` (score `1/trip`, always loses to a chop); final WAIT
`:1435-1437`; a self-targeting MOVE becomes WAIT `:732-736`.

## 5. The dance, traced

- **P1 — forced move under a static reservation [READ].** t: dancer at `a`, chop target `T`;
  teammate CHOPs on `c` → `c ∈ reserved`. `next_cell(a, T) = c`; `:750` fails; detour picks `b`
  with `dist(b) = dist(a) + 1` (the vacated cell is the least-bad neighbour in a corridor); the
  troll cannot hold `a`. t+1: at `b`, `next_cell(b, T) = a`, now free → `MOVE a`. t+2 ≡ t. The only
  thing that changes between turns is the dancer's own cell. Matches the rows: 75 of 77 episodes
  forward/back along the path; 32 of 34 blockers on the forward step.
- **P2 — landing-reservation alternation [INFERRED].** A chop-and-step teammate's cell is
  reserved on chop turns and free on move turns (and on move turns its *landing* is reserved
  first, higher id wins `:741`); the dancer's forward step is blocked on alternate turns → the same
  forced-move flap with a moving blocker.
- **P3 — argmax flip from horizon-phase jitter [READ formula / INFERRED flip].** One cell of travel
  changes `predict_tree`'s phase → `wood` ±1 → score ±30–70 points, non-monotonic (`:589-613`);
  any second tree in that band swaps rank; stepping toward it swaps back. Also: candidates blink
  when `predict_tree` returns `None` for an enemy-occupied tree (`:523-528`) or the horizon check
  `:606-608` fails; and the pair sum (`:669-687`) lets the *teammate's* scores decide which troll
  yields a shared best tree.
- **P4 — trade [READ].** `:729-731` + `:744-754`, or the door-clear swaps.

## 6. Composition walls

1. `compatible` (never both to one cell) + `reserved`/`:750` (never step on a standing teammate)
   + detour `:756` (if blocked, take the best free neighbour): each right alone; together an
   unbounded two-cycle in which the blocked step is re-proposed and re-rejected every turn.
2. Split world model: planner unit-blind (`:167-187`), executor occupancy-aware (`:720-772`);
   nothing carries the rejection back into planning.
3. Route-blind compatibility (`:646` compares destination cells only) + unit-blind pathing: the
   two trolls' *routes* are never deconflicted, only their destinations.
