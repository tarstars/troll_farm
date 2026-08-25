# Is there a road around the standing teammate? — what the two instrumented reads say (owner brief, 2026-08-25)

Task `20260825-dance-geometry-measurements`, run under the mission you activated this afternoon
("create goal file for measurements you just mentioned"). Definitions were fixed before any count
and accepted by `codex_1` (three revisions in 22 minutes); the measurement was built and run by
`claude_1`; every number below was **re-derived by me from the published turn rows**, and
`codex_1`'s independent re-run from a fresh archive reproduced the result files **byte for byte**
(15:26Z). Plain words; every code explained at first use. **No ruling is made here — the
swap-or-route-around decision stays yours.**

**Caveats that travel with every number:** a "dance" (detector D-1: one of our trolls stepping
a→b→a→b for ≥ 7 turns with zero progress) counted off replays is an *upper bound*; the two reads are
different days and opponent fields, not randomised; the counts are 80 + 25 dances.

## The answer in one paragraph

**Usually there is no road around.** On the older read (469 games, 80 dances) the standing teammate
stood on **every** shortest road to the dancer's own goal on **1,306 of 1,432** measurable turns
(91 %); on the newer read (160 games, 25 dances) on **328 of 420** (78 %). On a third of those turns
— **439** and **55** — taking that one teammate's square away left the goal **unreachable**: the
maps are small and the teammate stands in a doorway. Per dance (typical extra cost of the detour,
105 dances): **29 have no road around at all**, **40** have one costing 1–2 extra squares, **15**
cost 3–5, **13** cost more than 5, **7** had a free road, and **1** could not be measured (its
teammate stood *on* the goal for the whole dance). The column we committed to before counting —
turns where a zero-cost road existed and the troll still did not step forward — came back **0 on
both reads**. And on the older read's 25 short dances that began with "nobody next to the dancer",
one of **our own** trolls was on the square the dancer wanted on **60 of 68** backward steps (27
standing, 33 arriving or leaving); only 8 steps had nothing of ours there. "Nobody adjacent when it
began" did not mean "nothing in the way".

## What each answer means for the open choice (evidence, not a recommendation)

- **Route around** (plan the path with the standing teammate as a wall): has room where a road
  exists — **68 of 105** dances (40 at +1–2 squares, 15 at +3–5, 13 at more than 5), and a 1–2 square
  detour is cheap against a dance that runs 10–20 turns. It can do **nothing** for the 29 dances
  with no road, nor where the dancer wants the very square the teammate works (10 + 15 turns, one
  whole 33-turn dance).
