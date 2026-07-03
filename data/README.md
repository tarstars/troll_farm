# Troll Farm game-record dataset

Replays of **CodinGame Spring Challenge 2026 — Troll Farm** arena games, collected from
the public CodinGame services (no auth) for strategy analysis and future RL training.

- **Collected:** 2026-07-03 (single snapshot; re-run `scripts/collect.py` to extend).
- **Our bot at collection time:** `tass`, agentId **6536563**, **Gold** league,
  global rank 509, arena score 11.04. Live code: `v1.2.2-farmcap` (per in-game MSG).
- **Size:** raw 91 MB, processed 15 MB.

## Counts

| what | n |
|---|---|
| raw replays fetched | **290** (0 fetch failures, 0 parse failures) |
| tass games (all finished battles of the current agent) | 140 (+1 where tass appears in a top player's list) — 80W/61L |
| top-15 Legend players' recent games | 75 (5 each) |
| top-15 Gold players' recent games | 75 (5 each) |
| unique maps | **290** — every game has a freshly generated map (0 hash-duplicates) |
| unique players seen | 136 pseudos (183 agentIds — players resubmit) |
| participant league mix | Legend 167, Gold 413 (per-seat, of 580 seats) |
| boss games | 0 (arena `arenaboss` field always null in this sample) |
| full-length games (300 turns) | 266; the other 24 ended early (crash/timeout or all trees felled) |

## Directory layout

```
data/
  raw/
    leaderboard.json      full top-1000 leaderboard snapshot
    players.json          the 31 selected players (tass + top15 Legend + top15 Gold)
    battles/<agentId>.json  findLastBattlesByAgentId responses (battle lists)
    games/<gameId>.json   raw replays (gameResult/findByGameId, verbatim)
    fetch_log.json        per-gameId fetch status
    collect_run1.log      collection run log (provenance)
  processed/
    games.jsonl           one line per game (schema below)
    maps.jsonl            unique maps = THE REAL MAP CORPUS for mapgen calibration
    trajectories/<gameId>.jsonl  per-turn records for RL
    stats.json            dataset-level counts
    parse_failures.json   games that failed to parse (currently empty)
  scripts/
    collect.py            fetch leaderboard -> battles -> replays (idempotent)
    parse.py              raw -> processed
    qa.py                 end-to-end consistency checks
```

## processed/games.jsonl — one JSON object per game

```jsonc
{
  "gameId": 895035298,
  "players": [            // index-aligned with scores/ranks/per_player
    {"index":0, "agentId":6480900, "name":"eltoto", "isBoss":false,
     "league":"Gold", "leagueIndex":4, "arenaScore":10.79}, ...],
  "scores": [191.0, 243.0],   // official final scores (crashed player gets -1/-2)
  "ranks":  [1, 0],           // 0 = winner
  "n_turns": 300,
  "map_hash": "…",            // sha1[:16] of the terrain rows, joins to maps.jsonl
  "map": {
    "w":16, "h":8, "rows":["....#........#..", …],  // '.' walk '#' rock '+' iron '~' water '0'/'1' shacks
    "shacks": {"p0":[4,2], "p1":[11,5]},
    "iron": [[x,y],…], "water": [[x,y],…],
    "trees0": [{"type":"APPLE","x":3,"y":2,"size":4,"fruits":1,
                "stage":5,"health":20,"cur_cd":9,"cd_eff":9}, …]  // initial trees
  },
  "trolls0": [{"id":0,"player":0,"x":4,"y":2,"ms":1,"cc":1,"hp":1,"chop":1}, …],
  "per_player": {
    "0": { … }, "1": {
      "commands_summary": {"MOVE":493,"CHOP":91,"PLANT":51,…},  // attempted (from stdout)
      "trains": [[1,[2,1,2,2]], [104,[1,2,1,2]]],               // [turn, [ms,cc,hp,chop]]
      "plants_by_type": {"BANANA":34,…},                        // PLANT commands issued
      "planted_ok": {"BANANA":34,…},                            // plants that succeeded (referee summary)
      "harvested": {"LEMON":30,…},                              // fruits actually harvested
      "effects": {"collected_WOOD":57,"trained":2,"failed":12,…}, // other referee-confirmed effects
      "wood_curve":  [w100,w200,w300],                          // banked WOOD at end of t100/200/300 (null if game over)
      "score_curve": [s50,s100,s150,s200,s250,s300],            // fruits + 4*wood, end-of-turn
      "final_inv": [3,3,1,0,7,34]                               // [PLUM,LEMON,APPLE,BANANA,IRON,WOOD]
    }
  }
}
```

## processed/maps.jsonl — the real map corpus (290 unique maps)

One line per unique terrain (deduped by row-hash; in practice 1 map : 1 game).
Fields: `map_hash, w, h, rows, shacks, counts{walkable,rock,iron,water},
iron_cells, water_cells, tree_total, tree_counts{type:n}, trees0[…], n_games, gameIds`.

**Calibration facts for `sim/mapgen.py`** (measured over the 290 maps):

| dims | n | trees avg[min-max] | water | iron | rock |
|---|---|---|---|---|---|
| 16x8  | 68 | 15.9 [8-22] | 28.5 [14-52] | 2.9 [2-4] | 7.1 [2-18] |
| 18x9  | 70 | 15.7 [10-24] | 30.0 [10-56] | 2.9 [2-4] | 9.1 [2-20] |
| 20x10 | 84 | 15.9 [8-22] | 35.9 [10-74] | 2.9 [2-4] | 9.0 [2-20] |
| 22x11 | 68 | 16.1 [10-24] | 42.4 [16-82] | 2.9 [2-4] | 10.0 [2-20] |

- Four size classes only, roughly uniform. **Total tree count does NOT scale with
  area** (~16 either way) — tree density falls on big maps.
- Per-type tree counts 2-6 (even), ~4.0 avg each of PLUM/LEMON/APPLE/BANANA.
- Everything is point-symmetric (180° about map center): trees 290/290, water, iron
  (exactly 2 or 4 iron cells: 161/129 games), rocks, shacks.
- Initial tree stage (= size+fruits after referee pre-aging) is ~uniform over 1..7:
  {1:676, 2:716, 3:690, 4:694, 5:598, 6:710, 7:528} over all 4604 initial trees.
- Starting trolls: always exactly one `(ms,cc,hp,chop)=(1,1,1,1)` per player on the shack.
- Starting inventories: identical for both players, per-slot ~uniform in **[2,10]**
  for PLUM/LEMON/APPLE/BANANA/IRON, WOOD always 0.

## processed/trajectories/<gameId>.jsonl — RL turn records

One line per turn:
```jsonc
{"t":1,
 "inv0":[10,6,4,6,6,0], "inv1":[10,6,4,6,6,0],  // inventories at the START of turn t
 "commands0":"TRAIN 3 2 1 2;MOVE 0 3 2;",        // player 0's raw stdout that turn (null if silent/crashed)
 "commands1":"MSG v1.2.2-farmcap;MOVE 1 3 2"}
```
- Inventory order: **[PLUM, LEMON, APPLE, BANANA, IRON, WOOD]** (matches
  `sim.validate_replay.ITEMS`). Score = `sum(inv[0:4]) + 4*inv[5]`.
- **Positions are omitted** — troll/tree positions are exactly derivable by replaying
  `commands0/commands1` from the initial state (`map.trees0` + `trolls0` in
  games.jsonl) through `sim/engine.py` (see `sim/validate_replay.py` for the
  harness pattern). Referee action summaries remain in the raw replays
  (`frames[].summary`) if ground truth is needed.

## Replay `view` format (reverse-engineered, verified)

`frames[0].view` = `" 0\n" + JSON`:
- `global.inputmodule` = `"W H\nrow0\n…"` terrain grid.
- `frame.diff` = initial entities, `;`-separated, base-36 single chars:
  - troll: `<entId> W <id><x><y><player><ms><cc><hp><chop>`
  - tree: `<entId> P <x><y><type><stage><cur_cd><health><cd_eff>` where
    type `0=PLUM 1=LEMON 2=APPLE 3=BANANA`; `stage=size+fruits`
    (MAX_SIZE=4, MAX_FRUITS=3 → `size=min(stage,4)`, `fruits=max(0,stage-4)`);
    `cur_cd` = turns until next growth tick; `cd_eff` = growth cooldown
    (base PLUM 8 / LEMON 8 / APPLE 9 / BANANA 6, minus water boost 5/5/7/2 if
    water-adjacent — matches `sim/engine.py` `WATER_BOOST`).
- `frame.inputmodule` = both starting inventories (`"<inv p0>\n<inv p1>"`).

`frames[i>0]`: `agentId` = acting player index (0/1), `stdout` = that player's raw
commands. Every 2nd frame is a `keyframe` whose view JSON carries
`inputmodule` = both inventories AFTER the turn, plus a `diff` of tree/troll
property updates (`x`,`y` troll pos; `h` tree health; `s` stage; `c` cooldown) and
`summary` = referee action log (`$0:`/`$1:` prefixed; `[failed] …` lines included).

**Verification** (see `scripts/qa.py`): final scores recomputed from parsed
inventories match the official `scores[]` exactly in **289/290** games (the one
exception is a turn-48 opponent timeout, official score −2 by rule); tree decoding
passes range/symmetry invariants 290/290; type decoding cross-checked against
`"planted a <TYPE>"` referee summaries; health verified against chop damage
(−chop/turn, fell at 0); `cur_cd` verified against observed growth ticks; troll spec
encoding verified against `TRAIN` commands; water-boost values match `sim/engine.py`.

## Exact API calls (to extend the dataset)

All POST, `Content-Type: application/json`, public, no auth. Be polite: ~0.35 s
between calls, 20 s timeout (`curl -m 20`).

```bash
# 1. leaderboard (top 1000; divisionIndex 3=Silver 4=Gold 5=Legend)
curl -m 20 -X POST https://www.codingame.com/services/Leaderboards/getFilteredPuzzleLeaderboard \
  -H 'Content-Type: application/json' \
  -d '["spring-challenge-2026-troll-farm", null, "global", {"active":false,"column":"","filter":""}]'
# 2. battle list for an agent (returns ~90-230 most recent battles: {gameId, players[], done})
curl -m 20 -X POST https://www.codingame.com/services/gamesPlayersRanking/findLastBattlesByAgentId \
  -H 'Content-Type: application/json' -d '[AGENTID, null]'
# 3. replay
curl -m 20 -X POST https://www.codingame.com/services/gameResult/findByGameId \
  -H 'Content-Type: application/json' -d '[GAMEID, null]'
```

Or simply re-run (idempotent, skips already-downloaded games, then re-parse):
```bash
python3 data/scripts/collect.py && python3 data/scripts/parse.py && python3 data/scripts/qa.py
```

## Known limitations

- **No stderr**: bots' debug output is not in replays; only stdout commands, referee
  summaries, and the view state.
- **Positions must be re-derived** by replaying commands through `sim/engine.py`
  (trajectories carry inventories + commands only). Referee summaries in raw
  replays give move-by-move ground truth for spot checks.
- **Only the current agent's battles are reachable** (~140 most recent per agent).
  Older tass submissions' games are lost — no historical agentIds were recorded
  anywhere in the repo (checked cgauto logs). Battle lists rotate: re-run
  `collect.py` regularly to accumulate history. `raw/battles/*.json` show each
  selected player's last ~90-230 battles but replays were only fetched for the
  5 most recent per top player.
- **League labels** come from the collection-day leaderboard (matched by
  `codingamer.userId`); players outside the top 1000 would get `league: null`
  (none in this sample).
- **Boss games**: none present (bosses only appear in promotion-window battles).
  `players[].isBoss` flags them if collected later.
- Crashed/timeout games: official score is −1/−2 for the crasher and `n_turns<300`;
  `per_player.*.final_inv`-derived scores still reflect banked resources.
- Leaderboard snapshot is top-1000 only (`count` field says 4245 total players).

## Local opponent pool

For RL self-play seeding / evaluation ladders, the repo already contains:

### Ready-to-submit CG bots (`cgauto/submissions/*.rs`, single-file, stdlib-only)

Progression of our arena bot (all "Troll Farm bot" Rust ports; `VERSION` const in file;
detailed history in `docs/silver-experiment-log.md`):

| file | one-liner |
|---|---|
| v1.0.1-denialrace.rs | DW=3 denial wood-race; once rank 42/681 Silver, 66% real vs Boss 4 |
| v1.0.4-woodfarm-cheapchop.rs | ⚠️ canonical OVERFIT trap: 90.5% sim / 33% real; do not submit |
| v1.0.5-safe.rs | v1.0.1 + wedge bug-fix (full troll stuck on shack cell); safe fallback |
| v1.0.6-tempo.rs | + endgame banking, (2,2,0,2) chopper, ripeness anticipation; real 5W/3L |
| v1.0.7-woodfarm.rs | + surplus-fruit→banana wood plantation (woodfarm alone) |
| v1.0.8-woodprinter.rs | + banana PICK+replant "wood printer" (copied from arena player aRi); real 5W/3L |
| v1.0.9-mower.rs | + chop1 harvesters mowing own farm; sim-best BUT 2W/6L real (2nd sim-reality inversion) — quarantined |
| v1.1.0-sched.rs | scheduler architecture rebuild: global greedy (troll,task) marginal-rate assignment; "camper" denial |
| v1.1.1-sched.rs | + livelock fix, LATE_FREE=80 |
| v1.1.2-sched.rs | + anticipate-contention fix, single-banana-ferry gate → rank 3/681 Silver |
| v1.1.3-sched.rs | + raid gate (pause printer near enemy chopper) → arena REGRESSION (rank 51), reverted |
| v1.1.4-crops.rs | species-aware water-crop placement |
| v1.1.5-nolock.rs | livelock family eradicated → rank 1/681 Silver (peak 23.96) |
| v1.1.6-clear.rs | + mine-wedge fix, late-plant cutoff, clear-when-ahead |
| v1.1.7-lemonchoke.rs | lemon-choke vs boss's train-blocking — arena-falsified within one cycle |
| v1.1.8-safe.rs | = v1.1.6 behavior; converged 22.77, rank 2 Silver |
| v1.1.9-morning.rs | v1.1.5 behavior + mine-wedge fix; **the bot that promoted to GOLD** (2026-07-03 03:40) |
| v1.2.0-market.rs | Gold era: deficit-weighted harvesting, market mower, late liquidation; 71% wins avg 172 |
| v1.2.1-yield.rs | yield-mode from t20 (LIQ_T=280); denial only in the opening |
| v1.2.2-farmcap.rs | WF_MAX=10 two-big-farms (from Gold top-2 decode) — **live arena bot in this dataset's tass games** |
| v1.3.0-rhea.rs | RHEA (rolling-horizon evolutionary) experiment line |
| v1.3.1-assets.rs / v1.3.2-slim.rs / v1.3.3-unstall.rs | latest 1.3.x iterations (assets/slimming/unstall fixes) |

### Local strategy roster (`rust/src/strategies/mod.rs`, tournament-pluggable)

`planner_strategy::Planner, gatherer::Gatherer, orchard::Orchard, boss4::Boss4,
boss_real::BossReal (wrong-boss model, historical), chopper::Chopper,
harvester::Harvester, balanced::Balanced, search_bot::SearchBot,
silver_boss::SilverBoss (faithful Boss-4 model), script_boss::ScriptBoss
(referee-script boss), boss_v3::BossV3, printer_bot::PrinterBot (decoded field
archetype), sched_bot::SchedBot (scheduler architecture), rhea_bot::RheaBot,
mybot::MyBot (main heuristic line)` — plus `sim/` (Python mirror engine, validated
vs real referee via `sim/validate_replay.py`).
