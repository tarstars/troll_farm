# delineate — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #15, #29; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-25 16:58:33 UTC, 2026-05-26 17:11:58 UTC
- Author: delineate — #1 Legend (contest winner)
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #15 — delineate — 2026-05-25 16:58:33 UTC

An overview of my strategy for this competition (#1): https://gist.github.com/delineate/93ba9d48102e442e764db39d85ac44a3

---

## Post #29 — delineate — 2026-05-26 17:11:58 UTC

Yes, exactly right. And then the active troll plane tells the network which troll is the one we’re querying right now.

In earlier attempts I had tried other things, like running one inference for all trolls and having all the different movement actions in each troll’s output cells. That also sort of worked, but it seems to have trouble with some basic path finding. Given I was using so little time of the 50ms and had decided I probably wasn’t going to try any search, I then went to this architecture. It still has some trouble with basic path finding at times.

---


## Context: the questions delineate answered (xSkyline post #27 and eulerscheZahl post #28, verbatim)

### Post #27 — xSkyline — 2026-05-26 13:42:42 UTC

Thanks for the awesome write-up !

> 18-27 	own troll: movement, carry cap, harvest, chop, carried resources

I'm guessing these are the active troll's stats & inventory for which you're running inference ?


If so, which opponent troll do you keep in these next channels ?
> 28-37 	same for opponent troll

Edit: I think I got it after posting the question, you're actually describing the entire team for each player but setting the values to 0 if a troll is not present in the cell

### Post #28 — eulerscheZahl — 2026-05-26 13:56:49 UTC

> Observation Planes (104 x 11 x 22)

That's 104 channels for each cell on the grid. And while each cell only knows its own trolls, the network as a whole has full information of all trolls, trees, ...

