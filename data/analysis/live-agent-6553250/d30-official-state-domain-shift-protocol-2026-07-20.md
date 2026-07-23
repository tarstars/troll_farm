# D30 official-state domain-shift decomposition — protocol (2026-07-20)

## Purpose and sample boundary

D29c showed a `-78.045`-point mean prediction shift between generated confirmation roots and the
first 80 official resident trajectories.  D30 diagnoses that shift; it does not retune D29b,
estimate the unplayed farm outcome, or reopen the closed transfer.

The development sample is exactly the same first 80 game IDs already consumed by D29c.  No game
after row 80 of the frozen 171-game checkpoint may be read by this diagnostic.  The checkpoint
suffix remains disjoint for a later prospectively frozen D30 confirmation if a new hypothesis is
found.

## Frozen representations

- Field features: exact live D29 history and canonical grid at turn 75, emitted by a standalone
  extractor from the same decoded official protocol transcript used in D29c.
- Generated reference: all 1,920 D29b confirmation roots from seeds 53,720--53,839, both seats,
  and all eight structural opponents.
- Model: the frozen per-output-int8 D29b verification checkpoint.  No parameter, normalization,
  threshold, or feature change is permitted.

The extracted field grids must reproduce all 80 D29c grid hashes.  Frozen model predictions must
match the recorded D29c and generated confirmation predictions within `0.001` raw points.

## Analysis fixed before extraction

The analysis reports five layers:

1. **Representation integrity:** counts, feature shapes, grid hashes, and prediction parity.
2. **Scalar support:** standardized mean shift, field values outside generated min/max support,
   and the 25 largest single-feature replacement effects.  A replacement sets one field feature
   to the generated median while preserving every other field input.  It is diagnostic, not a
   deployable intervention.
3. **Spatial support:** per-plane totals/nonzero support and the 20 largest effects from replacing
   one normalized field plane with the generated mean plane.
4. **Branch factorial:** extract the learned 16-value spatial embedding and 8-value scalar
   embedding, then average the frozen nonlinear head over all independent spatial/scalar pairs for
   generated/generated, field/generated, generated/field, and field/field sources.
5. **Pairing interaction:** compare actual paired means with the independent-pair means.  This
   separates marginal branch shift from correlation between features without claiming causality.

The primary attribution is the change from generated/generated caused by substituting field
spatial embeddings at generated scalar embeddings versus substituting field scalar embeddings at
generated spatial embeddings.  If one absolute marginal is at least twice the other, that branch
is the leading D30 representation target; otherwise the result is mixed.  A material pairing term
is reported separately and is not assigned to either branch.

## Decision rule

D30 produces a new hypothesis only.  It cannot create a submission candidate from this sample.
Any proposed representation correction, official-root continuation method, or new selector must
be written and frozen before the checkpoint suffix is inspected.  Threshold-only rescue of D29b
is forbidden.
