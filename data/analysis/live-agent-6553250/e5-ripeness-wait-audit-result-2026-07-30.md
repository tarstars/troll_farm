# E5 on-site ripeness-wait audit

Date: 2026-07-30

Verdict: **`KEEP_RIPENESS_WAIT`**

## Question

When the resident stands on an unripe fruit tree, its selected zero-motion `MOVE` becomes
`WAIT`. Would removing only that candidate and letting the unchanged selector choose its
next-best task improve terminal local value?

## Method and integrity

The control is the exact 62,725-byte live source. A temporary diagnostic control adds
stderr only at the zero-motion/unripe conversion. A temporary alternate adds one
eligibility condition to the unique `fruit_candidates` guard; it does not force an action.

The frozen panel is reused seeds 0..59 against all six local opponents, both seats:
360 seed/opponent cells and 1,440 value games. Eight raw/probe sentinel cells add 16
seat-games.

All 360 value cells and eight sentinels complete. Raw/probe policy streams, opponent
streams, terminals, and outcomes are exact. Every first alternate divergence has an exact
common prefix and a matching control event on the same turn, unit, and zero-fruit plant.
Jobs 1 and 8 have identical value, sentinel, divergence, and normalized payload hashes.
No unexpected stderr or malformed command occurs; the sacred resident remains
`fff6669b…`.

As in E4, child processes use a fixed monotonic/entropy runtime because the immutable
`motion` opponent contains wall-clock search and randomized Rust collections. No bot
source byte changes.

## Mechanism

The probe records 162 wait turns in 57 episodes. Median episode length is one turn, mean
2.84, maximum 12. All events occur in the opening and target only PLUM (84) or LEMON
(78).

The alternate changes 33/360 seed/opponent cells across six seeds
(`6,7,28,29,45,52`), with 24 seat-0 and 21 seat-1 game activations. All six opponent
families activate. `ACTIVE_WAIT` passes every mechanism gate.

## Value

The whole-panel alternate-minus-control paired-margin delta is **+0.1056**, far below the
frozen +1.0 materiality gate. The activated-only mean is +1.152 but is descriptive because
activation is post-policy.

Seat means split: **−0.200** in seat 0 and **+0.411** in seat 1. Family means are motion
−0.300, taskplan +0.367, race −0.067, yield +0.242, ringfix3 +0.383, and chopharvest
+0.008. Only 14/360 cells are nonzero (8 positive, 6 negative).

Own score changes +0.150, opponent score +0.044, and wood edge +0.025. These are small,
heterogeneous downstream cascades, not evidence of a robust replacement.

## Decision

The mechanism is real, but the causal value fails magnitude and both-seat stability.
Under the frozen precedence the seat-0 loss independently returns
**`KEEP_RIPENESS_WAIT`**.

Keep the current on-site wait. Do not persist the alternate, build a candidate, expand the
map panel, or run an Arena cycle.

Machine summary:
`data/analysis/live-agent-6553250/e5-ripeness-wait-audit-result-2026-07-30.json`.
Analyzer: `cgauto/e5_ripeness_wait_audit.py`.