- **Swap** (exchange squares once, with a no-swap-back lock): the only mover-side remedy for the
  no-road dances and the doorways; its cost is the teammate's square — that teammate is working it
  (on a plant in 24 of 34 and 17 of 21 of the older read's standing cases), so a swap displaces a
  working troll unless the pair is allowed to step back once the dancer has passed.
- **Neither** touches the teammate-on-the-goal case (the OSC-030 shape: the dancer wants the tree
  its teammate is on) — that is a planner question, not a mover one.
- The **short** dances (7–11 turns) are where "no road" concentrates (17 of the older read's 23
  no-road dances) and where the passing-through teammate lives (33 of 68 steps): doorway traffic.

## Table 1 — typical detour cost × where the teammate stood when the dance began

Shapes: *one-cell* = teammate on one square, adjacent, the whole dance; *adjacent* = next to the
dance at its start, moved once; *nobody* = nobody of ours adjacent at the start.

| read | cost class | one-cell | adjacent | nobody | total |
|---|---|---:|---:|---:|---:|
| older (80) | free road (0) | 0 | 1 | 5 | 6 |
| older | +1–2 | 14 | 6 | 6 | 26 |
| older | +3–5 | 6 | 5 | 1 | 12 |
| older | more than 5 | 4 | 4 | 5 | 13 |
| older | **no road (∞)** | **10** | **5** | **8** | **23** |
| newer (25) | free road (0) | 0 | 0 | 1 | 1 |
| newer | not measurable (teammate on the goal) | 1 | 0 | 0 | 1 |
| newer | +1–2 | 9 | 5 | 0 | 14 |
| newer | +3–5 | 2 | 1 | 0 | 3 |
| newer | **no road (∞)** | **3** | **3** | 0 | **6** |

## Table 2 — typical detour cost × how long the dance lasted

| read | cost class | 7–11 turns | 12–29 | 30 or more |
|---|---|---:|---:|---:|
| older | free road (0) | 5 | 0 | 1 |
| older | +1–2 | 11 | 9 | 6 |
| older | +3–5 | 8 | 2 | 2 |
| older | more than 5 | 10 | 2 | 1 |
| older | **no road (∞)** | **17** | 0 | **6** |
| newer | free road (0) | 1 | 0 | 0 |
| newer | not measurable | 0 | 1 | 0 |
| newer | +1–2 | 3 | 7 | 4 |
| newer | +3–5 | 3 | 0 | 0 |
| newer | **no road (∞)** | **5** | 1 | 0 |

Beside both tables, an upper bound: among blocked turns a *sideways* step no farther from the goal
existed on 52 % (older) / 38 % (newer) — an upper bound, because the replay cannot see two of the
bot's own within-turn exclusions.

## Table 3 — what stood on the wanted square on each backward step (older read)

| dances | standing (there this turn and last) | passing through (arrived / leaving) | nothing of ours |
|---|---:|---:|---:|
| all 80 | 561 | 64 | 9 |
| one-cell 34 | 387 | 14 | 0 |
| adjacent 21 | 147 | 17 | 1 |
| **nobody 25 (the question)** | **27** | **33** | **8** |

Newer read, all 25: 188 standing, 10 passing, 0 nothing. No step was left undetermined. The nine
"nothing of ours" steps are listed whole in the results; two coincide with the dancer changing its
mind about the goal.

## The checks that make the numbers trustworthy

Walling a random far square instead of the teammate's square blocks the dancer on **1.1 %** of the
same turns, against **88 %** for the teammate's square — the measure sees the teammate, not the
map. On the newer read the bot's own per-turn letter for "stepped back because my next square was
taken" agreed with the geometry on **191 of 191** turns where the comparison is defined; on the
seven remaining "stepped back" turns the teammate stood on the goal itself, so no road could be
measured — and on **all 198** the teammate was on the wanted square. Two runs byte-identical, and
`codex_1`'s fresh-archive run byte-identical to both; all 105 dances reconciled, 0 refused; the
input rows hashed to the pinned digests; the older read's telemetry shim checked on 865 turns with
0 mismatches. Three things the builder found and reported rather than fixed quietly, each ruled on
by `codex_1`: a category table lacking a row for "teammate on the goal" (added; one dance's class
moved from "free road" to "not measurable"), a position-derived key that had merged two dances
(repaired, now asserted one-to-one as a standing control), and the need to reconstruct "who is
moving" from chosen targets rather than replayed commands (faithful to the bot).

## What this does not say

Nothing about score cost; no bug ruling; no change to the accepted classification of the dances;
nothing about opponents. The re-read that motivated these measurements (teammate next to the dance
at its start in 55 of 80 and 24 of 25) is on the record with its own caveats and was audited at the
definitions gate: it holds, narrowed to the games where the bot's hold rule was switched on (22 of
the newer read's 25 dances).

## Where everything lives

Definitions of record `claude_1/geometry1/definitions-g0-2026-08-25-r2.md` (`agent/claude_1@858b5c37`);
measurement, results (every dance, every turn) and execution report `claude_1/geometry1/` at
`agent/claude_1@c5727dc6` (`results/geometry-2026-08-25.json` sha256 `acb2feed…`);
`codex_1/reviews/dance-geometry-measurements-g0-2026-08-25.md` and `…-g1-2026-08-25.md`
(`agent/codex_1@28401227`: reproduction, the three rulings, the re-issued classes); my re-derivation
`coordination/messages/local_claude_1/20260825T145434Z-…-ack.md`; the input note
`local_claude_1/dance-geometry/re-read-2026-08-25.md`; the task record
`coordination/tasks/20260825-dance-geometry-measurements.md`.

One operational note from the afternoon: the VM's disk was full (a peer's old scratch extracts),
which silently killed the first reproduction attempt; cleaned, rule published, nothing lost.
