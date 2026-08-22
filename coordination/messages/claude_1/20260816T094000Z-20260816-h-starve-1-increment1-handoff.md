---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260816T094000Z-20260816-h-starve-1-increment1-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 4fc5439dbe496b2066767d45006c487e77c5e037
artifact_paths: ["claude_1/hstarve1/make_instrumented.py", "claude_1/hstarve1/audit.py", "claude_1/hstarve1/instrumented-hstarve1.rs", "claude_1/hstarve1/cause-table-2026-08-16.json"]
created_utc: 2026-08-16T09:40:00Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: H-STARVE-1 increment 1 — the suspected mechanism does NOT occur on the two specimens measured

## For the owner, in plain terms

Your hypothesis was that the parked troll is starved because a leftover "regrow this fruit"
commitment sends it to the wrong planner for the rest of the game. **On the two situations I have
measured so far, that is not what happens.** The parked troll goes through the *normal* planner,
every turn, with no leftover commitment at all — and the normal planner hands it a list of options
in which **every option is "wait"**.

So the troll is not starved by being sent to the wrong place. It is being asked, correctly, and
the answer keeps coming back "nothing to do". Whether that answer is *true* is the next question,
and I deliberately have not answered it — see below.

## What was measured

Artifact `4fc5439d`, pushed and remote-verified. Instrumented build (diagnostics only) plus an
audit runner that captures its stderr.

**The routing is as you described, statically.** `committed_regeneration` is the **first** arm at
`:1396-1398` and is **not** conjoined with `endgame`, so a unit holding a regeneration commitment
would get the endgame generator at any turn. That much is real. But *visible* is not *witnessed*,
which is the whole reason for an instrument.

**Witnessed, for the parked (non-dancer) unit across the full window:**

| situation | branch taken | committed mid-game | empty candidate lists | every candidate WAIT |
|---|---|---|---|---|
| OSC-001 | `MAIN` on **195 / 195** turns | **0** | **0** | 195 / 195 |
| OSC-012 | `MAIN` on **193 / 193** turns | **0** | **0** | 193 / 193 |

`main_candidates` is entered and returns a **non-empty** list — in which every candidate is a
`WAIT`. The endgame generator is never reached; there is no stuck commitment to be stuck on.

## The label I refused to write

My first classifier called this `NO_WORK_ON_MAP`. **That assumed the conclusion.** "All candidates
are WAIT" is the *generator's output*, not a fact about the world — a generator that fails to see
available work emits the identical signal to one correctly reporting an empty map. Labelling it
`NO_WORK_ON_MAP` would have handed you a finding that the instrument cannot support, and it is
exactly the distinction the audit exists to make (`NO_WORK_ON_MAP` vs `GENERATOR_GAP`).

Relabelled **`ALL_WAIT_CAUSE_UNDETERMINED`**. Separating the two needs the world-state predicate
`fuzz_panel.work_remaining(tr, t)` (`:1756`) — which already exists and which this slice does not
yet read. **That is increment 2** and it is the increment that answers your actual question.

## Non-interference — verified, not assumed

The instrumented and uninstrumented builds produce **byte-identical command streams** on OSC-001.
The runner checks this before emitting any table and voids the table if they ever differ. Without
that, the diagnostics would describe a different bot than the one being audited.

## Scope, stated plainly

- **Two specimens, not the ~24.** I am reporting an early contrary result rather than sitting on
  it until the full set is done, because it points the next increment somewhere different from
  where the charter points. The other specimens may still show the commitment mechanism; two are
  not a population and I am not generalising from them.
- **Packet-lite SLICE, never packet completeness** — routing branch and candidate count for one
  unit per turn, not the §4–§17 contract.
- **No cure code**, per your ruling.

## For `codex_1`

Review the instrument before the table is trusted, per the charter. The two places I would attack
first: (1) the non-interference check runs on the **first** situation only, so a build that
diverges only on a later map would pass it; (2) `classify()` reads only the window turns, so a
commitment acquired before `turn_start` and still held is counted as "committed" but its
*acquisition* is outside the observed range.

Both are real limits of increment 1 and I would rather name them than have them found.

## Boundaries

Resident byte-exact `98628e98…`. No resident mutation, no Arena action, no cure code. T-1 stage 2
numbers are from the other track and are not mixed into this table.
