# D19 residual capacity/identity diagnostic — development protocol (2026-07-20)

## Purpose

D17 and D18 show stable positive-label density but inadequate precision from deployment-sized
students.  D19 distinguishes two explanations before consuming another map block:

1. the visible state contains the signal, but the 4.6--5.4K-parameter students lack capacity;
2. terminal advantage depends strongly on hidden opponent policy, so a single visible snapshot is
   ambiguous without opponent-history information.

This is a research diagnostic on already-open data.  Its models are deliberately nondeployable
and cannot authorize a candidate, source integration, submission, Arena activity, or even a
locked test by themselves.

## Frozen data and models

Use D18's unchanged 28,800-row training set and 5,760-row fresh-validation set.  Do not generate
or open any other label block.  Train binary positive-label classifiers with seeds 1901 and 1902:

- large geometry MLP: 177 inputs, hidden widths 128/64/32;
- the same geometry MLP plus a six-way oracle development-opponent one-hot;
- large spatial model: width-12 dilation-1/2/4 encoder, active/mean/max context, hidden widths
  64/32, and 13 action-plane outputs;
- the same spatial model plus the oracle opponent one-hot.

Use the D17/D18 weighted binary objective, 80 geometry epochs, 30 spatial epochs, and selection
rates 0.5%, 1%, 2%, 4%, and 8%.  Opponent identity is the only new information in oracle models.
It is intentionally unavailable to a live generic policy; it measures hidden-policy dependence.

Geometry extraction is sharded across 12 forked workers but must reproduce the frozen D18 feature
schema exactly.

## Frozen interpretation rules

- **Capacity signal:** a non-oracle large model is useful only if a rate of at least 2% reaches at
  least 65% precision, positive conditional mean advantage, positive map-clustered CI lower bound,
  no new catastrophe, positive coverage on 12 maps/four opponents/both roles, and at least 72
  selections.
- **Identity signal:** at a matched architecture, seed, and selection rate of at least 2%, an
  oracle model must improve precision by at least 10 percentage points and conditional mean by at
  least +1.0 over its non-oracle counterpart, while retaining a positive map-CI lower bound and no
  catastrophe.
- If capacity passes without identity, freeze a new large-teacher/compression experiment.
- If identity passes, freeze an observable opponent-history representation experiment.
- If neither passes, close single-state terminal-advantage distillation and pivot away from this
  Monte Carlo target.

No threshold is tuned outside the five frozen rates, and no result from this already-open
validation block is a held-out policy estimate.

## Outputs

- `d19-resident-residual-capacity-identity-diagnostic-2026-07-20.json`;
- `d19-resident-residual-capacity-identity-diagnostic-result-2026-07-20.md`.
