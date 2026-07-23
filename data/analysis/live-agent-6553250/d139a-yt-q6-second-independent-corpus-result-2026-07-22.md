# D139a YT q6 second independent corpus — result

Date: 2026-07-22  
Decision: **open frozen eight-block learner selection**

YT operation `ded9b633-d229c8cd-42e03e8-9fe8f069` ran under
`//home/delivery_ml/research/tarstars/troll_farm`. It initially remained ready/pending with no
scheduler attempts despite an empty visible `delivery-ml` pool. A recorded exact local 20-thread
hedge was started, then stopped after about 195 seconds without emitting TSVs when YT allocated 11
jobs. YT subsequently ran all 16 jobs concurrently and completed 16/16 with zero failures.

All frozen infrastructure gates pass: correct shards and threads, active times 90.48--550.98
seconds, and throughput 14.49--48.25 arms/second. Streaming reconstruction used at most 997 MB and
produced 468 MB in four independent blocks:

| Global block | Seeds | Arms | Roots | Support | Teacher mean | Strict | Family floor |
|---|---|---:|---:|---:|---:|---:|---:|
| 4 | 9,844,064--079 | 19,446 | 1,190 | 231/256 | +34.789 | 89.84% | +24.813 |
| 5 | 9,844,080--095 | 23,142 | 1,412 | 235/256 | +39.387 | 89.84% | +23.469 |
| 6 | 9,844,096--111 | 22,333 | 1,357 | 241/256 | +38.910 | 92.58% | +24.313 |
| 7 | 9,844,112--127 | 21,205 | 1,302 | 231/256 | +35.258 | 89.45% | +22.063 |

Totals are exactly 1,024 baselines, 86,126 arms, 5,261 roots, and 938 supported tasks (91.60%).
Every nonavailability mechanics gate passes. Aggregate teacher value is `+37.086`, 90.43% strict,
all eight families positive with `+26.609` floor, own `+23.514`, opponent `-13.572`, 48.95%
act-now roots, 12.97% positive arms, 85.18% negative arms, and 26.95 target standard deviation.
Crop and workforce exactly match control.

D139 creates no model or platform candidate. It only authorizes D140's already-frozen selection on
eight blocks. Result SHA is `4ce55d81...`; download SHA is `6a867026...`; lock SHA is
`6cfcbcdc...`.
