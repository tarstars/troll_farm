---
schema_version: 2
type: handoff
task_id: 20260904-start-game-optimizer-design
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/local_claude_1/20260904T072434Z-20260904-start-game-optimizer-design-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: e1bd662eecf2c0078674ecafd483b3c35a0e8276
artifact_paths: ["coordination/tasks/20260904-start-game-optimizer-design.md", "coordination/tasks/20260904-orchard-kinetics.md", "coordination/tasks/20260904-instrument-audit.md", "coordination/GRAVEYARD.md"]
created_utc: 2026-09-04T07:24:34Z
---

- To: chatgpt_1
- CC: user, claude_1, chatgpt_2
- Task: 20260904-start-game-optimizer-design
- Requires acknowledgement: yes. **The owner has asked you directly for this.** Acknowledge with your start time and an
  estimate.

# HANDOFF — design a proper start-game optimizer; the owner asked for it by name, minutes after your judgement round

**The owner's word: "ask it to design proper start-game optimizer."** The card is
`coordination/tasks/20260904-start-game-optimizer-design.md` at this pin. **One design round. No build, no bot
integration, no ladder, no platform, no cluster.** A build, if any, is a separate card on the owner's word.

## Why you, and why now

The owner watched the three-troll bot play on the ladder and named the defect in a sentence: *"optimization doesn't
include planting trees, because of it trolls are weak and wood gain is small."* I verified it in source and it is true
of **both** optimizers this project has built — chatgpt_2's reads `view.plants` seventeen times as harvest sources and
never issues a plant command; claude_1's wood-charging forecast values the third troll entirely out of the **existing**
forest. Both searched a roster against a fixed, depleting resource base. **You generalised exactly this in your own
judgement round** — *every optimizer must publish its action vocabulary; an optimum without `PLANT` cannot answer the
owner's question* — and it is now a standing ruling. The owner has handed you the problem your own ruling defines.

You also own the instruments: the DP/A* oracle with dominance pruning and an optimality certificate, and the Rust
anytime planner with an always-valid incumbent, admissible bounds, budgets and a beam fallback. Both are verified —
I reproduced the planner's tests myself, 7 of 7.

## The eight questions the card asks, and the two that matter most

All eight are on the card. Two of them are where the last seven lines died, so treat them as the spine:

**The objective must not be the one we used before.** Stage 1's solver maximised *the turn the third troll arrives*.
That objective is now measured and it is wrong: stage 2A reached three trolls about **23 game turns ahead of the field**
and still read **4.13 rating points below the champion**. Name what this optimizer maximises — my expectation is
expected own score at turn 300 under a stated continuation policy, in points — and say how it is computed.

**The forest is finite and contested, and the opponent is not idle.** claude_1 measured the exact failure mode: a
forecast that values wood as *rate × turns remaining* over-states it about **tenfold**, because by turn 108 four trolls
have been felling the map for a hundred turns. And the idle-board assumption is what made stage 2A promise turn 70 and
deliver 74.5 into a stripped forest — a caveat you yourself named at design time and were right about. Use the measured
raid process: near trees taken at **0.19 per 100 tree-turns before turn 100**, **0.6–1.0 after**; the opponent plants
about **25.8 trees a game** and takes **23.5 fruit** from them.

The others: the full published action space with `PLANT` searched; how planting changes the convertible-wood bound over
time; where the optimizer hands back to the champion and on what evidence; the compute budget **measured, not
projected** (1,000 ms turn 1, 50 ms after, one core — your planner already benchmarks 378 ms and 84 MiB on its larger
case); the gates a build would have to pass, **including a fresh holdout panel**, per your own adopted finding that our
24-map smoke and 200-map panel are development data now; and **your own falsification** — what result would show the
design is wrong. Seven roster lines have died here; a design that cannot be killed by a measurement is not a design.

## Do not duplicate the live read — compose with it

claude_1 is running `20260904-orchard-kinetics` (the owner's own idea, due 2026-09-05 18:00Z): how much wood an orchard
delivers and when, whether a third troll pays when it arrives into one, and the value of a planting turn against a
chopping turn. **Do not re-derive that.** State plainly what you need from it, so the read supplies the wood-versus-time
curve and your design supplies the search that exploits it.

## One fact from this hour, so your design starts from the truth

The bot the owner submitted read **14.07 at rank 154 of 177** at 07:22Z, against the champion's **18.72 at rank 72**;
the champion is already back on the ladder. That is the bot whose optimizer had no `PLANT`. It is the measurement your
design is answering.

Budget to **2026-09-06 08:00Z**. Progress message with each commit.

— local_claude_1, coordinator
