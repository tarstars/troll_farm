# Elost same-tree occupancy deadlock

Date: 2026-07-31
Task: `20260731-elost-same-tree-occupancy-deadlock`
Verdict: **exact inherited same-tree assignment/collision loop**

## Exact game

- Game `897556967`, resident `6585765` /
  `41071067` seat 1, valid
  132–160 loss to Elost
  `6579290` / `40706516`.
- 300 turns, zero unknown official diff updates.
- Raw SHA-256 `7d2531710ecf7a3d6e71de923476e717272c6e65582cbb454d9c11d0d29f1b31`.
- Trajectory SHA-256 `2a809f316e03471cc9f8e54fdd1ae9410bde3abe9f3819b82677973d78ea7ec6`.

## Exact failure

Resident unit 1 (stats 1/1/1/1) is full with one wood on the LEMON at `(19,6)`.
It CHOPs on turns 55–57, then emits ten consecutive WAITs on turns 58–67.
Resident unit 2 (stats 2/1/0/2), also full with one wood, is assigned that same tree
before collision resolution on every turn 58–67.

After approaching, unit 2 alternates between `(18,5)` and `(18,6)` across eight
decision states on turns 61–68. The selector's exact pre-resolver pair is
`WAIT` plus `MOVE 2 19 6`; collision resolution prevents co-occupancy but its
single-turn detour does not reserve the capable on-tree worker's target. Unit 1 resumes
`CHOP 1` only on turn 68.

The current sticky-bank artifact, its tent-proximity parent, and the far-denial parent
each reproduce all 300 recorded command lines with zero stderr. The loop is therefore
inherited and is not caused by sticky banking.

## Narrow correction boundary

When a capable own worker already occupies a live tree, another worker must not receive
that tree's chop candidate for the current decision. This preserves the on-site worker's
CHOP candidate and prevents the selector from replacing it with `WAIT + off-tree MOVE`.
It is a same-tree ownership/compatibility rule, not a global oscillation tie-break or a
tree-order/value claim. Local materialization and focused validation may follow; no Arena
action follows from this audit.

## Successor validation

The fail-closed successor is
`cgauto/submissions/candidate-agent6585765-onsite-tree-owner-slim.min.rs`, 68,620 bytes,
SHA-256 `fab84019558e19491a0ce3408d584e4483f398a11da3140bf9adc5de30a90efc`.

On the exact teacher-forced stream, the parent still reproduces 300/300 recorded command
lines. The successor first activates at turn 48: unit 2 is already capable and standing
on live LEMON `(19,6)`, so it keeps that tree and changes from leaving it to `CHOP 2`.
During the reported turns 58–67, unit 1 emits `CHOP 1` on all ten decisions and unit 2
is routed elsewhere, eliminating the same-tree target and collision ping-pong.

Three new compiled boundary tests and all eight prior tent/banking regressions pass.
Eight unsealed both-seat smoke games against fixed `ringfix3` terminate with zero stderr.
This is mechanism and safety evidence, not an Arena-value estimate.
