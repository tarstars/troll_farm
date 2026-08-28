# Ztrk — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #30; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-26 20:05:16 UTC
- Author: Ztrk — #24 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #30 — Ztrk — 2026-05-26 20:05:16 UTC

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

---

