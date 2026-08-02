# E7a half-size successor attribution after r32 rejection

- Task: `20260802-e7a-half-size-logical-simplification`
- UTC: `2026-08-02T22:06:14Z`
- Evidence boundary: development attribution on the already-consumed r32 range only
- Untouched: seeds 9,854,043--9,854,127
- Arena action: none

## Question

r32 met the size and engineering gates but lost -53.6609 mean paired margin. Three
readable arms separate the late size cuts, removal of the secure orchard, and replacement
of the inner scheduler. All use the same already-consumed 43-map/516-task panel, so none is
qualification evidence.

## Results

| Arm | Bytes | Mean delta | Bootstrap lower | Catastrophes | Negative mass |
|---|---:|---:|---:|---:|---:|
| exact E7a baseline | 62,820 | 0 | -- | 19 | 4,138 |
| orchard removed, exact inner core | 48,644 | -7.6434 | -13.8295 | 23 | 4,955 |
| focused Yamo, exact Moisan core | 33,167 | -27.4535 | -38.9961 | 31 | 8,259 |
| r18 integrated simplification | 35,146 | -46.4864 | -59.3120 | 48 | 11,765 |
| r32 size-qualified result | 31,387 | -53.6609 | -69.2539 | 64 | 15,143 |

The orchard-only arm removes `SecureOrchardBot` and runs its exact configured inner
`YamoBot`; it is 14,176 bytes smaller but still materially negative. The 33,167-byte arm
also specializes the general opening/Yamo orchestration while retaining byte-exact Moisan
chop forecasting, banking, target compatibility, pair selection and movement resolution.
It recovers 19.03 mean margin relative to r18, showing that the final 1.8--3.8 KB of Moisan
simplification was costly, but it remains -27.45 and 1,757 bytes over the ceiling.

r18 is only 7.17 mean margin better than r32 despite being 3,759 bytes larger. Therefore
the terminal failure is not caused by r32's last few size cuts. The first major loss is the
focused Yamo replacement (opening/regeneration/endgame/door behavior); replacing Moisan's
economics and movement adds another large loss.

## Consequence

A successor should not continue trimming r32. The narrowest viable research route is a new
focused-Yamo implementation that restores the parent regeneration/endgame semantics while
retaining the exact Moisan core, then finds at least 1,757 additional bytes of named logical
reduction. That is a hard two-dimensional gate: it must recover roughly 27 development
margin and shrink at the same time. If such an arm is frozen, final validation must use an
untouched 43-map range, not seeds 9,854,000--9,854,042.

## Reproducibility

- development wrapper SHA-256:
  `362d0348705efcdad125584b9acedf065ca9b0bcd774bb8700d726c3590639d5`
- ablation builder SHA-256:
  `85c754303b07fe71ab3c1985f1c2e1ba5658bd84d9044bfecbaacb961a65a24a`
- orchard-only source SHA-256:
  `7a8f3d45621e6fe9b9bd22858476f0ae0cdfb1fcfd5b96a4fea6e7af42dfb69d`
- focused-Yamo/exact-Moisan source SHA-256:
  `8777252c938b2d99ffba257bbdcf60cf8a999f480ff3e2f3d51d4afdc942f990`

Both generated attribution sources pass strict optimized compilation. They are oversized
diagnostic artifacts and are not Arena candidates.
