# PEEK — let the traffic cop see where our trolls intend to go

**PEEK** is the handle. One line: *the movement layer is allowed to read, read-only, the
planner's target for each of our own units — including the ones currently waiting — solely to
decide whether to displace one.* The name is the word already used with the owner
("allow the peek") and it is deliberately small: this is one fact crossing one seam, not a
rewrite.

- Status: **SEQUENCE AGREED with the owner 2026-08-22. Step 0 CHARTERED; steps 1–5 wait on its
  answer**, because step 0 can change what the rest is worth.
- Record owner: local_claude_1 · Step 0 + build: **claude_1** · Construction and gate rulings:
  **codex_1** · Charter exception and the basket criterion: **local_claude_1** · Arena: **owner**.
- Created UTC: 2026-08-22T19:30:00Z

## Why this exists

Cure α is blocked at G-1 by **13 residual re-swaps** in one game. They are not separable at the
seam: claude_1 tabulated every field visible at the decision point and the bad fires sit in the
**same bucket** as the two we must keep. The distinguishing fact appears one tick later — the
displaced troll's next command is a move back to the contested cell. That fact is the planner's
target, and the movement layer cannot see it.

The same missing fact explains two more things:

- **The dance that forced deleting half of R-1.** In OSC-006 both trolls wanted the *same* cell;
  the swap only exchanged which one stood next to it. It looked geometrically like a
  pass-through — a pass-through test keeps all 27 of those fires — and it was not one.
- **The owner's swap-and-return** (a busy blocker steps aside, lets the mover past, returns to
  work). Correct mechanism; it needs to fire only on a *genuine* pass-through, which means
  knowing the mover's target is beyond the blocker's cell and not the same as the blocker's.

**One fact, three problems.** That is the whole case for PEEK.

## The sequence

**Step 0 — CHARTERED NOW. Check the prize before paying for it. Read-only, no build.**
Against the existing event table (`claude_1/swap1/g1-event-table-2026-08-21.json` and its
report), answer one question: with the planner target available, would a widened trigger fire
**inside** OSC-005's and OSC-027's recorded episodes — the busy-blocker cases R-1 is about?
The integrator's standing doubt, recorded so it is tested rather than assumed: **even rev 1
never fired inside OSC-005's episode** (its only fire lands at turn 52, 34 turns late), so the
widening may buy the 13 and none of R-1's other half. Report per episode, and report "cannot be
determined from the recorded fires" where that is the honest answer rather than inferring.
*Owner: claude_1. No candidate edit. This decides the scope of everything below.*

**Step 1 — the charter exception, ruled by local_claude_1.** α's charter confines it to
`resolve_move_conflicts*`; PEEK reaches outside it. codex_1 reserved this for
"`local_claude_1`/owner"; it is the coordinator's and it will be ruled with the cost named, not
waived. **Correction of record: this was labelled "owner-blocked" for a day and the owner never
had it — codex_1's body said coordinator-or-owner and its own headline compressed that; the
integrator then repeated the compression.**

**Step 2 — codex_1 rules the construction before anything is built.** Post the predicate, the
map's exact shape and lifetime, and what is explicitly untouched. Pre-build review has caught
three real holes in this programme already.

**Step 3 — claude_1 builds rev 3.** One predicate over the new fact: fire on a genuine
pass-through; refuse when both units target the same cell; refuse when the partner's target is
the cell being taken.

**Step 4 — G-1 must reach ZERO re-swaps**, which is the gate the current 13 fail, plus inertness
parity: byte-identical wherever the trigger does not fire.

**Step 5 — G-2 on the panel under the two-clause bar** — healed **with progress**, never
detector-silent, and with codex_1's warning carried: side-level healing can hide a unit that
never resumed.

Then **G-4 is the owner's**, on a ladder that is deliberately stopped.

## The honest framing — do not do this for the points

Ten pairs measured today put this whole class at **+0.17, ≈0.00 symmetrised**: no ladder gain we
can distinguish from zero (`local_claude_1/door1-vs-old-pooled-verdict-2026-08-22.md`). α's own
expectations were never large.

The reason to do PEEK is that it is the **smallest real instance of the cross-layer contract**
that both `chatgpt_1`'s position and the integrator's assessment now point at: one layer acting
on a fact it structurally lacks. If one fact crossing one seam fixes thirteen events we can
count, that is evidence about the architecture — which is what the owner has said the project is
for. Score is the guardrail here, not the objective.

## Named cost, and it is real

The movement layer gains a dependency on planner state and can act on a **stale or wrong**
target. codex_1's warning that "one-tick `WAIT` is not evidence of stable idleness" applies to
intentions too: a target read this tick may change next tick. Step 2 must state the map's
lifetime and what happens when it is wrong, and step 4's parity control is what keeps the blast
radius visible.

## What this does NOT authorize

No candidate edit before step 2's ruling. No Arena action. No widening beyond suppressing
displacement — PEEK is a read, never an input to scoring, target selection or the pair selector.
It does not touch α's other two open questions (the residual-13 disposition and the cure-arm
basket criterion), both of which remain the coordinator's.
