# D29b complete deployment qualification — result (2026-07-20)

> **Post-qualification field result:** the subsequently preregistered D29c audit selected the farm
> branch on only 7/80 official resident trajectories (`8.75%`) and failed both activation gates.
> D29b's controlled transfer is closed and this candidate must not be submitted.  See
> `d29c-official-field-activation-audit-result-2026-07-20.md`.  The qualification below remains an
> accurate record of implementation equivalence; it is not current transfer eligibility.

## Verdict

**Deployment qualification pass.**  The strict-`>4` int8 spatial option critic, exact warmed
resident, and exact cold permanent `ownership2` branch now form one directly compilable
**96,414-byte** Rust submission.  All 13,440 frozen cells matched the converted Python decision
and the selected reference branch exactly.  Live selection latency and the 100,000-byte source
gate both pass.

At the time, this pass opened a separately frozen controlled field-transfer gate; D29c later
closed it.  The qualification did **not** authorize an Arena submission or replace the resident.

## Integrated controller

The candidate runs the unchanged stable resident through turn 74 while recording the frozen
turn-1/25/50/75 history.  At turn 75 it exports 426 scalar and 36 x 11 x 22 canonical spatial
features, evaluates the frozen per-output-int8 critic, and permanently switches to a cold exact
`OwnershipAwareFarm::new()` specialization only when:

1. the converted raw prediction is strictly greater than `+4.0`; and
2. the live state has exactly two own workers.

The two-worker guard does not alter any frozen D29/D29b cell: all 13,440 common roots have exactly
two workers, and workers never disappear.  Outside that measured support the controller stays on
the resident.

## Exact option specialization

The source specialization removed command-irrelevant research machinery: the telemetry shadow,
telemetry counters, configuration/environment plumbing, and GoldElite's write-only target memory.
The D29 root invariant also made the max-two-worker policy's training and funding path unreachable.

Two independent complete audits were run:

- the initial behavior-preserving port: 13,440 scenarios and 5,922,310 commands, zero mismatch;
- the final two-worker specialization: 13,440 scenarios and 5,922,310 commands, zero mismatch.

The final audit covers seeds 53,000--53,839, both seats, all eight opponents, and every command from
the cold turn-75 root through termination.  The final TSV SHA-256 is
`582186df986ef586822c041c67037f3f0a39c4fb113ef9fbd08a5945203ee26e`.

## Complete integrated parity

The integrated controller was then run from turn 1 through termination on all frozen rows:

- expected/integrated rows: 13,440 / 13,440;
- missing, duplicate, unexpected, or unreached rows: 0;
- converted raw-prediction maximum error: `0.0003089901`;
- decision mismatches: 0;
- switches: 5,438 (`40.4613%`);
- selected-branch mismatches in final turn, margin, both scores, or command hash: 0;
- per-turn command mismatches against the appropriate warmed resident or cold original farm: 0;
- commands compared from turn 1: 7,567,885; and
- pooled selected-cell mean margin increment over resident: `+38.3158`.

The integrated TSV SHA-256 is
`d70bf1dddb75f96c3a8c68b0e2518a3e9d3e7658cc92354de1ab4416c91c9c95`; the machine-readable
qualification result SHA-256 is
`d835e7da6883e52cc753086877c745a15ead5b205b4c8ca7006ea6d49c5031f2`.

## Live-protocol discrepancy found and closed

The first compiled one-file replay found a boundary the in-memory feature parity could not expose.
The simulator initializes `game.scores` to `[0, 0]` and updates them after turn 1, whereas the live
parser immediately derives score from starting inventory.  That changed three turn-1 scalar
features and could flip the turn-75 decision.

The live extractor now intentionally sets only the turn-1 score snapshot to `[0, 0]`, reproducing
the frozen training representation.  The ordinary simulator feature export remained byte-identical
after the change.  Final compiled-source replay covered two five-map blocks (seeds 0--4 and
53,720--53,724), both seats, and all eight opponents:

- cases: 160;
- complete command lines: 45,249;
- byte mismatches: 0; and
- combined transcript SHA-256:
  `1cf505111db30a6e2295e74ce8d26e8822d63c275bf6594b34aac5a87abb8549`.

The protocol replay result SHA-256 is
`c4459fd33951293ce68e55992cb766624bd5ec207e92871dd780a4b3080114f2`.

## Latency

The full 13,440-cell run measured feature assembly, model construction/decoding/inference, and the
first selected branch command while 20 workers were active:

- median: `2.451 ms`;
- p95: `3.771 ms`; and
- maximum: `28.550 ms`.

An uncontended single-thread benchmark over 320 distinct turn-75 roots and 1,000 measured calls
included turn-75 history observation, scalar/spatial assembly, row serialization, payload decode,
model construction, and inference:

- median: `0.753 ms`;
- p95: `0.809 ms`; and
- maximum: `0.920 ms`.

Both measurements pass the frozen p95 `<=20 ms` and maximum `<=45 ms` gates.  The dedicated
benchmark artifact SHA-256 is
`7dfc3d7b2f9f351ca35d4f8f494460a979456401e72b72ae1024e58e478e8a4b`.

## Source gate and reproducibility

The final source accounting is:

- stable resident after constructor substitution: 62,708 bytes;
- compact live features/history: 5,485 bytes;
- int8 kernel and payload: 18,051 bytes;
- exact farm option: 9,593 bytes;
- module and controller wrapper: 577 bytes;
- total: **96,414 bytes**;
- remaining headroom below 100,000: **3,586 bytes**.

The source compiles with optimized Rust 2021 and a complete regeneration is byte-identical.
Candidate SHA-256:
`f074a553804a638d32cf97fe6e2e3cd2c718c4205ad79d6dfb2d6c7dde21c528`.

Frozen implementation hashes:

- candidate generator: `35d08c9bb3b909424f2495c53f861849567ccbeef75e36b6b1ba596ab5f907dc`;
- integrated qualifier: `88badba13b7c549844cbf68a944d6baff034215879562bc45cd4dcc8f565440a`;
- protocol replay gate: `908bbe91270c2171843a6d00acd892d9601544f6f53dafc03065d5cfeea39688`;
- exact farm module: `acda8e340a9c6154b627e9cb37b0bb39d5ad276750dc3950b874f4426a5df085`;
- live feature module: `8ea77c85f3e5960470d5bc97f034da0b768a9120c2cce0de43a20e92cbc09601`;
- exact-farm parity harness: `dbd6eaaee4477d63ed01b9290c108d54544840e87777285205349487ac0cd755`;
- integrated parity harness: `f5e4d908f135762d1a13ed0e46a1679eea3b83e07e0fbf86782b7826e10580fe`;
- live selection benchmark: `220f732b07e0b7d319209a58489df47c68439019ea2087098bc9ffb8ae53eb18`;
- frozen numerical corpus:
  `bcf126bfabd9d4c4ceaac7c57c6197a1f0c69ebd40b9ff5b07d8d7d323af48db`.

The focused Python tests pass (`9 passed`), and both the parity harnesses and final one-file source
compile successfully in optimized mode.

## Superseded next action

The separate controlled field-transfer protocol was frozen in
`d29b-controlled-arena-transfer-protocol-2026-07-20.md`, with the exact resident preserved as
rollback.  Its pretransfer read is identity-clean at 171 finished games, score 23.05, rank 34/107,
and zero runtime signals; the platform source was recovered at the resident SHA.  No submission has
occurred.  D29c subsequently failed its official-state activation gates, so execution is now
prohibited rather than merely awaiting authorization.
