# MSz — his earlier CodinGame post-mortems (NOT about Troll Farm) — context for his usual toolkit, verbatim

- URL: https://github.com/marekesz/contests (files listed below; raw via raw.githubusercontent.com/marekesz/contests/main/...)
- Repository state on 2026-08-28: one branch `main`, last commit 2025-01-29; files: "2022 - CodinGame Cultist Wars - PM.md", "2023 - CodinGame Fall Challenge (Seabed Security).md", "2023 - CodinGame Spring Challenge (Ants) - PM.md", "2024 - CodinGame Fall Challenge (Selenia City) - PM.md", "2024 - CodinGame Summer Challenge (Olympbits) - PM.md", "2024 - CodinGame Winter Challenge (Celluarena) - PM.md". NO Spring Challenge 2026 file.
- Author: MSz (GitHub marekesz). His CodinGame forum account has no post about Spring Challenge 2026; the forum post history shows: Winter Challenge 2024 (#2, 2025-01-29 "My PM:"), Fall Challenge 2024 (#1 optimisation), Summer Challenge 2024 (#1), Fall Challenge 2023 (#2, "one-turn ..."), Spring Challenge 2023 (#1), Fall Challenge 2022 (#10, "a mix of Hill Climbing and Hungarian algorithms"), Cultist Wars (#1, alpha-beta).
- Language: English
- Source type: the player's OWN descriptions of OTHER games. Archived only to show how he usually builds bots (exact simulation engine, hill climbing / beam search over action sets, Hungarian assignment, heavy speed optimisation, hard-coded eval weights). Nothing here is evidence about his Troll Farm bot.

Nothing below this line was written by us.

---

## File: 2024 - CodinGame Winter Challenge (Celluarena) - PM.md  (Winter Challenge 2024, a grid multi-unit game — the closest in kind to Troll Farm)

2nd

Thanks for the organizers and congratulations to @reCurse, @aCat, and @marwar22.

The Winter term including holidays was very inconvenient, as usual.
The game was interesting and the engine was well defined (e.g., without arbitrary pathfinding or dependency on double arithmetic).
Although it seemed too simple for a longer contest (deterministic, perfect information, flat and quite small grid, predictable opponent), which makes ordinary solutions work well.

### Algo

Nested beam search:
The main beam search is over full turns and is very standard.
However, action sets for a turn are computed in independent beam searches with a very small width (2 or 3).
The depth of the main beam is unlimited but in most cases, it runs out of time between depth 2 and 8.

For the opponent or when time is running up, the beam is replaced with a much chaper fast greedy choice: It evaluates each action separately, sort them, and then considers them in that order to build an action set.

The opponent prediction in the first turn consists of calculating three scenarios (potentially three different opponent's action sets).
Then, own actions are applied together with these opponent's choices.
For the eval of own actions, a weighted average is used, but for the next state for the beam, the worst case is used.

### Eval

The eval is the heaviest part, with many but standard ingredients:
Voronoi balance, filled cells, separate values for certain more relevant cells based on the shortest paths, distances to the resources, progressive evaluation of income and stored resources, threats including the size of the possibly killed subtree.

### Action generator

Generating possible actions suffers with a lot of pruning.
Harvesters, Sporers, and Tentacles are made only under certain conditions unless Basic is not affordable.

### Weaknesses

I simply did not have time to finish everything nor to try all promising ideas. Partly because of the Winter term, but also because of some mistakes.

* I did not optimize with bits. Instead, I started with compressed state representation and heavy eval. Therefore, calculating eval is the most expensive part and I am doing only about 9000 in the middle of a play. Bit representation could change that but requires a different and simpler eval and a different action generator. I spent too much time optimizing the algorithm itself and the action generator.

* I did not overcome timeouts and started to testing them on CG too late. Sometimes a single eval took about 10ms, maybe due to memory issues, thus not fixable without a big redesign.

* I did not use map analysis (identifying key resources, map type) nor used the initial 1s reasonably.


For some interested in what resource is most valuable:
I use C >> B > A > D for stored resources and C > B >> D > A for income.
(>> means a much larger weight.)
But these weights are independent on the map, unfortunately.

Traditionally, I attach results showing the potential of speed optimization (99% CI):
```
MSz[ 25% time] vs MSz:  28.61%  ±1.2
MSz[ 50% time] vs MSz:  41.44%  ±1.3
MSz[150% time] vs MSz:  54.22%  ±1.3
MSz[200% time] vs MSz:  56.07%  ±1.3
MSz[400% time] vs MSz:  59.16%  ±1.2
```


## File: 2024 - CodinGame Fall Challenge (Selenia City) - PM.md  (optimisation contest)

(Post Mortem for [Fall Challenge 2024 -- Selenia City](https://www.codingame.com/contests/fall-challenge-2024) optimization)

1st

I enjoyed the contest and the game was nice, although I prefer bot programming. Mastering the engine was moderately difficult, and the engine was optimizable.

The most troublesome thing was the need to adjust to particular test cases, which, moreover, we could only guess how much they will vary from the public ones. Fine-tuning for tests was a major concern to worry about, i.e., that a totally general agnostic algorithm would not be competitive, and on the other side, that assuming too much would spoil everything. I think it would be better to publish the generator and, for example, say there will be 100 uniformly random seeds or so. This would give the results more fair, not so dependent on untestable assumptions and luck.

The bot has three main ingredients:

* The algorithm is Hill Climbing, split into much-parametrized phases with different action types.
* Heavily optimized exact simulation engine.
* Test-dependent tunings.


### Algorithm

The algorithm is split into phases that differ in parameters and action types. In each phase, it performs each available action and simulates the score obtained in the current month (turn). The eval function depends on this score and the resources left. This is repeated until no improvement can be made, and then the next phase begins. The action types are, for instance, adding a path of a certain thickness (by adding tubes and optionally upgrading) and length together with a pod or two, adding a teleport, replacing a pod, etc. The next phases increase available thickness and the set of available actions.

The problem carries some similarities to the ants' movement optimization from Spring Challenge 2023, where I used a similar algorithm.


### Engine

The efficiency matters a lot on big maps, affecting the number of combinations to check by the HC. The simulation consists of inverse BFS to compute distances for each building type, and then days simulation, which consists of moving pods and astronauts. The nontrivial optimizations are as follows:

* Astronauts move in groups. A group is a set of astronauts of the same type and from the same pad in a continuous interval. On most maps, there are groups larger than one. Sometimes, when a whole group does not fit in one pod, it is split into smaller groups.
 There are no traffic jams. Computing jams considerably slowed the engine (the need to count used tube capacity, etc.), so I decided to disable it: only actions that ensure that pods will not get stuck are applied, thus each added pod comes with suitably new or upgraded tubes.
* I do not sort anything anywhere, always keeping the right order of pods and astronauts.
* When building tubes, they are checked for an intersection only with the tubes currently added in the turn. The other cases are preprocessed before the search.


### Test-dependent tuning

The most important parametrization is the value of left resources, which obviously must vary a lot across the maps. The other fine tunings involve the set of allowed actions in particular phases of HC. I am not too fond of such practice, but there was no other way of including information about the future turns, which were not random either.

The most computational heavy is Test 8 (Grid). For this, the bot brings an additional ingredient, which is computing initial direct tubes greedily without simulation. It was necessary because the number of needed actions is so large, that otherwise the HC does not have time to add them all and spend all resources.

Surprisingly, the general setting without test-specific tunings is not so much worse, getting the score smaller by only about 200k. The general, however, actually means being tuned to the tests giving the largest scores.


### Some results

Here are the results on each of the public tests:

```
Test 1: 53 710
Test 2: 128 830
Test 3: 254 605
Test 4: 261 575
Test 5: 415 110
Test 6: 379 390
Test 7: 739 409
Test 8: 1 393 168
Test 9: 870 763
Test 10: 766 489
Test 11: 933 093
Test 12: 901 280
Total: 7 097 422
```

Example replay with test 8: [https://www.codingame.com/replay/822629219](https://www.codingame.com/replay/822629219) .

Example replay with test 12: [https://www.codingame.com/replay/807001223](https://www.codingame.com/replay/807001223) .

The number of simulations (score computations) for Test 8 (Grid), in the first turn without the mentioned greedy optimization: 98 536 (the average over 5 runs).

And the results on the public validators from the repository, for a version close to the final one (I cannot test them again on CG, since there is no option. And, of course, the results on large tests may differ slightly in each run):

```
Test 13: 95 090
Test 14: 173 600
Test 15: 409 415
Test 16: 400 740
Test 17: 438 416
Test 18: 393 200
Test 19: 727 644
Test 20: 1 501 128
Test 21: 788 257
Test 22: 740 240
Test 23: 934 054
Test 24: 921 655
Total: 7 523 439
```


## File: 2024 - CodinGame Summer Challenge (Olympbits) - PM.md  (bot contest, won)

(Post Mortem for [Summer Challenge 2024](https://www.codingame.com/contests/summer-challenge-2024-olymbits) -- Olympbits)

1st

For such short contests, the most important thing is fighting with time and constantly improving the bot. I had a hard time keeping the tempo. I must say the term around the end of the (pre)school year is unfortunate. Although, it is not as bad as the term including Christmas, which is one of the worst options.

Thanks to the organizers, great idea for a game. Congrats to @reCurse and @Nanaeda for the excellent competition!
Thanks to @aCat, @gaha, @surgutti, and @Zylo for our discussions and sharing ideas.

### Game

The game is interesting yet difficult to play, and the rules in the referee were a piece of cake (compared to the nightmare from Fall Challenge 2023). It was possible to get the proper engine in just a few hours, and there was space for its further nontrivial optimization.
Overview

The algorithm is a variation of DUCT, mostly fully decoupled, which is called Smitsimax here. In the basic part, there are three independent trees of the players of branching 4, but this is extended around the root. The crucial parts are bizarre management of decisions in iterations based on the number of samples and optimizing a lot.

The fully decoupled DUCT is fragile and exploitable, but I supposed that the budget is too small for a more fancy algorithm. Indeed, the number of iterations strongly affects playing strength and the bot would still improve with more iterations.

Furthermore, the behavior varies depending on the time budget and requires tuning for a specific limit; this concerns mostly the things related to exploration. The fact that there were two different processors further complicated it, so I ended up with experiments with two respective budgets, to ensure that things worked good with both. The next step could be providing two separate tunings, but there was no time for that.

Efficiency matters a lot. The following are the results of the final bot with its two previous versions (99% CI). The final bot has doubled, normal, and halved the time budget, respectively.

    MSz[time 200%] vs MSz(v-1) vs MSz(v-2):   57.91%  ±1.0  : 48.27%  ±1.0  : 43.82%  ±1.1
    MSz[time 100%] vs MSz(v-1) vs MSz(v-2):   54.93%  ±1.0  : 49.55%  ±1.0  : 45.53%  ±1.1
    MSz[time  50%] vs MSz(v-1) vs MSz(v-2):   49.94%  ±1.0  : 52.12%  ±1.0  : 47.95%  ±1.1

### Algorithm

The strategy for simulations (rollouts) is to use a policy, which is a chosen minigame that the player wants to maximize. The policy is chosen by weighting minigames depending on the current and predicted scores. It is kept for the next turns until that minigame ends or becomes fully determined, which means the outcome for that player will not change anymore regardless of the actions. Choosing an action is taking a random one from the best ones for this minigame. The best actions are hardcoded by a set of very simple rules. Stunning (in hurdle and skating) does not disable the policy, but then the player temporarily chooses another minigame and makes a best move for it. This simulation part dominates efficiency; the key is to keep it simple and fast. More sophisticated methods worked better sometimes, but not in the timed setting.

When a minigame ends, the next edition is generated, with the same distribution as in the referee. However, each minigame is generated at most once in a simulation, except for skating, which is not generated. When the generated minigames end, the iteration finishes. The scores are completed with predicted scores from future minigames, depending on their expected number of remaining editions.
These numbers are easily calculated exactly for archery, skating, and diving, whereas for hurdle it was obtained from massive experiments with already good agents.
Playing with trees

For most nodes, the trees are fully decoupled, which means there are only 4 children for the player’s actions. However, we can branch also on the opponents’ actions, which gives 16 possibilities, and on the skating order, which gives 24. I do not want to consider branching on possible generated minigames.
The branching on opponents’ actions is taken in the root, so the branching there is 64. For skating order, a separate tree of a small depth is managed. The latter tree is used for decisions only after gathering a certain number of samples.

The important issue is to take only quality actions in simulations. First, an action is decided by UCT only if the number of samples reaches a certain threshold; otherwise, it uses the policy as above. This gives similar effects as mixing UCT with heuristic values but avoids that expensive formula. Then, there is a surprising mechanism: In contrast with the usual UCT, deciding by the tree starts from a very small exploration, thus mostly based on the choices made previously with the policy. I think this helps by keeping the statistics of the node of relatively good quality. The exploration reaches its normal formula after a certain threshold of samples, which happens only for a small fraction of the nodes at the top.

The final bot performs better when the available budget is smaller, which is mostly the result of the described threshold mechanisms employed in the latest versions. The following are the results with altered budgets but fair – the same for all agents.

    [  200% time] MSz vs MSz(v-1) vs MSz(v-2):   54.27%  ±1.0  : 50.21%  ±1.0  : 45.52%  ±1.1
    [  100% time] MSz vs MSz(v-1) vs MSz(v-2):   54.93%  ±1.0  : 49.55%  ±1.0  : 45.53%  ±1.1
    [   50% time] MSz vs MSz(v-1) vs MSz(v-2):   56.13%  ±1.0  : 49.61%  ±1.0  : 44.27%  ±1.1
    [   25% time] MSz vs MSz(v-1) vs MSz(v-2):   59.52%  ±1.0  : 49.28%  ±1.0  : 41.21%  ±1.1
    [   10% time] MSz vs MSz(v-1) vs MSz(v-2):   65.74%  ±1.0  : 45.78%  ±1.0  : 38.48%  ±1.0
    [:-) 1% time] MSz vs MSz(v-1) vs MSz(v-2):   74.45%  ±0.7  : 72.17%  ±0.7  :  3.38%  ±0.4

The branching and thresholds are specific to the time limit. For example, increasing branching besides the root seems to be better under a larger time limit, but worse otherwise.

    [200% time] MSz-IncBranching vs MSz(v-1) vs MSz(v-2):   55.04%  ±1.0  : 50.93%  ±1.1  : 44.03%  ±1.1
    [100% time] MSz-IncBranching vs MSz(v-1) vs MSz(v-2):   53.32%  ±1.0  : 51.36%  ±1.1  : 45.33%  ±1.1

### Optimization

As the number of iterations is crucial, optimization is essential. There are many tricks measured precisely to give a speed benefit.

The funniest part is precomputing all possible hurdle maps. Then generating a hurdle minigame boils down to get a random id from 1280 possibilities (some are repeated just to ensure the proper distribution). Furthermore, each map is already solved, hence getting the best actions and applying them is essentially done by one lookup and checking the stun.

The average numbers in the second turn over 10 runs on CG haswell:

    Iterations:         5 264.6
    Game states:      176 527.5
    Tree nodes:        15 989.8 + 1 041.3
    UCT calculations:  64 241.7

### What did not work

* Probabilities: An estimation for an unfinished minigame assuming random moves. Not that such probabilities are useless, but too costly compared to greedy decisions, and maybe not as realistic estimations, since the agents do not play randomly. Probabilities require more complex operations and/or big arrays, which are slow to access.

* Weighted moves: The benefit of using a policy is not only imitating a realistic play but also in terms of efficiency – in most of the turns, we do not have to even look at the possible actions for the other minigames. Weighting moves or weighting minigames in place of random greedy decisions were too costly.

* Restricting actions: Sometimes we know that certain actions are always worse than others, for example, when there is only one active nondetermined minigame. We can forbid choosing these actions in UCT, which normally tries them too. This helps, yet there are two obstacles: it is again too costly, and perhaps disturbs the statistics of a node because the same node can be used for different game states with different excluded actions.
