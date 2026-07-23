# D53a atomic TRAIN-bill reservation — result (2026-07-21)

## Verdict

**Reject D53a at transaction integrity before workforce interpretation.** The per-worker bill
reservation eliminates all 12,044 D52b worker-two budget failures, but 168 worker-three attempts
still lose currency before TRAIN. All are budget-only; none are shack or unexplained failures.

The repeated runs are deterministic and show descriptive workforce improvement, but the frozen
decision rule forbids treating it as a workforce pass/fail while transaction integrity fails.
Score direction, support, candidate value, and platform outcomes remain ignored.

## Integrity and transaction result

- Both exact 160 x 8 matrices are byte-identical and complete.
- All 468 parent-conditioned opening TRAIN commands and specs match; cap violations are zero.
- Every attempt partition balances and unexplained failures remain zero.
- Worker-two TRAIN: 1,524 attempts, 1,056 successes, 468 temporary shack-only opening failures,
  zero budget failures.
- Worker-three TRAIN: 482 attempts, 314 successes, 168 budget-only failures.
- Worker-four TRAIN: 9 attempts and 9 successes.
- Both runs complete in 16.92 s and 17.75 s at about 19.4 effective CPU cores.

## Descriptive mechanism counters (not an eligible workforce verdict)

| Mechanism | D52a V3 | D53a V4 | Delta |
|---|---:|---:|---:|
| Worker 2 | 948/1,280 (74.06%) | 1,056/1,280 (82.50%) | +108 cells |
| Worker 3 | 252/1,280 (19.69%) | 314/1,280 (24.53%) | +62 cells |
| Worker 4 among max-four | 4/640 (0.63%) | 9/640 (1.41%) | +5 cells |
| Successful crop | 1,280/1,280 | 1,280/1,280 | unchanged |
| Changed from V2 parent | 876/1,280 | 984/1,280 | +108 cells |

These counts do not satisfy the original workforce thresholds, but transaction failure is the
earlier binding gate.

## Causal interpretation

V4 passes the exact `training_cost` to every producer independently. Each producer therefore
allows a PICK only when the shared inventory appears strictly above that resource's bill. Multiple
workers select commands from the same pre-action snapshot, however, and no allocator ledger
decrements the apparent surplus after the first planned PICK. Two workers can each spend the same
single surplus unit; PICK resolution then leaves inventory below the bill.

This explanation is source-level deduction from the remaining exact budget-only class. D53b must
verify it directly by counting successful cost-currency PICKs and resource oversubscription on the
168 failed attempts while reproducing every D53a field. Only then may D54 add a shared intra-turn
inventory ledger. Do not change worker specs, producer counts, caps, shack rules, or workforce
thresholds.

## Evidence

- protocol SHA-256:
  `5ff6dd6ac01db8b84a7fbb22610af8e5ea5fe7f5df0e10635b0f085d428050e2`;
- repeated matrix SHA-256:
  `d378288dd24b992a027583ae6270fbff358311f34b8da666a5241880347c021b`;
- result SHA-256:
  `281699fc0a10b0904ec55a3be0fc8787698fcd7eb2f02602dcaefd876f94ee61`;
- runner SHA-256:
  `dd18c52790db4519e6d381afa38a2d42d010eb2361fd03eff7d53a1bb2e672e2`;
- V4 strategy SHA-256:
  `cf5cdb1df23033f88f465a8213d47b4291137c916d539f8861ba040f4363062a`;
- analyzer SHA-256:
  `0b32619bedbc953e36f9597d6a58181b1574b7f2862e144abb1d4cfe647c0ccd`;
- focused verification: five strategy tests, sixteen runner tests, and eleven D52/D53 Python tests
  pass.
