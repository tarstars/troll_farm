# <task-id>: <outcome>

- Status: proposed
- Record owner: <agent-id>
- Work owner: <agent-id>
- Reviewer: <agent-id>
- Integrator: <do not hardcode a name — read `coordination/roster.json` on `origin/main`>
- Area: <backlog item, experiment id, or none>
- Base commit: <full SHA>
- Branch: agent/<agent-id>
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: <YYYY-MM-DDTHH:MM:SSZ>
- Last updated UTC: <YYYY-MM-DDTHH:MM:SSZ>

## Outcome
<One independently verifiable result.>

## Frozen protocol
<Path to the experiment protocol that governs this work, or none. Where a frozen
protocol and this record disagree, the frozen protocol wins.>

## Exclusive write set
- `<path>`

## Shared read-only paths
- `<path>`

## Do not touch
- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred unless compile-then-restore is declared)
- `<path>`

## Deliverables
- `<path or result>`

## Acceptance checks
- `<exact command and expected property>`

## Arena authority
Read-only platform access: <allowed / not needed>
Platform mutation: forbidden unless the user separately authorizes the exact candidate
and the arena controller accepts the handoff (docs/PROMOTION-RUNBOOK.md).

## Handoff
<Expected commit, artifacts, measurements, and reviewer.>
