# Troll Farm — HANDOFF (2026-07-02, updated by review session)

Authoritative project state + everything a fresh agent needs. Read this first, then
`docs/silver-experiment-log.md` (full sweep history) and the memory files under
`~/.claude/projects/-home-tarstars-prj-troll-farm/memory/`.

════════════════════════════════════════════════════════════════════════
## 1. GOAL & CURRENT STATE
════════════════════════════════════════════════════════════════════════
- **Goal (user, 2026-07-02): advance to the GOLD league** = rank **above "Boss 4"** in
  the ranked arena.
- **Live arena bot (submitted 2026-07-02 ~10:20): `v1.0.6-tempo`** — real-validated
  **5W/3L (62%)** vs Boss 4 (bbox-good batch + 300/300 screenshot, tass 221–116), then
  submitted. Prior v1.0.1 had slid to **rank 134/682** (was 42/681 a day before — the
  field improves fast). Watch the new rank converge on the LEADERBOARD.
- **THE BAR (measured via public leaderboard API, see log):** tass score ~15;
  top-of-Silver ~20–24; **Boss 4 ranks ABOVE Silver's #1** ⇒ promotion ≈ be the best
  bot in Silver. Head-to-head 60-66% vs the boss is NOT sufficient — the rating gap is
  earned vs the whole field.
- **Working tree `rust/src/main.rs`:** `v1.0.6-tempo` = v1.0.5-safe + endgame banking +
  `(2,2,0,2)` chopper + ripeness anticipation + water-adjacent orchard placement — each
  validated on BOTH boss models (§5a). Compiles standalone, committed.
- **NEW (this session): `scriptboss`** — a model of the REAL Boss 4 script (from a real
  DEBUG dump), structurally different from `silver_boss`. See §5a. The old "ceiling
  ~66–70%, essentially reached" claim was MODEL-specific: loss decomposition vs scriptboss
  shows 30% both-seat (systematic → in-principle fixable) + 18% one-seat, vs 15/15 on
  silver_boss. Obvious knobs are exhausted, but the ceiling story is softer than §8 claims.

