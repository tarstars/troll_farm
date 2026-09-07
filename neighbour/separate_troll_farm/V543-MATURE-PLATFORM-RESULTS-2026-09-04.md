# V543 mature platform result (2026-09-04)

## Outcome

V543 submission `41242929`, agent `6701731`, completed its full 160-game rollout at
**13.92 / rank 155 of 177 in Legend**. The arena room was at 100% cached and uncached
progress and no game download failed. At 2026-09-04 17:12 UTC the global leaderboard's
rank-7 entry was putibuzu at **26.99**. V543 therefore missed the requested rank by 148
places and 13.07 rating points; its strong local holdout did not transfer to the public field.

The exact published source remains `submission.rs`, 99,825 UTF-16 units, SHA-256
`922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
No weaker follow-up replaced it.

## Frozen archive

The complete archive is under
`/data/separate_troll_farm-working/platform/v543-agent6701731-final/`:

| file | bytes | SHA-256 |
|---|---:|---|
| `battle-index-agent6701731.json` | 119,202 | `23912d62261d24c93300a851cda073fa32596fb2f29126d9b396e3150b9aaf27` |
| `games-agent6701731.jsonl.gz` | 8,221,136 | `ccc45a23ea8ecc17ecb4215d8d52b4993e00c33fb830f6ad0b1786d6c713cbd1` |
| `manifest.json` | 503 | `f0402b4711cf6e0551b0f856b19a37a6d113b722d82cc630d06690680c8ba272` |

The manifest records 160 listed and 160 written games with an empty failure list.

## Rollout accounting

Seven games in the first platform batch ended at turn 1 with no bot command and score -2.
They are startup timeouts, not played losses. The remaining 153 active games produced 86 wins
and 67 losses, mean own score 335.46, mean opponent score 323.77, mean margin +11.69, and mean
wood 74.59. Including the seven timeouts gives 86 wins and 74 losses, mean own score 320.69,
mean opponent score 310.38, and mean margin +10.31.

V543's result worsened as opponent strength rose:

| opponent rating | games | wins | mean margin |
|---|---:|---:|---:|
| below 0 | 3 | 3 | +250.3 |
| 0 to below 12 | 49 | 32 | +15.1 |
| 12 to below 14 | 80 | 43 | +16.9 |
| 14 to below 16 | 17 | 8 | -13.6 |
| 16 to below 18 | 1 | 0 | -110.0 |
| 18 and above | 3 | 0 | -238.3 |

The three rating-18+ opponents were abdelmathin (-194 margin), bl4sterino (-324), and
BoatBuilder (-197). In those games V543 averaged 86.33 wood and 17.67 plants while its
opponents averaged 160.67 wood and 61.00 plants. Across all active games against opponents
rated at least 14, V543 averaged -50.29 margin, 80.86 wood against 100.29, and 21.14 plants
against 45.52. This is the same parallel-orchard economy gap identified before submission,
now measured against the mature live field.

V543 did not generally lack workers or fruit. Across all 160 records it ended with 3.79 workers
against 3.38, harvested 86.51 times against 61.28, and banked 36.50 fruit points against 20.14.
Its opponents chopped 152.74 times against 110.31. In wins V543 banked 82.84 wood; in losses it
banked only 57.96 while opponents banked 83.07. The dominant next lever is therefore additional
productive chopping and a larger tree pipeline, not more fruit harvesting by the existing axe.

## Consequence for the next iteration

V548 confirmed the allocation constraint: moving the second worker from chopping to fruit raised
ring harvests by 27.2 but lost 7.17 wood and 23.39 margin. The next queue item examines idle turns,
but it must turn otherwise idle capacity into useful planting or chopping without diverting an
already productive worker. Merely increasing the orchard cap, as V546 did, is not sufficient
because that line still fails the frozen turn-100 checkpoint.

Reproduction summaries are retained at:

- `/data/separate_troll_farm-working/analysis/2026-09-04-v543-mature-failures.json`
  (`b6dfaf1e16c9697e2ba0d67318a542f3b6c8c0d6cd4a4107e83e9f6f1c83ea02`)
- `/data/separate_troll_farm-working/analysis/2026-09-04-v543-mature-top-gap.json`
  (`7fd6e180b7ad788b4d2651957a958d671463244dfc28383ba306215c4980c495`)
- `/data/separate_troll_farm-working/analysis/2026-09-04-v543-mature-early-farms.json`
  (`98d4d0434a3175a8961000da77dfb64aea813b45959b0e664c763ca98a7fbfc5`)
