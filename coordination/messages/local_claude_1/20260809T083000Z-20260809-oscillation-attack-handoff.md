---
schema_version: 2
type: handoff
task_id: 20260809-oscillation-attack
from: local_claude_1
to: ["claude_1", "chatgpt_1"]
cc: ["user", "local_codex_1"]
message_id: coordination/messages/local_claude_1/20260809T083000Z-20260809-oscillation-attack-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 1c65c9fc4cc242e4e8ce9abca325bc38cd83abc5
artifact_paths: ["local_claude_1/oscillation-attack-local_claude_1-2026-08-09.md"]
created_utc: 2026-08-09T08:30:00Z
---

# handoff: my oscillation answer — published without reading yours

`local_claude_1/oscillation-attack-local_claude_1-2026-08-09.md`. I did not read either of your
answers before writing it, as the task requires.

## Three things you can attack

**1. I think the fix will not help, and I want that challenged.** Terminal-oscillation games
average **+1.58** margin against **+16.74** for clean games, and the gap survives map-class
control at **−13.6**. But D176a is a real intervention study and measured the causal value of
fixing oscillation at **+0.045, CI [−0.024, +0.114]**. When an intervention says +0.045 and
correlation says −13.6, the intervention is right and the correlation is confounded. My reading:
**oscillation is a marker of a cramped, contended position, not the cause of losing it** — the
narrowness that makes two units contend for one tree is the same narrowness that makes the game
hard, and removing the pacing does not widen the corridor. Note the gap is **−24.7 on
choke_corridor and −0.2 on open_field**, which is what that hypothesis predicts.

If I am wrong here, my two preferred actions are wrong with me.

**2. I believe the task record's own suggestion fails.** It offered porting the Gold-era
anti-stall watchdog from `rust/src/botmain/motion.rs`. Having read it: it tracks a
**same-position streak** (`troll id -> (x, y, same-pos streak)`, "sidestep after 2 stuck turns").
**An oscillating unit is never in the same position twice running**, so that predicate cannot
fire on this defect. I wrote that suggestion into the task myself and now think it is wrong.

**3. Two facts I verified on this candidate, which make a memory fix cheap.** `YamoBot` already
carries per-unit state across turns (`regeneration_commitments: BTreeMap<i32, PlantKind>`) while
`grep` for `last_pos|prev_cell|history|streak` returns **0** — the bot is not stateless, only the
resolver is. And **all 34 episodes are 2-cycles between orthogonally adjacent cells**, 34/34, so
a no-immediate-backtrack rule breaks every one of them by construction.

## What I recommend, briefly

Repair the **gate's reference build**, not the shipped bot — the two-sided acceptance test needs
a repaired reference, and that reference need not be what we submit. Put the no-backtrack rule
inside it. Hours of work, no owner decision, nothing risked on the ladder, and it either
satisfies the gate or falsifies the fix cheaply.

In parallel I have asked the owner to rule on whether **"no terminal oscillation" should replace
"raw D-1 = 0"** as the gate condition, since SHORT episodes are 0/15 terminal and a perfect fix
buys +0.045. If that is acceptable, most of this work is unnecessary.

What I would *not* do: rewrite the resolver as joint assignment while the gate is unready; adopt
the Elost rule without the owner, given the 11.96-at-rank-111 precedent for its family.

## Reminder on scope

The standing closure is **not** overturned: nobody should argue this raises our score. The
justification is instrument compliance. An answer of "change what we require, not what the bot
does" is legitimate and I have made one myself.

Publish your own answer before reading mine if you have not already. I will merge all three with
disagreements preserved rather than averaged.
