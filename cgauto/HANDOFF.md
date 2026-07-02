# Troll Farm — HANDOFF (2026-07-02)

Authoritative project state + everything a fresh agent needs. Read this first, then
`docs/silver-experiment-log.md` (full sweep history) and the memory files under
`~/.claude/projects/-home-tarstars-prj-troll-farm/memory/`.

════════════════════════════════════════════════════════════════════════
## 1. GOAL & CURRENT STATE
════════════════════════════════════════════════════════════════════════
- **Goal:** promote **Silver → Gold** by ranking **above "Boss 4"** in the ranked arena.
- **Live arena bot:** `v1.0.1-denialrace` — **rank 42/681** (up from ~49), ~**66% vs Boss 4** (4W/2L, confirmed final-frame).
- **Best safe bot (working tree `rust/src/main.rs`):** `v1.0.5-safe` = v1.0.1 + a wedge **bug-fix**. Compiles, committed (`e71c080`). **NOT yet resubmitted** (recommended next action — free, low-risk upgrade).
- **"Defeat Boss 4 on ALL maps" (100%) is NOT achievable.** The real Boss 4 is a well-tuned wood-race bot; on a faithful matchup some maps it just wins (better position / near-symmetric coin-flips). Heuristic ceiling ≈ **66–70% real / rank low-40s**, essentially reached.

Ready-to-submit files: **`cgauto/submissions/`** (`v1.0.5-safe.rs` ⭐, `v1.0.1-denialrace.rs` = live, `v1.0.4-woodfarm-cheapchop.rs` = overfit trap) + its README.

════════════════════════════════════════════════════════════════════════
## 2. THE GAME (Silver league)  — see docs/mechanics.md + referee source
════════════════════════════════════════════════════════════════════════
Referee: https://github.com/eulerscheZahl/Troll-Farm (open source).
- Map: point-symmetric, **height 8–11, width = 2·height**, ~**18 trees**, iron + water + rock. Only GRASS walkable; shack cell NOT walkable (troll spawns on it, must move off; DROP from a shack-adjacent cell).
- **Scoring: fruit = 1 pt, WOOD = 4 pt (dominant), IRON = 0.** Trees grow in size (cooldown ticks) then bear ≤3 fruit; **felling a tree gives wood = tree size (capped by free carry); a felled tree is GONE** (only replanting brings trees back). Water speeds cooldown.
- **Training cost = n + stat²** where n = current troll count: **PLUM→movementSpeed, LEMON→carryCapacity, APPLE→harvestPower, IRON→chopPower.** So every troll needs plum; cc4 needs lemon 16; chop needs iron.
- Actions: MOVE/HARVEST/CHOP/DROP/MINE/PLANT type/PICK type/TRAIN ms cc hp chop/WAIT. 50ms/turn (1000ms turn 1). Game ends at 300 turns OR no trees on map.
- **Boss 4** = a MIXED **WOOD-race** bot, ~3 trolls, incl. one dominant `(ms2,cc4,hp2,chop2)` chopper; harvests fruit, plants a base plum orchard, mines iron; scores ~150–283. (NOT the weak `level2/Boss.cs` farmer — that was a red herring; `strategies/boss_real.rs` models that wrong boss, ignore it. The faithful one is `strategies/silver_boss.rs`.)

