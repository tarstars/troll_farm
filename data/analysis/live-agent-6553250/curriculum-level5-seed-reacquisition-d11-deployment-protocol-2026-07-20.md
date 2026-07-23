# Curriculum Level 5 D11 compact-deployment protocol — frozen 2026-07-20

## Question and boundary

Can the sole prospectively accepted D11 actor be converted into a deterministic compact Rust
controller without material policy loss, numerical implementation drift, latency failure, or
regression of accepted Curriculum Levels 1--4?

This protocol qualifies the learned actor and inference kernel.  It deliberately does not select
the requested worker recipe.  The network receives one of the already frozen eight recipes as an
input; autonomous recipe/first-move selection remains a separate high-level problem.  Passing this
protocol therefore cannot by itself create an Arena submission candidate or authorize an Arena
write.

The sole source checkpoint is
`curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt`, SHA-256
`44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`.  No checkpoint,
weight, layer, channel, or recipe may be selected from conversion results.

## Static feasibility result available before freeze

The full network has 34,926 parameters, but deployment needs only the 33,773-parameter actor.  Its
ten convolution kernels contain 33,616 weights and 157 biases.  Immutable payload accounting gives:

| Format | Raw/encoded bytes before inference code |
|---|---:|
| actor f32 | 135,092 raw; 180,124 base64 |
| actor f16 | 67,546 raw; 90,064 base64 |
| actor int8 kernels | 33,616 raw; 44,824 base64 |

Thus f32 and f16 cannot plausibly satisfy the 100,000-byte single-source limit.  This protocol
freezes one conventional int8 conversion.  The static audit did not execute a game, compare an
action, or inspect a conversion outcome.

## Phase A — sole numerical conversion

- discard the critic from the export payload; do not change the actor topology;
- retain the stem, four two-convolution residual blocks, ReLU locations, and 13-plane actor head;
- for each output channel of each convolution kernel, set the f32 scale to
  `max(abs(weights)) / 127` (or 1 for an all-zero channel);
- quantize with NumPy nearest-even `rint(weight / scale)`, clipped to `[-127, 127]`, as signed int8;
- preserve every actor bias bit-for-bit as little-endian f32;
- preserve every scale as little-endian f32;
- dequantize to f32 for the Python preservation reference; and
- do not retrain, calibrate on activations, prune, change channel width, mix precisions, revise
  scales, or try a second rounding rule in this protocol.

The exporter must write a manifest containing ordered tensor names, shapes, offsets, scales,
biases, payload hashes, checkpoint provenance, parameter counts, and maximum static weight error.
The dequantized PyTorch checkpoint and compact payload must be reproducible byte-for-byte.

## Phase B — frozen policy-preservation gates

First generate exactly 10,000 sequential D11 observations from the original actor on environment
stream beginning at 7,600,000, with 100 environments and the exact
`crop-first-funded-trio-repeated-pressure-reacquire-180` opponent.  On every original-trajectory
state, compare original and converted masked deterministic choices.  Preserve the first 512
observation/mask pairs as the Rust parity corpus and hash it before Rust execution.

The conversion passes the trace gate only if:

- all logits are finite and every selected action is legal;
- original-versus-converted masked argmax agreement is >=99.5% over all 10,000 decisions; and
- no conversion parameter or threshold is revised after the trace is read.

Then evaluate the converted actor exactly once on development `[6500, 7000)` and exactly once on
the already consumed prospective interval `[2031000, 2033000)`.  It must pass every frozen D11
functional, opponent-mechanism, and strict action gate on each interval.  On the 2,000-seed
prospective interval it may lose at most one percentage point relative to the f32 checkpoint on
overall, nontrivial, recipe-floor, height-floor, crop, and renewable-harvest rates.

The exact D11 gates remain: overall/nontrivial >=90%/88%, every recipe >=82%, every height >=85%,
crop >=90%, renewable harvest >=95%, paired-teacher median delay <=30 turns, all original
opponent-mechanism floors, farmer/chopper exact productive choice >=55%/90%, recovery MOVE verb
>=99%, recovery exact source >=30% aggregate and >=10% in every nonempty recipe, and no more than
3,000 unjustified waits.

## Phase C — accepted-level regression

