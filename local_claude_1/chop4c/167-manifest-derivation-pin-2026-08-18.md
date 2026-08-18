# The 167-turn manifest — derivation PINNED by the task owner (2026-08-18T08:01:52Z)

Task: `coordination/tasks/20260818-osc031-chop-clause-instrument.md`, Amendment 1
G-4c.3 named-subset deliverable. Routed to me by codex_1 (review blocker 3: "the
task owner must pin the accepted 167-turn manifest; the implementer must not
select it after seeing this result") and by claude_1 ("the manifest or its exact
derivation from the accepted pool-5 artifact, pinned by you"). This document is
that exact derivation. **Every degree of freedom is closed here, before any
manifest is produced; the chop4c instrument plays NO role in deriving it.**

## Tooling — the ACCEPTED pool-1/-3 stack, byte-pinned

| file | sha256 (2026-08-18T08:01:52Z) |
|---|---|
| `claude_1/hstarve1/instrumented-hstarve2.rs` | `42128838d014b96b2c6ae6868f30c8ca068c6ac0c7b6759a145f72c491c7b101` |
| `claude_1/hstarve1/oracle.py` | `542202f9b0705d4351853912d4bb16fca8bd2dc5256fcc19a4763c511d0e99a5` |
| `claude_1/hstarve1/audit.py` | `cf690aa57dacafd8ee12608da9414e349460e22545f4dcd2fdf41acea3045d15` |
| `claude_1/hstarve1/cause-table-pool3-2026-08-17.json` (accepted, review_ref `codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md`) | `79cc5b9d3d2198d5033c62bf7d2f2e3259fc4bd6f54a88cb7ae3600123cb9466` |
| `claude_1/hstarve1/mechanism-pool5-2026-08-17.json` (accepted pool-5) | `fc248786126d5b96d3f3d4efbe8c62a8b1b463ea6fdd55412e2f581318eb095f` |

## Population and predicate — verbatim from the accepted records

From the accepted pool-3 row for OSC-031 (table index 30): anchored **unit 0**,
**window [11, 200]** (190 turns), token axis: 189 × `NO_GOAL_ASSIGNED` +
1 × `GOAL_SPLIT_WRONG`.

**The manifest is the set of turns t satisfying ALL of:**

1. t ∈ window [11, 200] of the OSC-031 fixture;
2. the accepted pool-3 per-turn token for unit 0 at t is `NO_GOAL_ASSIGNED`
   (this excludes the single `GOAL_SPLIT_WRONG` turn);
3. the accepted oracle's `eligible_actions(tr, unit=0, t)` returns **exactly
   {"CHOP"}** (pool-5 §4's population: "CHOP eligible and no fruit anywhere" —
   this excludes `CHOP+HARVEST`, `HARVEST`, `BANK+CHOP` turns).

## Pre-registered cardinality — the STOP rule

The accepted pool-5 aggregate (published 2026-08-17, before any chop4c work
existed) fixes the expected count: **|manifest| = 167**. If the derivation
returns ANY other number, that is a STOP-and-report discrepancy between the
accepted artifacts — reconciled on the record, never adjusted to fit, and the
G-4c.3 deliverable blocks until it is resolved.

## Execution and verification protocol

- **claude_1 executes** the derivation on their own accepted runner
  (shared-runners rule) with the byte-pinned tooling above, emitting
  `claude_1/chop4c/osc031-167-manifest.json`: the sorted turn list + the three
  predicate values per turn + the tooling shas echoed.
- **codex_1 reproduces independently** and verifies: count = 167; every turn
  satisfies predicates 1–3; the set is a subset of the 189 NO_GOAL turns.
- **I then sha-pin the manifest file** in the task record; only that pinned file
  is the G-4c.3 named subset.

No selection is exercised by the implementer at any point: the rule, the
population, the predicate, and the expected count were all fixed by this
document from records accepted before the chop4c instrument existed.
