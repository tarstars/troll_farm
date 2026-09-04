# Task 20260904-wood-charging-gate — pay for the troll only if the troll beats the wood

- Born: 2026-09-04 03:3xZ on the owner's approval. The owner's own words for the rule, which are exactly right:
  *"we are going to predict two outcomes: with troll and without, and if 'with' wins, we do it."*
- Work owner: **claude_1** (builds). Verifier: **the coordinator** (reproduces every number by execution from the
  pinned commit). The owner reads one page and gives the prediction if it reaches a ladder hour.
- Budget: one build, one bed, one smoke, one timing run, one paired panel and one field reading. Two days, to
  **2026-09-06 04:00Z**. No evidence for two days = STALLED and the owner says kill or extend.

## Why this one, after six roster lines have died

Every previous attempt bought the roster and let the funding trips **suppress** the wood trips. The record says that is
what killed them: the port banked one-point fruit for a hundred turns while the champion banked four-point wood and was
thirty points ahead by turn 50; stage 2A reached three trolls **23 turns ahead of the field** and still read 4.13 below
the champion. So the defect was never the timing. **It is that nobody ever made the troll pay for the wood it costs.**

This card tests exactly that and nothing else.

## The rule

Inside the bot, at the moment a troll would commit to a trip that funds the third troll: estimate both futures over the
same turns — those turns spent **funding**, against those turns spent **chopping wood at four points a unit** — and
commit to the funding trip only if the troll's estimated contribution wins. Re-evaluate from the live board each turn
and abandon back to the champion's ordinary play when it stops winning.

**The forecast is the thing actually under test, and it is the part most likely to fail.** chatgpt_2's build had a gate
of this shape and it fired the wrong way: instead of declining the troll it bought a **cheaper one sooner** (median
game turn 30, the weakest tuple `1 1 0 1` ten times of fourteen) and lost 416 points a game to the resident. So the
report must state how often the gate **declines** a troll, not only how often it funds one.

## The build

- **Base: the champion of record, unchanged** (`readable/denial-off-champion.rs`, arm
  `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…`), through a generator as every
  build in this project is made, every replacement matched exactly once.
- **One variable.** No turn-2 second troll, no joint three-troll selector, no other departure. Those are separate
  questions and mixing them in is what made yesterday's result unreadable.
- **The control is the champion itself**, unmodified. That is the whole point: it clears the mechanics bar by
  construction, so the comparison cannot be spoiled by a damaged control the way chatgpt_2's was.

## Gates, and the pre-registered dead conditions

Done means: the generator, the readable source and diff, the compacted candidate, an exact compile and round trip, the
frozen 34-case bed, the 24-map smoke, one-core turn timing, the paired 200-map panel against the champion, and the
four-opponent field reading (the champion of record, orchard 6, the old champion with denial on, the network clone).

**Dead, written before any number exists:**

1. any compile, round-trip or mechanics failure — **the smoke must read 24/24 mechanics, and no map may stall**;
2. p99 warm turn time at or above 40 ms (the champion's own is about 2 ms, so this is slack, not a target);
3. ~~the field reading below zero with its 95 % interval clear of zero~~ — **AMENDED 2026-09-04 03:5xZ, before any
   reading of this card exists, by the instrument audit's ruling: the win-rate field reading is retired as a kill
   criterion.** It returns a confident `FIELD_BELOW_ZERO` (−0.1969, interval clear of zero) for orchard 6, a bot the
   ladder cannot distinguish from the champion, and it puts orchard 6 and the opening dispatcher 0.025 apart when their
   ladder outcomes are 4.78 apart. **The selector is now Δmargin with its 95 % interval, and this card is dead only if
   its Δmargin interval lies clear below about −20** (provisional, calibrated on two points: orchard 6 at −18.74 is
   ladder-neutral, the dispatcher at −28.71 was 4.13 down). Report Δwin as well, as a fact, but it decides nothing;
4. the gate never declining a third troll in any smoke game — that would mean it is not a gate at all, only a
   differently-timed purchase, which is how the last one failed.

**Report regardless of the verdict:** how many games the gate declined the troll and why, the third troll's arrival in
**game turns** (converted from the referee's frame index, convention named), the tuples chosen, the wood banked by
turn 50 and turn 100 against the champion's, and the paired panel with its interval.

## The measurement caveat that applies to this card

An instrument audit is running as this card is written (`coordination/tasks/20260904-instrument-audit.md`). It has
already established that **the duel against the champion inverts against the ladder** — orchard 6 loses the duel 65 of
400 and yet read 18.84 on the ladder against the champion's 18.19 the same week — and that **the champion's own file,
submitted four times, read 17.04 to 18.72**, a spread of 1.68 with nothing changed. So: the duel alone is not a
selector, the field reading is the selector, and no ladder difference smaller than about 1.7 means anything. If the
audit changes what we believe about the field reading, this card's condition 3 is revised **before** the reading is
taken, never after.

## Log

- 2026-09-04 03:3xZ born on the owner's approval; chartered to claude_1. — coordinator
