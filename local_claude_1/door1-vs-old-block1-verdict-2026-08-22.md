# Session 3, block 1 — the direct two-generation comparison. VERDICT, recovered.

**Reconstructed 2026-08-22 from the state JSON at commit `fe0ed7f8`, because the runner
erased the ledger that held it.** See "How this was lost" below. No number here is new: all
ten reads are exactly as `night_runner` recorded them.

Arms: **A = the Door-1 challenger** `547fa706…` (`candidate-door1-pure-deletion.rs`, the
champion of record) · **B = the very-old resident** `98628e98…`
(`submitted-agent6593838-readable-no-orchard.rs`). This is the owner's **gold standard**:
the two-generation distance measured directly in one block instead of composed across
nights. The composed estimate carried into it was about **+1.24**.

## Read log

| # | arm | agent | read (UTC) | battles | score | rank |
|---|---|---|---|---|---|---|
| A1 | challenger | 6643835 | 02:51:30Z | 160 | 23.7 | 26/176 |
| B1 | very-old | 6644257 | 04:48:57Z | 160 | 23.7 | 26/176 |
| A2 | challenger | 6644785 | 06:46:25Z | 160 | 21.3 | 40/176 |
| B2 | very-old | 6645217 | 08:43:59Z | 160 | 20.9 | 43/176 |
| A3 | challenger | 6645883 | 10:41:42Z | 160 | 23.8 | 26/176 |
| B3 | very-old | 6646271 | 12:39:20Z | 172 | 21.9 | 37/176 |
| A4 | challenger | — | 14:36:54Z | 160 | 21.8 | 39/176 |
| B4 | very-old | — | 16:34:22Z | 160 | 21.9 | 39/176 |
| A5 | challenger | — | 18:31:50Z | 160 | 21.8 | 38/176 |
| B5 | very-old | — | 20:29:2xZ | 160 | 21.3 | 43/176 |

## Verdict

- Pairs (A − B, adjacent, as pre-registered): **0.0, +0.4, +1.9, −0.1, +0.5**
- **Mean Δ = +0.54**, n = 5. Pre-registered arithmetic: σ_pair 1.5, SE 0.671, winner bar
  1.315, materiality floor 1.0.
- **Arithmetic outcome: IMMATERIAL** — below the 1.0 floor. KEEP/REVERT remains the
  owner's; the runner computes, it does not rule.
- Empirical pair spread (honesty clause): SD 0.766, well under the planning σ.
- The nine named costs travel with this verdict unchanged.

**Symmetrised for the pairing defect** (`docs/METHODS-LEDGER.md`,
`paired-order-carries-the-drift`): re-pairing each A against the B **before** it gives
−2.4, +2.9, −0.1, −0.1 → mean **+0.075**; the drift-cancelled estimate is **+0.31**. The
within-night slope was −0.18 points per slot. Both readings are far below the floor, so the
defect does not change this verdict's direction — but the honest figure to carry forward is
**+0.3 to +0.5, not +0.54 alone**.

## What it means

The composed estimate said the two generations of work were worth about **+1.24**. Measured
directly, in one block, on the same ladder within one night, it is **+0.3 to +0.5 and
immaterial**. The composition was optimistic, as its own caveat warned it might be
("composition chains ACROSS nights … the composed number is evidence, not gold").

This is the number the strategic discussion in
`docs/DISCUSSION-architecture-over-score-2026-08-22.md` anticipated. Under the owner's
reframing it is not a failure — the intervening step was a pure deletion kept on
score-neutral grounds — but it does close the question of whether the fixture-driven cure
programme has produced a demonstrable ladder gain. On this measurement it has not.

## How this was lost, and what survived

At 20:29:26Z the runner completed the block, wrote the verdict into the ledger, and then —
because the mean did not land between the floor (1.0) and the bar (1.315) — took branch 2
of the owner-approved post-B5 tree and **re-opened "session 3" onto the same two file
paths**. `open_session3()` rewrites the ledger with a fresh header, so the B5 row and the
verdict block were erased **before** the commit that published them; they exist in no
commit. The state JSON was written with the completed state and survived at `fe0ed7f8`,
which is where every number above comes from. A fresh 5-pair block of the identical
comparison started at once and is running now.

The behaviour was predicted before it happened, by running the real loop against the real
file paths with the Arena, git and lint stubbed. The shipped post-B5 test never used those
paths — session 2 lived on different ones — which is why it passed. Two consequences, both
still open:

1. The runner has **no session awareness**: it will do this again at the end of every block,
   forever, unless a branch is added or it is halted (`NIGHT-HALT` in the repo root).
2. The morning sheet published at the same moment is hard-titled *"session 2: Door-1
   challenger vs cure-C resident"* and adds night 1's +1.02 to this mean as a "composed
   distance" — which double-counts, because this block **is** the direct measurement of that
   composition. The numbers in it are this block's; its labels are not.
