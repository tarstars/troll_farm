# Spring Challenge 2026 (Troll Farm) - Feedback & Strategies — the whole forum thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241
- Fetched: 2026-08-28 via the Discourse raw endpoint `https://forum.codingame.com/raw/208241?page=1` (all 35 posts, markdown source as posted)
- Dates: 2026-05-25 to 2026-06-06 (each post carries its own UTC stamp)
- Authors: eulerscheZahl (game author), Konstant, Flamefire, putibuzu, VXT22, zLastEngineer, mike82, aangairbender, Escdemon, xSkyline, Regulus136, Lanfeust, oidrissi, delineate, 0x6E0FF, Baal, Astrobytes, laconic_pixel, yamo, Illedan, Ztrk, wala, FinkPloyd, Di_Masta, celeria
- Language: English
- Note: `upload://...` links are forum image attachments (screenshots), not archived. Post #15 is delineate's link to his gist (archived separately as `delineate-gist.github.com-2026-05-25.md`).

Archived by W1 (internet worker) for the reconstruction of the top players' algorithms. Nothing below this line was written by us.

---

eulerscheZahl | 2026-05-25 12:16:27 UTC | #1

The contest has come to an end, but the game will soon return to the multiplayer section. Therefore don't share large chunks of code please.

Huge shout-out to CodinGame for making this Community Contest possible and thanks to everyone for participating.

