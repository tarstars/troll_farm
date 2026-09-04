# Task 20260904-orchard-kinetics — grow the forest the third troll arrives into

- Born: 2026-09-04 05:4xZ, the owner's own idea, minutes after the wood-charging gate died. The owner's words:
  > *"in order [for the] third troll to be efficient, an orchard should be already planted and then replenished. Lean
  > orchard strategy means that we are to carefully calculate planting dynamics: plant apple, plum and lemon near the
  > tent with the first troll (or two trolls), collect resources for the third one, plant orchard, maintain orchard,
  > chop down orchard. Kinetics of orchard should be orchestrated with kinetics of trolls."*
- Work owner: **claude_1** (the read). Verifier: **the coordinator**. Kind: **a read on the exact referee, not a
  build.** No bot, no ladder, no platform.
- Budget: one read, two days, to **2026-09-06 06:00Z**.

## Why this is the right question, and why it is not a seventh repeat

The wood-charging gate (dead this morning) measured the trade honestly and found the third troll adds **no whole-game
wood**: it arrives at median game turn 108 into a forest four trolls have been felling for a hundred turns. **The owner's
reading of that is the correct one — the defect is not the troll, it is that there is nothing left for it to cut.**

**This is not the old orchard line.** Those builds (orchard 5–8, the three heroes, the apple farm) planted in order to
**fund** the troll: fruit into the shopping list, at one point a unit. The owner is describing planting to **feed the
wood race**: plant, maintain, then fell, at **four points a unit**. Nobody has tested that objective.

And the old line's closure is weaker than the board implied. **Orchard 6 read 18.84 against the champion's 18.19 —
inside the 1.68 ladder noise the instrument audit measured this morning**, so it was *indistinguishable*, not beaten;
orchard 8 read 17.98 on the same footing. Those bots were retired on readings that could not resolve them, and partly
on the win-rate field panel that was retired today. **Nothing in the record refutes an orchard; it only fails to
support the ones we built.**

## What the record already gives the planner, for free

- **The top four plant about 29 trees a game and their own trees overtake wild ones as the harvest source by turn
  40–70.** We plant **9.8**. The opponent in our own collected games plants **25.8** and takes **23.5 fruit** from them;
  we take **0.03**. (`claude_1/live-observations/READ-2026-09-04.md`, and the Track R reconstructions.)
- **Water is the whole game for timing.** A plum or lemon first bears about **32 turns** after planting inland but
  **12 beside water**; an apple **36 against 8**; a banana **24 against 16**. A full tree regrows one fruit the instant
  it is harvested, which is what makes "maintain" a real phase.
- **Raids are cheap early and dear late:** near trees are taken at **0.19 per 100 tree-turns before turn 100** and
  **0.6–1.0 after**, and roughly **8 near trees per 3 chop power** is the balance the solver's stage 1 measured.
- The champion already plants 9.8 and fells **81 %** of its banked plums and lemons — so the machinery exists; what is
  missing is scale, placement and timing.

## The read (no build)

Use the opening solver, which is referee-exact and already verified (1,492 of 1,492 schedules replayed exact), to
answer the kinetics question the owner poses — **on the pinned 200-map panel, with the opponent modelled as raiding at
the measured rate, not as idle** (the idle-board assumption is what cost stage 2A):

1. **How much wood can an orchard actually deliver, and when?** For a schedule that plants k trees near the tent at
   turns t₁…t_k (water-adjacent where the map allows), what is the standing convertible wood at turns 100, 150, 200,
   250 and 300, as a function of k and of the chop power available to fell it?
2. **Does the third troll pay when it arrives into that orchard?** Re-run the wood-charging comparison — the troll's
   wood from arrival to the end against the wood forgone funding it — but with the orchard's standing wood in place of
   the emptied wild forest. **This is the question the whole card exists to answer.** The gate declined on all 4,593
   turns against a bare board; report the decline rate against a planted one.
3. **What does the orchestration actually look like?** The turn to start planting, the number of trees, the order of
   plant / maintain / fell, and when felling should begin — and how much of it the *champion's existing* planting
   already achieves, since it plants 9.8 trees unaided.
4. **What does it cost?** Planting turns are turns not spent cutting or gathering. Report the wood forgone during the
   growing phase, which is exactly the cost that sank every previous roster attempt.

**Dead on paper:** if an orchard of the size the map allows cannot put more convertible wood in front of a turn-100
troll than the wild forest already does, say so with the number and stop — no build follows.

**Report:** one page in plain words with the turn numbers, the wood curve, and a straight yes or no on whether a third
troll pays when it arrives into a grown orchard. A build, if any, is a separate card on the owner's word.

## Log

- 2026-09-04 05:4xZ born from the owner's own idea; chartered to claude_1 as a read. — coordinator

## AMENDMENT 2026-09-04 06:3xZ — the owner's second observation, and it generalises: PLANTING IS NOT IN ANY OPTIMIZER'S ACTION SPACE

The owner watched the live games of chatgpt_2's bot on the ladder (submission `41239996`) and reported:

