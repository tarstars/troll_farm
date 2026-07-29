# Handoff: <task-id>

- From: <agent-id>
- To: <reviewer or integrator>
- Created UTC: <YYYY-MM-DDTHH:MM:SSZ>
- Task: <task-id>
- Branch: agent/<agent-id>
- Handoff commit: <full SHA>
- Base commit: <full SHA>
- Requires acknowledgement: yes
- Platform mutation performed: no

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
