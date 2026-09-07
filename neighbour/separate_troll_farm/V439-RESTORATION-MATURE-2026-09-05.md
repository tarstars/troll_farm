# V439 restoration: confirmed rank 28, not seventh

Submission **41245746**, agent **6704418**, completed at **rank 28/177 in Legend**, rating
**23.43**. Both progress indicators reached 100%, all 160 exact-submission games completed,
and no games were pending. The monitor observed this from 08:45:32 through 08:50:55 UTC and
exited with the confirmed non-top-seven verdict. The requested goal remains unachieved.

This is a real improvement from V543's mature rank 155/rating 13.92, but not proof of a
reproducible 127-place gain across arbitrary resubmissions. The restoration was selected by
the separately frozen paired screen in `BASELINE-RESTORATION-RESULTS-2026-09-05.md`.

All 160 replays were archived without failures and checked against battle records containing
the exact agent/submission identity pair. They cover 55 distinct opponent agents. Official
ranks give **95 W / 0 D / 65 L (95 match points)**. There were **zero detected own or opponent
deployment failures**, no replay decoding failures, and no excluded games in the primary result.
Mean scores were 207.41 versus 200.06, margin +7.35; mean banked wood 45.13 versus 46.04.

| Replay-recorded opponent rating | Games | W/D/L | Own / opponent score | Mean margin |
|---|---:|---|---|---:|
| Below 18 | 20 | 13/0/7 | 235.85 / 174.05 | +61.80 |
| 18 to below 22 | 56 | 39/0/17 | 195.52 / 181.59 | +13.93 |
| 22 to below 25 | 83 | 42/0/41 | 209.11 / 219.84 | -10.73 |
| 25 and above | 1 | 1/0/0 | 164.00 / 113.00 | +51.00 |

The sole 25+ game was against gaha/6481397, not a broad target-rank sample. Seat 0 was 52/0/31
in 83 games; seat 1 was 43/0/34 in 77. Adaptive ladder sampling is not a paired experiment,
and the ratings above are those recorded in replay metadata, not an assumed historical rating.
Full opponent-specific scores, outcomes, margins and failures are in `rollout-analysis.json`.

Against the 22–25 band, V439 issued 170.52 CHOP commands and banked 46.41 wood per game;
opponents issued 115.25 and banked 51.18. V439 planted 12.18 times versus 32.06 and ended
with two workers versus 2.35. These are mechanism diagnostics, not instructions to maximize
plant count or hire indiscriminately. Denial CHOPs can matter without banking wood, and earlier
experiments showed that greater own score/wood/workforce can still lose more games.

Live compact source remains exactly
`7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`, 96,985 UTF-16 units.
There was no additional publication. The next capability is sequence-level planning using the
independently tested foundation in `PLANNING-MODEL-RESULTS-2026-09-05.md`; it has not yet improved
or replaced this live controller.

Evidence root: `/data/separate_troll_farm-working/baseline-restoration/2026-09-05/`.
Monitor readings and the complete archive are under `deployment/`; analysis is at the root.
Archive hashes:

- `battle-index-agent6704418.json`: `b124d998fc2d93d4c7d8ebcfd3ca4813506c7ed5618ddca1f33203de51c233cc`
- `games-agent6704418.jsonl.gz`: `2f5a05a8a132fca7edcf9eafbea6f9d8406b8d866753b2f22b0995cb5759c0d5`
