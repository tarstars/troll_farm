---
schema_version: 2
type: handoff
task_id: 20260809-oscillation-attack
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260809T112000Z-20260809-oscillation-attack-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 1e3ce1dcc7bc20ee0e4b90103f4a355d93ad199e
artifact_paths: ["chatgpt_1/oscillation-attack-independent-answer-2026-08-09.md"]
created_utc: 2026-08-09T11:20:00Z
---

# Handoff: independent `readable__no_orchard` oscillation attack

I completed the independently assigned answer without reading either peer's oscillation answer
first.

## Root cause

The memoryless detour is real, but the deeper defect is the planner/resolver interface:

- the planner already jointly rejects equal target cells;
- it does not model route or first-landing compatibility with a stationary working peer;
- the resolver rewrites a blocked MOVE into a one-turn detour;
- that override is not fed back into target validity, commitment or scoring;
- on the next static state the same target pair is selected and the mirror detour returns the
  worker to its previous cell.

Thus two locally valid stateless functions compose into a terminal deterministic involution.
“Add distinct targets” is insufficient because distinct-target compatibility already exists.

## Important negative result

The retired Gold watchdog cannot be ported verbatim as the D-1 fix: it counts a same-position
MOVE streak, while A-B-A changes position every turn. The useful Gold components are the joint
landing solver, stationary-worker obstacles, stay option, non-negative progress and canonical
whole-vector tie-breaking.

## Preferred repair direction

1. freeze all 20 terminal rows and generated two-worker motion microstates;
2. combine the candidate's existing pairwise target enumeration with route/landing compatibility;
3. port the Gold joint landing solver;
4. apply Elost ownership to working tree cells as route obstacles;
5. feed resolver override/no-progress back into target invalidation;
6. retain a period-2 guard only as a safety net.

Acceptance is **20/20 terminal episodes eliminated**, no new terminal episode, no replacement
permanent WAIT/longer cycle, plus preserved swaps/chains and shuffle invariance. Count reduction is
not success and no value claim is made.

The full artifact gives twelve possible actions, expected effects, costs, risks, falsification
conditions and owner boundaries.

No bot, detector, gate, harness, candidate, host run, TestSession, submission, restore or Arena
action was performed.
