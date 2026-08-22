---
schema_version: 2
type: progress
task_id: 20260818-osc031-forecast-defect-fix
from: claude_1
to: ["claude_1", "codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260819T100521Z-20260818-osc031-panel-provenance-defect.md
artifact_ref: agent/claude_1
artifact_commit: "0276358664d016c0f081c11c539a835dc456ff11"
artifact_paths: ["claude_1/chop4c/g2-door1-floor.json", "claude_1/chop4c/g2-door1-cand.json"]
created_utc: 2026-08-19T10:05:21Z
---

- To: claude_1 (self — queue item), codex_1
- CC: local_claude_1, user
- Task: 20260818-osc031-forecast-defect-fix
- Requires acknowledgement: yes

# progress: panels run, decomposition NOT valid yet, and my config carries stale provenance

**Artifact `0276358664d016c0f081c11c539a835dc456ff11`.** Reporting a blocked step rather than a result.

## What is measured

Both 240-game panels ran on the c5 corpus: **matched floor (cure C) 58 blocking · Door-1
candidate 50 blocking.**

## What is NOT measured, and why I am not reporting it

The per-game de-novo decomposition **is not valid**. My comparator keyed game identity on
`game`/`id`/`name` — **none of which exist** in these rows; identity is `map_id` + `seat`. All
240 games collapsed into 2 buckets, and the comparator printed **"de-novo: 0"**.

**That zero was false and I am not carrying it forward.** It was caught by the both-ways
control — the reverse direction (floor turns absent from the candidate) never fired, which is
impossible across 240 games and is exactly the signature the control exists to raise. Without
that control I would have published a clean de-novo result built on two collapsed buckets. This
is the same defect family as the `p4_violations` key that did not exist during cure C; the
countermeasure worked this time.

## A provenance defect in my own config

I derived the Door-1 panel configs from the cure-C ones, and the copied metadata is **stale**:
the emitted JSON carries `parent_sha256 = 98628e98…` (the OLD resident) and a `task` string still
naming the cure-C acceptance panel. The runs themselves used the right binaries, but **the
artifacts misdescribe their own parent**, which is not acceptable for a gate record and would
have been a fair review blocker.

DEFERRED: fix the panel configs' parent/task provenance to cure C `ad3bfefe…`, rerun both
panels so the JSON self-describes correctly, repair the decomposition to key on
`(map_id, seat)`, and only then report de-novo by turn coverage with the both-ways control
observed firing in both directions.

## Boundaries

No gate is claimed passed. END STATE ready-with-gates; no Arena action; resident and dev copy
untouched.
