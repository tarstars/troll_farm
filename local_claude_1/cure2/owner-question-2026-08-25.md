# Candidate 2 (the swap) — stop and ask, v2 with the diagnoses: the loop is a goal re-assignment worth 5 points; the 75-point map is a champion bug the swap exposed (owner question, 2026-08-25, updated 18:15Z)

Task `20260825-dance-cure-candidate-2-swap`, under your ruling of this afternoon (swap, no lock,
the swap back impossible by construction and proved — rule R-1a). Plain words; every code
explained at first use. **Nothing has touched the ladder; nothing will until you rule.** v1 of this
page (17:33Z) asked the question before the diagnoses; this v2 replaces it.

## Where it stands

The design gate passed in 21 minutes (rule and proof accepted by `codex_1`). The build is correct:
with the rule off the bot is **byte-for-byte the champion** on all 34 frozen situations and all 240
panel games. With the rule on, on the same 240 games: **dances 27 on 25 games → 13 on 12**; every
other detector unchanged; 46 exchanges on 28 games. Over 48,000 turns **no pair ever swapped back
on the next turn** — the proof held on the wire. Measured at the rule itself on all 66 exchanges of
both corpora, the mover's goal was never the partner's square (the report's one contrary-looking
line was a transcription slip, corrected).

## Update 21:40Z — the controls that do not depend on your ruling

Since v2 was written, four of the remaining controls passed with independent reproduction by
`codex_1`: the referee really executes every exchange (66 of 66); the one-turn memory the proof
reads is right on every one of 54,800 turns; the whole build is deterministic run-to-run and
build-to-build (1,096 of 1,096 game-arms); and the loop counters are not inert (deleting the
standing test sends the "consecutive swap" counter from 0 to 344). The positive control also
passed, **with a cost you should have beside the loop and `m061`:** of the 13 dances the exchange
touches on the panel, **9 end with progress** (three are exactly frozen library episodes, four
would otherwise have run to the last turn) and **4 are silenced without progress** — the bot
stops bouncing but does not get on with its work inside the window (one of the four is a loop
game: three exchanges in eight turns, no progress). Since then (22:45Z) the orchard-map checks and the safety net passed too: the orchard scoping
does real work (with it switched off, 9 of 60 orchard views break the orchard rule, each at an
exchange; with it on, 0 — at the price of dances on those maps staying untouched and +39 margin
forgone), the candidate breaks the orchard rule on **0 of 240** views, and the trolls are **less
idle** with the rule (idle-with-work 0.38 % vs 0.73 %; the worst troll 11.5 % vs 95 %; no troll
newly above the 1.5 % line, three fewer). All that remains is the reviewer's reproduction of the
whole set, then this page comes back to you with the final table — the rulings above are still
yours to make and nothing waits on the reproduction to make them.

## Finding 1 — the loop, diagnosed: the goals stay with the cells

On 4 of 240 games (and 2 of 34 situations) the pair trades places every second turn. The wire shows
why, in four turns: troll A, blocked by B who is chopping the tree at square L, swaps onto L; the
moment A stands on that tree the planner gives A *that* tree (chopping the tree under your feet
outscores walking to the next one) and hands A's old tree to B, who now stands where A stood — so
the same block re-forms the other way and the rule fires again two turns later, entirely legally.
**The goals do not travel with the trolls; they stay attached to the cells.** It happens exactly
when the landing is itself a work square (11 of 12 loop exchanges land on a live tree the partner
was chopping); the one exchange in the set that landed on a plain square had no re-pick.

**Price: 5 points on one game of 240** (the shared tree is chopped 5 times in 10 turns instead of 6
in 6); on the other three looping games the score is identical to the champion's. The loop is
loud on the wire and cheap on the scoreboard. The rule's tick budget breach (2 games) is the same
thing counted differently.

## Finding 2 — the 75-point map, diagnosed: a champion bug the swap uncovered

On both seats of `m061` the map ends with **one tree standing**, and the champion's score comes
from *not* cutting it: the blocked troll that wants that tree never gets there, the tree keeps
fruiting, and the pair runs a plant-chop-bank cycle from the shack for the second half of the game.
The exchange delivers the blocked troll to its goal — which is the last tree — and it fells it.
The map is then empty. What costs the points is what happens next, and it is **not the swap**: a
fallback in the champion's planner (`main_candidates`, the "idle regeneration" branch) returns a
bare `WAIT` when there are no trees and **throws away the replant actions it had just built** —
two `PICK`s worth 7,500. Both trolls then stand goal-less for 131 and 96 turns with a fruit in
hand. Measured at the code line with a print-only probe on both arms. `claude_1` reported this
defect unanswered on 08-21; today it has a price. No detector fires because the panel's stall gate
excuses a stall that begins after the world is exhausted — and here the arm exhausted the world
itself. Rule R-2 ("a troll with available work must be employed") is violated by the champion on
that map every turn after the last tree falls.

Two smaller facts from the same read: the rule also **displaces a troll mid-chop** (a chopper
standing on its tree counts as a "standing partner" by construction — two lost chop turns on one
seat), and the rule has no notion of whether the mover reaching its goal is good for the *team*
(it proves the exchange helps the mover).

## Your decisions

**1. The loop.** Per your rule, nobody adds a lock, a timer or a cooldown. Options:
- **A (recommended): a planner rule — "a troll keeps its goal."** Once chosen, a goal is kept until
  done or gone, or a clearly better one appears (a margin). Then A walks on to its own tree after
  the swap and B steps back onto its tree when A has passed: one exchange, both working. It is the
  simple rule in the place the defect lives, and it is what every loop game "would have done"
  (read from the wire, one sentence per game in the anatomy). One build + panel before any read.
- **B: narrow the swap rule** — do not displace a partner that is working the very square it
  stands on. That removes the loop and the mid-chop displacement, but the standing worker *is* on
  its work square in most real dances (24 of 34, 17 of 21), so it would also remove most of the
  cure. Not recommended.
- **C: proceed to the read with the loop measured** (5 points, 4 games in 240). Defensible on the
  numbers; the loop will appear in real games too, and the read costs the ladder slot.
- **D: stop Candidate 2.**

**2. The champion bug (`m061`).** Recommend chartering the one-line fix — the fallback *extends*
the candidate list instead of replacing it — as its own small candidate ("Candidate 0"), with a
panel of its own: it is a likely pure gain, it is an R-2 violation, and it removes a 75-point
artifact from every later judgement of Candidate 2. Not part of Candidate 2's code.

**3. Order.** My recommendation: Candidate 0 first (hours), then Candidate 3 = "keep your goal"
(a day), then re-run Candidate 2's panel on top of both, then ask you for the real-game read. The
remaining Candidate 2 controls (the referee check that the exchange executes, poison arm,
determinism, orchard maps, positive control, per-troll safety net) run meanwhile regardless.

## Where everything lives

`claude_1/cure2/m061-diagnosis-2026-08-25.md` and `claude_1/cure2/loop-anatomy-2026-08-25.md` (with
the clause-6 census over all 66 exchanges) at `agent/claude_1@85c6647c`; the interim report
`claude_1/cure2/g1-interim-2026-08-25.md`; the rule and proof `claude_1/cure2/definitions-g0-2026-08-25.md`;
`codex_1/reviews/dance-cure-candidate-2-swap-g0-2026-08-25.md`; my disposition
`coordination/messages/local_claude_1/20260825T173045Z-…-policy.md`; the task record
`coordination/tasks/20260825-dance-cure-candidate-2-swap.md`.
