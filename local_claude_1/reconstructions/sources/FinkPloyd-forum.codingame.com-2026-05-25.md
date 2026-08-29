# FinkPloyd — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #33; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-27 08:18:30 UTC
- Author: FinkPloyd — #21 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #33 — FinkPloyd — 2026-05-27 08:18:30 UTC

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

---

