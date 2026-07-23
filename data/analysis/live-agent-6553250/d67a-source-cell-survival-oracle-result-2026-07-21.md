# D67a source-cell survival oracle result (2026-07-21)

## Verdict

**Close single-source placement as a universal repair.** None of the 88 cells admitted by D65's
full player-favored placement domain survives long enough for the unchanged D66 lease to harvest
and deposit two fruits. Both failed seed-9,830,002 seats have zero viable cells; so do both matched
seed-9,830,014 seats.

Placement affects partial survival, but cannot complete capitalization. Do not tune the nearest,
wet, safety-margin, or coordinate tie-break from these consumed outcomes. The next representation
must create/manage redundancy across multiple sources and materialize the bill from any surviving
fruit.

## Integrity

- Two 88-row matrices are byte-identical, SHA-256
  `5aa61fbcd49999ec1a2e4edfd0f15c67b21c0acb5d8608c40a85547db2bf0f41`.
- The exact D65 prefix is reconstructed identically for every fork: LEMON at turn 11 after the
  first PLUM transaction on seed 9,830,002, and PLUM at turn 8 on seed 9,830,014.
- Candidate domains are complete at 23, 23, 21, and 21 unique cells with contiguous original-
  selector ranks; rank zero matches the D65 target in every task.
- Every fork executes one PICK and one PLANT. Direct-command, provenance, deposit-prediction,
  prefix, trace-hash, and success-accounting checks are clean.

## Exhaustive outcome

| Task | Cells | 0 harvests | 1 harvest | 2-fruit drops | Viable |
|---|---:|---:|---:|---:|---:|
| 9,830,002 seat 0, LEMON | 23 | 18 | 5 | 0 | 0 |
| 9,830,002 seat 1, LEMON | 23 | 17 | 6 | 0 | 0 |
| 9,830,014 seat 0, PLUM | 21 | 5 | 16 | 0 | 0 |
| 9,830,014 seat 1, PLUM | 21 | 5 | 16 | 0 | 0 |

All 88 leases invalidate and all 88 roots are absent when the lease returns. There are 45 cells
with zero harvests and 43 with one, but no cell obtains a second fruit or executes a DROP.

Geometry has a real but insufficient effect. One-harvest cells have mean own-vs-opponent door
safety margin 11.98 versus 5.80 for zero-harvest cells, and 69.77% are wet versus 17.78%. This can
inform source-state features later, but selecting the safest/wettest cell would still yield zero
completed leases on this exhaustive cohort.

## Decision

Do not open a geometry-family experiment or D65/D66's fresh value bank. Freeze a bill-level
redundancy preflight with these invariants:

1. bank carried missing currency before any new investment;
2. harvest any ripe live missing-species source without requiring one root to survive twice;
3. create more than one source only as a state-derived redundancy portfolio, never a fitted count;
4. stop investment as soon as bank + carried acquisitions can execute the producer bill; and
5. retain exact D40 for every unrelated decision.

First prove on mechanism-only roots that the portfolio can produce net missing currency under
opponent pressure. Complete-game value and candidacy remain downstream.

## Reproducibility

```text
96b47df66008f04d76cb8e2a6ebf6ed1c7882f349ef8d8e87b4e84a022823312  d67a-source-cell-survival-oracle-protocol-2026-07-21.md
a7167a53554dfddb294680a2ac4040e04b8d238875b9a9c1a6e22b8e93608e07  rust/src/rl_macro.rs
c372010a6474414a1eb1468c5530fafc1ccba054839bd7a3974e9f57c76cff4f  rust/src/bin/d67_source_cell_survival_oracle.rs
4f226de5a8e06fc5934b7c728edca4988e56828010e221efe21fabb9df2c4d91  cgauto/analyze_d67a_source_cell_survival_oracle.py
5aa61fbcd49999ec1a2e4edfd0f15c67b21c0acb5d8608c40a85547db2bf0f41  each repeated oracle matrix
40e8951a6441e917b5762b44fe92a9a1f7db92c97e00d34c690382ce0572ebe5  d67a-source-cell-survival-oracle-result.json
```
