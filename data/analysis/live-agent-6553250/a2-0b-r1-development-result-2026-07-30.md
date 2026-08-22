# A2-0b r1 development result — READY FOR IMPLEMENTATION LOCK

The separately frozen r1 legality gate passes on the fixed 16-map development panel.
No implementation lock or 128-map confirmation existed when this record was written.

## Fixed panel

- seeds: 9,854,000–9,854,015
- matrix: 16 maps × two seats × eight frozen families = 256 tasks
- threads: 20
- terminal rows: 256/256
- sorted TSV SHA-256:
  `7daa4944bd9868873cbbfe602e9ca504c86515973ff7061ed2507f22747a9c21`
- sorted TSV bytes: 121,131
- first-vs-final r1 development TSV: byte-identical

## R1 legality gate

| mode | all issues | own | opponent | critical | unclassified |
|---|---:|---:|---:|---:|---:|
| legacy state + shadow checker | 10,782 | 44 | 10,738 | 0 | 0 |
| referee path | 10,132 | 0 | 10,132 | 0 | 0 |

Every row satisfies total = own + opponent, critical = own critical + opponent critical,
reason-count sums, phase/reason-count sums, exact task identity, family labels, margin
arithmetic, and terminal-state checks. Every observed reason belongs to the frozen
24-reason supported-noncritical set. The referee path's A2-controlled resident side emits
zero issues on this development panel.

Reason totals reproduce the immutable v1 smoke exactly:

- legacy: `move_blocked=10013`, `no_capacity=558`, `nothing_to_drop=11`,
  `opponent_plant_blocking=88`, `pick_stock_lost=2`,
  `train_affordability_lost=98`, `train_shack_blocked=12`;
- referee: `move_blocked=9584`, `no_capacity=524`, `nothing_to_drop=10`,
  `pick_stock_lost=2`, `train_shack_blocked=12`.

## Semantics accounting

- state-divergent tasks: 224/256
- legacy movement draws / true ties: 51,319 / 14,007
- referee movement draws / true ties: 52,434 / 14,562
- legacy development tail: four catastrophes, 1,051 negative-margin mass
- referee development tail: four catastrophes, 1,130 negative-margin mass

The result JSON retains per-mode, per-role, per-family, per-reason, and per-phase
accounting, first examples, score/margin deltas, and action/state hash-vector digests.

## Validation

- `cargo test --lib game::a2_referee_parity`: 18 passed, 0 failed
- analyzer compile: passed
- analyzer self-test: passed
- development analyzer verdict: `READY_FOR_IMPLEMENTATION_LOCK`
- result JSON SHA-256:
  `f750c063cc7a40c8787ff3492ada80a4c52a6added1c81e3a3e5232d91cd1fc9`

The optional trajectory bridge was also exercised on one complete map (16 tasks per
mode). Both mode files had exact task coverage, no duplicates, exact turn/state/command
counts, score agreement with the TSV, and zero decode/detector errors. All six frozen
`waste_sweep` detectors ran in both modes. This probe is validation only; the binding
detector gate remains the post-lock 2,048+2,048 confirmation pass.

Verdict: **READY_FOR_IMPLEMENTATION_LOCK**.
