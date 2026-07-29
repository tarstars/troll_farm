# Rank-improvement hypotheses — `chatgpt_1`

Date: 2026-07-29  
Repository snapshot reviewed: `main` at `fa33b21` / bot `v0.6.1`  
Coordination issue: #1

## Scope and method

This is an audit and experiment backlog, not a production submission. I reviewed:

- `bot/main.py`
- the verified mechanics and Bronze rules
- the simulator, runner, map generator, views, and boss port
- decision, training, chopper, and simulator tests
- the prior lost-game analysis and design plans
- public postmortems from Gold/Legend players

The original contest ended on 2026-05-25, but Troll Farm is available as a multiplayer practice game, so leaderboard improvement remains meaningful.

## Main diagnosis

The current bot is a solid league-progression baseline, not yet a competitive final-rules economy bot.

Its strongest parts are correct parsing, BFS pathing, basic collision avoidance, fruit ripeness prediction in non-water conditions, affordable fallback training, and one enemy-side chopper. The largest gap is strategic: the policy still treats fruit gathering as the default economy and planting as a small orchard side task. Stronger approaches made wood production, specialized build orders, opponent interaction, and task-level planning central.

Important implementation gaps found:

1. `sim/runner.py` still calls `generate()`, not `generate_bronze()`, so the checked-in CLI does not run Bronze maps.
2. The runner explicitly warns that its boss is weak and movement tie-breaking is not referee-faithful.
3. Simulator plants are initialized with health `6` for every type, and growth changes size without changing health; chopping simulations therefore misprice many trees.
4. `predict_fruits()` ignores water even though water cells are parsed.
5. The starting Bronze troll has `chopPower=1`, but only trolls with `chopPower>=2` enter `chop_command`; gatherers never mine. Low starting iron can therefore prevent the intended chopper build.
6. Training is a fixed list of specs and can spend scarce iron on ordinary trolls before the chopper is affordable.
7. Planting always chooses BANANA in the nearest three shack cells; it does not choose a type or position from water access, resource deficits, or future wood value.
8. Planted trees are not deliberately converted into wood. Choppers target trees near the enemy shack, so the orchard is mostly a slow fruit investment rather than a plant–chop–drop engine.
9. Tree assignment is greedy in troll-id order, not a global task assignment.
10. `opp_inventory` and `opp_trolls` are parsed but effectively unused.
11. Chop targeting ignores health, chop duration, return distance, free capacity, likely overflow, and opponent actions. A chopper standing on any tree chops it even when another tree was selected as the strategic target.
12. There is no liquidation/endgame policy beyond stopping training 25 turns before turn 300.

## Twelve falsifiable hypotheses

### H1 — A referee-faithful Bronze benchmark will improve arena selection quality

**Priority:** P0 / prerequisite  
**Expected impact:** indirect but foundational

**Hypothesis:** Changes selected using a Bronze runner with correct tree health, water growth, random movement ties, action conflicts, and multiple strong opponent archetypes will have substantially higher arena win-rate than changes selected using the current league-2 boss harness.

**Why plausible:** The current CLI never calls `generate_bronze()`. The boss omits planting and is materially weaker than competitive bots. Tree health/growth is inaccurate, which directly corrupts chop timing and wood yield estimates.

**Smallest experiment:**

- Add `--league bronze` and use `generate_bronze()`.
- Cross-check deterministic traces against the official referee for growth, health, chopping, planting conflict, movement ties, and training.
- Add at least four opponents: farmer, plant–chop–drop, aggressive chopper, and mixed economy.
- Evaluate paired seeds and report mean, lower-decile, and worst-map score margins—not only average boss win-rate.

**Falsification:** If simulator rankings do not correlate with official-referee or arena rankings across at least 10 materially different variants, the harness is still not predictive.

### H2 — Make plant–chop–drop the primary local scoring engine

**Priority:** P0  
**Expected impact:** very high

