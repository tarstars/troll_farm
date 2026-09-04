---
schema_version: 2
type: handoff
task_id: 20260904-champion-prefix-orchard
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/local_claude_1/20260904T133200Z-20260904-champion-prefix-orchard-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: abcde49244f2115a101af16c8f3da177b9d1efee
artifact_paths: ["coordination/tasks/20260904-champion-prefix-orchard.md", "coordination/tasks/20260904-orchard-kinetics.md", "coordination/BOARD.md"]
created_utc: 2026-09-04T13:32:00Z
---

- To: chatgpt_1
- CC: user, claude_1, chatgpt_2
- Task: 20260904-champion-prefix-orchard (new card)
- Kind: handoff (the charter — the owner's "run it", written up)

# CHARTER — the champion-prefix orchard experiment is yours, end to end

**The owner said "run it" at ~13:2xZ.** The card is
`coordination/tasks/20260904-champion-prefix-orchard.md` at the pin above. **The design in it is yours, unchanged** —
I wrote it up, I did not redesign it. Read the card; this message is the charter and the few things I added.

## What you own

**Everything: the experiment, the machinery, the numbers and the report.** Board row 3-8.

**Budget: one implementation round, one measurement, three days — to 2026-09-07 13:30Z.**

**Deliver to** `chatgpt_1/champion-prefix-orchard/`, then a handoff naming the pin, with the board row updated in the
same commit.

## The experiment, restated so we cannot drift

```text
A (baseline):  unchanged champion ────────────────────────────────────────► turn 300
B (candidate): unchanged champion through its own second TRAIN
               → searched near-orchard macros
               → continuously advanced shadow champion ────────────────────► turn 300
```

`NO_PLANT` always legal. **The third troll is disabled.** Same maps, seats, starts, opponent scripts and seeds on both
arms. The decision statistic is **paired final score margin** with its 95 % interval and n; **paired own score is a
mandatory guard**.

**The prefix being byte-identical through the champion's own second `TRAIN` is the point of the whole design**, not a
detail of it — it is what makes this immune to the disease that killed the last three builds. Any deviation is a dead
condition, not a tuning decision.

## Five things the card requires that were not in your recommendation

None of them change the experiment; they are the standing rules that came out of the instrument audit.

1. **Publish your action vocabulary** — every action the search could take, listed in the artifact. This is now
   standing for every optimizer, because the owner's own observation turned out to be exactly right: neither previous
   optimizer had `PLANT` in its action space at all, so neither could ever enlarge the resource base it was dividing.
2. **Mechanics before value, on both arms independently.** No value number is read from either arm until both run
   clean, the prefix is verified identical, all 300 turns are answered and any long-inactivity alarm is explained.
3. **Δwin is retired as a kill criterion everywhere.** Δmargin with its interval is the selector. And **no rating
   number may be derived from a margin by a slope** — the relation is flat then falling, not linear (the champion's
   own point is (0,0); orchard 6 (−18.74, ≈0); stage 2A (−28.71, −4.13)); my earlier "0.5 rating per margin unit" is
   withdrawn.
4. **No fresh sealed holdout yet, and no panel.** The 24-map smoke and the pinned 200-map panel are development data —
   every build since August has been shaped against them. Generalisation is tested after a positive mechanism, not
   during it.
5. **Never model the opponent as idle.** That assumption is what made stage 2A promise turn 70 and deliver 74.5 into a
   stripped forest.

## What you are given so you do not re-derive it — §4 of the card

The verified mechanics (a mature tree is **16 points**, not 4; banana 6 health against apple 20 for the same 4 wood,
and banana priced at **zero** for the training bill → plant bananas for wood, keep plums, lemons and apples for the
bill); claude_1's 400-map-seat planting geometry (**11.5** free cells within two steps of the shack, **27** within
four, of which only **2** and **5** are water-adjacent; starting fruit draw **24**) — so **the fast orchard is small
and the big orchard is slow**, and a thirty-tree orchard is not reachable near the tent; and the raid rates (0.19 per
100 tree-turns before turn 100, **0.6–1.0 after**).

## The two decisions I made around your card

- **claude_1's orchard-kinetics read is closed as superseded into yours**, its geometry kept as an input. One
  measurement, not two half-measurements.
- **claude_1 will independently reproduce your experiment when it lands** — from the card and the referee, without
  reading your implementation. That is not a review of you; it is the same protocol that made the stage-2A field
  reading trustworthy when two agents agreed to the digit.

## Your own falsification list is the card's dead conditions, verbatim, and I hold it

The optimizer-off path differing from the champion; the second troll changing in talent or turn; the paired
final-margin lower 95 % bound not above zero; paired own-score lower bound negative; the no-plant champion normally
selected; the gain vanishing under high raid; wood overstatement above 1.5×. **Plus your own soft stop:** below about
**+15** mean paired margin the result is a measured component and does not buy a ladder slot.

**No ladder, no submission, no platform, no Arena, no cluster on this card.** A slot needs a fresh decision and the
owner's prediction asked in chat first.

Your prior is recorded on the card before the result: **about +2.5 rating, range 0 to +4, explicitly uncalibrated**;
10–25 points of local margin on maps where the near reserve is used.

— the coordinator
