---
schema_version: 2
type: handoff
task_id: 20260907-two-project-analysis-and-plan
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "chatgpt_2", "claude_1", "codex_1"]
message_id: coordination/messages/local_claude_1/20260907T072337Z-20260907-two-project-analysis-and-plan-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: c25e3e8198a985eec02602581e60d6e7d093b92d
artifact_paths: ["coordination/tasks/20260907-two-project-analysis-and-plan.md", "coordination/BOARD.md", "neighbour/separate_troll_farm/SNAPSHOT-README.md"]
created_utc: 2026-09-07T07:23:37Z
---

- To: chatgpt_1
- CC: user, chatgpt_2, claude_1, codex_1
- Task: 20260907-two-project-analysis-and-plan (new card, board row A-1)
- Kind: handoff (the charter)
- Requires acknowledgement: yes

# CHARTER — one analysis of BOTH Troll Farm projects, and the plan for what to build next

**Two days, to 2026-09-09 08:00Z. A read and a plan. No bot, no build, no panel, no ladder, no platform.** The card is
at the pin above; read it whole before starting — it carries the questions, the inputs on both sides, and the
coordinator's own reading as claims for you to check.

## What changed this morning

The owner has a **second** Troll Farm project, `separate_troll_farm`, on the VM (primary agent "Astra", Claude as its
implementer, goal rank 7 or better, publication allowed). **It shares our CodinGame account.** Its bot V439 has held
the ladder since **2026-09-05 08:01Z at rank 28 / 23.43** (23.35 today), having replaced our champion of record
(19.23 / rank 60). Its lineage has read **21–25 (mean 23.1) across 23 mature readings** where ours reads 17–19. Neither
project had read the other's record until today.

You cannot reach the VM, so its 115 documents and its main source files are now in this repository, read-only, at
**`neighbour/separate_troll_farm/`** — start with `SNAPSHOT-README.md` there.

## The owner's words, which are the task

> *"give a task for chatgpt_1 to perform the similar analysis of troll_farm and separate_troll_farm and give a detailed
> plan for the further project development."*

"The similar analysis" is the review the coordinator did this morning: the state of each project, what each has
proven and killed, where their instruments agree with the ladder and where they do not, and what the most promising
next move is. Its conclusions are on the card (§2) so you can disagree with them with numbers. In one line: three
independent reads — ours of 08-26 and 09-06, theirs of 09-02 and 09-04 — name the same missing architecture (the
renewable own-crop lifecycle next to the shack, run by two workers), every graft of it onto the old job planner failed
in both projects, and nobody has built it as its own controller.

## The six deliverable questions (the card §3 has the detail and the file paths)

1. **One scoreboard** of every mature ladder reading of both lineages since 08-20, with each side's own noise figure.
2. **Both graveyards side by side**, clustered by mechanism: what the union of the evidence establishes, what it does
   not, and whose evidence is stronger.
3. **The gap in one statement**, with the numbers beside it, and the second-troll question settled or named unsettled
   (our census says the two-troll leaders buy 2/2/0/2; their read says putibuzu's commonest second worker is 2/2/2/2).
4. **The one evaluation pipeline** for the family — their paired unranked games against the real ranked agents, our
   sealed holdout and reproduction rule — with the resolution each stage buys and its cost.
5. **The ranked design decision** among the six directions on the card, chosen by the record, each with size, cost,
   dead condition and what would make it wrong.
6. **The plan**: phases with done / dead / budget, the division of labour between the two projects (one account, one
   queue?), a calendar, the owner's decisions in one word each, and the recorded traps built in.

## Done means

`chatgpt_1/two-project-plan/ANALYSIS-<date>.md`, `PLAN-<date>.md`, and **`OWNER-PAGE.md` — one page in plain words** with
every code explained at first use; any script you used, with its command line; a handoff pinning the commit. I then
reproduce every recomputable number by execution before it reaches the owner.

## Rules that bind this card

- **Every number cites the file it came from.** No rating claim from a single ladder reading; no margin-to-rating
  slope; no judging a bot by per-decision agreement with a stronger bot.
- **Treat every conclusion in both records as a claim to check** — including mine. Our coordinator's diagnosis of the
  port was wrong and its repair could not have worked; the neighbour's own review found its selector did not express
  its goal.
- If the snapshot lacks something you need, **say exactly which in a progress message and continue** — I fetch it
  from the VM. If two load-bearing facts contradict and the files cannot settle it, say so and name the one cheapest
  measurement that would; do not pick a side.
- No writes outside `chatgpt_1/`; `neighbour/` is evidence, never edited.
- **Heartbeat, both ways** (`WORKING-RULES.md` §8): I send you an ack-required note once a day while the card is live;
  you send a progress message each working session, even if it only says where you are.

## Why you

You wrote the instrument findings that changed how this project measures (the 2.2 is one reading, not a wall; the
sealed holdout; the paired-margin gate), the judgement that turned a failed optimizer into a clean experiment, and the
orchard experiment that closed honestly on its own dead condition. This card is that same judgement applied to two
records at once, and it ends in a plan the owner will act on.

**The owner activates you; this message is the assignment.** — the coordinator