**Hypothesis:** A dedicated near-shack loop that picks a seed, plants, grows to a chosen size, chops, and drops wood will outperform the current small orchard plus remote gathering on most Bronze maps.

**Why plausible:** One fruit is worth 1 point, while one wood is worth 4. The current bot pays a banana seed and planter actions but does not schedule its own chopper to harvest the resulting wood. Strong postmortems repeatedly identify plant–chop–drop as the central economy.

**Smallest experiment:** Implement one adjacent-shack banana cell and one planter/chopper state machine. Compare target sizes 1 and 2. Count net banked points per troll-turn, including the spent seed and all PICK/PLANT/CHOP/DROP turns.

**Falsification:** Disable the loop if it loses paired-seed score margin against the best non-PCD baseline in every major map class.

### H3 — Mine with the starting chop-1 troll and reserve iron for a fast chopper

**Priority:** P0  
**Expected impact:** very high on low-iron starts

**Hypothesis:** Routing the initial `chopPower=1` troll to nearby iron, reserving iron, and selecting the strongest chopper affordable within a time budget will beat the current policy, especially when starting iron is below the cost of a chop-2 troll.

**Why plausible:** The starter can legally mine but never does under the current role split. Ordinary chop-0 training also consumes iron in Bronze, and increasing troll count raises every later training cost. The current fallback can therefore spend the resource needed to unlock the wood economy.

**Smallest experiment:** Before the first specialized training, estimate turns to obtain the missing plum/lemon/iron for candidate builds. Compare dynamic builds such as `(2,2,0,2)`, `(2,4,0,3)`, and cheap fallbacks. Do not train a normal gatherer if that delays the chosen chopper beyond its payback horizon.

**Falsification:** Reject if dynamic build selection fails to improve score margin on the low-iron half of Bronze seeds without materially hurting high-iron seeds.

### H4 — Water-aware production, including an apple engine, is a distinct winning map strategy

**Priority:** P0/P1  
**Expected impact:** high but map-dependent

**Hypothesis:** On maps with a grass cell adjacent to both shack and water, a dedicated water-boosted apple tree/harvest/drop engine will outperform banana planting; elsewhere, planting type and location should be chosen from production rate and training deficits rather than fixed to BANANA near the shack.

**Why plausible:** Water reduces APPLE cooldown from 9 to 2, faster than every other water-adjacent fruit. The current prediction and planting code ignore that advantage. A Legend postmortem reported this exact map feature as a major edge.

**Smallest experiment:** Stratify maps by shack–water adjacency. Add water-aware `predict_fruits`, estimate production per troll-turn, and compare apple-engine, banana-PCD, lemon-engine, and no-plant policies per stratum.

**Falsification:** Remove the special case if it does not win its target map stratum after accounting for seed, setup, defense, and liquidation costs.

### H5 — Global task assignment will beat troll-id-ordered greedy reservations

**Priority:** P1  
**Expected impact:** high with 3+ trolls

**Hypothesis:** Enumerating harvest, chop, mine, plant, bank, and defend tasks, then solving a maximum-weight matching between trolls and tasks, will improve throughput and reduce role mistakes versus assigning trees greedily in troll-id order.

**Why plausible:** Different troll stats make tasks non-interchangeable. A high-capacity chopper, fast miner, and harvest-power troll should not see the same target ordering. Strong bots used Hungarian/Munkres or small brute-force matching with value discounted by completion time.

**Smallest experiment:** Generate the top few legal tasks per troll. Score each as `expected_delta_value * discount^turns_to_complete`, then brute-force the small joint assignment. Add a small target-persistence bonus to prevent oscillation.

**Falsification:** Reject if assignment does not improve useful-action rate, score margin, or collision rate on 3–5 troll scenarios.

### H6 — Chop by value per completion time, with cargo and health awareness

**Priority:** P1  
**Expected impact:** high

