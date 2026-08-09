# Requirements for a fast verification executor

- Author: `chatgpt_1`
- Requirements owner: project owner / coordinator
- Date: 2026-08-11
- Status: **REQUIREMENTS FROZEN FOR REVIEW — IMPLEMENTATION NOT SELECTED**
- Replaces: use of temporary GitHub Actions workflows as the default execution substrate
- Scope: repository verification, deterministic experiment execution, and evidence publication
- Out of scope: choosing an implementation, changing bot behavior, changing gate semantics, Arena actions, submission, or automatic acceptance

## 1. Purpose

The project needs a low-latency execution service that can run exact repository commands in a clean, reproducible environment and return durable evidence to agents and reviewers.

GitHub Actions was used only as a temporary execution substrate. The required product is not “CI.” It is a **fast verification executor** with these responsibilities:

1. select exact Git objects;
2. prepare a controlled execution environment;
3. run declared commands without silently changing their meaning;
4. retain complete outputs and identities;
5. optionally publish explicitly authorized artifacts;
6. never turn execution into self-acceptance.

The implementation of this contract is a separate task. This document deliberately specifies behavior and service levels without selecting a host, queue, container runtime, daemon, remote worker, or API framework.

## 2. Workloads the executor must support

The requirements are derived from the temporary Actions jobs already used in the project.

### W1 — transport identity and inbox verification

The executor must be able to:

- check out an exact commit;
- fetch all authoritative remote refs;
- compute literal SHA-256 and Git-blob identities for transport tools;
- run `scripts/inbox_sweep.py --me <agent> --fetch`;
- retain stdout, stderr, and exit code separately;
- distinguish exit 0, 1, and 2 without treating every non-zero code as infrastructure failure;
- preserve delivery errors and unacknowledged-message lists for review.

### W2 — golden-bundle regeneration and renewal

The executor must be able to:

- run an extractor against pinned source data;
- compare regenerated output byte-for-byte with a committed golden file;
- retain a pre-renewal diff;
- compute SHA-256 and Git-blob identities for every bundle member;
- materialize a declared dependency from an authoritative ref when the execution manifest explicitly allows it;
- run the bundle verifier and mutation/regression tests;
- retain all outputs, hashes, and exit codes;
- publish a renewed bundle only through a separately authorized write step;
- keep external review mandatory after a successful run.

### W3 — exact-commit review batches

The executor must support independent jobs pinned to different commits in one request, including:

- Python unit tests and static checkers;
- deterministic replay requiring `rustc`;
- mutation runners;
- corpus generation and reproduction;
- commands whose expected result is a domain verdict such as exit 1 / `BLOCK`;
- post-run assertions over generated JSON;
- parallel execution of jobs that have no dependency edge.

### W4 — short lint and integrity probes

The executor must make small checks cheap enough to run routinely:

- outbox lint;
- exact file/hash checks;
- manifest validation;
- source-identity verification;
- byte-equality comparisons;
- negative controls that are expected to fail.

## 3. Execution request contract

Every run must be described by an immutable, machine-readable request. At minimum it must contain:

- `request_schema_version`;
- `request_id` or content digest;
- repository identity;
- exact commit SHA for each job;
- required canonical refs and fetch policy;
- commands in execution order;
- working directory per command;
- environment variables;
- required toolchain capabilities;
- expected exit-code set per command;
- timeout per command and per job;
- CPU and memory limits;
- network policy;
- input paths and output paths;
- artifact-retention policy;
- write authorization, if any;
- dependency edges between jobs;
- determinism assertions and expected hashes, when known.

A mutable branch name may be recorded for provenance, but it may never substitute for the exact commit SHA used to execute the job.

## 4. Functional requirements

### FR-1 — exact source selection

The executor must run the exact requested commit. It must report the resolved commit and reject a missing or ambiguous object.

### FR-2 — authoritative-ref access

A job may request all remote refs because transport checks and cross-ref manifests depend on them. The executor must report fetch success or failure and must not claim authoritative results after a failed fetch.

### FR-3 — clean isolation

Every job must begin from a clean worktree derived from the requested commit. Undeclared files from another run must not affect it.

### FR-4 — controlled dependency materialization

Reading a file from another authoritative ref is allowed only when the request names the path, the acceptable ref set, and the expected identity or subsequent hash check. Silent fallback to “whatever branch contains the file” is forbidden.

### FR-5 — command fidelity

Commands must execute exactly as declared: exact argv, working directory, environment, and ordering. Shell interpretation must be explicit rather than implicit.

### FR-6 — expected non-zero results

The request must be able to declare expected exit codes. For example, a panel that correctly returns exit 1 / `BLOCK` can be a successful reproduction job. Infrastructure success and domain verdict are separate fields.

### FR-7 — complete evidence capture

For every command the executor must retain:

- exact argv or shell text;
- working directory;
- declared environment, with secrets redacted by policy;
- resolved input commit;
- stdout and stderr as separate byte streams;
- exit code or terminating signal;
- start and finish timestamps;
- wall-clock duration;
- timeout status;
- output-file inventory and hashes.

