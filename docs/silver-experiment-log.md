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
Loss decomposition vs scriptboss (400 seeds): 30% both-seat + 18% one-seat (vs 15/15 on
silverboss) — the systematic pool is BIGGER vs the real script, so the "~66% ceiling"
claim was model-specific; headroom exists but the obvious knobs are exhausted.