Only a Phase-B pass opens one converted evaluation on each already consumed independent
confirmation bank:

- Level 1 `[2002000, 2003000)`: overall/nontrivial/height >=85%/80%/75%, paired-teacher delay
  <=15 turns, HARVEST choice >=60%, waits <=20,000;
- Level 2 `[2007000, 2009000)`: overall/nontrivial/recipe/height >=85%/80%/70%/70%, productive
  choice >=60%, waits <=40,000;
- Level 3 `[2013000, 2015000)`: overall/nontrivial/height >=85%/80%/70%, crop >=88%, renewable
  harvest >=85%, paired delay <=30 turns, farmer/chopper exact choice >=60% each, waits <=20,000;
- Level 4 `[2017000, 2019000)`: overall/nontrivial/recipe/height >=88%/83%/75%/75%, crop >=90%,
  renewable harvest >=87%, paired delay <=35 turns, farmer/chopper exact choice >=50% each,
  worst nonempty recipe-role >=30%, waits <=35,000.

For every level, the converted actor must also remain within one percentage point of the original
D11 f32 checkpoint on overall success.  Both original and converted actors are read once on these
banks in that order; the comparison is a deployment-regression check, not new learning evidence.
A failure stops before Rust generation.

## Phase D — Rust numerical kernel

Only a complete Phase-C pass authorizes generation of one Rust actor kernel:

- concatenate int8 kernels in manifest order and encode them as standard padded base64;
- encode f32 scales and biases losslessly from their little-endian bytes;
- decode once at process initialization;
- perform every convolution, residual addition, ReLU, mask, and argmax in f32;
- preserve PyTorch NCHW cross-correlation semantics and zero padding; and
- break equal masked logits by the lowest flattened action index, matching PyTorch `argmax`.

On all 512 frozen parity observations, Rust versus the converted Python reference must have maximum
absolute logit error <=`1e-4`, 100% masked-argmax agreement, finite outputs, and legal actions.  The
comparison reports SHA-256 hashes of the corpus, payload, generated source, compiler, and binary.

The scalar kernel is then timed as complete two-worker inference (two forward passes per referee
turn) over at least 1,000 warm samples.  Median is diagnostic; p95 must be <=45 ms and no warm
sample may exceed 50 ms.  Initialization plus the first pair may take at most 1,000 ms.

## Phase E — source feasibility and next boundary

The generated single-file Rust 2021 source must compile directly with `rustc -O`, contain no file
or network dependency, write no diagnostic stderr, and be strictly below 100,000 UTF-8 bytes.
Kernel-only size is reported separately from the estimated and then actual protocol/parser,
observation, mask, two-worker action, and TRAIN integration sizes.  Lossless payload compression
and mechanical minification may be measured because they do not change weights or behavior;
lossy format changes are not allowed after Phase A.

A complete pass accepts the quantized actor kernel as input to a separately frozen integration and
high-level recipe-selection experiment.  A size, latency, parity, D11, or regression failure closes
this exact int8 deployment attempt and requires a new written hypothesis.  It does not permit
post-result threshold changes or Arena submission.

## Frozen anchors

- D11 prospective result SHA-256:
  `3eb1996cfb8196d6c963843ac103ef0caa736bda781c00ab68cbf2fedf8d7cb5`;
- model/evaluation implementation SHA-256:
  `1a855753a145a764d6c3c7d526335c88f5773113f8c32e98376708faed2baf92`;
- Level-1 observation ABI SHA-256:
  `7e76be2b2fae3385a4a1d42ebf2f507efdb3c503148f055932935f2263860b17`;
- Level-3/4/5 observation and action ABI SHA-256:
  `245fd4c8cd48861d40a7a600f65527c6b88fa53a22dc55f00ce5b5196d9555f6`;
- fast-state implementation SHA-256:
  `40e67af2492fa7a37e76729812c1ee078ac98303eafa140ceb5c8536ac9d3d3b`;
- map generator SHA-256:
  `b20bd6712fe47a280c602babf2f1a5aafb1a9b58207a0f3ed18766bd8a058dca`;
- release library SHA-256:
  `381ba5623afb13d77fed09a80dbc2fabc0dd483781a56e9f3c65477783a1dab7`.
