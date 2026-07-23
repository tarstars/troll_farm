# D29b quantization-uncertainty abstention — result (2026-07-20)

## Verdict

**Pass.**  The sole int8 controller with strict `raw_prediction > 4.0` activation passed every
gate on 120 new maps, seeds 53,720--53,839.  It switched 809/1,920 cells (42.14%), reached 86.28%
positive-cell precision, and improved seed-clustered terminal margin by **+36.501** with 95% normal
CI `[28.736, 44.266]`.  The complete prediction artifact repeated byte-for-byte.  This reopens
Rust numerical, latency, exact-branch, and source-size qualification; it does not authorize a
candidate or Arena action.

## Integrity and reproducibility

The independently generated label, scalar, and spatial arms joined all 1,920 expected cells with
zero missing/unexpected cells, duplicate/missing branches, root or reached-cut mismatch, bad plane
shape/hash/orientation, or nonfinite value.  All roots use the exact resident through turn 74 and
the frozen resident/`ownership2` terminal branches.

Two complete evaluations emitted identical artifacts:

- prediction artifact SHA-256
  `7ceea85f8e4f581ffd411c317075f3cb61903971f8d19b3d3450538a89d8c6f2`;
- prediction/decision digest
  `cd6dc28eea2dc1c3ad9390d84ad69090f4fbd80f2aebb8ba2c4bd6bb33e38a5e`;
- accepted result JSON SHA-256
  `0c57d4bf599c5874b9bbb368de3fd4d1956e28dd577f382f0116eba8562ca668`.

## Gate matrix

| Gate | Result |
|---|---:|
| Switch rate 5--55% | 42.14% |
| Positive-cell precision >=75% | 86.28% |
| Seed mean >=+8 | +36.501 |
| 5%-trimmed mean >=+5 | +33.928 |
| 95% lower bound >0 | +28.736 |
| Nonnegative opponent means >=6/8 | 8/8 |
| Worst opponent >=-5 | +25.892 (`silver_boss`) |
| Six 20-map blocks nonnegative | 6/6; range +24.534 to +46.197 |
| Catastrophic frequency <=resident | 9.79% vs 16.51% |
| Negative-margin mass <=resident | 45,906 vs 64,354 (ratio 0.713) |
| Hindsight positive value captured >=25% | 68.65% |
| Exact complete repeat | pass |

At the map level, 88 seed means improved, 22 tied, and 10 regressed; the worst was -36.0.  Own
score improved by +48.668 on average.  Every opponent-specific mean was strongly positive, from
+25.892 to +69.088.

## Interpretation

The result independently confirms that the D29 macro gain survives compact int8 deployment when
states inside the measured numerical uncertainty band abstain to the resident.  The new +36.50
estimate is not borrowed from D29/D29a: it comes from a third untouched 120-map bank designated
after D29a closed.  The switch rate remains close to D29's 40.99%, so the guard removes a narrow
boundary region rather than changing the controller's macro role.

The remaining uncertainty is now engineering and field transfer.  Python feature files are not a
live controller, local structural opponents are not the Legend field, and the resident plus
payload still leaves only about 22.8 kB before feature extraction, inference, farm policy, and
integration.  Rust parity and actual minified accounting must decide deployability.

## Frozen artifacts

- protocol SHA-256: `b7b18c2f18e9b61ec7e87eabb8e0d187fcf371b9cc7f9a63d46f720055952d49`;
- evaluator SHA-256: `366b6113944dfc873b1edb5deb5dc0391b0062f3b6721b4e9b4cb8a7cbe6548c`;
- label SHA-256: `f7cc0713203537c009c5ca8932a26c82ec9e2fb9d4e92855107827d8715eb303`;
- scalar SHA-256: `e6accc905076253cbbabf05cb809fdea2282b9213187e477ab51fded2c2a949e`;
- spatial SHA-256: `35c498743739446cc194a542040a653e7f7149b1e0d9a3814d410a2b13d79a15`.
