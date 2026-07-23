# PPO CPU parallelism benchmark — 2026-07-19

## Verdict

Retain **14 unbound Torch threads**.  This host has 20 logical CPUs but only 14 physical cores:
six hyperthreaded P cores and eight single-thread E cores.  A system monitor therefore reports
about 70--72% when one compute thread occupies every physical core.  The confirmation trainer
itself reported about 1,382% process CPU, which is 13.82 fully occupied cores rather than an
underutilized job.

Increasing logical-thread occupancy to 16, 18, or 20 raises the CPU meter but reduces useful PPO
throughput.  Pinning 14 threads to one sibling per physical core also loses in the longer repeat.
The safe retained command setting remains `--threads 14` without `taskset`.

## Non-gating fixed workload

The benchmark was isolated from every learning verdict and candidate decision:

- starting checkpoint: accepted Level-4 confirmation final, SHA-256
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
- fixed debug training seed base 91,000,000 and evaluation base 90,000,000;
- 100 environments x 100 steps, four PPO epochs, minibatch 1,000;
- learning rate exactly zero, so every run performs the same rollout, backward, clipping, teacher
  auxiliary, and optimizer machinery without changing policy weights;
- 30,000 decisions per primary configuration, followed by a 100,000-decision placement A/B;
- identical 100-map teacher/random controls at 100%/0%; and
- sequential execution on AC power, so configurations do not compete with one another.

These artifacts are performance diagnostics only.  Their seeds, evaluations, and checkpoints may
never qualify a learned model or submission.

## Primary 30k matrix

| Placement | Host CPU | Wall | Overall decisions/s | Median rollout/s | Median update/s | Wall vs 14 |
|---|---:|---:|---:|---:|---:|---:|
| 14 threads, unbound | 69.32% | **31.12 s** | **964.1** | 5,334 | 1,024 | 1.00x |
| 16 threads, unbound | 77.76% | 45.70 s | 656.4 | 1,412 | 640 | 1.47x |
| 18 threads, unbound | 86.41% | 60.45 s | 496.3 | 966 | 540 | 1.94x |
| 20 threads, unbound | 92.63% | 125.17 s | 239.7 | 403 | 253 | 4.02x |
| 14 threads, physical-core pin | 69.53% | 31.08 s | 965.2 | 6,524 | 1,025 | 1.00x |

The apparent short-run pinning tie required confirmation.  Higher thread counts do not: 20
threads consume 33.6% more aggregate CPU-meter capacity than 14 while making the fixed workload
4.02 times slower.  Its third batch fell to 273 rollout/s and 166 update/s.

## Longer placement confirmation

| Placement | Host CPU | Wall | Overall decisions/s | Median rollout/s | Median update/s |
|---|---:|---:|---:|---:|---:|
| 14 threads, unbound | 69.60% | **103.17 s** | **969.3** | **6,198** | **986** |
| 14 threads, physical-core pin | 69.00% | 122.26 s | 817.9 | 5,062 | 839 |

The manual affinity set `0,2,4,6,8,10,12-19` is 18.5% slower in wall time and 15.6% lower in
overall throughput.  Linux's normal hybrid-aware scheduling is better able to move work as power,
thermal, and background conditions change.  Do not retain the pinning wrapper.

## Power-state diagnosis

The large slowdown seen during the frozen confirmation was not missing parallelism.  With AC
disconnected, the host selected `power-saver`, all cores fell to roughly 0.7--0.9 GHz, and PPO
update throughput fell to about 235/s.  Connecting AC raised clocks to roughly 3.0--3.7 GHz and
restored about 900--1,000 update/s without changing the process, thread count, seed stream, or
optimizer.  Removing one stale filesystem diagnostic also freed a small amount of unrelated
CPU/I/O load.

For future CPU training runs:

1. require AC power and verify clocks before launch;
2. use 14 unbound Torch threads and at most four inter-op threads;
3. judge parallelism by decisions per wall-second, not logical-CPU percentage; and
4. run alternative experiments sequentially on this host.  Simultaneous full trainers would
   compete for the same 14 physical cores rather than add capacity.

## Reproducibility anchors

- 30k unbound 14 summary:
  `4274ac28f6cf9f7e7e3a78d643a78b65b665289ca68bab3295d2afd67022e2a5`;
- 30k unbound 16 summary:
  `269c35bcb8f7796849910a7ba3849710386f086cbe681acda9a5784f5bace2b4`;
- 30k unbound 18 summary:
  `21faaf2d077c4eacb94df646a43f179c14b1e6c984663c20c7e6c380b60151ee`;
- 30k unbound 20 summary:
  `20341f713455510df0435f55584f3a941a9ac6311cff29049f272b429fce2284`;
- 30k pinned 14 summary:
  `990a709283da73493e7f28236d71bf3c626ddd9fa0b309070e5b54f5c96dd4e8`;
- 100k unbound 14 summary:
  `2dd2f5c52305c1619d643bd6fd209313ce405efefe825657d2cc7095197c6384`;
- 100k pinned 14 summary:
  `ab428a7af4425621b27fadb32b6926f91b7d49c4494d81602424df2357b74c92`.
