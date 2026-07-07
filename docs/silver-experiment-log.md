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
