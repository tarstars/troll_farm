# Phase 3b — design proposal r2: make the idle fallback EXTEND, not REPLACE

Task `20260820-pair-selector-anti-benching`. Revision of
`claude_1/picker3/phase3b-design-proposal-2026-08-22.md` (`802e1388`), which codex_1 returned
**REVISION_REQUIRED at G-f** in `codex_1/reviews/pair-selector-phase3b-design-review-2026-08-22.md`
at `b8ce2a9ed96be4567bcf98005e91612086ddab84`. This document supersedes r1 in full; where the two
disagree, r2 governs.

**Design proposal only.** Nothing here is built, compiled, run or measured. No candidate source was
edited. It claims no improvement. Per `local_claude_1`'s ruling
(`coordination/messages/local_claude_1/20260822T165022Z-...-policy.md`) a build authorization is a
separate written act that this document does not request and cannot grant.

## 0. What changed from r1

Three blocking repairs and one added falsifier, all from the review, all accepted without dispute:

1. **§4 G-c** — r1 required byte identity *through* the first tick on which a candidate was rescued.
   The review is right that this is unsatisfiable at the intended success case: a selected rescued
   `PICK` must change the command on exactly that tick. r2 separates the **formation** boundary from
   the **effect** boundary and pins identity strictly *before* the first *selected* Δ-A tick.
2. **§4 G-b** — r1 compared Δ-B ticks turn-aligned across a paired closed-loop run, which is invalid
   once an earlier selected Δ-A has moved the trajectory. r2 replaces it with a same-state fork (§5),
   and states precisely what "same state" means for this code.
3. **§4 G-a/G-c** — the word `rescued` was overloaded across Δ-A and Δ-B. r2 replaces it with five
   explicit per-game counters and one orthogonal per-state property.
4. **§7** — added falsifier 5: local progress bought by a commitment that creates a new or worse
   P3/P4/r5-horizon event elsewhere.

Sections 1, 2, 3, 6 and 8 carry r1's accepted content forward; only §2's naming is touched.

## 1. The change (unchanged from r1, ruled form)

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

`out` was seeded `vec![MoisanBot::wait()]` at the top of the function and the unit is not mutated in
between, so the single seeded `WAIT` is already at `out[0]` and is not re-added. The ruled text is
kept rather than tidied, so that the built diff and the ruled diff are the same object.

## 2. Every behavioural delta this can produce — enumerated from the function's own guards

At the fallback's `return`, `out` can only contain, in order: the seeded `WAIT`; bank candidates from
the `carried>0 && is_adjacent(shack)` block; the replant `PICK`s from the
`safe_regeneration && carried==0 && turn>=100 && plants.len()<=2 && ...` block. The two earlier
`return`s (`safe_regeneration && carried_fruit`, and `free_capacity()<=0`) exit before the fallback,
so nothing else can be in flight. Exactly two deltas, **mutually exclusive** on `carried>0` versus
`carried==0`:

- **Δ-A — preserved replant `PICK`s.** `carried==0` and the replant block fired: one or more `PICK`
  candidates (score `7500 - priority`, target `Cell(unit.cell)`) survive instead of being discarded.
  This is the 101 measured idle turns of OSC-013 in `phase3-generator-route-2026-08-20.md`.
- **Δ-B — duplicated bank candidates.** `carried>0` and the unit is adjacent to the shack:
  `bank_candidates` are appended **twice** — once by the earlier block into `out`, once by the
  fallback. The duplicates are element-identical (same command string, score, target), and `select`
  is a score maximiser (`max_by` for one unit; a product loop with strict `score>best_score` for
  two), so identical duplicates *should* be command-inert. **That is an argument, not a
  measurement.** G-b (§5) is written to catch it, not to confirm it. Δ-B never fires on the measured
  idle windows of the four ruled fixtures (`carried=0` on every one); its reachability elsewhere on
  the panel is unmeasured.

If G-b shows Δ-B is not inert, the design does **not** patch around it: it returns to the owner with
the measurement, with the obvious alternative on the table (append the fallback's bank candidates
only when the earlier block did not). Deviating from the ruled snippet before that measurement exists
would be the unlicensed design move this programme keeps banning.

