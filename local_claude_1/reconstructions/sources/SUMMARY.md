# SUMMARY — what the public internet says about the four top players' algorithms

Worker W1 (internet), 2026-08-28, first complete version at ~03:30Z. Everything here is extracted ONLY from the
archived write-ups in this directory (each file starts with URL, date, author, language); our corpus is not used.
"Talents" are the four troll attributes in the order the game uses them: movementSpeed / carryCapacity /
harvestPower / chopPower, written as a/b/c/d. "PCD" = plant-chop-drop (plant a fruit, chop the grown tree for
wood, drop the wood at the shack). "Train N" = the N-th troll that a bot TRAINed (the starting troll is not counted).

## 0. The short version

| player | ladder now | contest | own write-up? | what exists |
|---|---|---|---|---|
| delineate | #1, 30.89 | #1, 33.77 | **YES** — a 13 kB gist + 2 forum posts | a neural-network policy trained by PPO; full architecture and curriculum described; no hand rules |
| norxondor_gorgonax | #2, 29.66 | #2, 30.36 | **NO** — never posted anywhere we can find | only the game author's per-player statistics (talents trained, trees planted, score curve) |
| Bubaptik | #3, 27.90 | not in the contest's Legend league | **NO** — no trace on the web at all | nothing |
| MSz | #4, 27.72 | #10, 27.25 | **NO** for Troll Farm (his post-mortem repo stops at 2024) | the author's statistics + his earlier post-mortems (usual toolkit) |

Everything else found: the whole "Feedback & Strategies" forum thread (35 posts; 12 Legend players describe their bots),
Astrobytes' post-mortem (the game co-author's alter ego trlr1990, #1 when Legend opened), the game author's own
bot description (#23), the rules statement from the referee repository, and the game author's statistics for all
69 Legend players (`all-legend-players-eulerschezahl-stats-2026-05-25.md`, with the JSON series next to it).

**The contest's top ten by the numbers** (game author's statistics; "2/3/4/5+" = share of games ended with that
many trolls; "planted" = trees planted per game by turn 295 as plum/lemon/apple/banana; "wood@200" = wood in the
shack at turn 200):

| # | player | W-L-D | own-opp score | 2/3/4/5+ trolls | train 1 | train 2 | train 3 | planted P/L/A/B | wood@200 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | delineate | 525-146-2 | 418-298 | 38/27/27/8 | 2.0/2.2/1.5/2.0 | 2.5/3.4/1.0/2.5 | 2.7/3.7/1.0/2.9 | 8.3/8.8/1.5/21.4 | 35 |
| 2 | norxondor_gorgonax | 345-267-4 | 370-356 | 19/28/41/11 | 2.1/2.1/1.7/1.7 | 2.3/3.1/1.1/2.0 | 2.4/3.1/0.4/3.0 | 10.0/11.1/2.1/8.7 | 39 |
| 3 | yamo | 470-396-8 | 184-196 | 100/0/0/0 | 1.9/2.0/0.0/2.1 | — | — | 0.8/0.8/1.7/5.5 | 30 |
| 4 | yaichi | 456-401-2 | 298-280 | 99/0/0/0 | 2.0/2.1/0.0/2.1 | — | — | 0.0/0.0/0.0/41.6 | 46 |
| 5 | bl4sterino | 387-371-1 | 544-519 | 10/42/46/0 | 2.0/2.1/2.0/1.1 | 3.0/4.0/1.1/3.0 | 3.0/4.0/0.0/3.0 | 4.1/4.4/1.6/40.1 | 48 |
| 6 | wala | 421-409-3 | 529-523 | 2/4/94/0 | 1.7/1.8/1.6/1.0 | 2.0/3.2/0.6/1.8 | 2.6/3.2/0.0/2.6 | 5.1/7.5/3.5/37.0 | 54 |
| 7 | uta_ccc | 329-330-1 | 391-380 | 13/19/53/13 | 2.0/2.0/1.7/1.0 | 2.0/3.0/1.0/2.0 | 3.0/4.0/1.0/3.0 | 1.9/4.1/0.6/31.6 | 31 |
| 8 | laconic_pixel | 314-299-3 | 384-387 | 47/13/17/24 | 1.8/1.8/0.7/1.7 | 2.0/3.0/0.9/2.0 | 2.0/4.0/0.0/2.4 | 5.0/5.3/0.8/26.9 | 36 |
| 9 | skotz | 361-335-2 | 292-283 | 99/0/0/0 | 2.1/2.2/0.0/2.2 | — | — | 0.1/0.2/0.0/39.2 | 43 |
| 10 | MSz | 314-319-1 | 480-481 | 11/42/47/0 | 1.7/1.7/1.5/1.0 | 2.0/4.0/1.0/2.7 | 2.1/4.0/0.0/2.9 | 8.6/9.3/3.1/8.9 | 52 |

