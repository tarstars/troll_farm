---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260816T155300Z-20260816-h-starve-1-increment2-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: f44fecf6a5cee4da6e9ba7c9590f75263b6bee5e
artifact_paths: ["claude_1/hstarve1/audit.py", "claude_1/hstarve1/cause-table-2026-08-16.json"]
created_utc: 2026-08-16T15:53:00Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: H-STARVE-1 increment 2 — the cause is a GENERATOR GAP, not a stuck commitment. 3 of 3.

## For the owner, in plain terms

We now know why the parked troll stands still, and **it is not what any of us expected.**

The troll is not sent to the wrong planner. It goes to the normal planner, every single turn, with
no leftover commitment. The planner hands it a list of options — and **every option is "wait"**,
on every one of ~190 turns.

And the map was not empty. I checked the world separately, using the same test the gate uses:
**there was work available on 100% of those turns.** So the bot was standing a troll still, for
the whole game, while there was something to do.

That is a bigger and more fixable finding than the one we went looking for.

## The measurement

Artifact `f44fecf6`, pushed and remote-verified.

| situation | branch taken | commit mid-game | every candidate WAIT | **world offered work** | cause |
|---|---|---|---|---|---|
| OSC-001 | `MAIN` ×195 | 0 | 195 / 195 | **195 / 195** | **GENERATOR_GAP** |
| OSC-012 | `MAIN` ×193 | 0 | 193 / 193 | **193 / 193** | **GENERATOR_GAP** |
| OSC-031 | `MAIN` ×190 | 0 | 190 / 190 | **190 / 190** | **GENERATOR_GAP** |

Increment 1 refused to label this, because *"all candidates are WAIT"* is the generator's output
and calling it `NO_WORK_ON_MAP` would have assumed the conclusion. Increment 2 asks the **world**
instead, using the panel's own `fuzz_panel.work_remaining(tr, t)` (`:1756`) — reused rather than
re-derived, so "there is work" cannot mean one thing to the gate and another here.

**The owner's suspected mechanism does not occur on any of the three.** No stuck regeneration
commitment, no endgame routing mid-game. The static hazard I confirmed at `:1396-1398` is real but
is not what is biting.

## The imprecision I am not going to gloss

`work_remaining` is a **player-level** predicate: its reachability BFS is multi-source over **all**
own units (`fuzz_panel:1774`). So a plant reachable only by the **dancer** still counts as "work
remains".

**Therefore `GENERATOR_GAP` here means:** *the world offered the player a resource action while
this unit was handed only WAIT.* It does **not** yet mean *this unit had reachable work of its
own*. A per-unit BFS from the parked unit's cell is the next increment and **could move rows to
`NO_WORK_ON_MAP`** — for instance if the parked troll is walled off behind the dancer in a
corridor, which is exactly the geometry several of these situations have.

I am stating this before anyone quotes "GENERATOR_GAP 3/3" as settled. The direction is strong;
the per-unit refinement is what would make it airtight.

## Why this matters for T-1

**T-1 cannot fix these.** Swap, yield and visibility are about a troll that wants to go somewhere
and is blocked. A troll being handed nothing but WAIT has nowhere it is trying to go — there is
no move to swap and no reason to yield. That is consistent with stage 2's measured result
(0 FIXED / 34) and it predicts stages 3–4 will not move these rows either.

If that holds, the prediction registry's 25 may be optimistic for a reason unrelated to transport
quality — the parked troll would need a generator fix, which is **out of T-1's charter and has no
owner gate**. Worth knowing before the nightly measurement is scheduled rather than after.

## For `codex_1`

Increment 1's two named limits stand and I have not closed them: the non-interference check still
runs on the **first** situation only, and `classify()` still reads only window turns. Added in
this increment: the player-vs-unit scope of `work_remaining` above — the place I would attack
first, because it is the one that could flip the headline label.

## Boundaries

Resident byte-exact `98628e98…`. Packet-lite SLICE, never packet completeness. **No cure code** —
if the cause table warrants a generator fix it gets its own charter and owner gate, per your
ruling. Three specimens, not the ~24; I am reporting early because it changes what the next
increment should be.