## 3. The change is STATEFUL (unchanged from r1)

Selecting a `PICK` is not a one-tick event. `remember_selected_regeneration` inserts the unit into
`regeneration_commitments`; on every later turn `commands()` routes a committed unit to
`endgame_candidates` instead of `main_candidates`. `reconcile_regeneration_commitments` clears the
commitment once the unit carries neither the fruit nor the wood and is not standing on a live plant
of that kind — self-limiting, but not confined to the tick. Consequently a whole-game byte-identity
requirement is unsatisfiable by construction on any game the change actually affects, which is what
§4 now encodes exactly rather than approximately.

## 4. Per-game classification and the repaired identity gates

### 4.1 Recorded quantities (non-overloaded)

Per game, on the candidate arm, with the base arm's paired run as reference:

| field | meaning |
|---|---|
| `delta_a_formed_ticks` | ticks where the fallback returned ≥1 replant `PICK` that the base's fallback discarded |
| `delta_a_selected_ticks` | ticks where the emitted command for that unit **is** one of those preserved `PICK`s |
| `first_delta_a_selected_tick` | the minimum of the above, or `null` |
| `delta_b_duplicate_ticks` | ticks where the fallback appended bank candidates already present in `out` |
| `whole_game_identical` | full command-stream byte identity against the base arm |

`delta_a_selected_ticks ⊆ delta_a_formed_ticks` is asserted, not assumed. On every tick, the
mutual-exclusion claim of §2 (`Δ-A` and `Δ-B` never co-occur for one unit) is asserted as a runtime
check; a co-occurrence fails the run and refutes §2.

### 4.2 Effect classes — exhaustive and exclusive

Every panel game lands in exactly one class, keyed on `first_delta_a_selected_tick`:

- **NO-EFFECT** (`= null`): `whole_game_identical` must be **true**. Δ-A may have been *formed* here
  and never selected; that is still NO-EFFECT and still requires whole-game identity. Any divergence
  in this class fails the run.
- **EFFECT** (`= T`, non-null): the command stream must be byte-identical for every tick `< T`.
  On tick `T`, the changed command must be one of the specifically preserved Δ-A `PICK` candidates
  for that unit, and its provenance is recorded (unit id, cell, plant kind, score, the base-side
  candidate list that lacked it). Divergence is permitted from `T` onward and every changed game is
  named in G-d.

Δ-B is **not** a third class. It is an orthogonal per-state property tested by §5, and a game may
carry Δ-B ticks in either class.

- **G-a — trigger census.** Report all five fields per game plus panel totals. Reported, not
  thresholded.
- **G-c — partition.** The two classes above, with the identity requirement each carries. A game
  satisfying neither, or violating its class's identity requirement, fails the run.

## 5. G-b — Δ-B inertness by same-state fork

Turn-aligned closed-loop comparison is abandoned. Instead:

**Why an argument-level fork is the *same* state here.** `main_candidates` is an associated function,
not a method: it takes `(view, unit, type_to_cut, idle_regeneration, safe_regeneration, opponent_eta_penalty)` — the
call site passes `self.persistent_regeneration` into `safe_regeneration` — and reads no `&self`. The bot's mutable memory
(`regeneration_commitments` and the strategy flags) reaches the generator only through (i) those four
scalar arguments and (ii) the routing branch chosen in `commands()`
(`committed_regeneration` / `endgame` / `early` / main). Therefore recording the argument tuple **and
the routing branch id** at a naturally reached state captures the whole of the memory dependence, and
no struct-level clone of `YamoBot` is required — which matters, because `YamoBot` does not derive
`Clone` and adding one would edit the pinned source.

**Procedure.** In a probe binary that links **both** fallback variants as two separately named
generator functions (old = REPLACE, new = EXTEND):

1. Instrument both arms to record, on every tick that reaches the main-candidates branch: the view
   snapshot, the unit, the four scalars, the routing branch id, the sibling unit's candidate list,
   `view.inventories[0]`, and `unit_cells`.
2. Take every naturally reached Δ-B state **from both arms**, including states reached after a Δ-A
   effect on the candidate arm.
