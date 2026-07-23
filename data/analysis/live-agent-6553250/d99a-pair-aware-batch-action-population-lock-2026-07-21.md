# D99a pair-aware batch-action population lock

Date: 2026-07-21  
Status: locked before any D99 or same-task D98 reference policy reached terminal state

The D99 protocol and random population are frozen before opening official-map seeds
`9,822,000--9,822,007`. The population contains one exact-zero control and 64 matched weight
vectors, each instantiated with intervention budget one and four. No outcome, score, rank, oracle
winner, target, favorable task, or D98 same-task reference value was used to construct, reject,
reorder, or alter a vector.

The D98 reference is the already-built release binary from the completed frozen D98 experiment.
It may produce a same-task architecture baseline but cannot influence D99's features, population,
implementation, thresholds, or gates.

Pre-outcome checks completed:

- the D99 population reconstructs exactly from NumPy PCG64 seed 9901;
- all 64 one/four pairs have identical 342-value vectors and exact budgets one/four; and
- all weights are finite, with the exact-zero control first and 129 unique labels.

Reproducibility anchors:

- protocol SHA-256:
  `7263a04fdef43f0ecd4cdb74aa377c3417eafe81e03a591f459db539cdc519b8`;
- population generator SHA-256:
  `f150f56f3472c5f71e94732944e60634d3d9348ad5c9524814d05c7c4934872c`;
- population SHA-256:
  `4e46456c2b8d156b7219cd5a78fb08b35bf4d59977ef30e4aa97afb6b8f18789`;
- frozen pre-change D98 release binary SHA-256:
  `1e660c8c4615b646f0cc3a190746b2af0e821dea309a34f748f88901249493eb`.

The protocol and population are now immutable. An implementation defect may be repaired only under
the unchanged protocol, population, reference binary, and outcome-map set, with the repair logged.
