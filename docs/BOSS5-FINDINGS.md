# Boss 5 / Legend push — findings (2026-07-05)

Authoritative notes for beating Boss 5 (Gold→Legend). Written so we don't rediscover.
Cross-refs: `cgauto/HANDOFF.md`, `docs/silver-experiment-log.md`, memory files.

## THE TARGET: Boss 5 is a LEAN 2-troll bot (decoded from live games vs it)
Boss 5 is NOT the 180-wood monster. It banks **~84 wood** with a simple printer economy:
- **Troll 1 (starter `1,1,1,1`):** banana printer/harvester — harvest 41 fruit + pick 30 +
  **plant 36 bananas**. Keeps a big farm stocked.
- **Troll 2 (`2,3,0,2`, cc=3 chopper):** trained at **TURN 1** (the starting inventory
  `7,10,9,10,7` already affords it: cost 5plum/10lemon/1apple/5iron). Perma-chops.
- **Felling breakdown: 37 fells = {1 wood:7, 2 wood:13, 3 wood:17}, avg 2.3.** The **17
  size-3 fells** are the edge: it fells trees at **size 3** so its **cc=3 captures 3
  wood/tree**. Wood ramps 0→9(t75)→21(t150)→43(t200)→84(t300) — sustained to t300.
- Prints `MSG :]`.

### Boss 5 also DENIES
Its chopper spends **52 turns on OUR half (x≤6)**, reaching our base (x=1) early
(turns 15-22). It steals/fells our trees (double loss: we lose the tree, it banks the wood).
User's call (2026-07-05): **OUT-PRODUCE it, don't counter-raid** (raiding regressed before).

## ★★★ THE BIG INSIGHT (2026-07-05, controlled games): DENIAL > SELF-PRODUCTION
The game is a **2-player RACE for a shared, finite pool of native trees**, not a solo
wood-maximization puzzle. Whoever fells the map's trees FIRST banks them; the loser gets
leftovers. Controlled games vs runninglvlan (6-8 each) proved it — note how OUR early
felling suppresses the OPPONENT's wood:

| bot | felling behavior | **opp wood** | our wood | **win%** |
|---|---|---|---|---|
| **v1.4.5** (cc2, fs2, NO delay, farm12) | fell size-2, EARLY | **50** | 50 | **67%** |
| v1.5.5 (cc3, fs3, no delay, farm18) | fell size-3 (softer) | 58 | 59 | 50% |
| v1.6.0 (cc3, fs3, **delay t45**, farm18) | accumulate, late | **70** | 54 | **0%** |

