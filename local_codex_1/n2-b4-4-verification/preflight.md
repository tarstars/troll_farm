# N2 B4.4 reconstruction preflight

- Run UTC: 2026-07-30T19:09Z–19:13Z
- Code base: `f5689063ed8a555f1a1b7fde7b1cfe1edd72d8a8`
- Input: observed 9,082-record
  `/home/tarstars/prj/troll_farm/data/processed/games.jsonl`
- Leaderboard:
  `/home/tarstars/prj/troll_farm/data/raw/snapshots/20260728T110709Z-d61p-wide/leaderboard.json`

## Result

The v1 assumption that commit-`46d36098`'s tracked 8,131-game stats identified B4.4's
corpus is false.

| prefix | clean | peers | strong | weak | tracked occurrences | resident games |
|---:|---:|---:|---:|---:|---:|---:|
| 8,131 | 8,072 | 23 | 12 | 11 | 2,700 | 196 |
| 8,395 | 8,336 | 25 | 12 | 13 | 2,787 | 204 |

An exhaustive evaluation of every prefix from 8,131 through 9,082 found exactly one prefix
with `(peers, strong, weak, occurrences) = (25, 12, 13, 2787)`: record 8,395, ending at
game 896651751. Its SHA-256 is
`1f9e3855fad01f5ade6dd1ece17f0e6b20597d0b01889ef5240ee27700b68d40`.

The 8,395 reconstruction also matches the published rank ranges: strong 7–38 and
peer/weak 46–104; resident rank 43, mean roster 2.000, median roster 2.0.

## Consequence

Protocol v2 freezes all three cuts: documented-stats 8,131 for the provenance discrepancy,
unique anchor-matching 8,395 as the primary reconstruction, and current 9,082 as
sensitivity. The inferred cut will never be described as the missing immutable original.