Three of the top ten (yamo, yaichi, skotz) are two-troll bots with one trained ≈2/2/0/2 chopper; yaichi and skotz
plant 39–42 banana trees per game and nothing else — a pure banana plant-chop-drop machine with two trolls.

---

## 1. delineate (#1) — the winner's own description

Sources: `delineate-gist.github.com-2026-05-25.md` (the gist, first-hand, 2026-05-25), `delineate-forum.codingame.com-2026-05-25.md`
(two forum posts, first-hand), `delineate-eulerschezahl.github.io-stats-2026-05-25.md` (measured, second-hand).
Confidence: HIGH that this is how the bot works (author's own text, detailed); but the bot is a learned
policy, so **no per-turn decision rules exist to copy** — only the action space, the training-target space, the
observation features, the inference procedure and the measured behaviour.

**What it is.** "a ResNet with PPO" — a convolutional policy network (about 101k parameters, 98k characters
submitted) that outputs, per cell, 13 action-type logits ("move, harvest, plant X, chop, pick X, drop, mine";
13 × 11 × 22 = 3146 logits) plus 144 "train-plan" logits. "There's no turn search/lookahead being done. As a
result, only the policy heads are needed after training." Inference "2-3ms out of the 50ms budget each turn".

**Per-turn procedure (verbatim from the gist):**
> - generate the obs from the current game state and run it through the network to get the train-plan logits
> - update the obs given the train-plan action chosen (max logit)
> - for each of my trolls:
>   - update the obs (just the active_troll plane needs to be updated)
>   - run inference to get the troll's action logits (the first "movement" logit of every valid cell it can go to, plus all the legal non-movement logits at the troll's current cell location)
> - given all the troll action logits, run a beam search over possible combinations of troll moves to find the highest probability moveset for all trolls (i.e. pick a troll, try each of its top X moves, use those moves to invalidate some other troll moves, pick the best moves for the next troll, etc)

So: one inference per troll plus one for the plan; a small beam search only to make the trolls' moves
compatible (no two trolls on one cell), never to look ahead in the game.

**Training plan (which trolls, when).** Decided each turn by the train-plan head: "scores each possible train
target separately … candidate features include target attributes, costs, deficits, and whether it matches the
previous target". Target space: "movement: 1-3, carry: 1-4, harvest: 0-2, chop: 0-3 … 3x4x3x4 = 144 possible
troll train targets"; "I masked troll targets with both harvest == 0 and chop == 0, and also masked troll targets
where harvest > carry"; target id 0 "was repurposed to mean 'done training trolls.'" The chosen target is fed back
into the observation ("train target: has target; target movement, carry, harvest, chop; costs; deficits"), so the
troll policy collects the resources for the current target. Measured result (game author's statistics, 673 Legend
games): games ended with 2 trolls 38 %, 3 trolls 27 %, 4 trolls 27 %, 5 trolls 8 %; average talents of the trained
trolls: Train 1 = 1.96/2.22/1.52/2.00, Train 2 = 2.47/3.35/0.98/2.50, Train 3 = 2.67/3.70/1.04/2.90,
Train 4 = 2.72/3.89/1.02/2.89 — i.e. a first extra worker that both harvests and chops, then carry-3-to-4,
chop-3 trolls with little harvest power.

**How it was made to work (the curriculum — the only "rules" the author imposed):**
- Level 1: "get a network to build a specific unit type that I specified (let's say for example: 3/4/0/1)" with
  reward shaping = "a rough calculation for how many turns it would take to collect the required resources … The
  network was given positive (or negative) rewards every time it moved closer (or farther away) from the target."
- Level 2: random targets, "As soon as the required resources are reached for its assigned target, then the
  corresponding train action is automatically carried out and a new random target is assigned to it."
- Level 3: "a random target number of trolls, between 2 and 5" and the true "endgame score difference"; "I gave
  the network 0.5 points immediately every time it deposited wood at its shack (and then counted its endgame
  wood as worth only 3.5 points)"; a temporary chop incentive.
