# Escdemon — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #10; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-25 12:15:11 UTC
- Author: Escdemon — #37 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #10 — Escdemon — 2026-05-25 12:15:11 UTC

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

---

