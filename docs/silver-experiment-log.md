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
