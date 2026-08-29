# laconic_pixel — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #22, #23; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-26 07:36:53 UTC, 2026-05-26 12:00:53 UTC
- Author: laconic_pixel — #8 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #22 — laconic_pixel — 2026-05-26 07:36:53 UTC

Absolutely impressed  by @delineate— definitely a well-deserved 1st place.

---

## Post #23 — laconic_pixel — 2026-05-26 12:00:53 UTC

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

---

