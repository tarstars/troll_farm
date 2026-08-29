# delineate — "Codingame Spring Challenge 2026 (delineate)" — the winner's own write-up, verbatim

- URL: https://gist.github.com/delineate/93ba9d48102e442e764db39d85ac44a3 (file `cg-spring-2026-delineate.md`; raw via the GitHub gists API)
- Date: gist created 2026-05-25T16:49:10Z, one revision (e8a005dd); linked from the forum thread post #15 the same day ("An overview of my strategy for this competition (#1)")
- Author: delineate — #1 of the contest (33.77), #1 of the multiplayer ladder now (30.89)
- Language: English
- Source type: the player's OWN description (first-hand). Fetched 2026-08-28; 13,065 characters, not truncated.

Nothing below this line was written by us.

---

# Codingame Spring Challenge 2026 (delineate)

This is an overview of my approach to the Codingame Spring Challenge 2026 where I finished in first place. Thanks to the game developers (eulerscheZahl, Illedan, aCat, and Astrobytes) and Codingame for a fun and rewarding competition. It was a very challenging game, which helped me learn a lot.

Rather than just laying out the final approach, I'll describe the full journey I took along the way to help motivate the final architectural design choices I made.

## Initial attempt
When I first saw the game description, I immediately thought of the Winter 2024 Challenge (Cellularena): relatively small grid board, multi-agent, large action space with discrete actions. The winner of that competition (reCurse) has an excellent writeup and I thought for this game it should be pretty straightforward to apply a ResNet with PPO, implement the rules, and then let it learn. If only things were that easy...

Using this approach, the network did all right (~25th at the time on the leaderboard), but it could never learn to mine iron, so it never ventured into higher tech units.

It makes sense why the network found this so difficult. The benefits to mining iron are extremely far in the future. The network needs to send a troll to a mine, take the mine action, return the iron to the shack, save up other resources to spend on some expensive powerful unit, and then use that powerful unit optimally to justify its cost. It was just too much for the network to figure out by randomly exploring, so I decided to try something different.

The new approach was to start from the basic building blocks of the game, and then slowly level up the neural network to do more complicated tasks until it is finally playing the full game. All the network training was done via PPO.

