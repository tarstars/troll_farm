# Decision-rule fits from replays (worker W4, night of 2026-08-27/28)

Everything here was produced from the raw CodinGame replays in
`/home/tarstars/prj/troll_farm/data/raw/games/<gameId>.json` with the code in this directory.
Nothing was fetched from the Arena; no git state was touched.

## The state-reconstruction route (step 1) and its validation

A replay has `2T+1` frames: frame 0 carries the map (`global.inputmodule`), the initial trolls
and trees and both inventories; then per turn one frame per seat with that seat's raw `stdout`,
the second of which is a keyframe with a viewer `diff` (the referee's own entity changes: troll
x / y / carried items per slot, tree health / stage / cooldown resets, new trolls with talents,
new trees with cell and kind) and an `inputmodule` with both inventories after the turn.
The keyframes do NOT carry the full per-turn bot input, only the two inventory lines, so the
exact per-turn state has to be rebuilt.

`reconstruct.py` does it the cheap exact way: it replays both seats' commands through our
referee mirror `sim/engine.py` (pre-turn state -> post-turn state) and then overlays the
keyframe diff and inventories, comparing every diff token with the engine's prediction before
overwriting it. Result over all 215 full-length delineate games and 184 norxondor games
(399 games x 300 turns):

* inventories, carried items, tree health, tree creation and death, troll creation, final
  scores: **0 disagreements** between engine and referee;
* troll positions: disagreements only for speed-2/3 trolls at equal-best path ties (the referee
  breaks them randomly, the engine lexicographically; e.g. 36 + 27 tokens in game 896599682) --
  the diff is the authority there and corrects the engine, so every stored state is the
  referee's;
* the only engine-side inference that the diff never echoes is tree growth (size and fruit
  counts); it is validated indirectly: every growth-driven health change and every harvest
  amount reported by the referee matched (0 `plant_health` / `plant_stage` / `inventory`
  mismatches).

So the per-turn states (map, every tree with kind/size/health/fruits/cooldown, every troll with
position/talents/carry, both inventories) are exact; a bot's pre-turn input can be printed
from them verbatim. One game takes 0.2 s.

Numeric plant aliases (`PICK 1 0`, `PLANT 3 2` = PLUM..BANANA by index) are normalised.

## Files

* `reconstruct.py` -- the route above; `python3 reconstruct.py <gameId>` prints the validation
  summary; `reconstruct(game_id)` returns the per-turn states.
* `decision_tables.py` -- builds `tables/<player>_trips.jsonl.gz` (one row per unit *trip*: a
  run of step-wise MOVEs ending in the first non-move action, with the pre-turn decision state
  and every living tree as a candidate with BFS distances) and `tables/<player>_turns.jsonl.gz`
  (one row per player-turn: inventories, roster, TRAIN command, tree counts).
  Both top bots emit step-wise MOVEs (target = next cell), so a destination can only be read
  from where the troll eventually acted.
* `fit_rules.py` -- the rule fits; `python3 fit_rules.py <player> [chop train plant harvest
  endgame roles]`; results also in `<player>_fit_results.json`.
* `delineate.md`, `norxondor.md` -- the fitted rules, accuracies, rejected alternatives and
  counter-examples per player (the deep ones); `MSz.md`, `Bubaptik.md` -- first passes over
  the same fits (Bubaptik = its latest agent 6568138 only; the other 35 agent ids are earlier
  versions of the same player and were not used).
* `tables/` -- the decision tables (gzipped JSON lines, < 10 MB each): 215 delineate games,
  184 norxondor, 203 MSz, 182 Bubaptik -- every 300-turn game of each.
* `<player>_fit_results.json` -- machine-readable copies of the fit numbers.

Validation over all four players: 784 games, every one "exact" apart from the random path
ties of fast trolls that the diff corrects (see above).

Accuracy convention: "share of decisions whose actual target is in the rule's arg-max set"; when
the rule leaves ties, the *expected* accuracy with a random tie-break is given too, and the
honest number is the second one.
