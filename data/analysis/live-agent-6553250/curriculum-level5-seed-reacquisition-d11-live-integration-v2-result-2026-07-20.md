# Curriculum Level 5 D11 live integration V2 result — 2026-07-20

## Verdict

**Reject and close V2.**  The sole post-transition crop-identity guard fixes V1's renewable-count
defect and exact parity advances through 35 complete new-bank games.  A distinct tracker mismatch
then appears on seed 7,700,135 at turn 151, phase 1.  The V2 bank `[7700100,7700164)` is consumed and
will not be rerun for acceptance.

The frozen V2 protocol SHA-256 is
`c881c2d0f2a4ed66ec04162d8e0c90d9f822f8f7afef9c29a2ffc403754fb582`.

## Static and exact results

V2 changes only the three preregistered pending-harvest expressions.  It is 68,325 bytes, compiles
without a diagnostic, and has source SHA-256
`559ebf54de1af5d91ab5f72ec533e0f56bc2ca65463e72fbb0c287a4ee22f981`.

All complete observation/mask hashes, phase counts, actions, and commands match on seeds
7,700,100--7,700,134 and through turn 150 of seed 7,700,135.  At the next phase-1 observation,
only channel **101, distance to the tracked crop/planned objective**, differs.  Source/reference
encoded values are 51/0, corresponding to source distance 8 versus reference distance 0.  Channel
93 now agrees at 191 in the same state, confirming V1's repair.

## Diagnosis

The prior phase actions are `[45, 515]`.  Action 515 is plane 2 (`CHOP`) at spatial cell 31,
coordinate `(9,1)`.  At the failing state the second own worker is still at `(9,1)` and no plant
remains there.  The curriculum tracker clears `created_crop` only for a detected opponent
destruction; it deliberately retains the coordinate when the learned own chopper removes that
crop.  Consequently `crop_exists` is false but the reference objective remains `(9,1)`.  V2's live
tracker instead cleared any missing tracked crop, fell back to the planned objective eight cells
away, and changed only channel 101.

This failure again precedes any mask or action comparison and is not a neural, parser, numerical,
or size defect.  Per-channel diagnosis used only the consumed failing trajectory.

## Next boundary

V3 may record an own CHOP issued on the tracked crop and suppress missing-crop clearing on the next
state only for that exact cell.  Missing crops without that own-action witness remain opponent
destructions and are cleared.  No other state, observer, mask, actor, or gate may change; V3 uses a
new disjoint bank.

