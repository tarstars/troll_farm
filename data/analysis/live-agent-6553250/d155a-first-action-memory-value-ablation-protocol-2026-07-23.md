# D155a first-action-memory conditional value ablation — frozen protocol

Date: 2026-07-23  
Status: frozen after D154a closed fixed snapshot slices, before building or fitting D155

## Hypothesis

D152's second-action value is conditional on the exact selected first intervention. The current
64-state snapshot records aggregate economy and a four-way previous proposal kind, but omits first
jobs, owners, targets, deposits, ranks, and expert support. Join the exact D148 selected-first action
features into every D153 group and test whether explicit memory restores map-fold transfer.

Require an exact 909-task first-action join: one selected first slot per task, matching D152's
`first_boundary`/`first_slot`, finite 379-wide features, unchanged 16,228 second actions/values, and
all original slot-zero controls.

Retain D153's objective, width 16, seeds `15301--15304`, 80 epochs, batch 64, optimizer, eight
outer folds, ten fork workers × two threads, and exact relative control anchoring. Compare:

| Name | Construction | Parameters |
|---|---|---:|
| `snapshot_compact` | concat current state64 + second semantic/context51, `115 -> 16 -> 1` | 1,873 |
| `history_concat_compact` | concat state64 + first compact51 + second compact51, `166 -> 16 -> 1` | 2,689 |
| `history_bilinear_compact` | ReLU context `(state64+first51) -> 16` dot ReLU second51 `->16` | 2,688 |
| `history_concat_full` | concat state64 + first379 + second379, `822 -> 16 -> 1` | 13,185 |
| `history_bilinear_full` | ReLU context `(state64+first379) ->16` dot ReLU second379 `->16` | 13,184 |

Compact51 is action `[0:45]` plus direct context indices `[109,154,199,244,289,334]`. Run the
complete 160-fit selection twice. Require exact A/B held counts and exact reproduction of D154's
`semantic_context115` held counts by `snapshot_compact`; record harmless threaded hash drift.

## Frozen readout

Apply every original D153 held gate to each architecture/seed. This is a multiple-architecture
discovery audit: an eligible cell opens a separately frozen confirmation on fresh nonreserved
maps, never an immediate checkpoint or submission. If none passes, close static first-action memory
and move to trajectory recurrence/online control or a coarser policy abstraction.

## Boundary

D155a cannot read/generate reserved maps `9,844,200--9,844,215`, collect new maps, use YT, integrate
Rust, save a deployable checkpoint, qualify or submit a candidate, change the resident, or interact
with Arena.
