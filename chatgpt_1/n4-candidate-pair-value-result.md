# N4 Phase A — exact resident pair surface

Prepared UTC: 2026-07-31T06:11:00Z  
Task: `20260730-n4-candidate-pair-value-audit`  
Verdict: **`RUNTIME_CLOSE`**

## Decision

Close N4 at the preregistered Phase-A runtime gate. The exact exporter/materializer is
correct and deterministic, but its measured candidate export plus boundary reconstruction
latency exceeds the frozen **5 ms p95** close by **42–67×** on the accepted one-root smoke.

The full 2,048-game census was deliberately not run. The pre-lock smoke exists to prevent an
infeasible census; one official root already emits 268,168 data rows / 83.3 MB, and linear
projection is roughly 34.3 million rows / 10.7 GB.

No Phase B, compact-format retune, pair pruning, alternative boundary definition, source
change, or value oracle is authorized.

## Diagnostic scope

The terminal decision uses an exact **one-root pre-lock diagnostic**, not full-matrix
coverage:

- map seed `9,854,000`;
- both resident seats;
- all eight frozen opponent families;
- 16 tasks;
- 4,028 natural two-worker decision states.

Therefore the result classifies only the runtime and instrumentation gates. It does not
claim full-population eligibility, boundary frequency, family breadth, seat balance, or
consumed-grammar distinctness.

## Correctness and parity

All pre-lock correctness gates pass:

- Python compilation and built-in self-test pass;
- focused pytest: 12/12, including materialize-and-Cargo regression;
- exact sacred-source materialization and release build pass;
- frozen resident SHA-256 remains
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- 0/4,028 frozen resident command-pair reconstruction failures;
- one-thread and 20-thread results have identical 268,169 total lines;
- after excluding only measured `latency_us`, normalized rows are byte-identical at
  SHA-256
  `9177b5c925d3a534bb19588f76314f26d163192cbb75f0118d41b979bce9b3be`.

This is a runtime close, not an instrumentation or parity failure.

## Runtime result

| measure | observed |
|---|---:|
| frozen p95 close | 5.000 ms |
| one-thread p95 | 210.408 ms |
| 20-thread p95 | 333.157 ms |
| multiple of close | 42.08× / 66.63× |
| one-thread elapsed | ~642 s |
| 20-thread elapsed | 235.04 s |
| 20-thread max RSS | 323,268 KiB |
| one-root data rows | 268,168 |
| one-root bytes | 83,327,440 |
| projected full rows | 34,325,504 |
| projected full bytes | 10,665,912,320 |
| projected one-thread time | 22.83 h |

Parallelism improves wall time but not the frozen per-state p95 measurement. The p95 miss is
not a one-thread artifact.

## Frozen implementation

Implementation lock:

`data/analysis/live-agent-6553250/n4-candidate-pair-value-phase-a-implementation-lock.json`

Lock commit:

`5c940549e7ea3d11c645b392aaf66fdf53826b39`

Generated hashes:

- instrumented resident:
  `37baf749f8b8f615432d089ff979a1a7c56e984c56acf8b5102540377fa3a744`;
- generated runner:
  `cecbf8ecb88d094dc68da75e8388dbec55f5bee7e297e71cfd4a24209dd4e980`;
- release binary:
  `9854cb1314b2dad1f632a19e0af7d40b558a1f03bf907437c6283506fd57a00c`.

Canonical machine result:

`data/analysis/live-agent-6553250/n4-candidate-pair-value-phase-a-result.json`

## Downstream consequence

- **L2** and **L3** close with N4: no authorized material compatible-pair continuation
  surface exists for a learned ranker/evaluator.
- **E1** cannot reuse this exhaustive exporter. It would require a separately reviewed
  compact, runtime-feasible candidate-pair publication before any opening-prefix oracle
  protocol; none is authorized.
- **Phase B** remains forbidden.

## Safety

The resident, module registry, referee substrate, raw/sealed data, submission tools,
TestSession, and Arena were untouched. No alternative terminal outcomes were generated.
