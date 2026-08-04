# Orchard/no-orchard overnight live cycle

Completed UTC: 2026-08-04T03:42:32Z

Eight fresh submissions alternated no-orchard then orchard four times. Every row is a
one-hour, identity-clean checkpoint with a complete sanitized replay package.

| Leg | Variant | Agent | Submission | Games | Score | Rank | W/T/L | Mean margin | Catastrophes | Negative mass |
|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | no-orchard | 6592330 | 41086822 | 160 | 24.0 | 28/137 | 87/7/66 | 20.256 | 11 | 4144 |
| 2 | orchard | 6592362 | 41087022 | 160 | 25.6 | 10/137 | 93/2/65 | -1.125 | 21 | 6435 |
| 3 | no-orchard | 6592383 | 41087215 | 160 | 20.44 | 54/137 | 92/1/67 | 9.412 | 22 | 6151 |
| 4 | orchard | 6592447 | 41087483 | 160 | 22.47 | 37/137 | 98/1/61 | 3.025 | 27 | 7175 |
| 5 | no-orchard | 6592495 | 41087642 | 160 | 24.18 | 24/137 | 82/2/76 | -1.581 | 21 | 6195 |
| 6 | orchard | 6592529 | 41087744 | 160 | 23.82 | 27/137 | 91/3/66 | 5.375 | 24 | 5643 |
| 7 | no-orchard | 6592612 | 41087830 | 160 | 23.81 | 27/137 | 82/7/71 | 4.844 | 15 | 5287 |
| 8 | orchard | 6592744 | 41087983 | 160 | 22.88 | 32/137 | 99/2/59 | 17.238 | 19 | 4703 |

## Repeated live comparison

- no-orchard: score mean 23.108, median 23.905; mean game margin across leg means 8.233.
- orchard: score mean 23.692, median 23.350; mean game margin across leg means 6.128.
- Orchard minus no-orchard paired score deltas: [1.6000000000000014, 2.0299999999999976, -0.35999999999999943, -0.9299999999999997]; mean 0.585, median 0.620.

Opponent queues are not paired game-for-game, so this is repeated live evidence rather
than a clean causal estimate. No endpoint fallback or automatic submission retry was used.
The sequence ends with orchard active.
