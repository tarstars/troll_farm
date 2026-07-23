# D101a production/suppression archaeology result

Date: 2026-07-22  
Decision: **pass the frozen mechanism gate; open a complete role-persistent scheduler preflight.**

## Reproducibility and integrity

- Frozen protocol: `aaede8638f7a0e7c0004351c182091358c5ec7c78e381969c36883fd2900e8b6`
- Analyzer: `9ffb10092180fa8a9ac848033650dc5d1c8fe95f83bff3a0aad9dc0dd37d4d30`
- One-process result: `c7fe5d2ab1685b23aad9288f3244c6fbd30cd80300cf8ed9480d7cfb205f94c2`
- Twenty-process result: `c7fe5d2ab1685b23aad9288f3244c6fbd30cd80300cf8ed9480d7cfb205f94c2`

The outputs are byte-identical. All 365 fixed actor/game occurrences reconstruct: 200 top-20
source appearances (ten for each agent), 50 rank-1--5, 150 rank-6--20, and 165 resident. There are
no sealed rows, duplicate occurrences, turn mismatches, unknown state diffs, unresolved crop
births, unassigned cargo deltas, missing worker ordinals, or spawn/TRAIN disagreements.

Two births exposed a legacy command-attribution edge case: an earlier positional `WAIT` shadowed
a later explicit `PLANT <unit-id> <kind>`. In both cases the explicit unit, cell, kind, and observed
state birth identify the creator uniquely. D101 repairs those two records rather than weakening
the frozen zero-unknown gate; all other events and lineages match the independent reconstructor
exactly.

## Frozen gate

All five rank-1--5 agents meet all four prospective conditions: crop creation in at least 80% of
games, opponent-crop suppression in at least 50%, both in at least 40%, and distinct-worker role
separation in at least 30% of multiworker games. The requirement was three of five, so the
architecture warrant passes `5/5`.

## What actually distinguishes the resident

| Cohort | Own crop creation | Own crop reaping | Creation + suppression | Strict producer/suppressor split | Temporal overlap | Mean final workers |
|---|---:|---:|---:|---:|---:|---:|
| Rank 1--3 | 100.0% | 93.3% | 90.0% | 83.3% | 80.0% | 3.50 |
| Rank 1--5 | 100.0% | 80.0% | 84.0% | 64.0% | 58.0% | 3.40 |
| Rank 6--20 | 99.3% | 83.3% | 92.0% | 76.5% | 74.7% | 2.61 |
| Resident | 100.0% | 10.3% | 88.5% | 9.7% | 9.1% | 2.00 |

The resident already plants and suppresses. Adding either behavior is therefore the wrong
abstraction. Its missing behavior is **keeping created crops productive while suppression is in
progress**.

At generation level, rank 1--3 create 1,254 crops and later reap 303 distinct generations
(`24.16%`); the resident creates 1,811 and reaps only 17 (`0.94%`). Per game this is about 41.8
created / 10.1 reaped generations for rank 1--3 versus 11.0 / 0.10 for the resident. Resident
crops are overwhelmingly an eventual wood surface, not a sustained renewable supply.

Suppression strength is not the deficit. The resident contacts 41.6% of opponent-created crop
generations with median latency 10; rank 1--3 contact 36.0% with median latency 17. The allocation
is inverted instead: 1,102 successful top-three suppression chops include only 11 at workforce
one and 232 at workforce two, with 859 (`78.0%`) after reaching workforce three. Every one of the
resident's 7,390 suppression chops occurs at workforce two.

The individual policies show multiple implementations of the same invariant:

- rank one `delineate` preserves a dominant starter production loop and commonly makes worker one
  the suppressor; all ten games are strict role-separated;
- rank three `wala` is the cleanest target architecture: workers zero and one perform the own
  loop, workers two and three perform suppression; seven of ten games are strict role-separated;
- rank four `Escdemon` is a useful counterexample: it remains a two-worker suppression-heavy bot
  and reaps own crops in only two of ten games. Thus replay rank is not a causal estimate and no
  single worker count should be copied blindly.

## Decision

D102 must test a complete scheduler whose invariant is production persistence, not a crop target
bonus. A designated producer (or foundation pair) must continue harvesting and replanting owned
crops, capitalization must train the later worker, and suppression must be assigned without
stealing that renewable loop. The first causal preflight should compare bounded delineate-like and
wala-like role layouts with exact current-controller fallback on fresh simulator maps.

Do not fit a D101 outcome selector, copy one top bot verbatim, infer causality from margins, or
submit from this observational result. No platform or resident action is authorized by D101.