> *"optimization doesn't include planting trees, because of it trolls are weak and wood gain is small"*

**Checked in the source, and it is exactly right — of both optimizers we have built.** In chatgpt_2's
`optimizer.rs.in` the word `plant` occurs 17 times and **every occurrence reads `view.plants`, the trees already
standing on the board, as harvest sources**; it never issues a `PLANT` command, and a grep for one returns nothing.
claude_1's wood-charging gate is the same: its forecast values the troll's future wood entirely out of the **existing**
forest. So both searched over *roster tuples and trip assignments against a fixed, depleting resource base*, and
neither could ever choose to enlarge that base.

**That is a better explanation of the last two failures than either build's own post-mortem gave.** The trolls come out
weak because the optimizer picks the cheapest tuple that its forecast can justify against a forest that is being cut
away, and the wood gain is small because nothing in the search creates wood — it only divides what is already there.
It also explains the shape of the choices: chatgpt_2's optimizer took the weakest tuples available (`1 1 0 1` ten times
of fourteen), and claude_1's took speed 1 with chop 3 in 19 of 22 — in both cases a small troll, because a large one
could not repay itself out of a shrinking forest.

**So this card's requirement is strengthened, and this is the point of it:** it is not enough to model an orchard as a
fixed prelude that happens before the optimizer runs. **PLANT must be inside the searched action space**, competing
turn by turn against harvesting, mining, chopping and training on the same points-per-turn scale — so the planner can
choose to spend turns now creating wood that will exist at turn 150. Question 3 on this card ("what does the
orchestration look like") is therefore the co-optimization question the owner is naming: **the planting schedule and
the troll schedule are one problem, not two.**

Two consequences for the read:

- Report the value of a planting turn **on the same scale** as a chopping turn, so the comparison the planner would
  make is visible in the numbers even before any bot exists.
- Report what the champion's own unaided 9.8 trees are already worth on that scale, since that is the baseline any
  planned orchard must beat — and the top four's ~29 trees are the ceiling to aim at.

- 2026-09-04 06:3xZ the owner's planting observation folded in, verified in both optimizers' sources. — coordinator

## AMENDMENT 2026-09-04 08:0xZ — mechanics verified in the referee, and one of them changes the crop choice

chatgpt_2 sent an unprompted supplement to this read (`20260904T071400Z`, its own directory, no claim on the card).
**The coordinator checked its mechanical assertions directly against `sim/engine.py` rather than accept them, and every
one holds.** They are recorded here as facts of record so the read need not re-derive them:

- **A mature tree is worth 16 points, not 4.** `WOOD_POINTS = 4` and felling yields `plant.size` wood, so a size-4 tree
  gives 4 wood at 4 points each. Thirty planted trees are therefore **480 points of gross standing potential** against a
  champion score of about 184 a game — the orchard is not a marginal resource if it can be felled and banked.
- **Health at maturity differs by species, and by a lot.** `TREE_HEALTH_BASE` is plum 4, lemon 4, apple 8, banana 2 and
  `TREE_HEALTH_SLOPE` is plum 2, lemon 2, apple 3, banana 1, so at four growth steps: **banana 6, plum and lemon 12,
  apple 20.** Every species still yields the same 4 wood.
- **Therefore bananas are the efficient wood crop, and by a wide margin.** A chop-1 troll needs **6 turns to fell a
  banana against 20 for an apple**, for the identical 16 points — **3.3 times the wood per chop-turn.** And the referee
  prices bananas at **zero** for training, so a banana consumes no resource the roster needs. **Plant bananas for wood
  and keep plums, lemons and apples for the training bill** is a candidate rule that falls straight out of the
  mechanics and that no bot of ours has ever followed. The read must price the species separately rather than assume a
  uniform orchard.
- One referee quirk to respect in any felling estimate: the chop loop is commented *"last wood can duplicate"* — with
  several choppers on one tree the final wood unit can be issued more than once. chatgpt_2 correctly excluded this from
  its single-tree instrument; a multi-chopper schedule must not.

**Three of its design points are adopted into this read as requirements:**

1. **One mutable future-forest state.** The forecast, the admission test and the emitted policy must share it. If
   planting is added only to the dispatcher, execution creates wood the value model still believes cannot exist — which
   is a new way to reproduce the tenfold over-statement from the other direction.
2. **Compare two optimized worlds, not a bot against a bot.** Best turn-300 value with `PLANT` **and** `TRAIN`, minus
   best turn-300 value with the same orchard action space and `TRAIN` **disabled**, under identical opponent scenarios.
   Anything else confounds the orchard's value with the troll's.
3. **The event-driven DP oracle is the right base**, not a fixed-deficit assignment that assumes fixed sources and
   additive resource curves.

Its nine-test single-tree kinetics instrument is at `chatgpt_2/orchard-kinetics/`; the coordinator has verified the
mechanics it encodes, not yet re-run its tests.

- 2026-09-04 08:0xZ chatgpt_2's supplement verified against the referee and folded in; the banana finding is new. — coordinator
