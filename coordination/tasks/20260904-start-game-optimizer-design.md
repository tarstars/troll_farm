# Task 20260904-start-game-optimizer-design — design a proper start-game optimizer

- Born: 2026-09-04 07:2xZ on the owner's word: **"ask it to design proper start-game optimizer"**, addressed to
  chatgpt_1 immediately after its judgement round.
- Work owner: **chatgpt_1** (the design). Verifier: **the coordinator**. Kind: **one design round. No build, no bot
  integration, no ladder, no platform.** A build, if any, is a separate card on the owner's word.
- Budget: one round, two days, to **2026-09-06 08:00Z**.

## Why now, and why chatgpt_1

The owner watched the live games of the three-troll bot and named the defect in one line: *"optimization doesn't
include planting trees, because of it trolls are weak and wood gain is small."* Verified in source — **neither
optimizer this project has built has `PLANT` in its action space.** chatgpt_2's reads `view.plants` seventeen times as
harvest sources and never issues a plant command; claude_1's wood-charging forecast values the troll entirely out of the
**existing** forest. Both searched a roster against a fixed, depleting resource base. chatgpt_1 generalised this in its
own judgement round into a rule now in force: **every optimizer must publish its action vocabulary.**

chatgpt_1 owns the two instruments this needs: the offline DP/A* oracle with dominance pruning and an optimality
certificate (delivered 11:15Z on 09-03, verified), and the Rust anytime planner with an always-valid greedy incumbent,
admissible bounds, wall-clock and expansion budgets and a beam fallback (delivered 12:01Z, 7 of 7 tests reproduced by
the coordinator). It is unassigned as of 07:16Z.

## What the design must settle — these are the questions, not a specification

1. **The objective, and why it is not the one we used before.** Stage 1's solver maximised *the turn the third troll
   arrives*. That objective is now measured and it is wrong: stage 2A reached three trolls about **23 game turns ahead
   of the field** and still read **4.13 rating points below the champion**. Name the objective this optimizer maximises
   — the coordinator's expectation is expected own score at turn 300 under a stated continuation policy, in points, not
   a roster time — and say how it is computed and what it assumes.
2. **The action space, published in full.** Which of MOVE, HARVEST, PLANT, PICK, DROP, CHOP, MINE, TRAIN are searched,
   which are fixed by rule, and why. **`PLANT` must be searched**, competing turn by turn against chopping and
   gathering on the same points-per-turn scale — that is the owner's question and the reason this card exists.
3. **The forest as a finite, contested resource.** claude_1 measured the failure precisely: a forecast that values wood
   as *rate × turns remaining* over-states it about **tenfold**, because by turn 108 four trolls have been felling the
   map for a hundred turns. State how the design bounds the wood actually convertible, and how planting changes that
   bound over time.
4. **The opponent model.** **Not idle.** The idle-board assumption is what made stage 2A promise turn 70 and deliver
   74.5 into a stripped forest. Use the measured raid process: near trees taken at **0.19 per 100 tree-turns before
   turn 100** and **0.6–1.0 after**; the opponent plants about **25.8 trees a game** and harvests **23.5 fruit** from
   them.
5. **The horizon and the hand-back.** Where does the optimizer stop and the champion's ordinary play resume, and what
   is the evidence for that boundary rather than another?
6. **The compute budget, measured not projected.** 1,000 ms on turn 1 and 50 ms a turn after, one core. chatgpt_1's own
   anytime planner benchmarks 378 ms and 84 MiB on its larger case, so it can cost this honestly rather than guess.
7. **The gates a build would have to pass, written before the build exists** — including, per chatgpt_1's own adopted
   ruling, a **fresh holdout panel** not used to choose the rule or its thresholds, because the 24-map smoke and the
   pinned 200-map panel are development data now.
8. **Its own falsification.** What result would show this design is wrong? Seven roster lines have died here; a design
   that cannot be killed by a measurement is not a design.

## What it must NOT do

No build, no bot integration, no ladder or platform action, no cluster or host job. It must not duplicate the live
orchard-kinetics read (claude_1, due 2026-09-05 18:00Z) — instead it must **state what it needs from that read** so the
two compose: the read supplies the wood-versus-time curve and the value of a planting turn, and this design supplies
the search that would exploit them.

## Log

- 2026-09-04 07:2xZ born on the owner's word; chartered to chatgpt_1 as one design round. — coordinator
