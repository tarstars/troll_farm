# D18 resident residual spatial distillation — development result (2026-07-20)

## Decision

**Reject both frozen spatial formulations.  Zero fresh-validation thresholds pass, so maps
35,000--35,039 remain ungenerated and no policy prototype is authorized.**

Path geometry improves the very narrow prediction tail, but neither the geometry MLP nor the tiny
dilated convolution separates positive interventions from high-cost negative lookalikes at a
useful activation rate.  D18 must not be repaired by moving a threshold on these validation maps.

## Complete execution

- Reconstructed 28,800 training observations and 5,760 fresh-validation observations, each
  `137×11×22` uint8.
- Every row passed exact scenario, candidate-count, action, active-cell, action-plane, and
  legal-count reconstruction checks.
- Training covered 200 maps and 5,044 positive labels; validation covered 40 entirely fresh maps
  and 1,024 positive labels.
- Trained eight frozen models: binary and clipped-value versions of a 4,585-parameter geometry
  MLP and a 5,401-parameter spatial scorer, each with two seeds.
- Evaluated all five precommitted activation quantiles per model.  All 40 recipes failed.

The observation exporter was also made genuinely parallel.  Eight worker processes replayed the
two 480-scenario blocks at 12,218--12,410 decisions/second, versus 2,747 decisions/second for the
earlier serial 1,920-scenario export.  A parallel smoke export was byte-identical to the serial
export.

## Closest tails

The best robust extreme tail was `geometry_binary_s1802` at 0.5%: 18 of 29 selections were
positive (62.07%), conditional mean advantage was +1.97, the map contribution CI was
[+0.0014,+0.0200], and there were no catastrophes.  It still failed the frozen minimum of 72
selections, 70% precision, and +2.0 conditional mean.

At the first activation rate large enough to meet the count gate (2%, 116 selections), the best
geometry classifier reached 53.45% precision but **-0.98 mean advantage**.  The other geometry seed
reached 50.86% precision and -1.42 mean with one new catastrophe.  The best tiny spatial model at
2% reached only 40.52% precision and -1.23 mean.  Thus this is not a near-pass hidden by one
conservative threshold: the loss tail becomes dominant as soon as coverage is useful.

## Multilevel interpretation

- **Data:** positive-label density reproduced again (17.78% on fresh validation), ruling out a
  shortage of positive examples.
- **Representation:** explicit walkable distances and the full map tensor add only modest
  discrimination.  Missing static geometry was not the main D17 failure.
- **Objective:** terminal one-intervention labels have a heavy, discontinuous loss tail.  Similar
  visible decisions can change later resident/opponent trajectories in opposite directions;
  classification precision alone does not control the magnitude of those losses.
- **Capacity:** D18 deliberately tested deployment-sized models.  It does not yet distinguish
  “the signal needs a larger teacher/student” from “the single-state label is intrinsically too
  unstable.”
- **Policy:** no D18 model is safe to put on trajectory.  The stable resident remains untouched.

## Next diagnostic

Before spending another fresh map block, measure the two remaining explanations on the already
opened D18 data:

1. train a research-capacity geometry/spatial model to estimate the representation's attainable
   cross-map precision;
2. give a diagnostic model oracle development-opponent identity, and compare it with the same
   model without identity.

This diagnostic is not deployable and cannot select a candidate.  If capacity helps, compress a
larger teacher on a new split.  If opponent identity helps, add observable opponent-history
features.  If neither helps, close single-state terminal-advantage distillation and pivot away
from this Monte Carlo target.

## Evidence

- training observation SHA-256 values:
  `b43d1c830af5845b42c5ee231b2744a921e00856a35ade1504b13cf5fee427ef`,
  `b5162947d924f36bea5e37b27e2edf854045dca39ca4e16dd12b6d136a90494e`;
- fresh-validation labels SHA-256:
  `a5b84ec974c0f4261650bb72388e3262ff7f19d4a125118e0fcb8c3d134d7e27`;
- fresh-validation observations SHA-256:
  `c18f36cc88aa68c13f84891373c74af5a94a5760fa9a6a198571ee6dafc29b8a`;
- analysis SHA-256:
  `8b1278c2c083ec6fab9ba121b5a27e472b3ac19349ea129b32c1378a29c6ae47`;
- trainer SHA-256:
  `5a7ab0ffea23c2aea558303427d950e4336580543fce4b04f02d95dd2a7dc7c8`;
- parallel exporter SHA-256:
  `ae20ba05b7112d8d921eb151a2f1625b577ff1e9b5437c6882a5010bf0a74d6b`.