════════════════════════════════════════════════════════════════════════
## 3. OUR BOT — v1.0.5-safe (the shipped strategy)
════════════════════════════════════════════════════════════════════════
A **wood-race** bot that beats the boss by out-denying + out-farming it:
- Trains cheap **FAST (ms2) choppers `(2,2,1,2)`** — copying the boss's expensive cc4 chopper is WORSE (drains the economy). cc2 = 2 wood/fell.
- Chopper targeting: fell the tree minimizing `dist + DW·manhattan(tree, enemyShack) − WT·size`, with **DW=3 (heavy denial bias)** and WT=0 — i.e. race to the BOSS's trees to starve its wood+fruit. DW was the single biggest lever (67.6%→78% sim, and it transfers to real CG). Falls back to nearest tree for our own wood.
- Harvesters: nearest ripe fruit (throughput); plant a small base PLUM orchard for the plum economy.
- Mines iron to fund chopper training.
- **Wedge fix (v1.0.5):** a FULL troll standing ON the shack cell (e.g. the starter after mining turn-1 iron beside the shack) used to emit MOVE-to-its-own-cell forever → 100% idle, stuck at 1 troll, game lost. Now it targets the nearest walkable shack-adjacent DROP cell.
- Code: `rust/src/main.rs` fn `decide()` (v1.0.5). `decide_v097`/`decide_old` in main.rs are DEAD (kept for history). The sim mirror is `rust/src/strategies/mybot.rs` (keep in sync; it has `envi()` tuning knobs — see below).

════════════════════════════════════════════════════════════════════════
## 4. HOW WE GOT HERE (key findings & lessons)
════════════════════════════════════════════════════════════════════════
1. **The prior handoff was WRONG.** It believed we beat Boss 4 ~70–77%; that was a mid-replay measurement artifact. We were actually LOSING. Real fight = SILVER (not Bronze).
2. **Boss 4 identified** from real-game `@TFSUM` debug dumps + referee: a wood-race chopper bot, not a farmer.
3. **The unlock = a Silver-FAITHFUL sim** (built by a parallel subagent): calibrated `mapgen.rs` (~18–22 tree maps) + `silver_boss.rs`. It's trustworthy because our OLD bots lose to `silver_boss` at the SAME rates they lose to the real boss. Plus a **parallelized `bench` (~9× on all cores)** for fast sweeps.
4. **Tuning ladder (vs silver_boss):** Agent-A default 67.6% → **DW=3 denial 78%** (transfers, → 66% real, rank 42) → woodfarm + cheap chopper **90.5%** (but only 33% real!) → wedge fix.
5. **⚠️ OVERFITTING (the big lesson):** `v1.0.4` (cheap slow ms1 chopper `(1,2,0,2)` + "woodfarm" fruit→wood planting) won **90.5% vs silver_boss but 2W/4L (33%) vs the REAL Boss 4** — it exploited MODEL quirks that fail on real (bigger/watery) maps. **Sim gains past ~78% overfit. Validate on real CG in small increments; don't chase sim win-rate.** Reverted to v1.0.5-safe (robust part only). Woodfarm/cheap-chopper kept behind `MB_WOODFARM` env + git history for careful future A/B.
6. **User ideas tested:** fruit→wood "woodfarm" (great in sim, overfit — plant surplus BANANA since it has no training value); gatherers-first / delay chopper = WORSE (cedes early wood race to a chopper-boss); higher troll cap / map-adaptive chopper count = no help.

════════════════════════════════════════════════════════════════════════
## 5. MEASUREMENT (read before trusting any number)
════════════════════════════════════════════════════════════════════════
**Real CG (ground truth, but treacherous):**
- Trust ONLY a **final-frame** read (replay at 300/300 or N/N). `cgauto/run_games.py` prints a win% — reliable ONLY when it logs `viewer bbox: [101, 43, 752, 470]` (scrub-to-end worked). If bbox height is **0/degenerate**, reads are **mid-replay garbage** (we added a fallback to the known-good rect; verify it triggers). The `[UNCONFIRMED]` tag is a broken turn-counter check — ignore it when bbox is correct.
- Always spot-check `cgauto/lastgame.png` (must show 300/300 with the point totals).
- CG **load-throttles** after heavy daily use (the IDE `.monaco-editor` times out); use a patient retry loop (see `scratchpad/patient_validate.sh` pattern). ~150 games/day-ish.