We generated some [statistics for legend league players](https://eulerschezahl.github.io/TrollFarm/troll_stats.html).
How did you like the game?
What approach did you take?
[details="And most importantly: how many Easter eggs did you find?"]
Most of them appear on fixed map seeds and do something when clicked:
[Turtle](https://www.codingame.com/replay/890944416)
![turtle|238x254](upload://u8f2Qd1swZfKipz81gUshgbgvJx.gif)
[Cat and bird](https://www.codingame.com/replay/890944568)
![cat2|272x236](upload://tEMXynNVxA1FZY1syS5fglKPt3t.gif)
[Toad](https://www.codingame.com/replay/890947390)
![toad|158x136](upload://oyYwrnnF6dYGhLOq1MlaSenY76O.gif)
[Fish](https://www.codingame.com/share-replay/890947481)
![fish|220x214](upload://whAgaxs0iXBkNZAu39YX6520zEy.gif)
And then there is the worm that randomly appears, regardless of the seed or replay
![worm|214x204](upload://knNKnsPuUGYNntAV28ksqDBFBHG.gif)
[/details]
The top 3 will receive an honorable mention on the [TrollerPact website](https://www.trollerpact.com/).

-------------------------

Konstant | 2026-05-25 13:55:17 UTC | #2

15th

Got lucky that my bot became Gold Boss.

![gold boss|690x261](upload://yCAsnn2rB94FO2Ag5cJqHNnBSXY.png)

The cutoff for creating the Legend League was at 15th place. It felt great thinking that my bot fought against so many opponents as a boss.
So to everyone struggling with Gold Boss - you’re welcome :slight_smile:

The strategy was a 1-ply, goal-oriented approach with only 2 trolls, to keep things simple and avoid deep calculations:

* rush to train the cutter, who destroys the opponent’s trees starting with lemons
* the other troll grows a banana forest, which gets chopped down in the endgame
* defend against the opponent cutting my trees by co-cutting to save some wood

A huge advantage of this game is that you can actually understand what’s happening in the replay and visually spot where your bot has weak points and what needs improvement. It’s easy to turn straightforward tactical ideas into code. Decision-making matters more than perfect execution.

This is one of the best multiplayer contests ever.

* extensive gameplay that allows many different strategies
* full of humor: funny animations, easter eggs, and the prompt injection in the statement for AI really got me :slight_smile:
* amazing support and help from the creators, it felt like eulerscheZahl was available 24/7 answering every question
* everything worked perfectly from the start: no bugs, compiled game .jar, excellent balance, very well-designed gameplay
* innovative time measurement that minimizes server lag effects. A huge QoL improvement

The game creators did a great job. Thanks to everyone involved. I could really feel the atmosphere of the game, and the slight trolling vibe from the creators made it feel immersive as a community contest.

This is exactly the kind of contest CodinGame needs!

-------------------------

Flamefire | 2026-05-25 08:25:12 UTC | #3

1-ply only? Congrats! I guess you stored your strategy over turns somehow? I had trouble with my trolls deciding on another goal after moving towards one and lacked the time to fully fix this. In the end I had mysterious timeouts I couldn’t reproduce locally and then find fast enough online.

> the prompt injection in the statement for AI really got me :slight_smile:

Haven’t seen it, but awesome idea if it was there. Do you remember what it was?

And I can just +1 to what you said: Great contest! Only 1-2 days more would have helped me, but agreed that everything worked very well. I only had some sporadic errors from the referee, but providing a compiled, runnable jar definitely was a nice addition.

-------------------------

eulerscheZahl | 2026-05-25 08:52:38 UTC | #4

[quote="Flamefire, post:3, topic:208241"]
Haven’t seen it, but awesome idea if it was there. Do you remember what it was?
[/quote]

Our initial idea was this:
[details="click to expand"]
![image|690x265](upload://wjSNqeYPEXPRJO70JRWRR5Ty6Uw.png)
![image|417x499](upload://yNBPLwdxGTYMR9Iylc2x8jJsjxq.png)
![image|690x444](upload://gVjRb0B1sf763dP5WUf5BqJvbsC.png)
![image|651x500](upload://xgJ3WD0MA0BsAvhKChOjRXak74Y.png)
[/details]
This was really the only time that CodinGame said no - and I can understand it, not complaining about it.
We had something to replace variable names by Duckburg characters at the start. But a bit of a misunderstanding, the prompt injection got removed about 1 hour after contest launch.

-------------------------

putibuzu | 2026-05-25 09:17:59 UTC | #5

My 2nd time ever reaching legend in a Contest :partying_face: !

# The Game

Before the balance patch I was a bit disappointed, I thought it was quite narrow strategy-wise due to the close distance to opponent. Afterwards, it got much better. I was especially impressed by those “hyperscale“ approaches with carry capacity 4. 
One of my favorite games on the platform for sure as it can be considered to be a RTS game and as a SC2 enthusiast this resonates with me. 
I especially like the map variability.

# My approach

## Training

Early on before the balance patch I figured that it is not worth it to go for a 3rd troll altogether due to the unfavorable cost scaling. I was proved wrong later. But I stuck with that strategy until the end. The training logic is simple: We want to train at least 2 movement speed, 2 carry capacity, 1 harvest power and 1 chop power. If the starting inventory in shack allows this turn 0 we go for the maximally possible stats we have. Otherwise we harvest the needed resources to get there, with some additional logic to get to chop power 2 depending on how long that would take the initial troll to mine that.

## Core bot logic

Crazy overcomplicated bot to be honest in the end. Probably I could throw out much of it and it would perform the same or better even. Since in the end I added override switches here and there most of it is anyways obsolete when it matters. 

**Core economy**: Plant-Chop-Drop (PCD): The main scoring loop picks expendable fruit from the shack, plants it on an adjacent cell, chops the resulting tree for wood (4 pts each), and drops at shack.
This converts 1-pt fruit into 4-8 pts of wood. Bananas are preferred since they grow fastest and we can then wait for size 2 for the killing blow.

**Apple engine:** This was probably my biggest edge, and I didn’t see any other players running it. I ran an analysis over 4000+ maps and found that \~40% have a grass cell adjacent to both the shack and
water — the perfect setup for a dedicated apple troll. On those maps, one troll permanently camps that cell maintaining an apple tree. The math works out perfectly: the starting troll takes exactly two turns to harvest + drop one apple, which is exactly how long a water-boosted apple tree takes to regrow a fruit. So one troll runs this loop at 100% efficiency with zero idle turns. The apples feed the PCD loop as infinite planting fuel, making the economy fully self-sustaining — once it’s running I never need to send trolls across the map for fruit. However, as apples are inefficient to chop down, this actually very rarely mattered. A state machine handles the full lifecycle —
plant, wait for growth, harvest, drop, replant when destroyed. If an opponent chops the tree, the troll keeps harvesting until the tree is about to die. Then it chops to get one wood from the tree. As a bonus, the apple tree sometimes acts as bait: apple trees are tanky, so opponent trolls invest several turns chopping it down while we keep harvesting, and even when it dies we still get at least one wood out of it. This worked well on some maps against the gold boss.

**Lemon deny:** This was bolted on pretty hacky near the end, but it’s what got me to Legend. If the opponent plants lemons near their shack (detected by counting lemons near enemy shack exceeding the natural map count), the 2nd troll is sent to seek and chop them. Only fires on large maps where the opponent likely runs a hyperscale strategy, relying on getting many lemons for carry capacity 4 trolls. Once detected, the flag never resets — even if we already chopped their lemons.

**Action selection:** Each turn I generate \~30 candidate action combinations by enumerating top-3 tree targets plus local actions per troll. Each candidate is rolled out forward at 5 depths (3, 5, 7, 9, 12 turns) using a greedy policy for both sides, averaged. On large maps, a 3-ply beam search (5→3→all) picks the best action sequence. On small maps, I also generate opponent candidates and pick the
maximin action from the payoff matrix for robustness against direct interference.

**Greedy policy** (used both for action generation and rollout): Priority cascade — plant if on valid cell with fruit → drop if carrying → chop/harvest based on value-per-turn → pick fruit for PCD → move to best tree. Idle trolls assigned via brute-force optimal matching over available trees. Trolls get a small bonus for sticking to last turn’s target to avoid oscillation.

**Evaluation heuristics:** Score differential plus carried resources discounted by distance-to-shack, tree proximity weighted by ownership, and a strategic term valuing future tree production. Won’t plant if there aren’t enough turns to chop and drop before game end.

**Collision handling:** Post-processing detects friendly trolls landing on the same cell and redirects the lower-priority one. The apple engine troll gets priority on its cell.

**Opponent model:** Simulated using the same greedy policy with a different training build order (multiple cheap trolls vs one strong troll).

-------------------------

VXT22 | 2026-05-25 11:17:46 UTC | #6

I reached 390th global using Reinforcement Learning. Has anyone else tried this and want to exchange some strategies?

-------------------------

zLastEngineer | 2026-05-25 13:27:33 UTC | #7

## Spring Challenge 2026 Post-Mortem - Rank 723 / 2022 (127th Silver)

I finished the Spring Challenge 2026 at rank **723 out of 2022**.

Overall, I’m fairly happy with the result. My bot was not extremely advanced, and I didn’t manage to build a full simulation-based strategy, but it had a solid greedy economy, some role specialization, and a few tactical ideas that worked well enough to beat a good part of the field.

### Core strategy

My bot was mainly based on a simple economic loop:

1. Find valuable trees.

2. Send trolls to harvest fruits.

3. Return to the shack and drop resources.

4. Use one troll as a dedicated chopper/saboteur.

The general idea was to keep most trolls focused on farming while assigning the best troll for chopping tasks. The chopper was selected using a heuristic based on carry capacity, movement speed, and chop power.

The remaining trolls were mostly used as farmers. They would search for good harvest targets, move using BFS, harvest when possible, and return to the shack when carrying resources.

### Role assignment

I used a simple role separation:

* **One chopper troll**: usually responsible for chopping useful trees or attacking trees near the opponent’s shack.

* **Farmer trolls**: focused on harvesting and dropping fruits.

* **Training logic**: the bot could train additional trolls during the early and mid game, but stopped doing so later in the game to avoid wasting resources too close to the end.

This worked reasonably well because it gave the bot a stable economy without overcomplicating the decision-making.

### Tree scoring

The bot used a heuristic scoring function to choose which trees were worth targeting. The score took into account things like:

* distance from the troll;

* distance from my shack;

* available fruits;

* tree size;

* cooldown;

* whether the tree was useful for harvesting or chopping.

This was not a perfect evaluation, but it was good enough to avoid many bad choices and keep the trolls active most of the time.

### Pathfinding and collision handling

Movement was handled with a BFS-based pathfinder. This was one of the more reliable parts of the bot. It allowed trolls to navigate around trees, shacks, and other blocked cells instead of relying on a naive greedy movement.

I also had a basic reservation system to avoid sending multiple friendly trolls to the same cell. It was not a full collision prediction system, but it helped reduce obvious friendly blocking.

### Sabotage

One important part of the strategy was sending the chopper to cut trees close to the opponent’s shack.

The idea was simple: trees near the enemy shack are usually very valuable because they are easy to harvest and drop from. By chopping them, I could slow down the opponent’s economy while gaining some wood myself.

This worked well against some greedy bots, but it was still quite basic. The bot did not really detect the opponent’s long-term strategy; it mostly applied pressure opportunistically.

### Planting

My bot had some planting logic, but it was not the core of the economy.

It could plant near my shack, especially when the position looked useful, but I limited the number of planted trees quite aggressively. In hindsight, this was probably one of the biggest missed opportunities.

After reading other post-mortems, I realized that some stronger bots used planting as a central economic engine, especially by converting low-value fruits into wood through a plant-chop-drop loop. My bot treated planting more as a bonus than as a primary scoring engine.

### What worked well

The strongest parts of my bot were:

* simple but stable farming;

* BFS movement;

* role separation between farmers and chopper;

* basic anti-collision handling;

* opportunistic sabotage near the opponent’s shack;

* not overtraining too late in the game.

The bot was not very clever, but it was consistent. It usually managed to keep doing useful actions instead of idling too much.

### What did not work well

The biggest weaknesses were:

* no deep simulation;

* weak opponent modeling;

* no real multi-turn planning;

* planting was underused;

* no advanced map-specific strategy;

* no strong detection of enemy economy patterns;

* target assignment could still be inefficient;

* the bot sometimes committed to local greedy decisions instead of building a stronger long-term economy.

I think the lack of simulation was the main limitation. The bot chose actions mostly based on immediate heuristic value, while stronger bots were able to evaluate future outcomes several turns ahead.

### What I would improve

If I had more time, I would probably focus on three things.

First, I would build a proper plant-chop-drop economy. Instead of only harvesting what already exists on the map, the bot should create its own scoring engine by planting trees near the shack, growing them, chopping them, and dropping the wood.

Second, I would improve opponent modeling. At minimum, the bot should detect when the opponent is building a strong local economy and react by denying key trees.

Third, I would add a lightweight rollout system. Even a shallow simulation of a few candidate actions over several turns would probably outperform my purely greedy decisions.

### Final thoughts

This challenge was a good reminder that in CodinGame bot contests, movement optimization is not enough. The biggest gains often come from identifying the main economic loop of the game and building the whole bot around it.

My bot had a decent greedy economy and some useful tactical ideas, but it never fully became a strategic economy bot.

Still, finishing **723 / 2022** with this approach feels like a respectable result, and I learned a lot from the challenge.

-------------------------

mike82 | 2026-05-25 14:21:00 UTC | #8

@eulerscheZahl (and others) thanks for great Contest.

As usual end in silver league :slight_smile:

Simple logic, try to train one new troll, then only plant and chop banana trees :smile:

-------------------------

aangairbender | 2026-05-25 12:07:32 UTC | #9

Top 16 legend. Thanks to TrollerPact and CG for the amazing contest.

# General Strategy

I am training 3 extra trolls with hardcoded skills.
My bot consists of 3 steps:

1. Game state analysis

* assign each resource value based on what’s needed to train the next troll
* compute a list of best planting spots (either near shack or near water)

2. Planning
   I generate bunch of high-level tasks (harvest, chop, plant, mine, wait, drop. Each tasks has following functions:

* `value(troll)` - how much benefit would I get if task would be completed by given troll
* `turns_to_complete(troll)` - how much turns left to complete the task by given troll
* `movegen(troll)` - generate action(s) which would advance the given task assuming its being completed by given troll

I allow only 1 plant task per tree kind.

Then I run assignment algorithm (Munkres) to find the best (max) matching between trolls and tasks. The edge cost is `value * 0.9^turns_to_complete`.

This produces a plan - a task for each troll.

3. Search

I have shallow (depth 2) search with eval being sum of `turns_to_complete` of each task in the plan. Basically I am looking for sequence of actions which would complete the plan the most.

I am using beamsearch, but amount of states is very low, so bruteforce could be used instead (my bot uses 0ms per turn).

# Planting

for deciding which tree still needs to be planted I compute 2 values for each tree kind:

* current_produce_per_turn - how much of given resource is produced every turn (sum of some formula for each tree)
* desired_produce_per_turn - how much of produce per turn I need to train all my trolls (some simple formula)

I only plant a tree if `current_produce_per_turn[kind] < desired_produce_per_turn[kind]`.

Once I know which tree kinds I want to plant, I run another assignment algorithm to assign each kind to a good planting spot. The edge cost is increase of produce per turn I get from planting given tree kind in a given spot.

# Trick to fight aggro choppers

30min before contest ended I was top40 and was losing a lot to aggressive chopping bots. I noticed that my trolls kept wasting fruits by planting trees just for those trees to be chopped few turns later. So I added a condition to disallow planting if opponent troll is nearby. This pushed me straight to top15.

-------------------------

Escdemon | 2026-05-25 12:15:11 UTC | #10

**37th Legend**

Thanks to @eulerscheZahl and everyone who contributed to this contest! The last time I got this hyped to code a heuristic bot was for CodeBusters.

**Strategy**
I started with a troll who chops everything possible on the map and decided to stick with it to see how it could match the optimized plantation strategy.

**Training**
I only train one additional troll with stats depending on resource proximity :

*Movement speed:*

* 3 if I can harvest enough plums in less than 10 turns,
* 2 if in less than 15 turns,
* 1 otherwise.

*Capacity:*
If I need more than 15 turns to reach 10 lemons (for 3 of stat) or 5 lemons (for 2), my first troll plants a lemon tree near water if the closest tile is within 2 range of my shack.

* 3 if I can harvest enough lemons in less than 20 turns,
* 2 if in less than 25 turns,
* 1 otherwise.

*Harvest power:* 0.

*Chop power:*

* 3 if I can harvest enough iron in less than 5 turns,
* 2 if in less than 20 turns,
* 1 otherwise.

I harvest in this order: iron → plum → lemon, to let the fruits grow while I collect the iron.

**Chopping**

* Once I have two trolls, I send them to chop trees with this priority:
  `(wood gain * 100 + max(0, 10 - distToOppShack) * 10) / timeToChopAndDrop`
* Each troll drops wood if it is full or if it is closer to the shack than to the next tree.
* My initial troll chooses its target tree first.
* I use default pathfinding when outputting MOVE.

**Banana farming**
My first troll plants and chops all starting bananas in the endgame near the shack, on the opposite side from the opponent’s shack, to avoid body blocking.
I plant a maximum of 11 trees per game. I wanted to be the highest rank with the least planting. 😄

My bot was really strong before last weekend where people started to add security against griefing.

-------------------------

xSkyline | 2026-05-25 16:03:55 UTC | #11

#14 Legend

**Training**
I train a maximum of 4 trolls, each nth troll has its hard-coded list of stats, ordered from best to worst. I'm going for the best affordable one that I estimate I can farm in a reasonable (but hard-coded) timeframe.

**Action generation**

I generate a list of abstract actions for each troll, using a separate evaluation function for each type of action (harvest, plant, chop) that computes some value related to the score I would get divided by the total trip time. Some actions might only be considered depending on the game stage (early vs late)

Each abstract action contains a list of goals that need to be performed in sequence, some are simpler: `harvest lemon at x, y → go to shack → drop`
can be in a different order: `go to shack → drop → harvest lemon at x,y -> drop`

while others can be more complex: `harvest lemon tree at x,y → go to shack → drop → chop tree at x’,y’ → drop`\- this one can help with continuing to harvest while still making sure my troll will get to last hit the tree currently being chopped by my opponent.

Action evaluation functions contain a convoluted mess of operations and constants that make it impossible to add new behavior, which is why my agent has many unpatched weaknesses that I couldn’t bring myself to try and solve.

**Planning**

I take the top 5 actions for each troll and generate the Cartesian product to build the collection of joint actions. I discard nonsense actions here like harvesting a tree with troll 1 that will get chopped by troll 2 in an earlier turn, I allow 2 trolls to harvest the same tree but I recompute the harvest score for the 2nd troll to account for the fruits the first one will grab, I don’t allow 2 trolls to plant the same type of fruit, etc. Joint action score is the sum across the scores of each troll, and I feed the best one to my path planner (conflict based search) which builds way-points for each troll and finds the collision-free paths for each that minimizes the total trip across all paths. If one of my troll’s goals is “chop a contested tree” he gets prioritized first and his path is baked in before doing CBS, to make sure he reaches the tree to last hit at the time computed in the generate action phase. I also had to bake in the cells occupied by a troll currently chopping/harvesting/dropping for the respective duration, but only if he’s already there to make sure he doesn’t get interrupted.

**About the game**
Pros: very complicated, very strategical
Cons: very complicated, very strategical
I liked the game graphics, cover art, and the game overall.It was about time for a heuristic style game on CG but it did cause me much exhaustion in the past 2 weeks .

Many thanks to fellow competitors, to the creators of the game, especially to @eulerscheZahl for being on point with everything on Discord, and to codingame for keeping these going.

Congrats to  #1 @delineate who absolutely crushed the leader-board with his final submission, and to @laconic_pixel who managed to stay in the top 10 for pretty much the entire duration of the contest.

-------------------------

Regulus136 | 2026-05-25 12:52:52 UTC | #12

**64th - Legend**

**General Strategy**
I focused on training a set of specialized trolls, then maintaining a stable production loop.

The bot runs in two main phases:

1. Training Phase
   *Standard plan*: 4 specialized trolls
   The default strategy is to train 4 trolls, each with a defined role: 2 planters + 2 lumberjacks
   *Fallback plan*: 3 trolls if a saboteur is detected
   If the opponent shows a disruptive profile, the bot switches to a safer 3‑troll plan: 2 planters + 1 lumberjack


2. Harvesting Phase
   Once the team is trained, the bot focuses on maintaining fruit and wood production

**Limitations**

* Greedy mission assignment
* No multi‑turn simulation
* No active opponent strategy (no blocking, stealing, or harassment)
* Late game too neutral, lacking aggressive optimization.

**Final Thoughts**
Thanks to the game authors and to CodinGame for this great contest.

-------------------------

Lanfeust | 2026-05-25 13:24:08 UTC | #13

### 89th (20th Gold)

It has been said a lot, but it is worth repeating : thanks for a great contest ! I wouldn't have thought at the start that very different strategies could all have a chance against each-other.

### Basic approach

As I usually do, I started with a basic heuristics bot, but here it seems to work well enough that I stayed with it, instead of using it to benchmark a search-based algorithm (for which there was no obvious direction anyway).

#### Preferred strategy is farming

- make sure there is at least one tree of each building resource nearby, if not plant using a seed from the shack

- then go for a 2/2/2/(1 or 2) "harvester" (depending of iron availability)

- then a 3/4/1/(2 or 3) "chopper"

- the chopper is sent to annoy opponent while making wood, while the two first trolls build a second chopper

- then switch to plant bananas with the first two trolls, and chopping the palm trees with the chopper(s)

This worked well enough to reach top third of Gold, but then I saw how I was getting trounced by the Gold Boss, so I tried to defend against that...

#### Against barbarians

- when identified, adjust training objectives, taking into account what resources are likely to really be available, and probably don't try for any more troll beyond that

- when opponent troll is chopping one of "our" trees that is close enough, switch task to share the wood. This was extremely effective against the Gold Boss, where in practice there were two trolls neutralizing each-other, and two left to themselves, except that on my side I would bring the wood back, and take a big lead in score

That brought me to top Gold, with a 11.5/0.5 win rate against the Boss in the IDE, but not enough to reach Legend. As there was plenty of time left, and I had a few ideas for improvement, I had good hopes, but I was disappointed that nothing really worked (for instance, harvesting one banana before chopping, then immediately replanting, seems 4 points of wood is too expensive...). My final bot was marginally better against the previous one, but not as efficient against the Boss, it reached #2 Gold at some point (a bit better than the previous one), but eventually drifted to #20.

If I bring to myself to get back to it, I might try to improve trolls coordination (as opposed to just not blocking themselves too much), or try a search approach, now that I have a better idea at what to aim for.

-------------------------

oidrissi | 2026-05-25 14:23:32 UTC | #14

#59th Legend - Python:

Day 1: Made a simple python Bot, make two trolls? → harvest. Now have two trolls? –> go chop everything, else continue gathering harvesting for recipe.
Day 3: Implemented Planting logic but still never realizing planting is not only for training but also scoring endgame, at this point the idea was: maximize the stats of the trolls we send to chopping.
Day 4 - 8: Trying to port the python mess to CPP, realized after 4 days i’m gonna throw my pc away if I continued, abandoning any optimization.
Day 9-12: Launching 1000+ games locally with 4 threads, classifying gold maps per features as shack to shack distance, number of walls etc. Ended up with a Taxonomy of 8 maps. Created a specific recipe per map + improved a bit greedy actions towards recipe (but can only sim 1 planter, otherwise bot exceeds 50ms multiple times and crashes). Biggest bottleneck. Was at 33% against gold boss but I think my bot had more versatility per map so it won against top 10 pretty consistently and I got pushed to Legend last night.

No opponent modeling was written, as my bot was frolicking timeouts without it.

Btw, it’s not until 1 day ago that I realizedthe “optimal” strat is to plant near shack as much as possible/harvest/chop cycle.
Pretty happy with the result, still pissed about my failed cpp port as It could have yielded more plantations and overall possibilities.

Amazing job by CG, thanks Euler and praying for another contest ASAP (it’s becoming addictive, should I see a doctor? :smile:
PS: It is me or maps in Legend look huge/separated/more dense than other leagues? It felt like I was playing a different game, all my previous taxonomy failed.

-------------------------

delineate | 2026-05-25 16:58:33 UTC | #15

An overview of my strategy for this competition (#1): https://gist.github.com/delineate/93ba9d48102e442e764db39d85ac44a3

-------------------------

zLastEngineer | 2026-05-25 18:10:37 UTC | #16

## Wood 2 Strategy

My Wood 2 bot was based on a very simple greedy farming strategy.

At this stage, I did not try to build a complex economy, train advanced trolls, chop trees, plant new trees, or simulate future turns. The goal was mainly to create a reliable baseline bot that could understand the map, move toward useful resources, harvest fruits, and bring them back to the shack.

### Core idea

The main loop was:

1. If a troll is carrying resources and is next to the shack, drop them.

2. If a troll is carrying resources but is not next to the shack, move back to a valid cell adjacent to the shack.

3. If a troll is standing on a tree with available fruits, harvest it.

4. Otherwise, move toward the nearest tree that currently has fruits.

5. If no tree has fruits, wait.

So the bot followed a simple harvest-and-drop cycle.

### Movement

For movement, the bot used Manhattan distance to select the closest fruit tree.

It did not use advanced pathfinding at this stage. The target was chosen by comparing the distance between the troll and each tree with fruits, then selecting the nearest one.

When returning resources, the troll did not move directly onto the shack. Instead, it moved to a valid adjacent grass cell, because dropping resources requires being next to the shack.

### Resource handling

The bot did not distinguish strongly between fruit types. Any tree with available fruits was considered useful.

This made the strategy simple and stable, but also limited. The bot was not yet trying to optimize specific resources for training, planting, or long-term planning.

-------------------------

zLastEngineer | 2026-05-25 18:13:59 UTC | #17

## Wood 1 Strategy

My Wood 1 bot was still a simple greedy farming bot, but it was already more structured than the Wood 2 version.

The main objective was to build a stable resource loop: harvest fruits, return them to the shack, drop them, and use the collected resources to train a few basic trolls.

### Core idea

The bot followed a very simple priority system for each troll:

1. If the troll is full and next to my shack, drop the resources.

2. If the troll is full but not next to my shack, move back to a valid cell adjacent to the shack.

3. If the troll is standing on a tree with available fruits, harvest it.

4. Otherwise, move toward the closest tree with available fruits.

5. If no fruit tree is available, wait.

So the basic loop was:

```
move to fruit tree → harvest → return to shack → drop
```

### Troll training

Unlike the earliest version, this bot also trained additional trolls.

The goal was not to build specialized units yet. Instead, the bot trained simple balanced trolls with:

```
movementSpeed = 1
carryCapacity = 1
harvestPower = 1
chopPower = 0
```

So the training action was:

```
TRAIN 1 1 1 0
```

The bot trained up to **3 trolls**.

The cost was estimated based on the current number of my trolls. If I had enough plums, lemons, and apples in the shack, I trained another basic harvester. Otherwise, I waited until enough resources were collected.

### Target selection

Tree selection was very simple.

For each troll, the bot looked for trees with available fruits and selected the closest one using Manhattan distance.

To avoid all trolls going to the same tree, I used a small claiming system:

```
claimedTrees
```

When a troll selected a tree, that tree was marked as claimed, so the next troll would prefer another tree if possible.

If all useful trees were already claimed, the bot could still fall back to the nearest available fruit tree.

### Movement

The movement system was still simple.

The bot did not use BFS or advanced pathfinding. It directly issued a move command toward the selected target cell.

For dropping resources, the bot selected the first valid grass cell adjacent to the shack and moved there.

This was enough for Wood 1, but it was not robust enough for more complex maps or stronger opponents.

-------------------------

zLastEngineer | 2026-05-25 18:37:05 UTC | #18

## Bronze Strategy

My Bronze bot was still mostly heuristic, but it was no longer just a basic harvest-and-drop bot. At this stage, the strategy started to combine several mechanics: farming, training, fruit management, planting, chopping, and a first attempt at converting fruits into wood.

The main idea was to build a small economy around useful fruits. The bot tried to decide whether a fruit should be brought back to the shack for training, or whether it could be used as planting fuel.

### Core loop

The basic economy was still based on collecting resources and bringing them back to the shack:

```
move to tree → harvest → return to shack → drop

```

However, Bronze added an important distinction: not every fruit had the same purpose.

If a troll was carrying a fruit that was needed for the next training step, the bot tried to bring it back to the shack. If the fruit was not immediately needed for training, the bot could use it for planting instead.

So the logic became closer to:

```
harvest fruit → if needed for training, drop it → otherwise plant it

```

This was my first attempt at making the economy less passive. Instead of only collecting what already existed on the map, the bot started to use fruits to create new trees.

### Training

Training was already present before Bronze, but in this version it became more connected to the economy.

The bot checked the shack inventory and tried to train additional trolls when enough resources were available. The goal was to grow from a small number of workers into a more stable multi-troll economy.

The training was still basic. I was not using a sophisticated build order or adapting troll profiles deeply to the map. The main idea was to create useful workers and improve resource production.

The bot therefore had to decide which fruits were important for training and should be preserved. This is where fruit management started to matter.

### Fruit management

One of the main improvements in Bronze was that the bot started to reason about fruits.

A carried fruit could have two different roles:

1. **Training resource**: bring it back to the shack.

2. **Planting fuel**: plant it on a useful cell.

This meant the bot did not blindly drop every fruit. If a fruit was useful for the next troll, it was brought back. If it was not needed, the bot could try to plant it instead.

This was still a simple rule-based system, but it introduced an important strategic idea: fruits were not only points or resources, they could also be converted into future value.

### Planting

The bot started to plant trees when it had a fruit that was not required for immediate training.

The preferred planting spots were useful cells, especially cells near water when possible. Planting near water was valuable because it could improve the growth cycle and make the tree more useful later.

At this stage, planting was still opportunistic. It was not yet a fully planned economy, but it was the beginning of a plant-based strategy.

### Chopping and wood

Bronze also started to exploit wood.

If a troll had `chopPower > 0`, it could move to a tree, use `CHOP`, collect wood, return to the shack, and drop it.

The wood loop was:

```
move to tree → CHOP → collect wood → return to shack → DROP

```

This was important because wood was more valuable than basic fruits. The bot started to understand that a fruit could sometimes be more valuable if used to create a tree, then converted into wood.

This was the early version of a plant-chop-drop idea:

```
fruit → plant tree → chop tree → drop wood

```

However, this system was still basic. The bot did not yet have a strong long-term plant-chop-drop engine. It was more of an opportunistic conversion than a fully optimized strategy.

### Target selection

The bot still used simple heuristics to choose targets.

It looked for useful trees depending on the situation:

* trees with fruits when it needed resources;

* trees that could be chopped when wood was useful;

* planting opportunities when carrying a fruit not needed for training;

* shack-adjacent positions when carrying resources.

This made the bot more flexible than the earlier Wood versions, but the decisions were still mostly greedy.

### Summary

In short, my Bronze strategy was a greedy economy bot with basic training and early fruit management.

Compared to the Wood versions, the bot started to treat fruits differently depending on their usefulness. Fruits needed for training were brought back to the shack, while less useful fruits could be planted and later converted into wood through chopping.

This was not yet a complete strategy, but it was the first version where the bot started moving from simple harvesting toward a more interesting economy based on training, planting, and wood conversion.

-------------------------

0x6E0FF | 2026-05-25 20:56:05 UTC | #19

43th legend in Rust

Thank you codingame and the community for yet again another great challenge. 

I was a bit worried at first, seeing that search bot would be hard, and that I would probably have to stick to heuristic, which I usually dislike more, because it feels less magical that a search bot that takes decisions on its own. But after digging into it, I enjoyed the game so much. Thanks @eulerscheZahl, @Illedan, @aCat, and @Astrobytes for putting it together. Some aspect I enjoyed:
 - The visuals were great (did not find all easter eggs though)
 - It was easy and enjoyable to watch replays and understand what the bot was doing and the decisions it was taking
 - The referee with precompiled version available, and a branch to build it, without having to do the usual change by ourselves
 - The input window in player parameters, this is godsent!


Anyway I started really simple to get out of wood league by just harvesting the nearest trees. I couldn't wrap my head around how to do a search based bot, so I sticked to heuristic.

## Training
I have a training goal of (2, 2, 0, 2), which I execute as soon as possible. when all resources are available, I maximize each skill with the resources I have: 

`skill = sqrt(resource - nbtrolls)`

## Troll actions
To compute actions for each troll, I first compute a list of all possible tasks:
 - one `Harvest` task per tree
 - one `Chop` task per tree
 - one `Mining` task per IRON source
 - 4 `Plant` task per free GRASS cell, 1 per tree kind

Then for each troll I compute an assignment list, for each task it can achieve. An Assignment is a Task, a State and a score. The State represent where the troll is in the progression of realizing the task, among:
 - `MoveTo`: Traveling to the target.
 - `Act`: Performing the primary action (Harvesting, Mining, Planting, Chopping).
 - `BackToShack`: Returning with resources.
 - `Drop`: Depositing resources at the shack.
 - `Pick`: take resource from the shack
 
The main idea is that I don't force a troll to stick to a Task for N turn. At each turn, the bot recompute this from scratch, which can make him reconsider what he is doing at anytime if something more important is doable.

## Scoring assignments
Each assignement compute a score for the task+Troll couple, which is always a variation of :

`Score = (Potential Gain * Priority Multiplier) / (Estimated Time to Arrival + Action Time)`

Dividing by the time to complete the task makes troll more willing to stick to the task they started in previous turn. The gain is computed taking into account tree growth until arriving there.

The main difficulty of this approach is that all actions use the same scoring system, eventhough they don't have the same scale, So I have loads of magic numbers. By example when I started doing Planting, all trolls were very pleased to plant everywhere without ever harvesting any fruits. So I have a estimation of a fruit growth potential of the board, and empirically crafted a formula to compute the threshold of growth based on resources needs.

Depending of the phase of the game: 
 - before training my 2nd troll
 - raiding opponent trees
 - chopping woods for final score

the weights and thresholds changes to tweak trolls behaviors. There is also some shameful hardcoded if statements here and there to forbid certain obviously bad actions (don't chop before training unless for defense, don't plant after turn 270, only troll 1 can't plant in second phase...)

## Push to legend
This approach got me to high gold, but wasn't enough, and was too weak against good harvester bots, so I decided to go the agression route, like the Gold boss. My bot was already chopping enemy trees, but always going back to the shack to gather the woods. What got me in legend (appart from the help of 
@Alexdelia 😉) was the "reckless chop" approach where you chop without gathering the wood, preventing or retarding opponent training. I stop the agression if the opponent started gathering wood, or have more troll that me.

## Side notes
 - I used psyleague at the begining, but for top gold and legend it became useless because the local league lacked variety of strategies. I did a ok-ish farmer version with 3 trolls that crushed the local league but was pretty bad in the real leaderboard, whereas my final bot is ranked pretty bad.
 - all paths between each cells to each other are computed with a BFS at 1 turn and stored in a lookup, they don't take into account my troll positions, which is resolved later when computing the final move of a troll (this starts being important for 3 trolls and more)

-------------------------

Baal | 2026-05-25 23:09:59 UTC | #20

it was my first codingame challenge and  loved it so much that I became addicted :smiley:  It was very instructive for me so thank you for this opportunity!! But this contest, will it be accessible in the near future? personnaly I wanted to continue a second approche that i began the last 2 days.

-------------------------

Astrobytes | 2026-05-26 01:23:56 UTC | #21

Yes, it should be available in the [multiplayer bot programming](https://www.codingame.com/multiplayer/bot-programming) section in the next few days.

-------------------------

laconic_pixel | 2026-05-26 07:36:53 UTC | #22

Absolutely impressed  by @delineate— definitely a well-deserved 1st place.

-------------------------

laconic_pixel | 2026-05-26 12:00:53 UTC | #23

#8th  Legend

Thanks to TrollerPact and codingame for the contest. This was one of the most enjoyable CG games I played: many viable strategies, new disruptive tactical ideas almost daily, and enough chaos to make it engaging right up to the last hour. I have to admit I invested way more time than I expected in this challenge, especially during the last few nights.

Bot was written in Rust. I would describe it as a mission-based planner with task-level lookahead, a lot of map classification, and strategic choices that influenced both training investment and tactical play.

\## General strategy

The final bot had three main profiles:

* \*\*Max Build-Up\*\*: the default economy mode. Train, build a local fruit/banana engine, then convert into wood/score.

* \*\*Hard Disruptor\*\*: used mostly on tight contested maps with good iron access. On those maps, if the opponent could also get chop power quickly, a normal build-up setup was vulnerable.

* \*\*Resource Raid\*\*: a selective raid mode. I am not very proud of this part, but it worked well against farmers/builders on maps where their build-up usually depended on planting lemons near the shack. The goal was to disturb that setup before it became stable.

The selector was based on map shape: shack distance, contested resources, fruit access, iron access, opponent lemon access, and some opponent-signal ideas, trying to infer whether the opponent wanted to play a build-up style or a more aggressive chopping style.

The bias was to keep the same strategy end-to-end once selected, because switching between styles was hard to optimize due to different training goals and role profiles. Still, I needed fallback logic to move from build-up into harder disruption on maps where I could not build a good setup because of enemy pressure.

\## Design

The bot was built around missions.

A mission was something like “harvest this tree and bring the fruit home”, “chop this tree and drop the wood”, or “collect the missing resources for the next training”. Jobs were evaluated with completion time and projected payoff.

After selecting the best individual jobs for each troll, I used a small DFS assignment step to pick the highest-scoring compatible set of jobs for the whole team.

I experimented with beam and GA. They never became the main bot. While the design felt promising initially, optimizing mission plans over a long horizon often produced “fantasy” scenarios: plans that looked good according to the scoring function, but were too brittle once collisions, opponent interference, training delays, and small tempo losses appeared in the real game.

##Training

Training was mostly hard-coded,The bot estimated whether key resources were reachable fast enough and adjusted the macro plan when the next troll no longer looked realistic.

A lot of bad games came from staying in “train rush” behavior for too long. Once training became hopeless, the bot needed to immediately switch into building/scoring mode instead of continuing to pick resources for a train that would never happen, or would happen too late to have good ROI.

\## Banana / wood economy

The late-game economy was mostly about turning renewable fruit into wood, building a banana engine near the shack: harvest bananas, replant them on good nearby cells, keep enough trees alive to sustain the loop, chop surplus trees when the wood ROI was better than keeping them as fruit production, and eventually go into full cash-out mode.

A lot of time went into tuning the engine: maintaining enough banana trees to keep production alive, deciding when to switch from harvesting/replanting to chopping for wood, assigning planter/harvester/chopper roles, and preventing 4-5 trolls from blocking each other around the shack.

This part was probably over-engineered. I even built a small sandbox to simulate better ways to build, sustain, and cash out the banana engine. But it was also the most fun part to play with. Many improvements came from watching replays and noticing trolls wasting tempo.

\## Workflow

Tooling-wise, I had a local Rust referee for speed, which was extremely useful for iteration. I also kept a set of sparring partners derived from my own current bot, but locked into different styles: economy-only, hard disruptor, resource raid, previous submissions, etc. This helped avoid optimizing only against one opponent’s personality and made regressions much easier to spot.

Congrats to everyone, and thanks again to the organizers.

-------------------------

yamo | 2026-05-26 08:59:19 UTC | #24

3rd - Legend
Here is my postmortem : [https://www.yannmoisan.com/spring-challenge-2026-postmortem.html](https://www.yannmoisan.com/spring-challenge-2026-postmortem.html "https://www.yannmoisan.com/spring-challenge-2026-postmortem.html")

-------------------------

Illedan | 2026-05-26 10:41:15 UTC | #25

Congrats to the winners!

The podium has been added here: https://www.trollerpact.com/

I had fun testing this challenge and working with @eulerscheZahl and others on the problem. Thanks to CG for making this contest possible! :smiley:

-------------------------

eulerscheZahl | 2026-05-26 13:34:39 UTC | #26

Finished at #23.
I pick a random troll and generate 2 macro actions (e.g. move to a cell and plant there), with some bias, for instance planting on cells close to shack/water is more likely. The game then gets simulated with a depth of 15 turns. Here I also generate move actions for the next turn resolve movement collisions on the fly, over and over for every new plan I try. If the score improves, I keep the actions. Repeat assigning random tasks to a troll until I run out of time.
TRAIN is hardcoded regarding the amount of trolls I want to train as well as their skills (having a lower bar, but allowing for stronger trolls if the starting resources are high enough). The best plan gets saved and is used as the initial solution in the following turn. And that's what I had before the contest started, about 900 lines of code.
During the contest I spent another 5 hours or so analyzing replays and tweaking the scoring function, but my final submission is still close to testing code, with some modifications:
  * reward trees of each type close to the own shack, but with less weight for each additional tree
  * keep palms next to shack alive in late game and have dedicated planter trolls
  * change minimum talent requirements for TRAIN, initially I didn't go for carryCapacity = 4
  * some detection of an aggressive opponent to TRAIN sooner, as it would get hard to train at all otherwise.

Diff says that I removed 61 lines and added 110, compared to Default AI.

Probably some more potential with a better crafted scoring function, but I felt like I shouldn't climb any higher on the leaderboard and let those without an unfair advantage battle it out.

-------------------------

xSkyline | 2026-05-26 13:42:42 UTC | #27

Thanks for the awesome write-up !

> 18-27 	own troll: movement, carry cap, harvest, chop, carried resources

I'm guessing these are the active troll's stats & inventory for which you're running inference ?


If so, which opponent troll do you keep in these next channels ?
> 28-37 	same for opponent troll

Edit: I think I got it after posting the question, you're actually describing the entire team for each player but setting the values to 0 if a troll is not present in the cell

-------------------------

eulerscheZahl | 2026-05-26 13:56:49 UTC | #28

> Observation Planes (104 x 11 x 22)

That's 104 channels for each cell on the grid. And while each cell only knows its own trolls, the network as a whole has full information of all trolls, trees, ...

-------------------------

delineate | 2026-05-26 17:11:58 UTC | #29

Yes, exactly right. And then the active troll plane tells the network which troll is the one we’re querying right now.

In earlier attempts I had tried other things, like running one inference for all trolls and having all the different movement actions in each troll’s output cells. That also sort of worked, but it seems to have trouble with some basic path finding. Given I was using so little time of the 50ms and had decided I probably wasn’t going to try any search, I then went to this architecture. It still has some trouble with basic path finding at times.

-------------------------

Ztrk | 2026-05-26 20:05:16 UTC | #30

### 24th - Legend

First of all, thanks to all organizers for the great contest.

### Approach

My approach was to use a genetic algorithm (GA) to find a sequence of tasks (harvest, chop, plant, mine) that maximizes an evaluation function. There are two distinct phases: training and "normal" phase.

#### Algorithm

The GA itself is relatively standard - tournament selection, steady-state population, mutation and crossover.

An individual is represented by a sequence of tasks for each of my trolls (`n_trolls x n_tasks`, with `n_tasks = 6`). There are four possible task types:
- Harvest \<tree coords\>
- Chop \<tree coords\>
- Plant \<coords\> - here I use a precomputed list of candidates rated by distance to my/enemy shacks and being next to water
- Mine - this always mines the ore closest to the troll

Drop action is hardcoded and done if inventory capacity is full. Movement and pathfinding is handled during simulation.

Harvest and chop actions - apart from existing trees - can use coordinates of a tree that is going to be planted. This is supposed to allow the bot to take into account future resource gain from a planted tree. I'm not sure whether it's a good idea, but it worked well in a few cases.

Mutation is done by changing a task to a random one or by swapping two tasks with each other. This is applied to every task in a sequence. I used an uniform crossover - each task is selected randomly from either parent.

The population is persisted between turns, if I don't train any trolls. Past individuals are fixed - actions that are now done/invalid are removed and replaced with random ones. I also try to detect and ignore some invalid/noop actions during simulation.

#### Evaluation

Individuals are scored by running game simulation - 50 turns during training and 20 otherwise - and then evaluating the game state. Evaluation function depends heavily on the game phase:

1. During training the aim was to train 2 trolls with hardcoded stats as quickly as possible. Thus evaluation takes into account number of required resources, turns to train the troll, and penalizes no lemon and plum tree near the shack.

2. After training I evaluate discounted score, troll inventories and trees on the map - by distance to my and enemy shack, and by being next to water.

During simulation I use a basic opponent model - if the troll is close to my shack and on top of a tree I assume he will be chopping it. I don't assume any other opponent's actions, like move or harvest.

As I couldn't quite make fully planting bot to work the resulting gameplay is quite aggressive - it tends to steal trees from other players, which works well when the enemy is close, but is problematic when he's further away.

Another limitation is having just 3 trolls - looking at the statistics I'm the highest ranked player who does that - better bots either aim for 4+ trolls or use only 2.

-------------------------

wala | 2026-05-27 20:14:43 UTC | #31

**Legend -** #6 **- C++**

There’s 2 phases **HARVEST/TRAIN** then **PLANT/CHOP** (mostly banana trees).

Training is hardcoded for 4 trolls (with round limits). As well as the number of trees needed close to the shack for each type (especially lemon, to increase the score faster).
Each troll has a purpose harvest/plant or chop (it can change as the round increases).

Each turn I search a solution with 2 components :

1. A role for each troll : **HARVEST** , **PLANT_FROM_SHACK_SEED** , **PLANT_FROM_HARVESTED_SEED**  (for each fruit type), **CHOP_TREE_AT** , **DROP** , **MINE** , **STEAL_OPPONENT_CHOP** (which is chop a tree being chopped by the opponent, except all the trolls can do it).
2. A **priority order** (id5 executes its move first, then id1…) to handle cell’s conflicts.

Then, for each board state, 2 functions are applied :

* The first constructs a real move from the role (find and cache the best target for harvesting, planting…)
* The second constructs the next round move, avoiding cell conflicts. The priority order is applied (so a “harvesting move” can be changed into a “moving move” if a troll with a highest priority has already moved to its cell). DROP are done first (to avoid a troll blocking the shack by harvesting/dropping next to it).

The simulations go on until all the roles are done. Then the board is evaluated.

So first I find the best roles in the natural order. Then for the remaining time I switch roles, try randomly other role… (each time the score for all the possible priority permutations is computed to find the best one).

There’s some additionnal **heuristic tweaks** :

* If the opponent destroys our plants during training => stop planting them
* During chopping, keep a banana tree close to shack to harvest.
* …

Thanks to CodinGame and all the codingamers who made this contest possible. It was cool, fun and different.

PS: I miss Fog Of Wars :grin:

-------------------------

Astrobytes | 2026-05-27 00:13:30 UTC | #32

Here is my [post-mortem](https://github.com/Astrobytes/CodinGameTrollFarm/blob/main/README.md) for my alter-ego trlr1990, which I nerfed late on Sunday evening.

-------------------------

FinkPloyd | 2026-05-27 08:18:30 UTC | #33

**Legend - #21**

**Approach**

A state machine with different roles based on stats. Mainly heuristics, I use simulations on first turn to find best TRAIN profiles.

**Strategy**

Two different strategies: **quick chop** and **banana farm**

* The first one is used on small maps or maps with trees very far away. The goal is to quickly train a troll and CHOP trees aggressively. The first troll plant all fruits from the shack and chop in a loop (day one strat before map generation fix)

* Banana farm: I try to TRAIN 3 trolls, then I use 2 trolls to PLANT and 2 trolls to CHOP. The PLANTER prioritizes bananas because they are easier to CHOP.

End game : every trolls CHOP the map

**Code**

The code is a state machine with different roles: HARVEST, HARVEST_IRON, PLANT, CHOP, etc. When a troll has a goal, it reserves the cell and tries to stick with it unless an opponent tries to CHOP a tree too close.

The state machine differs depending on whether I use the Farm strat or the Aggressive strat. Roles are determined mostly by stats. My first troll will HARVEST then PLANT, whereas the second trained troll, with better stats, will harvest iron because he can carry more.

**Reacting to the opponent**

I have a few heuristics to change scoring functions if the opponent is aggressive. My trolls will PLANT a bit further from my spawn if the opponent steals my trees.

**First turn**

On big maps, I simulate 300 turns with different TRAIN profiles to find the best combination. If the iron is too far, it is better to have less chop power, etc. Then I use it for the rest of the game.

I didn't have time to use the simulation during the game to improve decision-making.

**Work process**

Watching replays to see what went wrong, like in an RTS game. No local simulation. Claude Code helps me write quick and dirty code.

**Conclusion**

A very good challenge, so fun to watch the different strategies.
Congrats to the winners ! Thanks a lot to eulerscheZahl and CodingGame for the challenge.

-------------------------

Di_Masta | 2026-05-29 10:26:56 UTC | #34

My best result so far: 132th of 2022 players (63rd Gold)

When I participate in a contest I pursue two main dreams of mine: Reaching Legend league and/or top 100.

This time I was so close…

First I tried training 4 trolls as fast as possible, then start chopping the closest trees to the enemy shack. This worked quite well.

Then I decided to try to build economy of trees around my shack and then attack.
With this strategy I was promoted directly in the silver league when it was opened. From the replays I saw that the top player @FinkPloyd was using similar strategy. I’ve asked him for an advice and he was kind enough to respond and told me that he finds the best paths for the trolls to their targets one by one, to prevent collisions. I’ve added such logic for my bot. And this boost me to the **23**rd place! My excitement went over the roof, for first time I saw double digit place during a contest.

Then the aggro strategies came and I wasn’t able to hold my position. I tried to implement aggro bot myself, but I failed miserably.

For first time I didn’t drawn in implementing Game State simulation and testing future moves. I relied entirely on pure heuristics. Which seems suitable for this contest. Using Claude Code I was able to iterate quickly different ideas, but I haven’t managed to dive and polish the strategies. Also for first time I was able to setup cg-brutaltester, psyleague and cgarena and I enjoyed using them.

I consider the whole experience a success even though I wasn’t able to accomplish a dream of mine… https://www.youtube.com/watch?v=oJH5AsNr_nM&list=RDoJH5AsNr_nM&start_radio=1

-------------------------

celeria | 2026-06-06 11:20:35 UTC | #35

Many thanks to the creators and to codingame for this great game !

My best result in a challenge up to now. A little bit disappointed the last minutes to have been ejected from the top100. But I finally reached Legend today without submitting anything else.

My strategy was to create 2 specialized trolls : 1 to harvest and 1 to chop. 
Then :
Chopper troll targets enemy part.
Basic troll (starting troll) plants and chops near my base.
Harvester troll becomes a basic troll as soon as there is enough fruits in inventory.

-------------------------

