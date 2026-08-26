# PEEK — the ruled step-2 predicate refuses all 15 busy-blocker rows, by source

Task `20260822-peek-planner-target-map`. Written to codex_1's construction ruling
(`codex_1/reviews/peek-planner-target-map-construction-ruling-2026-08-22.md`,
`agent/codex_1@fc332164`), **before** rev 3 is built. Read-only: no build, no edit, no candidate.

## The ruled predicate

> genuine mover pass-through **plus a present partner target different from both the mover's final
> target and the landing cell being taken**; missing/`None` fails toward not displacing.

## The fact that decides it, read out of the base source

`chop_candidates` (base `cgauto/submissions/candidate-door1-pure-deletion.rs`, the `Candidate`
push at the end of the loop) sets:

```rust
let command = if plant.cell == unit.cell { format!("CHOP {}", unit.id) }
              else { format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1) };
out.push(Candidate{ command, score, target: Target::Tree(plant.cell) });
```

**A unit standing on the tree it chops carries `target = Target::Tree(its own cell)`.** That is the
value step 2 authorises the resolver to borrow.

## Therefore, on the census rows

Both blockers are chopping a tree **on the cell the mover is taking** — measured, not inferred:

- **OSC-005**: landing (8,2); `LEMON` at (8,2) in the entry state; blocker unit 0 holds (8,2) for
  the whole window with wait fraction 0.08 and the library's own classification records
  `plant_on_cell_at_entry: LEMON`, `blocker_state: WORKING`.
- **OSC-027**: landing (3,2); `APPLE` at (3,2) in the entry state; the census records occupant 0 on
  (3,2) with command `CHOP` on every one of the ten declining ticks.

So the partner's target **is** the landing cell being taken, and the predicate's second clause
fails on **all 15 rows** — the 5 in OSC-005 and the 10 in OSC-027.

**Consequence: rev 3 as ruled fires on none of the busy-blocker rows.** It reaches OSC-011's 13,
where the displaced troll's target is the contested cell it wants *back*, and it does not reach
R-1's other half, which is the half step 0b showed is mechanically reachable.

## What I am NOT claiming

- Not that the ruling is wrong. Refusing to displace a unit off the tree it is harvesting is a
  defensible reading of "do not swap a partner off its own target", and it is exactly the
  stale-or-wrong-target caution the coordinator named as the unwaived cost.
- Not that firing there would be *good*. Whether displacing a chopping unit restores progress is
  unmeasured; the two-clause bar applies and G-2 would have to show it.
- Not that this is measured end-to-end. The propagation map does not exist yet, so no row carries
  a partner target. The chain is: source says a standing chopper's target is its own cell; the
  fixtures say the blocker stands on the tree at the landing cell. Both halves are checkable.

## The question that has to be answered before rev 3 is built

The owner's swap-and-return is *"a busy blocker steps aside, lets the mover past, returns to
work."* Under the ruled predicate a busy blocker on its own target never steps aside — so either

1. the predicate stands and PEEK is scoped to the 13, with R-1's busy-blocker half explicitly out
   (a legitimate, smaller task, and cheaper); or
2. the second clause is narrowed — e.g. refuse only when the partner's target is a cell it must
   *travel* to, and permit displacement when the partner is standing on its target and can return
   next tick — which is a bigger claim needing its own justification and its own measurement.

That is codex_1's and the coordinator's to decide. **I have not built rev 3 and will not until it
is decided**, because the two branches produce different candidates and only one of them can be
measured against the 15 rows.
