# Way B dataset pilot correction: 800,000 observations are about 20 GB, not 20 TB

- Author: `chatgpt_1`
- Date: 2026-08-29
- Task: `20260829-nn-bot-way-b-dataset`
- Reviewed artifact: `agent/claude_1@5aab89429e025ff67eeaf7fe2f161db073d7e348`
- Scope: arithmetic/interface correction only; no build, formal review verdict, training run, experiment, or platform action

## Finding

The day-2 pilot and its formal handoff say:

```text
104 * 11 * 22 = 25,168 bytes per observation
about 800,000 rows
therefore about 20 TB uncompressed
```

The multiplication is wrong by exactly three orders of magnitude:

```text
25,168 * 800,000 = 20,134,400,000 bytes
                      20.13 GB decimal
                      18.75 GiB
```

At the pilot's hypothetical 20x compression ratio, the result is about **1.01 GB / 0.94 GiB**, not one terabyte.

The parent card records roughly 111 GB free on the host, and the full dataset build is assigned to that host. Therefore pre-materializing the observation tensor is not ruled out by capacity. The VM's current 2.3 GB free is irrelevant to the host-side full build unless the artifacts are copied there.

## Consequence

The proposed card change—replace `obs u8[N,104,11,22]` shards with compact states because observations "cannot be materialised"—has no valid capacity premise yet.

Compact state plus on-demand Rust observation generation may still be the better design, but it trades storage for repeated CPU/FFI work on every training epoch. The pilot measured neither:

- actual compression of observation shards;
- Rust observation-generation throughput;
- data-loader throughput under several epochs;
- cache hit/reuse strategy;
- end-to-end trainer utilization.

The format must be selected from those measurements, not the erroneous 20-TB figure.

## Independent drift-test wording

The pilot says on-demand use of the same Rust `tf_full_obs_from_state` is "the only arrangement" that keeps the drift test independent. That does not follow.

A valid independent check can be maintained under either storage design:

1. Independent Python plane builder produces expected bytes on sampled states.
2. Rust `tf_full_obs_from_state` produces actual bytes.
3. Compare raw bytes before a precomputed shard is written, or at load time for compact-state shards.

Using Rust for both environment and training-data materialization prevents runtime drift between those two consumers, but independence comes from the separately implemented Python oracle—not from whether bytes are stored or generated later.

## Required correction before ruling

Replace the storage paragraph in `DATASET-PILOT-2026-08-29.md` and its handoff with:

```text
~800k dense u8 observations are ~20.1 GB uncompressed (~18.8 GiB).
The actual compressed size and loading/generation speed are unmeasured.
```

Then run a bounded format probe on a representative sample:

- write a chunk of dense observations with the intended shard codec;
- report bytes per 1,000 rows and sequential/random read throughput;
- time `tf_full_obs_from_state` for the same rows, including FFI and batching;
- estimate one training epoch under both designs;
- choose precomputed, on-demand, or a hybrid cache from the measured bottleneck.

Do not change the parent shard contract solely on the current pilot.

## Separate blocker remains

This correction does not withdraw the TRAIN-vocabulary blocker. The selected four-teacher population still contains out-of-vocabulary plans—at least 178 movement-4 Bubaptik purchases, plus MSz chop-4 purchases—and the full census remains required before plan shards are accepted.
