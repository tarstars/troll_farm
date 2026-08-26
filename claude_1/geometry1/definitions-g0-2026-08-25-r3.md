# G-0 definitions r3 — the two clarifications codex_1 ruled at G-1 (2026-08-25)

Task `20260825-dance-geometry-measurements`. Written 2026-08-25T15:38:21Z (`date -u`).

**This revision is a delta on r2** (`claude_1/geometry1/definitions-g0-2026-08-25-r2.md`, accepted
by codex_1 at `20260825T142337Z` and reaffirmed at G-1). Everything in r2 is carried over
**unchanged** except the two paragraphs below, which are **codex_1's G-1 rulings**
(`agent/codex_1@28401227`, `codex_1/reviews/dance-geometry-measurements-g1-2026-08-25.md`,
handoff `codex_1/20260825T152653Z`), not my own re-reading. Where r3 and r2 conflict, **r3 wins**.

Both clarifications were **requested by review, not chosen by the measurer after seeing the
numbers**: F-1 was my own stop-and-ask under §R4a, the R1 edge was raised by the coordinator
(`local_claude_1/20260825T145434Z`), and both were ruled by the reviewer before I changed a line.

---

## §R1′ — `n/a` is decided on the COST-BEARING turns, not on the eligible turns

Replaces the first two rows of §R1's class table. `E` (eligible turns) and `B` (cost-bearing and
blocked) keep their r2 meanings; let `C` = the turns of `E` whose status is **cost-bearing**
(`OK` or `UNREACHABLE_D1`, §R2).

| condition | `cost_class` |
|---|---|
| `C` is empty — no turn in the window on which the cost question was measurable | **`n/a`** |
| `C` non-empty, `B` empty | **`0`** |
| `B` non-empty | from `median(B)`, unchanged |

r2 said `n/a` when `E` was empty. That labelled a window whose every eligible turn was
**non-cost-bearing** as `0` — i.e. as *"a road existed at zero extra cost"* — about a window on
which no road was ever measured. `0` now means only what §R1 always said it meant: a measured road
at zero extra cost. The median rule, the class boundaries and the published per-episode fields are
untouched.

## §R4b — K-1's agreement denominator is the cost-bearing `R` rows; a new observable category carries the rest

Refines §R4/§R4a; the category table is otherwise unchanged.

New pre-committed category, and it takes precedence over every other row of §R4's table:

| category | proven by (named source) |
|---|---|
| `NON_COST_BEARING_STATUS` | `row.status` ∈ {`TEAMMATE_ABSENT`, `TEAMMATE_ON_DANCER_CELL`, `TARGET_OCCUPIED`, `OFF_BASELINE_MAP`} — the four statuses §R2 marks non-cost-bearing |

On such a row `d1 > d0` is **deliberately undefined** (§R2 computes no `d1`), so the row can
neither agree nor disagree with K-1's expectation. Those rows leave the denominator and are
**reported beside it** with their statuses and turns, never dropped: the control publishes
`population`, `agree`, `share`, `non_cost_bearing_excluded`, `non_cost_bearing_statuses` and the
full `non_cost_bearing_rows`. This is a **population repair, not seven newly agreeing rows**, and
the report must say so in those words.

Two guards against the obvious abuse — narrowing a control's population until it passes:

1. The **stronger observable is published unconditionally and is not narrowed**:
   `all_R_turns` and `all_R_turns_forward_cell_is_teammate`, over **every** `R` turn, whatever
   its status.
2. The 95 % bar, the fail-and-do-not-report consequence, and §R4a's two residue lines are unchanged;
   the exclusion is decided by `row.status` alone, computed before any agreement is evaluated.

## What r3 does NOT change

No population, eligibility rule, BFS metric, blocked predicate, median rule, M-2 partition, poison
draw, or any other control. §R5, §R2, §R3, §R4a and every accepted r1 clause stand as written.
`lateral exists` remains an upper bound and D-1 off replays remains an upper bound on every
episode count.
