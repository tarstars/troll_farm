# Experiment log — beat boss4 (local sim, planner vs boss4, 300 seeds x2 seats = 600 games)
Calibration: local planner-vs-boss4 ~ real CG (real 70-77% per handoff).
Game shape: SCORCHED-EARTH. Trees ~9 -> 3 (t100) -> ~1 (t150) -> 0 (t200). Decided by ~t150.
Our edge = fruit (27.8 vs 19.2). boss4 edge = tiny wood (9.1 vs 8.5).

| # | change | winrate | margin | keep? |
|---|--------|---------|--------|-------|
| base | v0.8.3 as-committed | 68.7% | +7.2 | baseline |
| B1 | banker: nearest reachable free drop cell | 73.7% | +9.2 | KEEP (in best/) |
| E1 | chopper HARVESTs fruit before felling | 57.7% | +0.2 | REVERT (denial speed >> +1 fruit) |
| B1sweep | DENIAL_W: 0=76.2 1=74.0 2=72.8 3=71.2 (@200s) | monotone: lower W = more wins, lower margin | W=1 balance |
| B2 | FRUIT_DENIAL @W1: 0=74.0 1=75.0 2=75.5 4=76.5 (@200s) | chop fruited enemy trees = deny fruit | KEEP, tune |

## LOCKED: v0.8.5 = B1(banker fix) + W=1 FB=6 (denial+fruit-denial tuning)
Confirmed @300 seeds (600 games): 76.8% win, +9.9 margin. Baseline v0.8.3 was 68.7%.
Both main.rs and planner.rs updated; main.rs compiles standalone (rustc --edition 2021).
Chose W1/FB6 over W0/FB4 (78.7%): W0 has half the margin, 2x draws, drops denial-weight
(model under-values denial since real boss4 replants). W1/FB6 = robust decisive wins.

## PIVOT (real data): SILVER, Boss4 = level2/Boss.cs 2-troll FARMER. We lost 89-222 as chopper.
Sim was mis-calibrated (sparse -> favored chopping). Real Silver is dense -> farming wins.
Ported real boss -> strategies/boss_real.rs (bossreal). Sim not perfectly predictive but
DIRECTION clear: pure harvester out-farms the 2-troll boss.
| v0.9.0 | NO_CHOP pure harvester (no chop/mine/chopper-train) | vs bossreal HIGH-dens 96%, 189 fruit, 3.3 trolls | TESTING on CG |

## REAL DATA (turn-8 @TFSUM): Boss4 trains VERSATILE POWER-TROLLS (1,2,3,3) hp3+chop3+cc2, scores ~250.
We trained weak (1,1,1,0) + HOARDED apple8/iron9 -> scored 86. Both v0.8.5(chop) & v0.9.0(harvest) lost ~86 vs ~250.
| v0.9.1 | versatile power-trolls: train strongest affordable of [(2,3,3,3),(1,2,3,3),(1,2,2,2),(1,2,2,1)]; harvest fruited/chop else/mine iron/invest | CG TEST | ? |
NOTE: v0.9.1 = NEW clean decide() in main.rs ONLY (decide_old kept). planner.rs NOT synced (still v0.9.0 harvester). Sim unreliable for Silver anyway.
| v0.9.1 | versatile harvest-primary | CG: me=111 vs boss 202 (was 86); improved! but harvest-primary => only wood1 | direction right |
## FINAL @TFSUM t=300: boss wins on WOOD 184/283 via (2,4,2,2) cc4 chopper. We only 2 trolls, wood1.
| v0.9.2 | CHOP-primary: big choppers [(2,4,2,2),(2,4,0,3),..], target nearest tree, chop (grab fruit bonus), mine iron, invest | CG TESTING | ? |

## FINAL LADDER (real CG, single noisy games; boss varies ~110-283 by map):
v0.9.3 mixed=74 | v0.9.4 mixed+resource-fix=61 (5 trolls, weak) | v0.9.5 save-for-chopper=105 vs 109 (CLOSE; hoarded, 1 iron short)
v0.9.6 iron 1-short again (2 trolls, hoard) | v0.9.7 chopper-now-CHOPS: me=115 vs 202, LED at t150 (52-35), wood 0->18.
BEST = v0.9.7 (115, produces wood+fruit, 4 trolls, competitive early). Still LOSES ~115 vs ~202.
Remaining gap: boss builds (2,4,2,2) cc4/ms2 chopper by ~t100; ours is cc3/ms1 built later -> out-wooded late.
Next: push chopper to cc4 (needs lemon16 saved) built earlier; maybe 2 choppers; don't scorch (keep >=harvesters).
NOT submitted to arena (v0.9.7 still loses to boss; would risk rank 49). Committed HEAD = v0.8.3 arena bot (safe).

## DENIAL thread (user's idea) — NEGATIVE on real CG:
v0.9.8 deny+plant = 0/6 (planting drained our training plum -> stuck at 2 trolls, hoard apple56).
  BUT debug showed denial DID delay boss chopper (stayed 1.1.1.2 until ~t100, boss 162 not 244).
v0.9.9 time-limited deny (turns<=55, no plant) = 0/6. Chopper's early trek costs us wood; boss recovers.
CONCLUSION: denial mechanism is real (delays boss) but net-negative -- reverted to v0.9.7 (best, wins some maps).
Now relying on parallel agents (faithful sim + search bot).

## Post-handoff experiments (2026-07-02, "defeat all maps" investigation)
| test | result | verdict |
|------|--------|---------|
| self-play silverboss/mybot/gatherer (500s x2) | 47.9/47.9/4%dr, 46.3/46.2/8%dr, 44.9/44.9/10%dr | maps symmetric, NO seat/map bias; but mirror play does NOT draw -> guaranteed draw/win impossible |
| loss decomposition (400 seeds) | 59 both-seat (systematic, blowouts -40..-89) + 58 one-seat (coinflip) | ~15% systematic + ~15% variance |
| mapstat features of both-seat losses | shackdist 12.4 vs 14.1 all; trees/water/iron identical | NO separable map feature -> map-adaptivity can't target them |
| MB_MINE_ALL (mine iron for any next troll) | 77.5% vs 77.2% base, trolls still 2.6 | no-op; NOT iron-gated |
| MB_ADAPT_ECON (behind on trolls -> chop local dw=0) | 65.4% (was 77%), both-seat 58->90 | WORSE; "fewer trolls" is our normal winning state; DW=3 denial is load-bearing |
| systematic-loss root cause | out-ramped 2.6 vs 3.4 trolls due to denial trek | denial<->economy Pareto frontier; DW=3 is the peak |

CONCLUSION: 100% ("all maps") unreachable (RNG tie-breaks + no-draw engine + Pareto peak).
Ceiling ~66% real / rank ~42. Next real progress = submit v1.0.5-safe, ladder climbing.

## Session 2026-07-02 (review by newer model): scriptboss + v1.0.6-tempo
REVIEW FINDING: the uncommitted cgauto/last_console.txt held a FULL real-game DEBUG dump
(v0.9.8 era) revealing the REAL Boss 4 script, which silver_boss does NOT match:
train (1,1,1,2) at t~2; starter plants a base LEMON orchard + mines iron, harvest LOCALLY
(starter max dist from shack = 5 over 300 turns! util troll avg 4.7); hoard to lemon 18;
t~150 train ONE (2,4,2,2); it CHOPs literally every turn after (raiding our half);
wood stays 0 until t~190; NO 4th troll ever (23 lemon banked unspent at t=300).
=> the old ceiling analysis (out-ramped 2.6 vs 3.4 trolls / Pareto peak) describes the
MODEL, not the real boss. Built strategies/script_boss.rs to capture the real shape.

Anchor calibration (real% / vs silverboss / vs scriptboss):
| mybot v1.0.5 | ~66 | 77.6 | 60.6 |     | v1.0.4-config | ~33 | 90.5 (!) | 56.9 |
| planner | 35 | ~35 | 22.6 |          | gatherer | 31 | ~31 | 20.4 |
scriptboss gets the ORDERING right where silverboss inverted it (v1.0.4). Decision rule
going forward: accept a change only if it helps (or holds) on BOTH boss models.

| test (1000 seeds x2 unless noted) | scriptboss | silverboss | verdict |
|---|---|---|---|
| ENDGAME BANKING (return+DROP partial carries by t=300) | +0.3pp, margin +0.8 | +0.0pp, +0.3 | KEEP (pure correctness) |
| chopper (2,2,0,2) hp1->0 (saves n+1 apple) | +1.1pp, +3.5 | +0.9pp, +2.8 | KEEP |
| ripeness anticipation (pre-position at soonest-ripe tree) | +0.6pp, +0.8 | -0.1pp, +0.1 | KEEP (validated mechanics only) |
| MB_FELLT fell-time-weighted chopper targets (600s) | 62.4->58.4->53.6 (ft 0/1/2) | flat | DEAD-END (tanky trees ARE the denial) |
| MB_DEFICIT chase training-blocking fruit type | loose: -3.6pp; starved-only: -1.2pp | -1.6pp; +0.4pp | DEAD-END (cure < disease; root cause real: seed 1 = plum-corner map, stuck 2 trolls @ 78 banked fruit) |
| MB_LEMONW lemon-biased denial (600s) | -1.2pp @ lw2 | flat | DEAD-END (DW=3 already covers base lemons) |
| DW re-sweep vs scriptboss | 0:27.6 1:49.6 2:59.9 3:61.2 4:60.6 5:60.2 | (3 was peak) | DW=3 RE-CONFIRMED on both |
| NCHOP 1/2/3, cc3/cc4 specs | all within noise / clearly worse | same | keep NCHOP=2, cc2 |
| water-adjacent ORCHARD placement (plum cd 8->3 near water; route carrier to spot) | +2.0pp, margin +17.9->+21.8 | +3.0pp, +26.8->+33.6 | KEEP — biggest single win |
| MYBOT_MAX 4/5/6 + DW 2/3/4 re-sweep after the economy buff (600s) | flat | flat | defaults stay (MAX=4, DW=3) |
| pair-chopping idea | — | — | IMPOSSIBLE: referee allows 1 troll per team per cell |
Field sanity (300s): mybot vs planner 87.5 / gatherer 92.3 / balanced 93.7 / chopper 97.8.
Cumulative v1.0.5 -> v1.0.6-tempo FINAL (2000 seeds): scriptboss ~59.8->61.2% (margin
+13.7->+21.3), silverboss 77.6->80.8% (+24.0->+33.1).

### Field-strength phase (2026-07-02 late morning) — v1.0.7/v1.0.8
Arena intel pipeline (NEW, pure HTTP, no browser): findLastBattlesByAgentId(agentId)
-> gameIds; gameResult/findByGameId(gid) -> per-frame stdout (RAW COMMANDS of both
players incl. TRAIN specs!), summaries, final inventories. Decoded v1.0.6's arena run:
50% vs rating neighborhood, avg score us 152 / opp 154; losses are ECONOMY blowouts
(opp 204-275). The 275-pt winner (aRi): 3 trolls, **67 wood = 268 pts** via a BANANA
WOOD-PRINTER: PICK banana from inventory + replant near base (28 PICK/28 PLANT/195
CHOP, only 35 HARVESTs all game). Banana: cd 6 (fastest), health 2+s (3 chops @chop2),
cc2 extracts min(size,2) => fell at size 2, zero waste, ~8 pts/cycle forever.

