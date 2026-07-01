# Troll Farm — Handoff (2026-07-01, session 2)

## Goal (UNMET): rank above **Boss 4** in **Silver** → promote to Gold. Currently rank ~49/681 Silver.

## THE BIG CORRECTION (previous handoff was based on a wrong model)
The old handoff claimed "v0.8.3 beats Boss 4 ~70-77%". **That was a measurement artifact** — mid-replay
reads of the live "1ST/2ND" panel. **Reality (confirmed final-frame screenshots): our bots LOSE to Boss 4**
(v0.8.3-class chopper lost 89-222). Only trust a **300/300 final-frame screenshot** (`lastgame.png`), never
`run_games.py`'s win% counter. See memory `cg-measurement`.

## What Boss 4 actually is (from real-game `@TFSUM` debug + referee source)
A **mixed bot, ~3 trolls, that WINS ON WOOD**. Its engine is a **`(2,4,2,2)` chopper** (carryCapacity 4,
chopPower 2, speed 2) that fells trees for 4 wood = **16 pts each** (one game: 184 of its 283 pts were wood).
It keeps ~1 dedicated chopper + harvesters, so trees survive (they regrow — chopping is sustainable). It is
NOT `config/level2/Boss.cs` (a weak 2-troll farmer — a red herring; ignore `strategies/boss_real.rs`).

## Why WOOD matters: 4 pts/unit vs 1 pt/fruit. A cc4 chopper on a size-4 BANANA (health 3-6) makes 4 wood
(16 pts) in ~2-3 turns. That's the game. Harvesting fruit alone caps ~110; the boss's wood pushes it to ~200-280.

## Current bot state (working tree, UNCOMMITTED)
`rust/src/main.rs` = **v0.9.7** — a clean new `decide()` (old economic planner kept as dead `decide_old`):
- trains: starter + 1 harvester, then SAVE for one strong chopper (cc>=3), then hp-harvesters;
- one dedicated chopper (strongest chop>=2) **CHOPs** the nearest tree (never harvests, or it never fells);
- harvesters take the nearest fruited tree, PREFERRING the scarce training resource (fixes APPLE starvation
  that capped us at 2 trolls); chop-capable trolls MINE iron when saving for the chopper;
- banks with the wedge-free nearest-drop-cell logic.
**Result: v0.9.7 ~115 vs boss ~202** (led at turn 150, then the boss's cc4 chopper out-wooded our cc3 one).
Best of the 8-version ladder (86→115). **Still loses. NOT submitted to arena** (would risk rank 49).
Committed HEAD = v0.8.3 (the safe arena bot).

## Clearest next steps (to actually win)
1. **Get a cc4 chopper built EARLY** (boss has `(2,4,2,2)` by ~turn 100). cc4 needs lemon `n+16` — harvest
   lemon hard + mine iron; consider raising the chopper bar to cc>=4 (risk: stalling — v0.9.5 stalled 1 iron short).
2. Maybe field **2 choppers** for more wood, but keep >=2 harvesters so the map isn't scorched (all-chop = 58, scorched).
3. The local sim (`rust/`) is **NOT Silver-faithful** (too sparse; every bot beats the modeled boss). Either make
   mapgen dense (`TREE_LO/TREE_HI/WATER_PAIRS` env knobs added) AND port the REAL boss (cc4 chopper), or keep
   iterating on real CG. Real games are ~2-3 min each, ~150/day throttle.

## Tooling
- `cgauto/run_games.py N [main.rs]` — N real games; IGNORE the %, read `lastgame.png` (must show 300/300).
- `cgauto/run_game.py` — 1 DEBUG game, scrubs to end, saves `last_console.txt`. Grep `@TFSUM` for the final
  line: `me/opp` scores, `trees`, both inventories, and both `mybuilds/oppbuilds` (troll stats id:ms.cc.hp.chop).
  This is the key diagnostic — it revealed the boss's builds and our resource starvation.
- `@TFSUM`/`@TFD` are emitted by main.rs when `DEBUG=true` (run_game.py flips it automatically).
Login: DISPLAY=:0 + persistent Playwright profile in `cgauto/profile/` + cookies in `cg_session.txt`.
