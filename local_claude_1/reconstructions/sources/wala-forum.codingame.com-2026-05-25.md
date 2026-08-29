# wala — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #31; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-27 20:14:43 UTC
- Author: wala — #6 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #31 — wala — 2026-05-27 20:14:43 UTC

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

---