## Level 1
I chose a very simple task to start with: just get a network to build a specific unit type that I specified (let's say for example: 3/4/0/1). That itself is still quite challenging for the network to figure out, so to help it even more, I added reward shaping (like breadcrumbs) where the network was rewarded every time it got "closer" to making a 3/4/0/1 unit.

Specifically, I made a rough calculation for how many turns it would take to collect the required resources. I don't think it matters how accurate this is, anything close is probably good enough to help the network learn. For example, if I needed 3 more lemons and a lemon tree was 4 steps away from my shack and I had 2 trolls with various attributes, then I could get a rough estimate for how many turns it would take to get those 3 lemons. I did this for all the missing resources to get the total "distance" away from the target. The network was given positive (or negative) rewards every time it moved closer (or farther away) from the target.

In this setup, the network quickly learns to build any given target unit quite efficiently.

## Level 2
Extending this idea, the next level for the network was this modified environment:
 - at the start of a turn, if an agent doesn't have a target unit, randomly generate a target for it
 - the target is fed into the network's observations (more details later) so it knows what it needs to build
 - incremental rewards/penalties to encourage the network to build its target, with a big reward when the network gets all the required resources

At this stage, the network is not choosing its own train actions (yet). As soon as the required resources are reached for its assigned target, then the corresponding train action is automatically carried out and a new random target is assigned to it.

At this point, the network can efficiently build any target unit I assign to it. This is great, but it's still not learning how to use these units to actually win the game, so it will be difficult for it to know what units are good to build.

## Level 3
Making things a little more realistic for the network, the next environment is similar to Level 2 except I generated a random target number of trolls, between 2 and 5, at the start of the game. The network's reward is the same heavy reward shaping from Level 2 plus the actual endgame score difference.

To help it learn the "chop" action sooner, I gave the network 0.5 points immediately every time it deposited wood at its shack (and then counted its endgame wood as worth only 3.5 points). Along the way, I briefly added a temporary chop-incentive where I gave the network a slight bonus for taking a chop action after it has finished all its troll building tasks (probably not necessary, but it helped figure out the value of chopping down trees faster).

Note: going from Level 1 -> 2 -> 3 was the initial progression I took, but starting directly from Level 3 training also worked when I experimented with different observation planes.

Now I have a network that, when given a randomly assigned build order, can efficiently execute that build order and then use those units to maximize the endgame point differential. It's very close to being fully functional, it just now needs to figure out what units to actually build.

## Level 4
In some earlier attempts, every time I tried to allow the network to choose its own troll targets, it would find ways to game the reward shaping. For example, if the environment gave a +100 bonus every time it finished building a target unit, then the network would learn to build lots of cheap units to spam the completion bonus.

To get around this, I instead froze the parameters around the troll movement (from Level 3), and then trained a "troll plan selector" head with a completely different value head from the earlier levels. The new value head for Level 4 would be the actual endgame score difference with no reward shaping at all.

Big picture, I trained one network that can efficiently execute any build order, and then added and trained new policy and value heads whose only task is to figure out what unit to build next (if any).

## Level 5
With all the pieces in place, I then fine-tuned the whole network (all the parameters) on the actual endgame score differential (the second value head from Level 4) with no reward shaping. At this point I still wasn't sure how strong the network would be. I was hovering around 50th-100th place and my initial goal was just to make it into Legend. It was truly remarkable to see how much the network improved in the final 36 hours of training.


## Network Details


### Observation Planes (104 x 11 x 22)
| Channels | Contents |
|---:|---|
| 0 | valid cell mask (to account for different board sizes) |
| 1-6 | cell one-hot: grass, water, rock, iron, own shack, opp shack |
| 7-15 | tree: any tree; fruit one-hot plum/lemon/apple/banana; size, health, fruits, cooldown |
| 16-17 | troll occupancy: own, opponent |
| 18-27 | own troll: movement, carry cap, harvest, chop, carried resources |
| 28-37 | same for opponent troll |
| 38-41 | distances/adjacency: own shack dist, opp shack dist, adjacent iron, adjacent water |
| 42-58 | global game state: turn, own inventory, opp inventory, own/opp score, own/opp troll count |
| 59-71 | train target: has target; target movement, carry, harvest, chop; costs; deficits |
| 72-87 | aggregate troll attrs: own max, own sum, opp max, opp sum; each is movement, carry, harvest, chop |
| 88-92 | nearest useful target distance: plum tree, lemon tree, apple tree, banana tree, mine target |
| 93-96 | carried/free capacity: own carried, own free, opp carried, opp free |
| 97-99 | mini-step/train state: train queued, done-training target, active troll |
| 100-103 | other troll stats: own troll full, own full with only wood/iron, opp full, opp full with only wood/iron |

I don't think the exact observation planes are all that important and I would guess anything sensible would work. Given the time constraints, I have no idea which features are necessary or not, and erred on the side of just giving the network more information.

### Network architecture

- Input:
  - 104 x 11 x 22 observation tensor
- Stem:
  - 1x1 conv to project observation planes into CNN features
- Trunk:
  - 4 block ResNet
  - valid-cell mask applied so padded/out-of-board cells stay inactive
- Spatial policy head:
  - 1x1 conv at the end to get 13 action-type logits per cell
  - action types: move, harvest, plant X, chop, pick X, drop, mine
  - output: 13 x 11 x 22 = 3146 logits
- Global features (concat):
  - pooled CNN features
  - global state: turn, inventories, scores, troll counts, train target state
- Value head 1 (from global features):
  - used in Levels 1-3 training, heavy reward shaping
- Value head 2 (from global features):
  - used in Levels 4-5 training, actual endgame score differential
- Train-plan head:
  - scores each possible train target separately
  - combines global features with per-candidate train-plan features
  - candidate features include target attributes, costs, deficits, and whether it matches the previous target
  - output: 144 train-plan logits
- Final output:
  - 3146 spatial logits + 144 train-plan logits = 3290 action logits

One specific note about the train-plan head. In earlier versions I tried a flat 144 logit array, but I found the network was less able to generalize between similar trolls (i.e. 3/4/0/3 and 2/4/0/3 are similar, but flat logits would hide the similarity). So instead, the network produces a logit for each troll type by concatenating some board state, global state, and the specific troll target's attributes through a shared MLP to get that troll target's logit. For troll attributes, I had these restrictions:
 - movement: 1-3
 - carry: 1-4
 - harvest: 0-2
 - chop: 0-3

3x4x3x4 = 144 possible troll train targets

I masked troll targets with both harvest == 0 and chop == 0, and also masked troll targets where harvest > carry.

The first troll train target (id 0, which has harvest == 0 and chop == 0) was repurposed to mean "done training trolls."

When in the plan selection phase, the non train-plan logits are masked. When in the troll action phase, only the possible valid moves for that troll are allowed.


## Other details
For training, each game turn is split into a lot of mini environment steps. For example, each real game step consists of:
 - making a troll plan "move" (not visible to the opponent)
 - choosing a move for the first troll
 - choosing a move for the second troll
 - etc

For the final submission logic, each game turn works like this:
- generate the obs from the current game state and run it through the network to get the train-plan logits
- update the obs given the train-plan action chosen (max logit)
- for each of my trolls:
  - update the obs (just the active_troll plane needs to be updated)
  - run inference to get the troll's action logits (the first "movement" logit of every valid cell it can go to, plus all the legal non-movement logits at the troll's current cell location)
- given all the troll action logits, run a beam search over possible combinations of troll moves to find the highest probability moveset for all trolls (i.e. pick a troll, try each of its top X moves, use those moves to invalidate some other troll moves, pick the best moves for the next troll, etc)

So each turn, one inference step is needed per troll, and one extra inference step for the troll target plan. There's no turn search/lookahead being done. As a result, only the policy heads are needed after training.

The network has around 101k parameters (excluding the value heads) and the final submission file size came in at 98k characters. Inference was fast and I ended up using only around 2-3ms out of the 50ms budget each turn.

## General thoughts

I had mixed feelings on the game initially, but it really grew on me by the end, especially after seeing the diverse strategies the final network played. I really liked how unique this game was compared to previous competitions. The game reminds me of a mini real-time strategy game. The network learned to play many different styles depending on the map, sometimes choosing to "attack" or "rush" (while still developing its economy back home), sometimes choosing to play a more macro game, etc.

As strong as the network is, at times it can still do some incredibly dumb things, such as getting stuck moving in an endless circle or getting stuck forever mining iron, etc. I tried to manually patch up each of these edge cases but several still remain. It reminds me of LLMs today, where 95% of the time neural networks can be brilliant and show superhuman behavior, but then once in a while still get the simplest, most basic thing wrong.

## Closing thoughts

I want to give thanks to the Codingame community as a whole. It’s the perfect environment for learning new algorithms and skills. My favorite part of these competitions is reading everyone’s writeups afterwards. I’ve learned so much from them, and I love how open and supportive everyone is as we all keep training our own human neural nets: learning new skills, taking on harder challenges, and leveling ourselves up.
