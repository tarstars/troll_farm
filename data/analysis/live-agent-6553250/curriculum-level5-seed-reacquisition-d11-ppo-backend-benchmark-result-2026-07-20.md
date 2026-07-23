# Curriculum Level 5 D11 PPO backend benchmark result — 2026-07-20

## Frozen question

Can the neighboring project's YT RTX 4090 workflow execute the preregistered D11 PPO job with
functional parity and reduce projected end-to-end time for the sole four-million-transition run
to at most 80% of local time?

This is the conditional benchmark authorized by learning protocol SHA-256
`48922c1f7fe4d20936f3d6c1e8aed6b6040c9eb900e231d109fd931057fc368b`.  Both arms started from
NPZ SHA-256 `182a7fd6e738070a38c8f31d617824be851f099d9bc7071d6720dbedaa34cd99`, used model seed 137,
environment stream 7,200,000, one million transitions, and the same optimizer, rollout, teacher
auxiliary, and exact 500-episode development bank.  The only intended difference was CPU versus
CUDA execution.

## Timing

| Component | Local CPU | YT RTX 4090 |
|---|---:|---:|
| Inner trainer wall | 1,005.215 s | 102.364 s |
| Effective trainer throughput | 994.812 transitions/s | 9,769.023 transitions/s |
| Rollout time reconstructed from update logs | 157.104 s | 39.549 s |
| Non-rollout update time reconstructed from update logs | 830.542 s | 56.059 s |
| Evaluation | 17.421 s | 6.496 s |
| Complete local wrapper / YT operation | 1,007.201 s | 190.018 s |

YT trainer throughput is **9.820x local**.  The successful operation
`238b228b-9a1e6a82-42e03e8-7a4e73d7` started at `2026-07-19T23:43:06.030641Z` and finished at
`2026-07-19T23:46:16.048679Z`.  Allocation/startup to entrypoint was 30.054 s; the entrypoint took
154.609 s before output upload, including 45.876 s of offline runtime setup and 106.321 s around
the trainer subprocess.  Post-entrypoint output handling occupied the remaining approximately
5.355 s.  The 469,280-byte result archive took 1.15 s to retrieve and extract in a separately timed
repeat.  Initial package and input-upload launcher walls were approximately 2.3 s and 9.7 s.

Using the measured one-million body, adding the second final evaluation, and conservatively
scaling trainer-wrapper overhead with each additional million gives:

- projected local four-million end-to-end: **3,988.004 s = 66.47 min**;
- projected YT four-million end-to-end: **511.339 s = 8.52 min**; and
- projected YT/local fraction: **12.82%**, comfortably below the frozen 80% time ceiling.

## Functional parity

Both arms are finite and pass L5A plus the complete opponent-mechanism gate.

| Metric | Local | YT | Absolute difference | Frozen tolerance | Verdict |
|---|---:|---:|---:|---:|---|
| Overall success | 96.800% | 96.400% | 0.400 pp | 3 pp | pass |
| Nontrivial success (diagnostic) | 95.608% | 94.257% | 1.351 pp | — | informative |
| Worst recipe | 91.803% | 85.246% | **6.557 pp** | 5 pp | **fail** |
| Worst height | 95.935% | 92.800% | 3.135 pp | 5 pp | pass |
| Terminal crop | 97.400% | 97.400% | 0.000 pp | 5 pp | pass |
| Renewable harvest | 97.200% | 97.200% | 0.000 pp | 5 pp | pass |

The sole failure is the hybrid-chopper recipe: local solved 56/61 and YT solved 52/61 on the same
seeds.  That four-episode difference is 6.557 percentage points and therefore exceeds the frozen
backend-parity limit.  It is small in sample count but cannot be waived, rounded down, or retested
after observation.

## Decision

**Select local CPU for the one allowed four-million-transition PPO run.**  YT easily passes the
economic time test but fails the prerequisite parity test, so the protocol's conjunction is false.
The benchmark checkpoints remain throughput evidence and are not candidate checkpoints.  There
will be no benchmark rerun, alternate seed, or tolerance revision in this cycle.

The selected fresh run keeps the clone initialization, changes model seed to 139 and environment
stream to 7,400,000, evaluates Stage A at one million, and reaches the final gate at four million
only if Stage A passes.

## Evidence and hashes

- local checkpoint: `d0a22f9dd819411d646378b89ca0db105ebe5b4bcb352fd26495d35a42508bae`;
- local evaluation: `59f250c2be61f887b0bcc3af5fe80a813e5af9094b22b329fa92e7b125b24883`;
- local summary: `3beeea176e3383a63bd79b71e9e281cfb072fcf6d3d29f87d4198fa6b306c37b`;
- local outer timing: `286e6811337576fceb51b9e655b8b2ea8db3ea4c24605e4f7659b3ebdfe3b161`;
- YT checkpoint: `d0f206db0832a2a3a072115f5513c47109ad1f4dacee3b2930205483839a3044`;
- YT evaluation: `575874a24d73e97619492bd1fc6c48f5e8869773ad2417db1d7eeb28931dc7bf`;
- YT summary: `e4f3c9f520de0020eb620b24b572cb849146c55130da6a8e192de9fd051e659d`;
- YT output archive: `9893110027714df5288cbbe6745141c40dcae43b6cf20c33a2e76d7c285a5eaf`;
- YT metadata: `852afff29887367b1e3f77140362dda4fa3f23ec1f42332f7b45055dea2e445a`.

