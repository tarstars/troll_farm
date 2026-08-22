# Phase 3b — design proposal: make the idle fallback EXTEND, not REPLACE

Task `20260820-pair-selector-anti-benching`. Written under `local_claude_1`'s ruling
`coordination/messages/local_claude_1/20260822T165022Z-20260820-pair-selector-anti-benching-policy.md`
(2026-08-22), which resolved extend-versus-replace and explicitly unblocked this proposal while
leaving the build queued.

**This is a design proposal only.** Nothing here is built, compiled, run or measured. It proposes
one change, names every behavioural delta it can produce, and specifies the gates that would decide
it. It claims no improvement. Per the ruling, a codex_1 pre-build design ruling comes first, and a
build authorization is a separate act that this document does not request and cannot grant.

## 1. The change

`main_candidates`, the `idle_regeneration && chops.is_empty()` arm. Identical text and identical
position in both pinned candidate sources — `claude_1/picker2/candidate-cureC-p1p2.rs:1215` and
`claude_1/picker2/candidate-door1-p1p2.rs` (same block, offset by the door-1 forecast hunk).

Before:

```rust
if idle_regeneration&&chops.is_empty(){
    let mut fallback=vec![MoisanBot::wait()];
    fallback.extend(Self::idle_harvest_candidates(view,unit));
    if unit.total_carried()>0{
        fallback.extend(Self::bank_candidates(view,unit));
        }
    return fallback;
    }
```

After (the ruled form, verbatim in effect):

```rust
if idle_regeneration&&chops.is_empty(){
    out.extend(Self::idle_harvest_candidates(view,unit));
    if unit.total_carried()>0{
        out.extend(Self::bank_candidates(view,unit));
        }
    return out;
    }
```

`out` was seeded `vec![MoisanBot::wait()]` at the top of the function and the unit is not mutated
in between, so the `WAIT` the fallback used to rebuild is already present at `out[0]` and is not
re-added — as the ruling requires. `unit.total_carried()` is the same value as the local `carried`
computed at the top; the proposal keeps the ruled text rather than tidying it, so that the built
diff and the ruled diff are the same object.

## 2. Every behavioural delta this can produce — enumerated from the function's own guards

At the fallback's `return`, `out` can only contain, in order: the seeded `WAIT`; bank candidates
from the `carried>0 && is_adjacent(shack)` block; the replant `PICK`s from the
`safe_regeneration && carried==0 && turn>=100 && plants.len()<=2 && ...` block. The two earlier
`return`s (`safe_regeneration && carried_fruit`, and `free_capacity()<=0`) exit before the fallback,
so nothing else can be in flight. That gives exactly two deltas, and they are **mutually exclusive**
because one requires `carried>0` and the other `carried==0`:

- **Δ-A — the intended one.** `carried==0` and the replant block fired: one or more `PICK` candidates
  (score `7500 - priority`, target `Cell(unit.cell)`) survive instead of being discarded. This is the
  101 measured turns of OSC-013 in `phase3-generator-route-2026-08-20.md`.
- **Δ-B — a side effect the ruling did not name.** `carried>0` and the unit is adjacent to the shack:
  `bank_candidates` are now appended **twice** — once by the earlier block into `out`, once by the
  fallback. The duplicates are element-identical (same command string, score and target), and
  `select` is a score maximiser over the list (`max_by` for one unit; a product loop with strict
  `score>best_score` for two), so identical duplicates cannot change the chosen command. I expect
  Δ-B to be command-inert, but **that is an argument, not a measurement**, and gate G-b below is
  written to catch it rather than to confirm it. Δ-B never fires on the measured idle windows of the
  four ruled fixtures (the route census recorded `carried=0` on every one of them); its reachability
  on the rest of the panel is unmeasured.

If G-b shows Δ-B is not inert, the design does **not** proceed by patching around it: it returns to
the owner with the measurement, with the obvious alternative on the table (append the fallback's
bank candidates only when the earlier block did not already do so). Deviating from the ruled snippet
before that measurement exists would be exactly the unlicensed design move this programme keeps
banning.

## 3. The change is STATEFUL — this sharpens the ruling's inertness gate

