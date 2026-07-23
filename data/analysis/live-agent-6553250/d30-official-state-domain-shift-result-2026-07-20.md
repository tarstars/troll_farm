# D30 official-state domain-shift decomposition — result (2026-07-20)

## Verdict

**The D29b activation collapse is primarily a scalar representation failure caused by an
uncalibrated generated-map prior.**  In the frozen branch factorial, official scalar embeddings
account for `-72.122` raw points at generated spatial embeddings, while official spatial
embeddings account for only `-5.006` at generated scalar embeddings.  The interaction is
`-0.828`; the preregistered two-to-one discriminator therefore identifies the scalar branch.

This explains why D29b behaves differently in the field, but it does not prove that the farm
option is valuable on official roots.  D29b remains closed and no Arena action occurred.

## Integrity

- official development roots: 80/80, exactly the already-consumed D29c prefix;
- generated confirmation roots: 1,920/1,920;
- feature shapes: 426 scalars and `36 x 11 x 22` spatial cells;
- D29c grid-hash mismatches: 0;
- maximum field raw-prediction reproduction error: `0.0001221`;
- maximum generated raw-prediction reproduction error: `0.0000534`; and
- untouched official checkpoint rows inspected: 0.

The complete paired means reproduce D29c: generated `-13.690`, official `-91.735`, difference
`-78.045`.

## Branch-level decomposition

The exact frozen nonlinear head was averaged over every independent spatial/scalar embedding pair:

| Spatial source | Scalar source | Mean raw prediction |
|---|---|---:|
| Generated | Generated | -13.689 |
| Official | Generated | -18.695 |
| Generated | Official | -85.811 |
| Official | Official | -91.645 |

Actual within-row pairing changes the generated mean by only `-0.001` and the official mean by
`-0.090`.  Correlation between branches is therefore negligible here; the negative shift is a
direct change in the scalar embedding regime.

## Static-map mismatch

The single largest replacement effect is `map_water_count`.  Every generated root has exactly six
water cells.  The official development roots contain 12--104, mean 37, so all 80 are outside
generated support and the field mean is 31 training standard deviations above the generated mean.
Replacing only this official scalar with the generated median raises mean prediction by `+27.590`.

The spatial water plane independently confirms that this is real input geometry rather than a
scalar-extractor defect: its official total is also 37 versus six generated, all 80 roots are
outside support, and replacing that plane changes the mean by `+4.273`.

Other static differences reinforce the same diagnosis:

- official iron count is two in 48/80 games and four in 32/80; generated count is always four;
- official shack distance averages 9.675 versus 14.858 generated; replacing the map scalar raises
  prediction by `+6.201`;
- dimensions themselves are covered: both corpora use heights 8--11 and widths 16--22; and
- official walkable area averages 140.275 versus 170.683 generated, with 20/80 plane totals
  outside generated support.

The generated map family places three isolated mirrored water pairs.  Official maps contain broad,
variable water structures.  The critic treated a generator constant as a predictive feature and
then extrapolated far beyond it.

## Dynamic-state mismatch

The problem is broader than water.  All 80 official rows contain at least one scalar value outside
generated confirmation support, totaling 707 feature-value violations; spatial plane totals add
179 violations.  At turn one, official maps average 16.1 plants versus 19.55 generated, with lower
health, size, and cooldown mass.  Banana counts and later economy trajectories are also shifted.

The top one-feature replacement effects after water include shack-distance duplicates from the
turn-one snapshot (`+5.99` to `+6.16`), turn-75 nearby-fruit state (`-7.38`), and several plant-
health and worker-stat histories.  These replacements are deliberately diagnostic: correlated
one-at-a-time edits cannot be summed into a valid corrected prediction.

## Conclusions at three abstractions

1. **Model input:** D29b is numerically correct but out of distribution.  Threshold adjustment
   would hide the symptom and is prohibited.
2. **Simulation substrate:** the generated dimensions are representative, but terrain, initial
   ecosystem, and opponent-driven state evolution are not.  More seeds from the same generator
   cannot repair this.
3. **Policy evidence:** even a field-map-native critic would still need field-native option labels.
   Prior work already showed that the old eight-opponent zoo fails official trajectory coverage,
   so retraining against that zoo alone cannot qualify a candidate.

## Next eligible experiment

First test whether official replay roots can support a trustworthy fixed-opponent-action
counterfactual continuation.  On the consumed 80-game development prefix, validate the exact
resident branch against recorded commands and quantify command validity and simulator divergence
after turn 75.  Only if that control remains faithful may it label resident-versus-farm branches.
If it fails, the next causal discriminator requires prospectively controlled common-map A/B games;
generated-map threshold or model retraining remains ineligible.

Any proposed D31 labeler and gates must be frozen before rows 81--171 are inspected.  The suffix
remains untouched.

## Artifacts

- protocol SHA-256:
  `752f8e107f888527da7748aa944dacadb068d3ee3c93b3c3f1893f61d8f935b9`;
- exact field feature corpus SHA-256:
  `c8f155f5f3489780e57ab1a7a3ab0e3d948ed44b774436520ef8e7ad4db97b0e`;
- machine result SHA-256:
  `95865572917e3be6ea53f9c6f76d4ea5666f69f2edd995fae7b7475eb0a9511b`;
- extractor source SHA-256:
  `3db7c855da328a690cbce3d5fcfe89bdc03a5aa5e17e9daf99335128c46f8a74`; and
- analysis source SHA-256:
  `60a75e25ca3759f78c9c0ad2333e447203b48c1eb06738df25a8525743e8db44`.
