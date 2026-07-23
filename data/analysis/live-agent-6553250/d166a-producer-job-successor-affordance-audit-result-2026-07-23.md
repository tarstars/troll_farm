# D166a producer-job successor affordance audit — result

Date: 2026-07-23  
Verdict: **close a single forced return verb; move to state-conditioned, multi-step semantic job
value with exact resident KEEP.**

## Reproducible execution

D166 reuses the immutable D164 open snapshot and all 1,024 consumed D148/D161 local tasks. It
makes no platform, sealed-confirmation, YT, fresh-map, candidate, resident, Arena, or submission
change.

The 392-row field products are byte-identical at SHA
`a6fe0d28199d2ad201fdaf75441bded0c50cc6de8c1e402479ad4769da990091`.
One process takes 26.45 seconds and 20 processes take 3.95 seconds, a 6.70× speedup. The 1,024-row
local products are byte-identical at SHA
`30d294bcaf620ddff3932e8d153b8315572b198192a9532d84e899ca44c16e9f`.
One worker takes 116.41 seconds and the corrected 20-worker runner takes 11.36 seconds at 1,797%
CPU, a 10.25× speedup.

An initial nominally parallel local run exposed a lock-scope bug: the row mutex was acquired before
the simulation argument was evaluated, serializing all work. Moving simulation outside the lock
reduced wall time from 112.65 to 11.36 seconds without changing one output byte.

Every integrity gate passes:

- field cohort sizes and cycle counts reproduce D164 exactly: 36/50 top-five, 41/150 ranks 6--20,
  and 21/192 resident;
- all decoded states, crop generations, worker identities, and birth classifications are exact;
- the local resident reproduces D161 on every shared terminal, score, workforce, crop, mechanics,
  action-hash, and state-hash field;
- local production, suppression, and historical-worker counts reproduce D165 exactly:
  1,024 production tasks, 932 suppression tasks, and 1,976 historical-producer CHOPs in 237 tasks;
- reward, ownership, history, worker, and read-only gates are clean; and
- the D164--D166 focused Python suite passes 10/10 while the inherited Rust suite passes 6/6.

## Field return class

The field motif is not one action:

| Cohort | PLANT return | HARVEST return | PLANT rate | Dominant-class result |
|---|---:|---:|---:|---|
| Current top five | 21 / 36 | 15 / 36 | **58.33%** | fails frozen 60% |
| Ranks 6--20 | 28 / 41 | 13 / 41 | 68.29% | supports PLANT |
| Exact resident | 21 / 21 | 0 / 21 | 100.00% | PLANT only |

Both PLANT and HARVEST appear in all five top agents and both seats. Top-five median suppression
duration is 15 turns for PLANT and 32 for HARVEST. PLANT passes every frozen dominance condition
except the preregistered top-five rate, missing it by one cycle; HARVEST fails both top-five and
rank-6--20 rate conditions. Local coverage and outcomes are forbidden from breaking this tie.

Crop-generation continuity also rejects the stale-target model. Only 1/36 top-five cycles,
3/41 rank-6--20 cycles, and 0/21 resident cycles return to the exact prior generation. Reusing the
same cell is more common (7, 12, and 12 respectively), but usually with a new crop generation.
The successor is a new job, not resumption of an old asset.

## Local successor state

At the first exact historical-producer suppression entry:

| Immediate affordance | Supported tasks | Seats | Families | Decision |
|---|---:|---:|---:|---|
| Ripe own-crop HARVEST (`H-ripe`) | **2 / 237** | 2 | 2 | fail |
| Any live own-crop future HARVEST (`H-live`, diagnostic) | 14 / 237 | 2 | 6 | sparse |
| Carried-seed PLANT (`P-carry`) | **0 / 237** | 0 | 0 | fail |

The selected worker has harvest power zero in 177/237 entries and is full in 25/237. The exact
prior crop generation remains live in 0/237, confirming D165 with generation rather than cell
identity.

Yet the untouched resident later produces again in 135/237 tasks (56.96%), across both seats and
six families. All 135 returns are PLANT. Sixty-nine return within 16 turns, 105 within 32, and
median latency is 16. None reuses the prior crop generation. Because no worker carries a seed at
entry, these are necessarily multi-step acquisition-and-PLANT continuations rather than an
immediate return command.

## Decision

D166 does not open a D167 single-verb controller:

- field PLANT is broad but not dominant under the frozen threshold;
- immediate local PLANT has zero support;
- immediate local HARVEST has only two tasks; and
- choosing the locally common later PLANT path would violate the preregistered no-rescue rule.

The next representation should preserve exact warmed-resident KEEP and evaluate whole semantic
successor jobs conditioned on the entry trajectory:

```text
KEEP
acquire seed -> reach legal cell -> PLANT
reach current own crop -> HARVEST
```

Before a causal rollout, recover the seed-acquisition path between suppression and the 135 natural
local PLANT returns and the corresponding field PLANT returns. Freeze only job classes that are
observable, broad, and genuinely distinct from D87 immediate regeneration and D89 full-rate
farming. If acquisition paths are also heterogeneous, stop writing fixed controllers and evaluate
trajectory-valued semantic actions with short resident-backed rollouts.

No candidate, Arena test, or submission is justified by D166.

## Reproducibility

- protocol: `c9042a60c6fa96678ec5e87e6e87c89268d66035473a1187aae6d804a7d851ed`;
- lock: `d26b146eb826b5d82579d741ef529425c80e4d79843202a1bed25c72c540f0b0`;
- field extractor:
  `51190a7d81aeb5e651771ebe5c299ba882239c2f48e6d51a447fc10b9b920936`;
- local runner:
  `a1427f72db8d3ee038af4ca397b37533d6a04975d9d58e68e692c24434a2b072`;
- analyzer: `67849347c018cb0b75ed1a5ea9c2dcad129b7f29a2ccbe05749e30438e59d88c`;
- aggregate result:
  `bdc1419c3dff886957b6346a6d6ba3996416782163831b2b5f316eab4f0933af`;
- field rows: `a6fe0d28199d2ad201fdaf75441bded0c50cc6de8c1e402479ad4769da990091`;
- local rows: `30d294bcaf620ddff3932e8d153b8315572b198192a9532d84e899ca44c16e9f`.
