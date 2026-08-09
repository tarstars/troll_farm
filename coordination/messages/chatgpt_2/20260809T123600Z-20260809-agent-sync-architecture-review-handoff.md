---
schema_version: 2
type: handoff
task_id: 20260809-agent-sync-architecture-review
from: chatgpt_2
to: ["local_claude_1"]
cc: ["user", "local_codex_1", "claude_1", "chatgpt_1"]
message_id: coordination/messages/chatgpt_2/20260809T123600Z-20260809-agent-sync-architecture-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-09T12:36:00Z
artifact_ref: agent/chatgpt_2
artifact_commit: 5b1affd0e815cd48562fb07c091d47f174080152
artifact_paths: ["chatgpt_2/agent-sync-review-2026-08-09.md"]
---

- To: local_claude_1
- CC: user, local_codex_1, claude_1, chatgpt_1
- Task: 20260809-agent-sync-architecture-review
- Requires acknowledgement: yes

# Handoff: Troll Farm / Team Unagi synchronization architecture review

The user directly assigned `chatgpt_2` to review our multi-agent synchronization tools, inspect known working approaches, compare them with Team Unagi's public `icfpc2026` repository, write an idiotically clear PDF, and share the findings.

The read-only review is complete. No bot, experiment, shared protocol, data, candidate, TestSession, submission, or Arena state was touched.

## Canonical repository artifact

- Commit: `5b1affd0e815cd48562fb07c091d47f174080152`
- Path: `chatgpt_2/agent-sync-review-2026-08-09.md`
- Branch: `agent/chatgpt_2`

The owner also received a visually inspected, searchable, 36-page A4 PDF titled **Stop Using Git as a Mailbox**. PDF SHA-256:

```text
f30cdb1b7c359360a58de41f59874ee7973174dce81f1992cc5086b5b2861d67
```

The repository Markdown contains the actionable findings, migration plan, acceptance tests, and evidence map.

## Main finding

Troll Farm's strong ideas are not the problem. Keep:

- isolated writer branches/worktrees;
- explicit write sets;
- immutable corrections;
- exact ACK targets;
- hash-bound handoffs;
- independent review;
- one integrator and one Arena controller;
- durable negative-result and closure history.

The problem is using the same distributed Git history as the mailbox, task queue, lease clock, ACK database, compatibility layer, and live dashboard. Every agent must independently replay and interpret live state. The recorded `chatgpt_1` version-skew incident — zero visible v2 messages for ten days despite correct front-matter addressing — is direct evidence that publication does not guarantee delivery.

## Unagi comparison

Unagi uses different mechanisms for different jobs:

1. `iwiwi/v2/scheduler`: SQLite `ask`/`tell`, transactional FIFO claims, run identities, explicit outcomes, status UI, and concurrent-claim tests for human/LLM workers.
2. `crates/executor`: MySQL task rows with tokenized 30-second TTL locks, heartbeats, takeover/retry accounting, host identity, timeout, score/duration, GCS logs, and task dashboard for machine jobs.
3. Git: durable source, prompts, tests, memos, and knowledge.

Do not copy it blindly: the SQLite scheduler is primarily single-host unless placed behind an API, its public LLM claim lifecycle has manual stale-claim recovery, and the executor does not solve source write ownership or merge authority.

## Recommended target

Use three explicit sources of truth:

- **transactional control plane** — what is happening now;
- **Git** — what changed and what evidence exists;
- **CI plus integrator** — whether it may become official.

Start small: one `coordd` service backed by SQLite WAL on one reliable host, one `coordctl` CLI, and one connector-accessible gateway. Required concepts are atomic task/write-set claim, lease heartbeat, generation/fencing token, server sequence/time, exact event ACK, agent protocol/tool compatibility, Git artifact validation, idempotency keys, dashboard, and audit export to Git.

If a service is temporarily impossible, the bounded fallback is one canonical coordination branch with one writer/bot and one materialized current-state projection — not N agents scanning every ref.

## Suggested implementation decisions

Please review and, if accepted, cut narrow tasks rather than one giant rewrite:

### P0 — current-system containment

1. Declare dual-format temporary and define its exit gate.
2. Generate roster/onboarding/role/branch text from one config.
3. Record and verify agent protocol version, scanner digest, and capabilities.
4. Add fresh-clone/LFS and generated-document drift CI.
5. Build `coordctl doctor` against the current repository.
6. Remove agent timestamps from semantic ordering.

### P1 — shadow control plane

1. Implement SQLite-WAL `coordd` with tasks, path locks, leases, generations, events, exact ACKs, agent compatibility, and status page.
2. Add CLI plus a connector-accessible gateway.
3. Mirror current Git messages into the service in shadow mode and compare both projections before changing authority.

### P2 — authority switch

1. Make the service authoritative for new tasks, claims, leases, and ACKs.
2. Export compact immutable audit records back into Git.
3. Keep hash-bound Git handoffs and independent integration review.

## Acceptance gates highlighted in the report

- 20 simultaneous claims for one task yield exactly one owner.
- Non-overlapping write sets may proceed; overlapping prefixes may not.
- A stale lease generation cannot hand off after takeover.
- Unsupported agents are refused before assignment with an explicit upgrade reason.
- Command retries are idempotent and duplicate ACKs are harmless.
- Missing commits or artifact paths are rejected.
- Fresh clone with normal LFS behavior succeeds.
- One current-state page answers who owns what without scanning repository history.
- Audit export reconciles with database state and Git integration commits.

## Requested acknowledgement

Please acknowledge the exact handoff path, review the report, and record whether the project accepts the architectural direction. Acceptance of the direction need not authorize implementation; the next useful action is a bounded P0/P1 task split with explicit owners and write sets.
