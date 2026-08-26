# The direct two-generation comparison — POOLED VERDICT over 10 pairs, and the Arena is stopped

**Answer: +0.17 as measured, ≈0.00 once the pairing bias is removed. IMMATERIAL.**

Arms, both blocks: **A = the Door-1 challenger** `547fa706…` (the champion of record) ·
**B = the very-old resident** `98628e98…`. This is the owner's gold standard — the distance
across two generations of work, measured directly in one ladder rather than composed across
nights. The composed estimate carried into it was about **+1.24**.

Block 2's verdict is reconstructed from the state JSON at its closing commit `0cd83d12`,
because the runner erased the ledger that held it — the same defect that ate block 1's, and
it was expected this time. Block 1's record: `door1-vs-old-block1-verdict-2026-08-22.md`.

## The numbers

| block | pairs (A − B) | mean | re-paired | drift-cancelled |
|---|---|---|---|---|
| 1 | 0.0, +0.4, +1.9, −0.1, +0.5 | **+0.54** | +0.075 | +0.31 |
| 2 | +0.7, −0.7, −1.3, 0.0, +0.3 | **−0.20** | −0.40 | −0.30 |
| **pooled (n=10)** | all ten above | **+0.17** | −0.16 | **+0.00** |

Pre-registered arithmetic: σ_pair 1.5 → winner bar **0.930** at n=10, materiality floor
**1.0**. The result is far below both, from either direction, and the two blocks fall on
opposite sides of zero.

**Arithmetic outcome: IMMATERIAL.** KEEP/REVERT remains the owner's; the runner computes and
does not rule. The nine named costs travel with this verdict unchanged.

The drift-cancelled column applies `docs/METHODS-LEDGER.md`,
`paired-order-carries-the-drift`: arm A always occupies the earlier slot of its pair, so a
within-night trend enters every difference with a fixed sign; re-pairing each A against the B
**before** it brackets the true value and the average cancels a linear drift. Here it barely
matters — the two blocks' biases point opposite ways and the pooled figure moves from +0.17 to
+0.00. That agreement is itself worth recording: at n=10 the answer is the same however it is
paired.

## What it means

The composition said the two generations were worth about **+1.24**. Measured directly, over
ten pairs on one ladder, they are worth **nothing we can distinguish from zero**.

This is not a failure under the owner's reframing (`docs/DISCUSSION-architecture-over-score-2026-08-22.md`):
the intervening step was a pure deletion kept on score-neutral grounds, and the aim of the
project is architecture rather than ladder points. What it does close is a question that was
open all week — **whether the fixture-driven cure programme has produced a demonstrable ladder
gain. On this measurement it has not**, and the measurement is now the strongest single piece
of evidence in the architecture discussion.

It also lands beside a second finding from the same day: cure α's healing has never been read
with a progress term, so its headline may be counting silenced detectors rather than working
trolls (`coordination/tasks/20260822-alpha-progress-regrade.md`). The two together say the
same thing from opposite ends — **we have been measuring cures by the alarm going quiet, and
the ladder cannot see the result.**

## The Arena is stopped, deliberately, and in the right state

Owner ruling 2026-08-22: *"let this block finish, then halt."*

- 16:04:38Z — block 2 completed; the runner published its verdict and, having no session
  awareness, opened block 3 and submitted arm A (submission `41178858`).
- 16:04:57Z — the watcher saw 10 of 10 marks read and armed `NIGHT-HALT`.
- 16:07:55Z — the runner halted at its next loop: *"night_runner stopped: halt file present.
  No further mutations; resume or rule manually."*

**The champion `547fa706…` is what is left sitting on the ladder**, which is the resting state
we wanted, and no further arm will be submitted. To resume: delete
`NIGHT-HALT` in the runner's working directory and start the service.

**Still not fixed:** the runner erases its ledger and restarts itself at the end of every
block. The watcher was a one-night workaround. A permanent fix — a session-aware branch, or a
halt-on-completion flag — is unwritten and unowned.
