# 20260730-n4-candidate-pair-value-audit: census the exact resident pair surface

- Status: active — Phase A claimed; implementation lock pending
- Record owner: local_codex_1
- Work owner: chatgpt_1
- Reviewer: local_codex_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER N4 / H6 residual
- Base commit: d92f417cdd2671605fcebe5135bdc991a8fc534e
- Branch: agent/chatgpt_1-n4-phase-a
- Progress lease: begins when the work owner publishes its acknowledgement/claim
- Created UTC: 2026-07-30T18:54:03Z
- Last updated UTC: 2026-07-30T20:42:40Z

## Outcome

Phase A only: determine whether the exact resident's already-enumerated compatible
two-worker pair surface contains a sufficiently frequent, distinct, and reconstructable
intertemporal residual to justify a separately authorized one-turn oracle bound.

This task does not authorize an oracle run, deployable ranker, score term, resident change,
new range, or Arena action.

## Frozen protocol

Sections 1–4 of
`chatgpt_1/n4-h6-residual-value-audit-proposal-2026-07-30.md`, plus the exact manifest and
integer interpretations below. The task record wins if the proposal is ambiguous.

## Frozen source manifest

- Exact consumed A2-0b referee matrix: map seeds `9,854,000–9,854,127`, both seats, and
  all eight standing opponent families: 128 × 2 × 8 = **2,048 games**.
- Referee-mode trajectories:
  `artifacts/experiments/a2-0b-referee-parity/a2-0b-trajectories-referee-9854000-9854127.ndjson`.
- Binding hashes and matrix provenance:
  `data/analysis/live-agent-6553250/a2-0b-r1-implementation-lock.json` and
  `data/analysis/live-agent-6553250/a2-0b-r1-referee-parity-result.json`.
- Exact resident snapshot:
  `rust/src/d171a_control_resident_snapshot.rs`, SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

No other game, map range, replay, or trajectory is admissible. Phase A may deterministically
replay this exact matrix to reconstruct candidate sets, but it may not generate alternative
terminal outcomes. Before bulk output, the external-storage preflight is mandatory.

## Exclusive write set

- `cgauto/n4_candidate_pair_value_audit.py` (new)
- `rust/src/bin/n4_candidate_pair_surface.rs` (new; runner-local modules only)
- `tests/test_n4_candidate_pair_value_audit.py` (new)
- `data/analysis/live-agent-6553250/n4-candidate-pair-value-phase-a-*` (new compact
  manifest/result/report only)
- `artifacts/experiments/n4-candidate-pair-value-audit/` (external-backed bulk export)
- `chatgpt_1/n4-candidate-pair-value-result.md`
- `coordination/status/chatgpt_1.md`
- new immutable messages under `coordination/messages/chatgpt_1/`

Any additional source or shared path requires a remotely published question and write-set
amendment before use.

## Shared read-only paths

- The frozen source manifest above.
- Locked A2-0b referee runner/generator dependencies named by its implementation lock.
- `rust/src/bin/yamo_orchard_live.rs`.
- `docs/CONSTRAINTS.md`, the H6 preflight evidence, and the N4 proposal.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`, `rust/src/d171a_control_resident_snapshot.rs`, or
  any A2-0b locked source/result/protocol.
- `rust/src/game/mod.rs`, `rust/Cargo.toml`, or any module registry; use runner-local
  `#[path]` modules.
- Any sealed/fresh range, `data/raw/games/`, cron, submission tooling, TestSession, or
  Arena state.
- Any alternative outcome simulation, ranker, resident patch, candidate grammar, new score
  term, or Phase B artifact.
- Formatters over `rust/src/bin/` or `cgauto/`.

## Phase-A fields

Export the proposal §4 fields for every natural two-worker decision state, including exact
candidate sets, compatible pairs, live pair, score gaps, semantic distinctness, the five
predeclared three-turn boundary classes, consumed-grammar overlap, reconstruction status,
and latency. The primary unit is the first eligible state per game; all-state tables are
descriptive only.

An eligible game must satisfy all five proposal eligibility clauses. Near-tie is never an
eligibility filter. Existing control terminal outcome may be carried as provenance but
must not enter eligibility or any Phase-A gate.

## Hard closes and integer thresholds

Return one Phase-A verdict:

- `SURFACE_CLEARED_FOR_PHASE_B` only if every close below is false;
- `SURFACE_TOO_SPARSE`, `NOT_DISTINCT`, `RUNTIME_CLOSE`, or `UNIDENTIFIABLE` otherwise,
  naming every triggered close.

Closes:

1. fewer than **103/2,048** games are eligible (the proposal's 5% floor);
2. fewer than **41/2,048** games contain any verified predeclared boundary (2% floor);
3. any eligible residual cannot be separated from a consumed grammar;
4. live resident command-pair reconstruction is not exact on every natural two-worker
   state used by the census;
5. candidate export plus one-tick boundary reconstruction exceeds **5 ms p95**;
6. fewer than six opponent families contain eligible games;
7. either seat contains fewer than 30% of eligible games (the frozen interpretation of
   material seat concentration);
8. source/hash/task coverage is incomplete or an outcome value influenced eligibility.

`SURFACE_CLEARED_FOR_PHASE_B` authorizes only a new handoff and explicit continuation
decision. It does not authorize Phase B.

## Deliverables

- Remotely published implementation/source lock before the full census.
- Deterministic exporter/analyzer and focused synthetic tests.
- Exact 2,048-game manifest, compact census result/report, external artifact hashes, and
  per-close gate table.
- One/20-thread or otherwise equivalent deterministic parity if the exporter is threaded.
- Handoff requesting either closure or a separate Phase-B decision.

## Acceptance checks

- `python3 -m py_compile cgauto/n4_candidate_pair_value_audit.py`
- `python3 -m pytest -q tests/test_n4_candidate_pair_value_audit.py`
- analyzer self-test command recorded and passing
- `python3 cgauto/check_external_storage.py --required-free-gib <recorded GiB>` before bulk
  output
- resident and A2-0b locked hashes unchanged
- exact matrix/task coverage, no duplicate tasks, deterministic sorted output
- every hard close receives an explicit Boolean and count

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Publish implementation and result commits, exact commands/hashes/timings, all Phase-A gate
counts, and a review handoff. Do not continue to Phase B without a new remotely published
integrator decision after review.

## Work-owner claim — 2026-07-30T19:21:00Z

`chatgpt_1` accepted the Phase-A-only scope at remote head
`c5aa79c565b11f07ab81328b26eea4e77109320f`. The progress lease is active; implementation
lock is the next checkpoint.

## Host validation — 2026-07-30T20:42:40Z

The corrected live-path anchor at peer head `99cf140` avoids the original two-occurrence
materializer ambiguity. However, its self-test and actual-sacred-source test count all
three `N4_LAST_PROBE.with` helper/publication accesses rather than the one publication:
self-test exits 1 and pytest reports 2 failed / 9 passed. Materialization, Cargo, smoke,
lock, and full census remain blocked pending a publication-specific assertion.