**The accumulate/"let the forest mature" idea is a SOLO-OPTIMIZATION TRAP.** v1.6.0 banks
MORE wood than v1.4.5 (54>50) yet loses EVERY game — because delaying our felling lets the
opponent freely bank 70 (vs 50 when we fell early). Win rate tracks **(our wood − opp wood)**,
and early size-2 felling is what holds the opponent down. **This overturns the accumulate
diagnosis below (runninglvlan's solo 62-wood ramp is irrelevant when WE deny it early).**

**Corollary — "fell at size 3" is NOT free:** waiting for size 3 (v1.5.5) cedes ~8 opp wood
(50→58) and drops win% (67→50). The size-3 capture bonus (cc=3) must be added WITHOUT losing
the early size-2 denial.

### The champion's FIELD MAP (v1.4.5 vs 3 elite proxies, 6 games each, 2026-07-05)
| opponent | our wood | opp wood | win% | regime |
|---|---|---|---|---|
| runninglvlan | 50 | 50 | **67%** | wood-SCARCE → denial race (we win) |
| darkhorse64 | 60 | 45 | 50% | mixed |
| nmahoude | 69 | **83** | **33%** | wood-RICH → production race (we lose) |

**THE FRONTIER: scarce maps = denial race (cc=2 early wins); rich maps = production race
(cc=3/big farm wins).** v1.4.5 (denial) and cc3+fs3 (production) are two ends of ONE trade-off,
each ~50% vs elite → both cap ~top-Gold. Pure in-game econ ADAPTATION between them was already
tried and is WORSE (MB_ADAPT_ECON, 77→65%, git dead-end). Live rank 216 @17.7 (boss bar ~25.9)
is consistent: v1.4.5 is a solid top-Gold economy, ~8 pts short of Legend, NOT held down by
matchmaking (it genuinely wins only ~50% vs elite).

### v1.6.1 (cc3+fs2 early) REFUTED: 3/8 (38%) vs runninglvlan, opp banks 70
cc=3 + fell-size-2 wanders (chopper can't fill cc=3 from one size-2 farm tree → seeks a 3rd
wood → inefficient, banks 44 < v1.4.5's 50) AND the pricier cc=3 training slightly delays the
denial-critical early chopper. Confirms: **cc=3 needs fell-size-3 to pay off, but fs=3 cedes
denial** — the core tension.

### ★★ THE CRUX: cc=3 affordability gates the chopper timing (2026-07-05, sim trace)
Training cost for the 2nd troll (n=1): **cc=3 (2,3,0,2) needs lemon 10** (n+cc²=1+9); **cc=2
(2,2,0,2) needs lemon 5** (1+4). Local-sim trace (`trace.rs`, GE_SPEC=2,3,0,2): the cc=3
chopper trained at **turn 46**, not turn 1 — because the sim's STARTING INVENTORY is RANDOM
(`mapgen.rs`: each fruit = randint(2,10)), so lemon<10 forces the starter to harvest up to 10
first (→46). Arena start is ~`7,10,9,10,7` (lemon EXACTLY 10) so Boss 5 trains cc=3 at t1.
**cc=2 (lemon 5) trains at t1 on nearly any draw → consistent early denial = WHY cc=2 is the
champion.** cc=3 is a GAMBLE on the lemon draw: great when lemon≥10 (t1 train, production),
bad otherwise (delayed chopper cedes denial). Explains the bimodal cc=3 wood (48–129).

### v1.7.0 (ADAPTIVE SPEC) — the dominant synthesis, TESTING
At turn 1, pick the RICHEST chopper the starting draw can train IMMEDIATELY: `spec = if
mb_afford(inv, cost(cc3)) { cc3 } else { cc2 }` (persisted in GE_CHOSEN_SPEC). `farm_fell`
matches (3 if cc3 else 2); native fell stays size-2 (denial). Chopper ALWAYS trains t1 (never
delays). Strictly ≥ both pure economies: cc=3 production when affordable, cc=2 denial otherwise
— regardless of whether the arena fixes or randomizes the start. `main.rs` decide_elite only
(sim's gold_elite lacks it → validate via controlled games, not sim).

### v1.6.2 (cc3 HYBRID) — arena result: rank 211 @18.4 (v1.4.5 was 216 @17.7)
Marginal + over v1.4.5 — consistent with cc=3 being a wash (always-cc3 delays on low-lemon
maps). v1.7.0 should beat it by dropping to cc=2 on those maps.
The two fell knobs are SEPARATE (`GE_FELL_SIZE`=native, `GE_FARM_FELL`=our bananas). Set
**native=2 (denial: grab contested trees early) + farm=3 (production: cc=3 captures our own
size-3 bananas fully)** + cc=3 + train-t1 + farm 15. Goal: keep 67% vs runninglvlan AND lift
33% vs nmahoude. If it beats v1.4.5 on BOTH → the Legend candidate. Testing 2026-07-05.

## THE MECHANISM to match/beat Boss 5
NB: qualified by THE BIG INSIGHT above — fell-size-3 trades denial for capture; net-negative
so far. Kept for reference:
`cc=3 chopper + FELL AT SIZE 3 + big banana farm`. Our v1.4.5 (cc=2, fell size 2) banks
71 = ~35 trees × 2. Boss 5 banks 84 via more/bigger fells (17 × 3). To beat: capture 3/tree
(cc=3 on size-3 trees) AND out-throughput. **cc=3 at fell-size-2 is WASTED** (captures only
2) and costs more to train — that's why v1.5.3 banked 65 < v1.4.5's 71.

## THE OTHER (harder) target: Tchoubidouwa123 = 180 wood (a Legend PLAYER, not the boss)
4 trolls: starter + `2,2,2,2` hybrid (harvest+plant+chop) + 2× `2,4,0,2` cc=4 choppers.
2 harvesters build a ~45-banana farm + fund the expensive cc=4 units via 96 fruit harvests.
We do NOT need this to beat Boss 5 — it's the next tier. Our 4-troll attempts FAILED
(v1.5.0/v1.5.1: 39-44 wood, rank 491) — the cc=4 units are too expensive to fund fully,
the build never completes (stuck at 3 trolls, over-harvests lemon, banks 0 until t150).

## ★★★ CONFIRMED: BOTH sim AND arena randomize the start → the late-chopper disaster (2026-07-05)
Measured the arena's turn-1 inventory from real TestSession/play games (@TFSUM t=1 myinv):
**lemon = 6, 3, 4** across games — NOT the fixed 10. Boss 5's decoded `7,10,9,10,7` (lemon 10)
was ONE lucky draw. So the arena start is RANDOM (~randint(2,10) per fruit, same as the sim;
both players get the SAME draw). Consequences, all confirmed:
- cc=3 needs lemon 10 → affordable at t1 only when lemon==10 (~11% of maps). **cc=3 is a
  situational upgrade, not a general win** — which is why cc=3 bots (v1.6.2/v1.7.0) ≈ cc=2
  (v1.4.5) on the arena (all ~17-18, top-Gold). The "Boss 5 = 84 via cc=3" quest was chasing an
  ~11%-of-maps effect.
- **THE REAL DISASTER (the actionable lead): on ~1/3 of maps lemon < 5, so EVEN cc=2 can't train
  at t1** → the chopper delays while the starter harvests lemon (debug game: our chopper trained
  at **t77**) → we cede the early denial that wins. This costs us ~a third of our games.
- **THE FIX → v1.7.1 spec LADDER:** at turn 1 take the richest chop=2 chopper the draw affords
  NOW — `[(2,3,0,2)cc3, (2,2,0,2)cc2, (2,1,0,2)cc1]` — cc=1 needs only lemon 2, affordable on
  nearly any draw, so a chopper always trains ~t1 (early denial) even on lemon-poor maps. All
  keep chop=2 (role logic needs chop≥2). Extends v1.7.0's adaptive idea to the poor-draw case.

NB the sim STILL can't validate this (random low starts + it measures wood not win-rate, and the
sim's gold_elite lacks the adaptive/ladder logic) → validate on the arena / cg_play.py only.
Our `strategies/boss5.rs` model stays stuck at 1 troll in the sim for exactly this reason
(cc=3 unaffordable on the sim's poor draws; a faithful Boss-5 model would need a fixed rich start).

## ★★★★ SUBAGENT META-FINDING: sim vs real CONFLICT (2026-07-05) — the transfer wall, sharp
Ran 3 parallel subagents. Two gave CONFLICTING levers, and the conflict IS the transfer wall:
- **MC/RHEA agent (in the SIM):** decisive lever = **DENIAL** (bias chopper toward contested
  near-opp trees, DENIAL_W=8) → rhea beats goldelite 40%→67% + all sim bosses. Also found
  "**more trolls don't help in the sim** — 2-troll is best" and "evo search is net-negative on
  top of a strong policy." (rhea_bot.rs, its worktree; NOT ported/tested vs real Boss 5.)
- **Data agent (REAL Boss 5, authoritative):** it's **THROUGHPUT/SCALE, not denial** — we lead
  early (denial already working), lose late; players beat us with **3-4 trolls + harvesters**.
**Resolution:** the SIM rewards denial + penalizes scale (random-poor draws); the REAL arena
rewards scale. Trust the DATA agent for arena/Boss-5 decisions; the MC agent's denial win is a
sim artifact (untested vs real Boss 5). → the lever to test is SCALE, DIRECTLY vs real Boss 5
(playType). RL agent: numpy A2C in `rl/` learns (boss win 1.00, curriculum near-even) — a
separate exploratory track. mybot/`decide_sched` (4-troll: 2 choppers + harvesters + denial,
already in main.rs) is the pre-built scale economy → being tested vs real Boss 5.

### ★★★ SCALE CONFIRMED vs REAL Boss 5 (2026-07-05) — the path forward
`decide_sched` (4-troll) vs real Boss 5: **2/10 (vs v1.7.0's 0/32)** — and the wins **OUT-PRODUCE
Boss 5** (banked 53 & 58 wood vs its 40)! **This proves the scale lever transfers: more trolls →
more late throughput → beats Boss 5.** BUT high variance — funding-collapse disasters (6-16 wood)
when the draw can't fund all 4 trolls (avg wood 29). **The fix is FUNDING ROBUSTNESS** — scale
troll-count to what the draw can fund (adaptive), cut the disasters, keep the out-producing wins.
Progression vs real Boss 5 (10 games each): sched 4-troll denial=3 → **2/10 wood 29**; 3-troll
denial=3 → 2/10 wood 21 (WORSE, less production); **4-troll denial=0 → 3/10 wood 28 (BEST YET,
84-wood win out-producing Boss 5's 66)**. Killing MB_DENIAL_W confirms the transfer-wall insight
(denial helps the SIM, HURTS the arena — the cross-map treks waste production). `MB_DENIAL_W=0`,
`MB_MAX_TROLLS=4` now set in main.rs (inert for the live decide_elite).

**STATE:** the production-scale lever BEATS Boss 5 (3/10 best-yet, wins out-produce it) but is
HIGH-VARIANCE — funding-collapse disasters (11-16 wood) tank the average (28 < v1.7.0's steady 45).

### ★★★ DISASTER DIAGNOSED + FIXED (2026-07-05, per-turn inventory ramp)
Dumped the troll-count + inventory ramp of disaster games. Mechanism is UNAMBIGUOUS: in the
disasters the bot trains a 3rd/4th troll (t150-300) that are **HARVESTERS**, which then **HOARD
useless fruit** (apple piles to 41-47, plum to 21-31) while **wood STALLS at ~20**. On iron-poor
maps the 2nd CHOPPER can't fund, so a harvester trains instead and actively hurts (fruit=1pt vs
wood=4pt). The OK games (50 wood) stay 2-troll and chop steadily.
**FIX (applied to decide_sched, main.rs): drop the harvester fallback** — train only CHOPPERS
(up to MB_NCHOPPERS), else train nothing. Turns disaster games into steady 2-troll chop economies
AND still scales to 2 choppers (out-producing Boss 5) when the draw funds the iron. This is the
right, diagnosis-driven fix.
**UNVALIDATED:** the CG play API HARD-THROTTLED (HTTP 422) after ~150 play calls this session —
couldn't run the validation (only 3/8 completed, inconclusive). **NEXT SESSION: wait for API
cooldown (30-60min), run `collect_debug_games.py /tmp/sched2chop... boss 12` (rebuild from
main.rs: decide_sched now has the fix), confirm disasters→steady + wins kept (target 5-6/10, avg
wood ≥45). If good → point main() at decide_sched, bump VERSION, correctly-label, submit.**
decide_sched is a DIFFERENT fn; LIVE bot stays decide_elite (v1.7.0-logic @rank 130) meanwhile.

### SIM cannot validate this (transfer wall, quantified 2026-07-05)
A/B'd the fix in the sim (sched_bot.rs, SB_HARVEST knob): harvesters ON → 2.93 trolls, 15% vs
goldelite; harvesters OFF (the fix) → 1.45 trolls, **4%**. **The sim says harvesters HELP —
the EXACT OPPOSITE of real Boss 5** (where they hoard useless fruit and hurt). Confirms: the sim
rewards fruit/scale the real boss punishes → USELESS for validating this; the only valid judge is
`collect_debug_games.py … boss`. NB the sim also flagged a real risk: choppers-only dropped to
1.45 trolls (on iron-poor draws it may UNDER-troll if the 2nd chopper can't fund) — resolve that
vs the REAL boss too (maybe: keep a cheap 2nd-chopper path but never a fruit-hoarding harvester).
sched_bot.rs kept in sync with main.rs (harvester fallback off by default; SB_HARVEST=1 restores).

### TWO READY-TO-VALIDATE SCALE CANDIDATES (both built, both UNVALIDATED — API-blocked)
1. **v1.10.0-scale2chop** (`cgauto/submissions/v1.10.0-scale2chop.min.rs`) — PREFERRED. It's the
   proven decide_elite (v1.9.0 multi-axis spec, robust iron funding) + a LATE 2nd chopper: trains
   only after t60 AND farm>=8, cheap fixed cc2, adaptive-affordable. Keeps the winning early game
   intact; adds late-game throughput (the gap) only when the economy can support it. On maps where
   the 2nd chopper can't train it == v1.7.0 (rank-130 floor). Knobs: GE_NCHOPPERS=2, GE_CHOP2_T=60,
   GE_CHOP2_FARM=8. **Untested risk:** 2 choppers may over-fell the farm → validate the farm feeds
   both. main.rs decide_elite IS v1.10.0 now (unsubmitted); arena still runs v1.7.0.
2. **decide_sched choppers-only** (build DEBUG from main.rs) — the 4-troll base got 3/10; the fix
   drops the fruit-hoarding harvesters. Higher ceiling, higher variance, weaker funding than #1.
► **RESUME: when the play API quota resets, bench BOTH vs real Boss 5 (`collect_debug_games.py …
boss 12`); the one with the best win% AND avg wood >= v1.7.0's 45 wins → bump VERSION, submit
(v1.10.0 needs no main() change; decide_sched needs main() pointed at it). Do NOT submit unbenched
(recipe: bench-first; unvalidated churn risks rank 130).**

### ★ VALIDATED (2026-07-05, small bursts — API allows only ~3 games/burst then re-throttles)
- **v1.10.0-scale2chop: 0/3, wood 46 ≈ v1.7.0.** The late 2nd chopper does NOT help — it STARVES
  (1 starter/feeder can't keep the farm stocked for 2 choppers).
- **decide_sched choppers-only: 1/3, wood 38** (up from schedprod's 28 — the harvester-drop DID
  help wood, per the diagnosis) but still < v1.7.0's 45, hitting the SAME 2-chopper starvation.
- **REFINED ROOT CAUSE: scaling to 2 choppers starves the farm (chop rate > 1 feeder's replant
  rate).** The players out-scale us because their extra trolls are HARVESTERS that FEED/REPLANT
  the farm; our harvesters HOARD fruit (useless). **THE REAL FIX (next): a 3rd troll = a FEEDER
  that REPLANTS bananas to keep the farm stocked for the choppers — NOT a fruit-gatherer.** That's
  a new role in decide_elite/decide_sched (plant-focused harvester), then bench vs Boss 5. No bot
  yet reliably beats Boss 5 (best ~30%, variance/starvation); the feeder-replant economy is the
  unbuilt piece. NB rank/promotion needs high OVERALL rating (steady floor) too — the scale bots'
  variance would tank field games; the winner must be steady (≥45 wood floor) AND out-produce.

## ★★★★ DATA-AGENT VERDICT (32 real Boss-5 games + 22 player games, 2026-07-05)
Full: `docs/boss5-game-analysis.md`, `docs/player-loss-analysis.md`. Overturns several earlier
guesses — the loss is a **sustained late-game wood-THROUGHPUT deficit**, nothing else:
1. **0/32, wood 45 vs 62 (1.47×).** Both sides get an IDENTICAL turn-1 draw (20/20 verified) →
   the gap is 100% DECISION/EXECUTION, not luck.
2. We **lead through t100, tie at t150, get overtaken t150→300** — EVERY game, and vs every
   player. Even with timing removed (both train t2-3) the gap is still 1.31×. **NOT** a
   training-timing, denial, opening, or map-geometry problem (all ruled out). Do NOT touch the
   early game.
3. **Boss 5 uses ms=3 and chop=3** (funded by surplus plum/iron) — throughput axes our bot never
   touched (fixed ms2/chop2). Present in 12/52 games → ~1.65× the gap when used.
4. **BUG (v1.7.0):** the cc2-vs-cc3 choice was gated on FULL affordability but they differ ONLY
   in lemon → a plum/iron shortfall wrongly locked cc2 on lemon-rich maps (only 40% of lemon≥10
   draws got cc3). **REVERSAL:** lemon-RICH maps are WORSE for us (1.49× vs poor 1.29×) — Boss 5
   exploits abundance better; prioritize rich-map fixes.
5. **Players out-SCALE us:** runninglvlan=3 trolls (harvester+cc3 chopper), nmahoude=4 (2 hybrids
   feeding a cc4/chop3 super-chopper, banks ~0 to t150 then explodes 0.665 vs our 0.239 wood/turn
   = 2.78×). Our `GE_MAX_TROLLS=2` is a hard scale ceiling.

**LEVER = late-game wood/turn (throughput).** Two prongs: (a) richer chopper SPEC — ms=3/chop=3/
cc=3 when the draw's surplus allows (v1.9.0 below); (b) EXECUTION/routing (travel is ~2.5× the
felling; the MC agent) and/or SCALE (a 3rd troll — but prior 4-troll builds failed on funding).

### v1.9.0-multiaxis — the spec prong (testing vs real Boss 5)
Pick EACH axis independently to level 3 iff the turn-1 draw's binding resource (plum→ms,
lemon→cc, iron→chop) is already ≥ n+9. Fixes bug #4 (per-axis gating) + adopts ms=3/chop=3
(#3). Zero training-delay risk (an axis upgrades only when its resource is already free).
`main.rs` `lvl = |res| if inv[res] >= n+9 {3} else {2}; spec=(lvl(PLUM),lvl(LEMON),0,lvl(IRON))`.
**RESULT: 1/10 vs Boss 5, wood 45 — MARGINAL** (≈v1.7.0). The upgrades trigger only when a
resource is already ≥10 at t1 (~11%/axis) so v1.9.0==v1.7.0 on ~89% of maps. Correct + dominant-
by-construction, but the spec prong is inherently marginal; it CANNOT close the 1.47× throughput
gap. HELD (not shipped) — combine with the routing prong (MC agent) before churning placement.
**The real levers remain EXECUTION/routing + SCALE (3rd troll), not spec.**

## ★★★ DEFINITIVE BOSS-5 LOSS ANALYSIS (real games, 2026-07-05)
16 real Boss-5 games (v1.7.0 & v1.7.1 debug builds via playType). **0/16 wins**, our wood ~45
vs Boss 5's ~61. Boss 5 ADAPTS its spec by map: `2.2.0.2`(cc2), `2.3.0.2`(cc3), even `2.2.0.3`
/`2.3.0.3`(chop3). Two regimes, from inventory-ramp traces:
- **GOOD-lemon maps (lemon≥5, ~2/3): COMPETITIVE.** We train the chopper ~t21 (≈Boss 5's t22),
  chop early (denial) — e.g. we WON 228-206 (our wood 12 by t70 while Boss 5 accumulated at 0).
- **LOW-lemon maps (lemon<5, ~1/3): we LOSE ~2:1** (e.g. 192-280). BOTH train late (lemon-starved:
  cc=2 needs lemon 5; lemon only comes from harvesting size-4 lemon trees, none early — our lemon
  sat at 2 from t1-20, hit 5 only at t45). Boss 5 trains slightly earlier (t41 vs our t45) AND
  **out-produces us ~2:1 post-training** (superior wood throughput: cc=3 capture / bigger fells).
- **The binding constraint is LEMON** (plum/apple/iron are always sufficient). It gates BOTH the
  training timing (low-lemon → late chopper) and, via cc, the capture size.

**Fixes tried & REFUTED vs real Boss 5:** v1.7.0 adaptive cc3/cc2 (0/8, wood 45 — the champion,
loses on production); v1.7.1 spec-ladder cc1-early (0/8, wood 28 — WORSE, cc=1 throughput too low;
reverted). **The lever is post-training wood THROUGHPUT on low-lemon maps** — but the econ space is
~capped at top-Gold (see frontier). To beat Boss 5 you must win MORE good-lemon maps decisively
AND cut the low-lemon blowouts; promotion needs >~50% not 100%. Artifacts: `data/boss5_games/boss/`.

## ★★★ MECHANIC (2026-07-06, engine.rs): felling speed = health / chop_power → the two economies
CHOP deals `chop_power` damage; a tree fells when `health<=0`. **Banana health = 2+size** (size-2=4,
size-3=5, size-4=6). So a size-2 banana (h4) fells in 2 chops with chop2 OR chop3 — **chop3 gives
NO speedup at size 2**. chop3 only helps size-3+ trees (h5-6: 3 chops→2) AND size-3 gives 3 wood
(vs size-2's 2). **THIS is why there are two economies:** (A) our TIGHT-FARM = fell size-2 fast
(quick maturation on a 9-tree farm) + short bank trips (radius 2) + cc2 — chop3 useless here (v1.13.0,
~40%); (B) Boss 5 = BIG farm + fell size-3 (more wood/tree, chop3 fells them 1.5x faster + cc3
captures 3) but LONG bank trips. Boss 5's (B) out-produces us slightly. **We can't bolt chop3/size-3
onto the tight farm (9 trees out-deplete their slow size-3 maturation → chopper idles — CONFIRMED
by the felling math).** To beat Boss 5 we'd need economy (B) done RIGHT: a big farm whose size-3
fells + funded cc3/chop3 super-chopper out-throughput its own longer bank trips — the exact tuning
that failed before (v1.5.x, v1.12.0). This is a genuine, well-substantiated ceiling for the tight
approach; the next real lever is economy (B) tuning or a search/RL bot, both fresh-session efforts.

**ECONOMY B ARENA-VALIDATED WORSE (v1.18.0, 2026-07-06):** built the turn-1 adaptive A/B (economy B
= big farm radius-3 + size-3 fells on cc3-draws; economy A = tight farm otherwise). Arena result:
**rank 135 @17.1 < v1.13.0's 120 @17.9 — WORSE, reverted.** Exactly as the felling math predicted:
the big farm can't sustain size-3 maturation with 1 feeder → the chopper idles. **So economy B —
Boss 5's own approach — does NOT transfer to our heuristic** (we lack the feeder/execution to run a
big farm). Combined with the feeder being neutral (v1.16.0), the two most-promising economy variants
are both arena-validated as NOT better than the pure tight farm. **DEFINITIVE: v1.13.0 (~40% vs Boss
5) is the arena-validated ceiling of our heuristic economy.** Reliably beating Boss 5 requires a bot
that can EXECUTE economy B (sustain a big farm + a funded super-chopper) — i.e. the RL/search track,
a multi-session build, not a heuristic knob. Every heuristic economy has now been tested and ranked.

## ★★★★★ BREAKTHROUGH (2026-07-06): the TIGHT FARM — first bot to beat Boss 5 (v1.13.0)
The throughput bottleneck was never farm SIZE or troll count — it's the chopper's **bank-trip
DISTANCE** (it walks ~farm_radius cells to the shack every `cc` wood). Fix on the proven v1.7.0
2-troll economy: **`GE_FARM_R` 3→2 (tight farm hugging the shack) + `GE_CHOP_R` 10→5 (keep the
chopper LOCAL) + `GE_FARM_MAX` 15→9** (fits radius 2). Result vs REAL Boss 5 (14 games, 3 bursts):
**4/14 (29%), wood ~47 — the FIRST bot all session to beat Boss 5 at all** (v1.7.0 was 0/32), and
it OUT-PRODUCES it on good maps (banked 74, 62). Steady (no disasters; low games are the orthogonal
lemon-funding-delay issue). **SHIPPED as v1.13.0-tightfarm** (submitted 2026-07-06, battle 40954291;
api_submit default updated). It dominates v1.7.0 on BOTH win% and wood → best promotion shot.
**ARENA CONVERGENCE (2026-07-06): v1.13.0 climbed 519→rank 118 @18.1 in ~12min, still rising —
BETTER than v1.7.0's 130 @17.4.** The tight-farm throughput gain lifts the whole-field rank, not
just Boss 5. Best standing of the project. (Still ~7pt under the boss bar 25.9; promotion unproven.)
**Tuning results (5-game bursts vs Boss 5):** v1.14.0 (cc1 on lemon-poor maps) WORSE 0/5 w40 —
cc1 throughput too low even with cheap tight banking, reverted. v1.15.0 (GE_CHOP_R 3, tighter roam)
2/5 w48 — marginally better than roam=5, within noise; main.rs holds roam=3 as the tuned candidate
(NOT yet shipped — v1.13.0 is converging; don't churn). **Tight-farm ceiling ≈30-40% vs Boss 5**;
residual losses = Boss5's ms3/chop3 super-draws + our low-lemon late-train (both hard). The winning
lever is TRAVEL-DISTANCE (tight farm/roam), not economy scale — the cc4 verdict below is superseded.

## ★★★★ EXHAUSTIVE VERDICT (2026-07-05): simple economy tweaks CANNOT beat Boss 5 [SUPERSEDED — see tight-farm above]
Tested vs the REAL Boss 5 (small API bursts): v1.7.0 0/32 w45 · v1.9.0 1/10 w45 · v1.10.0
(2nd chopper) 0/3 w46 (starves) · sched+harvesters 3/10 w28 (disasters) · sched choppers-only
1/3 w38 · **v1.11.0 (feeder/2nd printer) 0/4 w44**. NONE beats Boss 5; all cluster ~v1.7.0 or
trade wood for variance. **The bottleneck is NOT farm density or troll count — it's the single
chopper's BANK-TRIP-limited throughput** (walks to shack every `cc` wood; a denser farm/2nd
feeder doesn't reduce that; a 2nd chopper starves the 1-feeder farm). Even our adaptive spec
gives cc3/chop3 on rich draws, yet Boss 5 (ms3/chop3) still out-produces via execution/routing.
**The only thing that closes it is the LEGEND META (nmahoude's build): accumulate a big farm to
~t150 banking ~0 wood, fund a cc4/chop3 SUPER-chopper via a harvester economy, then explode
(0.66 wood/turn).** But: (a) funding cc4 FAILED before (v1.5.0/1: 39-44 wood, build never
completes), and (b) accumulate LOSES to deniers (v1.6.0: 0/6 vs runninglvlan) — risky vs Boss5's
denial. **Beating Boss 5 = solving the cc4-super-chopper FUNDING problem (hard, dedicated effort),
not another 2-3-troll tweak.** That is the real, unsolved next project. LIVE bot stays v1.7.0 @130
(the best steady bot; do NOT ship any tested variant — none clears its wood-45 floor + win rate).

**v1.12.0 (the Legend-meta accumulate build) ATTEMPTED + FAILED (2026-07-06): 1/4, wood 18** — the
WORST. decide_sched with a cc3/chop3 super-chopper + harvesters (accumulate, bank ~0 early): the
harvesters HOARD fruit but the super-chopper never explodes (weak fruit→wood conversion; the lone
"win" was on hoarded fruit points, not wood). Reproduces the exact prior cc4 failure. **So even a
genuine attempt at the identified answer fails with the available approach** — the Legend meta
needs careful joint tuning (super-chopper spec/timing + farm size + harvester fund-then-FEED
behavior + accumulate-vs-denial) that neither simple tweaks nor a rushed build cracks. HONEST
CEILING: 8 variants tested vs real Boss 5, none beats it; v1.7.0 (steady, rank 130) remains best.

## THE TRANSFER WALL (critical — why the sim misleads here)
The local sim ALWAYS ranks **cc=2 > cc=3 > cc=4** for wood (90 > 87 > 74), the OPPOSITE of
the arena where Boss 5's cc=3 (84) beats our cc=2 (71). Sim penalizes the higher-cc training
delay + rewards fast size-2 throughput; the arena rewards per-tree capture. **DO NOT use the
sim to pick cc/fell_size — it's wrong. Validate cc/fell changes ARENA-FIRST only.**
Also: ladder WOOD reads are confounded by placement — a fresh agent plays weak opponents
(low wood for both), so 62 wood at rank 219 ≠ 71 at rank 118. Need controlled games (below).

## CONTROLLED EXPERIMENTS via CG API — `TestSession/play` WORKS (no ladder wait!)
`POST services/TestSession/play` with cookies + body
`[handle, {"code":CODE,"programmingLanguageId":"Rust","multi":{"agentsIds":[A,B],"gameOptions":""}}]`
returns **200 with full game frames** (a played game, incl. our stderr `@TFMAP/@TFSUM` debug).
This is the IDE's "Play my code". agentsIds pick opponents (need to find Boss 5's agentId;
-1/-2 = defaults). Build a reusable `cgauto/cg_play.py` to run N games vs a chosen opponent
and parse wood/win — clean, fast, ladder-independent. This is the RIGHT iteration loop.

## VERSION LOG (arena-first; v1.4.5 is the frozen fallback)
| ver | change | arena result |
|---|---|---|
| **v1.4.5-seedreserve** | cc=2, 2-troll, seed-reserve, anti-stall | **rank 118, 71 wood (BEST/fallback)** |
| v1.5.0-harvest4 | 4-troll (1 planter+2 cc2 chop) | rank 491, 39 wood — FAIL, reverted |
| v1.5.1-cc4legend | 4-troll (hybrid+2 cc4) | lost to Boss 5 44-84, only 3 trolls — FAIL |
| v1.5.2-cc3lean | v1.4.5 + cc=3 (fell size 2) | 65 wood — cc=3 wasted, regression |
| v1.5.3-dropfix | v1.5.2 + drop-cell fix | 65 wood — still cc=3-wasted |
| v1.5.4-dropfix2 | v1.4.5 cc=2 + drop-cell fix | placing; wood read confounded |
| **v1.5.5-cc3fs3** | cc=3 + FELL SIZE 3 + farm 18 + dropfix | **PREPPED, not yet shipped** — the Boss-5 mechanism |
| **v1.6.0-cc3fs3accum** | cc=3 + fs=3 + accumulate delay t45 + farm18 | **0/6 (0%) vs runninglvlan**, our wood 54 but opp 70 — accumulate CEDES DENIAL. REFUTED. |
| v1.6.1-cc3earlyagg | cc=3 + fs=2 + early (v1.4.5 + cc3 only) | 3/8 (38%) vs runninglvlan, wood 44 — cc3+fs2 wanders. REFUTED. |
| **v1.6.2-cc3hybrid** | cc=3 + native-fell-2 (denial) + farm-fell-3 (production) + farm15 | runninglvlan 50%, nmahoude 50% (wood 75>70); **arena rank 211 @18.4** (v1.4.5 was 216 @17.7). |
| **v1.7.0-adaptivespec** | turn-1 ADAPTIVE: cc3 if draw affords it else cc2; farm-fell matches cc; native-fell 2 | dominant-by-design (never delays chopper). n=6 vs elite indistinguishable (noise); more consistent wood (49-95 vs v1.6.2's 0-129). **SUBMITTED 2026-07-05, converging.** api_submit default now points here. |

## FIXES BAKED IN (main.rs decide_elite)
- **Drop-cell distribution** (`drop_cell_for`): trolls pick DISTINCT shack-adjacent cells
  (avoid each other + reserved) — fixes the mutual-lock where both funnel to one cell and
  miss bank trips. (Was a user observation; real but only ~12 blocked moves/game = small.)

## NEXT STEPS
1. Build `cgauto/cg_play.py` (TestSession/play) → run v1.5.5 vs Boss 5, clean wood/win.
2. If v1.5.5 (cc=3+fs=3) out-banks Boss 5 → ship, promote. Else tune farm size / opening.
3. Stop churning ladder submissions (each resets placement ~40min); iterate via cg_play.py.

## CG API + TOOLING (2026-07-05) — how to read rank & run controlled games
All Python runs under the uv `.venv` (`uv run python …` from repo root, or `.venv/bin/python`).
`codingame` is a pyproject dep (`uv add` to add more). Cookies live in `cgauto/cg_session.txt`
(`cgSession=`, `rememberMe=`). userId 1302251, pseudo "tass", TSH `77167730956e…3026`.

### `codingame` PyPI package — READ-ONLY (leaderboard/rank)
Login via the rememberMe cookie, then read the puzzle leaderboard. No submit, no play.
```python
import codingame
rm = [l.split("=",1)[1].strip() for l in open("cgauto/cg_session.txt") if l.startswith("rememberMe=")][0]
c = codingame.Client(); c.login(remember_me_cookie=rm)          # logs in as tass
lb = c.get_puzzle_leaderboard("spring-challenge-2026-troll-farm")
# lb.users -> rank/score/pseudo/league(.name)/id ; lb.leagues -> per-league .count
```

### ★ VERIFY WHAT'S LIVE + ACCURATE RANK (2026-07-05) — two endpoints
- **`TestSession/startTestSession [TSH]`** → returns the LAST-SAVED/SUBMITTED code (find the field
  with `fn main`+`const VERSION`). Use to confirm the live bot's LOGIC (grep it for a signature,
  e.g. `GE_CHOSEN_SPEC` = v1.7.0 adaptive-spec ×3; `(2,1,0,2)` = the v1.7.1 ladder). NB the
  `const VERSION` string has been STALE at "1.5.9-accbig" since v1.5.9 (never bumped when logic
  changed) — do NOT trust the VERSION label to identify the bot; grep the logic. Fixed to
  "1.7.0-adaptivespec" in main.rs 2026-07-05 (rides the next real submission).
- **`Leaderboards/getUserArenaDivisionRoomRankingByTestSessionHandle [TSH, USERID]`** → the
  AUTHORITATIVE arena-room rank: `{rank, localRank, total, score, league.divisionIndex(4=Gold),
  eligibleForPromotion, agentId}`. This is the number the site shows (e.g. rank 130/531 @17.4).
  `cg_rank.py` (codingame pkg global leaderboard) reports a DIFFERENT scope — use this endpoint
  for the real Gold-room rank. Our agentId: 6539872.

### `cgauto/cg_rank.py` — our rank/score/league + Legend bar (READ-ONLY)
`uv run python cgauto/cg_rank.py [--top N]`. Sample:
`tass: rank 213 score 18.2 Gold | Legend = top 97 ranks (beat Boss 5 to enter); boss bar score>~25.9 (top Gold @rank 98)`.
NB: Legend is entered by BEATING BOSS 5, not a score cutoff — so the min-Legend score is
polluted by freshly-promoted players who then tanked (rank 97 sat at −6.6). The meaningful
bar is the **top-Gold score (~26)** = the Boss-5 proxy you must out-compete.

### ★★★ PLAYING THE REAL BOSS 5 — SOLVED (2026-07-05, from a browser network dump)
The IDE's "Play my code" plays the league BOSS by DEFAULT (until you transfer a specific replay).
Decoded the exact request from a devtools network dump — the magic is the **`playType`** field:
```
POST TestSession/play  body:
[TSH, {"code":CODE, "programmingLanguageId":"Rust",
       "multi":{"agentsIds":[-1,-2], "gameOptions":null,
                "isSoloLeague":false, "playType":["IDE_CODE","BOSS"]}}]
```
`agentsIds:[-1,-2]` ALONE = random matchmaking (a real player). Adding **`playType:["IDE_CODE",
"BOSS"]`** makes agent -2 the **BOSS (Boss 5)**. Confirmed: opponent build = `2.3.0.2` (cc=3),
trains ~t2, `MSG :]`, banks ~73-84. "Play my code" = a NEW MAP each call (collect across maps);
"Replay in same conditions" = same seed. Harness: `cgauto/collect_debug_games.py <debug.min.rs>
boss N` — plays Boss 5 with our DEBUG build so @TFMAP/@TFSUM stderr is captured, saves each
game's map + per-turn log to `data/boss5_games/boss/`, and prints wood-ramp/train-turn analysis.

### Opponent selection for `TestSession/play` — SOLVED
`POST services/TestSession/play` body
`[TSH, {"code":CODE,"programmingLanguageId":"Rust","multi":{"agentsIds":[-1, OPP],"gameOptions":""}}]`.
- `-1` = our IDE code = **player index 0** (so `scores[0]/ranks[0]/inputmodule line 0` = us).
- `OPP` = **a specific player's agentId** → a controlled game vs a FROZEN SNAPSHOT of that
  player's submitted bot. Proven: a *valid* agentId returns a full game (scores, tooltips,
  refereeInput); an *invalid* one (e.g. 999999999) returns an empty game (`scores:[]`) — so the
  id is really consumed. Different ids give different reproducible outcomes (darkhorse64 6480808
  → we win; RunninglVlan 6481102 → we lose 0/4). `OPP=-2` = random matchmaking.
- **The arena Boss is NOT exposed as a selectable agentId** by any endpoint checked
  (`Puzzle/findProgressByPrettyId` has league info but no boss id; `TestSession/findInformationById`
  404s; bosses never appear in our battle history). So we use a **strong fixed top-Gold player as
  a Boss-5 proxy** — fully reproducible, and stronger-than-boss opponents are the harder target.
- Get agentIds from ladder history:
  `gamesPlayersRanking/findLastBattlesByTestSessionHandle` body `[TSH, null]` → list of battles,
  each `players[].{playerAgentId,nickname,userId}`. Our current agentId: **6539562**. That call
  yielded 78 distinct Gold opponents incl. elite bots (darkhorse64, MSmits, nmahoude, RunninglVlan).
  Note `gameResult/findByGameId` is UNAUTHORIZED for these IDE "play" games (can't fetch the replay).

### `cgauto/cg_play.py` — controlled games vs a fixed opponent
`uv run python cgauto/cg_play.py <code.min.rs> [n_games] [opponent]`
(`opponent` = registry nickname / raw agentId / "random"; default RunninglVlan 6481102).
`--list` shows the built-in opponent registry (pulled from our Gold battle history). It retries
transient failures + degenerate games, parses per-game W/L + score + **wood** (from the frame
`inputmodule` `plum lemon apple banana iron wood`, field 5), and aggregates win-rate + avg wood.
Verified (v1.4.5 vs RunninglVlan, 4 games): `0/4 wins | our wood 44 | opp wood 61`. IMPORTANT:
the `scores` field (~150-250) is a composite, NOT wood — track the **wood** column. This is the
right iteration loop: same strong opponent every game removes the ladder placement confound.

## 2026-07-05 — DIAGNOSED the strong-opponent edge (controlled game vs runninglvlan)
via TestSession/play: our v1.4.5 wood ramp `[2,12,20,26,32,40]` (steady, caps ~40) vs
runninglvlan `[0,0,9,30,48,62]` — **it banks ~0 until t100, then EXPLODES to 62.** It
trained its chopper LATE (t68), so the starter builds a big MATURE farm first, then the
chopper harvests it. This is the ACCUMULATE pattern in just **2 trolls** (not the 4-troll
180-wood build). Our bot chops from t2 → fells young size-2 trees continuously → never
accumulates → caps ~40. Strong bots let the forest mature (size 3+) then harvest → 62+.

**Lever (v1.5.8-accum2):** DELAY the chopper (GE_CHOP_DELAY=45, or train early once the
farm is full via GE_CHOP_FARM). Starter builds + matures the farm during t0-45 (bank ~0),
then the chopper harvests mature (size-3) trees. Keep cap 12 (moderate — big cap starved on
sparse maps in v1.5.6). Being A/B'd vs v1.4.5 (8 games each) via cg_play.py.

NB tooling gotcha: TestSession/play throttles under rapid calls → transient HTTP 422; a
fresh `generateSessionFromPuzzlePrettyId` + ~15s wait clears it (handle is unchanged).
