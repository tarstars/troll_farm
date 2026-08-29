# putibuzu — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #5; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-25 09:17:59 UTC
- Author: putibuzu — #30 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #5 — putibuzu — 2026-05-25 09:17:59 UTC

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

---