| change | scriptboss | silverboss | verdict |
|---|---|---|---|
| v1.0.7 = woodfarm ALONE on | 62.1 (+24.8) | 84.1 (+43.9) | KEEP (v1.0.4's flop was the coupled cheap chopper) |
| v1.0.8 = + banana PICK+replant printer | 60.8 (+22.5) @2000s | 84.0 (+49.8) | KEEP: +11 avg score (156->167, wood 90) = field currency |
| v1.0.8 CORRECTED baseline (MB_TIE desync healed: benches ran tie=2, shipped main.rs = tie=0) | **63.0 (+25.8)** | **85.1 (+51.4)** | true numbers; best on both models |

### v1.0.9-mower: THE SECOND SIM-REALITY INVERSION (critical lesson, 2026-07-02 ~13:00)
chop1 harvesters ("mowers", +n+1 iron each) that fell the base farm = the best numbers
ever on BOTH models (scriptboss 64.3 +31.6, silverboss 87.5 +54.1, wood 105)... and
**2W/6L = 25% on REAL CG** (bbox-good batch). v1.0.9 NOT submitted; defaults reverted.
PATTERN across both inversions (v1.0.4 cheap chopper 90.5/33, v1.0.9 mower 64+87/25):
**TRAINING-SPEC / economy changes are the repeat offender** — they interact with map
economy calibration (starting inventory, iron availability/distribution) where the sim
diverges from reality. The both-models rule catches boss-BEHAVIOR overfit only.
REFINED RULE: behavior changes (targeting, banking, planting) may ship after both-model
checks; ANY troll-spec/training change requires a REAL batch before merging to defaults.
Real record this session: v1.0.6 5W/3L (62%) submitted; v1.0.8 5W/3L (62%) submitted
~13:05 (replacing v1.0.6); v1.0.9 2W/6L quarantined behind MB_HARV_CHOP=0.

### SCHEDULER (v1.1.0-sched) — the architecture rebuild, same day (~13:30-14:30)
sched_bot.rs: global greedy (troll,task) assignment by marginal rate (BANK/FELL/
HARVEST/MINE/PRINT/ORCHARD/PICK). Key discovery: expressing mybot's fell metric
(d + 3*manh(tree,opp)) as a rate CAPPED BELOW a full bank (FB=0.8) creates a
"CAMPER": full choppers keep felling at zero yield deep in enemy land (permanent
denial) and only bank en route/endgame.
| config | script | silver | h2h vs mybot | density |
|---|---|---|---|---|
| mybot v1.0.8 (reference) | 63.9 | 85.1 | — | 167 |
| schedbot rate-based v1 | 57.7 | 71.0 | 41 | — |
| schedbot CAMPER (v1.1.0 defaults) | **83.8** | 79.4 | **56.8** | 144 |
| schedbot CYCLER (SB_FELL_FREE=1) | 67.3 | 81.5 | 49.1 | 160 |
Camper field sanity: printerbot 86.1, planner 90.8, gatherer 91.2, balanced 87.3.
+20pp on the real-script model (the promotion-gating matchup) and beats the
incumbent head-to-head; silverboss (synthetic) disagrees by -6. ALL behavior-level
changes (specs untouched) — but the v1.0.9 lesson says REAL batch before submit:
loop running (>=5W of 8 to replace v1.0.8; incumbent holds ties).

### v1.1.x ARENA BREAKTHROUGH (~15:00-17:30)
v1.1.0-sched: real batch 5W/3L (62%) -> submitted (auto-loop). Battle decode found a
PICK<->DROP LIVELOCK (no-plant-spot maps: cc1 starter picked+banked a banana for 130
turns; arena loss 21-148). v1.1.1 = livelock fix (all 3 implementations) + LATE_FREE=80
time-phased extraction gate: schedbot script 83.7 (margin +75.7!), silver 79.7 (+42.1).
Submitted ~16:45. Arena decode: 18W/12L (60%), avg 151 vs 128 (+23 margin, no more
catastrophes). **CONVERGED: RANK 18/681, SCORE 19.38** (day path: 134 -> ~50-70 -> 18).
Top-5 Silver: 23.4/21.9/20.7/20.7/20.4 — the promotion bar is ~4 points away.
THE WORKING RECIPE: decode own arena losses via HTTP -> find the leak -> fix ->
both-model bench -> real batch (specs only) -> submit -> converge -> repeat.

### v1.1.2 — RANK 3/681 (~18:10). Promotion gap ~1.5-2 pts. NEXT LEAK IDENTIFIED
v1.1.2 (anticipate-contention fix + single-banana-ferry gate) submitted ~17:20:
converged **rank 2-3/681, score 21.8-22.6** (peak rank 2 @22.64). Top: alexcercos
23.1, logiqub 22.5, tass 22.1; Boss 4 above #1. At this band we run ~50% vs the
elite with THREE 1-2-point losses (238-236, 252-250, 137-136 — endgame micro) and
blowouts only vs logiqub-tier engines (250-310 scores).
**NEXT FIX (identified, not yet done): third jam form in BOSS games** — lost a real
arena boss game 119-176 with 67 PICKs/65 fails/2 trolls: under the boss cc4's farm
raids, base_trees stays < cap and the pick/plant churn re-triggers; training starves.
Candidate fixes: pick-loop cooldown after a PLANT gets felled; suppress printer while
an enemy chopper is within base radius; or train-priority guard (never PICK when
training is fruit-blocked). Then: validate + submit -> likely crosses the boss.
Elite-tier structural study (logiqub/Glandouille 300-430-pt engines) = after Gold.

### GOAL: Gold rank <=100 (rating >=19.37). The TRAVEL thesis + throttle-gated grind.
Progress ladder (WIN-RATE = rank; only ARENA-MOTIVATED fixes transfer, sim gains don't):
v1.4.0 rank 392 -> v1.4.1 anti-starvation (chopper never idles) 187 -> v1.4.2 starter
anti-idle (same 187 in arena despite +5pp sim: TRANSFER WALL) -> v1.4.3 roam-cap 10
(TRAVEL is the confirmed arena cost) BROKE 187 -> rank ~174 -> v1.4.4 nearest-plant
(cut printer travel; validated non-negative) QUEUED behind heavy throttle.
KNOBS EXHAUSTED (verified: FARM_R/LIQ_T/FARM_MAX/spec all within noise vs the pool at
200 games). Residual travel is INHERENT (fell<->bank cycle, 60% of troll-turns, 0% idle).
Wood gap to the top: us ~42, GoodDevel (rank 98) ~70 — the rank-100 tier is ~50-55.
AUTONOMOUS CONTINUATION set up: (a) detached nohup submit loop lands v1.4.4 (agentId-
verified); (b) durable cron 7003406d (every 2h, 7-day expiry) resumes the full pipeline:
check rank -> land v1.4.4 -> decode losses -> next STRUCTURAL cut -> validate non-negative
-> minify+size-gate -> ship. Rank 100 is a throttle-gated grind (~10-20 ranks/cut, ~40min
convergence each), NOT a single action. Method + artifacts fully committed & resumable.

### GOAL RE-DEFINED: Gold rank <=200 (rating >=15.46). WIN-RATE, not score.
tass v1.4.0 plateaued at rank 392/rating 11.59. gold_elite verified at its greedy
ceiling: NO knob beats the mirror (farm/liq/spec/max/starter all 40-49%). But for a
WIN-RATE goal the lever is converting LOSSES, not raising margins. v1.4.1-nostarve:
the chopper fells the nearest reachable tree (size>=1) anywhere instead of idling when
its local farm empties (arena shutdown signature: 5 plants / wood 22 / 115-pt losses).
Measured win-rate gain vs FIXED opponents (self-play masked it — env hit both sides):
schedbot 52.7->63.3, scriptboss 70->78.7, silverboss 91->98, mybot 74.7->77.7,
printerbot 98->98.7. First change this session with a consistent measured win-rate lift.
The #1 bot GoodDevel (rating 25.9) decoded: chopper t13-14, 144-166 chops, 30-44 banana
plants, wood 69-71 — our clone matches on good maps, collapsed on hard ones (the fix).

### EFFICIENCY AUDIT (2026-07-04, user-prompted) — the search wasn't starved, we starved it
Platform: **50ms/turn**, 1000ms turn 1 (referee-verified). We hardcoded a 28ms budget —
44% of allowed compute WASTED. Profiled the fast engine (src/bin/profsim.rs):
- BARE ENGINE: 71,000 rollouts/sec = **3,202 full 40-turn rollouts per 45ms turn** (14us
  each); FastState copy ~0ns (1278B, register-cheap); NavTable::build 0.12ms once/game.
- But RHEA achieved only ~30 rollouts/turn -> the ~100x loss is ENTIRELY the full-
  scheduler policy_act running inside every rollout step (per troll/turn: 2 plant scans,
  a 242-cell bitmap, base census). The engine is competitive; the ROLLOUT POLICY is the
  hotspot. My earlier "search is a dead end" was WRONG in cause: fixable, not fundamental.
- Competitive CG practice (refs): top bots maximize sims/turn (10k-1M) via LIGHT
  (random/tiny-heuristic) rollouts + full budget + zero hot-path allocation; quality-vs-
  count tradeoff — we went 100% quality (30 sims), the sweet spot is a light policy.
REVIVAL PATH (post-200, toward Legend): budget 28->45ms + a cheap rollout policy (bare
engine + minimal heuristic ~20us/rollout) -> ~2000 real search rollouts/turn. v1.4.0
gold_elite (greedy, no search) is live at arena avg 194 meanwhile.

### THE ANSWER (2026-07-04): ship gold_elite — the winning meta, not our hybrid
gold_elite (built as a benchmark) turns out to be our STRONGEST bot AND the right thing
to ship. Clean sim (positive margin everywhere): vs schedbot 54.2% (+7.5), vs rhea 54.4%
(+15.8 @28ms), vs mybot 72%, vs printerbot 99%. Production ceiling 275 (ours: 205) —
decisive, because you cannot average 200 with a 205 ceiling that contests down to 170;
you need gold_elite's ceiling. It plays the real Gold-winning meta (2-troll pure
production, perma-chop local banana crops, 0.54 wood/chop vs our 0.16), so it should
TRANSFER better than our denial-hybrid, which the production-heavy field punishes.
Failed en route (measured vs the new gold_elite discriminator): SB_CHOP_FIRST hoard-for-
chopper (win 26%, wood unchanged — the deficit is production EFFICIENCY, not just the
missing chopper); cheap-opponent RHEA rollouts (47% h2h — opponent-model overfit).
Both RHEA search paths dead: accurate rollouts too slow (30 evals/turn), cheap ones
overfit. => decide_elite is the live bot (v1.4.0); RHEA/scheduler kept as dead code.

### CRITICAL PIVOT (2026-07-04): the RHEA search is throughput-starved
Instrumented eval-count/turn: RHEA does **5 rollouts/turn at 8ms, 18-36 at CG's real
28ms**, and `improved_over_policy` is MOSTLY FALSE — the search almost never beats the
plan its baseline policy already produces. Cause: porting the full evolved scheduler
into the rollout baseline made each policy_act ~5x costlier, so a 40-turn 2-player
rollout costs ~1ms. RHEA's 58% h2h edge over bare schedbot comes from the anti-stall
watchdog + asset-eval, NOT lookahead. CONSEQUENCE: the live bot's behavior == the
evolved scheduler; the arena plateau at ~170 is the SCHEDULER's ceiling, and the
deficit is WOOD PRODUCTION in the baseline (real-data: we lose wood 74 vs 165 in
losses), not search quality. To ever make the search matter would need ~10x cheaper
rollouts (H=20 + a cheap opponent heuristic instead of the full scheduler) -> ~300
evals/turn; parked as a lever, LOWER priority than fixing the baseline's wood.
Building a STRONG gold_elite sparring bot (printerbot only banks 129, useless) so the
sim finally discriminates and the wood fix can be measured -> arena.

### v1.3.5-fullpolicy (2026-07-04 afternoon): the baseline-policy leap
Subagent ported the FULL evolved scheduler into RHEA's rollout baseline as a per-troll
rate market (orchard/printer/pick/fell/harvest/mow/bank, evolved constants baked):
- pure policy (RH_MS=1): 8.3% -> 51.7% vs evolved schedbot — the floor RHEA degrades
  to on slow CG servers is now our best scheduler itself;
- with search (RH_MS=8): 55% vs schedbot, 74.2% vs mybot (was 35), density 224.5
  with wood x4 = 112.5.
main.rs synced verbatim (v1.3.5, 88.8k raw -> 71.5k minified, size-gated, timing
verified 28ms/turn on a 30-turn synthetic). Queued behind the afternoon throttle.

### RHEA arena iterations (2026-07-04)
v1.3.3-unstall (RHEA + anti-stall watchdog) reached the arena: first 25 games avg 146 —
PLANT MANIA (68 plants/30 chops/54-pt game): the uncapped 1.5*size tree-asset eval term
made burying fruit read as profit. v1.3.4-nogarden (term capped at 12, mutation band
halved): avg 172 @62% over 40 placement games, 200+ in 40%. No crashes in 55+ games —
the fast-engine port is protocol-solid.
DIAGNOSIS of the remaining sim->arena gap (226 sim vs ~172): on CG's slower servers the
search degrades toward its BASELINE policy, which is market-LITE (no printer/orchard/
deficit weights). Fix in flight: port the full evolved scheduler as the rollout baseline.
PROCESS: submit.py + loop got a HARD SIZE GATE (user caught a stale 138k artifact
burning 8+ 'throttle' failures that were really CG size rejections).
Falsified again: mid-game high-carry hauler (2,3,1,2) — h2h 55->29% (lemon drain).

### GOLD ERA / goal: 200 avg in-game score (2026-07-03 morning)
Baseline arena (v1.1.9 in Gold): 44% wins, avg 162. v1.2.0-market submitted 09:37:
**71% wins, avg 172 (+10 real)** — deficit-weighted harvesting (NEED_W=1: roster
2.28->2.72 trolls, +7 density), market mower (starter fells own farm, seed-gated),
liquidation (fell-by-yield late). v1.2.1-yield: yield-mode from t20 (LIQ_T=280,
denial only in the opening — the Gold field is printer-elites; scriptboss knob kept).
v1.2.2-farmcap: WF_MAX 10 (Gold top-2 decode: GoodDevel/PonyPonyCodeCode run TWO
trolls, zero denial, 21-46 plants + 140-163 chops; PonyPony banked 328 with 2 trolls).
Chop1 harvester ladder re-tested in scheduler: REJECTED again (168 density, iron tax).
Sim density plateau ~192+-4 vs printerbot (was 172). Sim->arena offset ~ -15:
arena-200 needs sim ~215 => next class = multi-turn planner (sequencing waste is
the remaining overhead: ~40-50% troll-turns are MOVEs).

### ★★★ GOLD LEAGUE — PROMOTED (2026-07-03 03:40) ★★★
v1.1.9-morning (= v1.1.5-nolock behavior + the mine-wedge fix, nothing speculative)
submitted 02:47 into the quiet overnight pool. Placement peaked **24.69**, held above
the boss bar, and CodinGame promoted: **divisionIndex=4, GOLD, entry ~355/531 @12.3
(fresh Gold rating scale)**. The winning composition rejected both unconditional
boss-countermeasures (t230 cutoff, clear-when-ahead) — general strength + pure bug
fixes is what crossed the bar, exactly the pattern of the whole climb.
FULL ARC (36h): rank 134 Silver -> Gold. Architecture: task-market scheduler with
denial camping + water-species wood printer. Method: decode arena replays over HTTP ->
fix the leak -> two-model bench -> agentId-verified submit -> converge -> repeat.
Falsified en route (each within one arena cycle): raid gate, lemon-choke, spec-change
mower, plant-cutoff/clearing (suspect). The boss (starter + 2 local utils + ONE
(2,4,2,2)) fell to the accumulated correctness + economy work, not to any
boss-specific trick.

### Boss model v3 postmortem (~03:00) + composition CORRECTION
CORRECTION: the boss's "double (2,4,2,2)" is ONE cc4 + a same-turn failed repeat
(shack occupied). Real composition: starter + TWO local utils (specs vary) + ONE
(2,4,2,2). Trajectory decode (122-279 game): utils avg dist 2.9-3.4 from its shack;
the cc4 avg 5.1 — it works ITS OWN HALF (big-first), not deep raids. CHOP actions
produce NO summary lines (why fells were invisible in earlier decodes).
v3-as-built stays far too weak (schedbot 95%, v3 wood=0.0: its cc4 NEVER trains
in-sim — our campers raze its baby lemon orchard instantly, while vs our SAME
arena agents the real spike lands ~60% of games). The unmodeled piece is the real
boss's lemon-economy resilience (orchard micro/replant cadence/map supply). Parked:
tuning vs a model that can't reach its kill condition would only re-teach denial.

### Night wrap (~02:20): four agents at the bar's edge; morning window queued
v1.1.7 lemon-choke ARENA-FALSIFIED within one cycle (boss 3W3L unchanged; a spike
still landed t93; far-lemon chasing cost our own economy — mode #3 again). Reverted:
v1.1.8-safe (= v1.1.6 behavior) submitted 01:48, converged 22.77 rank 2.
Night convergence chronology (hardened field): 23.96 / 23.43 / 21.92 / 22.77 —
all just under the boss bar (~24+). Morning cron (08:23) resubmits v1.1.8 into the
~3-5 pt softer morning field; expected ~24.5+ = the promotion window.
Boss intel bank (for the next engineering cycle if needed): double-(2,4,2,2) =
39 lemon = the kill condition; 12/12 wins when absent; simple lemon-bias failed —
candidate next levers: general early-denial strength, or boss model v3 done right
(needs the utils' real harvest behavior decoded from more games).

### v1.1.7-lemonchoke (~01:30): THE BOSS'S KILL SWITCH, from 30 decoded boss games
Mined every boss game from tonight's agents (30 games). THE PATTERN:
- boss never trains its DOUBLE (2,4,2,2): we won 12/12 (boss scores 15-114);
- double lands <=t105: we lose nearly all (boss 201-310);
- double lands >=t120: we win ~60%.
The pair costs ~39 LEMON (n=3,4: 19+20) — its timing IS the boss's lemon economy.
=> LEMON-FIRST early denial: enemy-half LEMON trees count 12 cells closer in the
fell metric while turn<120. scriptboss 86.9->91.6% (+4.7pp; its cc4 needs lemon 18 —
the real double needs 39, expect stronger live), silverboss flat.
Boss opening pairs VARY per game ((2,2,2,1),(1,2,1,2),(2,1,3,2)x2 etc) — random-ish
utility specs; only the double-(2,4,2,2) spike is invariant. bossv3 model attempt too
weak (95% -- doesn't reproduce the real save speed); parked, the lemon-choke conclusion
came straight from the real data instead.
Carriers overnight: agentId-verified submit loop (v117_submit.log) + 08:23 cron.

### v1.1.6-clear (midnight): mine wedge + late-plant cutoff + clear-when-ahead
From the decoded 122-279 boss loss + USER's IDE debug findings: (1) MINE now needs
free capacity (full cc1 starter no-op-mined 30 turns — Mine rate outbid Bank);
(2) plant window ends t230 (late plants feed the boss cc4); (3) clear-when-ahead:
lead>=40 & turns_rem<=60 -> fell OUR half (deny cc4 food; empty map ends the game
while ahead). Models 87.3/87.8 margins up. Arena: converged 23.43, rank 2-3, SILVER.
**PROMOTION BLOCKER QUANTIFIED: the real top-band Boss 4 opens with TWO trolls at
t1-2 (specs vary: (2,2,2,1)+(2,2,1,1) / (1,2,1,2)x2 / (2,1,3,2)x2) and fields TWO
(2,4,2,2) at t80-142; our boss head-to-head is only ~40-60% (2W3L sample). Neither
sparring model captures this. NEXT CYCLE: build boss model v3 (greedy 2-troll open +
double cc4 ~t100), tune vs the TRIO, revalidate.** Boss bar > 23.96 (v1.1.5 peaked
there unpromoted); both night agents finished 23.4-24.0.

### v1.1.5-nolock: RANK 1/681 (23:00-23:30) — the livelock family eradicated
User-supplied replay (v1.1.0 vs LostInCode) showed the full damage: starter did 119
PICK BANANA + 129 DROP with 2 PLANTs. Two closing fixes on top of v1.1.2's gates:
(1) PICK cooldown 12 turns when a recent pick got banked back (plant failed);
(2) idle parking prefers dry cells (never squat the plantable spot).
Sim: BOTH models 87.5% (script margin +85.0!) — the churn cost sim games too.
Arena: **RANK 1/681, score 23.96** > alexcercos 23.2 > logiqub 22.5. Placement done
(114/115). STILL SILVER => Boss 4's fixed rating > 23.96. Roster re-sweep on the
scheduler (NCHOP 2-3 x MAX 4-5): flat 86-88 both models — sim saturated; remaining
gains live in arena details. Post-placement drift at rank 1 trends UP (each field win
nudges toward the boss bar); v1.1.4-crops = species-aware water crops also landed
earlier tonight (apple/plum near water, reserve-guarded).

### v1.1.3 ARENA REGRESSION + revert (evening): the raid gate over-triggers vs the field
v1.1.3 (printer pauses while enemy chop>=2 within base_r+2) converged at **rank 51 /
17.23** vs v1.1.2's rank 2-3 / ~22 — a 5-point regression with ONE change. Models said
flat-to-up (script 85.5, silver 80.2, h2h 58.3): the gate fires rarely vs the boss
models' choppers but CONSTANTLY vs field bots whose choppers roam our half; the
printer sat silenced. **Transfer-failure mode #3: field-behavior triggers that both
boss models under-represent.** (Modes: 1 silverboss-only overfit, 2 spec/economy
changes, 3 opponent-conditional triggers.) Any opponent-state-conditional behavior
needs an arena test, same rule as spec changes. REVERTED: v1.1.2 resubmitted.
Precise-raid response idea for a future cycle: trigger only on an actual base-tree
fell event (tree count near base decreased while enemy chopper adjacent), not mere
proximity. Also note: my submit loop's triple-fire bug earlier (~18:43-18:59) came
from trusting submit.py's exit code under pipefail — verify submissions via the
leaderboard agentId instead.

### Evening treadmill (22:00-23:00): same code, different field
Anchor-ladder theory tested and REJECTED: identical v1.1.2 resubmissions converged at
17.8 then ~16.4-17.0 (120-battle placements) regardless of starting anchor, vs 22.6 in
the afternoon. Conclusion: the FIELD hardened during peak evening submission hours —
the arena is a treadmill; afternoon's rank 2-3 was real but the median opponent
improved under us within ~4 hours. Same-code resubmissions gain nothing; only bot
improvements move true standing. Next engineering targets stand: razor 1-2-pt endgame
losses; logiqub/Glandouille-tier engines (250-430 pts, replays decodable); precise
raid-response (fell-event-triggered, not proximity).

### v1.0.8 live arena decode (~14:20, first 34 placement battles)
12W/22L over the PLACEMENT mix (includes top-Silver: Psyho 266, ISeeSharper x5 up to
271, Bojii13 253 — placement sweeps high; converged rank ~50-70 already reflects it).
**Score density transferred: real avg 152 (v1.0.6) -> 164 (v1.0.8), matching sim's +11.**
aRi rematch: -93 (182-275) -> -7 (122-129). The elite prints 200-270; our remaining
40-90-pt gap = the per-troll scheduling rebuild (HANDOFF §7.2). Starter-as-mower
variant tested and rejected (46.7/65.6 — the starter IS the early economy).
| MB_FARMW chopper farm-affinity 8/16/32 | 59.8/57.6/50.2 | 83/81.6/75.8 | DEAD-END (denial is load-bearing; farm gets felled opportunistically) |
| MB_MIXORCH plum+lemon+apple orchard | flat, trolls 2.44 | flat | DEAD-END (chicken-and-egg: never CARRY the starved type) |
| MB_TIE=2 scarcity tie-break | -2.7pp | -1.2pp | DEAD-END loose; MB_TIE=0 (exact ties only) neutral -> kept |
| MB_BIG late (2,4,2,2) hoard 80/120/160 | flat | flat-worse | parked (n>=3 gate rarely met at our 2.7-troll economy) |
| WF_MAX 8/10, WF_START 10 | worse (10: 56.3!) | worse | defaults 6/20 confirmed |
| MIRROR tests (seat-knob A/B): DW3 vs DW0, MAX4 vs 5/6, FARM vs none | all ~50/50, margin ~0 | | contested equilibria self-cancel; use score-density vs fixed opponents as the field metric |
Post-v1.0.6-submission arena: rank 134 -> **58-59/682 converged, score ~16.9** (bar for
Gold ≈ >24, Boss 4 sits above Silver's #1). diag: we average only 2.47-2.7 trolls
(training blocked by fruit COMPOSITION, structural).

### Architecture A/B round (2026-07-02 ~12:00) — where the remaining gap is NOT
| test | result | conclusion |
|---|---|---|
| printerbot (decoded field archetype) vs mybot | mybot 85.9% | our strategy beats the archetype in-sim |
| anti-field configs (DW0 / DW0+FARMW) vs printerbot | 76-78% (worse than DW3's 85.9!) | denial is the best config vs EVERY archetype in-sim; adaptive-config idea dead |
| MB_TENDER (aRi chop1+hp2 base-farm tender) | flat both bosses | gates on n>=3; economy stalls below it |
| MB_BIG late cc4 hoard (80/120/160) | flat | same n>=3 trap |
| hybrid chopper (2,2,2,2)/(2,1,2,2) | -6pp both | hybrids pay only in base-camping architectures |
| ORCHARD 2/3/4 (water-placed) | flat | plateau |
CONCLUSION: every knob and role-addition is at a plateau. Real printer bots beat us on
MICRO THROUGHPUT (aRi: 195 chops, 67 wood — 3x our print rate with the same concepts),
not strategy choice. Next real lift = per-troll action scheduling (joint assignment/
lookahead over the validated engine, using the 50ms budget), i.e. an architecture
rebuild — NOT more heuristic knobs. The 2.5-troll training stall (fruit composition)
is the other structural constraint no knob fixed.

### REAL-CG validation + submission of v1.0.6 (2026-07-02 ~10:20)
- v1.0.6-tempo real batch: **5W/3L = 62%** vs Boss 4, bbox [101,43,752,470] (known-good),
  lastgame.png spot-checked at 300/300 showing tass 221 — Boss 4 116 (a historically high
  score for us). No overfit collapse (v1.0.4 test was 33% here). Statistically level with
  v1.0.1's 4W/2L=66%; both local models say v1.0.6 is stronger.
- **SUBMITTED v1.0.6-tempo to the arena** (submit.png: editor shows 1.0.6-tempo, battles
  IN PROGRESS). Live bot had slid to rank 134/682 (was 42/681 a day earlier) — the field
  improves fast; holding rank requires continuous iteration.
- **LADDER REALITY (public leaderboard API + submit-page ranking):** tass score 15.05;
  top-of-Silver ~20-24; **Boss 4 ranks ABOVE the #1 Silver player** — promotion = be
  effectively the best in Silver. Beating Boss 4 ~60-66% head-to-head is necessary-ish
  but NOT sufficient; the rating gap (15 -> >24) is vs the whole field. API:
  POST /services/Leaderboards/getFilteredPuzzleLeaderboard
  ["spring-challenge-2026-troll-farm", null, "global", {...}] (public, no auth).
Loss decomposition vs scriptboss (400 seeds): 30% both-seat + 18% one-seat (vs 15/15 on
silverboss) — the systematic pool is BIGGER vs the real script, so the "~66% ceiling"
claim was model-specific; headroom exists but the obvious knobs are exhausted.

### RHEA baseline upgrade (2026-07-04): rollout policy market-lite -> full evolved schedbot
`policy_act` (rhea_bot.rs) now ports the ENTIRE evolved schedbot cascade as a per-troll
rate market with the searched constants baked (FB 0.654, PRINT 8.36, ORCH_V 10, NEED_W
1.0, RETW 0.592, LIQ_T 189, WF_MAX 13, MOW_R 4, CROP_RES 8, LATE_FREE 82): FB denial
fells -> liquidation yield flip, LATE_FREE capacity gate, deficit-weighted harvest
(next-troll (1,1,1,0) cost), mower, plum orchard, wood printer (pick+plant, species
follows the spot), bootstrap chop-role. Bank-when-full is a market rate (not a hard
rule) so seed-carrying printers outrank banking — the old hard rule would pick/drop
livelock a cc1 troll; PICK anti-livelock = spot-exists + no-other-ferry + empty carry
(replaces schedbot's 12-turn cross-turn cooldown, which rollouts can't keep).
| bench | before | after |
|---|---|---|
| RH_MS=1 rhea vs schedbot 60 (pure policy) | 8.3%, margin -68.6 | **51.7%, +15.0** |
| RH_MS=8 diag rhea vs printerbot 60 (rhea line) | 211.3 / 95% | **224.5 / 97%** (trolls 3.06->3.27, wood*4 70.8->112.5) |
| RH_MS=8 rhea vs schedbot 80 | 13.8%, -55.7 | **55.0%, +13.2** |
| RH_MS=8 rhea vs mybot 60 | 35.0%, -15.5 | **74.2%, +28.7** |
NOTE: the earlier "printer-lite in the cascade = -80 density" finding was about
HARD-priority planting; market-priced printing (schedbot's fix) transfers cleanly into
the rollout baseline. Search on top of the strong baseline still adds (51.7 -> 55.0 as
budget grows 1 -> 8 ms).

---

## 2026-07-04 — v1.4.5-seedreserve: fixed the #1 arena loss (deforestation stall)

Decoded v1.4.4's arena games (rank 204, rating 15.51 — a regression vs v1.4.3's
~159-174). Signal: we WIN on average wood (47 vs opp 41) yet lose 45%, and 13/44 games
score <150. Decoding those 13: **12 were STALLED** — `endW == maxW`, wood frozen
partway through, both trolls parked at a shack-adjacent cell for the rest of the game
(replay 895134585: our trolls stuck at (8,0)/(9,1) while opp kept working).

**Root cause:** trees only fruit at MAX_SIZE=4, but the chopper felled farm bananas at
`GE_FELL_SIZE=2` -> they never fruited -> banana-seed supply only drained -> when
banked seeds hit 0 with no reachable native banana, the printer died, the farm emptied,
and both trolls fell through to `park_cmd` forever. (Felling at size 2 doesn't even
help wood rate: wood == size.)

**Fix:** keep the K=2 most-mature farm bananas as a protected seed reserve the chopper
won't fell (`GE_SEED_RESERVE=2`, new `seed_cells` set + `fell_ok` closure in both
gold_elite.rs and main.rs decide_elite). They ripen, fruit, and the starter harvests
the fruit as seeds to replant -> self-sustaining farm.

**Sim-calibration insight:** the DEFAULT sim (`TREE_LO=2 TREE_HI=3`) is ~2x too
tree-rich; the farm never deforests (0 starved turns) so it CANNOT reproduce the stall.
The real arena maps are SPARSE — `TREE_LO=1 TREE_HI=1` reproduces arena wood (~47) and
the idle. New tool `src/bin/stall.rs` reports winrate/wood/idle/starved/plants@end.

| map density | metric | baseline (reserve=0) | v1.4.5 (reserve=2) |
|---|---|---|---|
| SPARSE (arena-like) vs scriptboss | wood | 45.0 | **82.0** |
| SPARSE vs scriptboss | idle turns/game | 7.2 | **2.7** |
| SPARSE vs scriptboss | plants@end | 1.1 | **7.3** |
| RICH vs scriptboss | winrate | 80% | **88%** |
| RICH vs schedbot | winrate | 68% | **75%** |
| RICH vs silverboss | winrate | 100% | 100% |

Uniformly non-negative vs all three pool bots on rich maps; large wins on sparse.
Submitted via api_submit (40950032). At submit: rating 18.32, position 122/531.

---

## 2026-07-04 — 3-troll redesign attempt (kurigen build): REFUTED; wood is supply-limited

Motivated by a user-supplied game log where opponent **kurigen** ran THREE trolls
(starter + `2,2,2,2` hybrid chopper @t16 + `2,3,0,2` chopper @t86) and banked **121
wood**, crushing our old v1.2.2 (64). Hypothesised a 2nd chopper would add throughput
+ deny the opponent's trees. Built an env/config-gated 3-troll variant
(`GoldElite::hybrid()`, roster `goldelite3`): staggered 2nd chopper (train @t60),
`GE_CHOPPERS`/`GE_STAGGER`/`GE_SPEC2` knobs.

**Every configuration is decisively WORSE:**
| test | 2-troll v1.4.5 | 3-troll variant |
|---|---|---|
| sparse vs scriptboss (wood) | 83 | 22 |
| dense vs schedbot (winrate) | 78% | 47% |
| dense vs schedbot (wood, full-len games) | 76 | 49 |
| **H2H vs v1.4.5 itself, dense (winrate)** | **92%** | **8%** |
| **H2H vs v1.4.5 itself, sparse (winrate)** | **98%** | **2%** |

Traced `goldelite3` — it is NOT buggy (trains 3 trolls, both choppers CHOP), but the
two choppers repeatedly converge on the same cell competing for a depleted supply, and
in the H2H the opponent v1.4.5 banks its full ~354 wood UNsuppressed (denial fails —
its seed-reserve defends its farm). Also refuted single-chopper spec swaps: `2,2,2,2`,
`2,2,1,2`, `2,3,0,3` all ≤ current `2,2,0,2`. Carry-capacity `2,3+..` refuted earlier
(training cost = n+cc²).

**ROOT CAUSE / ceiling insight: WOOD IS SUPPLY-LIMITED, not chopper-limited.** Total
wood is bounded by the tree supply (native trees + the sustainable banana-farm
replant rate, which is gated by the single fixed `(1,1,1,1)` printer and ~15-25-turn
banana maturation). One chopper consumes that sustainable supply; a 2nd chopper only
races through it faster then starves, while its training cost (n+ms²+cc²+chop² fruit)
sets us back. The 2-troll (1 printer + 1 chopper) design is the economic OPTIMUM for
this game's tree mechanics — which is why the meta converged there. v1.4.5's
seed-reserve already maximises the sustainable supply. kurigen's 121 came from a weak
opponent (denial worked vs v1.2.2) + a dense map, NOT a repeatable edge vs a strong bot.

**Conclusion:** hold v1.4.5 (live @ rank ~104, rating ~18.5, up from v1.4.4's 204).
Config infra kept (default = v1.4.5, submission `main.rs` untouched) for any future
faithful hybrid-economy work. Reaching Legend (Boss 5) appears to need a deeper,
higher-risk economy redesign the current evidence does not support.

### follow-up: the FAITHFUL self-planting hybrid also fails (refutation complete)

My first refutation used PURE 2nd choppers — not kurigen's build. kurigen's 2nd unit is
`2,2,2,2` (harvest-capable), so it can PLANT bananas, raising the farm's supply rate
(the suspected real bottleneck). Built it faithfully: routed hp>0 choppers through the
flexible printer/chopper branch (`is_chopper = chop>=2 && hp==0`), spec2=`2,2,2,2`, so
the hybrid plants when the farm is low and chops when it's full.

Result: **still 2% (dense) / 1% (sparse) H2H vs v1.4.5**, banks LESS total wood (237 vs
366 dense, 146 vs 299 sparse). So even the faithful mechanism fails. Conclusion is now
airtight: a 3rd troll's marginal wood < its ~20-resource / ~40-turn training cost,
because total wood is bounded by tree supply (native depletion + farm cap × ~15-25-turn
maturation), NOT by planting rate — a 2nd planter fills the cap faster but can't raise
the maturation-limited fell rate, and 2 choppers just deforest faster then starve.
kurigen's 121 wood was denial vs a weak (v1.2.2) opponent on a dense map, not a
repeatable economic edge. **v1.4.5 (2-troll seed-reserve) is the confirmed optimum.**

### 2026-07-05 — search/RHEA path CLOSED by data: losses are economic blowouts

Before investing in a search-bot rewrite, decoded v1.4.5's arena loss MARGINS (agent
6538316, 50 games, 22W/28L): only **1/28 losses within 25 pts**, **18/28 are >50 pts
behind**, **median loss −78 pts (≈20 wood)**. Flipping every close game → winrate
44%→46% (negligible). CONCLUSION: losses are decisive PRODUCTION blowouts, not tactical
→ a search/RHEA bot (which only improves tactical micro over the near-optimal heuristic)
CANNOT reach Legend. The constraint is 100% economic, and the economy is already proven
optimal (2-troll) with the 3-troll alternative refuted. Boss 5/Legend is beyond reach
without a genuinely superior economy that this session could not construct (the opponents
banking 87+ wood do so via more supply — denial vs weaker fields — which our 2 trolls
can't replicate). v1.4.5 @ rank ~118 (top-of-Gold) is the rigorous endpoint.

### 2026-07-05 — cc x fell_size combo also refuted (throughput > wood-per-tree)

Re-examined the "economy optimal" claim: our cc=2 chopper captures ≤2 wood/tree (engine
DROPS overflow when felling a size>cc tree). Hypothesised cc=3 + fell-at-size≥3 = 3
captured wood/tree. Tested the COMBO (untested before — had only tried cc and fell_size
separately): DECISIVELY WORSE (wood 74.8 vs 81.5 sparse; 86 vs 90 dense; cc=4/fs=4
catastrophic 13-21 wood). Reason: THROUGHPUT dominates — felling fast at size 2 extracts
more total wood than felling slowly at size 3-4 (waiting for growth + higher n+cc²
training cost kills the fell rate). `cc=2 / fell-size-2` is throughput-optimal. Ceiling
re-confirmed. Levers now refuted with data: knobs (all), 3-troll (both variants),
search/RHEA (losses are -78 blowouts not tactical), cc×fell_size combo. v1.4.5 stands.

### 2026-07-05 — MAJOR: the real Legend meta is ACCUMULATE-HARVEST (180 wood), not steady-state

Decoded my worst arena blowout (game 895146562, lost 386 vs Tchoubidouwa123 **729**).
Opponent banked **180 WOOD** (vs my 93). Wood trajectory `[0,0,24,128,176,180]` at
(0,25,50,75,95,100)% — banks ~0 for the first HALF, then EXPLODES +104 in the 3rd
quarter. Trained 3 extra trolls (turns ~3/73/119 → a 4-troll economy). This is a
two-phase **accumulate-then-harvest**: build a big farm + several trolls early (bank ~0),
let a huge mature forest stand, then MASS-HARVEST it late. This OVERTURNS the earlier
"~90-wood ceiling / v1.4.5 optimal" conclusion — that was optimal only for STEADY-STATE
felling; the real ceiling is ~180.

Built a first `accumulate()` variant (roster `goldelite_acc`; GE_HOLD_UNTIL = choppers
PLANT not fell before turn N; big farm_cap; multi-troll). Results vs v1.4.5 h2h:
- config A (hold=140, cap=30, cc=4 harvester): **0%**, banks 207 (< v1.4.5's 391).
- config B (hold=100, cap=20, cheap cc=2 choppers): **11% dense / 1% sparse**, banks 302.
Improving but still loses. Diagnosis — TWO hard mechanisms my prototype lacks:
  1. **Full-capture felling**: cc=2 grabs only 2 wood from a size-4 tree (engine DROPS the
     overflow), so accumulating size-4 trees is wasted unless you CO-FELL (2 choppers/tree
     = 4 captured) or train cc=4 (expensive). Must add co-fell coordination (currently
     `reserved` forbids 2 choppers on one cell).
  2. **Seed-economy buildup**: filling a 20-30-tree farm needs exponential early seed growth
     (harvest fruit→plant→more fruit); the single printer can't fill it fast.
NEXT: implement co-felling of big trees in the harvest phase + a dedicated early
seed-multiplication phase. This is the genuine path to Legend/Boss 5; v1.4.5 (steady-state)
stays live as the safe floor. Default gold_elite/main.rs UNCHANGED (hold_until=0).

### 2026-07-05 — accumulate param sweep: implementation is 4.5x short (hard-hold is wrong)

Swept GE_ACC_* (hold 90-180, cap 24-40, choppers 3-4) vs scriptboss. EVERY config banks
only ~40 wood (best: hold=90/cap=24 → 40 wood, 42%) vs v1.4.5's 90 and the Legend bot's
180. Can't even fund the 4th troll (banking 0 during the hold starves funding). So the
HARD-HOLD implementation is fundamentally wrong, not mistuned. The real Legend economy is
NOT "bank 0 then harvest" — the decoded opponent banked 24 by t150 (not 0) and trained
trolls EARLY (t3/t73/t119), i.e. it FRUIT-FUNDS aggressively early + PARTIAL-fells to pay
for trolls while the farm compounds, then explodes. That's a subtle fruit-funded compound-
buildup, well beyond a hard hold. My 8+ redesign prototypes across 4 strategies (3-troll,
hybrid, search, accumulate) all bank LESS wood than v1.4.5 — I cannot replicate the Legend
economy this session. HONEST LIMIT: v1.4.5 (steady-state, ~90 wood, rank ~118) is the best
bot I can build; Legend/Boss 5 needs the compound seed-economy cracked, which is a focused
multi-hour effort (ideally collaborative). Not shipping any prototype (all worse). v1.4.5 holds.

### 2026-07-05 — cheap-PLANTER supply build: right mechanism, best redesign yet, but plateaus < v1.4.5

Found the mechanism I'd been missing: every prior redesign added expensive CHOPPERS
(~17 res) which starved funding; the supply bottleneck needs CHEAP (1,1,1,1) PLANTER
trolls (~8-12 res, hp>0 so they harvest+plant). Added `planters` field + train-planters-
first logic (roster `goldelite_acc`, GE_ACC_PLANT). This moved the redesign from 0-11% to
**best 38% h2h vs v1.4.5** (PLANT=1 CHOP=1, ~79-85 wood) — the closest any redesign got.
BUT it plateaus BELOW v1.4.5:
- DENSE: best ~85.6 wood (CAP=12) vs v1.4.5's 90; 27-38% h2h. Bigger farm HURTS (planters
  spread thin, chopper travels more): CAP 12→85w, 16→75, 20→59, 24→47.
- SPARSE (arena-like!): **1% h2h** — 3-4 trolls badly overcrowd/starve a sparse map.
Since the ARENA maps are sparse (~47 wood matches TREE_LO=1), the supply build would TANK
the arena rank. NOT arena-viable. CONCLUSION: v1.4.5 (2-troll) is the efficient frontier
for the testable map distribution; the extra troll's training cost + throughput caps keep
every multi-troll build ≤ v1.4.5 net, and multi-troll is catastrophic on sparse maps. The
Legend bot's 180 wood likely needs specific dense/watery maps + micro-routing I can't
replicate generally. v1.4.5 stays live @ rank 118. Cheap-planter mechanism validated + left
in gold_elite.rs (GE_PLANTERS, default 0) for future dense-map or map-adaptive work.

### 2026-07-05 — map-adaptive bot: apparent edge was NOISE (44-45% over 240 games)

Built a map-adaptive variant (roster `goldelite_ad`): detect tree density at turn 1, run
the cheap-planter+hold SUPPLY economy on dense maps (which showed 53% h2h at 40 seeds) and
the lean 2-troll v1.4.5 build on sparse. At 40 seeds it looked like a breakthrough (52%
dense / 54% sparse — first bot all session to seemingly beat v1.4.5). But at 120 seeds
(240 games) it's **44% dense / 45% sparse — it LOSES**. The 52-54% was small-sample noise.
Worse, sparse h2h at 45% (should mirror v1.4.5 at 50%) shows the density threshold
MISCLASSIFIES some maps -> wrong economy -> avoidable losses. RIGOROUS FINAL RESULT: nothing
built this session beats v1.4.5 at a proper sample size. The cheap-planter mechanism is real
(validated the supply concept) but even its best assembly loses. v1.4.5 (2-troll) is the
statistically-confirmed optimum for the testable map distribution. All experiment variants
left additive in gold_elite.rs (default new()=v1.4.5, submission main.rs untouched).
LESSON: validate apparent edges at >=200 games before believing them.

## 2026-07-06 ~11:30 — T1 (roadmap): decide_sched 4-troll scale economy vs REAL Boss 5 = CLOSED, FAILED
Executed roadmap T1: dispatched main() to decide_sched (1 super-chopper 2.3.0.3 + up to 3
harvesters, MB_MAX_TROLLS=4, MB_DENIAL_W=0 — the post-"disaster-fix" config), DEBUG build,
12 real Boss-5 games via collect_debug_games.py. **RESULT: 1/12 wins, our avg final wood 13
(range 2-22) vs boss 45 — uniform wood collapse in every game**; the lone "win" was 10-22 on
wood (won on hoarded fruit). The remembered 3/10-with-out-producing-wins form did NOT
reproduce; the config as it stands in main.rs banks fruit, not wood, and is ~3x below
decide_elite's 39-49 wood. Dispatch reverted to decide_elite same hour (cargo build+tests
green). VERDICT: the 4-troll scale-economy hope is CLOSED as a dead end in its current shape;
do not re-run without a fundamentally different wood pipeline. Next per roadmap: T2.a
late-feeder (GE_FEEDER_T 45→150, GE_MAX_TROLLS 2→3) after the v1.21.0 arena verdict lands.
Also this morning: v1.21.0-motion (goal-directed sidestep + proactive re-route) verified
block rate 4.1%→1.73% on 4 real games, submitted 10:35; convergence reads 18.0 (11:05),
17.7 (11:13), 18.1 (11:27) vs v1.20.0 baseline 18.4 — verdict pending.

## 2026-07-06 ~12:00 — v1.21.0 verdict; T2.a inconclusive; ★ SEED-LOOP root cause found (T2.0)
- **v1.21.0-motion arena verdict: converged 119 @ 18.1** (reads 18.1 @11:27/11:30/11:48) =
  baseline −0.3 → REVERTED to v1.20.0 per roadmap §3.G (resubmitted 11:52, api_submit default
  restored to v1.20.0). The motion code (blocks 4.1%→1.73%) stays in the tree — arena-neutral,
  not harmful; future versions carry it.
- **T2.a late feeder (GE_MAX_TROLLS 3, GE_FEEDER_T 150): INCONCLUSIVE-BY-CONSTRUCTION** —
  0/12, wood 42.3, but the feeder NEVER TRAINED (12/12 games 2-troll). @TFFEED instrumentation
  (3-game probe) shows why: want_feeder=false throughout — farm_now=0-1 (<5 gate) AND
  inv plum/lemon ≈ 0-4 (<6/6/6 cost; post-funding the starter only harvests banana/water-apple,
  the wallet never refills). Reverted knobs; reopen after the seed loop works + pair with a
  funding fix.
- **★ ROOT CAUSE of the late-throughput ceiling (probe + @TFD analysis): the SEED LOOP IS
  DEAD.** banana_seeds = 0 for essentially ENTIRE games (all 3 probes); farm EMPTY (0-1 trees)
  by t140; map deforests 21→9 trees. Mechanism: everyone fells bananas at size 2 (nothing ever
  fruits) AND both ANTI-STARVATION fallbacks (chopper ~L2384, starter ~L2562) bypass fell_ok —
  they EAT the 2 protected seed trees. The v1.4.5 seed-reserve fix and the anti-starvation
  floor fight each other; the reserve loses. Note: with cc2, size-2 and size-4 fells yield the
  SAME 2 wood — ripening reserves is ~free.
- **v1.23.0-seedloop shipped to the 12-game boss gate (~12:00)**: seed_cells widened to
  our-half bananas within chop_r when farm bananas < K; both anti-starvation fallbacks exclude
  seed_cells. Gate extras: expect banana_seeds>0 & farm>2 at t150+ in @TFFEED, t300 delta
  better than −12, wins ≥4/12 → arena as usual.

## 2026-07-06 ~12:10 — ★ v1.23.0-seedloop GATE PASSED → SUBMITTED; v1.23.1-fruitbank gating
- **Seedloop 18-game gate: 4/18 wins (22% vs 14% baseline), avg wood 46.9 (vs 38.7), t300
  delta −6.8 (vs −15.3, halved), late-quarter gap us +13.4 vs boss +17.8 (was +12/+23).**
  Out-produced the boss on wood in 4 games (57-52, 77-75, 57-40W, 53-52W) — never happened
  with decide_elite before. Mechanism verified: farm ALIVE (≥2 trees) at t150+ in 10/12
  (was 0-1); bank seeds stay 0 because carried bananas are planted directly (expected).
  SUBMITTED 12:04 (TestSession 40956279); arena verdict ≥13:05 vs baseline 18.4; frozen at
  submissions/v1.23.0-seedloop.{rs,min.rs}. api_submit default stays v1.20.0 until verdict.
- **New diagnosis from the seedloop games: we lose wood-won games on FRUIT** (57-52 & 77-75
  wood, both L) — post-funding the starter harvests only banana/water-apple; all other ripe
  fruit is left on the map while the boss banks everything. **v1.23.1-fruitbank**: from t150
  (GE_FRUITBANK_T) the starter harvests ANY ripe fruit — banked points + refills the
  plum/lemon/apple wallet (which also unblocks the T2.a late feeder later). Early game
  untouched (seed priority + gates unchanged before t150). 12-game gate running ~12:10.

## 2026-07-06 ~12:15 — v1.23.1-fruitbank gate: HOLD for the seedloop arena verdict
15 games (3 of the 6-game extension failed — throttle warming; ~71 API games today): **3/15
wins, avg wood 51.3, t300 delta ≈ −6.2** — equal to seedloop on wins, better on wood, and its
extra value (banked fruit points) is INVISIBLE to the wood-only gate metrics: its wins include
two fruit-decided wood-draws/losses (59-60 W, 69-70 W), the exact scenario seedloop lost.
Strictly dominates seedloop on expected score. Frozen: submissions/v1.23.1-fruitbank.{rs,min.rs}
(MIN-OK). DECISION: hold submission until v1.23.0-seedloop's arena verdict (~13:05) — one arena
variable at a time; if seedloop transfers (≥18.2), submit fruitbank on top; if seedloop craters
(<18.1), that's a boss↑/field↓ divergence — revert to v1.20.0 and re-examine the family vs
FIELD opponents (T3) before any resubmit.

## 2026-07-06 ~12:57 — ★ v1.23.0-seedloop ARENA VERDICT: CRATERED — boss↑/field↓ divergence PROVEN
Arena-room read 12:55 (51 min post-submit): **rank 205 @ 15.6** (baseline 117 @ 18.4, −2.8) —
far below any convergence trajectory seen (v1.21.0 read 18.0 at +30 min). User spotted it first.
REVERTED to v1.20.0 at 12:57 (TestSession 40956563). LESSON (now proven, not just suspected):
the 12-18-game boss gate measures ONLY Boss 5; the arena rating is earned against the FIELD
(~15-19-score players), and a change can be the best-ever vs the boss while LOSING to the field
— seedloop's seed-tree protection/ripening evidently gives field opponents standing value or
costs tempo they punish. CONSEQUENCES: (1) v1.23.1-fruitbank submission CANCELLED (contains
seedloop); (2) the whole seedloop family goes to FIELD analysis first (T3): collect games vs
rank-100-140 players, find HOW they beat seedloop; (3) roadmap gate procedure gains a field
check before arena submits of economy changes.

## 2026-07-06 ~13:40 — FIELD GATE built + first field data; seedloop crater mechanism
`cgauto/field_targets.py` (raw getFilteredPuzzleLeaderboard → agentIds): ★ GOAL MATH CORRECTED:
Gold ranks 95-113 hold scores 19.0-19.9 → **rank ≤99 = ~19.7 = +1.3-1.5 from baseline** (the old
+7.5 figure conflated the separate Legend/boss bar 26.2). Field games via collect_debug_games
with agentIds WORK. v1.20.0 baseline vs the band: RunninglVlan(102) 1/2 wood 49-46;
nmahoude(110) 1/2 wood 60-64 — ~EVEN with our matchmaking diet; Tchoubidouwa123(98) 0/2 wood
86-123 (4-troll ms3/cc4 scale tier — not required for rank 99). Field games are WOOD-RICH
(60-86 avg vs 39-50 vs boss): the field expands (3-4 trolls incl. (2,2,2,0)/(2,2,1,1)
harvesters + cc3 choppers) instead of denying. SEEDLOOP A/B vs same opponents (n=2/cell,
directional): vs RunninglVlan lost 37-67 (same opp got 46/27 vs baseline) — **mechanism
hypothesis: our ripening protected bananas = 3-4-wood gifts for field cc3 choppers (cc2 caps
US at 2)**; explains boss-gate↑ (boss cc2 + shallow raids) vs field-crater. Seedloop family
stays frozen. NEXT: v1.24.0 = fruitbank-only on the v1.20.0 base (no ripening, banks existing
fruit from t150; field-safe by construction) → FIELD gate first.

## 2026-07-06 13:36 — v1.24.0-fruitbank SUBMITTED (field-gated, single-variable)
Baseline reconvergence CONFIRMED first: v1.20.0 back at **118 @ 18.6** (13:35; above the old
18.4 read — arena noise band ±0.2 confirmed empirically). v1.24.0 = fruitbank ONLY (starter
harvests/banks ANY ripe fruit from t150) on the v1.21-logic base; ALL seedloop edits removed
(dead-end note left in code). Field gate: level with baseline vs RunninglVlan/nmahoude (1/2
each; 88-77 high-water win); no crater signature. Boss numbers not re-run (fruitbank's value
= fruit points, invisible to wood metrics; arena = the only sufficiently sensitive scale).
Submitted 13:35:57 (TestSession 40956721). Verdict ≥14:35 vs baseline 18.5±0.1; revert rule
armed (≤18.2 → resubmit v1.20.0). If kept: next = T2.a.2 late feeder (fruitbank refills its
6/6/6 wallet) or Phase R refactor on user go.

## 2026-07-06 14:50 — v1.24.0-fruitbank verdict: −1.0, REVERTED (124 @ 17.5 converged ×2)
Two identical reads (14:35, 14:46). Baseline was 118 @ 18.6. MECHANISM (hypothesis): from t150
the starter stops chop-helping (step 6 contributes to 4-pt wood fells) to chase 1-pt fruit —
net negative. LESSON: the 4-game field gate filters CRATERS only; ±1.0 effects are invisible
under wood noise — the arena is the only scale for knob-sized effects, and even "additive-
looking" behaviors trade against the tight 2-troll machine. DAY TALLY: 4 arena experiments
(v1.21 motion −0.3 neutral; v1.23 seedloop −2.8 crater; v1.24 fruitbank −1.0), ALL reverted;
baseline v1.20.0 intact (118 @ 18.6). The decide_elite knob well is DRY — every bolt-on
behavior loses. ⇒ The remaining road to +1.3 is COORDINATED policy change = Phase R (L2 jobs
layer). Starting R1/R2 (behavior-preserving extraction + equality harness — zero arena risk)
while v1.20.0 reconverges.

## 2026-07-06 ~16:15 — Phase R: R1 DONE + R2a DONE + bundler DONE (all gates green)
R1: `src/bin/equality.rs` black-box harness (two bot binaries over the CG protocol on sim
games; opponent = frozen reference binary or WAIT — lib strategies are nondeterministic).
Found+fixed the bot's own nondeterminism (2 HashSet-tie sites → `(score, cell)` keys);
self-play determinism proven; **reference frozen** (submissions/v1.25.0-ref-deterministic.rs,
target/refactor/reference_bin; VERSION frozen "1.25.0-layers"); **500-game baseline: EQUAL
(0 divergences)**. Goal-file amendments documented (reference = v1.20.0+2 tiebreaks; version
freeze; binary opponents; bundler allowance).
R2a: whole bot moved VERBATIM into the lib (`src/botmain.rs`, `pub fn run()`); main.rs = 6-line
shim; 18 test suites green; **100-game equality vs reference: EQUAL**.
Bundler: `tools/bundle.py` (recursive `mod x;` inliner + fn main trampoline). Gates: rustc
compiles ✓, bundled binary **50-game equality EQUAL** ✓, minified 89,101 B < 100 KB ✓.
NEXT (R3, each step harness-gated ≥50 seeds + bundle gates): R3a `mod state` (types+helpers+
consts), R3b `mod motion` (watchdog, camp-cell claims, bank/park), R3c `mod jobs` (the per-troll
cascade → Job enum + assignment fn; the delicate one — preserve priority order + reserved/claimed
side-effect order), R4 `mod tactics` (spec/farm/liquidation/seed_cells). Then final gates +
arena hold-check per docs/refactor-goal.md.

## 2026-07-06 ~16:40 — R3a DONE: `mod state` extracted, all gates green
tools/extract_state.py (anchor-based): 160 lines → src/botmain/state.rs (types Cell/Troll/
Tree/State + impls, item-index consts, TOTAL_TURNS, plant_cooldown/water_boost, manhattan/
ortho_neighbors/bfs_distances, training_cost/afford_fruit_only/mb_afford/ge_fruit_ty), with
`pub` visibility added mechanically; botmain.rs keeps `mod state; pub use state::*;` so all
references work unchanged. GATES: 18 test suites ✓, 100-game equality vs reference EQUAL ✓,
bundled single file compiles + 20-game equality EQUAL ✓, minified 89,397 B < 100 KB ✓.

## 2026-07-06 ~16:55 — R3b DONE: `mod motion` extracted, all gates green
src/botmain/motion.rs: pick_camp_cell/bank_cmd/park_cmd (closures → pub fns; thin closure
wrappers kept in decide_elite so call sites are unchanged), the ANTI-STALL WATCHDOG
(GE_LASTPOS thread_local moved in, `motion::reset()` at turn 1, `motion::watchdog(state,
&my, &mut cmd_by_id)` replaces the inline block). GATES: build ✓, 18 suites ✓, 100-game
equality EQUAL ✓, bundled compiles + 20-game equality EQUAL ✓, minified < 100 KB ✓.
NEXT: R3c `mod jobs` — the per-troll cascade → Job enum + assignment fn (delicate: preserve
priority order + reserved/claimed side-effect order); then R4 `mod tactics` (spec ladder,
farm config, seed_cells, liquidation); then final gates + arena hold-check.

## 2026-07-06 ~15:40 — R3c+R4 DONE in one restructuring; FINAL gates running
tools/extract_layers.py: decide_elite split into **tactics.rs (L1)** — `pub struct Plan` (24
fields = the explicit L1→L2 interface) + `plan(state, my)` (spec ladder, train gating, farm
config, seed reserve, all verbatim; GE_CHOSEN_SPEC moved in) — and **jobs.rs (L2)** —
`assign_all(state, plan, my) -> HashMap<id, cmd>` (fell_ok/own_half/within_roam closures +
the whole per-troll cascade verbatim; plan fields re-bound as same-named locals so ZERO
renames; GE_MEM moved in). decide_elite is now 15 lines: resets → tactics::plan →
jobs::assign_all → motion::watchdog → assemble+TRAIN. Compiled FIRST TRY; dead root
thread_locals removed.
GATES: 18 suites ✓; **100-game equality EQUAL** ✓; bundled layered file compiles + 20-game
equality EQUAL ✓; **minified 92,071 B < 100 KB ✓ (criterion 3)**. 500-game final equality
(criterion 1) running. **Criterion 4 hold-check: v1.25.0-layers SUBMITTED 15:40**
(submissions/v1.25.0-layers.{rs,min.rs}). ⚠ Baseline drift observed: v1.20.0 converged
17.8 @ 15:39 (was 18.6 @ 13:35, 18.4 morning) — the arena wanders ±0.4-0.8 across hours;
judge the hold-check vs the CONTEMPORANEOUS baseline (17.8-18.6 band), fallback = resubmit
v1.20.0 if clearly below it.

## 2026-07-06 16:45 — Phase R hold-check verdict + goal closeout
v1.25.0-layers converged **128 @ 17.3** (3 stable reads 16:05/16:33/16:43). Contemporaneous
v1.20.0 baseline: 17.8 (15:39); day's same-code v1.20.0 spread: 17.8-18.6 (the room drifts
±0.4-0.8/hours). Delta −0.5 = outside the strict ±0.2, inside the observed drift scale —
cannot separate drift from a real tiebreak cost without a multi-hour alternating A/B.
CONSERVATIVE CLOSE per the goal text: **v1.20.0 resubmitted 16:45 → the baseline ends
intact**; v1.25.0-layers stays the frozen, equality-proven PLATFORM (all four criteria
executed: 500-game EQUAL ✓, 18 suites/28 tests ✓, minified 92,071 B compiles ✓, hold-check
run with conservative outcome ✓). OPEN QUESTION for R5.0: the 2 determinizing tiebreaks pick
lexicographically-smallest cells (clustered plants?) — a seeded-rh_rand tiebreak would keep
determinism AND spread; test as the first experiment ON the new platform if the −0.5 recurs.
Phase R deliverables: src/botmain/{state,motion,tactics,jobs}.rs (L1 Plan interface → L2
assign_all → L3 watchdog; decide_elite = 15 lines), src/bin/equality.rs harness,
tools/{bundle,extract_state,extract_layers}.py, frozen v1.25.0-ref-deterministic +
v1.25.0-layers.

## 2026-07-06 17:23 — baseline restoration VERIFIED; goal closed
v1.20.0 reconverged **125 @ 17.9** (+39 min) — baseline intact, goal criteria all executed.
NB: same-hour comparison now exists: v1.20.0 17.8-17.9 (twice) vs v1.25.0-layers 17.3 —
the −0.5 gap looks more like a REAL (small) cost of the lexicographic tiebreaks than pure
drift. ⇒ **R5.0 (first experiment on the new platform): seeded-rh_rand tiebreaks** in
free_base + funding-iron picks (keeps per-process determinism, restores spatial spread);
it changes streams → freeze a new reference after it validates.

## 2026-07-06 19:26 — R5.0 seeded tie-breaks: all local gates green, arena cycle started
Implemented on the layered platform (first platform experiment): `state::tie_salt` (per-game
salt from immutable map facts — STABLE within a game so tied targets never flap) +
`state::tie_mix(cell, salt)`; jobs.rs free_base + funding-iron picks now break score-ties by
seeded rank instead of lexicographic (which clustered plants and measured ~-0.5 same-hour).
VERSION 1.25.1-spread. GATES: 18 suites ✓; self-determinism EQUAL (20 games) ✓; diverges
from old reference (change active) ✓; bundled EQUAL + minified 92,885 B compiles ✓; boss
spot-check 2/6 wood 48.5 (healthy, no flapping) ✓. NEW stream reference frozen:
submissions/v1.25.1-ref.rs + target/refactor/reference_bin_v1251. Bracket: v1.20.0 stable
125 @ 17.9 (17:23→19:26). v1.25.1-spread SUBMITTED 19:26; verdict ~20:30: keep live if
≥ 17.7 (bracket −0.2), else revert to v1.20.0.

## 2026-07-06 ~20:05 — NEW TOOL cgauto/battles.py + live-bot arena-battle analysis (40 games)
Fetches LAST BATTLES for the current submission via REST (findLastBattlesByTestSessionHandle
+ gameResult/findByGameId), joins opponents with the Gold leaderboard. v1.25.1-spread @ ~122:
**19/40 wins, avg score 236 vs 262. THE TIER SPLIT: vs peers (17.5-18.5) we win ~60-65% with
modest margins; vs the 18.7-19.6 tier we get BLOWN OUT (nep7un 19.5: -238/-287 with scores
566/658; Eagleast 19.6: -271; plcc 19.0: -138/-140/-101; mikdiet 18.7: -104/-92/-91).**
Those bots build 120-160-wood late economies; our ceiling ~60-85 wood. ⇒ the +1.5 to rank
≤99 is concretely: STOP BEING BLOWN OUT by the 19+ tier = raise the late economy ceiling =
exactly R5.1 (farm-supply invariant as an L2 job rule) + field-gate vs nep7un/plcc/mikdiet
(agentIds via field_targets.py). Matchmaking is rank-local: all 40 opponents were rank
105-128, so these ARE the gatekeepers.

## 2026-07-06 20:07 — R5.0 verdict: KEEP. The layered platform is LIVE (v1.25.1-spread, 122 @ 18.2)
Reads 18.1 @+30min, 18.2 @+41min vs same-hour bracket v1.20.0 = 17.9 → the seeded tie-break
recovered the lexicographic clustering cost. api_submit default → v1.25.1-spread.min.rs.

## 2026-07-06 ~21:20 — R6a joint move solver: gates + arena submit
`motion::solve_moves`: joint landing-cell choice for ALL movement intents (exhaustive ≤8^n,
max total progress, swaps/chains legal, stationary teammates obstacles, canonical tie-break).
TESTS (all first-run green): corridor 5-turn unload EMERGES from the objective; SHUFFLE
INVARIANCE (permuted intents + troll lists → identical plans); crossing pair swaps.
Integrated as decide_elite's motion stage (MOVEs pinned to joint landings; watchdog kept as
net). 19 suites ✓ self-determinism EQUAL ✓ bundle EQUAL ✓ min 96,815 B ✓ (headroom ~3 KB!).
@TFMOVE instrument RESTORED (was lost with the v1.20.0 tree restore — DEBUG-only).
BOSS: 0/12 + 2/4 (win noise), wood 49.1, delta −6.5 (top-tier economy, unchanged).
BLOCKS with solver: 1.83% ≈ the enemy-contention + intentional-wait floor (self-blocks ~0;
structural payoff scales with troll count → R6b). FIELD vs the blowout tier: **1/2 vs each of
nep7un/plcc/mikdiet, wood 78-77/71-79/54-46 — NO blowouts** (arena showed −100..−287 vs them).
SUBMITTED after bracket read; keep if ≥ bracket−0.2.

## 2026-07-06 21:19 — ★★ R6a VERDICT: KEEP — ALL-TIME BEST 118 @ 18.9 (+0.7 vs bracket)
v1.26.0-jointmove converged 118 @ 18.9 (reads 18.7 @+29m, 18.9 @+39m, 18.9 @+49m) vs the
same-hour bracket v1.25.1-spread = 122 @ 18.2. Best score ever recorded (prior best reading
18.6, standard 18.4). The user's activity-manager concept, stage one (joint move solving),
is the first change of the project to GAIN vs a clean bracket. api_submit default updated.
Gap to rank ≤99 (~19.7): ~0.8. NEXT: R6b — joint task assignment (valuation matrix + exact
matching replacing the sequential cascade in jobs::assign_all).

## 2026-07-06 ~22:15 — R6b task planner: built, debugged, gated, SUBMITTED
planner.rs (L2): cascade branches → value BANDS (hierarchy preserved), ETA within band,
exhaustive conflict-free matching, canonical ties. Tests: shuffle invariance, contested-tree,
priorities (3/3 green). USER-FOUND BUG fixed along the way: farm membership / chopper roam
were MANHATTAN-radius (ignores water — biz1 game showed the starter planting across a lake);
now MAP distance via shack-BFS shared in Plan (farm_d). SIZE saga: bundle hit 121 KB → deleted
the dead deciders (sched/RHEA/legacy, −1906 lines; pre/post-cut equality EQUAL 30 games) →
then a BUNDLER RESOLUTION BUG (mod planner; captured the legacy src/planner.rs — rustc
resolves botmain/planner.rs first; fixed candidate order) → true artifact **37,132 B**.
FIRST boss gate FAILED 0/8 wood 36 → diagnosis: single 70-band let farther-faster fells
outrank FINISHING the tree underfoot (cascade never abandoned invested chops) → fix:
continue-to-completion bands (72/42/31 standing > 70/40/30 travel) → **BOSS 3/8, wood 51.2,
delta −4.2 (best ever)**. FIELD vs blowout tier: 2/6, wood 69-80 (72-34 over nep7un!), no
blowouts. SUBMITTED vs bracket v1.26.0 @ 118 @ 18.9. Keep if ≥ 18.7.

## 2026-07-06 22:47 — v1.27.0 verdict: REVERTED (17.7, −1.2); v1.28.0 gate FAILED; two defects found
**v1.27.0-taskplan arena: 18.7@+20m → 17.7@+40m → 17.7 (fell through convergence) = −1.2 vs
the 18.9 bracket → REVERTED to v1.26.0-jointmove.** Boss/field gates were good — the fade is a
FIELD leak the probes under-sample.
**v1.28.0-thirdhand boss gate: FAILED 1/8 wood 46 delta −11.5**, and the new telemetry
(@TFFARM: farm/seeds/hands/flaps) explains everything:
1. **PERPETUAL-FUNDING BUG**: want_feeder=true switches cost to the feeder and my funding
   bands (60/58) outrank printer work (50/48) → the starter chases plum/lemon/apple ALL GAME
   for a feeder that never affords (lemon-starved maps), instead of planting/seeding. The
   feeder never trained (n=2 end, 8/8). Fix: feeder-funding band 45 (chopper keeps 60/58 —
   existential vs luxury).
2. **FLAPPING CONFIRMED: 16-36 mid-travel target switches/game** — the joint matcher re-plans
   globally each turn; small ETA shifts flip assignments; steps leak. Likely v1.27's arena
   fade. Fix: stickiness — small value bonus for keeping last turn's MoveTo target.
3. **Farm still dead at t150+ (0-1 trees)** — the untreated original disease (seedloop's fix
   cratered vs field and was reverted); also blocks the feeder's farm≥3 gate.
NEXT: v1.28.1 = stickiness + feeder-band demotion → boss gate; expect flaps↓, feeder trains
on lemon-ok maps, wood ≥ v1.27's 51. Arena bracket vs v1.26.0 @ 18.9.

## 2026-07-06 23:00 — v1.28.1/.2: stickiness works; 3rd hand blocked by the farm disease; v1.28.2 in arena
v1.28.1 (sticky targets STICKY=3 + feeder-funding demoted to luxury band 45/44): **flaps
16-36 → 2-12**, wood back to 50, but 3rd hand trained 0/8 — the DEAD FARM gate (farm≥3 @t60+)
blocks it; the farm disease (seeds exhausted, farm 0-1 by t150) is the standing blocker for
ALL scale plays and remains THE strategic target. v1.28.2 = planner + map-fix + stickiness
with the 3rd hand DORMANT (MAX_TROLLS=2) — the minimal test of "stickiness fixes v1.27's
arena fade" — boss 1/6 wood 50 flaps 2-21 (noisy but < 16-36), SUBMITTED 22:55. Verdict vs
v1.26.0's established 18.9 (its 22:47 reconvergence was only +8min → bracket is the 21:19
convergence; drift risk noted). Census tool insight: label-matched equality runs against the
right BASE = a decision-diff catalog; vs v1.25.1 the diffs conflate R6a landing-pinning —
census v2 must diff against a label-matched v1.26 binary.

## 2026-07-06 23:34 — ★★★ v1.28.2-steady2 VERDICT: KEEP — ALL-TIME BEST 113 @ 19.1
Converged 19.7@+19m → 19.1@+29m → 19.1@+39m vs v1.26.0's 18.9. **The full manager
(joint tasks + joint moves) with sticky targets is the new champion: rank 113, score 19.1**
(era baseline 18.4-18.6; two manager stages = +0.5-0.7 total). The v1.27 fade is EXPLAINED
and CURED: assignment flapping (16-36/game → 2-12 with STICKY=3). Gap to rank ≤99 (~19.7):
~0.6. NEXT (v1.29.0-reserve): treat the FARM DISEASE the field-safe way — the seed reserve
(2 most-mature FARM bananas, map-distance r≤2 — inside our pocket, minimal gift-surface
unlike seedloop's mid-map widening) becomes inviolable to the ANTI-STARVATION bands too
(30/31 currently bypass it, exactly how the cascade broke v1.4.5's reserve). Expected:
seeds regenerate → farm survives t150+ → late delta up → ALSO unblocks the 3rd hand.

## 2026-07-06 23:55 — v1.29.0-reserve: THE FARM LIVES — submitted
One line: the anti-starvation bands (30/31) now SPARE plan.seed_cells (farm-local reserve,
map-distance pocket — NOT seedloop's mid-map widening). Result: **farm alive at t150+ in 6/8
boss games (0/8 all era)**; wood 50 (holds); field spot-check wood **90/89 avg (era best:
69-80)** — 1/4 wins but the losses were 90-96 monsters. The seed loop is resurrected the
field-safe way. SUBMITTED vs bracket v1.28.2 @ 113 @ 19.1. If kept: the 3rd hand's farm gate
is finally passable → v1.30 = re-arm GE_MAX_TROLLS=3 (machinery already in, dormant).

## 2026-07-07 00:20 — v1.29.0 verdict: REVERTED (~17.0, −2 vs 19.1). ★ THE PIE INSIGHT
Converged low-and-falling (17.1@+20, 16.9@+30, 17.1@+40) → reverted to v1.28.2 (19.1
champion). THIRD strike for the protection family (seedloop −2.8, fruitbank −1.0, reserve
~−2) and the boss/field wood numbers were GOOD every time. The synthesis that fits all data:
**protection GROWS THE PIE (more standing trees, longer supply) and the 19+ tier out-eats us
on a bigger pie — our arena edge is the early game + short supply.** Field probes showed it:
our wood 90 but opp 96 in the same games. COROLLARY (v1.30 hypothesis): the reserve is only
worth shipping TOGETHER with the extra eater it enables — reserve + 3rd hand (farm gate now
passable: farm alive 6/8) converts the living farm into OUR wood instead of feeding the
tier's better late engines. Pie + eater, not pie alone.

## 2026-07-07 00:45 — NIGHT CLOSE: champion v1.28.2 @ 19.1; the LEMON WALL; tree restored
v1.30.0 (pie+hands): best boss delta ever (−2.8) but 3rd hand 0/8. v1.30.1 (errand band 52,
t<150): STILL 0/8. ★ ROOT CAUSE — **THE LEMON WALL**: any 3rd troll needs ≥3 lemons (cc1 =
n+1); the chopper consumes ALL starting lemons at t~3 (cc2/3 = 6-11); lemons never ripen
later because BOTH players fell everything at size 2 (same dynamic that killed bananas).
The wallet is structurally unfillable on most maps → the 3-troll line is CLOSED under the
current fell-at-2 meta unless a lemon is deliberately ripened (= protection = pie = feeds
the tier, −2 measured). v1.30.x NOT submitted (≡ v1.29 in the field). Tree restored to the
champion source (equality-verified vs the live artifact).
NIGHT LEDGER: baseline 18.4-18.6 era → **champion v1.28.2-steady2 @ 113 @ 19.1** (planner +
map-fix + sticky). Arena experiments: v1.27 −1.2 (flapping, cured), v1.29 −2 (pie insight),
v1.30.x gate-closed (lemon wall). Gap to rank ≤99 ≈ +0.6. NEXT CANDIDATES: (a) battles.py
census on the 19.1 champion — who beats it now and how; (b) valuation polish from the census
(fell-target scoring: size-3 natives vs size-2, denial weighting by opponent distance);
(c) decision-diff census vs label-matched v1.26 to find residual planner regressions;
(d) STICKY sweep (3 → 5/8) — flaps 2-21 residual; (e) endgame liquidation timing on the
planner. The lemon wall + pie findings close the scale line for now.

## 2026-07-07 00:55 — champion census (40 battles @ 19.1-19.4, rank 111-115)
**rank 100-150 band: 17/35, avg margin +4 — the tier split is nearly ERASED** (wins over
plcc 19.8, TheMagicShop 19.6, RunninglVlan 20.0, Dasein8 19.3). Remaining losses: the ≤100
tier (94-96 @ 20.0): 1/5, avg −98, one −265 blowout (jrl86 @ 602 = monster long-game
economy). MORNING AGENDA (data-driven): (1) convert the +4-margin coin-flips in the 100-115
band (STICKY sweep 3→5/8; endgame liquidation timing on the planner; valuation polish);
(2) shrink the 20.0-tier blowouts (their monster games are LONG — our anti-long-game levers:
earlier liquidation? denial weighting?); (3) the decision-diff census vs label-matched v1.26.
Champion reconvergence confirmed: 19.4@+18m / 18.9@+28m (band ≈ 19.1±0.3, rank 111-115).

## 2026-07-07 01:05 — champion replays collected + the 20.0-TIER BLUEPRINT decoded
data/arena_replays/: 7 full arena replays of the champion (both players' command streams).
**jrl86's 602-337 monster decoded: HOARD-THEN-FACTORY.** t0-150: harvest/mine only (2 chops
total!), 2→4 trolls trained from the untouched map — THE LEMON WALL DOESN'T EXIST FOR THEM
because they harvest fruit before anyone fells the fruit trees; our wall is a TIMING artifact
of chopper-first + fell-at-2. t150-300: plant-and-fell factory — 40 PLANT feeding 149 CHOP
with 4-5 trolls (they grow their own chop targets → denial cannot starve them; only
out-scoring works). Confirms the two-basin frontier: tempo optimum (us, ~19.1) vs scale
optimum (them, ~20.0); crossing = the hoard-first build order = the Legend-harvest design
(docs/superpowers/specs/2026-07-05-…) — NOW buildable on the planner machinery (daytime
project). Tonight's path stays in-basin: convert the +4-margin coin-flips vs the 100-115
band. NEXT CYCLE: v1.28.3-sticky6 (STICKY 3→6; residual flaps 2-21 = the measured defect).

## 2026-07-07 09:25 — v1.28.3-sticky6 verdict: NEUTRAL (114 @ 19.0 vs bracket 19.2)
STICKY 3→6: flaps 3-15 (marginal), arena within noise. The stickiness lever is EXHAUSTED.
Overnight stability datum: v1.28.2 held 113 @ 19.1-19.2 for ~7h. sticky6 left live (same
policy); v1.28.2 remains the frozen champion + submit default. Champion band: 19.0-19.2,
rank 111-115. Gap to ≤99: ~+0.5-0.7.

## 2026-07-07 ~12:30 — A1 (GE_LIQ_T 34→44) REJECTED at the gatekeeper; pipeline live
First candidate through the 4-stage subagent pipeline (spec/plan: docs/superpowers/
{specs,plans}/2026-07-07-*). Builder: all local gates green (reviewed: SPEC PASS/Approved).
Gatekeeper: FAIL — boss 1/8 wood 44.6 (bar 45), t300 delta −7.8 (ok), flaps ok, field 0/4
with −173 blowout vs plcc, and the liq-specific readout REGRESSED (final-34-turn banking
+6.1 vs era +8-12 — earlier liquidation did not bank more, it banked less late). No arena
cost. Track-A negative #1 of 2 before A retires. Next: B1 phase skeleton (zero-behavior),
then B2 hoard.

## 2026-07-07 14:30 — REASSESSMENT: hoard parked; T-hand is the new queue head
Scale gates #1-#4: machinery fixed to working (hands 7/8) but strategy condemned — our wood
0/0/4/23 vs opp CONSTANT ~57-60 (the ceded-map signature), field −400 avg. Matchmaking makes
the hoard unclimbable from 113. SALVAGE: the funding stack (65/64 iron > 63 deficit-fruit,
want_feeder-scoped, graceful) = the lemon wall is DEAD. → v1.35.0-thand: Tempo + funded 3rd
hand — every historical blocker (coordination, wallet, farm gate, perpetual-funding) now
individually dismantled. Gates: boss 8 + field 4, then arena vs the 19.0 bracket.

## 2026-07-07 ~20:00 — user replay-review findings queued (race-check, banana flow, diagonal farm)
Three user-observed inefficiencies from live games (see spec Amendment 2): doomed-target
chasing (race math in fell valuation), tent-PICK-before-tree-harvest inversion (8:1
plant-fell conversion argument), diagonal-to-shack plant placement (distance 2, off the
bank path). Queued as v1.36.0-race and v1.37.0-nanaflow behind the T-hand arena verdict.

## v1.35.0-thand arena verdict (2026-07-07 20:46) — REVERTED (converged 16.8, −2.2 vs bracket 19.0)
**Bracket (pre-submit):** 19:40:59 — ARENA-ROOM rank 113/527, Gold score **19.0** (agentId
6542129). **Submit:** 19:41:09, SUBMIT-OK (TestSession 40964128).

**Convergence reads (v1.35.0-thand, agentId 6542461 confirmed live from the first read):**
| time | Δt | rank | score |
|---|---|---|---|
| 20:01:39 | +20m | 123/527 | 17.4 |
| 20:16:23 | +35m | 145/527 | 16.7 |
| 20:31:27 | +50m | 143/527 | 16.8 |
| 20:45:48 | +64m (confirmatory) | 143/527 | 16.8 |

Reads 3→4 (15 min apart) moved 0.0 → converged at **16.8**. Shape: NOT climb-then-fall (no
climb phase at all) — straight fall (17.4→16.7) then flatten (16.8→16.8). Fails KEEP (needs
≥18.8 = bracket 19.0 − 0.2) by **2.2 points**, the worst arena miss of the whole T-hand/hoard
cycle (worse than v1.29.0-reserve's −2.0 and v1.30.x's gate-closure).

**Revert:** 20:46:05, submitted `v1.28.3-sticky6.min.rs`, SUBMIT-OK (TestSession 40964380).

**Reconvergence reads (agentId 6542490 confirmed live from the first read):**
| time | Δt (post-revert) | rank | score |
|---|---|---|---|
| 21:06:42 | +20m | 116/527 | 18.5 |
| 21:21:26 | +35m | 114/527 | 18.9 |
| 21:30:42 | +44m (confirmatory) | 117/527 | 18.6 |

+35m read (18.9) clears the ≥18.7 reconvergence bar; the 18.5-18.9 band matches the champion's
known ±0.2-0.3 noise around its 19.0-19.2 home band (rank 111-117). **Arena is SAFE on
v1.28.3-sticky6.** `api_submit.py` default left **unchanged** (still `v1.28.2-steady2.min.rs` —
that was already the intentional kept-at-parity default from the sticky6 NEUTRAL verdict on
2026-07-07 09:25; v1.35.0-thand did not qualify to replace it either).

**Reading vs the gatekeeper:** gatekeeper verdict #3 was the strongest of the T-hand line (6/6
hand trains, era-best boss economy: 47.0 avg wood, −9.5 t300 delta) — and it still cratered the
field by 2.2 points, the same boss-gate-clean/field-negative shape as the whole protection
family (seedloop −2.8, fruitbank −1.0, reserve −2.0 on 2026-07-06/07). The gatekeeper's own
report flagged the live half of this candidate as unverified: readout 2 (farm/seed revival) was
"inconclusive/negative" in all 6 boss games — farm stayed at 0-2 and seeds drained to 0
regardless of whether/when the hand trained. This arena result supplies the missing half: on
the field's 19-20 tier, whatever the 3rd hand does live costs more than it returns — consistent
with either "one more funded mouth with a farm that isn't reviving" or "the funding tax itself
(iron/fruit rerouted to fund hand #3) is the direct cost," per the tempo-vs-scale ("pie") thesis
from 2026-07-07 00:20 and 14:30.

**NEXT for the analyst:** run `battles.py` + pull 1-2 loss replays for agentId 6542461
specifically (window 19:41-20:46) and check the feeder troll's actual command stream once
trained — does it ever issue plant/seed actions, or does it sit idle? That distinguishes "the
3rd hand is a net-negative idle mouth" (kills the whole hand line) from "the hand plants fine
but the funding tax alone costs >2pts vs the field" (might be salvageable with a cheaper trigger
condition). Track record update: T-hand now joins the protection family as arena-negative
despite being boss-gate-clean — reinforces the tempo/scale frontier as the standing explanation
for why boss-gate wins keep failing to transfer to the field.

## v1.36.0-race arena verdict (2026-07-07 22:24) — KEEP, new CHAMPION (converged ~19.9-20.1 vs 18.6 bracket, +1.3-1.5 pts)
**Change:** doomed-target race check in fell valuation — skip trees an enemy chopper will
finish before we arrive, join winnable shared-tree contests at a small (`RACE_SHARE_PEN=2`)
discount. Pure waste-cut, no training/farm/funding change (`GE_MAX_TROLLS` reverted 3->2,
T-hand parked pending its own analyst follow-up). Champion-equality gate explicitly waived by
design (behavior only changes on contested cells); gated PASS by the builder (see
`data/candidates/v1.36.0-race/report.md`), boss/field probe games waived under the
arena-queue idle-slot policy (2026-07-07).

**Bracket (pre-submit):** 21:34:12 — ARENA-ROOM rank 117/527, Gold score **18.6** (agentId
6542490). **Submit:** 21:34:21, SUBMIT-OK (TestSession 40964539).

**Convergence reads (agentId 6542530 confirmed live from the first read):**
| time | Δt | rank | score |
|---|---|---|---|
| 21:54:29 | +20m | 116/527 | 18.6 |
| 22:09:17 | +35m | 88/527 | 20.1 |
| 22:24:24 | +50m | 103/527 | 19.9 |

Shape: flat-at-bracket (+20m), then climb (+35m), then flatten (+50m, 20.1->19.9, Δ0.2) —
steady-climb-to-flat, clears the KEEP bar (bracket−0.2 = 18.4) by roughly a full point-and-a-
half. Decided at +50 per the tight-window policy — not ambiguous (both post-climb reads sit
well clear of the bar and are within 0.2 of each other). Biggest single-candidate jump of the
whole T-hand/protection cycle, and the first clean positive verdict since sticky6.

**Decision:** KEEP. Converged score sits clearly ABOVE the bracket (not mere parity), so per
step 5 of the arena-runner brief, `cgauto/api_submit.py`'s default path was updated — it had
gone stale at `v1.28.2-steady2.min.rs` (already behind the actual champion, v1.28.3-sticky6)
and now points at `submissions/v1.36.0-race.min.rs`. v1.36.0-race is the new standing
champion; `docs/arena-queue.md` Champion/Queue/Verdict-log sections updated accordingly.

**Reading vs the brief's own prediction:** the builder's report explicitly predicted this
"isn't an economy lever, it's an execution/efficiency fix" and expected wood/economy numbers to
stay flat since no training/farm/funding changes were made — the result is consistent with that
framing while still producing the largest score jump of the whole recent cycle, suggesting
wasted travel into doomed shared-tree races was a bigger tax on field performance than the
economy-side experiments (T-hand, protection family) were able to move in the other direction.

**NEXT for the analyst:** run `battles.py 40`, confirm the win-rate/margin shift lines up with
fewer wasted-trek losses (not a variance artifact) — see the 1-2 loss replay command-mix method
in the analyst brief — and decide whether v1.37.0-nanaflow (next in queue) should now gate its
champion-equality check against v1.36.0-race instead of sticky6.

## 2026-07-07 ~22:55 — ★★★ v1.36.0-race KEPT: 19.9-20.1, rank 88-103 — biggest jump ever (+1.3-1.5)
The user's doomed-chase replay finding, as a pure waste-cut in the fell valuation, added more
than every economy experiment combined. Read sequence: bracket 18.6 → +20m 18.6 → +35m 88@20.1
→ +50m 103@19.9 → stable 103@19.9 ×3. CHAMPION = v1.36.0-race; submit default updated by the
runner. Goal (≤99 twice): oscillating at the line (88 once, 103 steady) — nanaflow mini-gate
running for the decisive push. Meta-lesson reinforced: at this band, EXECUTION waste-cuts
transfer to the arena at full size; economy rebalances don't.

## v1.37.0-nanaflow arena verdict (2026-07-08 00:41) — REVERT (converged ~16.6-16.7 vs 19.9 bracket, −3.2/−3.3 regression)
**Change:** banana TREE-FIRST harvesting (removed the `inv[BANANA]==0` gate on the ripe-seed-
tree MoveTo band, re-ranked it 52·BAND ahead of the 50·BAND tent Pick/Park) + DIAGONAL plant
placement (added `bank_adj`/`diag` geometry terms to the plant-cell tie-break key, penalizing
the four orthogonal bank/DROP cells and rewarding the four diagonal cells). Both changes live
entirely in `rust/src/botmain/planner.rs`'s `candidates()`; no fell/funding/race-band/training
constants touched. Mini-gate (boss 6, reduced probe) PASSED: avg wood 45.3, min wood 30, delta
−11.3 (better than the −15.3 historical baseline), 0/6 crashes, flaps 6/6 ≤15 — no crater
signature. Champion-equality gate explicitly waived by design (both mechanisms intentionally
change behavior). Full detail: `data/candidates/v1.37.0-nanaflow/report.md`.

**Bracket (pre-submit):** 2026-07-07 22:58:26 — ARENA-ROOM rank 103/527, Gold score **19.9**
(agentId 6542530) — matches the v1.36.0-race champion's own converged band exactly, confirming
a clean pre-submit baseline. **Submit:** 22:58:44, SUBMIT-OK (TestSession 40964870).

**Convergence reads (agentId 6542585 confirmed live from the first read):**
| time | Δt | rank | score |
|---|---|---|---|
| 23:19:06 | +20m | 199/527 | 15.6 |
| 23:34:26 | +35m | 145/527 | 16.6 |
| 23:49:44 | +50m | 142/527 | 16.7 |

Shape: drop, then climb (+20m→+35m: +1.0), then flatten (+35m→+50m: Δ0.1, converged) — a
climb-then-flatten shape at a level **3.2-3.3 points below the bracket**, well clear of the
KEEP bar (bracket−0.2 = 19.7) on the wrong side. Not ambiguous — the flattening at +50m
resolves the shape cleanly (this is not a still-climbing trajectory that might reach parity
with more time), so decided at +50 per the tight-window policy, no +65m read needed.

**Decision:** REVERT. Converged score (16.6-16.7) sits far below bracket−0.2 (19.7); this is a
clear regression, not noise. Resubmitted `cgauto/submissions/v1.36.0-race.min.rs` (the correct
revert target per the current champion — NOT sticky6) at 23:50:11, SUBMIT-OK (TestSession
40965088).

**Revert reconvergence (agentId 6542604 confirmed live from the first read):**
| time | Δt (post-revert) | rank | score |
|---|---|---|---|
| 2026-07-08 00:10:25 | +20m | 117/527 | 18.2 |
| 00:25:43 | +35m | 111/527 | 19.3 |
| 00:41:00 | +50m | 111/527 | 19.3 |

Two consecutive reads 15m17s apart (+35m, +50m) are identical (111/527, 19.3, Δ0.0) — satisfies
the "two stable" reconvergence criterion (the alternative to reaching ≥19.5 explicitly allowed
for revert verification). Slightly under the champion's historical 19.9-20.1 peak band but a
stable, confirmed-live champion; arena is NOT left on a regressed bot. `api_submit.py` default
was already `v1.36.0-race.min.rs` (unchanged by this episode — nanaflow never earned the
default-path update in step 5 of the arena-runner brief since it was reverted, not kept).

**Goal gate (rank ≤99):** did NOT fire on any read this session — nanaflow's own reads
(199/145/142) never approached it, and the champion's revert-reconvergence bottomed at
rank 111. No confirming read required.

**Reading vs the mini-gate's prediction:** the gatekeeper's report explicitly flagged the
banana-flow readout as "a plateau, not a climb" (tent stock set by t5 then flat for the rest
of the game in 5/6 boss games) and recommended this as "worth a follow-up note for the analyst,
not a defect" — the arena result suggests it undersold the risk: a pure boss-gate crater check
(wood/delta/crashes) cannot see the interaction between the new tree-first travel pattern and
the v1.36.0-race doomed-target check, nor between the diagonal plant bias and real-field bank-
cell contention under 2v2-vs-4-trolls pressure — exactly the transfer-wall failure mode this
project has hit before with boss-clean, field-negative candidates.

**NEXT for the analyst:** run `battles.py 40` against the CURRENT (reverted) champion state to
re-confirm v1.36.0-race's own field numbers are unaffected by this episode, then specifically
pull 1-2 nanaflow-window loss replays (if still queryable — check the 22:58-23:50 submission
window) and check whether the tree-first re-ranking caused choppers/starters to divert onto
farther ripe trees mid-farm-cycle (increasing exposure to contested/raided cells the race-check
would otherwise have steered around) or whether the diagonal-placement bias interacted badly
with a tighter or more irregular field-map geometry than the boss-gate's map pool exercised.
Also resolve the flagged-but-unresolved queue note: since v1.36.0-race (not sticky6) is now the
confirmed champion, any future re-attempt at the tree-first/diagonal mechanisms should gate
champion-equality against v1.36.0-race directly rather than waiving it, so a future flag-off
comparison can isolate which of the two sub-changes (A or B) is responsible before restacking
both again.

## Analyst census on the race champion (2026-07-08 night)

**HEADLINE BLOCKER: a live, per-opponent `battles.py` census of v1.36.0-race itself was NOT
obtainable this session** — the arena test slot was occupied by a different, already-converged
candidate for the entire analysis window. Read-API only was respected throughout (no submits,
no games played by this analyst).

**What was found instead, in detail:**

`cg_rank.py` at the first read (00:48) showed `agentId=6542627`, rank **521/527**, score **0.0**
— not any of the champion's confirmed-live agentIds (6542490 / 6542530 / 6542585 / 6542604),
and not remotely near its 19.3-20.1 band. `battles.py 40`'s first pull (9 finished games) showed
an opponent spread of rank **4 to 484** — nothing like the champion's ~90-130 diet. The brief's
own self-check ("verify the opponent list looks like the race champion's diet") **FAILS**
outright. Diagnosis (high confidence, inferred, not directly confirmed via source-code
inspection — no read-only API path to the live source text was found; `Puzzle/
generateSessionFromPuzzlePrettyId` was probed and confirmed read-only/safe but returns only a
session handle, not code): this is **v1.38.0-deny1** (A2, `DENY_W=1` contested-tree fell-target
bias). It was fully builder-complete (report + frozen `.min.rs`) since 22:22 the previous
evening — the only queue item ready to submit — and the agentId change lands within ~5-7
minutes of the champion's 00:41 reconvergence confirmation, exactly matching `docs/
arena-queue.md`'s "queue never idles" policy (a concurrent arena-runner submitting the next
item immediately on verdict).

Confirmed (read-only) that `gamesPlayersRanking/findLastBattlesByTestSessionHandle` only ever
returns the CURRENT live agent's battles — passing an old agentId (6542604, 6542530) as the
2nd argument instead of `None` made no difference to the result. **There is no read-API path to
recover the champion's own per-opponent battle history once a newer candidate has taken the
arena slot** — this is a structural limitation of the tool, not a one-off fluke, and will recur
for any analyst pass that lands mid-queue-rotation. Worth a tools note for future sessions.

Monitored `cg_rank.py` read-only for ~40 minutes (00:48→01:24, no arena actions taken):
0.0/rank521 → 15.7/190 → 15.1/224 → 15.7/190 → 15.5/203 → 16.6/146 → 17.0/134 → 17.0/136 →
17.0/135 — the last three reads over ~10 minutes are stable (**converged at score 17.0, rank
~134-136**). A fresh `battles.py 40` at this point (134 total battles listed, 40 analyzed)
confirms a genuine, properly-matched rating, not noise: **20/40 wins, avg score 181 vs 180**,
opponents rank 98-175 / score 16.1-17.5 (by band: rank100-150 13/31 wins avg margin −6;
rank150-250 7/9 wins avg margin +27) — a coherent ~17.0-skill matchmaking pool, not a
still-climbing transient. **This candidate's converged rating sits ~2.3-3.1 points below the
champion's own logged band (19.3-20.1) and ~2.1 points below the pre-race 00:55 baseline
(19.1) — a clear regression**, in the now-familiar boss-gate-clean/field-negative shape shared
by the protection family, T-hand, and nanaflow. This is an observation for the record, not a
verdict — reverting is the arena-runner's call, and `api_submit.py`'s default is unchanged
(`v1.36.0-race.min.rs`).

### (a)-(c) vs the 2026-07-07 00:55 census — best-available comparison

Since a fresh per-opponent pull for the champion wasn't possible, the comparison falls back to
the champion's own already-logged convergence reads (aggregate score only, both live windows):
- First promotion (07-07 21:34-22:24): bracket 18.6 → 18.6(+20m) → 20.1(+35m) → 19.9(+50m),
  rank 88-117.
- Post-nanaflow-revert reconfirmation (07-08 00:10-00:41): 18.2(+20m) → 19.3(+35m) →
  19.3(+50m), rank 111-117.

**Headline: champion band 19.3-20.1 / rank 88-117 now vs 19.1 / rank 111-115 at 00:55 ⇒
roughly +0.2 to +1.0 pts net** — real, but smaller than the "+1.3-1.5" the race-check's own
arena verdict quoted (that figure was measured against an artificially low 18.6 bracket, not
against the historical 19.1 baseline this census is supposed to check against).

(a) **Blowout-shrinkage: UNRESOLVED** for the champion (no fresh per-opponent breakdown
obtainable). Indirect-only signal: a higher converged score against a similarly-strong
opponent pool implies fewer/smaller losses in aggregate, consistent with but not proof of the
race-check's intended effect.
(b) **Which opponents still beat us: UNRESOLVED** for the champion specifically (same
blocker).
(c) **New dominant loss pattern: partial answer**, from the currently-live (presumed-deny1,
NOT champion) candidate's converged 40-game sample — see the replay decode below. Caveat
clearly: this reflects deny1, not v1.36.0-race. However deny1's ONLY delta from the champion
is a small fell-target tie-break scoped to bands 70/72 (confirmed in `data/candidates/
v1.38.0-deny1/report.md`) — opponent-side behavior (what THEY do to win) should generalize to
the champion; only OUR OWN command-mix numbers (esp. MOVE:CHOP ratio, below) are
deny1-specific and must not be attributed to the champion.

### Task 3 — loss replay decode (from the live, presumed-deny1 session; champion-specific replays unavailable)

Fetched + command-mix-decoded (75-turn phases, both players, verbs normalized case-insensitive
after discovering some opponents emit lowercase command tokens) the 3 worst losses from the
converged 40-game sample, via `gameResult/findByGameId` (same call `battles.py` uses):

| game (gameId) | opp (rank/score) | margin | opp CHOP by phase (t1-75/76-150/151-225/226-300) | my MOVE:CHOP |
|---|---|---|---|---|
| 895447389 | ArgoZ (152/16.4) | −113 | 0 / 0 / **143** / 38 | 379:54 = **7.0** |
| 895447344 | mlomb (140/16.8) | −92 | 22 / 2 / 8 / 8 (low — wins via HARVEST 171 + DROP 186 instead) | 336:83 = **4.1** |
| 895447761 | NicknamedTwice (121/17.5; game ended EARLY at turn ~219/300) | −68 | 0 / **116** / 78 / (n/a, game over) | 259:98 = 2.6 |

Sanity-checked the decode script against the already-known jrl86 monster game
(`data/arena_replays/game_895341619.json`, pre-race v1.28.2 champion) — reproduced the
documented shape (opp CHOP 0/2/60/87, PLANT-heavy back half) before trusting it on fresh data.
Also decoded 3 more pre-race replays on disk (RunninglVlan, plcc, TheMagicShop) to get a
historical MOVE:CHOP baseline for "me": **2.3-3.4, avg ~2.7**, across all 4 historical games.

**Sharpest new pattern:** in 2 of the 3 worst fresh losses (ArgoZ, mlomb), our own MOVE:CHOP
ratio (7.0, 4.1) runs **1.5-2.6x the historical baseline (~2.7)** — the chopper burns far more
travel per tree felled than usual. That is exactly the shape a wasted-travel-inducing
tie-break would produce, and it lines up mechanically with deny1's design: `DENY_W` biases the
chopper's PRIMARY fell choice (bands 70/72 — the same decision point `race()`'s doomed-target
check already governs) toward trees FARTHER from us / nearer the opponent whenever two
candidates are near-tied. If near-ties are common on some maps, this could systematically add
travel beyond what `race()` alone would allow — the two mechanisms are not obviously
composable, they compete for the same tie-breaks. The third loss (NicknamedTwice, ratio 2.6,
in-baseline) shows the effect isn't universal, consistent with `DENY_W` only firing on
near-ties (map-dependent).

Independent of the deny1 confound, two distinct opponent win shapes recur and are both
untouched by the race-check (so they're standing champion weaknesses, not artifacts of
tonight's live-slot mixup): **(i) explosive delayed chop-burst** — ArgoZ (0/0/143/38) and
NicknamedTwice (0/116/78) both jump from ~0 chops to 100+ in a single 75-turn window, a
sharper/more sudden cousin of jrl86's gradual hoard-then-factory ramp (0/2/60/87); **(ii)
fruit-harvest/bank economy** — mlomb wins with a LOW chop count (40 total) but very high
HARVEST (171) + DROP (186), a win condition not previously catalogued as distinct from the
wood/chop economy in this log. All 3 opponents out-trained us (+1 to +2 trolls over the game),
reconfirming the standing scale gap is untouched by the race-check (expected — it doesn't
touch training/funding). One of three losses ended in a notably short game (~219 of 300 turns)
— single-sample, flagged not confirmed as a pattern.

### Task 4 — re-ranked hypothesis queue (also applied to `docs/arena-queue.md`)

1. **RACE_SHARE_PEN sweep (2→4)** — NEW TOP PICK. Tunes the one mechanism with a proven, large
   positive field result; lowest risk of the remaining ideas, and doubles as an indirect probe
   of whether `RACE_SHARE_PEN` is already doing enough on contested trees that a second,
   independent contest-bias (`DENY_W`) is actively harmful (redundant tie-breaks colliding).
2. **chop_r 5→4 retest** — NEW SECOND PICK. Orthogonal travel-reduction lever in the same
   "cut waste" family as the race-check's proven win; does not touch fell-target valuation at
   all, so zero interaction risk with the race-check or the deny1 defect above.
3. **tree-first-only (nanaflow's safe half)** — unchanged priority, proceed when picked up, but
   per the nanaflow post-mortem's own recommendation, gate champion-equality UN-WAIVED against
   v1.36.0-race specifically (not sticky6) so a flag-off run can isolate it from the
   diagonal-placement half before restacking both.
4. **diagonal-contest design** — still undesigned; lowest maturity, unchanged last place.
5. **DEMOTED: any further `DENY_W` sweep/A2 follow-up** — the live evidence above (converged
   ~17.0, a 2.3-3.1pt regression vs the champion, plus the elevated MOVE:CHOP signal in the
   worst losses) argues against pursuing this family further unless the arena-runner's actual
   verdict is unexpectedly positive. If reverted as trending, file A2/deny1 next to the
   protection family / T-hand as a closed dead end (boss-gate-clean, field-negative).
6. **NEW, filed for later (not urgent tonight):** the mlomb-style fruit-harvest/bank win
   pattern (low chop count, high HARVEST+DROP volume) is not addressed by anything in the
   current queue — worth a dedicated look once a champion-specific census is unblocked.

**Process recommendation:** re-run `battles.py 40` + the loss-replay decode against
v1.36.0-race specifically once the arena slot is confirmed back on it (watch for the agentId
to revert away from 6542627, or a fresh verdict log entry) — this session could only
characterize the *arena-occupancy* problem and the *deny1* candidate, not the champion's own
current per-opponent diet.

## 2026-07-08 01:47 — A2/deny1 verdict (controller takeover): REVERTED at 135 @ 17.0 (−2.3+)
The deny1 arena-runner went silent past its decision window; the analyst's independent monitor
had already measured convergence at 17.0/135 with the collision mechanism (DENY_W vs the race
check at the same decision point; MOVE:CHOP blew up 1.5-2.6x in worst losses). Controller
reverted to v1.36.0-race at 01:47. DENY_W parked at 0 inside v1.39.0-sharepen4 (merged,
controller-reviewed: exactly 2 consts + TDD both directions). sharepen4 submits after race
reconverges (~02:30).

## v1.38.0-deny1 arena verdict (arena-runner's own record, filed 2026-07-08 ~02:40)

**REVERT — confirmed.** This section is the arena-runner-of-record's own full read sequence,
filed after the fact because a parallel "controller" process took over the revert mid-episode
(see "process collision" below). The verdict itself is unanimous across three independent
observers (this runner, the analyst's b62c977 census, and the controller) — no disagreement,
just a coordination gap in *who* pressed the button and *when*.

### Bracket + submit

- **BRACKET** 2026-07-08 00:46:06 — ARENA-ROOM rank **111/527**, Gold score **19.3**,
  agentId=6542604 (matches the champion's known reconverged band from the nanaflow-revert
  episode exactly — clean pre-submit baseline).
- **SUBMIT** 00:46:19 → 00:46:22 — `api_submit.py cgauto/submissions/v1.38.0-deny1.min.rs` →
  `TestSession/submit: 200 40965251` → **SUBMIT-OK**.

### Convergence reads (agentId 6542627 confirmed live across all three)

| time (MSK) | Δt | rank | score |
|---|---|---|---|
| 01:06:54 | +20m | 146/527 | 16.5 |
| 01:21:39 | +35m | 141/527 | 16.8 |
| 01:36:35 | +50m | 135/527 | 17.0 |

Shape: slow monotonic climb, decelerating (+0.3, then +0.2) — not a sharp flatten like
nanaflow's (+0.1 at the same interval), so per the brief's "decide at +50 unless ambiguous"
clause, this runner took one more read at +65m to remove doubt before deciding.

**+65m read (01:51:22): rank 353/527, score 12.0, agentId=6542647 — DISCARD, contaminated.**
This is a *different* agentId. Between the +50m and +65m reads, a parallel "controller" process
— per its own commit message, believing this runner had "gone silent past its decision window"
(incorrect: this runner was still inside the brief's own explicitly-allowed +65m confirmatory
window, 61 minutes after a 00:46 submit is not "silent past the window") — independently
resubmitted `v1.36.0-race.min.rs` to the arena at 01:47:07, replacing deny1 in the ONE arena
slot before this runner's own +65m read landed. The 353/12.0 reading is therefore the freshly
resubmitted *champion's* own cold-start noise (~4 minutes post-resubmit), not deny1 — it is
discarded for deny1's verdict, not treated as a fourth deny1 data point.

**Decision basis:** the uncontaminated +20/+35/+50 trajectory alone (stable agentId throughout)
is sufficient and unambiguous: converged **~17.0 vs bracket 19.3** (need ≥19.1 = bracket−0.2 to
KEEP) — a clear **−2.3pt** shortfall, decisively below the keep bar. This independently matches
**two other sources reaching the same number by different methods**: the analyst's parallel
40-minute read-only `battles.py`/loss-replay monitor (`b62c977`, filed 01:27:41, *before* this
runner's own +50m read) measured "convergence at 17.0/rank~135" — an exact match; and the
controller's own resubmit-at-01:47:07 action, taken independently of this runner's not-yet-filed
verdict, reaches the identical REVERT conclusion.

**VERDICT: REVERT.** (Already executed by the controller at 01:47:07; this runner's own data
independently confirms it was the correct call and was not a premature or mistaken takeover in
substance — only in timing/coordination.)

### Process collision (flagged for the orchestration layer, not this candidate's fault)

The controller's stated reason for taking over — "runner silent past its decision window" — was
factually wrong at the moment it acted: this runner was mid-flight on the brief's own explicitly
allowed +65m confirmatory read (60-65 minutes after a 00:46 submit is standard duration for this
brief: bracket + submit + three 15m spaced reads + optional +65m + revert-reconvergence
verification routinely totals 90-120 minutes end to end, e.g. the nanaflow episode). No
heartbeat or in-flight marker exists to distinguish "actively sleeping between scheduled reads"
from "actually stalled/dead" — worth a queue-doc process note so a future concurrent controller
waits for an explicit verdict commit (or a longer silence threshold, e.g. 90+ min with no
activity) rather than timing out an arena-runner still inside its own brief's allowed window.
No harm resulted this time (both conclusions agreed), but a future case where the runner's
in-flight read is still trending toward KEEP could get preempted incorrectly.

### Champion reconvergence verification (this runner's own check, post-collision)

Per the brief's step 4 ("REVERT otherwise → v1.36.0-race.min.rs, verify reconvergence"): the
revert-resubmit action was already taken by the controller (01:47:07), so this runner did not
resubmit a second time (that would have reset convergence yet again via a third agentId) and
instead verified the *existing* resubmission's reconvergence:

| time (MSK) | Δt post-resubmit | rank | score | agentId |
|---|---|---|---|---|
| 01:51:22 | +4m | 353/527 | 12.0 | 6542647 |
| 02:07:18 | +20m | 117/527 | 17.9 | 6542647 |
| 02:22:14 | +35m | 121/527 | 17.6 | 6542647 |
| 02:37:14 | +50m | 121/527 | 17.6 | 6542647 |

Two consecutive stable reads (+35m/+50m, 121/527 @ 17.6, Δ0.0, 15 min apart) satisfy the
brief's "two stable reads" reconvergence criterion. This level (17.6) sits below the same
champion code's most recent 19.3 mark (and below bracket−0.4 = 18.9) but is **byte-identical
code** to the standing champion (`api_submit.py` default unchanged throughout, confirmed) — this
is arena-room score drift, the same phenomenon already on record for this room (111@19.3 vs an
earlier 19.9 band for the *same* candidate), not a code regression. Direct in-project precedent
(the nanaflow-revert reconvergence, 2026-07-08 00:41, accepted "slightly under...historical peak
band, but a stable, confirmed-live champion" as sufficient) supports treating this the same way.
**Arena is NOT left on a regressed bot.**

### Goal gate (rank ≤99)

Did not fire on any read across this entire episode — deny1's own reads (146/141/135, plus the
discarded 353) and the champion's reconvergence reads (117/121/121) all stayed well above 99.
No confirming read required.

### Records / no further action needed

`cgauto/api_submit.py` default was already `v1.36.0-race.min.rs` throughout (REVERT case — no
change per brief step 5). `docs/arena-queue.md` champion/queue/verdict-log updated in the same
commit as this entry to close out the stale "deny1 pending" / "arena-slot note" text left by the
analyst's b62c977 commit (predates the controller's takeover). v1.39.0-sharepen4 (next queued
candidate, `RACE_SHARE_PEN` 2→4 + `DENY_W` parked at 0) is out of scope for this runner — left
untouched for its own arena-runner episode.

## v1.39.0-sharepen4 arena verdict (2026-07-08 03:37) — KEEP, AT PARITY (converged 17.6 == 17.6 bracket)

**Phase 0 — champion reconvergence, independently re-confirmed:** after the deny1 revert
(01:47), read `cg_rank.py` every ~9-10 min:

| time (MSK) | rank | score | agentId |
|---|---|---|---|
| 02:16:59 | 117/527 | 18.1 | 6542647 |
| 02:28:33 | 121/527 | 17.6 | 6542647 |
| 02:37:43 | 121/527 | 17.6 | 6542647 |
| 02:46:58 | 121/527 | 17.6 | 6542647 |

Three consecutive reads at 121/527 @ 17.6 spanning 02:28→02:46 (19 min, Δ0.0) satisfy the
"two reads ≥15 min apart moving <0.15" fresh-bracket criterion. This matches (does not just
corroborate — is numerically identical to) the deny1 arena-runner's own closing reconvergence
record filed minutes earlier (121/527 @ 17.6 at 02:22:14/02:37:14) — three independent read
sequences (analyst, controller-adjacent deny1 runner, this runner) now agree on the same
number. Per the brief ("late-night drift may land it lower, use what you measure"), **BRACKET
= 17.6, rank 121/527**, well below the champion's historical 19.3-20.1 band but the correct
current baseline to compare sharepen4 against.

**Phase 1 — submit:** 02:47:19 MSK, `api_submit.py cgauto/submissions/v1.39.0-sharepen4.min.rs`
→ `TestSession/submit: 200 40965544` → **SUBMIT-OK**.

**Phase 2 — convergence reads** (new agentId 6542656 confirmed live on all three, distinct
from the champion's 6542647):

| time (MSK) | Δt post-submit | rank | score | agentId |
|---|---|---|---|---|
| 03:07:11 | +20m | 123/527 | 17.4 | 6542656 |
| 03:22:16 | +35m | 121/527 | 17.6 | 6542656 |
| 03:37:26 | +50m | 121/527 | 17.6 | 6542656 |

Shape: flat from the start, converged by +35m (121/527 @ 17.6, unchanged at +50m — two reads
15m5s apart, Δ0.0). Not ambiguous (no climb-then-fade or slow-drift shape) — decided at +50m
per the brief, no +65m read needed.

**Phase 3 — verdict:** converged score **17.6 == bracket 17.6** exactly (bracket−0.2 = 17.4;
17.6 ≥ 17.4) → **KEEP**. The `RACE_SHARE_PEN` 2→4 sweep (+ `DENY_W` parked at 0) produced **no
measurable change** in this arena room relative to the champion's own immediately-preceding
reconvergence level — a clean tie, not a regression and not an improvement. Candidate remains
the live arena entry (no revert needed).

**Phase 4 — at parity, per the brief's explicit instruction ("at parity leave at race"):**
`cgauto/api_submit.py`'s default is **left unchanged** at `v1.36.0-race.min.rs` — sharepen4 is
NOT promoted to champion/default status despite being kept live in the slot. Verified the file
still reads the race path (no edit made). This mirrors the v1.28.3-sticky6 precedent (NEUTRAL
verdict, "left live (same policy)", champion/default pointer untouched).

**Goal gate (rank ≤99):** did not fire — every read this episode stayed in the 117-123 range
(bracket reads 117/121/121/121, convergence reads 123/121/121), nowhere near ≤99. No
confirming read required.

**One line for the analyst:** `RACE_SHARE_PEN` 2→4 landed as a flat no-op in this arena room
(17.6→17.6, exact tie with the champion's own concurrent bracket) — either the mechanism is
already saturated at the old value (2) for this room's current opponent mix, or the effect is
being masked by the same night-drift band that's depressed the champion itself from 19.3-20.1
down to 17.6; the next candidate (chop_r 5→4, queue #2, an orthogonal travel-reduction lever
with no fell-valuation interaction risk) is unaffected by this null result and remains the
right next submit — but note the arena room is currently reading ~2pt below the champion's
historical peak band for reasons unrelated to any candidate's code, so don't over-interpret
small deltas until a read lands back near 19-20 to re-baseline.

### Records

`cgauto/api_submit.py` default confirmed unchanged (`v1.36.0-race.min.rs`) — no edit needed
(parity case). `docs/arena-queue.md` champion/queue/verdict-log updated in the same commit.
Committed the moment this verdict was decided (03:37), per the slot-ownership rule and the
brief's "commit early and again at the end" instruction.

## 2026-07-08 07:40 — MEASUREMENT POLICY v2 (user-designed): deltas, chaining, noise bands
User's critique of the overnight process, adopted wholesale: (1) only base→feature DELTAS
carry signal — absolute positions across hours are noise (the "trough" was a category
error); (2) baseline valid ~5h → CHAIN candidates against one base measurement instead of
re-measuring per pair (2× slot throughput); (3) bands recalibrated to the measured ±1
single-convergence noise: ±0.5 decision bands, +1.0 (or 2×+0.5) for promotion — the old
±0.2 threshold operated BELOW the noise floor (sharepen4's "exact parity" was a coin-read).
In-flight conformance: the 07:20 pure-champion resubmission IS the fresh baseline; roam4
chains on it; sharepen4's parity verdict downgraded to INCONCLUSIVE retroactively.

## Probe: champion vs killer archetypes (from our side)

**Setup.** Champion probed = `cgauto/submissions/v1.36.0-race.rs` (the FROZEN artifact, not
the tree — matches the current live champion per this log). DEBUG probe rebuilt fresh:
`sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` (1 hit) → `tools/minify.py`
(71454→43305 chars, byte-identical size to the candidate's own gate report) →
`rustc --edition 2021 -O` on a dot-free copy → exit 0. Opponent exemplars identified via
`field_targets.py 60 160` cross-referenced against the "Analyst census on the race champion
(2026-07-08 night)" entry above: **mlomb** (agentId `6480863`, rank 142/16.8 — the
harvest-economy archetype, "wins with a LOW chop count but very high HARVEST+DROP volume")
and **ArgoZ** (agentId `6480671`, rank 153/16.4 — the sharper of the two burst-chopper
exemplars named in that census's worst-losses table, "explosive delayed chop-burst" shape,
full 300-turn game vs NicknamedTwice's early-ended single sample). 5 DEBUG games played per
opponent via `collect_debug_games.py` (10 of the 12-game budget; the other 2 held in
reserve — both samples converged on clean, low-variance mechanisms with all-games agreement,
so more play wasn't needed for signal). Artifacts: `data/boss5_games/6480863/` (mlomb),
`data/boss5_games/6480671/` (ArgoZ) — `.map`/`.log`/`.raw` per game.

### Results

**mlomb (harvest-economy): 2W / 3L**

| gameId | W/L | wood (me-opp) | score (me-opp) | my_train | opp_train | note |
|---|---|---|---|---|---|---|
| 895459345 | W | 50-26 | 208-115 | t11 | t2 | |
| 895459363 | **L** | 26-**3** | 123-152 | t89 | t2 | we OUT-WOOD them 26-3 but lose on fruit: oppinv fruit=140 vs mine=19 |
| 895459396 | L | 17-28 | 75-131 | t3 | t2 | game ends early t125 (deforestation); double-dimension loss |
| 895459414 | **L** | 24-48 | 103-211 | **t77** | t2 | lopsided map (16 trees our half / 2 theirs); opp on OUR half up to 71% of troll-time in phase 1 |
| 895459425 | W | 48-35 | 204-168 | t13 | t2 | |

**ArgoZ (burst-chopper): 5W / 0L**

| gameId | W/L | wood (me-opp) | score (me-opp) | my_train | opp_train | oppwood shape |
|---|---|---|---|---|---|---|
| 895459446 | W | 97-68 | 389-283 | t43 | t63 | 0 through t175, then 8→25→40→59→68 (t200→300) |
| 895459486 | W | 66-46 | 269-184 | t17 | t37 | 0 through t175, then 6→28→35→40→43 |
| 895459521 | W | 69-51 | 278-214 | t58 | t69 | 0 through t175, then 13→37→48 |
| 895459556 | W | 83-70 | 341-294 | t55 | t81 | 0 through t200, then 25→42→59→70 |
| 895459591 | W | 82-84 | 342-342 (tie-break W) | t15 | t39 | 0 through t150, then 11→30→52→64→77 |

Note: ArgoZ went **5/0** against the true champion, whereas the 2026-07-08 night census's
"explosive delayed chop-burst" loss decode came from a different, deny1-confounded live
candidate — not v1.36.0-race. Under the actual champion code, this archetype's burst shape
is still clearly visible (see below) but doesn't flip any of these 5 games; our own wood
ramps steadily and monotonically from early game in every one (e.g. game 1: 0,2,12,22,30,
40,50,60,70,80,90,97 every 25 turns) while theirs sits at literal 0 until ~t175-200.

### Move-fraction + flap analysis (from @TFMOVE MOVE-intent presence; role = final
`mybuilds` hp==0∧chop>0 ⇒ chopper, else starter)

| bucket | chopper MOVE% | starter MOVE% | avg total flaps |
|---|---|---|---|
| mlomb WINS (n=2) | 48% (237/495) | 81% (417/517) | 7.5 |
| mlomb LOSSES (n=3) | 57% (288/508) | 84% (564/674) | 0.0 |
| ArgoZ WINS (n=5, no losses) | 41% (527/1272) | 69% (1001/1455) | 5.0 |

Chopper MOVE-fraction runs **9pp higher in mlomb losses than wins** (57% vs 48%) — the
chopper spends more of its turns traveling instead of chopping when we lose, reproducing
(now against the TRUE champion, not the deny1 confound) the earlier census's "elevated
MOVE:CHOP in worst losses" finding. Flap counts stayed single-digit in all 10 games (0-8),
inside `STICKY`'s documented "absorbed" 2-21 band — not a differentiator here (if anything
losses show *fewer* recorded flaps, likely just small-sample noise, not a real inverse
effect).

### New finding: training-gate / farm-stall correlation (mlomb)

`my_train` is t11/t13 in both mlomb wins vs **t77/t89** in 2 of the 3 losses (`opp_train`
is a rock-solid t2 in literally every game, no variance on their side). `@TFFARM` shows
`farm_now`/`seeds` (banana bank) **flatlining at 0 for 60-90 straight turns** in exactly
those two slow-train losses — game 895459363: `seeds` stuck at 1 then 0 from t10 through
t85, `farm_now=0` from t35-t85; game 895459414: `farm_now` peaks at 5 by t20 then decays to
0 by t95 while `seeds=0` from t25 onward — while both wins keep `seeds≥2`/`farm_now≥2`
continuously right up to their (fast) training point. This is the same farm-stall failure
mode already documented against Boss 5 (`GE_FEEDER_FARM` comment: "farm_now collapsed to
literal 0 for 63-100% of sampled turns per game"), now reproduced against mlomb
specifically: it costs ~20-30% of the game running a solo, travel-heavy (76-91% MOVE)
starter while the opponent has already doubled its workforce since turn 2. The third loss
(895459396, `my_train=t3`, ended early at t125 via deforestation) is unrelated to this
mechanism — training was fast there; that loss is a plain short-game economy/scale defeat.

### New finding: the burst IS a cross-half raid (ArgoZ)

Opponent-troll presence on OUR half of the map (nearest-shack bucketing off turn-1 `@TFI P`
tree/shack positions, confirmed exactly point-symmetric per game: reflecting `my_shack`
about the map center lands exactly on `opp_shack` in every sampled map) is **~0-4% for the
first three 75-turn phases (t1-225) in ALL 5 games**, then **jumps to 37-52% in the last
phase (t226-300)** — exactly coincident with their wood curve going from flat 0 to +40-77
in every single game. The archetype's "explosive delayed chop-burst" is mechanically a
**late cross-half raid**: hoard/train (up to 4 trolls) on their own side while doing
essentially nothing (0 wood) for 175-200 turns, then send a meaningful fraction of that
larger roster across the midline once trees thin out, harvesting whatever's left —
including trees on OUR side. We still won all 5 sampled games (our steady early ramp
outpaces their delayed one), but the mechanism itself is unambiguous and reproduces
identically across every game in the sample.

### Answers to the two specific questions

- **Harvest-economy (mlomb) — do we lose because they out-SCORE us on fruit while we match
  wood?** PARTIALLY. In the sharpest loss (895459363) yes exactly: we out-wood them 26-3 but
  lose 123-152 on a pure fruit blowout (140 vs 19 fruit-points). But the other 2/3 losses are
  plain double-dimension defeats (they out-produce us on BOTH wood and fruit) — so the
  fruit-only mechanism explains 1 of 3 losses, not the majority; the bigger recurring driver
  is the training-gate/farm-stall above.
- **Burst-chopper (ArgoZ) — is their burst fed by trees WE left standing, i.e. would earlier
  liquidation/denial on our side starve it?** YES. Opponent troll-presence on our half jumps
  from ~0% to 37-52% exactly in the burst window in all 5 games, so part of their late yield
  is trees on OUR side that our own chopper hadn't reached yet; earlier liquidation of our
  own-half ripe trees (denying them targets by the time they cross) should shrink what's left
  for the raid to take — though it didn't cost us the game in this sample (5/5 wins).

### Single most actionable our-side waste

The farm/seed funding stall that delays 2nd-troll training to t77-t89 in 2 of 3 mlomb losses
(vs a rock-solid t11-t13 in the wins), against an opponent that trains its own 2nd troll at
t2 in literally every game sampled: `@TFFARM` shows `farm_now`/`seeds` flatlining at 0 for
60-90 straight turns exactly in those two games — the same known farm-stall pattern already
documented against Boss 5, now confirmed to recur against a live field archetype and to cost
up to 30% of the game running a solo, travel-heavy starter while the opponent has already
doubled its headcount.

## Champion loss taxonomy (2026-07-08 morning)

**Read-API only, no DEBUG games, no arena actions.** Confirmed live/uncontaminated (unlike the
2026-07-08 night census, which hit a different candidate's slot): `cg_rank.py` read 115/527 @
19.1 (agentId 6543178), squarely inside v1.36.0-race's documented 17.6-20.1/rank-88-121 band
right after the 07:20 pure-champion resubmission baseline. `battles.py 40` pulled **20W/20L**
(140 battles listed), opponent ranks 103-121 / scores 17.7-19.9 — matches the champion's diet
exactly, so this census is clean (all 20 losses are genuinely v1.36.0-race's).

**Method:** fetched all 20 losses via `gameResult/findByGameId` (same call `battles.py` uses,
`userId=1302251`), decoded every frame's `stdout` (one command per troll, `;`-joined, verbs
normalized uppercase) into command-mix counts per 75-turn phase (t1-75/76-150/151-225/226-300)
for both players. Scratch decode/classify scripts + cached raw JSON live under this session's
scratchpad (not committed); full per-game numbers reproduced below.

### The 20-loss table

| gameId | opponent (rank/score) | margin | shape | our anomalies |
|---|---|---|---|---|
| 895459072 | Eagleast (113/19.2) | -155 | HARVEST-ECONOMY | MOVE:CHOP 3.1 (in/near baseline); scale gap (opp trained 2 vs our 1); chop 124 vs opp 93 |
| 895458889 | TheMagicShop (104/19.9) | -141 | BURST-CHOPPER | MOVE:CHOP 4.0 (1.5x baseline); scale gap (opp trained 2 vs our 1); chop 100 vs opp 207 |
| 895458757 | TheMagicShop (104/19.9) | -115 | DUAL-ECONOMY | MOVE:CHOP 5.1 (**1.9x** baseline 2.7 — severe travel waste); scale gap (opp trained 2 vs our 1); chop 80 vs opp 180 |
| 895458926 | mikdiet (112/19.4) | -78 | OTHER (balanced scale-grind) | MOVE:CHOP 2.6 (in/near baseline); scale gap (opp trained 2 vs our 1); chop 106 vs opp 129 |
| 895458987 | mikdiet (112/19.4) | -74 | HARVEST-ECONOMY | MOVE:CHOP 2.5 (in/near baseline); scale gap (opp trained 2 vs our 1); chop 123 vs opp 109 |
| 895459147 | mikdiet (112/19.4) | -68 | HARVEST-ECONOMY | MOVE:CHOP 2.9 (in/near baseline); scale gap (opp trained 2 vs our 1); chop 130 vs opp 78 |
| 895459143 | R4N4R4M4 (118/17.9) | -66 | BURST-CHOPPER | MOVE:CHOP 3.6 (1.3x baseline); scale gap (opp trained 3 vs our 1); chop 95 vs opp 204 |
| 895458790 | Crouistiti (119/17.8) | -50 | OUT-TEMPO | MOVE:CHOP 6.5 (**2.4x** baseline — severe travel waste); equal troll count; chop 49 vs opp 146 |
| 895459050 | 7AM (114/19.1) | -46 | HARVEST-ECONOMY | MOVE:CHOP 2.8 (in/near baseline); scale gap (opp trained 3 vs our 1); chop 132 vs opp 159 |
| 895458981 | TheMagicShop (104/19.9) | -37 | HARVEST-ECONOMY | MOVE:CHOP 3.5 (1.3x baseline); scale gap (opp trained 2 vs our 1); chop 116 vs opp 136 |
| 895458742 | Haseir (106/19.8) | -36 | DUAL-ECONOMY | MOVE:CHOP 7.4 (**2.8x** baseline — severe travel waste); scale gap (opp trained 3 vs our 1); harvest+drop starved (29 vs opp 162); chop 65 vs opp 125 |
| 895459060 | Bizzon. (117/17.9) | -32 | OUT-TEMPO | MOVE:CHOP 6.0 (**2.2x** baseline — severe travel waste); equal troll count; chop 60 vs opp 103 |
| 895458705 | lD (116/18.3) | -31 | DUAL-ECONOMY | MOVE:CHOP 5.1 (**1.9x** baseline — severe travel waste); scale gap (opp trained 2 vs our 1); chop 67 vs opp 101 |
| 895458698 | HLhop (108/19.6) | -28 | CLOSE-MARGIN | MOVE:CHOP 2.3 (in/near baseline); equal troll count; chop 113 vs opp 141 |
| 895459126 | HLhop (108/19.6) | -27 | OUT-TEMPO | MOVE:CHOP 3.7 (1.4x baseline); equal troll count; chop 115 vs opp 270 |
| 895459170 | HLhop (108/19.6) | -16 | CLOSE-MARGIN | MOVE:CHOP 1.2 (in/near baseline); equal troll count; chop 238 vs opp 207 |
| 895458693 | Haseir (106/19.8) | -13 | DUAL-ECONOMY | MOVE:CHOP 4.8 (**1.8x** baseline — severe travel waste); scale gap (opp trained 3 vs our 1); chop 86 vs opp 151 |
| 895458876 | Bizzon. (117/17.9) | -11 | OUT-TEMPO | MOVE:CHOP 5.1 (**1.9x** baseline — severe travel waste); equal troll count; chop 60 vs opp 95 |
| 895458944 | pbou (103/19.9) | -10 | CLOSE-MARGIN | MOVE:CHOP 2.6 (in/near baseline); equal troll count; chop 80 vs opp 113 |
| 895458712 | HLhop (108/19.6) | -6 | OUT-TEMPO | MOVE:CHOP 3.7 (1.4x baseline); equal troll count; chop 105 vs opp 241 |

Classification rule (priority order, applied mechanically from the phase-chop series + totals):
(a) BURST if opponent CHOP jumps from ≤10 to ≥60 in one phase transition; else (e) DUAL if
opp HARVEST+DROP ≥1.8x ours AND opp CHOP ≥1.3x ours; else (b) HARVEST-ECONOMY if opp
HARVEST+DROP ≥1.6x ours; else (c) OUT-TEMPO if opp CHOP ≥1.5x ours; else (d) CLOSE-MARGIN if
|margin|<30; else (e) OTHER (described per-case). Shape boundaries are fuzzy at the edges (see
TheMagicShop below) — opponent IDENTITY often predicts the shape better than any one game's
numbers.

### Shape distribution

| shape | n | share | avg margin | avg MOVE:CHOP (ours) |
|---|---|---|---|---|
| b HARVEST-ECONOMY | 5 | 25% | -76.0 | 2.94 |
| c OUT-TEMPO | 5 | 25% | -25.2 | **5.00** |
| e DUAL-ECONOMY (new) | 4 | 20% | -48.8 | **5.60** |
| d CLOSE-MARGIN | 3 | 15% | -18.0 | 2.05 |
| a BURST-CHOPPER | 2 | 10% | -103.5 | 3.82 |
| e OTHER (scale-grind) | 1 | 5% | -78.0 | 2.63 |

**(e) shapes described precisely, both new since the last (deny1-contaminated) census:**
- **DUAL-ECONOMY**: opponent trains a 2nd/3rd troll and out-produces us on BOTH wood (CHOP
  ≥1.3x) AND fruit (HARVEST+DROP ≥1.8x) at once — a strict superset of HARVEST-ECONOMY, not a
  specialist build. TheMagicShop/Haseir/lD, all with opp_train > ours.
- **OTHER (balanced scale-grind)**, single sample (mikdiet, -78): opponent's extra troll (2 vs
  our 1) buys a uniform ~1.2-1.25x edge on chop AND harvest/drop, no specialization at all —
  just a flat scale tax.

**Ranking by (share × |avg margin|)**, the requested weighting: (1) HARVEST-ECONOMY 0.25×76.0
= **19.0**; (2) BURST-CHOPPER 0.10×103.5 = **10.35**; (3) DUAL-ECONOMY 0.20×48.8 = 9.76 (near
tie with #2, n=4 vs n=2); (4) OUT-TEMPO 0.25×25.2 = 6.3; (5) OTHER 0.05×78 = 3.9; (6)
CLOSE-MARGIN 0.15×18 = 2.7. If HARVEST-ECONOMY and DUAL-ECONOMY are merged (same root
mechanism — opponent's extra troll runs a fruit economy, just with a chop edge attached or
not): n=9/20 = **45% of ALL losses**, avg margin **-63.9**, weight **28.75** — by a wide margin
the single biggest lever in this dataset.

### Two cross-cutting findings (not one of the requested shapes, but sharper)

**1. Scale parity perfectly predicts shape family.** Split by opp_train vs our fixed
GE_MAX_TROLLS=2 (we trained exactly 1 extra troll in all 20 games, no exceptions):
- **Equal troll count** (8/20 = 40%: all 4 HLhop games + both Bizzon. games + Crouistiti +
  pbou): **100%** land in OUT-TEMPO or CLOSE-MARGIN, avg margin only **-22.5**.
- **Opponent out-trains us** (12/20 = 60%, 2-3 trained): **100%** land in HARVEST-ECONOMY /
  DUAL-ECONOMY / BURST-CHOPPER / OTHER, avg margin **-71.7** — 3.2x worse.
No exceptions either direction across 20 games. Opponent identity clusters the same way: HLhop
(4 losses, always equal-scale, always out-tempo/close) and TheMagicShop/mikdiet (3 each, always
out-training us, always a specialized-economy shape) are recognizable recurring builds, not
random draws — 5 opponents (HLhop, mikdiet, TheMagicShop, Bizzon., Haseir) account for 13/20
(65%) of all losses at this rank band.

**2. The late-throughput-ceiling reproduces live, inside the current champion's own arena
losses** (previously only quantified vs the real Boss 5, `late-throughput-ceiling` memory).
Average CHOP count by phase, both sides, across all 20 losses:

| phase (turns) | our avg CHOP | opp avg CHOP | delta |
|---|---|---|---|
| 1-75 | 29.2 | 13.2 | **+16.0** (we lead) |
| 76-150 | 26.8 | 40.0 | -13.3 |
| 151-225 | 23.9 | 49.7 | -25.8 |
| 226-300 | 22.3 | 46.5 | -24.2 |

Our own chop output *declines* every phase (29.2→22.3) while the opponents' *triples*
(13.2→46.5) — we win the opening in every one of these 20 losses and still lose the game.
Textbook late-throughput-ceiling, now confirmed against the live arena field, not just Boss 5.

### The single sharpest our-side anomaly

**Our own MOVE:CHOP ratio averages 3.93 across all 20 losses vs the historical baseline ~2.7
(≈1.46x), and is NOT a deny1 artifact** — `DENY_W` is parked at 0 and has been since the
02:40 revert; this is pure v1.36.0-race. It is elevated almost identically in both scale-parity
groups (equal-scale 3.89, opp-out-trains 3.95 — a champion-wide trait, not opponent-shape-
specific) and peaks brutally in exactly the two most damaging shapes: DUAL-ECONOMY (avg 5.60,
up to 7.45/7.4x-baseline vs Haseir) and OUT-TEMPO (avg 5.00, up to 6.53 vs Crouistiti — the
*same-troll-count* group, so this is a pure execution/routing signature, unconfounded by
scale). Best read as the mechanism behind finding #2 above: turns burned on travel are turns
not spent chopping, compounding into the observed late-game chop-output decline. The prior
night's census (deny1-contaminated) attributed an elevated MOVE:CHOP specifically to `DENY_W`
colliding with `race()`'s tie-break — this data shows the elevated ratio predates and outlives
deny1, so that attribution was at best partial; the travel-waste defect is standing and
champion-wide.

### Top-2 counters, ranked for the arena queue

**#1 (top pick, addresses HARVEST-ECONOMY + DUAL-ECONOMY, 45% share / -63.9 avg margin
merged).** Traced the mechanism in `rust/src/botmain/planner.rs`: the only "go get fruit" bands
are (a) band 75, opportunistic-only (standing on it already), gated to BANANA/water-APPLE
`when !want_chopper`, and (b) funding bands 58-65, narrow fruit-type + narrow
`want_chopper||want_feeder` window. The one genuine "MoveTo any ripe fruit" band (62, line
~270-274) is gated `plan.phase == Phase::Hoard` — and `phase_for` (`tactics.rs`) maps
`Meta::Tempo` (the live meta; Scale/T-hand is reverted) **unconditionally** to `Phase::Tempo`,
so that band never fires for the live champion. Net effect: under Tempo, fruit is harvested
only as a side-effect of standing on it or of chopper/feeder funding — there is no active
"path toward ripe fruit for its own point value" band once funding is satisfied, which is the
direct, code-level explanation for our flat 20-90/game HARVEST+DROP totals regardless of the
opponent's 91-307. **Proposed change:** add a modest Tempo-active MoveTo-to-ripe-fruit band
(any fruit type, ~band 45-48 — below the primary chop bands 70/72 and funding 58-65, above
chop-help 40/42) whenever a troll has free capacity and no higher-value candidate. **Testable
prediction:** our own HARVEST+DROP totals should rise from 20-90 toward 100+ in games vs
HARVEST/DUAL-economy-style opponents (mikdiet/TheMagicShop/Eagleast/7AM/Haseir/lD), and the
avg margin against that specific cluster should close from -63.9 toward the OUT-TEMPO band
(-25) or better, without touching CHOP valuation at all (zero interaction risk with `race()`
or the parked `DENY_W`).

**#2 (second pick, addresses BURST-CHOPPER, 10% share / -103.5 avg margin, n=2 — thin
sample).** Both burst losses pair an opponent troll-count edge (2-3 vs our fixed
`GE_MAX_TROLLS=2`) with a near-zero opponent CHOP count through phase 1 that converts
explosively once their extra troll(s) come online (turn ~76-150). **Deliberately NOT**
proposing to train our own extra troll earlier/cheaper to match — that mechanism is a
re-tread of two already-dead ends (T-hand, reverted 2026-07-07 -2.2pts, the added troll never
found a role and didn't repay its funding; and the older "2nd chopper starves the farm" result)
whose failure was about the added troll's ROLE, not its training timing. **Proposed change
instead:** a turn-gated valuation change confined to our *existing* single chopper — during
phase 1 only (turns 1-75), loosen `own_half`/`within_roam` (planner.rs ~122-124, feeding bands
70/72) so the chopper claims a slightly wider tree pool while these opponents are still
dormant, banking extra fell-ready supply before the delayed burst starts converting.
**Testable prediction:** re-sampled games vs R4N4R4M4/TheMagicShop-style delayed-onset
opponents should show our phase-1/2 CHOP counts rise further above the current lead
(29.2/26.8 avg) and the opponent's phase-3/4 burst should find a smaller remaining-tree pool,
narrowing the -66/-141 margins toward the OUT-TEMPO band (-25 avg). Flagged as the
thinnest-evidence proposal here (n=2); if it doesn't pan out, the more precise version (relax
only when the opponent is *observed* to have felled ~0 trees so far, rather than a blanket
phase-1 gate) is the natural follow-up but needs new per-game opponent-chop-count state, not
just a knob.

Both counters are orthogonal to the current in-flight candidate (chop_r 5→4 / v1.40.0-roam4,
queue #2) and to the parked `DENY_W`/`race()` collision — neither touches fell-target
tie-breaks.

## v1.40.0-roam4 arena verdict (2026-07-08 ~10:13) — REVERTED (converged 199/527 @ 15.5 vs bracket 115/527 @ 19.1, −3.6pt)

**Process note — mid-episode bracket redirect from the controller (07:20-07:21 MSK).** This
runner's original Phase-0 loop (wait for a `cg_rank.py` read ≥19.0, or a 6h cap, per the
arena-runner brief's night-trough clause) had logged **8 consecutive flat reads, 121/527 @ 17.6,
agentId 6542656 (v1.39.0-sharepen4, live at parity), from 03:58 through 07:03 MSK (3h05m, zero
movement)**. At 07:21:28 the controller messaged in: it had independently resubmitted the PURE
champion `v1.36.0-race.min.rs` at 07:20:53 (SUBMIT-OK) as a clean re-baseline, on the theory
that the persistent flat 17.6 might be masking a sharepen4-specific regression rather than pure
night-trough drift, and instructed this runner to hold the roam4 submit, monitor that fresh
resubmit's reconvergence, and use THAT as the Phase-1 bracket instead of the original loop's own
threshold-or-cap criterion. This runner verified the claim independently rather than taking it
on faith — `agentId` shifted 6542656 → **6543178** on the very next read, confirming a real
resubmission had landed:

| time (MSK) | rank | score | agentId | note |
|---|---|---|---|---|
| 07:22:52 | 335/527 | 12.6 | 6543178 (new) | cold-start; resubmit confirmed |
| 07:38:16 | 119/527 | 17.8 | 6543178 | climbing |
| 07:53:34 | 115/527 | 19.1 | 6543178 | climbing |
| 09:20:20 | 115/527 | 19.1 | 6543178 | **stable** (Δ0.0, 86m46s after prior read) |

(A `sleep 360` issued between the 07:53 and 09:20 reads returned after an unexplained ~72-minute
wall-clock overrun beyond its requested duration — flagged as an environment/scheduling anomaly,
not an arena event; `agentId` was unchanged across the gap, so it does not contaminate the read.)

Two stable reads 86m46s apart, same agentId, Δ0.0 → **Phase-1 bracket = 115/527 @ 19.1**
(v1.36.0-race, freshly resubmitted), superseding this runner's own Phase-0 criterion per the
controller's redirect.

**On the "sharepen4 masked regression" question the controller asked this runner to record:**
the data is *consistent* with that hypothesis (the fresh pure-race resubmit settled 1.5pt above
sharepen4's rock-flat 17.6) but is **not conclusive**, for a timing reason worth flagging
plainly: sharepen4's flat-17.6 window (03:58-07:03) and the fresh race resubmit's climb-to-19.1
window (07:20-09:20) are *sequential*, not concurrent. This room's own verdict log already
documents the *identical, byte-unchanged* `v1.36.0-race` code reading anywhere from 17.6 to
19.9-20.1 across different resubmissions/times of day (the documented drift band). Simple
morning trough-recovery (this runner's original Phase-0 premise) is therefore an equally
sufficient explanation for the 17.6→19.1 change as a sharepen4-specific cost is — no concurrent
A/B (a fresh race resubmit DURING the 03:58-07:03 window) exists to separate the two. Recorded
per the controller's request, flagged for the analyst to weigh rather than asserted as proven;
if pursued, the controller's implied next step is a `RACE_SHARE_PEN` 4→2 isolation retest.

**Update — this question already has an authoritative (partial) answer.** Mid-episode, the user
landed `73d3c10` (07:32:50 MSK) — see "## 2026-07-08 07:40 — MEASUREMENT POLICY v2" above — which
explicitly addresses exactly this: "the old ±0.2 threshold operated BELOW the noise floor
(sharepen4's 'exact parity' was a coin-read)," and states **"sharepen4's parity verdict
downgraded to INCONCLUSIVE retroactively."** That resolves the label (sharepen4 is INCONCLUSIVE,
not KEEP-AT-PARITY) but not the underlying mechanism question — INCONCLUSIVE means "can't tell
from this data," not "confirmed no cost," so the `RACE_SHARE_PEN` 4→2 isolation retest above
remains the way to actually settle whether `RACE_SHARE_PEN=4` costs anything. The same 07:40
note also explicitly sanctions this runner's bracket choice: **"the 07:20 pure-champion
resubmission IS the fresh baseline; roam4 chains on it"** — i.e. using 115/527 @ 19.1 (not the
flat sharepen4 17.6, and not a fresh from-scratch bracket read) as this candidate's baseline is
the policy-designer's own prescribed methodology, not just this runner's/the controller's
independent judgment call.

**Phase 2 — submit** (09:20:59 MSK): `api_submit.py cgauto/submissions/v1.40.0-roam4.min.rs` →
`TestSession/submit: 200 40966338` → SUBMIT-OK. New agentId confirmed live on first read
(6543450).

**Phase 3 — convergence reads:**

| time (MSK) | Δt post-submit | rank | score | agentId |
|---|---|---|---|---|
| 09:41:18 | +20m | 174/527 | 16.1 | 6543450 |
| 09:55:36 | +35m | 187/527 | 15.7 | 6543450 |
| 10:09:59 | +50m | 199/527 | 15.5 | 6543450 |

Shape: monotonic fade, 16.1→15.7→15.5, same agentId throughout, no rebound at any point —
unambiguous (a clean "flat-low/fading" shape, decidable without a +65m read per the queue's own
shape taxonomy). Decided at +50m per the brief.

**Phase 4 — verdict:** under **MEASUREMENT POLICY v2** (landed mid-episode, `73d3c10`, and
confirmed to apply to this exact candidate — "roam4 chains on it," see above), delta =
candidate − baseline = 15.5 − 19.1 = **−3.6**, decisively past the v2 revert bar (delta ≤ −0.5)
→ **REVERT**. Cross-checked against the pre-v2 brief's own criterion too (bracket 19.1, keep bar
= bracket−0.2 = 18.9; 15.5 is −3.6pt below it) and against the original brief's fallback bracket
(had the 6h cap been hit using the flat sharepen4 17.6 instead, keep bar 17.4; 15.5 still fails
by −1.9pt) — all three framings agree. `GE_CHOP_R` 5→4 does not help in this arena room:
tightening the roam radius by 1 further on the current R6b planner costs performance rather than
saving travel, opposite the sweep's working hypothesis. Given the monotonic (not flat, not
rebounding) fade shape, this reads as a genuine effect, not noise.

**Revert executed:** `api_submit.py cgauto/submissions/v1.36.0-race.min.rs` at 10:19:18 MSK →
`TestSession/submit: 200 40966560` → SUBMIT-OK.

**Revert reconvergence:**

| time (MSK) | Δt post-revert-submit | rank | score | agentId |
|---|---|---|---|---|
| 10:34:38 | +15m | 131/527 | 17.1 | 6543474 (new) |
| 10:47:56 | +29m | 140/527 | 16.8 | 6543474 |
| 11:02:19 | +43m | 135/527 | 17.0 | 6543474 |
| 11:16:57 | +58m | 135/527 | 17.0 | 6543474 |

Settled after a brief 17.1→16.8 wobble; the last two reads are an exact match (135/527 @ 17.0,
Δ0.0, 14m38s apart) — reconvergence confirmed, same agentId throughout (no contamination). 17.0
sits a little below the most recent 19.1/17.6 points but is the same byte-identical champion
code, consistent with this room's already-documented drift band (17.6-20.1) — **arena is NOT
left on a regressed bot.**

**Goal gate (rank ≤99):** did not fire at any point this episode (best rank reached: 115/527).

**One line for the analyst:** `GE_CHOP_R` 5→4 REVERTED under v2 (delta −3.6, monotonic fade, not
noise) — the cascade-era "radius 3 marginally better / within noise" verdict does not license
assuming radius 4 is safe on the R6b planner either; tightening roam is net-negative here,
opposite this sweep's premise, so the roam-radius family looks closed for now (5 stays live) and
the queue's own top-ranked pending ideas — the Tempo-active fruit-harvest band (#1,
HARVEST/DUAL-economy, 45% share) and the phase-1 `own_half`/`within_roam` loosening for
delayed-burst opponents (#2, BURST-CHOPPER) — are the better next bets; separately, v2's own
07:40 note already downgraded sharepen4 to INCONCLUSIVE (noise-floor correction, not this
runner's finding), but that still leaves the underlying `RACE_SHARE_PEN=4` mechanism question
open — a dedicated 4→2 isolation retest (chained against a single baseline, per v2) would settle
it either way, and this runner's own bracket data (sharepen4 flat 17.6 for 3h+ vs a same-day
fresh-resubmit champion settling at 19.1) is at least suggestive that it's worth doing sooner
rather than later.

### Records

`cgauto/api_submit.py` default confirmed unchanged (`v1.36.0-race.min.rs` — was already correct
pre-episode; REVERT case needs no edit). `docs/arena-queue.md` champion/queue/verdict-log
updated in the same commit. Committed the moment this verdict was decided (~10:13), per the
slot-ownership rule and the brief's "commit early and again at the end" instruction; reconvergence
verified above (~11:17), second commit follows immediately.

**Cross-reference — a real process gap this revert exposed (not this runner's action item, fixed
by a concurrent gatekeeper):** this runner's revert, per the brief, only resubmitted the frozen
`v1.36.0-race.min.rs` *artifact* to the arena — it did not (the brief never asked it to) restore
`rust/src/botmain.rs`'s source consts, which still carried `GE_CHOP_R=4` (roam4) and
`RACE_SHARE_PEN=4` (sharepen4) from the working tree's own commit history. A concurrent
gatekeeper working an unrelated candidate (`v1.41.0-nopickloop`) built on top of that tree and
got contaminated results (see "## 2026-07-08 ~11:00 — TREE-TRACKS-CHAMPION rule + pickloop
refrozen clean" below) before catching and fixing it (`059ee5c`: consts restored to
`GE_CHOP_R=5`/`RACE_SHARE_PEN=2`, a new "tree-tracks-champion" rule adopted — after every arena
revert, restore the tree's consts to champion semantics too, not just the arena artifact). Flagged
here for anyone reading this candidate's history end-to-end; no action needed from this runner
since the fix already landed and this candidate's own arena verdict (measured entirely from
pre-frozen `.min.rs` artifacts, never the live tree) is unaffected by the gap either way.

## 2026-07-08 ~11:00 — TREE-TRACKS-CHAMPION rule + pickloop refrozen clean
Gatekeeper contamination find: roam4's arena revert (−3.6) never restored the SOURCE tree —
pickloop was built+gated carrying GE_CHOP_R=4 (and PEN=4 from the inconclusive sharepen4).
NEW RULE: after every arena revert, the tree's consts are restored to champion semantics and
the candidate's tests get #[ignore]+reason (roam.rs, share_pen test done now; GE_CHOP_R=5,
PEN=2 restored; 55 pass/7 ignored; self-det EQUAL). v1.41.0-nopickloop REFROZEN on the clean
base (min 44,2xx B, compiles, DEBUG probe rebuilt). Fresh mini-gate next; the contaminated
gates' verdicts (074e5b8, b2f46eb) are void for the fix itself (weak-positive evidence:
0/12 livelock pins, the one precondition map scored above sample average).

## 2026-07-08 15:08 — v1.41.0-nopickloop arena verdict: KEEP (+0.5); session-limit gap handled

Runner a3e1a9d bracketed the champion 135/527 @ 17.0 (3 stable reads 11:13-11:33, agentId
6543474), submitted v1.41.0-nopickloop 11:33:31 (SUBMIT-OK, TestSession 40966815), then the
account-wide session rate limit killed it at 11:42 (9 min post-submit, zero convergence reads).
Controller resumed after the 14:50 reset: 123/527 @ 17.5 at 14:56:59 and again exact at
15:07:55 (agentId 6543505) — **delta +0.5 vs bracket, KEEP** at the v2 bar. Left live =
chained baseline (~valid to 20:00). NOT champion-promoted (first +0.5 of the required two;
default stays v1.36.0-race.min.rs). Goal gate did not fire (123 > 99).

Same window, D1 pipeline: v1.42.0-idlefruit review APPROVED (proof-grade band-order check:
fresh chop-help ≥ 3,999,751 vs sticky-held band-38 ≤ 3,800,006 — sticky=6 cannot cross the
200k inter-band gap; NB STICKY=6 since v1.28.3, older notes saying 3 are stale). Reviewer's
one IMPORTANT (band 38 lacked the race() doomed-target skip — the exact waste class v1.36.0
cured) fixed in-worktree (9948578) with a RED→GREEN doomed-fruit test; 58 tests green;
artifacts rebuilt 44,986 B. Next: re-review → merge → mini-gate → arena chained on 17.5.

## 2026-07-08 16:50 — SUPERSEDED tent-wall analysis: old "shacks are WALKABLE" hypothesis was wrong

User watched game 895493013 vs Sasso_Stark (16x8 map, we won 214-81 as agent 1, agentId
6543636 = v1.42.0's recalc burst) and saw absurdly long paths around a lake+tent+boulder
wall. Verified: the wall's ONLY gap is our tent (13,4); the referee treats shack cells as
walkable (engine mirror rust/src/game/state.rs:75-92 — trolls walk over/stand on tents;
TRAIN's "shack unoccupied" check exists precisely because of this), but the LIVE BOT's
parse_grid (botmain.rs ~:190) never inserts '0'/'1' into walkable — both tents are rocks in
every BFS the bot runs (d, farm_d, camp/park, solver landings).

Measured on the replay: BFS (12,4)->(14,4) = 24 steps in the bot's model vs 2 real. Our MOVE
destinations: unit1 9 W<->E treks, unit3 4, all via the y=0 top corridor (side-sequence
compression: Wx39 T Ex7 T Wx22 T Ex7 ...): ~18-22 wasted steps/trek ≈ 200+ troll-turns of
~600 in the game (~1/3 of locomotion). Opponent stayed west (1 trek) and paid nothing.

Fix queued as v1.44.0-tentgap (data/candidates/v1.44.0-tentgap/brief.md): parse_grid adds
'0'/'1' to walkable + two guards (never PLANT on shack — engine allows it; never PARK/idle-
land on shack — blocks TRAIN + it's the door) + fixture-shift discipline for pickloop/
corridor tests that encoded the old walkability. Pure execution waste-cut class (the class
that transfers). Queue position: next build after D2 (v1.43.0-yield, in build now); they
compose (D2 handles the real temporary blocker on the door cell, D4 removes the phantom wall).

## 2026-07-08 19:39 — CORRECTION: tentgap premise disproven; shacks are spawn-only, NOT walkable

The 16:50 "shacks are WALKABLE" conclusion above is **wrong**. Do not implement
`v1.44.0-tentgap` as originally written. Two independent checks resolve the issue:

1. **Official referee source:** `Cell.isWalkable()` is `type == GRASS`; the statement says
   "Only GRASS cells are walkable" and explicitly says trolls cannot walk back onto the shack
   after leaving it. `PlantTask` also rejects non-GRASS cells, so the original "never PLANT on
   shack after making it walkable" guard was compensating for a change the referee does not make.
2. **Live TestSession probe:** scratch bot `rust-scratch/tent_probe.rs` trained a troll, moved
   it off the tent, then ordered it back to the tent. Corrected probe game `895503881`:
   - t1 starter `id=0` starts at `shack=(9,4)` and moves to `(10,4)`.
   - t2 trained troll `id=2` starts at `shack=(9,4)`; starter clears `(10,4)->(11,4)`, and
     `id=2` is ordered to `(10,4)`.
   - t3 `id=2` is at `(10,4)` and receives `MOVE 2 9 4`.
   - t4 `id=2` is still at `(10,4)`, `on_shack=false`.
   Raw artifact: `data/boss5_games/boss/game_895503881.raw`.

An earlier probe game `895503844` repeatedly showed the trained troll stuck on the shack, but
that was a probe-design bug: the starter stayed on the only exit cell, so own-unit collision
prevented the new troll from stepping out. It is not evidence about return-to-shack movement.

**Action:** `data/candidates/v1.44.0-tentgap/brief.md` is now marked REJECTED. Do **not** add
`'0'`/`'1'` to `walkable`; do **not** create `parse_grid_shacks_walkable`; do **not** treat tent
cells as transit cells. The Sasso_Stark long-route observation must be explained as normal
unwalkable-shack geometry or as another movement/planner issue. Active next candidate remains
`v1.43.0-yield`.

## 2026-07-08 21:38 — v1.43.0-yield arena verdict: KEEP / PROMOTED (+1.0)

Builder/gatekeeper summary: D2 task-interference/yield-to-urgent built as `v1.43.0-yield`
with one bounded L2/L3 yield pass. Local gates passed; DEBUG mini-gate was PASS-WATCHLIST:
Boss pool `1/8`, our final wood `42.5`, t300 wood delta `-10.2` (not a crater vs the `-15.3`
baseline), no crashes, and no game had more than one `@TFYIELD` on the same turn. Watchlist:
plcc field probe was harsh (`0/2`, our wood `48`, opp wood `92`).

Arena estimate: bracket read immediately before submit was `127/527 Gold score 17.4`, agentId
`6543636` (`v1.42.0-idlefruit`, read 20:47:11 MSK). Submitted `v1.43.0-yield.min.rs` at
20:47:20 MSK (SUBMIT-OK, submit id `40969224`). Candidate landed as agentId `6543753`.
Read trajectory:

- +20m: `139/527 @16.9` (delta `-0.5`) — initial dip.
- +35m: `116/527 @18.6` (delta `+1.2`) — rebound.
- +50m: `116/527 @18.4` (delta `+1.0`) — policy read.

Verdict: **KEEP / PROMOTED**. Final estimate is **Gold score 18.4**, rank **116/527**, delta
**+1.0** against the chained baseline, meeting measurement policy v2's single-convergence
promotion bar. Left live in the arena slot; `cgauto/api_submit.py` default now points at
`cgauto/submissions/v1.43.0-yield.min.rs`. Goal gate did not fire (`116 > 99`). Full detail:
`data/candidates/v1.43.0-yield/report.md`.

Follow-up mechanism note from user replay review: the next high-value inefficiency appears to
be tree-resource compatibility, not the yield mechanism itself. A gatherer can ignore a nearby
ripe apple and walk to a farther apple because the chopper claims the near tree as a fell target;
the matcher treats `HARVEST tree_cell` and `CHOP/MoveTo tree_cell` as the same exclusive
`target: Some(cell)`. Candidate direction: harvest-before-fell / split fruit-vs-wood tree
claims, so a gatherer can harvest a ripe nearby tree before the chopper fells it later.

## 2026-07-08 22:49 — v1.44.0-harvest-before-fell arena verdict: REJECT / REVERTED (−2.6)

Built the user-observed tree-resource compatibility candidate as `v1.44.0-harvest-before-fell`.
Mechanism: wood-capable trolls skip a ripe tree if a free-capacity gatherer can harvest it within
two turns and the fruit is non-idle work (funding fruit, seed/printer fruit, or Hoard wallet
fruit). Explicit exceptions preserve urgent wood behavior: no protection in liquidation, no
protection under nearby enemy chopper pressure, no protection when the wood worker already stands
on the tree, and ordinary idle fruit remains unprotected.

Local tests: new `harvest_before_fell` suite has three pins (near water-apple gatherer beats
chopper claim; adjacent enemy chopper keeps the tree fellable; ordinary idle fruit does not
protect a tree from felling). Full release suite green (`61 passed / 7 ignored`), bundle/minified
equality green, minified size `59684` bytes.

Mini-gate had an important iteration:

- Broad first version protected all nearby ripe fruit, including idle-fruit band 38. Boss 8 failed:
  `0/8`, our wood `40`, opp wood `58`, t300 delta `-17.8`. Rejected locally.
- Narrowed version protected only funding/printer/Hoard fruit. Boss 8 recovered: `2/8`, our wood
  `41.6`, opp wood `51.4`, t300 delta `-9.8`. Field: plcc `1/2`, our wood `50`, opp wood `38`;
  mikdiet `0/2`, our wood `84`, opp wood `96` (mixed, not a wood crater).

Arena bracket before submit: `v1.43.0-yield` at `116/527 @18.4`, agentId `6543753` (read
22:13 MSK). Submitted `v1.44.0-harvest-before-fell.min.rs` at 22:13 (SUBMIT-OK, submit id
`40969606`). Candidate landed as agentId `6543779`.

Read trajectory:

- +20m: `136/527 @16.9` (delta `-1.5`).
- +35m: `182/527 @15.8` (delta `-2.6`).

Verdict: **REJECT / REVERTED**. The candidate does not improve Gold arena rating; it damages the
live field despite the acceptable narrowed mini-gate. Reverted immediately to
`cgauto/submissions/v1.43.0-yield.min.rs` at 22:49 (SUBMIT-OK, submit id `40969730`). Restore
landed as agentId `6543791` by the 23:11 read (`180/527 @16.0`, early reconvergence), confirming
the rejected v1.44 agentId `6543779` was no longer live. Do not retry this as simple ripe-tree
fell suppression; any future tree-resource compatibility work needs a different mechanism, likely
explicit timing/role scheduling rather than hiding wood candidates. Full detail:
`data/candidates/v1.44.0-harvest-before-fell/report.md`.

## 2026-07-08 23:39 — v1.45.0-earlyroam local verdict: REJECT / NOT SUBMITTED

Built the burst-chopper follow-up as `v1.45.0-earlyroam`. Mechanism: during Tempo turns `<=75`,
only the true chopper gets one extra primary-fell farm-distance roam ring and a one-cell own-half
tolerance. Starter chop-help and anti-starvation fallback remain champion behavior.

Local code gates were clean:

- `cargo test --release --test early_roam`: `3 passed`.
- `cargo test --release`: all active tests passed.
- self, bundled, and minified equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- minified source size: `57515` bytes.

Boss DEBUG mini-gate rejected it:

- Boss 8: `0/8 wins | our wood 40 | opp wood 53`.
- Formal ramp: t75 `+3.2`, t150 `+1.8`, t225 `-4.6`, t300 `-13.4`.
- Aggregate: wins `0/8 (0%)`, our avg final wood `39.9`, late gain us `+11.6` vs boss `+20.4`.

Interpretation: the feature does what it was designed to do early, but that is not enough. It
starts ahead through t150, then loses the late burst from t225 onward. Static turn-gated roam
widening is closed and was not submitted to the arena. If this family is revisited, it should be
with an observed-opponent trigger or a different resource plan, not unconditional opening roam.
Full detail: `data/candidates/v1.45.0-earlyroam/report.md`.

## 2026-07-09 00:47 — v1.46.0-splitclaims arena verdict: KEEP / NOT PROMOTED (+0.9)

Built the user-requested split fruit-vs-wood tree claim mechanism as `v1.46.0-splitclaims`.
The matcher now classifies assigned targets as `Fruit`, `Wood`, or ordinary `Cell`. Same-resource
claims still conflict. A fruit claim and wood claim on the same tree are compatible only if the
fruit worker's ETA is strictly smaller than the wood worker's ETA, avoiding equal-ETA movement
fights and avoiding v1.44's failed fell suppression.

Local gates:

- `cargo test --release --test split_tree_claims`: `3 passed`.
- `cargo test --release`: all active tests passed.
- self, bundled, and minified equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- minified source size: `58814` bytes.

Mini-gate:

- Boss 8: `1/8 wins | our wood 44 | opp wood 60`.
- Formal ramp: t75 `+2.8`, t150 `+1.5`, t225 `-6.5`, t300 `-15.9`.
- plcc (`6480966`): `0/2 wins | our wood 62 | opp wood 92` (still loses, but our wood is above
  the v1.43 watchlist probe's `48`).
- mikdiet (`6480914`): `2/2 wins | our wood 72 | opp wood 26`.

Verdict before arena: **PASS-WATCHLIST**. The Boss gate is not clean, but the candidate directly
addresses the observed nearby-apple contention and field probes did not crater.

Arena bracket before submit: restored `v1.43.0-yield` agentId `6543791` at `151/527 @16.5`
(`2026-07-08 23:55 MSK`). Submitted `cgauto/submissions/v1.46.0-splitclaims.min.rs` at
`2026-07-08 23:56 MSK` (SUBMIT-OK, submit id `40969964`). Candidate landed as agentId
`6543815`.

Read trajectory:

- Landing check: `371/527 @11.7` (delta `-4.8`) — severe early dip.
- +20m: `169/527 @16.3` (delta `-0.2`) — recovered inside the inconclusive band.
- +35m: `127/527 @17.4` (delta `+0.9`) — KEEP signal.
- +50m: `127/527 @17.4` (delta `+0.9`) — policy read.

Verdict: **KEEP / NOT PROMOTED**. The final delta `+0.9` crosses the v2 KEEP bar but misses the
single-read promotion bar (`+1.0`). Left live as the chained baseline for the next candidate;
`cgauto/api_submit.py` default stays on `cgauto/submissions/v1.43.0-yield.min.rs`. Goal gate did
not fire (`127 > 99`). Full detail: `data/candidates/v1.46.0-splitclaims/report.md`.

## 2026-07-09 01:13 — v1.47.0-ripefund local verdict: REJECT / NOT SUBMITTED

Built D3 funding-stall robustness as `v1.47.0-ripefund`. The idea was chopper-funding
ripeness anticipation: while the second troll was still pending, let the starter pre-position
for soon-ripe deficit PLUM/LEMON/APPLE instead of waiting until funding fruit is already ripe.

Two variants were tried:

- Broad band-57 anticipation: any soon-ripe chopper-funding fruit, below already-ripe funding
  band 58 and above printer work.
- Narrowed final-missing-fruit form: only when one harvest would complete the chopper fruit
  wallet and all other fruit costs were already covered. This is the frozen artifact.

Code gates for the narrowed artifact were clean: focused tests, full release suite, self
equality, bundled equality, and minified equality all passed. Minified size was `61761` bytes.

Mini-gate results rejected both variants:

- Broad form Boss 8: `1/8`, our wood `47`, opp wood `60`, ramp t300 `-13.5`.
- Broad form field probes: `6480966` `0/1`, wood `48-83` (one HTTP 422); `6480914` `0/2`,
  wood `34-52`.
- Narrowed frozen form Boss 8: `1/8`, our wood `44`, opp wood `62`, ramp t300 `-18.1`.
- Narrowed field probes: `6480966` `0/1`, wood `78-107` (one HTTP 422); `6480914` `0/1`,
  wood `62-106` (one HTTP 422).

Verdict: **LOCAL REJECT / NOT SUBMITTED**. Simple chopper-funding ripeness anticipation is closed:
it worsens production-heavy field probes and does not produce a Boss lift over v1.46. Active
source was restored to `v1.46.0-splitclaims`; the arena slot was not touched. Full detail:
`data/candidates/v1.47.0-ripefund/report.md`.

## 2026-07-09 01:45 — v1.48.0-localprinter local verdict: REJECT / NOT SUBMITTED

Before building, the live rank was still `127/527 @17.4`, and the rank-99 gate remained around
Gold score `20.1`. A new reusable analyzer, `cgauto/battle_taxonomy.py`, was added to make the
command-count loss decode reproducible from recent arena `gameResult` frames. On the last 80
finished games filtered to opponent ranks 100-150, the live bot was `24/49` with avg score
`194-195` and wood `44.8-43.8`. Losses showed the same throughput shape as the earlier ad hoc
decode: our TRAIN stayed `1.0`, opponent TRAIN `2.2`; our CHOP `92.1` vs opponent `149.7`;
our HARVEST `17.4` vs `47.8`; our DROP `26.4` vs `68.7`.

Built `v1.48.0-localprinter` as a narrow response to starter/printer travel waste. Mechanism:
restrict premium printer band 52 to ripe banana / water-adjacent apple sources inside the farm
ring (`farm_d <= farm_r`), while leaving distant fruit harvestable through the existing lower
idle-fruit band 38. The candidate was built and frozen; code gates were clean:

- Focused suites: `nanaflow` `4 passed`, `split_tree_claims` `3 passed`, `idlefruit` `3 passed`.
- Full release suite passed.
- Self, bundled, and minified equality each returned `EQUAL: 16 games`.
- DEBUG smoke equality returned `EQUAL: 4 games`.
- Minified size: `59759` bytes.

Mini-gate rejected it:

- Boss 8: `2/8`, our wood `41.2`, boss wood `54.6`; ramp t75 `+4.5`, t150 `+3.1`, t225 `-4.5`,
  t300 `-13.4`.
- mikdiet (`6480914`): `1/2`, wood `72-51`, worse than v1.46's `2/2`, wood `72-26`.
- plcc (`6480966`): `0/1`, wood `72-117`.

Verdict: **LOCAL REJECT / NOT SUBMITTED.** The change did not crater the Boss probe, but it
worsened a production-heavy field probe and failed the rank-95 gatekeeper. Simple local-only
premium printer demotion is closed. Active source was restored to `v1.46.0-splitclaims`; restore
checks passed (`cargo test --release`, self equality `EQUAL: 16 games`). Full detail:
`data/candidates/v1.48.0-localprinter/report.md`.

## 2026-07-09 01:57 — v1.49.0-farmhand local verdict: REJECT / NOT SUBMITTED

Built the remaining obvious workforce lever as `v1.49.0-farmhand`: re-arm
`GE_MAX_TROLLS` from 2 to 3, but avoid v1.35.0-thand's tourist failure by role-filtering the
third pure gatherer. Only a troll with `plan.n >= 3`, `chop_power == 0`, and
`harvest_power > 0` was treated as the farmhand; for that role only, printer band 52 and
idle-fruit band 38 required `farm_d <= farm_r`. Starter behavior stayed at v1.46 semantics.

Code gates were clean:

- `cargo test --release --test tactics_scale`: `7 passed`, with old T-hand tests re-enabled.
- `cargo test --release`: all active tests passed.
- self equality: `EQUAL: 16 games`.
- bundled equality: `EQUAL: 16 games`.
- minified equality: `EQUAL: 16 games`.
- minified size: `59973` bytes; DEBUG minified size: `59972` bytes.

Boss 8 DEBUG rejected the candidate:

- `0/8` wins.
- Final wood `46.4-63.8`.
- Ramp t75 `+3.1`, t150 `+1.0`, t225 `-5.0`, t300 `-17.4`.
- Late quarter: us `+11.5`, boss `+23.9`.

The mechanism engaged: DEBUG `@TFFARM` summaries reached `n=3` in 7/8 games, first at
t85/t85/t115/t140/t145/t150/t175 depending on the seed, and final build summaries showed the
added hand as `1.1.1.0`. It still did not repay its bill or close the late wood-ramp gap. The
stored ramp baseline for this gate was `14%` wins, final wood `38.7`, t300 delta `-15.3`, so
v1.49 improved own wood but worsened the score shape.

Verdict: **LOCAL REJECT / NOT SUBMITTED.** Do not retry simple farm-ring-restricted cheap third
hand. If extra workforce comes back, it needs a materially different role or late-ramp plan.
Active source was restored to `v1.46.0-splitclaims`; restore checks passed (`cargo test
--release`, equality against frozen `v1.46.0-splitclaims.min.rs`: `EQUAL: 16 games`). Arena was
not touched. Full detail: `data/candidates/v1.49.0-farmhand/report.md`.

## 2026-07-09 02:21 — v1.50.1-latethreat local verdict: REJECT / NOT SUBMITTED

Built an observed-trigger answer to the late raid problem. Broad `v1.50.0-threatfell` gave the
chopper a band-71 emergency own-half fell candidate whenever an enemy wood-capable troll was
within Manhattan distance 2 of a fellable own-half tree. It did not change training or global
roam. Because field probes showed the broad trigger was too loose, it was narrowed to
`v1.50.1-latethreat` by adding `state.turn >= 150`.

Code gates for the narrowed form were clean:

- `cargo test --release --test threatfell`: `4 passed`.
- `cargo test --release`: all active tests passed.
- self, bundled, and minified equality: `EQUAL: 16 games`.
- minified size: `60930` bytes; DEBUG minified size: `60929` bytes.

Broad form result:

- Boss 8: `2/8`, final wood `40.8-48.8`, t300 `-8.0`, late gain us `+10.5`, boss `+17.6`.
- Field: `mikdiet` `1/2`, wood `40-41`; `plcc` `0/2`, wood `85-134`.

Narrowed form result:

- Boss 8: `2/8`, final wood `46.9-59.6`, t300 `-12.8`, late gain us `+11.2`, boss `+17.5`.
- Field: `mikdiet` `2/2`, wood `68-60`; `plcc` `0/2`, wood `30-77`, including one `18-97`
  blowout.

Verdict: **LOCAL REJECT / NOT SUBMITTED.** The mechanism can reduce Boss late gain, but it is not
field-safe; simple enemy-near-tree emergency fell priority pulls the chopper into bad work against
at least one rank-gate production opponent. Future late-raid work needs stronger selectivity tied
to actual cross-half raid economics, not just proximity. Active source was restored to
`v1.46.0-splitclaims`; restore checks passed (`cargo test --release`, equality against frozen
`v1.46.0-splitclaims.min.rs`: `EQUAL: 16 games`). Arena was not touched. Full detail:
`data/candidates/v1.50.1-latethreat/report.md`.

## 2026-07-09 — v1.51 standing-claim line local verdict: REJECT / NOT SUBMITTED

Postmortem on the `v1.50.1-latethreat` `plcc` blowout found a different root cause than the
late-threat rule itself. The severe `18-97` loss had `91/265` blocked intended moves (`34.3%`);
chopper `id=2` sat at `(2,7)` repeatedly trying to enter `(2,6)` while starter/gatherer `id=0`
stood on `(2,6)` harvesting fruit. Better `plcc` games were normally `0-7` blocks, not ~90.

Two standing-claim fixes were built:

- `v1.51.0-standclaim`: same-tree fruit-vs-wood claims conflict whenever the fruit claimant is
  already standing on the tree. It fixed the block rate (`plcc` new games `3.1%` and `1.4%`) and
  Boss 8 looked watchlist-positive (`1/8`, wood `47.4-56.1`, t300 `-8.8`), but field probes were
  mixed: `plcc` `0/2`, wood `74-106`; `mikdiet` `1/2`, wood `75-65`. The matcher often moved the
  fruit worker away so the chopper could take the cell, which looked too wood-biased.
- `v1.51.1-fruitstand`: narrower rule; wood candidates skip only a ripe tree currently occupied
  by our own harvest-capable fruit worker. It removed the `plcc` block pattern completely
  (`0.0%` and `0.5%`), but did not improve score: Boss 8 `0/8`, wood `48.1-59.1`, t300 `-11.0`;
  `plcc` `0/2`, wood `60-91`; `mikdiet` `0/2`, wood `80-92`.

Verdict: **LOCAL REJECT / NOT SUBMITTED.** The standing fruit-vs-wood occupancy bug is real, but
simple claim exclusivity is not a profitable rank push. Do not requeue this mechanism as a
standalone fix. Active source was restored to `v1.46.0-splitclaims`; restore checks passed
(`cargo test --release`, equality against frozen `v1.46.0-splitclaims.min.rs`: `EQUAL: 16
games`). Arena was not touched. Full detail:
`data/candidates/v1.51.1-fruitstand/report.md`.

## 2026-07-09 — phase-binned live loss taxonomy after v1.51 rejection

Extended `cgauto/battle_taxonomy.py` to bin command counts by inferred turn phase
(`t001-075`, `t076-150`, `t151-225`, `t226-300`). Current live arena state remains
`v1.46.0-splitclaims`, rank `127/527 Gold @17.4`, agentId `6543815`.

Read: `uv run --no-sync python cgauto/battle_taxonomy.py 100 80 150`.

Across 49 recent finished games against opponent ranks 80-150, selected sample stayed `24/49`
with avg score `194-195` and wood `44.8-43.8`. Losses were `0/25`, score `192-235`, wood
`44.7-53.4`.

The phase split makes the next direction sharper:

| phase | CHOP us | CHOP opp | delta | key extra opponent gaps |
|---|---:|---:|---:|---|
| t001-075 | 28.6 | 15.1 | **-13.5 opp-us** | opp +0.4 TRAIN, +6.2 HARVEST, +7.6 DROP |
| t076-150 | 28.8 | 40.9 | +12.1 | opp +0.6 TRAIN, +12.1 HARVEST, +12.7 DROP |
| t151-225 | 22.8 | 58.4 | **+35.6** | opp +13.0 DROP, +6.7 PICK, +3.0 PLANT |
| t226-300 | 11.9 | 35.3 | **+23.4** | opp +8.9 DROP, +5.5 PICK, +5.4 PLANT |

Interpretation: the opening is not the failing phase; in losses we still out-chop the field by
turn 75. The gap opens from turn 76 and becomes decisive after turn 150. Opponents are not just
raiding one tree; they run a sustained late production loop with more CHOP plus supporting
PICK/PLANT/DROP. This matches the older "late-throughput ceiling" and seed/farm-supply notes.

Next candidate should target late wood production/farm supply from t150 onward, with field probes
including `plcc`, `mikdiet`, and one of `kurigen`/`Dasein8`. Avoid another opening-roam,
standing-claim, or simple third-hand retread unless it directly changes t151-300 production.

## 2026-07-09 — v1.52 late seed-home candidate rejected / reverted

Built `v1.52.0-lateseedhome` from the phase-binned finding above. DEBUG Tempo replays had many
late turns with `farm=0` while banked banana seeds remained in the tent; the starter still chose
remote ripe seed trees because printer tree-first band 52 outranked tent PICK/Park band 50.

Change: keep early tree-first intact, but after t150 under live Tempo, when `base_trees < 2`,
banked bananas exist, and a plantable cell exists, raise tent PICK/Park to band 54. No third
troll, no roam change, no global printer demotion.

Gates passed: focused `lateseedhome` test, full release suite, bundled equality, minified
equality. Minified size `59968` bytes.

Local gate:

| probe | candidate | direct v1.46 comparison |
|---|---:|---:|
| Boss 8 | `1/8`, wood `47.9-55.1`, t300 `-7.2` | stored baseline line `-15.3`; older v1.51 t300 `-11.0` |
| plcc | `1/2`, score `232-279`, wood `56-68` | `1/2`, score `250-193`, wood `56-44` |
| mikdiet | `1/2`, score `202-204`, wood `48-48` | `1/2`, score `175-167`, wood `38-26` |
| kurigen | `1/2`, score `299-232`, wood `69-55` | `0/2`, score `273-346`, wood `63-86` |
| field aggregate | `3/6`, score `244.3-238.0`, wood `57.8-57.0` | `2/6`, score `232.7-235.2`, wood `52.3-52.5` |

Verdict: arena-worthy locally, but arena-rejected. It fixed the measured middle-late farm
starvation shape and beat the direct six-game field aggregate, but `plcc` worsened on opponent
wood and the live field punished it.

Submitted explicitly from `cgauto/submissions/v1.52.0-lateseedhome.min.rs` at bracket
`v1.46.0-splitclaims` `127/527 @17.4`, agentId `6543815`. Submit id `40970510`; landed as
agentId `6543941`. Arena reads: `521/527 @0.0`, `426/527 @10.7`, `261/527 @13.9`,
`226/527 @15.1`, `211/527 @15.3`, `180/528 @15.9`, `172/528 @16.2`. Final delta was `-1.2`,
past the v2 revert bar.

Reverted to prior live baseline `cgauto/submissions/v1.46.0-splitclaims.min.rs` (submit id
`40971048`), landed as agentId `6544763` with first fresh-low read `256/528 @14.2`. Active
source restored to `v1.46.0-splitclaims`; full release suite passed and the restored release bot
equals frozen v1.46 over `EQUAL: 16 games`. `lateseedhome` tests are parked with `#[ignore]`.
`api_submit.py` default remains `v1.43.0-yield.min.rs`.

## 2026-07-09 11:40 — chain-end champion restore + working tree committed (controller)

Two housekeeping fixes after inheriting the parallel Opus session's uncommitted state:

1. **Committed the working tree** (was ~60 modified + 56 untracked work files, HEAD stuck at
   49fb8da). Verified first: `cargo test --release` exit 0 (all suites green, incl. yield_pass
   3/3). Two commits: a0de498 (champion source v1.43-yield + v1.46-splitclaims + ownership.rs +
   tests) and 9b51ddd (submissions v1.43-v1.52, tools, verdict docs, ownership design). Added
   /target, rust-scratch/, data/boss5_games/ to .gitignore (build/debug output).

2. **Restored the champion to the arena slot.** Live occupant was the post-lateseedhome-revert
   v1.46.0-splitclaims cold-start (agentId 6544763), STALLED at 212/528 @ 15.3 across 3 reads /
   ~25 min (not reconverging to its 17.4 KEEP level — room drift ~2pt low + incomplete cold
   start, not a regression: splitclaims passes cargo test and its +0.9 gate). The candidate
   chain has ended (pivot to the ownership diagnostic — no more submissions), so per policy v2
   ("champion returns to the slot at chain end") resubmitted the promoted champion
   v1.43.0-yield (submit id 40971679, SUBMIT-OK). splitclaims' +0.9 was single-convergence
   (noise ±1), never met the +1.0/2×+0.5 promotion bar → yield stays the confident champion.
   Convergence read pending (~+50m). Best rank remains 116; goal (≤99 twice) not reached.
