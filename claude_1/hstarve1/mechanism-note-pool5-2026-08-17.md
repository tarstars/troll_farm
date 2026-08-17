# H-STARVE-1 Pool #5 — mechanism note per `NO_GOAL_ASSIGNED` situation

Scope: exactly the eight accepted situations — OSC-001, OSC-005, OSC-008, OSC-009, OSC-028,
OSC-031, OSC-032, OSC-033. `review_ref:`
`codex_1/reviews/h-starve-1-pool3-incidence-revision-review-2026-08-17.md`.
Subject byte-exact `98628e98…`. Diagnosis only.

Charter question: **which generator path emits the WAIT-only list, and is it deliberate (phase
gating) or broken?**

---

## 0. First correction: the routing label is not the generator

`HS2`'s `branch=` field records which **top-level arm** `commands()` selected. It does **not**
record which function produced the list, and on this subject those differ.

The resident runs `tuned_carry_regeneration_transit_idle_harvest()`, which sets
`idle_regeneration = true` (:790). Inside `main_candidates` (:1189):

```rust
let chops = Self::yamo_chop_candidates(...);
if idle_regeneration && chops.is_empty() {
    return Self::endgame_candidates(...);       // <-- MAIN falls through to the ENDGAME generator
}
```

`main_candidates` starts its list as `vec![wait()]` and only ever *extends* it, so a
**WAIT-only list from a `MAIN`-labelled turn implies `chops.is_empty()`**, which implies the list
actually came from `endgame_candidates`. I nearly published "MAIN emits the WAIT-only list";
that would have been the right count attached to the wrong function.

**So: on 7 of the 8 situations the WAIT-only list is produced by `endgame_candidates`, whatever
the routing label says.** OSC-005 is the exception and is handled separately below.

---

## 1. The dominant mechanism: a qualifying harvest exists and the gate refuses to look

`endgame_candidates` with an empty-handed unit offers: a chop, a regeneration `PICK`/`MOVE` drawn
from **already-banked** inventory fruit, and nothing else. **It contains no harvest generator at
all.** HARVEST is produced only by `idle_harvest_candidates`, which `commands()` adds back at
:1418:

```rust
if endgame && self.idle_harvest && (!self.idle_harvest_clock_only || view.turn > 250)
   && candidates.iter().all(|c| c.target == Target::None) { ... }
```

The fall-through above is gated on `idle_regeneration && chops.is_empty()`. The harvest top-up is
gated on **`endgame`**. Those are different conditions, and the gap between them is the mechanism:

> **The unit is routed into the endgame *generator* while being denied the endgame *harvest
> fallback*, because the fallback is gated on the endgame *flag* rather than on the same
> condition that caused the fall-through.**

This is not a speculative reading. `harvest_gate_blame()` replays
`idle_harvest_candidates`' filter clause by clause on every `NO_GOAL_ASSIGNED` turn where the
oracle reports HARVEST eligible, and reports `WOULD_HAVE_QUALIFIED` when a fruiting plant passes
**every** clause — reachable from the unit, path back to the shack, unclaimed, round trip inside
the clock:

| situation | turns | qualifying harvest existed |
|---|---:|---|
| OSC-032 | 110 (all `MAIN`) | **110 of 110** |
| OSC-033 | 143 (all `MAIN`) | **143 of 143** |
| OSC-028 | 51 (all `MAIN`) | **51 of 51** (≥1 plant each turn) |
| OSC-008 | 7 (all `MAIN`) | **7 of 7** |
| OSC-031 | 22 of its 189 | 11 |
| OSC-001 | 16 | 3 |

**Verdict: deliberate gating, wrong scope.** Nothing here is a coding error — every clause does
what it says. But the phase gate withholds a candidate the subject's own helper would have
produced, on turns where the fruit is reachable, unclaimed and bankable. That is the owner's cure
property (*"a troll with reachable, usable work receives at least one non-WAIT candidate"*) failing
**by design**, which is a materially different finding from a bug and should be ruled on as such.

---

## 2. The counter-finding, against my own instrument: the planner is right more often than the token says

On many of the same situations the reason no harvest was offered is that **an opponent with empty
hands is standing on the plant** (:1350–1353), and the subject declines it on purpose.

`OPPONENT_SITTING_ON_PLANT`: **OSC-009 4 of 4 · OSC-001 13 of 16 · OSC-031 11 of its 22 harvest
turns.**

**My eligible-action oracle ignores opponent occupancy**, so it calls those turns harvestable when
the subject was correct to decline. `NO_GOAL_ASSIGNED` is therefore **over-counted on this
corpus**, and OSC-009 in particular has *no* unexplained turn — all four are the subject correctly
refusing a contested plant.

This is the same class as OSC-012, where my earlier oracle ignored capability and I withdrew a
`GENERATOR_GAP` claim. I am reporting it rather than letting the count stand: **the honest
strong cases are OSC-032, OSC-033, OSC-028 and OSC-008**, where a qualifying harvest existed on
every single turn.

---

## 3. OSC-005 — a different path entirely, and not a starved troll

Unit 0 has capacity 2 and is carrying 2 wood, so `free_capacity() <= 0` and `main_candidates`
returns at :1185 with `[WAIT] + bank_candidates(...)` — never reaching the chop fall-through. The
list was WAIT-only, so `bank_candidates` produced nothing on that turn.

It is **one turn**, and the situation's status is `NOT_STARVED`. I flag it as a distinct path
rather than folding it into the harvest story it has nothing to do with.

---

## 4. OSC-031's other 167 turns — HONESTLY UNRESOLVED

167 of OSC-031's 189 turns have CHOP eligible and no fruit anywhere, so the harvest analysis does
not apply. The unit has `chop_power = 1` and free capacity, so `chop_candidates` ran and its
per-plant loop rejected every plant.

**I have not localized which clause rejects, and I am not going to guess.** The candidates are
`predict_tree` returning `None`, a predicted `size`/`health <= 0` at arrival, the round-trip clock
test, or `wood <= 0`. Two can be narrowed by argument — free capacity is 2, so `wood <= 0`
requires `final_size <= 0`; and with `TOTAL_TURNS = 300` against a 200-turn fixture there are
≥ 101 turns left, so the clock test is unlikely to bite — which points at the **tree-prediction**
clauses. That is a **hypothesis, untested**, and it is written here as one.

Resolving it needs `predict_tree`/`chop_outcome` replicated faithfully or logged directly, and a
wrong replica would be worse than no answer. I would rather hand over a named open item than a
fourth cause claim resting on an unvalidated proxy.

---

## Summary

| mechanism | turns | reading |
|---|---:|---|
| endgame harvest fallback gated out of the mid-game while the endgame generator is in use | 325 | **deliberate gating, wrong scope** — cure property fails by design |
| opponent camping the plant; subject correctly declines, **my oracle over-counts** | 28 | **correct behaviour** — instrument limitation, reported against myself |
| full-capacity unit, `bank_candidates` empty (OSC-005) | 1 | distinct path, not starvation |
| chop rejected inside the per-plant loop (OSC-031) | 167 | **unresolved**; clause not localized, hypothesis stated only |

Turn totals reconcile against the pool-#3 table: 325 + 28 = 353 harvest-eligible turns
(= 78 `HARVEST` + 275 `CHOP+HARVEST`), plus 167 `CHOP`-only and 1 `BANK+CHOP` = **521**, the
`NO_GOAL_ASSIGNED` turn total. (My first draft of this summary wrote 311 for the first row while
the per-situation table above already summed to 325; the table was right.)

Nothing here prices anything or recommends a cure. Whether the gating is worth changing is pool
#6, the owner's.
