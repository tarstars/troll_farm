# H3′ numeric-pressure contact-causality result — 2026-07-31

## Verdict

`TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY`

Opponent third-worker scaling precedes a material decline in the resident's
opponent-crop first-contact hazard, including in a window that ends before permanent
loss. This is observational evidence for a pressure-linked timing signal, not proof
that conditioning a policy on workforce changes has value. It authorizes only a
separate three-arm preflight with conditioned, identical always-on, and unchanged
control arms.

## Integrity and population

All integrity gates pass. The frozen D159 manifest/result/source hashes are exact; all
200 unique named raw games and trajectories are present; every game decodes with zero
unknown updates; the resident identity and seat are exact; no outside game is read; and
two complete runs are byte-identical.

Successful TRAIN transitions identify 77 scaled games and 123 games with no successful
opponent third-worker TRAIN. Seventy scaled games have complete 50-turn pre/post
windows. Nearest matching with replacement finds a same-seat, sufficiently long
no-scale control for all 70, spanning 29 exact scaled-opponent identities and both
resident seats. The pre-loss subset retains 69 pairs, 28 identities, and both seats.

## Descriptive coverage

Across whole games, the resident first contacts:

- 814/2,301 opponent crops in scaled games: 35.38%;
- 1,131/2,368 crops in no-scale games: 47.76%;
- difference: −12.3859 percentage points;
- game-cluster 95% interval: `[−18.8284,−5.8550]` percentage points
  (10,000 replicates, seed 20260731).

The exact D159 no-scale baseline therefore updates the older 41.3% descriptive figure,
while preserving and strengthening the direction of the lead. Scaled games also have a
far lower descriptive mean resident margin (−46.23 versus +31.65), which is why the
temporal pre-loss test is decisive and terminal association is not treated as causal.

## Matched temporal ordering

Matching uses only frozen pregame/map fields. All eight post-match standardized mean
differences are at most 0.1806 in absolute value, below the frozen 0.25 gate. There are
45 unique controls and maximum reuse is five.

For the complete 50-turn windows:

- scaled hazard falls from 13.489 to 8.057 contacts/1,000 at-risk crop-turns;
- matched-control hazard is nearly flat, 16.940 to 16.722/1,000;
- scaled post/pre ratio: 0.5977;
- control post/pre ratio: 0.9862;
- difference-in-differences hazard ratio: **0.6061**;
- matched-pair bootstrap 95% interval: **`[0.4100,0.8954]`**.

For the 69 pairs whose entire 20-turn post window precedes permanent negative
crossover:

- scaled hazard falls from 12.108 to 6.100/1,000;
- matched-control hazard is nearly flat, 19.169 to 19.048/1,000;
- scaled post/pre ratio: 0.5068;
- control post/pre ratio: 0.9932;
- difference-in-differences hazard ratio: **0.5103**;
- matched-pair bootstrap 95% interval: **`[0.2928,0.8407]`**.

Every aggregate event/risk cell is nonzero. Both DiD point estimates clear the frozen
0.80 gate and both upper confidence bounds are below one. The effect therefore appears
after the TRAIN event even before the resident becomes permanently behind; it is not
explained solely by already-lost late turns.

## Decision boundary

The event remains observational. A third-worker TRAIN can proxy a broader opponent
policy, resource state, or hidden trajectory difference; pregame matching cannot remove
that confounding. Do not implement a conditional bonus, reopen exact 1:1
opponent-crop scoring, infer intervention value, create a candidate, or touch Arena.

The only successor justified by H3′ is a newly frozen value preflight with three arms:

1. a workforce-pressure-conditioned change;
2. the identical change always on;
3. an unchanged control.

The conditioned arm must beat both alternatives under frozen breadth, integrity, and
value gates before the conditioning can be called load-bearing.

## Validation and boundaries

- `python3 -m py_compile cgauto/h3_numeric_pressure_contact_causality.py tests/test_h3_numeric_pressure_contact_causality.py`
- `python3 cgauto/h3_numeric_pressure_contact_causality.py self-test` →
  `self-test: ok`
- `python3 -m pytest -q tests/test_h3_numeric_pressure_contact_causality.py` →
  `7 passed`
- two complete 200-game outputs are byte-identical at SHA-256
  `ebc7924e5f0f3670576cdf19372fa4ec1d39de02a1241dcf59e4e51b5bd472b3`
- sacred source SHA-256 remains
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

No raw/processed replay, policy source, simulator/referee, map/range, game, candidate,
submission, or Arena state changed.
