# 20260824-anti-benching-causal-split-design: isolate the replant option on paper

- Status: **HANDOFF PREPARED — `ISOLATABLE`; PUBLICATION/ACK PENDING**
- Record owner: `local_codex_1`
- Work owner: `local_codex_1`
- Reviewer: `codex_1` only if the completed handoff requests review; no review is required to write the memo
- Integrator: `local_codex_1` per `coordination/roster.json` on `origin/main`
- Area: `20260820-pair-selector-anti-benching`, post-r2 causal split
- Base commit: `89b74912d480a8272d98e9f3b2dd1d0f21f105d1`
- Branch: `agent/local_codex_1`
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-08-24T07:24:45Z
- Last updated UTC: 2026-08-24T07:35:56Z

## Progress — 2026-08-24T07:34:19Z

All ten pins resolve on their named canonical refs and the sacred resident remains `fff6669b…`.
Source tracing separates `main_candidates` formation, `MoisanBot::select`, and
`remember_selected_regeneration`. The first design conclusion is `ISOLATABLE`: construct the exact
parent fallback, append only Delta-A, keep selector code unchanged, and exclude selected Delta-A
provenance from commitment. The memo is drafted; requirement audit and publication remain.

## Handoff state — 2026-08-24T07:35:56Z

The memo artifact is published at
`agent/local_codex_1@c51f8260fd90cde20193ad4ded38e7b1290ca202`. A later immutable handoff pins
that commit and exact path. No implementation or experiment is assigned by the handoff.

## Outcome

One evidence-cited memo concluding either `ISOLATABLE` or `NOT_ISOLATABLE` for a replant-`PICK`-
only design, without implementing or running it.

## Frozen protocol

No new experiment protocol. The activated mission brief is
`coordination/goals/20260824-one-hour-anti-benching-causal-split-design.md`. The accepted r2 design,
frozen gates, stopped result, and pinned rereview are immutable inputs.

## Exclusive write set

- `local_codex_1/reviews/anti-benching-causal-split-design-2026-08-24.md`
- `coordination/messages/local_codex_1/*-20260824-anti-benching-causal-split-design-*.md`
- `coordination/status/local_codex_1.md`
- `coordination/tasks/20260824-anti-benching-causal-split-design.md`

## Shared read-only paths

- Exact pins listed in the activated goal file
- `docs/STATE.md`
- Matching entries in `docs/CONSTRAINTS.md`
- Tail of the live ledger named by `docs/STATE.md` section 5

## Do not touch

- Any candidate source, panel, detector, grader, protocol, or frozen result
- `rust/src/bin/yamo_orchard_live.rs`
- Sealed ranges, `data/raw/games/`, bulk roots, TestSession, submissions, and Arena state

## Deliverables

- `local_codex_1/reviews/anti-benching-causal-split-design-2026-08-24.md`
- A pinned coordination handoff naming the memo's artifact commit and path

## Acceptance checks

- `git diff --check`
- Every goal-file deliverable is present: six-row causal ledger, exact option-only contract, five
  P3 cases, the `m035` pre-divergence P4 counterexample, unexecuted measurement matrix, stage order,
  and one bounded conclusion.
- Every pin resolves from its named canonical branch and the sacred resident SHA-256 retains prefix
  `fff6669b`.
- `python3 scripts/lint_outbox.py --me local_codex_1 --fetch --staged` exits 0 before publication.

## Arena authority

Read-only platform access: not needed. Platform mutation: forbidden. This task cannot submit or
start a TestSession, simulation, replay run, or Arena cycle.

## Handoff

Publish the memo first on `agent/local_codex_1`; then publish a valid v2 handoff in a later commit
that pins the full artifact commit and exact path. Integrate only after checks pass.
