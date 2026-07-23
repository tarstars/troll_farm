# Exact field-map / opponent-model gap — result (2026-07-19)

## Question and integrity

The frozen diagnostic replayed the five consumed Stage 2A candidate maps against both the exact
resident and exact three-worker policy under all eight legacy local opponent models.  The grid is
complete: 5 maps x 2 policies x 8 models = 80 unique terminal cells.  The normalized map corpus
hash is `0fcc3007c94227971a9c87c9d5902fa9c42132bbe23d5dfc3c9a62470fee7b61`.

This experiment asks whether the Stage 2A failure came from map distribution, opponent behavior,
or both.  It does not reuse the local grid as candidate qualification evidence.

## Results at four levels

### Worker-funding mechanism

The field candidate stopped at two workers against Escdemon and laconic.  On those exact two maps,
the same three-worker controller reached worker three in 15/16 legacy-model simulations.  Across
all five exact maps it reached three in 39/40 cells.  This passes the frozen opponent/model-driven
discriminator and rejects a primarily map-driven funding explanation.

When the field candidate did fund worker three, its successful turns were 77, 98, and 84.  The
corresponding legacy-model medians were 78, 103, and 78, giving residuals -1, -5, and +6 turns.
Thus the local controller reproduces training timing once the funding path survives; it does not
reproduce the interactions that determine whether that path survives.

### Complete-policy value on field maps

Even within the legacy local domain, worker three is not beneficial on these maps.  Relative to
the resident across 40 paired cells, the three-worker policy changes:

| Measure | Three-worker minus resident |
|---|---:|
| own score | -11.250 |
| opponent score | +17.725 |
| margin | -28.975 |
| wood | -6.450 |

Only `mybot` has a positive mean margin delta (+13.6).  The other seven model-family deltas range
from -22.6 to -51.0.  The official map sample therefore also removes the payoff that made the
Silver architecture look attractive on generated maps.

### Field calibration

Actual own score lies inside the eight-model local range on only 2/5 maps; actual margin lies
inside on only 1/5.  The most severe misses are opponent-side compounding: actual margins against
delineate and wala are -245 and -265, while the local ranges bottom at +57 and -81 respectively.
Against Escdemon and laconic, actual own scores 44 and 55 fall below local minima 56 and 70.

Both predeclared 4/5 calibration gates fail.  The old generated-map/eight-model zoo is therefore
retired as a field-transfer or promotion gate.  It remains useful only for implementation parity,
mechanism isolation, and deliberately local causal tests.

### Strategic abstraction

The direct Silver transplant fails for two independent reasons:

1. real opponent interactions can break its funding path even on maps where almost every old
   model funds worker three; and
2. on the exact field maps, its continuation loses locally even when worker three is funded.

The next controller must be evaluated closed-loop against field agents on controlled platform
maps.  Another parameter sweep against the legacy zoo cannot supply promotion evidence.

## Verdict and next experiment

The diagnostic passes integrity and decisively retires the legacy transfer gate.  Before creating
another policy, establish whether `TestSession/play` supports deterministic common-seed A/B games.
The IDE client feeds a replay's `refereeInput` back through `multi.gameOptions`; Troll Farm exposes
that input as `seed=<signed int64>`.  A frozen A/A replay test is the next discriminator.

Artifacts:

- `norxondor-field-map-model-gap-protocol-2026-07-19.md`;
- `norxondor-three-worker-stage2a-field-5.maps`;
- `norxondor-three-worker-stage2a-field-5-observed.json`;
- `norxondor-field-map-gap-5x2x8.tsv`;
- `norxondor-field-map-model-gap-2026-07-19.json`.
