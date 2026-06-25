# v0.6.1 lost-game analysis (full both-player reconstruction)

Source: `docs/plays/game_v061_ide.html` (IDE DOM dump, 2026-06-25). The dump
interleaves both agents' per-turn stdout (600 subframes = 300 turns x 2 players;
even idx = us/player 0, odd idx = opponent/player 1). This gives BOTH command
streams — the whole game is reconstructable.

## Command-verb comparison (whole game)

| verb     | US (v0.6.1) | Winner |
|----------|-------------|--------|
| trolls   | **2** (ids 0,2) | **3** (ids 1,3,4) |
| MINE     | **1**       | 6      |
| PLANT    | **38**      | 5      |
| PICK     | 34          | 5      |
| HARVEST  | 32          | **54** |
| DROP     | 53          | **70** |
| CHOP     | 90          | 96     |
| MOVE     | 350         | 547    |

## Root causes (ranked)

1. **Iron starvation -> 2-troll cap.** Training costs IRON in Bronze. We MINE
   only once all game -> almost no iron -> after the first chopper we can't fund
   any gatherer -> stuck at 2 while the winner reaches 3. CONFIRMED in sim:
   v0.6.1 averages 1.3 MINE commands/game, 2.17 trolls. The cause is behavioural:
   `chop_command` only mines when *incidentally adjacent* to iron, and the
   chopper hunts trees near the ENEMY camp (our denial heuristic), so it is
   rarely near our iron. It never ROUTES to iron.

2. **Orchard over-investment / churn.** We PLANT 38 + PICK 34 (~72 troll-turns)
   vs the winner's 5 plants. 38 plants for a 3-cell footprint = constant
   re-PICK/re-PLANT churn (a troll cycling PICK->PLANT-fails->PICK), burning a
   troll's whole game on busywork instead of harvesting/banking.

3. **Under-production.** Consequence of 1+2: HARVEST 32 vs 54, DROP 53 vs 70.
   The winner runs a lean economy (almost no planting, mines iron, 3 trolls all
   harvesting) and simply out-produces us.

## Fix direction

Lean economy targeting the winner's profile: (a) the chopper/a troll must
deliberately ROUTE to iron and bank enough to fund training (fixes the 2-troll
cap at the source); (b) cut the planting churn so trolls harvest natural trees
instead. NOTE: self-play (us-vs-us on generate_bronze) has consistently rejected
expansion and anti-planting — but this replay is GROUND TRUTH that a lean 3-troll
bot beats v0.6.1, so trust the replay over self-play here and let the ARENA judge.
