---
schema_version: 2
type: handoff
task_id: <task-id>
from: <agent-id>
to: <reviewer or integrator>
cc: []
message_id: coordination/messages/<agent-id>/<YYYYMMDDTHHMMSSZ>-<task-id>-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: <YYYY-MM-DDTHH:MM:SSZ>
artifact_ref: agent/<agent-id>
artifact_commit: <full 40-hex SHA of the commit containing every handed-off artifact>
artifact_paths: ["<repo-relative path>", "<source/test manifest path>"]
---

# Handoff: <task-id>

<!--
Canonical publication rule (coordination/multi-agent-protocol.md §4): publish artifacts
first on your canonical agent/<agent-id> branch, then this message in a later commit on
the same branch. The handoff is valid only when artifact_commit is a full 40-hex object
reachable from refs/remotes/origin/<artifact_ref>, every artifact_path exists in that
commit, and this message is present on refs/remotes/origin/agent/<agent-id>. Task
branches cannot satisfy a v2 handoff. A repair is a new `correction` message naming this
file in supersedes — never an edit or a copy. Sweep exit codes: 0 healthy, 1
unacknowledged, 2 transport/schema/delivery error.
-->

- Base commit: <full SHA>

## Outcome
<Concise result.>

## Diff scope
- `<path>`

## Validation
- `<exact command>` — <observed result>

## Measurements
- <Distinguish local, projected, and live-ladder facts.>

## Invariants re-verified
- `sha256sum rust/src/bin/yamo_orchard_live.rs` — <prefix, must be fff6669b>
- `git status --short` — <clean / explained>

## Known failures and assumptions
- <Failure, unverified assumption, or none.>

## Integration notes
1. <Order, generated artifacts, conflicts, or migration notes.>

## Requested action
Review and integrate this exact commit. Do not submit to the Arena unless the user has
separately authorized the exact candidate.
