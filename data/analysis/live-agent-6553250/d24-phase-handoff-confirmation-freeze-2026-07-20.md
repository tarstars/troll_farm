# D24 phase-handoff confirmation freeze (2026-07-20)

The complete discovery grid passed integrity: 23,040/23,040 rows, 3,840/3,840 common
seed/seat/turn/opponent scenarios, no duplicate or missing branch, and identical root fields across
all continuations.

Exactly two of twenty option/turn combinations pass every frozen discovery gate:

| Option | Cut | Seed-clustered margin | 95% interval | Own score | Worst opponent | Catastrophe rate control → option | Negative mass ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| `private2` | 75 | +25.973 | [+7.609, +44.337] | +64.803 | +5.417 | 17.188% → 12.500% | 0.858 |
| `ownership2` | 75 | **+28.325** | **[+10.327, +46.323]** | **+67.800** | **+8.192** | **17.188% → 12.396%** | **0.846** |

The predeclared lexicographic rule first maximizes worst-opponent mean.  It therefore freezes:

- option: **`ownership2`**;
- decision turn: **75**;
- confirmation seeds: **50,060--50,119**;
- both seats and all eight opponents;
- only the exact warmed resident control and `ownership2` alternative.

No other option or cut may use the confirmation block.  All original discovery gates apply, and
the seed-clustered margin-delta 95% lower bound must be above zero.

Frozen evidence hashes:

- discovery TSV SHA-256:
  `6370e359354cd48d1c81d38ad28844dc2521a8678a97e4b76c28632a275edbba`;
- discovery JSON SHA-256:
  `eaff1c729efc52d26c2a0ca0560c49eb2bbaafcf35a9ea211bc07ce24fe96b98`.

This freeze authorizes one local confirmation run.  It does not authorize candidate packaging,
submission, or Arena activity.
