# D66a source net-surplus lease result (2026-07-21)

## Verdict

**Close the fixed single-root lease at the consumed recovery gate.** Every planted root is removed
before the worker can collect two fruits and make a net-positive deposit. All six leases fail, no
lease executes a DROP, and only one of four tasks creates worker two. The fresh 1,024-row bank was
not opened.

The next representation must manage the whole pending bill across any surviving sources, carried
fruit, and bank deposits. It cannot bind the sole worker to one root, retry the same root, add more
fixed sources, or tune D66's wait/harvest count on these outcomes.

## Integrity

- The two eight-row consumed matrices are byte-identical, SHA-256
  `fd5ef3a95c4a76ee2b0c56318748456592655669837021743e9a13e4a64a6d45`.
- Exact D40 controls reproduce all four historical terminal, action, and state hashes.
- Direct-command, provenance, deposit-prediction, reward-identity, action-accounting, finite-state,
  and worker-cap checks are clean.
- Every task activates its D64i-diagnosed missing species and creates crops; no lease starts after
  worker two.

## Recovery failure

Across six source leases:

- PICK: 6;
- PLANT: 6;
- WAIT: 144;
- HARVEST: 3;
- two-fruit DROP: **0**;
- failed leases: **6 / 6**; and
- mean lease duration: 26.875 turns.

Worker two appears in only seed 9,830,014 seat 0. The other seed-9,830,014 seat, which D65 had
recovered, now remains at one worker. Both seed-9,830,002 seats remain at one worker. The sole
worker's presence on a root therefore does not protect it and sacrifices large productive windows.

One task records a bootstrap-call failure after a destroyed lease leaves fruit carried: the D65
trigger can identify another uncovered species before the experimental lease method's empty-carry
precondition is restored. Unchanged D40 later handles the carry. This is additional evidence for a
bill-level state machine rather than independent source transactions.

## Diagnosis-only value

The lease improves all four consumed margins by +29.0 on average, composed of +5.25 own score and
-23.75 opponent score, and reduces catastrophic losses from four to three. This likely reflects
the worker occupying/contesting a valuable cell and the opponent spending effort on the root. It
does not rescue the failed recovery invariant and cannot justify fresh value or candidacy.

## Decision

Reject fixed source waiting and preserve the still-unopened seeds 9,831,000--9,831,031. The next
experiment should first define a bill-capitalization state machine that:

1. treats bank + carry + all live/ripe own sources as one portfolio;
2. banks any carried bill fruit before another source investment;
3. acquires ripe missing currency from whichever source remains reachable;
4. invests only when no live source can make progress; and
5. returns to D40 immediately when the full bill is executable.

Before value, test this representation only on the four consumed failures with exact D40 parity.

## Reproducibility

```text
c9b3165d07f65b5394777fcc522be345aef06a277e5f21a5b3c4ab9e846a598a  d66a-source-net-surplus-lease-protocol-2026-07-21.md
7ee5943b9e64389de6285482c3f894e58edf4df6b44c5e28912246a3fad055d7  rust/src/rl_macro.rs
ab742d7f7657f5a7e15c8079f00404ba95b83d470790a9c01fc1b26aa432d1df  rust/src/bin/d66_source_net_surplus_lease.rs
feee65db2c7dec2ca5e441d99491b50b8ca5f11e0f1aac8b56acd465c86801d3  cgauto/analyze_d66a_source_net_surplus_lease.py
fd5ef3a95c4a76ee2b0c56318748456592655669837021743e9a13e4a64a6d45  each repeated consumed matrix
6ea4eb5068c497f0157f76c90f1179b91880e4e270c9f3a73c1768ecca8d9e2d  d66a-source-net-surplus-lease-result.json
```
