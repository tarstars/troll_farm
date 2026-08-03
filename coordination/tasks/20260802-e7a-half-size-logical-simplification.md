# 20260802-e7a-half-size-logical-simplification: halve live source without leaving top 15

- Status: in_progress
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: pending
- Integrator: local_codex_1
- Area: owner-directed deployment simplification
- Base commit: c123a551c0d9ce7bc7c9c0cf0e1edd494b949d65
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-08-02T19:52:10Z
- Last updated UTC: 2026-08-03T00:10:33Z

## Outcome

Reduce the exact 62,820-byte live E7a source to at most 31,410 bytes by removing or
replacing inefficient logical blocks—not identifier shortening, encoding tricks, or
obfuscation—then demonstrate a live rank no worse than 15 after reconvergence.

## Frozen protocol

`docs/e7a-half-size-logical-simplification-protocol-2026-08-02.md`

## Exclusive write set

- `docs/e7a-half-size-logical-simplification-protocol-2026-08-02.md`
- `local_codex_1/e7a-half-size-logical-simplification/`
- `data/analysis/live-agent-6553250/e7a-half-size-*`
- new paths matching `cgauto/submissions/candidate-e7a-half-size-*`
- `coordination/tasks/20260802-e7a-half-size-logical-simplification.md`
- `coordination/messages/local_codex_1/*20260802-e7a-half-size-logical-simplification*`
- `coordination/status/local_codex_1.md`

## Shared read-only paths

- exact E7a and stable-parent submission artifacts
- `cgauto/slim_live_source.py` and existing validators/runners
- current public replay inventory and decoded audit
- open local evaluation substrates and already-open maps
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, live ledger, promotion runbook

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred)
- every existing `cgauto/submissions/*` artifact
- `data/raw/games/`, the 05:17 cron, and sealed/confirmation map ranges
- Arena mutation endpoints before a recorded qualifying candidate and controller preflight

## Deliverables

- Byte-attribution report naming live logical blocks and their removable sizes.
- Readable candidate source(s), deletion/replacement manifest, builder, and hashes.
- Compile, legality, liveness, command-difference, open-panel value, size, and latency evidence.
- At most one active Arena mutation at a time, fully recorded if a candidate qualifies.
- Mature live checkpoint proving both source bytes <=31,410 and rank <=15.

## Acceptance checks

- `wc -c <candidate>` is at most 31,410 (50% of 62,820).
- A mechanical audit proves no identifier-renaming or compression/minification pass.
- The candidate compiles as standalone optimized Rust and passes malformed/empty-input checks.
- The candidate passes the frozen semantic, liveness, open-panel, and latency gates.
- Arena exact-source recovery matches the candidate SHA-256.
- Mature Arena room read reports rank <=15 for that recovered exact agent identity.
- Sacred source and raw-game cache remain unchanged.

## Arena authority

Read-only platform access: allowed. Platform mutation: only the sole controller
`local_codex_1`, after the frozen local qualification and promotion preflight. The user has
set the terminal live objective (rank <=15), but this record does not waive serialization,
identity, health, or no-ambiguous-retry rules.

## Handoff

Exact candidate, source-size proof, non-obfuscation audit, full validation evidence, live
identity/checkpoint, and final requirement-by-requirement audit.

## Progress 2026-08-02T20:21:09Z

`INTEGRATED_HALF r5` is 30,949 bytes (50.73% below the exact 62,820-byte baseline), SHA-256
`6692fa59...`; standalone optimized compile, empty input, dead-code lint, baseline hash, and
sacred hash gates pass. Static report:
`data/analysis/live-agent-6553250/e7a-half-size-r5-static-qualification-2026-08-02.md`.
Behavioral, liveness, latency, and value qualification remain in progress; no Arena action.

## Progress 2026-08-02T21:12:00Z

r5 failed the 16-game closed-loop smoke (-262.5 mean paired margin; 14/16 catastrophes).
Repairs through r18 restored the same smoke to -6.625 with 3/16 catastrophes and maximum
period-2 target run 3, but r18 is 35,146 bytes, 3,736 over the ceiling.  r19's larger chop
forecast regressed to -11.4375 and was rejected.  Reproducible runner, exact r18/r19 JSON,
and the negative iteration report are prepared for publication; no Arena action.

