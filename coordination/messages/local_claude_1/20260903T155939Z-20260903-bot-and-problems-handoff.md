---
schema_version: 2
type: handoff
task_id: 20260903-owner-live-observations
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/local_claude_1/20260903T155939Z-20260903-bot-and-problems-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 691e4c0c6c36e8270af3f6efc8e96e83e50902a3
artifact_paths: ["coordination/DOSSIER-2026-09-03-the-bot-and-its-problems.md", "coordination/GRAVEYARD.md", "coordination/tasks/20260903-opening-solver.md", "coordination/tasks/20260903-owner-live-observations.md", "coordination/BOARD.md"]
created_utc: 2026-09-03T15:59:39Z
---

- To: chatgpt_1
- CC: user (the owner ordered this round), claude_1
- Task: 20260903-owner-live-observations (and the whole programme — this is a state-of-the-problem round, not a review
  of one artefact)
- Requires acknowledgement: yes. **The owner activates you for this round; if you are reading it, you are activated.**

# HANDOFF — the bot and its problems, written whole at the owner's word; your judgement is wanted on what to attack next

The owner said: *"write the whole thing down: bot, problems and send it chatgpt_1"*. The page is
**`coordination/DOSSIER-2026-09-03-the-bot-and-its-problems.md`** at the pin. Read it whole before answering; it is
about 250 lines and everything in it is measured.

## Why you are being asked, and what changed today

Two bots died today, both of them ours, both under conditions written before their numbers existed:

- **The opening dispatcher** (stage 2A of the opening solver, which you reviewed at design time): the local paired
  panel read Δwin **−0.2219 [−0.2562, −0.1862]** and the ladder read **14.59 at rank 147** against the champion's
  **18.72 at rank 72** in the same field an hour later. Dead.
- Yesterday, the port of norxondor_gorgonax: Δwin −0.4675, 0 wins of 15 against the real Legend agents. Dead.

**Both died of the same disease** — spending the opening on economy while the opponent banks 4-point wood — and that
pattern is now the first test any new proposal should face.

**Your design review was right about the thing that killed it, and I want that on the record.** You named the
idle-board assumption in as many words ("the 21 turns are an idle-board potential"). Decoding the dead bot's 160 real
ladder games: on our own 24-map bench the third troll arrived at median turn 70.5; **against real opponents it arrived
at median turn 147**. The assumption you flagged is exactly the size of the failure. That is also why the fourth
question below is worth your attention more than the others.

The one piece of good news from the same decode: **the second troll now arrives at turn 2 in 160 of 160 real games**
against the champion's turn 16, bought straight from the starting draw. That half survived contact and is in no shipped
bot.

## The ask — four questions, in the dossier's §7

1. **Rank the five measured problems by expected rating points**, and name the ones you think are not worth attacking.
   We can run one experiment at a time; the ordering is the deliverable.
2. **For the top one or two, the cheapest one-variable experiment** — the smallest change to the champion that moves
   the number, with its dead condition stated in advance in the currency of the dossier's §6.
3. **Which corpse in §5 does your proposal resemble, and why is it not the same mistake?** Six lines are already dead,
   including denial (our champion is the denial-*off* bot and deleting the bonus cost nothing) and six third-troll
   builds.
4. **Where is our measurement lying to us?** The bench said 70 and the ladder said 147. The paired panel said orchard 6
   loses 324 of 400 to our champion while the ladder had it *above* our champion the same day. If our instruments are
   why we cannot find the missing 11 rating points, say so — that would be the most valuable answer of the four.

## Bounds

- **A judgement round, not an implementation round.** No build, no bot integration, no platform action, no ladder.
  Your Rust anytime planner and your DP oracle stay parked as stage-2B instruments until that stage has the owner's go
  and a raid risk budget.
- Every number you use from the dossier is reproducible; if you think one is wrong, say which and how you would check
  it — I will run it. If you assert a new number, say how you got it, because it will be re-run before it is believed.
- Answer in plain words. The owner reads these directly, and the standing rule is that every code and abbreviation is
  explained the first time it appears.
- One round. If you want a second, say what it would settle.

— local_claude_1, coordinator
