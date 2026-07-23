# D68a bill-capitalization portfolio result (2026-07-21)

## Verdict

**Close this exact adversarial-capacity portfolio at the consumed gate.** The controller recovers
both PLUM-only seed-9,830,014 tasks, funds worker two at turns 71/65, and eventually reaches three
workers. It nevertheless fails both decisive mixed-deficit seed-9,830,002 tasks: neither ever
makes the producer bill executable or creates worker two. The unopened fresh bank remains sealed.

This is a useful representation result, not a candidate. Redundant sources and bill-wide banking
can capitalize when a source family has positive net flow, but a snapshot count of hostile
choppers cannot bound repeated destruction across sequential replacement waves.

## Integrity

- The repeated eight-row matrices are byte-identical, SHA-256
  `d484dec78c9e37ed894e98fe301f0d964cdd6feec0d26e67e11eafd10e8b534b`.
- All four D40 controls reproduce D66's terminal, action, and state hashes.
- All four treatment prefixes reproduce D67's turn, state/action hashes, bootstrap mask, bank,
  carry, ripe stock, and missing species exactly.
- There are zero direct-command, provenance, deposit-prediction, reward-identity, formula,
  carry-before-investment, post-affordability, harvest-target, post-worker-two, action-accounting,
  finite-state, and worker-cap failures.
- All 43 source transactions contain one PICK and one PLANT. Thirty-one of 34 forced source
  harvest jobs deposit successfully.

## Consumed mechanism result

| Seed / seat | Control margin | Portfolio margin | Delta | Source investments | Harvest deposits | Missing-bank progress | Bill affordable | Final workers | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 9,830,002 / 0 | -140 | -105 | +35 | 11 | 11 | 0 | never | 1 | fail |
| 9,830,002 / 1 | -148 | -124 | +24 | 21 | 7 | 0 | never | 1 | fail |
| 9,830,014 / 0 | -123 | -20 | +103 | 5 | 6 | +3 | turn 70 | 3 | pass |
| 9,830,014 / 1 | -136 | +60 | +196 | 6 | 7 | +3 | turn 64 | 3 | pass |

Mean paired margin improves by **+89.5**, and all four task margins improve. That value is
diagnosis-only because the frozen recovery invariant passes only 2/4 and fails both originally
failed seats.

## Multilevel analysis

### Mechanics

The state machine is implementable and deterministic. It banks carried currency first, harvests
ripe owned sources from any surviving root, builds formula-derived concurrent portfolios, and
returns to exact D40 once the bill is deposited. The earlier transaction and placement failures
are not implementation blockers.

### Stock flow

The successful PLUM-only tasks make the exact required surplus: 5/6 PLUM investments produce 6/7
deposited fruits, net **+1** in each seat. Their PLUM bank rises from 3 to 6, the producer bill
crosses at turns 70/64, and worker two follows one turn later.

The failed tasks reveal species-coupled capital starvation. Their PLUM branch is productive: one
new PLUM source plus five deposits gives experimental net **+4**, taking PLUM bank to the required
5 or 6. LEMON is a replacement sink instead:

- seat 0: 10 LEMON investments, six deposits, net **-4**;
- seat 1: 20 LEMON investments, two deposits, net **-18**.

Maximum LEMON bank never exceeds its prefix value of 4, one below the producer cost. The controller
can harvest fruit and still make zero capital progress because it immediately spends the scarce
currency replacing threatened capacity.

### Controller representation

Current hostile capacity peaks at two workers, but those workers can destroy successive source
generations. D68's formula treats `T` as simultaneous denied sources and assumes remaining roots
can realize a three-fruit stock. It is therefore structurally optimistic under reusable adversarial
pressure. Increasing the count, changing the coefficient, or adding another placement heuristic
would tune the same failed representation on consumed outcomes.

The asymmetric result also explains why strong bots can afford workers while this recovery cannot:
they enter the capitalization decision with an established, cycling economy. D68 tries to finance
that economy from the final scarce unit of a missing currency after the opponent already has the
capacity to tax every replacement wave.

### Arena transfer

No fresh value, held-opponent robustness, confirmation data, candidate source, or Arena behavior
was tested. The large consumed margin gain partly reflects opponent effort spent destroying crops;
it cannot waive worker recovery or authorize submission.

## Decision and next hypothesis

Do not open seeds 9,831,000--9,831,031, tune the redundancy formula, or build a late rescue
candidate. D65--D68 now close deposited-seed rescue at the one-worker terminal-deficit boundary:
transaction, lifecycle, surplus lease, exhaustive placement, and adaptive redundancy have all
been tested.

Return to whole-game sequence ownership. The next discriminator is an **opening capitalization-
window audit**: determine whether a complete controller can establish diversified renewable flow
before reusable hostile chop pressure appears, and whether that earlier state causally enables the
later top-policy workforce transition. This must compare whole opening trajectories, not add
another source rule to the failed boundary.

## Reproducibility

```text
be59b11c22d2dd97063b4bc9dcaae5ee301d02085c5e0d4116204abc2e5659f8  d68a-bill-capitalization-portfolio-protocol-2026-07-21.md
7c6b07b91019741104b888b735823b6531e1eadafe311c90f599dde5e8b1c5be  rust/src/bin/d68_bill_capitalization_portfolio.rs
88e5648093d04526d3de99f4c9386a7e78e263841ff029c6de028462765ddab8  cgauto/analyze_d68a_bill_capitalization_portfolio.py
390397410bab24afcab1dafba4f4e4baedd6a19c233d4e5a7bb6cc49deb3cf6b  tests/test_analyze_d68a_bill_capitalization_portfolio.py
d484dec78c9e37ed894e98fe301f0d964cdd6feec0d26e67e11eafd10e8b534b  each repeated matrix
33f0bd462a0c46f85b7f80db928666cb2f89fc327bfd1fffef295552a11fa900  d68a-bill-capitalization-portfolio-result.json
```
