# V550 V425 opponent measurement result

## Outcome

V425 can now run as a separately measured thirteenth opponent family, without changing the
frozen 12-family development gate. Its fixed training ladder is strongly consistent with the
archived public R1FA profile, but its full economy is not: against V468 it scored and banked less
than half the public R1FA aggregates and lost all 16 games. V425 is therefore useful only as an
optional adversarial diagnostic. It is not a validated substitute for R1FA and was not added to
the selector.

This was measurement V550, not a bot candidate. `bot.rs`, `submission.rs`, V543's platform agent,
the V468 baseline, the eight development maps, and `OPPONENTS = 12` in the canonical panel runner
were unchanged. Nothing was submitted.

## Instrumentation and validation

`build_v550_v425_measurement_runner.py` renders a separate runner from the frozen
`candidate_compare_panel_runner.rs`. It adds opponent index 12, a V425 view adapter, opponent
command capture, final opponent worker count, and opponent legality fields. V425's source used
hard-coded `crate::candidate::` paths, so the builder also renders a measurement-only copy whose
only source change is replacing that root namespace with `crate::r1fa_v425::`. Five focused
pytest tests cover both renderers, output isolation, profiling, and rejection of unequal arms.

The compiled runner used exact V468 in both arms on seeds 9,941,000 through 9,941,007, both seats
and all 13 families. All 208 paired rows agreed in own and opponent scores, margins, wood,
checkpoint scores, workers, legality, and both command streams. The original 12-family
runner remains byte-for-byte unchanged at SHA-256
`9ad74518c8692da001e90a7cf259d8713aa96b575e138c3d5ce6de239c3c5cff`.

## Twelve-family and thirteen-family readings

The 192 original-family rows reproduce the frozen V468 development reading. Adding V425 changes
only the diagnostic aggregate:

| measure | original 12 families | all 13 families | V468 versus V425 only |
|---|---:|---:|---:|
| games | 192 | 208 | 16 |
| own score at turn 100 | 93.01 | 92.53 | 86.75 |
| own score at turn 200 | 176.18 | 175.49 | 167.19 |
| final own score | 247.25 | 245.26 | 221.38 |
| final opponent score | 108.22 | 109.27 | 121.88 |
| final margin | +139.03 | +135.99 | +99.50 |
| own wood | 45.02 | 44.73 | 41.19 |
| opponent wood | 18.02 | 18.59 | 25.44 |
| W/T/L | 177/3/12 | 193/3/12 | 16/0/0 |

V425 is more suppressive than the pooled local average: V468's score falls by 25.88 and its
margin by 39.53 in the V425 subset. It is not a stronger match opponent in the outcome sense,
however; V468 wins every game. The result supports retaining V425 for occasional mechanism
checks, but not weighting every development decision toward it.

## Comparison with public R1FA

The archived R1FA profile covers 133 platform games. Those games do not expose the executable or
the same local states, maps, and opponents, so aggregate similarity can corroborate a
reconstruction but cannot establish command equivalence.

The training signature is corroborated. V425 issued the same ordered ladder in every game:
`2/2/1/1`, then `2/2/1/2`, then `2/4/0/3` when the third hire was affordable. It made 2.31
training attempts per game versus public R1FA's 2.71, finished with 3.31 workers versus 3.67, and
issued no illegal commands. Five of 16 games completed the fourth worker; the median first turns
for the three specifications were 2.5, 72, and 213.

The wider economy diverges too much to validate the full proxy:

| measure | local V425 | public R1FA | local/public |
|---|---:|---:|---:|
| final score | 121.88 | 248.16 | 0.49 |
| final wood | 25.44 | 60.15 | 0.42 |
| MOVE/game | 495.94 | 437.8 | 1.13 |
| CHOP/game | 66.94 | 144.4 | 0.46 |
| DROP/game | 59.13 | 77.4 | 0.76 |
| HARVEST/game | 40.69 | 64.8 | 0.63 |
| MINE/game | 9.13 | 20.7 | 0.44 |
| PICK/game | 2.94 | 16.0 | 0.18 |
| PLANT/game | 7.00 | 27.8 | 0.25 |
| TRAIN/game | 2.31 | 2.7 | 0.86 |

Seven score, wood, or command aggregates lie outside an explicit 0.65--1.35 corroboration band.
The large shortfall is the same structural behavior relevant to the ladder target: V425 moves
more while planting, harvesting, and chopping far less. The defensible conclusion is
"training-signature reconstruction", not "local R1FA". The public R1FA executable would be
required for literal same-state validation.

## Gate and platform verdict

The standard 12-family gate remains the only selector, and its V468 identity reading was
unchanged. V550 introduced no candidate improvement, so no fresh-map holdout, duel, packaging
audit, or platform submission was opened. The optional measurement runner is retained for future
diagnostics under the `candidate_compare_v425_measurement` Cargo target.

Evidence:

- 208-row panel SHA-256: `909044e6e37f3c9ffce5ffea094f886d85124a0152a5e537417cfa7b89b6696c`
- analysis JSON SHA-256: `797c55383ff42a24a0cf8f1b187fa6c868e8e63fb5cbe3e45ea3d744605f0a46`
- measurement runner source SHA-256: `d35fc46faea154ba5f12141ac8acd9875d0215d7be06bb4ea9e868d150eb521e`
- measurement V425 module SHA-256: `2356440bbc84bb9c9af81560cef3b140f54ca98314da87ac626aac6222483a40`
- compiled runner SHA-256: `067eb65a229f6aabaf9e01b3b0fb5d93d7080a4f23ab5fd531d1cea1ed80f362`
