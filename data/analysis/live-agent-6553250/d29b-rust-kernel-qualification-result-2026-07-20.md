# D29b Rust kernel qualification — result (2026-07-20)

## Verdict

**Numerical kernel pass; live integration still open.**  The generated dependency-free Rust 2021
critic matched the converted Python model on all 13,440 frozen rows with zero decision mismatch
and maximum normalized-output error `3.132e-6`, far below the `1e-4` gate.  Two complete parity
invocations emitted byte-identical output.  Kernel-side row decoding, normalization, and inference
also pass latency comfortably.  This does not yet prove live GameState feature assembly, exact
resident/farm branch identity, or combined source size.

## Corpus

The 257,147,544-byte binary corpus contains, in fixed order:

- 9,600 D29 development rows;
- 1,920 D29 confirmation rows; and
- 1,920 D29b confirmation rows.

Every row contains the canonical 8,712 i16 spatial values, 426 f32 scalars, converted-Python raw
prediction, and strict-`>4` decision.  Corpus SHA-256 is
`bcf126bfabd9d4c4ceaac7c57c6197a1f0c69ebd40b9ff5b07d8d7d323af48db`.

## Parity

- rows: 13,440;
- finite outputs: 13,440/13,440;
- maximum raw prediction error: 0.000308990;
- maximum normalized prediction error: 0.000003132;
- decision agreement: 13,440/13,440;
- deterministic checksum: `184832108992849567` on both complete runs; and
- payload identity: `acf192cf6b2225de01b12e0507120866f20c7b2e8296a026aa85dfae288be87f`.

## Kernel latency

The single-threaded optimized Rust harness measured 16 warmups and 1,000 calls while cycling the
frozen corpus.  Each call includes binary feature decoding, plane/scalar normalization, both
convolutions, masked pooling, and all affine layers:

- payload decode plus first call: 1.879 ms;
- median: 0.532 ms;
- p95: 1.464 ms; and
- maximum: 1.824 ms.

This is diagnostic headroom, not the final live latency result, because constructing the 426
history scalars and 36 planes from `GameState` is not included yet.

## Source accounting

The standalone source is 23,708 bytes: 19,786 bytes for the kernel including the 14,488-byte
base64 payload and 3,817 bytes for the parity/benchmark harness.  The kernel alone plus the
62,725-byte resident is already about 82.5 kB, leaving roughly 17.5 kB for live feature/history
extraction, exact `ownership2`, and integration.  Therefore numerical deployment is easy but the
100 kB complete-controller gate is still the dominant risk.

## Frozen hashes

- corpus generator: `dc2e758469c6a07238320d61b1ef322c86e96cc92e721db79292c9ccb96e9486`;
- corpus manifest: `3b4841c526f66e8d4742c30a272fd56e236daeb8c501271cd64d2f2675ad858c`;
- Rust generator: `755a689d30ccfd690d05424e8a518d6aae42585442c8494654e2cfb47701187d`;
- generated source: `a2e5785e30f093bff750be9937a431fb9db92bd9bd14959428f9f901548486a9`;
- compiled binary: `05becf862aa06a910e5921510e6be3e9fef17513a3b3aa7293e464e1abacea75`;
- compiler: rustc 1.75.0 / LLVM 17.0.6.

## Next action

Implement behavior-identical live feature/history extraction and measure its incremental bytes and
latency before porting the farm option.  If selector plus exact option cannot fit, close exact D29b
integration and open a separately validated compact distillation; do not substitute a surrogate
under D29b's result.
