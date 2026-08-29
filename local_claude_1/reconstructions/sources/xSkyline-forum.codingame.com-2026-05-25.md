# xSkyline — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #11, #27; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-25 16:03:55 UTC, 2026-05-26 13:42:42 UTC
- Author: xSkyline — #14 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #11 — xSkyline — 2026-05-25 16:03:55 UTC

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

---

## Post #27 — xSkyline — 2026-05-26 13:42:42 UTC

Thanks for the awesome write-up !

> 18-27 	own troll: movement, carry cap, harvest, chop, carried resources

I'm guessing these are the active troll's stats & inventory for which you're running inference ?


If so, which opponent troll do you keep in these next channels ?
> 28-37 	same for opponent troll

Edit: I think I got it after posting the question, you're actually describing the entire team for each player but setting the values to 0 if a troll is not present in the cell

---