## Progress 2026-08-02T21:45:15Z

r32 is frozen at 31,387 bytes, SHA-256 `abb202db...`: 23 bytes under the ceiling and a
50.034% real logical reduction. Strict optimized compilation, empty input, sacred hash,
and all 10 semantic fixtures pass. Motion smoke is -6.625 with equal catastrophes and
maximum period-2 target run 3 versus 6. The one-map continued-referee smoke is negative
(-9.9167) but has 12/12 worker-two coverage and zero median delay; one/four-thread task rows
are byte-identical. The exact 43-map/516-task command is now published and locked. No Arena
action; full value and exact live-counterexample liveness gates remain pending.

## Progress 2026-08-02T21:50:00Z

The frozen full panel completed once and terminally rejects r32: mean paired margin
-53.6609, bootstrap lower -69.2539, catastrophes 19 -> 64, negative mass 4,138 -> 15,143,
all six families negative, and both seats negative. Worker-two timing, latency, integrity,
and the local period-2 gate pass, but value does not. No Arena action. r32 will not be tuned
on its evaluated panel; a distinct successor and untouched validation range are required.

## Progress 2026-08-02T22:06:14Z

Already-consumed-panel attribution localizes the loss. Removing only the orchard while
retaining the exact inner core is -7.6434 at 48,644 bytes. Retaining the exact Moisan
forecast/banking/selector/movement beneath the focused Yamo yields -27.4535 at 33,167
bytes, versus r18 -46.4864 and r32 -53.6609. The next route is not further r32 trimming:
it must restore focused-Yamo regeneration/endgame value while removing another 1,757 named
bytes. Seeds 9,854,043--9,854,127 remain untouched; no Arena action.

## Progress 2026-08-02T22:34:10Z

Two consumed-panel ablations recover most of the focused-Yamo loss. Deleting the
unconditional 10,000-point current-tree commitment improves the 516-task mean from
-27.4535 to -20.6298 while shrinking 33,167 -> 32,819 bytes. Restoring the exact tuned
opening then improves it to -9.8101 at 36,059 bytes. A fixed worker, approximate all-profile
search, partial-wood banking, score-aware endgame boundary, and blunt liveness router were
rejected on 96-task probes. The remaining problem is to specialize the exact opening
decisions and remove 4,649 bytes without losing their value. Untouched seeds remain closed;
no Arena action.

## Progress 2026-08-02T23:00:27Z

A distinct size-qualified successor now exists at 31,401 bytes (50.014% reduction),
SHA-256 `923395d8...`. It preserves exact initial tuned-opening decisions and exact Moisan
economics while deleting general policy, priority-router, N-worker, unused trait, and
unused protocol logic. Adding `WAIT` to bank routes repairs an empty-pair single-door case
and improves the 516-task mean to -6.9574, bootstrap lower -13.0213, catastrophes 19 -> 22,
and negative mass 4,138 -> 5,012. Size/compile/latency pass; value and liveness do not, so
the source is not frozen for untouched validation and no Arena action is allowed.

## Progress 2026-08-03T00:04:17Z

A structural-specialization successor is now 31,337 bytes, 73 below the ceiling, SHA-256
`7fd755c2...`. It deletes unused runtime state and zero-harvest/training/rule/target/container
generality without renaming or formatting compression. Standalone compile and empty input pass.
Its 96 non-latency task rows are byte-identical to the prior wait-on-conflict smoke: +6.03125
mean, +0.88542 lower, and zero period-2 episodes >=6. Full 516-task consumed evaluation is the
next phase; untouched maps remain closed and no Arena action is allowed.

## Progress 2026-08-03T00:10:33Z

The exact 31,337-byte successor passes every full 516-task consumed gate: mean +5.5310,
lower +1.8178, catastrophes 19 -> 11, negative mass 4,138 -> 3,695, six/six positive
families, both seats positive, worker-two coverage 100% with delay 0, and period-2 >=6
115 -> 0. Candidate and evaluator hashes are locked. Fresh seeds 9,854,043--9,854,085
were unopened before the lock and are now reserved for transfer validation. No Arena action.
