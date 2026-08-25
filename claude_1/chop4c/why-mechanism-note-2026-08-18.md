# Phase 1 — WHY the forecast answers "nothing there" (OSC-031)

Task `20260818-osc031-forecast-defect-fix`. **Measured, not reasoned.** Parity IDENTICAL before
any row was counted. Neutral wording: this note reports a mechanism; the fix design is a
*proposal* and the door is the owner's.

## The measurement, over the pinned 167 turns

| quantity | value |
|---|---|
| `predict_tree` evaluations | **630** |
| exits | **NONE: 630 · SOME: 0** |
| `opp_chop` on every NONE exit | **1** |
| tree health at forecast start | **4**, every time |
| forecast horizon (`travel_turns`) | **9** on 624 evaluations, **8** on 6 |
| iteration the forecast killed the tree | **4**, every time |
| per-turn evaluation multiplicity | 4 on 148 turns, 2 on 19 turns |
| `predicted_opp_chop` provenance (whole run) | **DAMAGED_FLAT1: 732 · ON_TREE: 0 · NONE: 2** |

## The mechanism

`predict_tree` has exactly **one** `return None`, at the opponent-damage guard. It fires because:

1. `predicted_opp_chop` finds **no opponent on the tree** (`ON_TREE` never fires here). It then
   falls to its second rule: *the tree's health is below full for its size, so assume an opponent
   is chopping it at **1 per turn***. That flat 1 is returned in **732 of 734** calls.
2. The forecast horizon is the walk length, **`travel_turns` = 8 or 9** — measured, not assumed.
   The forecast subtracts 1 health per simulated turn from a starting health of **4**.
3. Health reaches 0 at simulated **iteration 4 — well before arrival at turn 8 or 9** — so
   `predict_tree` returns `None`. **The 4 is the death iteration, not the walk length**; an
   earlier draft of this note conflated the two, and the long horizon in fact makes the outcome
   more certain rather than less, because the loop has 8–9 chances to reach zero.
4. `chop_candidates` treats `None` as "no tree to plan against" and skips it — every tree, every
   turn.

**The loop that makes it permanent:** the tree is damaged, so the forecast assumes it is dying;
because the forecast says it is dying, the troll never goes to chop it; because nobody chops it,
it stays damaged. The assumption maintains its own precondition.

## Fix design — a PROPOSAL, for the owner's design gate. Nothing is built.

The defect is not the guard; a tree that will genuinely be dead on arrival *should* be skipped.
It is the **evidence** the guard runs on: a flat "1 per turn forever" inferred from damage alone,
with no opponent present and no expiry.

Options, with the trade I can see for each — **I am not choosing**:

- **A. Require an actual opponent.** Use `on_tree` damage only; drop the damage-implies-chopper
  inference. Simplest, and it restores chopping of damaged trees. Risk: loses caution in the case
  the inference was written for — an opponent who *just* stepped off the tree.
- **B. Bound the inference.** Keep the flat 1 but stop applying it past the point where evidence
  is stale (e.g. only while the damage is recent, or cap the assumed damage below full health).
  Preserves the original intent; needs a rule for "recent", which is a new constant.
- **C. Treat forecast death as a cost, not a veto.** Let the planner score a tree that may be
  contested rather than removing it from consideration. Largest change; touches scoring, and
  **two-correct-doors-make-a-wall** applies most strongly here.

**Standing hazard, flagged because it is the one this project keeps paying for:** this sits in the
planner core, and each option changes what *other* generators see. Whichever door the owner picks,
the Phase-2 gates should include the whole-game panel, not just the fixture that showed the bug.

## Limits

One game. Whether other games hit the same guard for the same reason is **not** measured here.
The probe logs both exits and all three provenance branches with equal fidelity, so a different
answer elsewhere would be visible rather than hidden.
