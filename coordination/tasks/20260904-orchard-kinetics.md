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