Logs must not be silently truncated. A UI may show a bounded preview, but the complete stream must remain available by content hash.

### FR-8 — partial-result retention

When a command fails, times out, or produces an invalid artifact, all evidence produced before failure must be retained. A failed run must not disappear from the denominator.

### FR-9 — typed run verdicts

The executor must distinguish at least:

- `EXECUTION_COMPLETE`;
- `DOMAIN_EXPECTATION_FAILED`;
- `INFRASTRUCTURE_ERROR`;
- `TIMEOUT`;
- `RESOURCE_LIMIT`;
- `UNAUTHORIZED_WRITE`;
- `INPUT_IDENTITY_MISMATCH`;
- `OUTPUT_IDENTITY_MISMATCH`;
- `CANCELLED`.

### FR-10 — deterministic rerun comparison

The request may declare output paths that must be byte-identical across two runs. The executor must compare them and identify every differing path.

### FR-11 — content-addressed artifacts

Every retained artifact must have at least SHA-256, size, generating command, source commit, and media/type metadata. The artifact manifest itself must be immutable.

### FR-12 — streaming progress

Stdout/stderr and state transitions must be observable while the job runs. The caller must not wait for the entire job to finish before learning that compilation or a first test failed.

### FR-13 — cancellation

A caller must be able to cancel a queued or running request. Cancellation must terminate descendants and retain partial evidence.

### FR-14 — independent-job concurrency

Jobs without dependency edges must run concurrently. One slow corpus run must not serialize unrelated hash, lint, or unit-test jobs.

### FR-15 — caching without semantic drift

Repository objects, toolchains, and compiled artifacts may be cached. A cache hit is valid only when its key includes all load-bearing identities. Cache reuse and cache misses must be visible in the result.

### FR-16 — LFS policy

Git LFS smudging must be disabled by default unless the request explicitly requires LFS objects. Missing LFS content must fail clearly rather than blocking unrelated repository execution.

### FR-17 — toolchain availability

The baseline environment must support:

- Git;
- Python 3.12 or the exact version requested;
- standard Unix hashing/comparison tools;
- Rust compiler/toolchain for differential and replay jobs.

Any additional dependency must be pinned and declared. A missing tool must fail; tests may not silently skip the oracle because `rustc` is absent.

### FR-18 — read-only default

Execution is read-only with respect to remote Git refs by default. Running code does not authorize commits, pushes, merges, comments, or status changes.

### FR-19 — separate publication transaction

Publication, when requested, must be a separate explicit step with:

- target canonical branch;
- expected old head;
- exact allowlisted paths;
- commit message;
- author identity;
- fast-forward requirement;
- resulting commit SHA.

The executor must reject a stale target head instead of force-pushing.

### FR-20 — no automatic acceptance

A green execution run is evidence, not an acceptance verdict. The executor must not write `ACCEPTED`, merge a candidate, or satisfy a review gate unless a separately authorized reviewer or policy engine makes that decision.

### FR-21 — external-execution identity

When a review requires a second-machine run, the result must identify the worker/environment separately from the authoring environment. Re-running in the same mutable workspace must not be presented as independent execution.

### FR-22 — result querying

The caller must be able to query by request ID, exact commit, job name, or artifact hash and retrieve status and evidence without scanning repository history.

### FR-23 — retry semantics

A retry must either:

- replay the exact immutable request; or
- create a new request with an explicit diff from the old one.

A changed command under the same run identity is forbidden.

### FR-24 — manifest self-description

The result must embed or hash the execution request that produced it. A result without its exact command manifest is not reviewable evidence.

### FR-25 — assertion support

The executor must support post-command assertions over files and structured output, including:

- exact hash;
- exact byte equality;
- JSON field equality;
- expected count;
- expected exit-code class;
- absence or presence of a path;
- no skipped tests.

Assertions must be recorded individually rather than collapsed into one generic failure.

## 5. Security and authority requirements

### SR-1 — untrusted-code sandbox

Repository code is untrusted. It must run without host-level privileges and without access to unrelated workspaces.

### SR-2 — no secrets by default

Jobs receive no repository, cloud, or user secrets unless the request explicitly declares a narrowly scoped credential requirement.

### SR-3 — network deny by default

Network access is denied by default after source acquisition. Permitted endpoints and methods must be explicit. Verification commands should not be able to exfiltrate data or download unpinned dependencies silently.

### SR-4 — filesystem boundaries

The request must declare writable directories. Writes outside those boundaries fail the run.

### SR-5 — resource limits

Every job must have enforceable CPU, memory, process-count, disk, and wall-time limits. Limit termination must be reported as such, not as an arbitrary test failure.

### SR-6 — publication isolation

The process running untrusted tests must not hold a write credential. If publication is authorized, a separate minimal publisher receives only the artifact manifest and allowlisted files.

### SR-7 — immutable audit log

Requests, state transitions, cancellations, publications, and artifact identities must be append-only and attributable.

## 6. Performance requirements

These targets measure executor overhead, not the intrinsic time of compilation or the program under test.

### PR-1 — dispatch latency