- Level 4: freeze the troll-movement network, add and train a "troll plan selector" head on the pure endgame
  score difference (because letting the network choose targets with shaped rewards was gamed: "it would learn to
  build lots of cheap units to spam the completion bonus").
- Level 5: fine-tune everything on the endgame score differential; "It was truly remarkable to see how much the
  network improved in the final 36 hours of training."
- A first plain attempt (ResNet + PPO on the full game) "could never learn to mine iron, so it never ventured into
  higher tech units" (~25th at the time).

**Observation (what the policy sees, 104 planes on an 11 × 22 grid):** cell type one-hot; tree type/size/health/
fruits/cooldown; troll occupancy; the active troll's talents and cargo; opponent trolls' talents; distances to
both shacks, adjacency to iron/water; turn, both inventories, both scores, troll counts; the current train target
with costs and deficits; aggregate own/opponent talents (max, sum); "nearest useful target distance: plum tree,
lemon tree, apple tree, banana tree, mine target"; carried/free capacity; flags "own troll full, own full with
only wood/iron". The author: "I don't think the exact observation planes are all that important".

**Phases, planting, chopping, denial, endgame** — all learned, not written. The author's only description of
the resulting play: "The network learned to play many different styles depending on the map, sometimes choosing
to 'attack' or 'rush' (while still developing its economy back home), sometimes choosing to play a more macro
game". Measured behaviour (statistics file): trees planted per game by turn 295 — banana 21.4, lemon 8.8,
plum 8.3, apple 1.5 (a banana-heavy planter; by turn 100 already 1.9 plum + 2.6 lemon + 1.8 banana); wood in the
shack 1.8 at turn 50, 5.6 at 100, 14 at 150, 35 at 200, 67 at 250 (it deposits wood early and continuously —
consistent with the 0.5-point deposit shaping); own score 47 at turn 100, 85 at 150, 168 at 200, 296 at 250,
421 at the end versus 298 for the opponent; 525-146-2 record (78 % wins); games last 297 turns on average.

**Known weaknesses (author):** "getting stuck moving in an endless circle or getting stuck forever mining iron
… I tried to manually patch up each of these edge cases but several still remain"; "It still has some trouble
with basic path finding at times" (forum post #29).

---

## 2. norxondor_gorgonax (#2) — no write-up; statistics only

Sources: `norxondor_gorgonax-eulerschezahl.github.io-stats-2026-05-25.md` (measured by the game author over 616
Legend games, second-hand). Mentions only: TrollerPact "Contest Hall of Champions" lists norxondor_gorgonax,
delineate, yamo; Astrobytes' post-mortem: "big shout out to norxondor_gorgonax, fink_ployd and yaichi for giving
my bot all kinds of trouble throughout the contest". Confidence: LOW for any mechanism (nothing from the author);
MEDIUM for the measured habits below (averages over 616 games).

**Nothing found by the author.** No CodinGame forum account exists under this name (so no post in any thread);
no GitHub user (`norxondor`, `norxondor_gorgonax`; the unrelated account NORXONDOR has no CodinGame repositories);
web searches in five languages return only the xkcd comic the name comes from (queries in §7).

**Sketch from the statistics (what a program would have to reproduce):**
- Trains to 4 trolls in most games: games ended with 2 trolls 19 %, 3 trolls 28 %, **4 trolls 41 %**, 5 trolls
  11 %, 6 trolls 1 %.
- Talent ladder (averages): Train 1 = 2.09/2.08/1.66/1.65 (a balanced worker that can harvest and chop);
  Train 2 = 2.29/3.08/1.15/2.00; Train 3 = 2.36/3.10/0.45/3.00; Train 4 = 2.36/4.07/0.43/3.00 — the third and
  fourth trained trolls are chop-3 lumberjacks with carry 3–4 and (almost) no harvest power; movement stays
  around 2.3.
- Plants an orchard of the training fruits near home early: trees planted per game — lemon 11.1, plum 10.0,
  banana 8.7, apple 2.2 (by turn 50 already 2.9 lemon + 2.4 plum, twice delineate's early planting; bananas
  come late: 0.75 by turn 100, 2.8 by 150, 5.7 by 200).
- Stockpiles: plums in the shack rise steadily to 11 by turn 200 (surplus), lemons to about 8; bananas held at
  6–7 until turn 150 then spent (down to 5 at turn 250).
- Wood phase starts around turn 120–130: wood in the shack 1.7 at turn 100, 12 at 150, 39 at 200, 65 at 250;
  score 32 at turn 100, 79 at 150, 185 at 200 (faster than delineate's 168), 290 at 250, 366 at the end versus
  356 for the opponent — a thin margin, 345-267-4 record (56 % wins). Games are the shortest of the three
  (293.85 turns on average): some of his games end early (the referee ends a game early when a player can no
  longer lose or when the last tree is chopped).
- Reading: an economy bot with a deliberate 4-troll build (worker, then carry-3/4 chop-3 lumberjacks), a lemon and
  plum orchard first (lemons pay carry capacity, plums pay movement), then mass chopping from mid-game. Whether it
  denies the opponent, how it chooses targets, and how it searches are unknown.

---

## 3. Bubaptik (#3 on the ladder now) — nothing found

See `Bubaptik-NOTHING-FOUND.md`. Bubaptik is not one of the 69 Legend players of the contest's final standings,
has no forum account, no GitHub account, and no web page mentions the handle in connection with CodinGame or
anything else. Probably a post-contest entrant (the game reopened in the multiplayer section on 2026-05-26) or a
different name than in the contest. Only our own corpus can say anything about this bot.

---

## 4. MSz (#4 on the ladder now, #10 in the contest) — no Troll Farm write-up; statistics + his usual toolkit

Sources: `MSz-eulerschezahl.github.io-stats-2026-05-25.md` (measured over 634 Legend games, second-hand);
`MSz-github.com-marekesz-earlier-postmortems-2024.md` (his own post-mortems of OTHER contests; context only).
Confidence: LOW for mechanism, MEDIUM for the measured habits. Note the rank gap: his contest bot was #10
(27.25) and lost as often as it won (314-319-1); the #4 ladder entry (27.72) may be a later submission.

**Nothing about Troll Farm by the author.** His forum account (MSz, since 2020) posted post-mortems for
Cultist Wars (#1), Fall 2022 (#10), Spring 2023 (#1), Fall 2023 (#2), Summer 2024 (#1), Fall 2024 (#1), Winter
2024 (#2) — and nothing in 2026. His post-mortem repository `github.com/marekesz/contests` has one branch and its
last commit is 2025-01-29; no 2026 file.

**Sketch from the statistics:**
- Trains immediately: the average score falls from 12.6 at turn 0 to 8.2 at turn 15 (the starting shack fruits
  are spent on the first TRAIN within the first turns), then a cheap first worker: Train 1 = 1.67/1.70/1.47/1.00.
- Then two heavy lumberjacks with **carry 4 always**: Train 2 = 2.04/4.00/1.00/2.71, Train 3 = 2.05/4.00/0.00/2.87
  (no harvest power at all on the third). Never a fifth troll: games ended with 2 trolls 11 %, 3 trolls 42 %,
  4 trolls 47 %.
- Lemon farming for those carry-4 trolls (carry 4 costs 16 + number-of-existing-trolls lemons): lemons in the
  shack 1.9 at turn 25, 8.1 at turn 50, 10.5 at turn 100. Trees planted per game: lemon 9.3, banana 8.9, plum 8.6,
  apple 3.1 (plums early: 1.5 by turn 25, then almost none until turn 100).
- The strongest pure economy of the three: wood 1.1 at turn 100, 22.6 at 150, 52 at 200, 78 at 250; score 27.6
  at turn 100, 117 at 150, 250 at 200 (delineate: 168), 480 at the end — but the opponent also scores 481 on
  average, i.e. the bot does not deny and does not defend; it out-produces and gets out-produced.
- His usual toolkit (earlier post-mortems, NOT Troll Farm): an exact, heavily optimised simulation engine; hill
  climbing or beam search over sets of actions ("Nested beam search: The main beam search is over full turns …
  action sets for a turn are computed in independent beam searches with a very small width (2 or 3)"); "a mix of
  Hill Climbing and Hungarian algorithms" for assignment problems; hand-weighted evaluation ("Voronoi balance …
  distances to the resources, progressive evaluation of income and stored resources"); opponent modelled by a
  cheap greedy. It is a reasonable GUESS (flagged as such) that his Troll Farm bot is a simulation-based search
  with hard-coded train targets (2/4/1/3-ish) and a lemon-first economy.

---

## 5. Other top-25 write-ups found (all first-hand, forum thread of 2026-05-25/27 unless noted)

- **yamo (#3)** — already archived at `docs/reference/yann-moisan-postmortem-2026-05-26.txt` (2 trolls, chop everything, throughput scoring). Skipped here.
- **wala (#6, C++)** — "2 phases HARVEST/TRAIN then PLANT/CHOP (mostly banana trees). Training is hardcoded for 4 trolls (with round limits). As well as the number of trees needed close to the shack for each type (especially lemon…)". Each turn searches (a) a role per troll among HARVEST, PLANT_FROM_SHACK_SEED, PLANT_FROM_HARVESTED_SEED (per fruit), CHOP_TREE_AT, DROP, MINE, STEAL_OPPONENT_CHOP and (b) a priority order for cell conflicts; roles are simulated "until all the roles are done. Then the board is evaluated"; then random role switches for the remaining time. Tweaks: "If the opponent destroys our plants during training => stop planting them"; "During chopping, keep a banana tree close to shack to harvest." Statistics: 4 trolls in 94 % of games, 37 bananas planted per game.
- **laconic_pixel (#8, Rust)** — mission planner with task-level lookahead; three profiles chosen by map shape ("Max Build-Up" default: "Train, build a local fruit/banana engine, then convert into wood/score"; "Hard Disruptor" on "tight contested maps with good iron access"; "Resource Raid" against builders "where their build-up usually depended on planting lemons near the shack"). Jobs scored by completion time and payoff, team set chosen by a small DFS; beam/GA tried and rejected ("fantasy scenarios"). Training hard-coded with feasibility checks; "Once training became hopeless, the bot needed to immediately switch into building/scoring mode". Banana engine: "harvest bananas, replant them on good nearby cells, keep enough trees alive to sustain the loop, chop surplus trees when the wood ROI was better … eventually go into full cash-out mode".
- **xSkyline (#14)** — "I train a maximum of 4 trolls, each nth troll has its hard-coded list of stats, ordered from best to worst … the best affordable one that I estimate I can farm in a reasonable (but hard-coded) timeframe." Abstract multi-goal actions scored as score gained / total trip time; top-5 per troll, Cartesian product, nonsense combinations pruned; paths by conflict-based search with the "chop a contested tree" troll planned first so it "last hits" on time.
- **aangairbender (#16)** — "training 3 extra trolls with hardcoded skills"; tasks (harvest, chop, plant, mine, wait, drop) with `value`, `turns_to_complete`; Munkres assignment with edge cost `value * 0.9^turns_to_complete`; depth-2 beam search on completing the plan; plants a kind only if `current_produce_per_turn[kind] < desired_produce_per_turn[kind]`; "disallow planting if opponent troll is nearby. This pushed me straight to top15."
- **Konstant (#15, the Gold boss)** — "a 1-ply, goal-oriented approach with only 2 trolls": "rush to train the cutter, who destroys the opponent's trees starting with lemons"; "the other troll grows a banana forest, which gets chopped down in the endgame"; "defend against the opponent cutting my trees by co-cutting to save some wood".
- **FinkPloyd (#21)** — state machine with roles by stats; "quick chop" on small maps ("quickly train a troll and CHOP trees aggressively") versus "banana farm" ("TRAIN 3 trolls, then … 2 trolls to PLANT and 2 trolls to CHOP. The PLANTER prioritizes bananas because they are easier to CHOP"); "End game : every trolls CHOP the map"; on big maps "I simulate 300 turns with different TRAIN profiles to find the best combination" on turn 1; plants further away if the opponent steals trees.
- **eulerscheZahl (#23, game author, 2026-05-26)** — random macro actions (e.g. "move to a cell and plant there", biased to cells near shack/water) for a random troll, simulated 15 turns, kept if the score improves, plan carried to the next turn; TRAIN hard-coded (count and talents, "allowing for stronger trolls if the starting resources are high enough"); rewards "trees of each type close to the own shack, but with less weight for each additional tree"; "keep palms next to shack alive in late game and have dedicated planter trolls"; "initially I didn't go for carryCapacity = 4"; "some detection of an aggressive opponent to TRAIN sooner".
- **Ztrk (#24)** — genetic algorithm over task sequences per troll (harvest/chop/plant/mine, 6 tasks per troll), 50-turn simulation during training and 20 after, 3 trolls only; opponent model: a troll on a tree near my shack is assumed to chop it.
- **putibuzu (#30)** — 2 trolls (minimum 2/2/1/1, more if the turn-0 shack allows); PCD loop with bananas ("wait for size 2 for the killing blow"); "apple engine" on the ~40 % of maps with a grass cell adjacent to both shack and water (one troll harvests + drops one apple every two turns, matching the water-boosted apple regrowth); "lemon deny" when the opponent plants more lemons near its shack than the map had; ~30 candidate action combinations rolled out at depths 3/5/7/9/12 with a greedy policy; 3-ply beam on large maps, maximin on small maps; won't plant without enough turns left to chop and drop.
- **Escdemon (#37)** — one extra troll whose talents depend on how fast the resources can be reached (speed 3 if enough plums within 10 turns, 2 within 15, else 1; carry 3/2/1 by lemon time 20/25; chop 3/2/1 by iron time 5/20); harvest order iron → plum → lemon; chop priority `(wood gain * 100 + max(0, 10 - distToOppShack) * 10) / timeToChopAndDrop`; "plants and chops all starting bananas in the endgame near the shack, on the opposite side from the opponent's shack"; "a maximum of 11 trees per game".
- **Astrobytes / trlr1990 (game co-author; #1 when Legend opened)** — Kuhn-Munkres goal assignment then hill climbing over goal sequences (depth 25 with 5 goals per troll, later 15/4; ~300k iterations on turn 1, ~10k after); hard-coded troll attribute array; three phases with goal weights; planting skewed to water-adjacent cells near the shack; the "aha" was to drop the distance-based (Voronoi) tree ownership and "simply consider all trees as equally owned/unowned. This caused my bot to begin raiding and chopping opponent trees."
- Also in the thread (outside the top 25): 0x6E0FF (#43: training goal (2,2,0,2), `skill = sqrt(resource - nbtrolls)`, "reckless chop" without collecting the wood to delay the opponent's training), Regulus136 (#64: 2 planters + 2 lumberjacks, 3 trolls if a saboteur is detected), oidrissi (#59: taxonomy of 8 map types with a recipe each), Lanfeust (Gold: 2/2/2/(1–2) harvester then 3/4/1/(2–3) chopper; co-chop the opponent's chopper), celeria (2 specialised trolls).
- **Not found (write-ups):** yaichi (#4), bl4sterino (#5), uta_ccc (#7), skotz (#9), zasmu, siman, DaNinja, Halphas, gaha, DoubtinGiyov, icecuber, Bondo416, viewlagoon, tsukammo, Risen, FredericBautista, Stounate (#41), FreZzz (#51; only two rules questions in the puzzle thread), therealbeef (not in Legend). None of them posted in 2026 on the forum (checked each account's post history) and none has a findable blog/GitHub write-up (tsukammo's Japanese blog has rule summaries up to Summer 2025 only). Their statistics rows are in `all-legend-players-eulerschezahl-stats-2026-05-25.md`.

---

## 6. The ten most important algorithmic facts learned

1. **The winner has no rules to copy.** delineate's bot is a 101k-parameter policy network (ResNet, PPO) with one inference per troll plus one for the train plan, no lookahead, 2–3 ms per turn. What is copyable is its action/target spaces, its observation features, and its measured habits (banana-heavy orchard: 21 bananas + 9 lemons + 8 plums planted per game; trolls trained ≈ 2/2/1.5/2 then 2.5/3.4/1/2.5 then 2.7/3.7–3.9/1/2.9; 2 trolls in 38 % of games, 3–4 in 53 %).
2. **The curriculum is the real trick**: a network trained on the raw game "could never learn to mine iron"; delineate made it learn by rewarding progress toward a given train target (estimated turns-to-collect), then randomising the targets, then freezing the movement policy and training a separate target-choosing head on the pure score difference, then fine-tuning everything. Wood deposits were rewarded immediately (0.5 points, endgame wood counted 3.5) to teach chopping.
3. **Two economies coexisted at the top.** (a) Two trolls, one trained ≈2/2/0/2 chopper, that chop everything and/or run a pure banana plant-chop-drop loop (yamo #3, yaichi #4 with 42 bananas per game, skotz #9 with 39, Konstant #15, Escdemon #37, putibuzu #30); (b) three-to-four-troll build-up: hard-coded train targets, an orchard next to the shack (and next to water), then mass wood (norxondor and MSz by statistics, bl4sterino #5, wala #6, uta_ccc #7, laconic_pixel #8, xSkyline #14, aangairbender #16, FinkPloyd #21). The statistics show the #2 and #10 bots are of kind (b): norxondor ends with 4 trolls in 41 % of games and plants 11 lemon + 10 plum trees per game; MSz's second and third trained trolls always have carry 4.
4. **Late trolls are carry-4 / chop-3 lumberjacks with no harvest power** in the strong build-up bots (norxondor Train 4 = 2.4/4.1/0.4/3.0; MSz Train 3 = 2.05/4.0/0.0/2.9; bl4sterino Train 3 = 3.0/4.0/0.0/3.0; delineate Train 3–4 ≈ 2.7/3.8/1.0/2.9). eulerscheZahl: "initially I didn't go for carryCapacity = 4" — a mistake he corrected. Carry capacity is paid in lemons (cost = existing trolls + 4² = 16–19 lemons), hence the lemon orchard first and hence "lemon deny" as a counter.
5. **PCD — plant, chop, drop — converts 1-point fruits into 4-point wood; bananas are the currency**: fastest growth (cooldown 6, 4 next to water) and lowest health (3–6), "wait for size 2 for the killing blow" (putibuzu); "the other troll grows a banana forest, which gets chopped down in the endgame" (Konstant); FinkPloyd's planter "prioritizes bananas because they are easier to CHOP"; laconic_pixel's banana engine "harvest bananas, replant them … chop surplus trees when the wood ROI was better than keeping them as fruit production, and eventually go into full cash-out mode". Six of the top ten plant 27–42 banana trees per game.
6. **Target choice = value per turn of the whole trip**, everywhere: yamo `min(treeSize, carryRemaining) / (travel + chop + return)`; 0x6E0FF `(gain × priority) / (time to arrive + action time)`; Escdemon `(wood × 100 + max(0, 10 − distToOppShack) × 10) / timeToChopAndDrop` (a bonus for trees near the opponent's shack); xSkyline "score I would get divided by the total trip time"; aangairbender `value × 0.9^turns`.
7. **Team coordination is an assignment problem, then a short search**: Munkres/Hungarian (aangairbender, Astrobytes), DFS over compatible jobs (laconic_pixel), Cartesian product of the top-5 actions per troll with pruning and conflict-based-search paths (xSkyline), role + priority-order permutations simulated to completion (wala), GA over task sequences (Ztrk), random macro actions simulated 15 turns (eulerscheZahl). Long-horizon plan optimisation was tried and abandoned by several ("fantasy scenarios", laconic_pixel).
8. **Anti-griefing rules were the last big jumps**: co-chop any tree the opponent is chopping so the wood is shared (Konstant, Lanfeust, wala's STEAL_OPPONENT_CHOP, xSkyline's last-hit planning); "disallow planting if opponent troll is nearby" (aangairbender: top-40 → top-15); "If the opponent destroys our plants during training => stop planting them" (wala); plant on the far side of the shack (Escdemon) or further from spawn (FinkPloyd); detect an aggressive opponent and TRAIN sooner (eulerscheZahl) or switch to 3 trolls (Regulus136); stop the train-rush as soon as it is hopeless (laconic_pixel).
9. **Map classification decides the strategy before turn 1**: laconic_pixel's profile selector uses shack distance, contested resources, fruit/iron/lemon access; FinkPloyd simulates 300 turns of several TRAIN profiles on turn 1 on big maps, "quick chop" on small maps; putibuzu's apple engine only on the ~40 % of maps with a grass cell adjacent to both shack and water; Escdemon's talents from the turns needed to reach each resource; oidrissi's 8-map taxonomy; Astrobytes' "all trees equally owned" (no Voronoi) turned the bot into a raider.
10. **Endgame = everybody chops, and stop investing in time**: "End game : every trolls CHOP the map" (FinkPloyd); no planting without enough turns to chop and drop (putibuzu), "don't plant after turn 270" (0x6E0FF); training stops late (zLastEngineer, wala's "round limits"); "keep a banana tree close to shack to harvest" while chopping (wala); the referee ends the game early once a player cannot lose or the last tree is chopped (rules file), which is why norxondor's games average 293.85 turns against 297 for the others. Measured wood curves: MSz 52 wood at turn 200, norxondor 39, delineate 35 — the mass-wood phase starts near turn 110–130 for all three.

---

## 7. Queries tried (all on 2026-08-28; WebSearch unless noted)

General: `codingame "Spring Challenge 2026" feedback strategies troll farm`; `site:forum.codingame.com "Spring Challenge 2026"`; `"troll farm" codingame postmortem 2026`; `"troll farm" codingame spring challenge 2026 bot github`; `github "spring-challenge-2026" OR "SpringChallenge2026" troll farm`; `"codingame" "troll farm" 2026 blog strategy legend bot write-up`; `codingame spring challenge 2026 troll farm site:reddit.com OR site:habr.com OR site:zenn.dev OR site:qiita.com`; `codingame "Troll Farm" 2026 youtube OR twitch stream bot`; Russian `codingame "troll farm" … ферма троллей OR "тролль" бот стратегия`; Japanese `codingame "Spring Challenge 2026" 参加記 OR 振り返り OR トロール`; French `codingame "troll farm" 2026 stratégie OR "post mortem" OR retour d'expérience`; Polish `codingame "troll farm" 2026 strategia OR podsumowanie OR "bot" polski`; `dev.to epigene codingame 2026 spring challenge trolls`. GitHub API repository searches: `troll farm codingame`, `spring-challenge-2026`, `SpringChallenge2026`, `trollfarm`, `codingame 2026 spring` (found: the official referee, Astrobytes' post-mortem, and bot repositories by babilonio, agiordan101, tdkkdt, J35P1N, njaros, Epigene, lankev, Homnibus, codingame-team — none by a top-20 player, none with a strategy write-up beyond agiordan101's French notes on a macro-action MCTS and njaros' to-do list).
Per player: `delineate codingame "troll farm"`; `"delineate" codingame neural network bot gist OR blog OR postmortem`; forum post history of `delineate` (Discourse user_actions); `norxondor_gorgonax OR norxondor codingame`; `"norxondor_gorgonax" OR "norxondor gorgonax" codingame troll farm second place bot`; GitHub user search `norxondor`, `norxondor_gorgonax`; forum `/u/norxondor_gorgonax` (no account); `Bubaptik codingame`; `"Bubaptik"`; `"Bubaptik" OR "bubaptik" bot OR codingame OR leaderboard OR github`; GitHub user search `Bubaptik`; forum `/u/Bubaptik` (no account); `MSz codingame "troll farm" OR "spring challenge 2026"`; `"MSz" codingame legend poland bot contest`; `marekesz contests codingame troll farm 2026 post mortem`; forum post history of `MSz`; GitHub `marekesz/contests` tree, branches and commits.
Secondary players: `yaichi OR skotz OR Stounate codingame "troll farm" 2026 strategy`; `tsukammo OR yaichi OR uta_ccc codingame 2026 Troll Farm 参加 OR ブログ`; `skotz OR icecuber OR therealbeef codingame "troll farm" OR "spring challenge 2026" github OR blog`; `"tdkkdt" codingame`; forum post histories of yaichi, Stounate, skotz, therealbeef, Risen, viewlagoon, gaha, tsukammo, Bondo416, FreZzz, DoubtinGiyov, FredericBautista, bl4sterino, uta_ccc, zasmu, siman, DaNinja, icecuber, Halphas, trlr1990.
Not reachable from here: the CodinGame Discord (not indexed), X/Twitter (not indexed), CodinGame profile pages (the CodinGame API is off-limits by the task rules).

## 8. Files in this directory

- `SUMMARY.md` — this file.
- `delineate-gist.github.com-2026-05-25.md` — the winner's gist, verbatim. `delineate-forum.codingame.com-2026-05-25.md` — his two forum posts plus the questions he answered. `delineate-eulerschezahl.github.io-stats-2026-05-25.md` — measured statistics.
- `norxondor_gorgonax-eulerschezahl.github.io-stats-2026-05-25.md` — measured statistics (the only source).
- `Bubaptik-NOTHING-FOUND.md`.
- `MSz-eulerschezahl.github.io-stats-2026-05-25.md` — measured statistics. `MSz-github.com-marekesz-earlier-postmortems-2024.md` — his 2024 post-mortems (other games), verbatim.
- `contest-forum.codingame.com-feedback-strategies-thread-2026-05-25.md` — the whole thread, 35 posts verbatim; per-player slices: `Konstant-…`, `putibuzu-…`, `aangairbender-…`, `Escdemon-…`, `xSkyline-…`, `laconic_pixel-…`, `wala-…`, `Ztrk-…`, `FinkPloyd-…`, `eulerscheZahl-forum.codingame.com-2026-05-26.md`, `astrobytes-forum.codingame.com-2026-05-27.md`.
- `astrobytes-github.com-2026-05-27.md` — Astrobytes/trlr1990 post-mortem, verbatim.
- `all-legend-players-eulerschezahl-stats-2026-05-25.md` + `.json` — one row per Legend player (69), full time series in the JSON.
- `contest-rules-statement-github.com-eulerscheZahl-Troll-Farm.md` — the top-league statement text and the referee README. `contest-forum.codingame.com-puzzle-discussion-2026-05-26.md`, `contest-forum.codingame.com-contest-discussion-2026-05-13.md` — the two side threads (rule clarifications), verbatim.