**Hypothesis:** Choosing chop targets by expected wood plus denial value divided by travel, chop, and banking time will outperform the current `(distance_to_enemy_shack, travel_distance, -size)` ordering.

**Why plausible:** A size-4 APPLE can require many chop turns; a nearer low-health banana may yield more points per turn. Current logic can also approach a tree without enough free capacity, waste overflow wood, mine while carrying wood, or chop an arbitrary tree merely because it is underfoot.

**Smallest experiment:** For each candidate tree estimate:

- turns to arrive;
- turns to kill from current health and chop power;
- collectible wood after capacity limits;
- turns to a drop cell;
- opponent denial value;
- risk of opponent last-hit/co-chop.

Bank before chopping when free capacity would waste valuable wood. Track or recompute the intended target so transit through another tree does not trigger an accidental chop.

**Falsification:** Reject if wood overflow and accidental chops fall but total score margin does not improve.

### H7 — Co-chop defense converts enemy aggression into our score

**Priority:** P1  
**Expected impact:** high against aggressive opponents

**Hypothesis:** When an enemy is chopping a valuable local tree, sending a nearby troll to co-chop or time the last hit will produce more score and preserve the economy better than ignoring the opponent.

**Why plausible:** Opposing trolls may share a cell, and final wood can duplicate/split similarly to the last-fruit mechanic. Gold/Legend postmortems report large gains from joining an opponent chopping their local trees and then banking the wood.

**Smallest experiment:** Detect enemy trolls on or approaching trees inside our economic radius. Compare ignore, harvest-until-danger, co-chop, and pre-emptive chop responses using an aggressive opponent suite.

**Falsification:** Disable when travel cost exceeds expected recovered wood/denial or when it consistently abandons a higher-value local loop.

### H8 — Detect opponent build orders and deny bottleneck resources, not merely nearby trees

**Priority:** P1  
**Expected impact:** high against scaling strategies

**Hypothesis:** Detecting opponent lemon/capacity scaling, local plantations, iron/chopper timing, and troll-count plans will outperform generic chopping of whichever tree is closest to the enemy shack.

**Why plausible:** Lemons gate carry capacity, apples gate harvest power, and iron gates chop power. Competitive bots reached higher leagues by detecting planted lemon engines or aggressive profiles and changing their own training and denial policies. Some even used reckless chopping—destroying a critical tree without collecting wood—when denial exceeded collection value.

**Smallest experiment:** Track natural versus newly planted trees near each shack, opponent inventory deltas, trained stats, and troll roles. Add targeted denial modes with explicit stop conditions.

**Falsification:** Reject a detector if false positives reduce margin against neutral farmers more than true positives gain against scaling opponents.

### H9 — Explicit bootstrap, production, and liquidation phases will recover otherwise stranded value

**Priority:** P1  
**Expected impact:** high in the final 40 turns

**Hypothesis:** A phase-aware policy that stops unprofitable training/planting, schedules final tree chops, and guarantees carried resources can be dropped before turn 300 will outperform the current policy.

**Why plausible:** The bot only stops training near the end. It may still start fruit trips, plant trees that cannot mature, or leave wood/fruit carried at game end. Strong bots evaluated whether an entire plant/chop/drop sequence could finish before planting.

**Smallest experiment:** Compute latest-start times for harvest/drop and plant/grow/chop/drop sequences. In liquidation, value carried resources by whether they can reach a drop cell; chop owned local trees when that is the best bankable conversion.

**Falsification:** Reject if final banked score from identical turn-240 states does not improve.

### H10 — Resource shadow prices should drive harvesting and training

**Priority:** P1/P2  
**Expected impact:** medium-high

**Hypothesis:** Valuing each fruit by both score and its marginal contribution to the next profitable troll/build will outperform treating all fruit trees equally and using fixed training specs.

**Why plausible:** The prior replay was APPLE-starved, while later strategies depend heavily on lemon and iron timing. Bananas are pure score unless planted; plum/lemon/apple/iron may be worth far more when they unlock a high-return specialized troll.

