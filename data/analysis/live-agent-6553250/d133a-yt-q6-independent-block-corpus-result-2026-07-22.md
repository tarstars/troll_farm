# D133a YT q6 independent-block teacher corpus — result

Date: 2026-07-22  
Decision: **close D133a on its frozen support gate; audit support semantics only**

The distributed execution itself is a full success. Operation
`f68fd8f9-83f2b344-42e03e8-a0934784` completes all sixteen four-map shards under
`//home/delivery_ml/research/tarstars/troll_farm` with zero failures. Every shard uses 16 threads,
finishes in 88.45--382.13 seconds, and produces 17.16--49.95 arms/s, so all six infrastructure
gates pass.

Streaming reconstruction yields exactly 1,024 baselines and 81,440 exact arms in four independent
blocks:

| block | seeds | supported tasks | roots | arms |
|---:|---|---:|---:|---:|
| 0 | `9,844,000--9,844,015` | 236/256 (92.19%) | 1,302 | 21,557 |
| 1 | `9,844,016--9,844,031` | 233/256 (91.02%) | 1,461 | 23,679 |
| 2 | `9,844,032--9,844,047` | 217/256 (84.77%) | 1,015 | 16,560 |
| 3 | `9,844,048--9,844,063` | 224/256 (87.50%) | 1,202 | 19,644 |

All complete-root, schema/finiteness, paired-gain, reward-identity, one-intervention,
single-expert-bank, and zero-failure checks pass in every block. The only failed inherited gate is
q6 availability: global support is 910/1,024 (`88.87%`) rather than the frozen 90%, and blocks 2
and 3 individually miss 90%. D133a therefore correctly stops before interpreting their teacher
values or opening D134.

This is not evidence of corrupt records: D113 already defines zero-boundary tasks as valid forced
control, and D133 retains 81,440 labels and 4,980 roots above its explicit sample-size floors. The
next legal step is a separately frozen retrospective audit of support rates across all earlier
independent q6 panels. Only if that audit shows 90% per block was an unstable small-panel property
may a support-semantics repair reinterpret availability while preserving every exact mechanics,
sample-size, signal, safety, and final-validation gate.

Lock SHA-256: `e6c6d554fdeddc961317e94b45972711a4dadbb9da20d9061eda91b385a118c1`  
Launch SHA-256: `4aef7d0f10c4ae9652dd9e1ef8175fbb32fc4f19dd1444c848e2cd07262a4e42`  
Download SHA-256: `a6e9585407e3a89da81ace80e7dd5f8ecbcd7ec0f3fafe1617513c6f8edcc97a`  
Result SHA-256: `3fa237c363b5b559428261df7dad49f78291238c94f2de14fcb837b2574893af`
