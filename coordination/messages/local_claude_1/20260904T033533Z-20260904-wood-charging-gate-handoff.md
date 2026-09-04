---
schema_version: 2
type: handoff
task_id: 20260904-wood-charging-gate
from: local_claude_1
to: ["claude_1"]
cc: ["user", "chatgpt_1", "chatgpt_2"]
message_id: coordination/messages/local_claude_1/20260904T033533Z-20260904-wood-charging-gate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 9d5518fd36ba2b067881c75800c0ac42cbfa1d8f
artifact_paths: ["coordination/tasks/20260904-wood-charging-gate.md", "coordination/tasks/20260904-instrument-audit.md", "coordination/GRAVEYARD.md", "coordination/BOARD.md"]
created_utc: 2026-09-04T03:35:33Z
---

- To: claude_1
- CC: user, chatgpt_1, chatgpt_2
- Task: 20260904-wood-charging-gate
- Requires acknowledgement: yes — a new card, chartered to you on the owner's approval. Acknowledge with your start
  time and an estimate per gate.

# HANDOFF — make the troll pay for the wood it costs; the champion is the control; one variable and nothing else

The card at the pin carries it whole. The owner approved it in their own words, and their phrasing is the clearest
statement of the rule anyone has managed: **"we are going to predict two outcomes: with troll and without, and if
'with' wins, we do it."**

## The rule, and the one thing it must not become

At the moment a troll would commit to a trip that funds the third troll, estimate both futures over the same turns —
those turns spent **funding**, against those turns spent **chopping wood at four points a unit** — and commit only if
the troll wins. Re-evaluate from the live board each turn; abandon back to the champion's ordinary play when it stops
winning.

**The forecast is what is actually under test, and it is the part most likely to fail.** chatgpt_2 built a gate of this
shape yesterday. It did not decline the troll — it bought a **cheaper one sooner** (median game turn 30, the weakest
tuple `1 1 0 1` ten times of fourteen) and lost 416 points a game to the resident. So a dead condition on your card is
that **the gate must decline a third troll in at least some smoke games**; a gate that never says no is not a gate,
only a differently-timed purchase.

## One variable

The base is the champion of record unchanged (sha `0e92f8fa…`) through a generator, every replacement matched exactly
once. **No turn-2 second troll. No joint three-troll selector. Nothing else.** Those are separate questions and mixing
them in is precisely what made yesterday's result unreadable.

**The control is the champion itself**, unmodified. That is the point of the design: it clears the mechanics bar by
construction, so the comparison cannot be destroyed by a damaged control — which is how chatgpt_2's build lost the only
measurement it existed to make (its control stalled on 9 maps of 24).

## Gates and the pre-registered dead conditions

The bed, the 24-map smoke, the timing, then the paired 200-map panel against the champion **and** the four-opponent
field reading. Dead: any compile, round-trip or mechanics failure — **the smoke must read 24/24 and no map may stall**;
p99 warm turn at or above 40 ms; the field reading below zero with its interval clear of zero; or the gate never
declining a troll. Report the decline count and reasons, the third troll's arrival **in game turns** (converted from the
referee's frame index — it is two frames to a turn, and misreading it cost this record four hours yesterday), the
tuples chosen, and the wood banked by turns 50 and 100 against the champion's.

## Two measurement facts you should build against

An instrument audit is running as I write this, and it has already established two things that bear on your card:

1. **The champion's own file, submitted four times, read 17.04, 18.14, 18.19 and 18.72** — a spread of **1.68** with
   nothing changed about the bot. **No ladder difference below about 1.7 is evidence of anything.** Do not design for a
   small edge; it would be unmeasurable.
2. **The duel against the champion inverts against the ladder.** orchard 6 loses the duel 65 of 400 — clearly worse
   than the champion's 113 against itself — and yet read **18.84** on the ladder against the champion's 18.19 the same
   week. So a duel is not a selector. The field reading is. I am running orchard 6's field reading now as the decisive
   test of whether even that is trustworthy; if it changes the picture, **I will revise your card's field condition
   before your reading is taken, never after.**

Send a progress message **with each commit**, not after the last gate. Budget to 2026-09-06 04:00Z.

— local_claude_1, coordinator
