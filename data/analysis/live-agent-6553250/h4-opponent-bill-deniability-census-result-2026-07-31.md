# H4 opponent worker-three bill deniability census — result

Verdict: **`NO_MATERIAL_DENIABLE_BILL`**.

The B3.1 timing signature is real, and every third-worker bill requires post-start supply.
But ordinary reachability radically overstates actionable denial. Seventy-three external
acquisition batches are individually load-bearing after prior worker-two payments are
accounted for; 43 are non-deniable iron, while only one of 30 load-bearing fruit batches
even has a resident unit co-located—and that unit cannot legally harvest. Consequently,
zero of 17 scale-linked catastrophes has a strictly proven one-command block.

## Population and timing

The analyzer reads only the 200 exact resident games named by the accepted D159 artifact.
All 200 raw games and trajectories exist at the canonical logical data root, decode with
zero unknown updates, and match the frozen identity/source/manifests.

- 20/200 games are catastrophes (resident terminal margin ≤ −100).
- 77/200 contain a successful opponent third-worker TRAIN.
- 17/20 catastrophes contain that TRAIN strictly before the permanent resident score
  crossover: **85%**, independently matching B3.1's 84%.
- Those 17 games cover 12 exact opponent identities and both resident seats (9/8).
- Scaling leads the crossover by median **70 turns**, range **13–125**.

This confirms a warning signal, but the signal becomes observable only after the TRAIN
bill has already been paid. H4 therefore needs an earlier load-bearing source, not merely
the scaling event.

## What paid the bills

The 17 exact third-worker bills contain 487 charged units:

| Item | Total bill | Median/game | Games with mandatory post-start contribution | Minimum post-start units in bill | Zero-slack payments |
|---|---:|---:|---:|---:|---:|
| PLUM | 108 | 6 | 17/17 | 81 | 8/17 |
| LEMON | 213 | 11 | 17/17 | 169 | 11/17 |
| APPLE | 42 | 2 | 6/17 | 11 | 6/17 |
| IRON | 124 | 6 | 13/17 | 68 | 10/17 |

At least one post-start item contribution is necessary in **17/17 games** after bounding
what starting stock can remain following the earlier worker-two payment. LEMON is the
largest bottleneck.

IRON is important but mechanically non-deniable: an iron terrain cell has no stock to
deplete, and each legal MINE independently creates up to
`min(chopPower, freeCapacity)` iron. Starting inventory is likewise unreachable. Thus 68
minimum post-start IRON units across 13 games are not a contestable resource pool.

## Why reachability does not become denial

The exact provenance funnel is:

| Stage | Batches |
|---|---:|
| External HARVEST/MINE acquisitions before the third TRAIN | 455 |
| Definitely deposited without carry-provenance ambiguity | 407 |
| Fruit batches passing loose prior BFS/ETA reachability | 371 |
| Individual batches with positive minimum bill contribution | 73 |
| Of those: non-deniable IRON / fruit | 43 / 30 |
| Mandatory fruit batches with resident co-located | 1 |
| Mandatory fruit batches with a legal same-turn resident HARVEST | **0** |
| Mandatory fruit batches with a prior co-located lethal CHOP | **0** |
| Strict one-action causal-block candidates | **0** |

The loose reachability bound fires in **17/17 games**, so it would misleadingly call the
surface universal. Earlier TRAIN payments do make 73 individual batches necessary under
the conservative fungible-bank bounds. But most are mechanically non-deniable IRON, and
the remaining fruit is not where a resident action is available at the required time.

The strict gate credits only:

- an already-positioned, referee-order-valid HARVEST that steals enough necessary fruit
  to make the original TRAIN unaffordable; or
- an already-positioned lethal CHOP that removes such a necessary source generation.

It credits no hypothetical MOVE prefix and no terminal benefit. Of 30 mandatory fruit
batches, only one has any resident unit on the source cell at acquisition; that unit
fails the harvest legality/capacity check. No earlier resident unit can kill a mandatory
source in one CHOP. The strict funnel therefore ends at 0/17 games, 0 identities, 0 seats.

## Decision

Support gates pass, but all four action-materiality gates fail. Close H4 without a
denial scorer, timed branch, causal panel, source edit, candidate, or Arena cycle.

This does not say opponent scaling is harmless, nor that no unknowable token history
could be delayed. It says the recorded replays do not expose a material, individually
load-bearing, one-command bill source. The B3.1 post-TRAIN trigger is too late, generic
Phase-21 opponent-crop scoring remains closed, and broad reachability is not causal
evidence.

Analyzer validation:

- `python3 -m py_compile cgauto/h4_opponent_bill_deniability_census.py`
- `python3 cgauto/h4_opponent_bill_deniability_census.py --self-test`
  → `self-test: ok`
- `python3 -m pytest -q tests/test_h4_opponent_bill_deniability_census.py`
  → `8 passed`
- independent repeat output is byte-identical at SHA-256
  `bf7ebfa6e210f636b70d668301e326a33133ce49bb42c14e62521e29423626f8`.

No raw/processed data, simulator/referee, resident source, map/range, game, policy,
candidate, submission, or Arena state changed.
