# policy: 20260729-protocol-bootstrap

- From: claude_1
- To: user
- CC: any future agent
- Created UTC: 2026-07-29T05:22:14Z
- Task: 20260729-protocol-bootstrap
- Branch: session-2026-07-01
- Head: 4a1772e6cb4ebc5bfdac40ad310f9c62a8aa23ba
- Requires acknowledgement: no
- Supersedes: none

## Summary
I am **claude_1**, the first and currently only agent on this repository, taking the
integrator and arena-controller roles by default until the user assigns otherwise. The
multi-agent coordination protocol has been ported from the neighbouring icfpc2026 project
and is now in force: see `coordination/multi-agent-protocol.md`.

Carried over unchanged in substance: worktree-per-agent topology with one integrator; the
four artifacts (task records, status snapshots, immutable typed messages, handoffs); the
filename grammar `YYYYMMDDTHHMMSSZ-<task-id>-<kind>.md`; sender-owned message
namespaces; the 15-minute concrete-progress lease with its stop/takeover procedure; the
path-ownership model; and the merge-collision prefix rule.

Adapted for this project: the contest-submission section became **Arena authority**, tied
to the existing promotion runbook and the standing rule that platform mutations need
explicit user authorization for the exact candidate. The lease definition now names our
**phase markers** as the traceable output that renews it, because experiments here run for
hours rather than minutes. A new hazards section (§7) records the invariants that silently
break other agents' work: the byte-sacred resident dev copy, the ban on running formatters
across hash-locked experiment sources, the sealed map ranges, the daily collection cron,
and the external-storage preflight.

## Evidence
- `coordination/multi-agent-protocol.md` — the adapted spec
- `coordination/README.md`, `coordination/templates/{task,status,message,handoff}.md`
- `scripts/inbox_sweep.py --me claude_1` — sweeps all refs plus the working tree
- `coordination/status/claude_1.md` — my status snapshot
- source: `/home/tarstars/prj/icfpc2026/docs/two-agent-protocol.md` (read-only review)

## Requested action
None. Two things for the user to note. First, the canonical transport is Git refs pushed
to origin, and this repository has never pushed the current era — until it does, agents
must be co-located on this machine and exchange messages through the shared filesystem;
`inbox_sweep.py` already handles both. Second, roles are defaults: name a different
integrator or arena controller at any time and I will publish the change as a policy
message.
