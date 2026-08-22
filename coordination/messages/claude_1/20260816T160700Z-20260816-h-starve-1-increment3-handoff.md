---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260816T160700Z-20260816-h-starve-1-increment3-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: f5a9d2e90944789845f4827c7f7827d568a48f12
artifact_paths: ["claude_1/hstarve1/audit.py", "claude_1/hstarve1/cause-table-2026-08-16.json"]
created_utc: 2026-08-16T16:07:00Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: H-STARVE-1 increment 3 — I built the check that could refute my own finding. It confirmed it.

## For the owner, in plain terms

Last message I told you the parked troll is being handed "wait" every turn while there was work
available — and I flagged one way that conclusion could still be wrong: my test asked whether the
*team* had work, not whether *that particular troll* could get to any of it. If the only reachable
tree was on the dancer's side of a corridor, my finding would have collapsed.

I built that stricter test and ran it. **The finding holds.** The parked troll could reach work
itself, on every single turn, and was still told to wait every single turn.

## The measurement

Artifact `f5a9d2e9`, pushed and remote-verified.

| situation | every candidate WAIT | player had work | **this unit could reach work** | cause |
|---|---|---|---|---|
| OSC-001 | 195 / 195 | 195 / 195 | **195 / 195** | GENERATOR_GAP |
| OSC-012 | 193 / 193 | 193 / 193 | **193 / 193** | GENERATOR_GAP |
| OSC-031 | 190 / 190 | 190 / 190 | **190 / 190** | GENERATOR_GAP |

`unit_offered_work()` uses the **same two clauses** as the authority
(`fuzz_panel.work_remaining`, `:1756`) — own cargo to bank or plant, or a standing plant on a
reachable cell — with one narrowing: reachability is BFS **from this unit's cell alone** rather
than multi-source over all own units. A narrowing of the authority's predicate, not a second idea
about what work is, so the two cannot drift apart.

**`GENERATOR_GAP` now survives the check designed to overturn it.** On these three specimens
`main_candidates` hands the parked unit nothing but WAIT for ~190 consecutive turns while that
unit can itself reach work, with no regeneration commitment and no endgame routing.

A fourth label exists and went **unused** here — `UNIT_CANNOT_REACH_WORK`, for a unit cut off
from work the player still has. It is a reachability fact rather than a generator defect, and it
is the label these rows would have taken if my increment-2 caveat had been the real story.

## What I want on the record about method

I named this weakness myself in increment 2, before anyone asked, and said it was the first place
to attack. Building it was the cheapest way to find out I was wrong — and it would have been the
cheapest way to find out, had I been. **A finding that has survived a serious attempt to kill it
is worth more than one that has not been tried**, and until this increment mine had not been.

That does not make it general: **three specimens are not the ~24**, and the remaining ones may
well split across the other labels. I am not generalising from three.

## Standing limits, still open and still mine

- non-interference is checked on the **first** situation only — a build diverging on a later map
  would pass;
- `classify()` reads only window turns, so a commitment acquired before `turn_start` is counted
  without its acquisition being observed;
- **no cure code**, per your ruling. If this warrants a generator fix it needs its own charter and
  owner gate — and on current evidence it would be the single highest-value item in the
  oscillation programme, since it idles half the workforce for most of a game.

## Consequence for T-1, restated because it affects scheduling

T-1 cannot fix these rows: swap, yield and visibility all presuppose a troll that wants to move
and is blocked. A troll handed only WAIT is not blocked — it has been given nothing to do. This is
consistent with stage 2's measured 0 FIXED / 34 and predicts stages 3–4 will not move them either.
Worth weighing before the nightly measurement is scheduled.

## Boundaries

Resident byte-exact `98628e98…`. Packet-lite SLICE, never packet completeness. No Arena action.