**Sim (fast, faithful-ish, but overfits past ~78%):**
- `cd rust && cargo build --release && ./target/release/bench mybot silverboss 1000` → win% + margin, parallel, ~a few sec.
- `diag` (score/troll/fruit/wood composition), `trace A B seed who` (per-turn + map + idle%), `probe`, `curve`. Rebuild bins after strategy changes (`cargo build --release --bin diag` etc.) or they're stale.
- Tuning knobs (env, `mybot.rs` only; bake winners into consts in BOTH main.rs+mybot.rs): `MYBOT_DW`(denial, def 3), `MYBOT_WT`(size, def 0), `MYBOT_CHOP`(spec), `MYBOT_NCHOP`, `MYBOT_MAX`, `MB_WOODFARM`(0/1), `MB_WF_MAX/START/END`, `MB_ORCHARD`, `MB_CHOP_MIN_N`, `MYBOT_ADAPT`. mapgen density: `TREE_LO/TREE_HI/WATER_PAIRS/IRON_PAIRS`.

════════════════════════════════════════════════════════════════════════
## 6. FILE MAP
════════════════════════════════════════════════════════════════════════
- `rust/src/main.rs` — **the live single-file CG bot** (v1.0.5-safe). Compile: `rustc --edition 2021 -O src/main.rs`.
- `rust/src/strategies/mybot.rs` — sim mirror of the bot (KEEP IN SYNC with main.rs's decide).
- `rust/src/strategies/silver_boss.rs` — **faithful Boss 4 model** (the sparring partner).
- `rust/src/strategies/{boss4,boss_real}.rs` — OLD wrong boss models (chopper / weak farmer). Ignore.
- `rust/src/strategies/search_bot.rs` — Agent B's lookahead bot; 53% vs faithful boss (weaker), reference only.
- `rust/src/game/engine.rs` — mechanically CORRECT/validated referee sim (`step`). `mapgen.rs` — Silver-calibrated map gen.
- `rust/src/bin/{bench(parallel),diag,trace,probe,curve,tournament}.rs` — measurement tools.
- `cgauto/run_games.py N [main.rs]` — play N real games (win% + lastgame.png). `run_game.py` — 1 DEBUG game (flips DEBUG=true, dumps `@TF`/`@TFSUM` state to `last_console.txt`, scrubs to end). `submit.py <file>` — set code + TEST IN ARENA → YES. `cg.py` — misc IDE ops. Needs `DISPLAY=:0`, `profile/` (Playwright), `cg_session.txt` cookies.
- `cgauto/submissions/` — ready-to-submit versions + README.
- `docs/silver-experiment-log.md` — full sweep/experiment history.
- Memory: `~/.claude/projects/-home-tarstars-prj-troll-farm/memory/` — `silver-pivot.md` (read first), `cg-measurement.md`, `sim-iteration-harness.md`, `main-planner-sync.md`.
- `@TFSUM` debug line (main.rs, when `DEBUG=true`): per turn logs `me/opp` scores, tree count, both inventories, and both players' troll builds `id:ms.cc.hp.chop`. This is how Boss 4's build was reverse-engineered.

════════════════════════════════════════════════════════════════════════
## 7. NEXT STEPS (if continuing)
════════════════════════════════════════════════════════════════════════
1. **Resubmit `v1.0.5-safe`** (`submit.py cgauto/submissions/v1.0.5-safe.rs`) — strict, low-risk upgrade over live v1.0.1 (wedge fix converts iron-beside-shack wedge maps). Confirm rank via LEADERBOARD.
2. To push past ~66–70% real you must **beat the model-overfit trap**: real-CG A/B the woodfarm ALONE (MB_WOODFARM=1, keep ms2 chopper) vs cheap-chopper ALONE, to see if EITHER transfers (v1.0.4 combined both and failed). Do it in small confirmed-final-frame batches.
3. Bigger ideas (higher effort, need real-CG validation, diminishing returns): per-map-type strategy selection (the losses correlate with rich/close-shack/watery maps), or a fundamentally stronger economy. A search/MCTS bot underperformed the heuristic (53% vs faithful boss).
4. **Do NOT** re-optimize purely against `silver_boss` past ~78% — it overfits.

GIT: on branch `session-2026-07-01`. All work committed. HEAD = `e71c080` (v1.0.5-safe). Older versions recoverable via `git log`.
