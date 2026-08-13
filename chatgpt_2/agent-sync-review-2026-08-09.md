# Stop using Git as a mailbox

**Agent:** `chatgpt_2`  
**Review date:** 2026-08-09  
**Troll Farm snapshot:** `5d679d22de0654e17ba150f4490ce785c6961444`  
**Team Unagi snapshot:** `cce422caf777695b3685d81966fff8973d4a4f25`

## One-sentence verdict

Keep Git for code, immutable evidence, review, and history. Move live task state, claims, leases, heartbeats, exact acknowledgements, and agent compatibility into one transactional control plane.

The full owner-delivered PDF is a 36-page, searchable A4 report titled **Stop Using Git as a Mailbox**. Its SHA-256 is:

```text
f30cdb1b7c359360a58de41f59874ee7973174dce81f1992cc5086b5b2861d67
```

This Markdown file is the repository-native findings and migration record.

## The whole comparison

Troll Farm currently makes one mechanism do six jobs:

1. code store;
2. mailbox;
3. task queue;
4. lease clock;
5. acknowledgement database;
6. dashboard.

Git is excellent at the first job and poor at the other five. The resulting client has to reconstruct live state by scanning remote refs, parsing every historical schema, checking canonical publication, deduplicating immutable paths, validating exact ACKs, migrating seen state, applying quarantine, checking artifact ancestry, and coping with tool-version skew.

Team Unagi does not use one mechanism for everything. Its public ICFPC 2026 repository has two relevant systems:

- `iwiwi/v2/scheduler`: a small SQLite `ask`/`tell` scheduler for human and LLM workers. Shared mutable state is in tables, claims are transactional, suggestions are FIFO, runs have identities and outcomes, and a web page displays current state.
- `crates/executor`: a MySQL-backed machine-job executor. It uses tokenized 30-second TTL locks, heartbeats, takeover after expiry, retry/failure accounting, host identity, command timeout, scores, durations, GCS logs, and a task dashboard.

Git remains the durable place for source, prompts, tests, solution memos, and knowledge.

That separation is the lesson. It is not “copy Unagi's SQLite file.” It is “use transactional state for what is happening now and immutable Git objects for what happened.”

## What Troll Farm must keep

The current coordination work is not wasted. It discovered valuable invariants:

- one isolated branch/worktree per writer;
- explicit write sets;
- one integrator and one Arena controller;
- immutable corrections rather than history rewriting;
- exact ACK targets rather than task/time guesses;
- hash-bound handoffs naming a reachable commit and concrete paths;
- sender-side lint and receiver-side validation;
- independent review before integration;
- preserved negative results, consumed ranges, closure records, and decision evidence.

These belong in the replacement as policy and server-side validation.

## Observed failures, not hypothetical failures

### A correctly addressed message was invisible

At the inspected main commit, `chatgpt_1` was still running a legacy-only scanner. It saw **zero** schema-v2 messages from the preceding ten days, including a critical handoff correctly addressed in front matter. The emergency fix was dual-format messages.

This proves that publication and delivery are different things, and that delivery currently depends on every recipient running a compatible parser.

### A request was mistaken for a completed fix

The coordinator told an agent to update its scanner and later inferred success from unrelated replies. The update had not happened. A replacement must store desired version, reported version, verification time, and compatibility state; the scheduler should refuse assignment to an incompatible client.

### Earlier transport defects already required a major hardening pass

The 2026-08-05 hardening record documents failed fetches appearing healthy, local or unpushed ACKs influencing state, timestamp watermarks missing late messages, and task/time ACK matching forcing synthetic timestamps. The fixes are individually good. The architectural problem is that every new guarantee becomes more client code and more migration state.

### Message publication and artifact publication diverged

A canonical handoff existed before all referenced artifacts were on the canonical branch. Later copying the artifacts did not create a new message event. This is ordinary transactional consistency being emulated through Git conventions.

### Backlogs hide the current fact

A stale client accumulated 188 “new” and 29 unacknowledged messages. A task table should materialize the current owner, state, blocker, lease, and review directly. History remains available but does not have to be replayed to answer “what should I do now?”

### Onboarding and authority text drifted

At the inspected snapshot, the authoritative roster, peer prompt, README, and runbook did not all describe the same branch and integrator. Generate human documentation from one machine-readable configuration and fail CI when generated files differ.

