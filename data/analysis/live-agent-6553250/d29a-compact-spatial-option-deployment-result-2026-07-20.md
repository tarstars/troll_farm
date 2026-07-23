# D29a compact spatial-option deployment — result (2026-07-20)

## Verdict

**Closed at Phase A.**  The sole int8 conversion was highly faithful and retained every original
D29 resident-relative gate, but it missed D29a's stricter no-tail-regression conjunction on the
development partition.  Converted negative-margin mass was 205,672 versus 205,447 for f32, an
increase of 225 (0.11%).  Per protocol, Rust generation, live integration, candidate construction,
and Arena activity did not open.

## Conversion and reproducibility

The five affine layers contain 6,976 weights and 41 biases.  Per-output-channel signed-int8
weights, exact f32 biases/scales, scalar normalization, plane scales, and target normalization
produce a 10,864-byte payload.  Maximum static weight error is 0.0020364.

Two complete exports produced byte-identical payload, manifest, and verification checkpoint:

- payload SHA-256 `acf192cf6b2225de01b12e0507120866f20c7b2e8296a026aa85dfae288be87f`;
- manifest SHA-256 `16535ae78ab9a0105c89c3ac0b46098b80fc5a604d10c5cb2b00c130070699c4`;
- verification-checkpoint SHA-256
  `9d4ef336880ac2ae57e868f05cb99646f94bb2e92a7d1aedd0ad1a22d12b33ba`.

## Preservation results

| Metric | 600-map full development | 120-map confirmation |
|---|---:|---:|
| Decision disagreements | 21 / 9,600 (0.219%) | 2 / 1,920 (0.104%) |
| f32 / int8 switches | 4,038 / 4,027 | 787 / 785 |
| f32 selected seed mean | +40.242 | +35.225 |
| int8 selected seed mean | +40.144 | +35.209 |
| Int8 minus f32 mean | -0.098 | -0.016 |
| Maximum raw prediction error | 3.044 | 2.617 |
| Catastrophic frequency | unchanged | unchanged |
| f32 / int8 negative-margin mass | 205,447 / 205,672 | 40,790 / 40,790 |

Both partitions pass the <=1% decision-change and <=1-point paired-mean-loss gates.  The converted
model also retains every D29 aggregate gate on both partitions.  Nevertheless, D29a explicitly
required no tail regression against f32 on each partition, and the 225-unit development increase
is nonzero.  Its magnitude does not permit revising the requirement after observation.

## Engineering implication

Raw payload size is encouraging but not sufficient by itself.  Standard base64 would occupy
14,488 source bytes; resident plus encoded payload would already consume about 77,213 of the
100,000-byte cap before feature/history extraction, inference code, the exact farm option, and
integration.  Source feasibility therefore remains tight even after numerical preservation is
repaired.

## Next hypothesis

All observed decision changes lie near the zero boundary, and the maximum development prediction
error is 3.044.  D29b freezes a conservative `+4` raw-margin activation threshold—the integer
ceiling of that development discrepancy—and tests it once on new seeds 53,720--53,839.  This is a
new prospectively evaluated policy, not a retroactive D29a pass.

## Frozen artifacts

- protocol SHA-256: `59422146871b8beb7de72547dcb12f42cfea14dd22cad23188d9b38bcb42b3db`;
- exporter SHA-256: `d5862404107a2f722c142e91baf81442357b1cd0d97b7488096b020753be4f7d`;
- analyzer SHA-256: `b7495e2c82155b6452ab39dc233286f1dcebf8bfe2c889c3a8d7366af06a55ff`;
- result JSON SHA-256: `139864a3d96bb9c2afe738791642edc4eae89ebeff04d78ed610a828ad794847`.
