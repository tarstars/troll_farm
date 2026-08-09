---
schema_version: 2
type: handoff
task_id: 20260811-fast-verification-executor-requirements
from: chatgpt_1
to: ["local_claude_1", "claude_1"]
cc: ["user", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260811T233000Z-20260811-fast-verification-executor-requirements-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: a560603ea89f677cb5f13e09e71a20137eb09d53
artifact_paths: ["chatgpt_1/fast-verification-executor-requirements-2026-08-11.md"]
created_utc: 2026-08-11T23:30:00Z
---

- To: local_claude_1, claude_1
- CC: user, local_codex_1
- Task: 20260811-fast-verification-executor-requirements
- Requires acknowledgement: yes

# Handoff: requirements for the fast verification executor

The owner does not want GitHub Actions to remain the execution substrate because its queue and startup latency are too high.

I have separated the system's requirements from the temporary Actions implementation and frozen them here:

`chatgpt_1/fast-verification-executor-requirements-2026-08-11.md`

## What is specified

The contract covers:

- exact-commit and authoritative-ref source selection;
- clean isolated execution;
- expected non-zero domain verdicts;
- complete untruncated stdout/stderr and partial-result retention;
- content-addressed artifacts and deterministic rerun comparison;
- concurrency, cancellation, retry identity and cache correctness;
- read-only execution by default and a separate authorized publication transaction;
- untrusted-code sandboxing, network/filesystem/resource policies;
- explicit latency targets for warm and cold paths;
- the result schema;
- acceptance tests reproducing the transport and M3a verification evidence;
- non-goals and implementation decisions deliberately deferred.

## Important boundary

This is **requirements only**. It does not choose a local daemon, remote worker, container runtime, API, cache, artifact store or deployment model. The quicker implementation must be a separate task after requirements review.

## Review requested

`local_claude_1`: review scope, authority boundaries, publication separation, and whether the acceptance tests cover the project's execution-review needs.

`claude_1`: review whether the contract supports the actual Python/Rust/unit/differential/mutation/corpus workloads without embedding GitHub Actions assumptions.

Please identify requirements that are missing, internally inconsistent, unnecessarily restrictive, or unmeasurable. Do not begin implementation under this handoff.
