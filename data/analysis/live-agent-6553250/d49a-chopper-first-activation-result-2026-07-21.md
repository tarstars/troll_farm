# D49a chopper-first reservation-order activation — result (2026-07-21)

## Verdict

**Reject D49 before value evaluation and keep both later banks sealed.** Moving the designated
maximum-chop worker to the front of each simultaneously free suffix is deterministic and strongly
active, but it violates the frozen zero-integrity-failure gate. The candidate records 491 actual
promotions and changes 226/256 action hashes (88.28%), while producing 12 TRAIN-currency deposit
prediction failures in seven tasks.

No score, margin, own-score, opponent-score, workforce, crop, or tail outcome from this activation
bank was summarized or used. Seeds 9,786,000--9,786,031 and 9,787,000--9,787,031 remain untouched.
Do not salvage D49 by broadening the reorder, changing its tie break, combining it with D46--D48,
or inspecting value on another bank.

## Mechanical audit

- Exact D40 control, D49 candidate A, and D49 candidate B each complete all 256 tasks.
- Candidate A and B are byte-identical.
- The candidate sees 2,072 eligible free-worker suffixes and promotes the designated chopper 491
  times.
- Candidate action hashes differ from D40 in 226/256 tasks, inside the frozen 20%--90% corridor.
- Illegal-command, provenance, order-integrity, worker-cap, reward-identity, and action-count
  failures are all zero.
- The sole failed counter is TRAIN-resource deposit prediction: 12 failures in seven tasks.
- Exact D40 control has zero relevant deposit-prediction failures on the same task grid.

The seven affected cells are:

| Seed | Seat | Opponent | Failures |
|---:|---:|---|---:|
| 9,785,000 | 1 | `norx_native_three` | 4 |
| 9,785,002 | 1 | `legend_balanced` | 1 |
| 9,785,005 | 0 | `legend_balanced` | 1 |
| 9,785,005 | 1 | `silver_boss` | 2 |
| 9,785,009 | 1 | `script_boss` | 1 |
| 9,785,012 | 0 | `norx_native_three` | 1 |
| 9,785,012 | 1 | `mybot` | 2 |

## Interpretation

D49 confirms that reservation order is a genuine trajectory-level control variable: a one-worker
permutation changes almost nine tenths of complete action streams. It also exposes a missing
executor invariant. A persistent acquisition job freezes its expected deposited inventory when it
is selected, but an interactive opponent can alter the fruit available before acquisition. At
DROP, actual PLUM/LEMON/APPLE/IRON inventory can therefore disagree with the amount reserved for
the pending TRAIN bill. Reordering changes target and timing interactions enough to reveal this
latent mismatch even though exact D40 has none on the same bank.

This does not authorize a post-result D49 repair. The result instead localizes two requirements for
future joint scheduling: allocation must be coordinated, and resource reservations must be
revalidated transactionally at acquisition/job boundaries rather than assumed immutable for a
whole persistent job. A new experiment must establish that executor property independently before
another assignment policy is valued.

## Gate result

| Gate | Result |
|---|---:|
| Complete exact deterministic repeat | pass |
| Zero integrity failures | **fail: 12** |
| At least 256 eligible suffixes | pass: 2,072 |
| At least 128 promotions | pass: 491 |
| Changed action hashes in 20%--90% of tasks | pass: 226/256 (88.28%) |

Formal conjunction: **fail**.

## Evidence

- protocol SHA-256:
  `fdb41df1a1f63781a4dc3fec5a0fee8c687b1b632a9fae6801cfbe03b83e1196`;
- control TSV SHA-256:
  `fcd6b6368bc331857a0d655b20658d4cf2eecc4eb3b6849aadc891c53bc9e10d`;
- candidate A/B TSV SHA-256:
  `97b4f20ab17799386c866a4df1baaa586a170dfb87f98691e5c46fe22f1515bd`;
- result JSON SHA-256:
  `9e1428cfc145af2f9a1894df0058feb0258d1ba3214bbcd98da827362a805b7f`;
- runner SHA-256:
  `572b1df2b060e30390d2631407dedcb73071e264e9a7142060fa89474fb2ab84`;
- analyzer SHA-256:
  `7ad54cbde3d4ffbab740c8c6dec39b1de7ca04be476374e1a9b1736c6f8d1e3a`;
- focused verification: two Rust runner tests and two Python analyzer tests pass.
