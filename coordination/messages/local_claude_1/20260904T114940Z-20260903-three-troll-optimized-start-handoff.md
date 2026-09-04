---
schema_version: 2
type: handoff
task_id: 20260903-three-troll-optimized-start
from: local_claude_1
to: ["chatgpt_2"]
cc: ["user", "chatgpt_1", "claude_1"]
message_id: coordination/messages/local_claude_1/20260904T114940Z-20260903-three-troll-optimized-start-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 81fe9c2f11cf445d860540f56f38f67bca7f100d
artifact_paths: ["coordination/GRAVEYARD.md", "coordination/tasks/20260904-instrument-audit.md", "coordination/tasks/20260904-orchard-kinetics.md", "chatgpt_2/three-troll-optimized-start/RESULTS.md"]
created_utc: 2026-09-04T11:49:40Z
---

- To: chatgpt_2
- CC: user, chatgpt_1, claude_1
- Task: 20260903-three-troll-optimized-start
- Requires acknowledgement: yes. **A judgement round, not a build.** No code, no bot, no ladder, no platform.

# HANDOFF — the owner asks you directly: how would you improve your bot?

**The owner's words: "ask chatgpt_2 how would it improve its bot."** You have the run results already (my 07:51Z
message) and the data to check them. This asks for your judgement, in your own order, not a wish list.

## What your bot did, so we are working from the same facts

Ladder **14.07 at rank 154 of 177** against the champion's **18.72 at rank 72**. The decode of its 160 games: a third
troll in **47 %** of them at **median game turn 25** — about 71 turns before the field bought its own, and the earliest
roster any build here has achieved — and **19 points a game less than the champion** (165.5 against 184.5). The
matchmaking confound runs *against* you: at rank 154 your bot met a weaker field (opponents' mean 172.3 against the
champion's opponents' 210.1) and still scored fewer points, so the gap is understated. Its card is dead on mechanics
(19/24 and 15/24 against a 24/24 bar, five and nine maps stalled).

## The question, and the three parts I would most like answered

1. **How would you improve it?** Ranked, with an expected size in points or rating for each, and — for each — **what
   measurement would show you were wrong.** A proposal that cannot be falsified is not usable here.
2. **Why did your candidate stall on five maps and your control on nine?** *Nobody has diagnosed this*, and you are
   the only one who knows the internals. It is the single largest unexplained thing about your build: a bot that stops
   moving loses those games outright, and it killed the card before any value number could be trusted. If the cause is
   in your funding pathway rather than in the optimizer, say so.
3. **What would you keep?** Your build got the roster faster than anything this project has made, your control arm was
   built without anyone asking, and your `DEAD_AS_BOT` verdict matched my independent reproduction in every figure.
   Some of that machinery is probably worth more than the bot was — say which parts.

## What is already closed, so you do not spend the round on it

- **The roster on the present forest is closed four ways** and must not be re-proposed: the honest forecast declined
  all 4,593 evaluated turns; the fruit valuation flips only 7.8 % of admissions; and a loosened-forest gate that
  declines 4,024 turns of 4,219 **still loses all three games it admits**, with a nearly calibrated forecast
  (with-troll 20–53 against without 17–41). The trade is bad at the very margin where it looks closest.
- **`PLANT` being absent from your action space is understood** and is being addressed — chatgpt_1 is building a
  start-game optimizer with `PLANT` searched, on the owner's word. **Do not duplicate that build.** If your answer
  bears on it, say what it should change rather than proposing a parallel one.
- **The measurement rules have moved**: Δwin is retired as a kill criterion and Δmargin with its interval is the
  selector; the ladder's noise floor is **2.2** (five readings of the champion's identical file span 17.04 to 19.23),
  so nothing smaller than that can be settled by a ladder hour; and the 24-map smoke and 200-map panel are development
  data now, not holdouts.

## Facts you may not have

Verified in `sim/engine.py` since your build: a mature size-4 tree is **16 points**, not 4; health at maturity is
**banana 6, plum and lemon 12, apple 20** for the same 4 wood, so a chop-1 troll fells a banana in 6 turns against an
apple's 20 and bananas cost **nothing** toward training. And claude_1's map geometry over 400 map-seats: **11.5 free
planting cells within two steps of the shack, 27 within four, of which only 2 and 5 are water-adjacent** — so a
thirty-tree orchard needs four-step planting, and the fast water-side orchard is small.

Answer in plain words; the owner reads these directly. One round.

— local_claude_1, coordinator
