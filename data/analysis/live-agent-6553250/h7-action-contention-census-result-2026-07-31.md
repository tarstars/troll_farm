# H7′ action-contention census result — 2026-07-31

## Verdict

`NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE`

Cross-player action contention is mechanically real and common, but it is not a
strong-opponent discriminator in the exact 200-game D159 resident panel. No controller,
causal panel, candidate, or Arena action is justified.

## Integrity and population

All gates pass: the frozen manifest/result/source hashes are exact, all 200 unique named
raw games and trajectories are present, all 200 decode with zero unknown updates, every
accepted simultaneous-action transition agrees with pre/post carry and plant state, no
outside ID is read, and both comparison cohorts cover both resident seats. The panel has
36 rank-1–20 games over 18 opponent identities, 82 rank-21–40 games over 18 identities,
and 82 rank-41+ games over 28 identities.

## What happens

Across 53,427 turns:

- 6,836 tree-turns have one unit from each player co-located;
- 3,662 turns contain legal dual CHOP on the same tree;
- 558 of those are combined-only kills: neither side is lethal alone;
- 598 duplicated wood units are created by the last-wood referee rule;
- only 3 legal dual-HARVEST turns occur, creating 2 duplicated fruits;
- 13 exact resident MOVE targets are removed by a lethal opponent CHOP and 28 are
  depleted to zero fruit by an opponent HARVEST;
- in the reverse direction, 276 opponent MOVE targets are removed and 15 depleted by
  resident actions;
- both players name the same extant tree in MOVE commands on 518 turns.

The duplicated-item total has a direct score-equivalent ceiling of
`2 fruit + 4 × 598 wood = 2,394`, or 11.97 per panel game. That is total extra shared
resource created by the simultaneous referee rule—not opponent-attributed material,
banked score, causal margin, or an avoidable resident loss.

The delicate cases were spot-checked against their raw commands and decoded states. For
example, game `896350365` turn 226 has both players legally HARVEST one APPLE from the
same cell and both receive one; the same turn has two power-2 choppers jointly kill a
3-health size-1 BANANA and both receive one wood. The analyzer reproduces both
duplications exactly.

## Why the strong-agent premise fails

Primary events occur in 180/200 games and cover 61 identities and both seats. They are
nearly saturated in both comparison cohorts:

- rank 1–20: 35/36 games, 97.22%;
- rank 41+: 75/82 games, 91.46%;
- difference: +5.7588 percentage points;
- opponent-identity-cluster bootstrap 95% interval:
  `[−1.6353,+14.4928]` percentage points (10,000 replicates, seed 20260731).

The frozen +10-point uplift gate fails and the cluster interval crosses zero. Frequency
also points away from a strong-agent signature: primary events occur at 47.87 per 1,000
turns in the strong cohort versus 78.93 in the comparator cohort. Strong games have a
smaller duplication ceiling (11.22 per game) than comparator games (15.12).

Event games have a lower descriptive mean resident margin (−4.14) than non-event games
(+53.90), but this replay-conditioned association cannot distinguish contention causing
losses from close/losing games creating more shared-target actions. It is not a causal
value estimate.

## Frozen gates

Passed:

- at least 20 primary-event games;
- at least 8 event opponent identities;
- both resident seats;
- at least one exact mechanical consequence.

Failed:

- strong minus comparator prevalence is not at least 10 percentage points;
- the opponent-identity-cluster bootstrap lower bound is not above zero.

Therefore H7′ closes at diagnosis. Do not describe body-blocking as possible, treat
ubiquitous dual chopping as a learned strong-agent tactic, tune opponent-crop targeting,
or build an action-contention controller from this census.

## Validation and boundaries

- `python3 -m py_compile cgauto/h7_action_contention_census.py tests/test_h7_action_contention_census.py`
- `python3 cgauto/h7_action_contention_census.py self-test` → `self-test: ok`
- `python3 -m pytest -q tests/test_h7_action_contention_census.py` → `7 passed`
- two complete 200-game runs compare byte-identical
- sacred source SHA-256 remains
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

No raw/processed replay, source, simulator/referee, map/range, game, candidate,
submission, or Arena state changed.
