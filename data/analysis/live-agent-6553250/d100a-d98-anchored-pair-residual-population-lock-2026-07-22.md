# D100a D98-anchored pair-residual population lock

Date: 2026-07-22  
Status: locked before any D100 or same-task D98 reference terminal outcome

The protocol and 193-policy population are frozen before opening official-map seeds
`9,823,000--9,823,007`. The population contains exact D40, 64 frozen D98 parents, 64 zero
pair-residual variants, and 64 PCG64-seeded random pair residuals. No outcome, score, rank, oracle
winner, target, favorable subset, or same-task reference value influenced any row.

Pre-outcome checks completed:

- all parent vectors reconstruct exactly from frozen D98 `four_00--four_63`;
- every parent/zero/random triplet shares the same 153 parent weights;
- all parent and zero residual vectors contain 342 exact zeros;
- random residuals reconstruct from NumPy PCG64 seed 10001; and
- all 193 labels are unique and all weights are finite.

Reproducibility anchors:

- protocol SHA-256:
  `1180aab70fb6220d82778f3caf4758d8e03dd90faef8c8166c3230555c9995b9`;
- population generator SHA-256:
  `a8344776a91ce532e523b10b84ddf3277869c9f259fe81a78e513cff1a51f1d8`;
- population SHA-256:
  `a3524fc945667edf63c548c5400453bf75e1264529cf139e67bb236da92e5b95`;
- frozen D98 population SHA-256:
  `3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e`;
- frozen pre-change D98 release binary SHA-256:
  `1e660c8c4615b646f0cc3a190746b2af0e821dea309a34f748f88901249493eb`.

The protocol and population are immutable. An implementation defect may be repaired only under the
unchanged population, reference binary, and outcome-map set, with the repair logged.
