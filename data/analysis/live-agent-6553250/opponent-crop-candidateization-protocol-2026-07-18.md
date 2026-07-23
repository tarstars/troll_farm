# Opponent-crop suppression — Phase 18 local candidateization protocol, 2026-07-18

## Frozen implementation

Phase 17 selected exactly one treatment before fresh replication: add 100 score points to an
already-existing resident tree candidate when the tree is inferred to be opponent-created and
the current worker ETA is at most six turns. The treatment starts on turn one after at least one
opponent crop is observed. Both the 480-cell discovery and unchanged 480-cell replication passed.

Candidateization must preserve those semantics exactly. It may remove research-only telemetry,
configuration fields, and dead policy families, because they cannot influence commands. It may
not change the bonus, ETA, provenance rule, resident target library, selection order, opening,
orchard wrapper, or any other behavior.

## Reproducible parent

The generator starts from
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs`, 90,547 bytes,
SHA-256 `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`. It must first reproduce
the exact 62,725-byte resident slim source with SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`; otherwise it aborts.
Only then may it insert the fixed provenance state and priority operation. Every insertion anchor
must be unique and fail closed on source drift.

The local output name is
`cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`. A matching SHA-256
sidecar is required. This is a local candidate artifact, not a submission authorization.

## Frozen deployment gates

All gates must pass:

1. generator unit tests cover source/hash drift and the fixed treatment;
2. provenance unit tests prove initial natural trees are excluded, unattributed new trees are
   included, and our preceding `PLANT` excludes its resulting tree;
3. source size is below 100,000 bytes and standalone `rustc --edition 2021 -O` succeeds;
4. all 120 turn-one commands on already-consumed seeds 1300--1359, both seats, are action-identical
   to the exact resident;
5. the slim candidate is byte-for-byte command-stream identical to a standalone build of the
   formatted Phase-17 research controller configured as `b100_e6` on 16 dynamic streams: consumed
   seeds 1300--1307, both seats, alternating RingFix3 and TaskPlan continuations;
6. candidate stderr is empty; interactive command latency over those streams has p95 at most
   20 ms and maximum at most 100 ms;
7. the full Python and release Rust suites, formatting, diff whitespace, JSON parsing, resident
   size/hash, and submit-default pointer remain clean.

No fresh generated seed, seeds 402--999, official-map holdout, controlled platform game, arena
submission, or edit to `cgauto/api_submit.py` is authorized here. Passing Phase 18 establishes a
reproducible, compact local candidate and nothing more.

## Execution result

The fail-closed generator first reproduced the resident slim artifact byte for byte, then emitted
the fixed candidate at 64,522 bytes with SHA-256
`6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`. Standalone optimized
compilation succeeds. The candidate adds only 1,797 source bytes over the validated resident.

| Gate | Result |
|---|---:|
| Generator unit tests | 3/3 pass |
| Provenance unit tests | 3/3 pass |
| Source size | 64,522 / 100,000 bytes |
| Turn-one resident parity | 120/120 cells exact |
| Dynamic research parity | 16/16 streams exact |
| Streams with actual resident divergence | 16/16 |
| Interactive latency p95 | 0.970 ms / 20 ms |
| Interactive latency maximum | 4.135 ms / 100 ms |
| Candidate stderr | empty |

Machine-readable gate:
`data/analysis/live-agent-6553250/opponent-crop-candidate-local-gate-2026-07-18.json`.

## Verdict

Phase 18 passes. The local slim artifact is a reproducible deployment encoding of the exact
Phase-17 research treatment; specialization changed no tested command. This does not establish
arena transfer and does not authorize a game or submission. The next evidence should be a
read-only activation audit on already downloaded official replay states, followed by a separately
declared small controlled transfer protocol only if the field audit confirms that the candidate
changes the intended catastrophic-loss mechanism.