3. Run both generator variants on that identical recorded tuple. Assert that the only multiset delta
   between the two candidate lists is one or more **duplicate, element-identical** bank candidates
   (same command string, score bit pattern, and target) — nothing added, nothing removed, nothing
   altered.
4. Replay `select` over the recorded `by_id` with only that unit's list substituted, plus the
   recorded inventories and `unit_cells`, and require the selected command to be byte-identical
   between the two variants. Then `resolve_move_conflicts` on both and require identity again.

Any failure at step 3 or 4 stops the build and returns to the owner (§2). Whole-game byte parity
remains the requirement only for NO-EFFECT games (§4.2).

**Probe-shim inertness (the gate on the gate).** The probe binary carries a second generator copy and
recording hooks that the shipped candidate must not. Two checks, both fail-the-run: (a) the shipped
candidate source used for G-c/G-d must be byte-identical to the pinned source plus exactly the §1
hunk — diffed, not asserted; (b) the probe's second generator and its recorders must be unreachable
from the panel arm's command path, demonstrated by the panel arm being built from (a)'s source and
not from the probe binary. This is the same failure mode as the inert checks of 08-15→21: an
instrument that measures its own instrumentation.

## 6. Remaining gates

- **G-d — panel with named costs**, every changed game named, per the standing behaviour-changing
  gate class in the task file.
- **G-e — the two-clause bar** of `coordination/tasks/20260822-alpha-progress-regrade.md`: a healed
  event must be healed **with progress**, never merely detector-silent. The re-grade instrument at
  `79dfdd63` (`claude_1/regrade3/`, scope note `SCOPE-NOTE-2026-08-22.md`) is the intended grader.
  This change is especially exposed here: a `PICK` that plants and yields nothing silences a detector
  while the troll still does nothing.
- **G-f — pre-build design ruling by codex_1**, before any candidate is built, as on α. This document
  is the re-submission.

## 7. Named falsifiers

1. The preserved `PICK` is formed but never selected (target incompatibility with the partner unit,
   or `stock_compatible` refusing two picks of one kind on one unit's inventory). Then Δ-A is real in
   the generator and invisible in the command stream: every game is NO-EFFECT and the change is inert.
2. The `PICK` is selected, plants, and the troll still makes no progress — G-e fails and the change is
   a detector-silencer, which the bar rejects.
3. The commitment side effect (§3) routes the unit into `endgame_candidates` and makes things worse on
   games outside the four fixtures — visible only in G-d's named costs, which is why G-d is panel width.
4. Δ-B is not inert (§5).
5. **Downstream commitment cost (added per review).** Δ-A is selected and makes local progress at the
   OSC-013 window, but the commitment-induced continuation creates a **new or worse P3, P4 or
   r5-horizon event elsewhere** in the same game or on another panel game. G-d and G-e **stop** on
   this outcome; an aggregate improvement does not license it, and the per-event named-cost table —
   not the panel mean — is the deciding artifact.

Any of 2, 3, 4 or 5 is a stop, not a patch.

## 8. Inputs

- `claude_1/picker2/phase3-generator-route-2026-08-20.md` — the measurement this rests on.
- `claude_1/picker2/route-census-2026-08-20.json` — routes, predicates, discarded candidates.
- `claude_1/picker2/candidate-cureC-p1p2.rs`, `claude_1/picker2/candidate-door1-p1p2.rs` — the two
  pinned sources carrying the identical fallback.
- `claude_1/picker3/phase3b-design-proposal-2026-08-22.md` — r1, superseded by this document.
- `codex_1/reviews/pair-selector-phase3b-design-review-2026-08-22.md` @ `b8ce2a9e` — the review.
- `coordination/messages/local_claude_1/20260822T165022Z-...-policy.md` — the ruling.

## 9. Scope lock (unchanged)

Justified by **101 idle turns of OSC-013 in one game**, and by nothing else. On OSC-013's other 69
idle turns, and on every idle turn of OSC-004 / OSC-017 / OSC-034, the fallback discarded nothing
real; on OSC-032/033 the generator formed nothing on any idle turn. If this change is ever reported,
it must not be reported as addressing those. Restoring the `PICK`s is **not** claimed to restore
progress — that is what G-e is for, and it may return a negative.
