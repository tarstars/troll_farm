# eulerscheZahl — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #1, #4, #26, #28; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-25 12:16:27 UTC, 2026-05-25 08:52:38 UTC, 2026-05-26 13:34:39 UTC, 2026-05-26 13:56:49 UTC
- Author: eulerscheZahl — #23 Legend (game author)
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #1 — eulerscheZahl — 2026-05-25 12:16:27 UTC

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

---

## Post #4 — eulerscheZahl — 2026-05-25 08:52:38 UTC

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

---

## Post #26 — eulerscheZahl — 2026-05-26 13:34:39 UTC

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

---

## Post #28 — eulerscheZahl — 2026-05-26 13:56:49 UTC

> Observation Planes (104 x 11 x 22)

That's 104 channels for each cell on the grid. And while each cell only knows its own trolls, the network as a whole has full information of all trolls, trees, ...

---