- Warm worker: p95 start latency at or below 2 seconds.
- Cold worker: p95 start latency at or below 10 seconds.
- Normal operation must not add a multi-minute queue before a one-second hash or lint command.

### PR-2 — per-job overhead

Preparation and result-finalization overhead should be at most 2 seconds on a warm repository/toolchain cache for a small job.

### PR-3 — streaming latency

New output should be visible to the caller within 250 milliseconds under normal load.

### PR-4 — short-job completion

A warm transport-identity or lint job should normally complete end-to-end within 15 seconds, including evidence finalization.

### PR-5 — parallel batch behavior

For independent jobs, batch wall time should approach the longest constituent job plus bounded orchestration overhead, not the sum of all job durations.

### PR-6 — cached source preparation

When the repository object database already contains the requested commit, creating the clean worktree should be sub-second to low-single-digit seconds. Re-cloning the full repository for each run does not satisfy the warm-path target.

### PR-7 — result publication latency

A read-only result must become queryable within 2 seconds of process completion. An explicitly authorized Git publication should normally complete within 5 seconds after evidence finalization, excluding remote outage.

## 7. Required result schema

At minimum, every run result must expose:

```text
request_id
request_digest
executor_version
worker_identity
source_commit_per_job
canonical_ref_snapshot
started_at
finished_at
infrastructure_status
domain_status
jobs[]
  command_records[]
    argv_or_shell
    cwd
    environment_digest
    stdout_artifact
    stderr_artifact
    exit_code
    signal
    duration
    timeout
  assertions[]
  input_hashes[]
  output_artifacts[]
cache_events[]
publication_record_or_null
```

The schema must be versioned and backward-readable.

## 8. Acceptance tests for a future implementation

A proposed executor is not acceptable until it passes all of the following.

### AT-1 — transport snapshot reproduction

Against the pinned repository snapshot used by the temporary runner, it must reproduce:

```text
inbox_sweep Git blob:
  db4adb7e24cf53aad9033aadccb92c9a6133a934
inbox_sweep SHA-256:
  0f78bf38f32cdd805e29ebfa5591f4f4a55e5a288cd85541df022a452e235515
lint_outbox SHA-256:
  f3c47b70d4f99647eed917876a675a1c28fe5e7236e609455d367a34f6af045d
```

It must retain the sweep's exit code and all delivery errors exactly.

### AT-2 — M3a renewal reproduction

Against the pinned verification snapshot, it must reproduce:

```text
extractor exit: 0
verifier exit: 0
tests exit: 0
golden SHA-256:
  78592335641d45029078e4b67b9d80b2270c9ced5dfb433b00257bc9b422bf8b
manifest SHA-256:
  1287b5a8028514e6e675ebe4c5143d4bccb94afb1633f721e4430964f2031ffc
```

It must also prove the regenerated golden output is byte-identical and that the negative mutation tests actually fail when their target is altered.

### AT-3 — expected-domain-failure handling

A corpus command declared to expect exit 1 / `BLOCK` must produce infrastructure success and domain status `BLOCK`. The same exit code without that declaration must not be silently accepted.

### AT-4 — exact-commit matrix

One request must run at least four jobs pinned to four different commits and prove each job saw its own requested bytes.

### AT-5 — no-oracle skip

Remove `rustc` from a test environment. A differential job must fail explicitly; it must not report success with skipped cases.

### AT-6 — timeout and partial evidence

Terminate a planted long-running command. The result must be `TIMEOUT`, preserve pre-timeout stdout/stderr, and kill descendants.

### AT-7 — unauthorized write

A test command that tries to write outside the allowlisted output directory or push a branch must be blocked and reported as `UNAUTHORIZED_WRITE`.

### AT-8 — stale publication head

Change the canonical branch after a publication request is prepared. The publisher must reject the stale expected head and must not force-update.

### AT-9 — content drift

Change one byte in a pinned source, tool, golden output, or test. The relevant hash or byte-equality assertion must fail and name the changed member.

### AT-10 — latency SLO

Measure cold and warm paths over a representative sample. The implementation must publish raw timing distributions and meet the performance requirements above; an anecdotal single fast run is insufficient.

## 9. Non-goals

The executor is not required to:

- replace the project's git-based communication protocol;
- infer what tests should run;
- decide whether a detector or scientific claim is valid;
- merge branches automatically;
- store every artifact permanently in Git;
- provide arbitrary Internet access;
- hide flaky or non-deterministic behavior by retrying until green;
- convert a self-authored test run into independent review.

## 10. Deferred implementation questions

The following are intentionally left for the separate design task:

- local daemon versus remote service;
- container, VM, sandbox, or other isolation mechanism;
- worker placement and scheduling algorithm;
- cache implementation;
- artifact-store implementation;
- transport/API choice;
- authentication model;
- deployment ownership;
- whether publication should be supported by the executor or by a separate service.

Any design proposal must map every choice back to this requirements document and identify requirements it cannot satisfy.

## 11. Current disposition

- Temporary GitHub Actions workflows remain historical execution evidence only.
- They are not the selected long-term implementation.
- No faster replacement is designed or authorized by this document.
- The next task is requirements review. Only after that should the project open a separate implementation-design task.
