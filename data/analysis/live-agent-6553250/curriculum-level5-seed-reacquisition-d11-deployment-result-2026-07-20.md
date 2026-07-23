# Curriculum Level 5 D11 compact-deployment result — 2026-07-20

## Verdict

The frozen per-output-channel int8 actor conversion preserves the learned policy, passes every
D11 and Levels 1--4 behavioral gate, compiles as a dependency-free 54,938-byte Rust source, and
passes exact Python/Rust numerical parity.  The first scalar Rust implementation nevertheless
**fails the frozen tail-latency gate**: its 28.387 ms median and 31.484 ms p95 are acceptable, but
one of 1,000 warm two-worker pairs takes 129.258 ms versus the fixed 50 ms maximum.

This exact scalar implementation is closed.  The result neither creates an Arena candidate nor
authorizes a submission.  It opens only the separately frozen, behavior-preserving K2 kernel
optimization experiment.

## Conversion and policy preservation

The sole source checkpoint is
`curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt`, SHA-256
`44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`.  Actor-only int8 export
contains 33,616 quantized weights and 157 f32 biases/scales in 34,872 bytes.  Its payload SHA-256 is
`eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`; repeated export was
byte-identical.  Maximum static weight error is 0.007541.

On the frozen 10,000-decision D11 trace, original f32 versus dequantized-int8 masked choices agree
9,952/10,000 = **99.52%**, above the 99.5% gate, with no illegal or nonfinite result.  The converted
actor then passes both complete D11 banks:

| Bank | Overall | Nontrivial | Worst recipe | Worst height | Crop | Renewable harvest |
|---|---:|---:|---:|---:|---:|---:|
| Development `[6500,7000)` | 97.40% | 96.28% | 90.16% | 96.06% | 97.80% | 97.40% |
| Prospective `[2031000,2033000)` | 97.95% | 97.59% | 96.41% | 96.99% | 98.40% | 98.40% |

Both strict action audits pass.  On the prospective bank, farmer/chopper exact productive choice
is 92.78%/97.10%, aggregate exact empty-seed recovery is 46.50%, worst-recipe recovery is 24.18%,
recovery MOVE-verb choice is above 99%, and unjustified waits are 344/3,000.

## Accepted-level regression

The original checkpoint and converted actor were each read once on the frozen banks, in that
order.  Every functional/action floor passes and converted overall success stays within one
percentage point of f32:

| Level and exact bank | f32 overall | int8 overall | int8 nontrivial | int8 worst recipe | int8 worst height |
|---|---:|---:|---:|---:|---:|
| L1 `[2002000,2003000)` | 99.50% | 99.50% | 99.43% | n/a | 99.19% |
| L2 `[2007000,2009000)` | 99.30% | 99.25% | 98.73% | 96.65% | 98.80% |
| L3 `[2013000,2015000)` | 99.70% | 99.70% | 99.58% | n/a | 99.40% |
| L4 `[2017000,2019000)` | 99.55% | 99.55% | 99.51% | 98.37% | 99.20% |

L1 retains 4,056/5,347 = 75.85% legal HARVEST choices.  L2 retains 94.58% needed productive
choices.  L3 retains 93.07%/97.37% farmer/chopper agreement and 51 waits.  L4 retains
94.19%/96.92% farmer/chopper agreement, 88.79% worst nonempty recipe-role agreement, and one wait.

## Rust parity, size, and latency

The generated Rust 2021 file uses standard base64, decodes the payload once, dequantizes into f32,
and evaluates the exact ten-layer residual actor without an external crate or file.  Direct
`rustc --edition=2021 -O` compilation produced no output or warning.

- generated source: 54,938 bytes, SHA-256
  `60dbbca2f8c4cd67c912675be8444dd1ab8892af138b77fd83d9da3552532ab0`;
- actor kernel including embedded payload: 51,126 bytes;
- parity/benchmark harness: 3,650 bytes;
- frozen 512-observation corpus: compressed SHA-256
  `392bbea038a5d2e0e6a60a4dd2fd459b56752470d5b13c60a3472dca90943d62`, raw SHA-256
  `cbb4bb88013e574c81955dd9ba083730720e464c8641c3fa7af14709ff75f77b`;
- compared logits: 1,610,752; maximum/mean absolute error
  **0.0000686646 / 0.00000312950**;
- masked choices: **512/512 identical**, zero illegal actions and zero nonfinite logits;
- initialization plus first two-worker pair: 89.143 ms;
- 1,000 warm pairs: 28.387 ms median, 31.484 ms p95, **129.258 ms maximum**.

The numerical, source-size, initialization, median, and p95 checks pass.  The maximum-latency check
fails, making Phase D and this exact deployment attempt fail under the preregistered conjunction.
The machine-readable result is
`curriculum-level5-seed-reacquisition-d11-rust-qualification-2026-07-20.json`, SHA-256
`e91b8c95f8d911f707cea839387930f5259febab731e1810788b75ff482e90dd`.

## Interpretation and next boundary

Policy loss, quantization, Rust numerical drift, and standalone source size are no longer the
immediate bottlenecks.  The scalar kernel's ordinary latency is already safe, but its implementation
allocates fresh input, hidden, scratch, and residual buffers inside every forward pass and performs
bounds checks in the deepest convolution loops.  Those are avoidable sources of work and allocator
tail exposure.  K2 tests exactly one predeclared mechanical rewrite: persistent workspaces plus a
bounds-elided convolution that preserves the existing accumulation order.  It may not change the
payload, model, rounding, action rule, parity thresholds, or timing thresholds.

