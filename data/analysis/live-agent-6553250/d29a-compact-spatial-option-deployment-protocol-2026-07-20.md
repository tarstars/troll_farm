# D29a compact spatial-option deployment — frozen protocol (2026-07-20)

## Question and boundary

Can the sole accepted D29 checkpoint be converted into a deterministic Rust turn-75 controller,
preserve its decisions and value, execute within the live turn limit, and fit the complete resident
plus exact `ownership2` option below CodinGame's 100,000-byte source cap?

This is a deployment-preservation experiment.  It may not retrain, prune, calibrate a threshold,
change the turn-75 cut, replace either branch, inspect Arena battles, submit, or change the active
resident.  A pass opens a separately frozen field-transfer gate only.

Frozen anchors:

- checkpoint SHA-256 `765e3bc5707ced9053a76d2735232e873003baccff6500bd8c1377b3c28721c9`;
- D29 result SHA-256 `eda7d83d565cd9dc66cb586fe73bb51f6df276625938e2d3fdb22875a0d2313b`;
- fallback `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes, SHA-256
  `a8eb3b3ac53211b5279edb35c09ba8f887369a43b926f44d2d4916f234303051`;
- exact option `OwnershipAwareFarm::new()` with its frozen two-worker configuration; and
- development/confirmation partitions and labels from D29, with no new outcome-selected corpus.

## Phase A — sole numerical conversion

Convert exactly the five frozen affine layers (`conv1`, `conv2`, `scalar`, `hidden`, `output`) as
follows:

- quantize each weight tensor independently per output channel/row with symmetric signed int8;
- scale is f32 `max(abs(channel weights))/127`, or 1 for an all-zero channel;
- rounding is NumPy nearest-even `rint`, clipped to `[-127, 127]`;
- preserve all 41 biases, 426 scalar means, 426 scalar standard deviations, target mean/std, and
  plane scales as exact little-endian f32;
- dequantize weights once at startup and perform inference in f32; and
- do not try another bit width, scale rule, rounding rule, mixed precision, calibration, or model
  variant after reading conversion outcomes.

The ordered payload and manifest must be byte-identical on a complete repeat.  The manifest records
tensor names, shapes, offsets, byte counts, scales, biases, all input-normalization arrays, source
hashes, payload hash, and maximum static weight error.

Evaluate the original full-development model and its dequantized conversion on all 9,600
development and 1,920 confirmation cells.  On each partition require finite predictions, no more
than 1% decision disagreement, no more than one point loss in seed-clustered selected margin, and
no tail-gate regression.  The converted model must independently retain every D29 confirmation
aggregate gate at the frozen zero threshold.

## Phase B — deterministic Rust inference

Generate one dependency-free Rust implementation with the same canonical planes, fixed scales,
folded scalar normalization, NCHW 3 x 3 zero-padded cross-correlation, ReLUs, in-map masked mean and
maximum, concatenation order, and f32 affine accumulation.  Decode/dequantize immutable payloads
once.  No threading, SIMD intrinsics, alternative topology, or outcome-informed optimization is
allowed before the first parity result.

On every one of the 11,520 frozen development and confirmation feature rows, compare Rust with the
dequantized Python reference.  Require:

- all outputs finite;
- maximum normalized-output absolute error <=1e-4;
- 100% zero-threshold decision agreement; and
- byte-identical Rust output on a repeated invocation.

Measure complete canonical feature assembly plus inference on at least 1,000 warm calls.  Startup
plus first inference must be <=1,000 ms; warm p95 must be <=20 ms and every warm call <=45 ms.

## Phase C — live branch and source parity

Integrate the kernel into a single stateful controller that:

1. runs the exact warmed resident through turn 74 while collecting only the frozen observable
   snapshots/trajectory scalars;
2. evaluates once on the turn-75 state;
3. keeps the same warmed resident forever when the prediction is nonpositive; or
4. creates/uses a cold exact `ownership2` policy forever when the prediction is positive.

On smoke seeds 0--4 and the 120 confirmation maps, both seats and all eight opponents, require the
integrated controller's turn-1--74 commands to equal the resident, its turn-75 decision to equal
the accepted quantized Python decision, and its complete command stream/final outcome to equal the
corresponding frozen resident or `ownership2` branch.  No fallback on an inference or feature error
is permitted in qualification.

Bundle/minify exactly once after parity.  The final UTF-8 source must compile directly with
`rustc --edition=2021 -O`, produce empty compiler/runtime diagnostics under the qualification
harness, and be strictly below 100,000 bytes.  Report resident, feature/history, payload/kernel,
farm-option, integration, unminified, and minified byte accounting separately.

## Disposition

A failure of numerical preservation, parity, latency, branch identity, or size closes this exact
deployment attempt.  The next hypothesis may distill the option or slim semantically dead resident
code, but may not silently substitute a cheaper policy and claim D29 evidence.  A complete pass
authorizes only a preregistered controlled field-transfer plan, not submission or Arena action.
