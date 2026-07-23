# Curriculum Level 5 D11 live integration V1 result — 2026-07-20

## Verdict

**Reject and close V1.**  Static feasibility passes: the complete referee-facing source is 68,270
bytes, compiles directly with no diagnostics, and leaves 31,730 bytes below the submission limit.
Interactive ABI parity then fails on exact seed 7,700,003 at referee turn 129, phase 0.  The frozen
bank `[7700000,7700064)` is consumed and will not be rerun for acceptance.

The frozen protocol SHA-256 is
`f7d05facb1f5fffd08f484a72ce58b6604d91e165451c2b5e67f0da0fe703fb7`.

## Static result

- standard-base64 payload: 46,496 bytes;
- K2 kernel/payload and live prefix: 52,112 bytes;
- parser, state, and static navigation: 5,368 bytes;
- observer, mask, and tracker: 7,922 bytes;
- command, TRAIN, audit, and main loop: 2,868 bytes;
- complete source: **68,270 bytes**, SHA-256
  `61a276360e053fa23abe9a71b611a59eff3de0852bdd23d5ac89205556bce41e`.

The source is byte-reproducible and `rustc --edition=2021 -O` emits no stdout/stderr.  Thus the
complete learned controller—not merely its standalone kernel—fits comfortably under 100 kB.

## Exact failure and diagnosis

V1 passes every observation and mask hash through seeds 7,700,000--7,700,002 and through turn 128
of seed 7,700,003.  At turn 129 its complete observation FNV-1a hash is
`f1ef56e5ebc2fbb4`, versus reference `5443ce9f9ac138b4`.  Per-channel localization finds exactly
one differing channel: **93, renewable-harvest count**.  Every other one of the 104 channels is
byte-identical; the failure occurs before a mask or action discrepancy.

The source encodes channel 93 as 128, corresponding to count 2 under the frozen scale of 4; the
reference encodes 64, corresponding to count 1.  The triggering transition simultaneously lets an
own worker receive BANANA fruit from a HARVEST and lets the opponent destroy the tracked renewable
crop.  `Level3Env` first clears/replaces the tracked crop after the referee step and only then counts
a harvest whose pre-step worker position still equals the **post-step tracked crop**.  V1 instead
remembered only worker id and prior BANANA carry, so it counted the fruit increase even after that
crop identity was cleared.

This is an exact state-reconstruction defect, not neural drift, parser failure, action illegality,
or source pressure.  The diagnostic used only the consumed failing trajectory and per-channel
hashes; it did not inspect or rerun a new acceptance seed.

## Next boundary

V2 may change exactly one semantic condition: store the pending harvest cell and increment the
renewable counter only when the post-transition tracked crop still equals that cell, after crop
destruction and successful pending-plant resolution.  All other code, weights, gates, and source
accounting remain fixed.  V2 must use a new disjoint parity bank.

