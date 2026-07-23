# D29b quantization-uncertainty abstention — frozen protocol (2026-07-20)

## Hypothesis and boundary

D29a's sole int8 model changed only 0.219%/0.104% of development/confirmation decisions and lost
0.098/0.016 seed-mean margin, but increased development negative-margin mass by 225 because a few
states crossed the zero threshold.  Activating the converted farm option only above **+4.0 raw
predicted margin**, the integer ceiling of D29a's 3.044 development maximum error, should remove
numerically ambiguous switches while retaining D29's large macro gain.

This is exactly one new controller.  The checkpoint, int8 payload, feature representation,
turn-75 cut, resident, `ownership2` branch, and every network operation remain frozen.  There is no
threshold grid, retraining, new quantization, model selection, Arena read, submission, or resident
change.

Frozen anchors:

- int8 verification checkpoint SHA-256
  `9d4ef336880ac2ae57e868f05cb99646f94bb2e92a7d1aedd0ad1a22d12b33ba`;
- int8 payload SHA-256 `acf192cf6b2225de01b12e0507120866f20c7b2e8296a026aa85dfae288be87f`;
- D29a result SHA-256 `e482c585d933140ae40ad090500384ed323e299de37538aff2aa551e8d10ead2`; and
- activation rule `converted_raw_prediction > 4.0` (strict inequality).

## Sole selectable test

Generate exactly 120 new maps, seeds **53,720--53,839**, both seats and the same eight structural
opponents.  Each cell runs the exact resident through turn 74 and records exact terminal resident
and cold permanent-`ownership2` branches from their common turn-75 root.  Export the unchanged 426
scalar and 36 x 11 x 22 canonical spatial features independently.

The 1,920-cell prediction artifact must be byte-identical on a complete rerun.  It is the only
selectable evidence; D29/D29a development and confirmation results are diagnostic and cannot pass
D29b.

## Gates

The +4 controller passes only if all conditions hold on the 120 new maps:

1. all 1,920 cells join with zero missing, duplicate, root, reached-cut, plane-shape, plane-hash,
   canonical-orientation, or nonfinite error;
2. switch rate is 5--55% and positive-cell precision is >=75%;
3. seed-clustered mean margin is >=+8, 5%-trimmed mean >=+5, and 95% lower bound >0;
4. at least 6/8 opponent means are nonnegative and the worst is >=-5;
5. every one of six contiguous 20-map block means is nonnegative;
6. catastrophic frequency and total negative-margin mass do not exceed the resident;
7. at least 25% of the hindsight positive-option seed mean is captured; and
8. two complete executions produce byte-identical raw f32 predictions and decisions.

No threshold or requirement changes after reading the new partition.

## Deployment continuation

A pass reopens D29a Phase B/C with the sole change that Rust and integrated live inference use the
strict +4 activation rule.  Rust must match the converted Python outputs/decisions on every frozen
row, complete turn-75 branch behavior must match the corresponding resident/`ownership2` branch,
warm feature-plus-inference p95 must be <=20 ms with maximum <=45 ms, and the final directly
compilable minified source must be strictly below 100,000 bytes.

A test or deployment failure closes D29b.  A complete deployment pass opens a separately frozen
controlled field-transfer gate; it does not authorize submission or Arena by itself.
