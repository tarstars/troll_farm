# D65a missing-currency seed-source result (2026-07-21)

## Verdict

**Close the exact one-seed source transaction at the consumed recovery gate.** The transaction is
mechanically correct and valuable on these four diagnostic tasks, but it creates worker two in
only two of four. Per the frozen protocol, the fresh 1,024-row repeated value matrix was not run.

This is not evidence against source access in general. It shows that merely planting each missing
species once and returning to unchanged D40 does not guarantee that the new source survives,
matures, and deposits the bill. The next eligible work is a source-survival audit on the two failed
seed-9,830,002 trajectories, not a count, cell, timing, or species-order retune.

## Integrity and mechanism

- The eight-row consumed grid contains D40 and repair for both seats of seeds 9,830,002 and
  9,830,014 against `resident`.
- Every D40 terminal, action, and state field reproduces the original D64 controls exactly,
  including all four action and state hashes.
- Illegal-command, provenance, deposit-prediction, source-job, bootstrap, finite-state,
  reward-identity, and action-accounting failures are all zero.
- Six source transactions each execute exactly one deposited-seed `PICK` and one `PLANT`.
- Every task plants its D64i-diagnosed terminal missing species, every task creates crops, no
  transaction occurs after worker two, and the maximum workforce is two.

## Recovery result

| Map | Seats reaching worker two | Source transactions per seat | Species planted |
|---|---:|---:|---|
| 9,830,002 | 0 / 2 | 2 | PLUM, then LEMON |
| 9,830,014 | 2 / 2 | 1 | PLUM |

Seed 9,830,002 is the decisive falsification. Both sides plant the initially largest uncovered
PLUM coordinate at turn 8 and the still-uncovered LEMON coordinate at turn 11, yet both finish
with one worker. Seed 9,830,014 plants PLUM at turn 8 and both sides reach worker two.

The repair improves all four consumed margins and regresses none:

- mean own-score delta: **+32.5**;
- mean opponent-score delta: **-12.5**;
- mean margin delta: **+45.0**; and
- catastrophic losses: **4 -> 2**.

These are diagnosis-only consumed outcomes. They cannot waive the universal recovery gate or
justify a candidate.

## Decision

Do not run D65 fresh seeds 9,831,000--9,831,031 and do not construct or submit a candidate. Trace
the two seed-9,830,002 repair trajectories at every boundary and source lifecycle event. Determine
whether each planted PLUM/LEMON source is destroyed, renewed before deposit, harvested by the
opponent, inaccessible when ripe, or simply too late to complete the bill. Compare the two
successful seed-9,830,014 trajectories without changing D65 behavior.

## Reproducibility

```text
a02157119501e23e1f7b2413ad0241bdbac7153ac351e851441dde20784064e9  d65a-missing-currency-seed-source-protocol-2026-07-21.md
152571cd089b2c77f5f4316d024f5530e0a9678594cb72602e005805168b5ac3  rust/src/rl_macro.rs
7ea09949c68237de6ce53b2457e6ee1c8aaff311290a177806a73d1d7d966224  rust/src/bin/d65_missing_currency_seed_source.rs
686d03e4d048768e8369bb07d31b8e10182f9f61a21ae32e7c09163184ea4562  cgauto/analyze_d65a_missing_currency_seed_source.py
2bb4154c572b1abb32dc132255e9e31c015300416f4a38259a409773f55f4216  d65a-consumed-recovery-final-9830002-9830014.tsv
8bc4e54252c3d1a21676e1a4bd0cb11f02a29774723368bde16296a5db5d9aed  d65a-missing-currency-seed-source-result.json
```
