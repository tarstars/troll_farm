# Curriculum Level 5 D11 optimized Rust kernel K2 protocol — frozen 2026-07-20

## Hypothesis and boundary

The accepted int8 actor is numerically and behaviorally deployable, while its first scalar Rust
kernel fails only the 50 ms maximum pair-latency gate.  Reusing four fixed inference workspaces and
removing provably redundant slice-bound checks from the innermost convolution loop should create
enough headroom to pass the unchanged latency conjunction without changing a logit materially.

This is a kernel implementation experiment, not a second quantization search.  The payload,
manifest, checkpoint, corpus, model topology, action ABI, and every threshold remain frozen.  A
pass qualifies only the actor kernel for later integration and high-level recipe selection; it
does not create or authorize an Arena candidate.

## Sole implementation

Generate exactly one K2 Rust source from payload SHA-256
`eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832` and manifest SHA-256
`6bb7a07852308e8ce6b2cce6da5404aedbdd428c0fee0e76cfb5cf7fd47e32db`:

- retain standard padded base64, one startup decode, per-channel f32 dequantization, f32 bias, zero
  padding, NCHW cross-correlation, residual/ReLU positions, and lowest-index masked argmax;
- allocate input, hidden, convolution scratch, and residual buffers exactly once and reuse them for
  every forward pass;
- in each 3x3 output cell, compute the valid kernel-coordinate ranges before accumulation and use
  bounds-elided accesses only inside those proven ranges;
- preserve accumulation order exactly as input channel, kernel row, kernel column; and
- do not introduce threading, SIMD intrinsics, integer accumulation, alternative loop ordering,
  pruning, compression, new compiler flags, or any parameter change.

The generator and tests are written only after this protocol is hashed.  There is no implementation
catalog and no post-result selection.

## Frozen gates and order

1. Generate once, compile directly with `rustc --edition=2021 -O`, and require a dependency-free
   UTF-8 source strictly below 100,000 bytes with no compile diagnostics.
2. On the already frozen 512-observation corpus (compressed SHA-256
   `392bbea038a5d2e0e6a60a4dd2fd459b56752470d5b13c60a3472dca90943d62`), compare every logit with
   the accepted dequantized Python reference.  Require maximum absolute error <=`1e-4`, 512/512
   masked-action agreement, finite logits, legal actions, and empty runtime stderr.
3. Only a parity pass opens the same in-process timing method: initialization plus the first
   two-worker pair <=1,000 ms, then 16 unmeasured warmup pairs and exactly 1,000 measured pairs
   cycling through the frozen corpus.  Require p95 <=45 ms and every measured pair <=50 ms.
4. Report source, payload, corpus, compiler, and binary hashes plus all timing order statistics.

A failure closes K2 without rerun or threshold revision.  A complete pass opens source-integration
accounting and a separately frozen autonomous recipe/first-move controller experiment; it still
does not authorize Arena submission.

