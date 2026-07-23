# D54a shared PICK-ledger workforce preflight — result (2026-07-21)

## Verdict

**The TRAIN transaction is fully repaired; reject the workforce mechanism before support.** Every
worker-three and worker-four TRAIN attempt succeeds, with zero budget, shack, or unexplained
failure. The scheduler nevertheless reaches worker two in only 1,056/1,280 cells (82.50%), worker
three in 324/1,280 (25.31%), and worker four in 9/640 max-four cells (1.41%). It therefore fails all
six frozen workforce gates by a wide margin.

No support, score direction, candidate value, TestSession, submission, or Arena conclusion is
opened.

## Integrity and transaction result

- Both exact 160 x 8 matrices are complete and byte-identical.
- All 468 parent-conditioned opening TRAIN commands/specs match; cap violations are zero.
- Every attempt partition balances.
- Worker two: 1,524 attempts, 1,056 successes, and only the 468 known temporary opening
  shack failures.
- Worker three: 324 attempts and 324 successes.
- Worker four: 9 attempts and 9 successes.
- Budget-inclusive and unexplained failures are zero at every target.
- The two runs complete in 17.15 s and 17.81 s at about 19.4 effective CPU cores.

## Workforce result

The cap and post-producer variants are identical through worker three:

| First worker | Worker 2 | Worker 3 |
|---|---:|---:|
| hp2 | 130/160 (81.25%) | 44/160 (27.50%) |
| balanced | 134/160 (83.75%) | 37/160 (23.13%) |

Among max-four configs, hp2 reaches worker four in 4/160 for either producer count; balanced reaches
0/160 with one producer and 1/160 with two. Every config creates a crop in 160/160 cells, and
996/1,280 complete signatures differ from the V2 parent.

D54 recovers only ten additional worker-three cells over D53, despite eliminating 168 failed
attempts. Those failures were repeated attempts concentrated in a small set of trajectories. Most
cells never issue the next TRAIN at all because the exact bill never becomes affordable.

## Multilevel interpretation

- **Transaction:** closed successfully. Per-worker cost reservation plus a shared planned-PICK
  inventory is sufficient; no further reserve padding, command-order changes, or transaction
  telemetry is eligible.
- **Role surface:** one/two post-producer settings now have identical worker-two/three reach. Their
  earlier divergence was a spending artifact, not evidence that fewer producers fund better.
- **Renewable mechanism:** universal crop creation is too weak a metric. The scheduler can plant
  while failing to reproduce the specific PLUM/LEMON/APPLE/IRON stock vector needed by the hybrid
  worker.
- **Workforce:** worker two remains enabling rather than sufficient. Of 1,056 worker-two cells,
  only 324 ever make the hybrid bill affordable and all 324 train successfully.
- **Next abstraction:** distinguish deposited shortage from currency already carried, harvestable
  ripe supply, and absent/depleted source species. D55 must inspect stock flow without changing V5
  commands or viewing score/support outcomes.

## Gate result

All integrity, opening, cap, crop, activation, and transaction gates pass. Every worker-two,
worker-three, and worker-four gate fails. Formal conjunction: **fail**.

## Evidence

- protocol SHA-256:
  `2231f5972c0a5243a1ade1771d79a9e3b827e2ce8fab6988137c0917836a5175`;
- repeated matrix SHA-256:
  `66f99af783e855fc64e48df3990bf04469fe1dea07798ede6b95a4fea17a1263`;
- result SHA-256:
  `58b88a2ea9e8e6931052e7efa17018d050e1bfafe086a782197a824067281803`;
- runner SHA-256:
  `99aec36964f8d6b865f9ad34801f97565877d7ddb9e3e50aa004c0152fea8e3e`;
- V5 strategy SHA-256:
  `f5ec11f3ec8b480e82bbbc6c39e7caa77efdb2a678e0d5a190eaf0035c8e098d`;
- analyzer SHA-256:
  `027df3b53722138f6682425b9c94431c4e2b415c25757ba12684c08b1c801fff`;
- focused verification: six strategy tests, seventeen runner tests, and four D53/D54 analyzer tests
  pass.
