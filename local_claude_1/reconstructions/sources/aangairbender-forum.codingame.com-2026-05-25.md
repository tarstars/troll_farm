# aangairbender — posts in the "Spring Challenge 2026 (Troll Farm) - Feedback & Strategies" thread, verbatim

- URL: https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241 (post numbers #9; direct link form `https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/<post number>`)
- Dates: 2026-05-25 12:07:32 UTC
- Author: aangairbender — #16 Legend
- Language: English
- Source type: the player's OWN description (first-hand), unless the post is a reply to someone else.

Nothing below this line was written by us.

---

## Post #9 — aangairbender — 2026-05-25 12:07:32 UTC

Top 16 legend. Thanks to TrollerPact and CG for the amazing contest.

# General Strategy

I am training 3 extra trolls with hardcoded skills.
My bot consists of 3 steps:

1. Game state analysis

* assign each resource value based on what’s needed to train the next troll
* compute a list of best planting spots (either near shack or near water)

2. Planning
   I generate bunch of high-level tasks (harvest, chop, plant, mine, wait, drop. Each tasks has following functions:

* `value(troll)` - how much benefit would I get if task would be completed by given troll
* `turns_to_complete(troll)` - how much turns left to complete the task by given troll
* `movegen(troll)` - generate action(s) which would advance the given task assuming its being completed by given troll

I allow only 1 plant task per tree kind.

Then I run assignment algorithm (Munkres) to find the best (max) matching between trolls and tasks. The edge cost is `value * 0.9^turns_to_complete`.

This produces a plan - a task for each troll.

3. Search

I have shallow (depth 2) search with eval being sum of `turns_to_complete` of each task in the plan. Basically I am looking for sequence of actions which would complete the plan the most.

I am using beamsearch, but amount of states is very low, so bruteforce could be used instead (my bot uses 0ms per turn).

# Planting

for deciding which tree still needs to be planted I compute 2 values for each tree kind:

* current_produce_per_turn - how much of given resource is produced every turn (sum of some formula for each tree)
* desired_produce_per_turn - how much of produce per turn I need to train all my trolls (some simple formula)

I only plant a tree if `current_produce_per_turn[kind] < desired_produce_per_turn[kind]`.

Once I know which tree kinds I want to plant, I run another assignment algorithm to assign each kind to a good planting spot. The edge cost is increase of produce per turn I get from planting given tree kind in a given spot.

# Trick to fight aggro choppers

30min before contest ended I was top40 and was losing a lot to aggressive chopping bots. I noticed that my trolls kept wasting fruits by planting trees just for those trees to be chopped few turns later. So I added a condition to disallow planting if opponent troll is nearby. This pushed me straight to top15.

---