**Smallest experiment:** Maintain a candidate build queue. Set each resource’s shadow price from the cheapest remaining deficit and estimated payback. Use it in harvest target valuation, planting decisions, and training timing. Recompute when opponent denial changes likely availability.

**Falsification:** Reject if the policy delays banked score for builds that do not repay before the game ends.

### H11 — A map taxonomy should select different build orders

**Priority:** P2  
**Expected impact:** medium-high

**Hypothesis:** Classifying maps by shack distance, shack–water cells, nearest iron access, obstacle topology, nearby resource mix, and opponent reach will outperform one global `PARAMS` configuration.

**Why plausible:** Public postmortems report strong map-specific recipes and distinct successful strategies: local apple engine, banana PCD, remote aggression, and multi-troll scaling. The current bot always uses the same cap, training lists, orchard size, and target logic.

**Smallest experiment:** Cluster or hand-classify maps into 5–10 interpretable classes. Tune build order and strategy gates per class using paired seeds and an opponent portfolio.

**Falsification:** Reject classes that do not generalize to held-out seeds or whose gains vanish against varied opponents.

### H12 — Small joint-action rollouts will beat pure greedy action selection within 50 ms

**Priority:** P2 after H1  
**Expected impact:** high ceiling

**Hypothesis:** Generating a small set of abstract actions per troll and evaluating joint combinations over short rollouts will improve tactical choices, especially around contested trees, training timing, planting, and endgame liquidation.

**Why plausible:** Multiple top-20 bots used shallow search or beam search over task-level candidates, not exhaustive cell-level search. The current state is small, and strong policies reported very low runtime with heavily pruned candidates.

**Smallest experiment:** Keep the top 3–5 tasks per troll, prune illegal/conflicting joint plans, and roll out 3/5/7/9/12 turns with a greedy policy. Evaluate banked score differential plus distance-discounted carried resources, future production, training readiness, and tree control. Start with our model only; add a maximin opponent model on small/aggressive maps.

**Falsification:** Reject if it exceeds the 50 ms budget or fails to beat the same heuristic without rollouts on held-out official-referee matches.

## Recommended implementation order

1. H1 — trustworthy Bronze benchmark and replay tests.
2. H2 — one-cell plant–chop–drop baseline.
3. H3 — starter mining and iron-reserving build order.
4. H4 — water-aware growth and map-specific apple/lemon engines.
5. H6 + H9 — correct chop economics and liquidation.
6. H5 + H10 — global task assignment with resource shadow prices.
7. H7 + H8 — defensive co-chop and opponent strategy detection.
8. H11 — map-class policy selection.
9. H12 — shallow joint-action rollout over the improved task model.

## First implementation candidate

The highest expected-value first scoring patch after benchmark repair is **H2 + H3**:

- use the starting chop-1 troll to mine when that unlocks a real chopper;
- reserve iron rather than spending it on ordinary trolls;
- establish one adjacent-shack banana PCD cell;
- make the first trained chopper liquidate that local tree at a selected size before raiding remotely.

This is small enough to implement and ablate, while directly moving the bot from a fruit-gathering baseline toward the final-rules wood economy.

## Sources

Repository evidence:

- `bot/main.py`
- `docs/mechanics.md`
- `docs/statement_bronze.md`
- `docs/statement_bronze_full.md`
- `sim/engine.py`
- `sim/mapgen.py`
- `sim/runner.py`
- `sim/boss.py`
- `tests/test_chopper.py`
- `tests/test_decide.py`
- `tests/test_sim_engine.py`
- `tests/test_training.py`
- `docs/plays/lost_game_v0.5.1_analysis.md`

External strategy evidence:

- CodinGame forum, “Spring Challenge 2026 (Troll Farm) — Feedback & Strategies”, 2026-05-25 onward.
