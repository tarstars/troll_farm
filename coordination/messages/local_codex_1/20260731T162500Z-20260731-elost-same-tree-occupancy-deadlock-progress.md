---
type: PROGRESS
task_id: 20260731-elost-same-tree-occupancy-deadlock
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T16:25:00Z
requires_ack: false
---

Exact game `897556967` is reconstructed: 300 turns, zero unknown updates, valid 132–160
loss. Unit 1 is full with wood on LEMON `(19,6)` and WAITs on turns 58–67; full unit 2
receives `MOVE 2 19 6` before collision resolution on all ten turns and alternates across
eight states. Current, tent parent, and far-denial parent reproduce 300/300 commands, so
the loop is inherited.

Narrow successor: when a capable own worker already occupies a live tree, exclude that
tree from other workers' chop candidates for the current decision. No global tie/order,
cross-turn memory, or Arena action.
