# Orchard ablation: fresh-queue opponent-standardized comparison

## Identity and headline correction

- orchard: `6592131` / `41086057`, score 23.56, rank 32/137;
- no orchard: `6592097` / `41085842`, score 23.27, rank 34/137;
- fresh difference: +0.29 score and two rank places in favor of orchard.

The earlier rank-12 orchard row is not a clean control: the exact same source's fresh restore landed at rank 32. The apparent rank-12 to rank-34 drop therefore mixes source, reset, matchmaking and queue effects.

## Raw outcomes

| metric | orchard | no orchard | orchard - no orchard |
|---|---:|---:|---:|
| games | 162.0000 | 160.0000 | +2.0000 |
| win rate | 0.5741 | 0.5687 | +0.0053 |
| mean own score | 183.8272 | 189.4313 | -5.6041 |
| mean opponent score | 174.0185 | 178.8625 | -4.8440 |
| mean margin | 9.8086 | 10.5687 | -0.7601 |
| catastrophe rate | 0.1111 | 0.1000 | +0.0111 |
| negative-margin mass | 5569.0000 | 5441.0000 | +128.0000 |

Raw outcomes favor no-orchard on wins and tails. They do not explain the ladder score, which is not a direct transform of terminal margin and is sensitive to opponent mixture.

## Common-opponent standardization

Common exact opponents: 35; opponent-set Jaccard 0.427.

| weighting | win-rate diff | own-score diff | opponent-score diff | margin diff | catastrophe-rate diff |
|---|---:|---:|---:|---:|---:|
| equal_opponent | +0.0007 | +5.958 | +13.476 | -7.518 | +0.0099 |
| minimum_count | -0.0112 | -0.042 | -2.252 | +2.210 | +0.0130 |
| pooled_count | +0.0163 | +0.619 | -5.603 | +6.222 | +0.0094 |

Equal-opponent cluster bootstrap (orchard minus no-orchard):

| metric | lower 95% | median | upper 95% | P(diff <= 0) |
|---|---:|---:|---:|---:|
| win_rate | -0.1345 | +0.0013 | +0.1332 | 0.4925 |
| our_score | -14.2262 | +5.8021 | +27.4969 | 0.2910 |
| opponent_score | -22.2152 | +12.9083 | +52.7053 | 0.2428 |
| margin | -40.4833 | -7.4058 | +24.3056 | 0.6744 |
| catastrophe_rate | -0.0594 | +0.0101 | +0.0784 | 0.3856 |

## Interpretation boundary

This is an observational comparison. It can show whether opponent composition explains the raw result, but it cannot identify orchard value on identical map/opponent/seat states. A replay-level mechanism join and paired local continuation are required for that.

