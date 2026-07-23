# D144a two-intervention Monte Carlo pilot — frozen protocol

Date: 2026-07-22  
Status: frozen after implementation and excluded-seed mechanics/throughput smoke, before creating
any D144 target YT path, table, operation, or result

## Purpose and hypothesis

D140--D143 close further threshold, normalization, composition, and first-positive refinements of
the current one-use q6 gate: none reaches the prospective 40% strict-transfer floor across 2,048
out-of-fit tasks. Reopen Monte Carlo only as an offline teacher, not as a live controller. Prior
online MC exceeded the 50 ms move budget, while D107 showed that bounded repeated q6 authority has
real headroom: its unselectable four-use population oracle added `+3.758` margin beyond matched one
use and improved 45.313% of tasks.

The prospective D144 hypothesis is narrower: deterministic sampled sequences containing at most
two interventions recover at least `+3` mean margin beyond the complete exact one-use oracle on a
new panel, with broad task/family support and no relative establishment or workforce regression.
Passing would justify a trajectory-labelled two-use learner. Failing closes this sampled schedule
and proposal population; it does not claim that every multi-use search is valueless.

## Excluded preflight

All preflight uses already consumed seed base `9,829,000` and cannot enter the target analysis.
Two one-map, four-replica executions are byte-identical at SHA-256
`2dda090c1344b3d6fddb8117a9b31fad3ead1731fecb1640836f5a2aaebe0c08`; each contains 64 episodes,
and 15/32 double-mode episodes reach two interventions. A separate eight-map/four-replica
throughput smoke produces 512 episodes at 10.949/s, uses 14.34 average CPU cores, and has SHA-256
`4cd091db6faff6345cd737658e96ad271865e977b05762be7ecd1a73ffe2de27`.

The actual isolated worker layout was also exercised. Its MC output reproduces the one-map hash.
Its exact-teacher branch emits 950 arms plus 16 baselines in 33.235 seconds, or 28.589 arms/s. These
smokes may repair mechanics and capacity thresholds only; they cannot tune target value gates.

## Frozen target panel and sampling

Use previously unused training seeds `9,844,128--9,844,135`, both seats, and the eight frozen
opponents: 128 tasks. Preserve consumed D126 as veto-only and leave final seeds
`9,843,800--9,843,815` untouched.

For each task generate 128 deterministic episodes:

- replica 0 is exact D40 control;
- replicas 1--16 allow exactly one scheduled intervention; and
- replicas 17--127 allow at most two scheduled interventions.

Schedule the first boundary by the capped trailing-zero stratum in the locked driver. Schedule the
second strictly later using an independently hashed capped gap. At each scheduled boundary choose
one legal noncontrol proposal by the locked SplitMix64 key. Force control elsewhere and after the
mode cap. Record the complete terminal, schedule, selected slots, and selection hash. Repeat the
entire 16,384-episode matrix independently as executions A and B; require byte identity.

In parallel collect the complete exact one-use D112 teacher for the same eight maps as two fixed
four-map shards. Do not modify the already validated Rust Q6 environment, D112 binary, expert
population, or proposal ABI.

## Frozen YT execution

Use root `//home/delivery_ml/research/tarstars/troll_farm` and build
`d144a_two_intervention_mc_9844128_9844135_20260722`. Submit exactly four mapper jobs: `mc-a`,
`mc-b`, `exact-00`, and `exact-01`. Each receives 16 CPUs/threads, 8 GiB, the frozen Jammy/Python
3.11 layers, and the `delivery-ml` pool. Pin NumPy BLAS to one thread and Rust Rayon to 16 threads.

Require operation completion, exactly four prescribed metadata records, and 16 threads in every
job. Each MC job must complete within 2,700 active seconds at at least 5 episodes/s. Each exact job
must complete within 900 active seconds at at least 12 arms/s. Capacity failures authorize only an
infrastructure repair with unchanged panel, sampler, and scientific thresholds.

## Mechanics gates

Require all of the following before interpreting value:

1. A and B are byte-identical and each contains exactly 16,384 uniquely indexed episodes.
2. Counts are exactly 128 control, 2,048 single-mode, and 14,208 double-mode episodes, with the
   prescribed per-task counts.
3. Scenario mapping, schedules, selection hashes, terminal identities, and intervention caps are
   exact; direct-command, provenance, and deposit-prediction failures are zero.
4. Every control terminal exactly matches the corresponding dense D112 baseline.
5. Every selected single-mode terminal exactly matches its `(task, boundary, slot)` dense D112 arm.
6. The inherited exact one-use schema, pairing, feature, reward, accounting, and support mechanics
   pass with exactly 128 baselines.
7. At least 40% of double-mode episodes execute two interventions, and at least 95% of tasks have
   at least one executed two-intervention sample.

## Prospective value and safety gates

For every task select the complete exact one-use oracle, then compare it with the best sampled
episode that executed exactly two interventions. Use the two-intervention result only when its
terminal margin is strictly higher; otherwise retain the one-use choice. The combined oracle must:

- add at least `+3.0` mean margin beyond exact one use;
- strictly improve at least 20% of all 128 tasks;
- have positive mean increment in at least six of eight opponent families; and
- have nonnegative increment in the worst family.

Following D122's corrected safety semantics, report absolute crop creation but gate relative harm:
the combined oracle may introduce zero new crop failures versus exact one use. Its worker-three
rate may fall by at most five percentage points. This does not weaken the establishment invariant;
it avoids blaming a forced-control map with no q6 boundary on an intervention policy.

## Decision boundary

A full infrastructure, mechanics, value, and safety pass opens a separately frozen
two-intervention trajectory-teacher and deployable policy-fit experiment. D144 itself creates no
candidate, consumes no D126/final validation, changes no Rust resident code, submits nothing, and
does not touch TestSession or Arena. A mechanics-clean signal failure closes this exact sampler and
promotes analysis of where its sequences lose value before any larger search.
