# Task 20260904-start-game-optimizer-build — build the start-game optimizer

- Born: 2026-09-04 10:2xZ on the owner's word: **"tell chatgpt_1 to implement its design."**
- Work owner: **chatgpt_1** (builds). Verifier: **the coordinator** (reproduces every number by execution from the
  pinned commit; nothing enters the record otherwise). The owner gives the prediction if it ever reaches a ladder hour.
- Budget: one implementation, one validity/smoke/timing run, one paired panel, one report and handoff. Three days, to
  **2026-09-07 10:00Z**. No evidence for two days = STALLED and the owner says kill or extend.
- The specification is chatgpt_1's own accepted design, `chatgpt_1/start-game-optimizer/DESIGN-2026-09-04.md`, and its
  eight answers are binding as written.

## The gate the owner has lifted, stated plainly so the record is honest

The coordinator accepted the design at 08:0xZ **gated on two things**: the orchard-kinetics read clearing its no-code
gate, **and** the owner's word. The design gates itself the same way — its own falsification reads *"no build if
orchard kinetics cannot make eight net points on 60 % of development maps."*

**The owner has given the word with the read still outstanding.** So this build proceeds on an untested premise, and
that is recorded rather than glossed: **if claude_1's read comes back dead on paper, this build may be discarded.** The
owner has accepted that risk; the coordinator's advice was to wait, and the owner's call overrides it.

**What makes it a defensible call:** the architecture does not depend on the answer. The event-driven search, the
published action space with `PLANT` inside it, the mutable future-forest state, the replay harness and the mechanics
gates are all needed whatever the orchard turns out to be worth. Only the *parameters* — growth curves, worker-turn
costs, raid survival, the best orchard size and timing — come from the read. **So build the machine and parameterise
the numbers; do not hard-code them.**

## Inputs already verified, so the build need not wait for all of them

These are facts of record, checked in `sim/engine.py` by the coordinator, and may be used immediately:

- **A mature size-4 tree is 16 points**: `WOOD_POINTS` is 4 and felling yields `plant.size`.
- **Health at maturity, all yielding the same 4 wood**: banana 6, plum 12, lemon 12, apple 20
  (`TREE_HEALTH_BASE` 2 / 4 / 4 / 8, `TREE_HEALTH_SLOPE` 1 / 2 / 2 / 3). A chop-1 troll therefore fells a **banana in 6
  turns against an apple's 20**, and the referee prices bananas at **zero** for training.
- **First fruit**: plum and lemon about 12 turns beside water against 32 inland; apple 8 against 36; banana 16 against
  24. A full tree regrows one fruit the instant it is harvested.
- **The measured raid process**: near trees taken at 0.19 per 100 tree-turns before turn 100 and 0.6–1.0 after; the
  opponent plants about 25.8 trees a game and takes 23.5 fruit from them.
- **The champion plants 9.8 trees a game unaided and fells 81 % of its banked plums and lemons**; the top four plant
  about 29 and their own trees overtake wild ones as the harvest source by turn 40–70.
- **Provisional, from claude_1's uncommitted work and to be confirmed:** the median map offers about **11.5 free
  planting cells within two steps of the shack** (q1 9, q3 14, min 3). This bounds the orchard's size before any timing
  question and must be treated as provisional until the read lands.
- The referee's chop loop is commented **"last wood can duplicate"** — a multi-chopper schedule must respect it.

## Gates and dead conditions — the design's own, and they bind

Done means: the generator, the readable source and diff, the compacted candidate, an exact compile and round trip, the
published **action manifest**, the frozen 34-case bed, the 24-map smoke, one-core turn timing, the budget-quality
curve, the paired 200-map panel and the four-opponent field reading — and finally the **sealed fresh holdout**, revealed
only after the source and every threshold are frozen.

**Dead:**

1. **Mechanics first and mechanics hardest.** The 24-map smoke must read **24/24 with no map stalling**, and both arms
   must pass independently. This is what killed the last two builds in this family before any value number could be
   read; run it before anything expensive.
2. Any compile, round-trip or replay failure; exact macro replay is required.
3. p99 warm turn time at or above the design's own internal stop (35 ms planning, 850 ms on turn 1), against platform
   limits of 50 ms and 1,000 ms on one core; source below 100,000 UTF-16 units; memory no more than 128 MiB.
4. The search normally returning the no-plant champion, or over-stating wood by more than 1.5× at the 90th percentile.
5. Failing the sealed holdout: the bar is paired mean margin at least **+8** with its lower 95 % bound above zero,
   own-score lower bound non-negative, and non-negative mean in three of four opponent archetypes. **Note the
   coordinator's standing caveat: the +8 is an assumption, not a calibrated threshold** — every calibration point we
   hold is on the negative side, so this build may be the one that anchors the positive side.

**Selector rules in force:** Δmargin with its 95 % interval decides, Δwin is reported and decides nothing; a candidate
that is itself one of the four panel opponents has that cell dropped; and no ladder hour is spent on an expected effect
below about **2.2**, the measured noise floor.

## Bounds

No ladder, no platform, no Arena, no cluster, no champion edit, no `main` write outside its own namespace. A ladder
submission needs the owner's prediction asked in chat and that is the coordinator's to do.

## Log

- 2026-09-04 10:2xZ born on the owner's word, with the orchard gate lifted and the risk recorded; chartered to
  chatgpt_1. — coordinator

## AMENDMENT 2026-09-04 11:2xZ — the planting geometry, measured, and it constrains the search

claude_1 computed the map geometry before it ran out of credits, and the coordinator preserved and committed the
result (`claude_1/orchard-kinetics/results/curve.json`, 400 map-seats). **These are hard bounds on any orchard the
optimizer can plan, and they should be inputs to the search rather than discoveries within it:**

| free planting cells within | median | q1 / q3 | min / max | of which water-adjacent (median) |
|---|---|---|---|---|
| 2 steps of the shack | **11.5** | 9 / 14 | 3 / 19 | **2.0** |
| 4 steps | **27.0** | 21 / 34 | 9 / 48 | **5.0** |
| 8 steps | — | — | — | **13.0** |

The starting fruit draw is a median of **24** over the same map-seats, which bounds how much planting the opening can
fund before any harvesting.

**Two consequences the search must respect:**

1. **A thirty-tree orchard cannot be planted close to the tent.** The median map holds 11.5 free cells within two steps
   and 27 within four, so the 480-point ceiling implied by thirty mature trees requires planting out to **four steps** —
   with the extra walking, and the raid exposure that distance brings (0.19 per 100 tree-turns before turn 100, but
   **0.6–1.0 after**). Tree count and tree distance are one decision, not two.
2. **Water-side planting is scarce and water is what makes trees fast** — 2 free water-adjacent cells within two steps,
   5 within four, 13 within eight, against first-fruit times that water cuts from 32 turns to 12 (plum, lemon) and 36
   to 8 (apple). **So the fast orchard is small and the big orchard is slow.** The optimizer should treat the
   water-adjacent cells as a scarce resource to be allocated by species, not as a preference.

Combined with the felling costs already on this card — banana 6 chop-turns against apple's 20 for the same 16 points,
and bananas costing nothing toward training — the species/placement choice is a real optimization, which is precisely
what a search with `PLANT` in its action space exists to do.

- 2026-09-04 11:2xZ geometry added from claude_1's preserved work. — coordinator
