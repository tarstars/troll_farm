---
schema_version: 2
type: handoff
task_id: 20260905-port-postmortem
from: local_claude_1
to: ["chatgpt_2"]
cc: ["user", "codex_1", "claude_1", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260905T060000Z-20260905-port-postmortem-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 93b842683e365c93fcfb505260bcea100f2be2a5
artifact_paths: ["coordination/tasks/20260905-port-postmortem.md", "coordination/BOARD.md", "coordination/tasks/20260902-norxondor-port.md"]
created_utc: 2026-09-05T06:00:00Z
---

- To: chatgpt_2
- CC: user, codex_1, claude_1, chatgpt_1
- Task: 20260905-port-postmortem (new card, board row P-2)
- Kind: handoff (the charter)

# CHARTER — the biggest unexplained number we have, and it is yours

**Two days, to 2026-09-07 06:00Z. A read. No bot, no build, no ladder, no platform.** Card at the pin above.

This is not a routine card. The owner stepped back yesterday and asked what we are doing; I gave the honest
scoreboard — **nine days, twelve ladder readings, not one change shown to improve the bot, fifteen lines in the
graveyard** — and put four strategic options up. **The owner chose this one.** It is the project's main bet for the
next two days.

## The contradiction

**We implemented the design of the #2-ranked player, rated 29.66, and it lost 8–0 to our own 19-point champion.**
Rung 1: Δwin −0.421 [−0.453, −0.389], Δmargin −71.1 over 1,600 local games. Rung 2: 8–0 over 15 paired games on the
same seeds against five real Legend agents. Then one parameter repair read *worse*, and we closed the line.

**We closed it on "our build read worse", which is a fact about our build, not about the design.** Three things can be
true and they have completely different consequences for the project:

1. the design is not worth 29.66 in our hands → **copying top players is a dead strategy and we stop**;
2. our reconstruction of it is wrong → **Track R's four documents are worth much less than we treat them**, and every
   idea drawn from them is suspect;
3. the port broke it identifiably → **there is a ~10-point design sitting in our repo that we mis-built**, and that is
   the entire gap.

**Say which. That is the deliverable.**

## The lead, which is in our own reconstruction's own words

`local_claude_1/reconstructions/README.md` lists under **"Not solid"**: *"the target-selection rules (**chop**; the
plant kind) of all four; norxondor's tie-breaks…"*

**The chop targeting was never recovered.** So the port ran **norxondor's economy on our champion's chop targeting** —
and it lost **precisely in the wood race** (banking 1-point fruit while the champion banks 4-point wood, joining the
wood race ~100 turns late). That is either the answer or a coincidence, and it should not be left unexamined.

Two more facts from our own history, both of which cut against the original diagnosis:

- **Per-decision accuracy does not survive the closed loop.** The one previous norxondor-shaped controller built from
  fitted rules lost **−173 points closed-loop while matching 77 % of its recorded decisions.**
- **Two correct doors make a wall** — this project's own name for two individually correct components that fail in
  combination. A graft of their economy onto our targeting is exactly that shape, and the hybrid was chosen
  deliberately *because* a straight port had failed before.

## ★ The decisive question needs no implementation at all

**Measure the real norxondor against our real champion, from recorded games.** We hold **218 corpus games of the
actual #2 bot** (agent `6480540`, `local_claude_1/reconstructions/profiles/`) and 160-game packages of our champion
(`local_claude_1/ladder-queue/games-*/`), both validated against the referee's own tallies.

Compare **score trajectories, wood-versus-fruit banking over time, roster timing, and final margins** against
comparable opposition. **This answers "is the design worth ~10 points over ours" from what both bots really did, with
no implementation in the way.**

**The confound that has bitten this project twice: opponent strength differs between packages.** Report opponents'
mean rating for every cut, and never compare raw scores across packages without it. It ran *against* the three-troll
bot and understated its loss; it can just as easily run the other way here.

And the trap that is specific to this question: **question 2 on the card.** The loss read says the port banks fruit
while the champion banks wood. **Does the real norxondor do that too?** If it does, and still rates 29.66, then our
original diagnosis named a symptom and the repair was aimed at the wrong thing entirely.

## Dead means something the project needs either way

**If the real norxondor's recorded games show no large, mechanically identifiable advantage over our champion against
comparable opposition, say so with the number and stop.** Then the 29.66 is not ten transferable points, the port
stays closed, and **we stop mining the top four for ideas** — a strategy we have spent weeks on. That is a real and
valuable outcome, not a failure, and it would redirect the project more than a positive answer would.

## Why you

Twice in two days you have taken two of our own numbers that disagreed and shown what each was actually measuring —
the stall subset that overturned three post-mortems, and the `705/734` versus `83.7 %` reconciliation. **This is the
same instrument at larger scale.** And you wrote neither the reconstruction (mine) nor the port (codex_1's), which is
the qualification for auditing both.

**codex_1 built the port and is available to answer questions about it.** It does not own this read and does not
review it.

— the coordinator
