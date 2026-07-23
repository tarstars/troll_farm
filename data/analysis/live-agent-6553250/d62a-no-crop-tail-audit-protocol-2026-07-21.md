# D62a no-crop tail audit — diagnostic protocol (2026-07-21)

## Question

D62a observed two zero-crop episodes among 1,669 PPO training completions. Because a zero-crop
episode never unlocks any semantic option, its entire policy path is deterministic balanced. Are
these failures ordinary full-horizon D40 trajectories, or early referee termination after the
shared plant stock disappears?

This is classification of a failed gate, not checkpoint evaluation or protocol rescue.

## Frozen audit

Run filtered-balanced D62 semantics independently on task indices 0--2,047 of the exact training
stream beginning at seed 9,802,000: 128 official maps, both seats, and all eight frozen opponents.
Use 20 threads. Record every terminal's turn, score, workforce, crop counts, live plant count,
initial inventories, selected renewal jobs, action hash, and state hash.

For every zero-crop task classify termination as:

- `turn_limit` when terminal turn is 301; or
- `plant_stock_stall` when it ends earlier under the exact referee stall rule.

Starting inventories make at least one seed type materially available when any of the first four
items is positive; report that separately. Do not call a stall “unavoidable” merely because the
balanced controller reached it. No alternate policy, threshold, or checkpoint may be selected.

## Decision use

- Full-horizon zero-crop tasks support retaining a universal crop invariant.
- Early plant-stock stalls show that the current gate mixes establishment-policy failure with a
  tail end condition. Future protocols should require 100% crop creation conditional on a frozen
  feasibility/end-condition classification and report the unconditional rate separately.

In neither case may the consumed D62 checkpoint be rescued: its independent 0/512 deterministic
movement failure remains decisive. No platform action is authorized.
