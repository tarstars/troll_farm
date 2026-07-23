# YT compute assessment for Troll Farm — 2026-07-20

## Decision

**YT is decisively profitable for training-scale work, but the frozen D11 run must remain local
because its one allowed parity benchmark failed.**  The measured RTX 4090 trainer is 9.82x faster
than local CPU and projects to 8.52 rather than 66.47 minutes end to end for 4M transitions.  Keep
single controls and 500--2,000-episode gates local.  Use YT for future multi-million-transition
runs, replica portfolios, large checkpoint-by-opponent matrices, or millions of Monte Carlo games
only after each frozen workflow clears a backend-parity rule.

D11 did trigger the planned live benchmark.  Both arms passed the functional Stage-A gate, but
their worst-recipe floors differed by 6.557 percentage points against a preregistered 5-point cap.
That makes YT ineligible for the sole current 4M run despite its clear time advantage; the
threshold is not being revised after observation.

## Infrastructure verified

The neighboring `/home/tarstars/prj/math_through_eml` project provides reusable patterns for:

- YTsaurus table-backed CPU map/sort/reduce jobs;
- vanilla GPU jobs with payload/runtime archives and output retrieval;
- separate launcher and worker credentials; and
- run-status, resource-report, and artifact-download tooling.

Its documented GPU smoke successfully allocated one NVIDIA GeForce RTX 4090 in
`gpu_starfield_24g_cloud/research_gpu`, with Torch 2.4.1+cu121, CUDA visible, and table reads from
inside the worker.  This is a validated workflow template, not a guarantee of immediate GPU
availability.  Troll Farm subsequently completed its own dedicated operation
`238b228b-9a1e6a82-42e03e8-7a4e73d7`, also on an RTX 4090, under
`//home/delivery_ml/research/tarstars/mle/troll_farm` without modifying the math project's run or
table namespaces.

A read-only live metadata query on 2026-07-20 succeeded against `watt.yt.yandex.net`.  Shared
account `delivery_ml` reported:

- 236 / 1,251 Cypress nodes;
- 1,112 / 22,528 chunks;
- 61,960,189,845 / 10,995,116,277,760 bytes; and
- the existing math project subtree used 82 nodes, 1,060 chunks, and 53,269,187,751 bytes.

The named Starfield GPU pool exists and exposes no explicit pool-local resource limit in its
attributes.  It is shared capacity; queue delay must be measured per launch.

Reproduction commands used for this assessment:

```text
cd /home/tarstars/prj/math_through_eml
.venv/bin/python scripts/yt_resource_report.py --json
```

The GPU workflow evidence is in
`/home/tarstars/prj/math_through_eml/docs/watt_yt_gpu_workflow.md`.

## Measured Troll Farm workload

| Workload | Local measured cost | YT decision |
|---|---:|---|
| D9 prospective teacher, 2,000 episodes | 6.90 s; 99,991 transitions/s | local |
| D9 prospective random, 2,000 episodes | 10.65 s; 65,297 transitions/s | local |
| D9 prospective neural actor, 2,000 episodes | 71.83 s; 9,856 transitions/s | local |
| Level-4 behavior clone | 539--589 s | local for one run; YT if sweeping many |
| Level-4 PPO, 4M transitions | 4,092.77--5,270.28 s; 759--977 effective transitions/s | YT benchmark justified |
| D11 PPO benchmark, 1M local | 1,007.20 s outer; 994.81 transitions/s | parity reference |
| D11 PPO benchmark, 1M YT RTX 4090 | 190.02 s operation; 102.36 s trainer; 9,769.02 transitions/s | time pass, parity fail |
| D11 projected PPO, 4M | 66.47 min local versus 8.52 min YT | local selected by frozen conjunction |

The simulator is already fast.  The expensive component is neural training, not Rust environment
stepping.  Moving tiny controls to YT would add packaging, queue, startup, and artifact-transfer
latency to work that finishes locally in seconds.

## Profitable YT shapes

### Independent PPO replicas

The strongest near-term use is one self-contained vanilla GPU job per frozen seed/model replica.
Four to eight replicas can run independently, then return only checkpoints and compact summaries.
This reduces serial wall time and produces the variance evidence needed for a reliable candidate.

### Large evaluation matrices

Distribute cells of `checkpoint x opponent x seed block` when their aggregate local estimate exceeds
about one hour.  Each cell writes a compact JSON aggregate; raw episodes stay table-backed only if
needed for diagnosis.

### Monte Carlo and dataset generation

Package the Rust engine as a CPU mapper for millions of independent games, opening choices, or
counterfactual continuations.  Partition by deterministic seed/state key and reduce sufficient
statistics centrally.  This is a better fit than trying to multithread one Python driver across a
single host.

### Behavior-cloning data

Generate teacher trajectories in CPU map jobs and train the compact model in a GPU vanilla job.
Unlike PPO rollouts, this dataset is stationary and requires no distributed policy synchronization.

## Poor YT shapes

- one 500-episode control;
- one prospective 2,000-episode actor evaluation;
- debugging ABI, legality, or deterministic environment behavior;
- an on-policy distributed rollout system before a local actor failure exists; or
- remote jobs whose raw per-transition output creates thousands of small Cypress objects.

## Transfer plan when the trigger occurs

1. Freeze the failing task, checkpoint, seeds, gates, and training configuration.
2. Create a dedicated Troll Farm payload and YT root; reuse workflow code, not the math project's
   run namespace.
3. Build the Rust shared library inside a compatible Linux payload and create a dedicated
   Python/Torch runtime.  Do not assume the math runtime is compatible: Troll Farm currently uses
   Python 3.11.15, Rust 1.75.0, and Torch 2.13.0+cpu, while the proven math GPU runtime uses a
   different Torch/CUDA build.
4. Run identical local and YT jobs with a 1M-transition measured section.  Record cold-start time,
   steady-state transitions/s, total wall time, final metric parity, and artifact hashes
   separately.  A 100k-only cold benchmark is too dominated by startup to extrapolate a 4M run.
5. Use YT only if projected total wall time for the frozen full run improves materially and result
   parity holds.
6. If profitable, launch independent preregistered replicas, not adaptive hyperparameter fishing.

## Current trigger status

**Triggered, benchmarked, and closed for D11.**  YT passes the economic discriminator at 12.82% of
projected local wall time but fails prerequisite functional parity on one recipe floor.  The sole
model-139/stream-7,400,000 D11 PPO run therefore executes locally.  The benchmark checkpoints are
throughput evidence, not selectable candidates.  Exact timings, metrics, operation metadata, and
hashes are in the
[D11 backend benchmark result](curriculum-level5-seed-reacquisition-d11-ppo-backend-benchmark-result-2026-07-20.md).
