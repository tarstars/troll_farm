# Lineage-collapse liquidation — result, 2026-07-19

## Verdict

**Reject and seal confirmation seeds 2200--2259.** The exact stock state is observable and the
implementation is clean, but permanent liquidation loses substantially. Opponent lineage absence
is a downstream marker of the resident's successful scheduler, not an instruction to stop that
scheduler.

## Integrity

The consumed 0--29 adaptive-Gold panel contains 180 rows and its 20-worker repeat is byte-identical.
All frozen integrity checks pass:

- zero exact-resident shadow mismatches;
- zero switches before turn 101, without prior opponent BANANA crops, or outside the exact
  zero-bank/zero-carry/zero-own-crop-fruit/zero-crop state;
- persistent liquidation after entry;
- zero forbidden TRAIN/PLANT/PICK/HARVEST/MINE commands;
- exact post-entry command accounting;
- exact resident outcomes in all 19 inactive cells; and
- complete games with at least 95% assigned wood provenance.

The controller activates in 41/60 consumed cells. Even there, it loses 17.117 mean margin versus
resident: opponent score falls 4.767, but our score falls 21.883. This warning did not alter the
frozen protocol; fresh discovery still ran.

## Fresh discovery

Seeds 2140--2199, both seats, eight fixed opponents produced 960 paired cells and 2,880 games.

| Gate measure, candidate minus resident | Result | Frozen requirement | Pass |
|---|---:|---:|:---:|
| mean margin | **-12.556** | >= +3.0 | no |
| 10% trimmed mean margin | **-7.693** | >= 0 | no |
| positive opponent families | **0/8** | >= 5/8 | no |
| worst family | **-43.625** (`printer_bot`) | >= -12.0 | no |
| adaptive-Gold margin | **-19.158** | >= +5.0 | no |
| adaptive-Gold opponent score | -8.283 | <= -5.0 | yes |
| adaptive-Gold own score | **-27.442** | >= -10.0 | no |
| adaptive-Gold activations | 93/120 | >= 30/120 | yes |

The candidate activates in 381/960 cells. The 579 inactive cells are exactly resident-identical,
so all loss is attributable to the switch.

## Active-cell causal decomposition

Across the 381 active cells, mean margin changes by -31.638: own score falls 39.549 while opponent
score falls only 7.911. Opponent successful planting changes by just -0.402. Only 13/381 active
cells improve.

The result is not explained by one unlucky entry region:

| Entry cohort | Active cells | Mean margin delta |
|---|---:|---:|
| turns 101--149 | 159 | -44.126 |
| turns 150--199 | 90 | -33.656 |
| turns 200--249 | 78 | -21.051 |
| turn 250+ | 54 | -6.796 |

Even the latest cohort remains negative. Entry while behind loses 11.613; entry margins 0--49,
50--99, and 100+ lose 36.374, 35.658, and 32.620. A score threshold would therefore be post-hoc
tuning, not a supported rescue.

Fifty active cells show later BANANA-lineage recovery. They lose 37.400 margin and prevent about
one planting, while the 331 non-recovery cells lose 30.767. Rebootstrap after the exact boundary
is uncommon and not the missing causal lever.

## Interpretation at three levels

### Command level

The liquidation scheduler successfully removes plants and banks material, but it replaces ongoing
orchard planting and harvesting with low-value travel and chopping. Its target ordering is not the
problem: the opportunity cost dominates.

### State-transition level

Once owned BANANA stock and crops are gone, the opponent has almost nothing left for a terminal
policy to suppress. Adaptive-Gold planting changes by only -0.058 per game overall despite 93
switches. The state marks suppression already achieved by the resident's preceding policy.

### Architectural level

The resident must continue its private renewable economy after rival lineage extinction. The
strong clue is upstream: resident exposes zero fruit on our BANANA crops, while productive farm
profiles maintain roughly 8--9 such fruits at late checkpoints. The next experiment should alter
the production species while preserving the complete productive scheduler, not stop production
after success.

## Closure and next move

Close lineage-triggered liquidation, turn/score filtering of this switch, and its target-order
variants. Preserve the stock-flow state as a diagnostic feature only.

Advance one canonical **species-separated renewable supply** intervention: keep the complete
adaptive farm scheduler and replace its BANANA commodity loop with PLUM. PLUM is fixed a priori as
the lowest-index member of the mechanically identical PLUM/LEMON pair; on water it grows in three
turns per stage and has materially lower chop health than APPLE. Do not catalog species and select
a winner.
