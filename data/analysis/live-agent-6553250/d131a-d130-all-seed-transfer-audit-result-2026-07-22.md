# D131a D130 all-seed transfer audit — result

Date: 2026-07-22  
Decision: **close coefficient-1 cross-sign ranking and replace tiny-lineage selection**

D131 exactly reproduces every D130 model, fit metric, and training-calibrated gate offset, then
scores all four fixed controllers on consumed D126 data. Two complete artifacts are byte-identical.
No seed descriptively passes:

| seed | fit eligible | development mean | strict | positive families | family floor |
|---:|:---:|---:|---:|---:|---:|
| 13001 | no | -0.137 | 37.11% | 5 | -5.094 |
| 13002 | yes, selected | -0.047 | 40.23% | 5 | -11.719 |
| 13003 | no | +1.410 | 43.36% | 5 | -6.031 |
| 13004 | yes | +1.477 | 43.75% | 6 | -5.531 |

Seed13004 confirms a selector defect: the unselected eligible model is materially better than
seed13002. Across only four points, fit proposal regret versus development mean is `r=+0.890`, the
opposite direction from the D126 minimum-regret selector. Fit mean versus development mean is
`r=-0.251`, fit family floor versus development floor `r=-0.641`, pair accuracy versus development
mean `r=-0.181`, and positive-winner rate versus development mean only `r=+0.201`.

Changing the selector cannot save this objective: even the best seed misses mean and family-floor
gates substantially. Close coefficient-1 cross-sign pairwise training without a coefficient or
margin sweep. More generally, selecting among four initializations on one 16-map fit panel is too
unstable for the remaining tail problem.

The next move should change the evidence scale rather than add another loss to the same small
panel. Build a multi-block exact-teacher training corpus with many more independent maps, retain
block identity, and select by leave-one-block-out transfer rather than in-sample regret. First
audit the existing distributed/YT collection path and freeze a bounded collection/throughput
protocol; do not spend the still-untouched final validation range or touch Arena until the larger-
data learner clears held-out local blocks.

Lock SHA-256: `5a79ff2b1d20b87c3b67dfc81410953b2f158af78d735652a2dfe3059ecb857e`  
Result SHA-256: `e4380658b271e6f63389402fed2602ba8407c166d5b9872ff7f6cbb200728a2c`