## Where Unagi is better

Unagi gives direct answers for:

- atomic claim;
- current owner;
- run identity;
- explicit completion;
- concurrent worker safety;
- TTL lock and heartbeat for machine jobs;
- retry or requeue;
- current dashboard state;
- structured operational logs.

No worker has to scan every branch and independently reimplement the state machine.

## Where Unagi is not enough

Do not copy it blindly.

- The v2 SQLite scheduler is primarily single-host unless placed behind one API or on a reliably shared filesystem.
- The public v2 LLM scheduler keeps a suggestion claimed until `tell`; manual requeue is visible, but I did not find an automatic TTL heartbeat there.
- The executor coordinates jobs, not overlapping source-file ownership or Git merge review.
- A database creates operational duties: backup, authentication, migrations, monitoring, and recovery.
- Public code is evidence of a concrete implementation, not an independent audit of private live operations.

Troll Farm should combine Unagi's atomic claim with its executor's lease pattern and retain Troll Farm's write-set and integration rules.

## Recommended architecture

Use three explicit sources of truth:

| Question | Source of truth |
|---|---|
| What is happening now? | Transactional coordination service |
| What changed and what evidence exists? | Git commits and branches |
| May it become official? | CI plus the integrator |

### Small control plane

Start with one small service, `coordd`, backed by SQLite in WAL mode on one reliable host. Expose a `coordctl` CLI and a connector-accessible gateway. Move to PostgreSQL/MySQL only when availability or multi-instance requirements justify it.

Minimum tables/concepts:

- `agents`: id, role, protocol version, tool digest, capabilities, last seen, compatibility;
- `tasks`: id, state, priority, owner, requirements, current generation;
- `task_paths`: normalized write-set prefixes with conflict checks;
- `leases`: task, owner, generation/fencing token, expiry, last heartbeat;
- `events`: server-assigned monotonic sequence, server time, type, actor, task, payload, idempotency key;
- `acks`: exact event and acknowledging agent;
- `artifacts`: task, generation, Git ref, full commit, paths, hashes;
- `reviews`: reviewer, verdict, evidence, reviewed artifact generation.

### Required semantics

1. **Atomic claim.** Claiming a task and reserving its write set happen in one transaction.
2. **Lease plus heartbeat.** A crashed agent loses ownership without a human editing status prose.
3. **Fencing generation.** After generation 4 expires and generation 5 is claimed, a late generation-4 handoff is rejected.
4. **Server sequence and time.** Client filename timestamps become presentation only.
5. **Exact ACK rows.** An ACK names one event ID; retries are idempotent.
6. **Compatibility gate.** Unsupported protocol/tool versions cannot receive tasks.
7. **Git artifact validation.** A handoff still names a reachable full commit and paths that exist in it.
8. **Human dashboard.** One page shows active tasks, owners, lease age, blockers, pending review, and incompatible agents.
9. **Audit export.** Important state transitions are periodically exported as compact immutable Markdown/JSON into Git.

### Keep integration separate

The control plane decides who owns live work. It must not silently merge code. Main remains protected by required checks and explicit integrator approval. A merge queue may serialize tested changes, but the project can retain its existing single-integrator rule.

## No-new-service fallback

If some active agents cannot call a database/API, do not return to “scan every branch.” Use one canonical coordination branch and one writer/bot:

- agents submit commands through one supported gateway;
- one writer serializes them;
- one materialized state file answers current-state queries;
- one append-only event log preserves history;
- clients read the canonical projection, not every remote ref;
- Git remains transport, but the state machine has one implementation and one order.

This is weaker than a transactional service but much safer than N independent scanners.

## Migration plan

### P0 — stop making the current system worse

1. Declare dual-format a temporary migration with an explicit exit condition.
2. Generate roster, onboarding, role text, and branch names from one config.
3. Add agent protocol version, scanner digest, and capabilities to registration/status.
4. Add fresh-clone/LFS CI and generated-doc drift CI.
5. Implement `coordctl doctor` over the current repository.
6. Stop using agent timestamps for semantic order.

### P1 — build in shadow mode

1. Implement `coordd` with SQLite WAL.
2. Add atomic task claims, path locks, leases, generations, events, ACKs, and status UI.
3. Mirror current Git messages into the service and compare both projections.
4. Keep Git messages authoritative during comparison.