Ready-to-submit files: **`cgauto/submissions/`** (`v1.0.6-tempo.rs` ⭐ pending real
validation, `v1.0.5-safe.rs` = fallback, `v1.0.1-denialrace.rs` = live, `v1.0.4` = overfit
trap) + its README.

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
## 3. OUR BOT — v1.0.6-tempo (working tree; v1.0.1 is live in arena)
════════════════════════════════════════════════════════════════════════
v1.0.6-tempo = everything below PLUS (all both-model-validated, see §5a):
- **Endgame banking:** any troll carrying anything returns + DROPs before t=300
  (was: partial carries stranded = dead points; a chopper's stranded wood = 4 pts each).
- **Chopper spec (2,2,0,2)** (hp1→hp0): saves n+1 APPLE per chopper.
- **Ripeness anticipation:** when nothing is ripe, pre-position at the tree whose first
  fruit lands soonest relative to arrival (minimize max(travel, time-to-ripe)).

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
- Tuning knobs (env, `mybot.rs` only; bake winners into consts in BOTH main.rs+mybot.rs): `MYBOT_DW`(denial, def 3), `MYBOT_WT`(size, def 0), `MYBOT_CHOP`(spec, def 2,2,0,2), `MYBOT_NCHOP`, `MYBOT_MAX`, `MB_ENDBANK`(1), `MB_RIPE`(1), `MB_WOODFARM`(0/1), `MB_WF_MAX/START/END`, `MB_ORCHARD`, `MB_CHOP_MIN_N`, `MYBOT_ADAPT`, dead-ends kept off: `MB_FELLT`(0), `MB_DEFICIT`(0), `MB_LEMONW`(0). mapgen density: `TREE_LO/TREE_HI/WATER_PAIRS/IRON_PAIRS`.

════════════════════════════════════════════════════════════════════════
## 5a. TWO BOSS MODELS — the both-models decision rule (2026-07-02)
════════════════════════════════════════════════════════════════════════
A real-game DEBUG dump (was sitting uncommitted in `cgauto/last_console.txt`; committed
knowledge now) revealed the REAL Boss 4 script, and it is NOT what `silver_boss` plays:
- t~2 train **(1,1,1,2)**; starter PICKs a LEMON, PLANTs a base LEMON orchard, MINEs iron.
- Harvesting is **LOCAL** (starter never left radius 5 of its shack in 300 turns; util
  troll avg 4.7) — measured from the dump's per-turn `@TFD` positions.
- Hoard to **lemon 18** (+6 plum/6 apple/6 iron), **t~150 train ONE (2,4,2,2)**, which
  then CHOPs every single turn (fells = 4 wood = 16 pts, raids into our half).
  Wood stays ~0 before t~190. **No 4th troll ever** (23 lemon banked unspent at t=300).
`rust/src/strategies/script_boss.rs` (= `scriptboss` in the roster) models this shape.

**Anchor calibration** (bot: real% / vs silver_boss / vs scriptboss):
mybot-v1.0.5: ~66 / 77.6 / 60.6 · v1.0.4-config: ~33 / **90.5 (inverted!)** / 56.9 ·
planner: 35 / ~35 / 22.6 · gatherer: 31 / ~31 / 20.4. scriptboss gets the ordering
right where silver_boss failed catastrophically (the v1.0.4 trap).

**RULE: accept a strategy change ONLY if it helps (or at least holds) on BOTH models.**
Neither model alone is the real boss; together they bracket it. This replaces the old
"don't tune past 78% vs silver_boss" heuristic with something you can actually act on.

════════════════════════════════════════════════════════════════════════
## 6. FILE MAP
════════════════════════════════════════════════════════════════════════
- `rust/src/main.rs` — **the live single-file CG bot** (v1.0.5-safe). Compile: `rustc --edition 2021 -O src/main.rs`.
- `rust/src/strategies/mybot.rs` — sim mirror of the bot (KEEP IN SYNC with main.rs's decide).
- `rust/src/strategies/silver_boss.rs` — Boss 4 model #1 (greedy-expansion flavor).
- `rust/src/strategies/script_boss.rs` — **Boss 4 model #2: the REAL script** (§5a). Judge every change on BOTH.
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
1. DONE 2026-07-02: v1.0.6-tempo real-validated (5W/3L) and SUBMITTED. Next: confirm the
   converged rank (LEADERBOARD or the API in the log). Throttle tip: if `.monaco-editor`
   times out repeatedly, `pkill -f "cgauto/profile"` (stale Playwright chromium instances
   holding the profile were the actual blocker once; after killing them the IDE loaded).
2. **The road to Gold (score ~17 → >24) is an ARCHITECTURE rebuild, not knobs** — every
   knob/role sweep is at a plateau (see log 2026-07-02 ~12:00 table). The evidence-backed
   direction: per-troll action scheduling (joint assignment/1-2-ply lookahead over the
   validated engine within the 50ms budget), targeting the two measured structural
   deficits: (a) micro throughput (real printer bots get 3x our chop/print rate with the
   same concepts — decode more of their replays via the HTTP pipeline in the log), and
   (b) the 2.5-troll training stall from fruit composition. Water-orchard was tried
   (shipped, +2-3pp); pair-chopping is IMPOSSIBLE (1 troll per team per cell).
3. **The both-models rule (§5a) replaces "don't tune past 78%"** — any change must hold
   on silver_boss AND scriptboss.
4. **The real fight is the FIELD, not the boss** (see §1 THE BAR): to reach the boss's
   rating you must out-perform ~everyone in Silver. Study losses vs top-Silver players
   (LAST BATTLES / review.py), not only vs Boss 4. Their bots differ from both boss
   models — consider adding a third sparring model from observed top-player behavior.

GIT: on branch `session-2026-07-01`. HEAD = v1.0.6-tempo + scriptboss (see git log).
Older versions recoverable via `git log`; submissions/ has the frozen artifacts.

════════════════════════════════════════════════════════════════════════
## 8. CEILING ANALYSIS (2026-07-02) — why 100% ("all maps") is unreachable
════════════════════════════════════════════════════════════════════════
Measured facts (all reproducible with the parallel `bench`):
1. **Maps are point-symmetric: NO map bias, NO seat bias.** Self-play (identical strategy
   vs itself, 500 seeds x2 seats): silverboss 47.9%/47.9%/4% draws, mybot 46.3/46.2/8%,
   gatherer 44.9/44.9/10% — margin ≈ 0. So no map is unfair by design.
2. **BUT symmetric ≠ drawable.** Identical/mirror play draws only ~4–10%; ~90%+ of games
   are decisive. The engine breaks symmetry during play (absolute-coordinate targeting,
   ordering, shared-resource resolution; the REAL referee also breaks movement ties with
   RNG). ⇒ a guaranteed-draw strategy does not exist; guaranteed-win on every map is
   impossible. Even copying the boss exactly loses ~48% of games to it.
3. **Loss decomposition vs silver_boss** (400 seeds, `bench mybot silverboss 400 --losses`):
   ~15% of seeds = ONE-seat losses (coin-flip variance); ~15% = BOTH-seat systematic
   losses (often blowouts −40..−89).
4. **The systematic losses = the denial↔economy Pareto tradeoff.** On those maps we get
   out-ramped (mybot ~2.6 trolls vs boss ~3.4) because DW=3 choppers trek to deny instead
   of gathering. DW=3 is the measured overall peak; softening it loses more maps than it
   converts. They have NO separable coarse map feature (`mapstat`: loss maps shackdist
   12.4 vs 14.1 overall; trees/water/iron identical) ⇒ map-feature adaptivity can't work.

**DEAD-ENDS — all tested; do NOT retry** (each documented in code comments + git):
- `MYBOT_ADAPT` (chopper count by shack distance): no gain.
- `MB_MINE_ALL` (mine iron for any next troll): no-op — we are NOT iron-gated.
- `MB_ADAPT_ECON` (in-game switch to economy when behind on trolls): WORSE 77%→65% —
  "fewer trolls than boss" is our NORMAL winning state; the trigger kills the denial edge.
- Higher troll cap (MAX 5/6/7), gatherers-first (`MB_CHOP_MIN_N`≥2): worse or flat.
- Cheap-chopper `(1,2,0,2)` + woodfarm: 90.5% SIM but 33% REAL (overfit, §4/§5).
New tool: `rust/src/bin/mapstat.rs` (per-seed map features: shackdist/trees/water/iron).

**Conclusion (REVISED 2026-07-02):** the 100%-unreachable part stands (RNG tie-breaks,
no-draw engine). But the "~66% real is THE ceiling" claim rested on silver_boss-specific
loss structure: vs the real-script `scriptboss` the systematic (both-seat, fixable-in-
principle) pool is 30%, double the silver_boss picture, and the real boss is NOT the
fast-ramping opponent the Pareto argument assumed (it sits on 2 trolls until ~t150).
Realistic reading: meaningful headroom may exist beyond 66% real, but not via the simple
knobs (all swept, see log §2026-07-02); it would take a structurally better bot (see §7.2).
