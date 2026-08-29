# Astrobytes (alter ego trlr1990) — "Contest Post-Mortem", verbatim

- URL: https://github.com/Astrobytes/CodinGameTrollFarm/blob/main/README.md (raw: https://raw.githubusercontent.com/Astrobytes/CodinGameTrollFarm/main/README.md)
- Date: commit bf84d11b 2026-05-27T00:04:07Z ("Update README with contest post-mortem and strategies"); linked from the forum thread post #32
- Author: Astrobytes — one of the four game co-authors (eulerscheZahl, Illedan, aCat, Astrobytes); competed under the pseudonym trlr1990, which was #1 when Legend opened and finished #69 Legend after he deliberately weakened it
- Language: English
- Source type: the player's OWN description (first-hand)

Nothing below this line was written by us.

---

# CodinGameTrollFarm
# Contest Post-Mortem — trlr1990 aka Astrobytes

Hello. My bot, under my pseudonym, trlr1990, finished bottom legend after I nerfed it, but was previously #1 or top 5 for a fair part of the contest, and indeed #1 when legend opened. I only had a few hours per night to work on it and it's the hardest I ever worked on a contest for no reward whatsoever other than the satisfaction of seeing it #1 Legend for a while!

Obviously I had a head-start so my simulation and a basic crappy random search was ready when the contest started.
It seems quite a few of us took similar approaches and tried the same things. I tried beam search, hill-climbing and GA approaches, all with varying degrees of opponent interaction and varying degrees of success.

In my final bot I assign goals (macro actions/plans) using Kuhn-Munkres, score it, then try to improve that by hill-climbing over the solution mutating a random troll's goal sequence each iteration.

I had a depth of 25 with 5 goals per troll for most of the contest, then dropping to 15 and 4 respectively just before legend opening. Maximum ~300,000 iterations on turn 1 and max ~10,000 thereafter (map and tree count dependent, also machine-dependent — pretty amusing to see your bot go from 200k+ to 60k from game to game sometimes on the same map).

I have a hardcoded array of troll attributes that I modified throughout the contest depending on what I was seeing during lost games. I tried doing this dynamically but it was unsuccessful. Training is allowed if the cost/projected benefit is favourable. If I don't have enough of a fruit/iron I increase the weight of the appropriate resources based on the actual deficit to favour accumulating that resource. I only allow mining if iron is required for the next train.

I split the game into three phases — early, mid and late — and maintain an array of weights for each goal which are skewed towards harvesting, planting or chopping etc. depending on game phase. I spent a lot of time tweaking this right up until the end. Useless goals (e.g. gathering anything while fully-loaded, planting/dropping without carrying anything) are pruned from random mutations by giving them a zero weighting. I also, as seems a common approach, skew planting goals towards water-adjacent tiles and close to my shack.

Evaluation has a small bonus for troll count to encourage training, shack and troll inventory count, and goddamn trees. For trees, trying to balance distance from shack, harvest potential (fruit count) and cooldown, wood potential (size) with the resource gathering weights and goal weights was... what I spent about 5 days on.

I had a lot of (greedy) opponent simulation initially, which seemed alright at first but quickly became unhelpful as bots improved, so I started to limit what I was simulating and evaluating.

The *'aha'* moment was when I removed distance-based tree eval (basically a Voronoi) and simply considered all trees as equally owned/unowned. This caused my bot to begin raiding and chopping opponent trees. Again I had to spend time tuning the weights for everything again to get that working better.

I didn't run any offline games during the contest whatsoever — all tweaking was done in the IDE and tested via submits. Numbers were arse-pulled for the most part (to use a jacek-ism).

Sorry if some of this is a little vague; I didn't keep many notes throughout and my version control was `version_1`, `version_2_detail`, `version_3_HELL_NO` etc. I don't consider it a good bot — I think I was just faster at adapting and lucky tbh. Looking at the code again I can see multiple inconsistencies and probable bugs which really should be fixed, and will probably break it if I do so of course. There really are some parts that could do much better, but it is what it is. We'll see where it ends when I submit it in the multi.

---

Massive congratulations to **delineate** who won the contest by a clear margin with a rather brilliant bot!

Thank you to everyone who played, thank you to CG for the chance to make this contest happen, and most of all thank you to **eulerscheZahl** for the brilliant game idea!

And big shout out to **norxondor_gorgonax**, **fink_ployd** and **yaichi** for giving my bot all kinds of trouble throughout the contest!