### P2 — switch authority

1. Make the service authoritative for new tasks, claims, leases, and ACKs.
2. Export compact audit records into Git.
3. Keep hash-bound Git handoffs and independent review.
4. Retire dual-format only after every active client passes compatibility checks.

### P3 — harden integration

1. Protect main with required checks and integrator approval.
2. Serialize merges through a merge queue where available or the existing integrator.
3. Upgrade the datastore only when measured needs justify it.

## Acceptance tests

The replacement is not complete until these are impossible or loud:

- 20 simultaneous claims for one task produce exactly one owner;
- non-overlapping write sets may proceed concurrently;
- overlapping path prefixes cannot both be active;
- a stale generation cannot hand off after takeover;
- restart preserves lease generation and event history;
- unsupported clients are refused with an upgrade message;
- retrying one command with one idempotency key creates one event;
- duplicate ACK is harmless;
- missing commit or missing artifact path is rejected;
- a normal fresh clone, including LFS behavior, succeeds;
- one page shows all active tasks without scanning repository history;
- audit export can be reconciled against database state and integration commits.

## Prioritized decision

**Keep:** worktree isolation, write sets, hash-bound handoffs, immutable corrections, explicit reviewer/integrator authority, and negative-result history.

**Move:** tasks, claims, leases, heartbeats, generations, exact ACKs, version compatibility, and live status into one transactional control plane.

**Reject:** permanent dual-format messages, filename timestamps as ordering, per-agent full-ref scanners, leases without fencing, replies as evidence of upgrades, and premature Kafka/NATS/Kubernetes deployment.

## Final verdict

Turn the protocol into server-side state transitions. Keep Git as the immutable evidence layer. Keep the integrator as the authority layer.

Then the system becomes deliberately boring:

- one task has one owner;
- one lease has one generation;
- one event has one sequence;
- one ACK names one event;
- one handoff names one commit;
- one integrator decides whether it reaches main.

Boring is the goal.

## Evidence map

### Troll Farm

- `coordination/multi-agent-protocol.md`
- `scripts/inbox_sweep.py`, blob `db4adb7e24cf53aad9033aadccb92c9a6133a934`
- `scripts/lint_outbox.py`, blob `172779076bcd6f2c3282322701bf0a498ee652c4`
- `coordination/tasks/20260805-coordination-transport-hardening.md`, blob `c8dfac161da1ff18097f03b429f19c9f49fee94b`
- commit `5d679d22de0654e17ba150f4490ce785c6961444`, version-skew/dual-format incident
- `coordination/roster.json`
- `coordination/peer-prompt.md`
- `docs/RUNBOOK.md`, blob `dbf93be9a7f1c2c54908cfedac6ff09d05c8ed9f`

### Team Unagi

- `icfpc-unagi/icfpc2026`, main `cce422caf777695b3685d81966fff8973d4a4f25`
- `iwiwi/v2/scheduler/README.md`, blob `2f850b5fca0c2ba4ebb4214ddbe54cec2f7298ae`
- `iwiwi/v2/scheduler/scheduler.py`
- `iwiwi/v2/scheduler/tests/test_scheduler.py`, blob `5c614bb9826aabda5814a5931945eee248732514`
- `iwiwi/v2/solver/loop.sh`, blob `c6e3efedd0055c97545ae41be6e4d0875637aade`
- `crates/executor/src/lib.rs`
- `crates/executor/src/lock.rs`
- `crates/lock/src/lib.rs`
- `crates/www/src/handlers/www/task.rs`, blob `93714e1d067ecfa644be5c97dfea077dd70f1802`

### External primary references used in the full PDF

- SQLite transaction and WAL documentation;
- MySQL locking reads, including `NOWAIT` and `SKIP LOCKED`;
- Kubernetes Lease and coordinated leader-election documentation;
- NATS JetStream durable consumer/ACK/redelivery documentation;
- GitHub protected branches, CODEOWNERS, and merge queue documentation.

## Scope and uncertainty

I inspected public repository code and documentation, not Unagi's private database contents or cloud account. I did not benchmark latency or throughput. The public implementation is a concrete, runnable design example rather than proof that every private operational detail was failure-free. The proposed schema is a starting contract, not a drop-in migration script.
