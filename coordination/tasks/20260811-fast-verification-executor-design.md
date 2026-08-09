# Task — design a faster verification executor

- Task ID: `20260811-fast-verification-executor-design`
- Created by: `chatgpt_1`
- Requested by: project owner
- Status: **PROPOSED / BLOCKED ON REQUIREMENTS REVIEW**
- Owner: **unassigned**
- Requirements:
  `chatgpt_1/fast-verification-executor-requirements-2026-08-11.md`
- Requirements artifact commit:
  `a560603ea89f677cb5f13e09e71a20137eb09d53`
- Requirements review handoff:
  `coordination/messages/chatgpt_1/20260811T233000Z-20260811-fast-verification-executor-requirements-handoff.md`

## Objective

Design a low-latency replacement for the temporary GitHub Actions execution substrate while preserving exact-commit reproducibility, evidence quality, isolation, and authority separation.

## Start condition

Do not begin implementation or select a platform until:

1. `local_claude_1` has reviewed the requirements for authority, publication, and execution-review coverage;
2. `claude_1` has reviewed the requirements against the actual Python/Rust/differential/mutation/corpus workloads;
3. the owner or coordinator has adjudicated review disagreements and frozen a requirements revision.

## Design deliverable

The design phase must produce, without implementation:

- at least two viable architectures;
- a requirement-by-requirement compliance matrix;
- warm/cold latency model;
- isolation and credential model;
- repository/cache/artifact data-flow diagram;
- failure, retry, cancellation, and partial-evidence semantics;
- deployment and operational ownership;
- cost and maintenance comparison;
- migration plan from temporary Actions evidence;
- a recommended architecture with rejected alternatives and reasons;
- a falsifiable prototype/benchmark plan.

## Binding constraints

- GitHub Actions is not the default target architecture.
- No agent-authored automation may push a verdict or canonical ref from the same process that executes untrusted tests.
- A green run is evidence, not acceptance.
- Exact commits and exact command manifests are mandatory.
- The design must meet or explicitly challenge the performance SLOs in the requirements document with measured assumptions.
- No bot, candidate, detector, gate, Arena, TestSession, or submission work is part of this task.

## Exit condition

The task exits design only when the owner/coordinator accepts one architecture and opens a separately authorized implementation task with a pinned design artifact and acceptance-test plan.
