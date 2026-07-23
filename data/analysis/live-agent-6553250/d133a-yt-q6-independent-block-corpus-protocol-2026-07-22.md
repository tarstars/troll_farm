# D133a YT q6 independent-block teacher corpus — frozen protocol

Date: 2026-07-22  
Status: frozen before any D133 YT table or operation is created

## Purpose and evidence change

D131 shows that selecting four initializations on one 16-map panel is unstable, and D132 proves
that the exact D112 Rust collector is byte-identical between local execution and YT CPU workers.
D133 changes evidence scale without changing the teacher, feature schema, expert bank, opponents,
or counterfactual semantics.

Collect unused seeds `9,844,000--9,844,063`, both seats, and all eight fixed opponents. Preserve
four consecutive independent 16-map blocks:

| block | seeds | tasks |
|---|---|---:|
| 0 | `9,844,000--9,844,015` | 256 |
| 1 | `9,844,016--9,844,031` | 256 |
| 2 | `9,844,032--9,844,047` | 256 |
| 3 | `9,844,048--9,844,063` | 256 |

Source/path searches found no earlier experiment artifact using this range. Final validation seeds
`9,843,800--9,843,815` remain untouched and excluded.

## Immutable distributed execution

Use YT root `//home/delivery_ml/research/tarstars/troll_farm`, pool `delivery-ml`, and the D132-
validated Jammy base plus Python 3.11 layers. Attach the exact release collector SHA-256
`5bed211a33393f041221dcda81bdd2bf5d11522ad1aa3978fe4d3b79492f6d02`, expert-bank SHA-256
`87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`, and unchanged D132 mapper.

Create sixteen four-map specs, four per evidence block. Write each spec as a separate YT input
chunk, request 16 map jobs, allocate 16 CPUs and 8 GiB per mapper, and run each collector with 16
threads. Stream line-preserving JSON records to YT. Download without materializing the output
table in memory, reconstruct each shard in row-index order, deduplicate identical TSV headers, and
merge shards only within their fixed 16-map block.

## Frozen gates

### Infrastructure and throughput

- the YT operation completes and emits exactly sixteen distinct mapper metadata records;
- every prescribed shard appears once with its exact start seed, four-map span, and 16 threads;
- each shard's active collection time is at most 900 seconds and its own arm throughput is at
  least 12 arms/s; and
- every emitted arm/baseline record has a contiguous row index and the prescribed shard/start
  identity, with one identical header per record type.

### Exact mechanics and coverage

Run the inherited D113 zero-boundary-aware mechanics independently on each 16-map block. Require:

- exactly four passing blocks, each with its prescribed 256 unique baseline tasks;
- globally exactly 1,024 baselines, at least 80,000 arms, and at least 4,800 supported roots;
- at least 90% task support globally and within each block; and
- all inherited schema/finiteness, complete-root, paired-gain, reward-identity, one-intervention,
  single-expert-bank, and zero direct-command/provenance/deposit-failure gates in every block.

D132's byte-exact backend parity is inherited; D133 does not repeat every new seed locally.

### Teacher usefulness

Compute D113's teacher statistics independently per block, retain every label with its block id,
and aggregate only sufficient counts/moments. Record per-block signal/safety statistics
descriptively. On the full 1,024-task corpus require the unchanged D113 gates:

- oracle mean margin gain at least `+20`, strict gain at least 75%, at least seven positive
  opponent families, and worst family mean at least `+8`;
- nonnegative mean own-score gain or nonpositive mean opponent-score delta;
- act-now roots between 5% and 90%, positive arm targets between 1% and 50%, at least 40% negative
  arm targets, and target standard deviation at least five; and
- 100% oracle crop creation with worker-three reach within five percentage points of control.

Per-block teacher thresholds are not gates: their purpose is to expose transfer variance, and
rejecting a sound corpus because one block has a noisy rare-family mean would recreate the small-
panel selection defect D133 is meant to address.

## Decision

- **Infrastructure or mechanics failure:** repair only that execution/collection defect under a
  separately locked protocol; do not interpret labels.
- **Aggregate signal or safety failure:** close this corpus for q6 learner selection.
- **Full pass:** open D134 leave-one-block-out training. Select architecture, objective,
  regularization, and random seed only by performance on blocks excluded from each fit; then train
  the frozen recipe on all four blocks.

D133 does not qualify a model, open final validation, create a submission, mutate the resident, or
touch TestSession/Arena.
