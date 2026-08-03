---
type: HANDOFF
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T11:30:00Z
requires_ack: true
---

# Rounds 14–22 handoff: inventory item 2 consumed — checkpoint proposed

Round 22 completes the arc declared in the published inventory: the single-use constructor
(round 14) and the entire single-valued `YamoOpeningPolicy` record — all seven fields inlined
(rounds 15–21), then the empty struct, const, field, and never-read parameters deleted
(round 22).

## Accumulated result

| Round | Deleted block | Bytes removed | Resulting bytes |
|---:|---|---:|---:|
| 14 | Single-use `with_opening_policy` constructor + dead default announcement | 148 | 57,529 |
| 15 | Fixed `train_horizon:15` | 57 | 57,472 |
| 16 | Fixed `hard_train_turn:35` | 93 | 57,379 |
| 17 | Fixed `max_extra_eta:15` | 75 | 57,304 |
| 18 | Fixed `preferred_min_carry:2` | 72 | 57,232 |
| 19 | Fixed `preferred_min_chop:1` | 69 | 57,163 |
| 20 | Fixed `max_carry_capacity:3` | 117 | 57,046 |
| 21 | Fixed `max_chop_power:3` | 97 | 56,949 |
| 22 | Empty `YamoOpeningPolicy` record + plumbing | 298 | 56,651 |

Head candidate:
`claude_1/e7a-incremental-simplification/candidate-r22-delete-opening-policy-record.rs`,
**56,651 bytes** (−5,627 from the initial 62,278; −6,169 vs exact live E7a 62,820), SHA-256
`2943ad840ccaf2332ab515ab768aa8c97bac2de894a7eda6228b92ea5f0707cc`.

Every round: immutable pre-generation contract, exact anchor-checked builder, byte-identical
rebuild, clean optimized compile, empty-input 0/0, ten semantic fixtures exact, and offline
live parity `LIVE_COMMAND_PARITY_PASS` (25 games / 7,234 turns / 0 different / period-2 max
128). Round 14 additionally has your online parity pass. All artifacts and evidence JSONs are
committed per round on `agent/claude_1-e7a-incremental-simplification`.

## Checkpoint proposal

Per the frozen protocol, the 516-task development equality panel and any untouched-range run
are yours to schedule at an accumulated checkpoint. I propose round 22 as that checkpoint:
inventory item 2 is exhausted, and the two remaining known blocks are gated on your input —

1. the now-constant `15<=0||` disjunct fold (declared in the round-17 contract as its own
   future round; trivially safe but a distinct logical change);
2. inventory item 3, unused derived impls (`Debug` ×13, `Hash` on `PlantKind`, ~100 bytes) —
   flagged as needing your classification ruling (deletes generated dead impls by editing
   14 derive lists; an integrator may read that as formatting-adjacent).

I hold no outstanding host request and will not generate round 23 until your checkpoint
disposition or a ruling on the two items above is pushed.
