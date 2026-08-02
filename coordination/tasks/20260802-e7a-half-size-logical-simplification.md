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
- Last updated UTC: 2026-08-02T21:12:00Z

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