Selecting a `PICK` is not a one-tick event. `remember_selected_regeneration` inserts the unit into
`regeneration_commitments`, and on every later turn `commands()` routes a committed unit to
`endgame_candidates` instead of `main_candidates`. `reconcile_regeneration_commitments` clears the
commitment again once the unit carries neither the fruit nor wood and is not standing on a live
plant of that kind — so the commitment is self-limiting, but it is not confined to the tick.

Consequence for the ruling's "inertness parity" gate, which I therefore state in a checkable form:

> **Inertness is byte-identity of the command stream up to and including the first tick on which the
> fallback rescues a candidate the old code would have discarded, and byte-identity of the entire
> stream on every game where no such tick exists.**

A whole-game byte-identity requirement would be *unsatisfiable by construction* on any game the
change actually touches, and quietly weakening it after the fact is how a gate becomes inert. Stated
this way it is the strongest claim the change can be held to, it is decidable per game, and the count
of games in each class is itself a reported number (G-c).

## 4. Gates — the ruling's list, made operational

- **G-a — trigger census.** Per game: ticks where the fallback fired; ticks where it fired with `out`
  holding something beyond the seeded `WAIT` (the rescues), split Δ-A / Δ-B. Reported, not thresholded.
- **G-b — Δ-B inertness.** On every tick classified Δ-B, the emitted command stream must be
  byte-identical to the base. Any difference stops the build and returns to the owner (§2).
- **G-c — partition.** Every panel game lands in exactly one class: *no rescue* (whole-game
  byte-identity required) or *rescued* (identity required up to the first Δ-A tick, divergence
  allowed and named after it). A game in neither class, or in both, fails the run.
- **G-d — panel with named costs**, every changed game named, per the standing behaviour-changing
  gate class in the task file.
- **G-e — the two-clause bar** of `coordination/tasks/20260822-alpha-progress-regrade.md`: a healed
  event must be healed **with progress**, never merely detector-silent. The re-grade instrument
  delivered at `79dfdd63` (`claude_1/regrade3/`, scope note `SCOPE-NOTE-2026-08-22.md`) is the
  intended grader, and the ruling is right that this change is especially exposed here — a `PICK`
  that plants and yields nothing would silence a detector while the troll still does nothing.
- **G-f — pre-build design ruling by codex_1**, before any candidate is built, as on α.

## 5. Scope lock

Justified by **101 idle turns of OSC-013 in one game**, and by nothing else. On OSC-013's other 69
idle turns, and on every idle turn of OSC-004 / OSC-017 / OSC-034, the fallback discarded nothing
real; on OSC-032/033 the generator formed nothing on any idle turn, so nothing was lost there. If
this change is ever reported, it must not be reported as addressing those. Restoring the `PICK`s is
**not** claimed to restore progress — that is what G-e is for, and it may return a negative.

## 6. Named falsifiers — how this proposal could be wrong

1. The rescued `PICK` is formed but never selected (target incompatibility with the partner unit, or
   `stock_compatible` refusing two picks of one kind on a single unit of inventory). Then Δ-A is real
   in the generator and invisible in the command stream, and the change is inert everywhere.
2. The `PICK` is selected, plants, and the troll still makes no progress — G-e fails and the change
   is a detector-silencer, which the bar rejects.
3. The commitment side effect (§3) routes the unit into `endgame_candidates` and makes things worse
   on games outside the four fixtures — visible only in G-d's named costs, which is why G-d is panel
   width and not fixture width.
4. Δ-B is not inert (§2).

Any of 2, 3 or 4 is a stop, not a patch.

## 7. Inputs

- `claude_1/picker2/phase3-generator-route-2026-08-20.md` — the measurement this rests on.
- `claude_1/picker2/route-census-2026-08-20.json` — routes, predicates, discarded candidates.
- `claude_1/picker2/candidate-cureC-p1p2.rs`, `claude_1/picker2/candidate-door1-p1p2.rs` — the two
  pinned sources carrying the identical fallback.
- `coordination/messages/local_claude_1/20260822T165022Z-...-policy.md` — the ruling.
