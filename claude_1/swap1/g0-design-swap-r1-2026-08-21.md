# G-0 design note — cure α, rule R-1 (own-troll swap / yield) at the transport level

Task `20260821-swap-r1-cure`, gate **G-0**. Work owner claude_1 · reviewer codex_1 (pre-build
ruling) · integrator local_claude_1. **Design only — no code exists yet, and none will be written
until codex_1 rules.**

- Base: champion of record `547fa706cc1c…` = `cgauto/submissions/candidate-door1-pure-deletion.rs`
  (byte-identical to `claude_1/chop4c/candidate-door1.rs`).
- Seam: `MoisanBot::resolve_move_conflicts_with_priority_and_forbidden`, line **720** of the base.
- Target candidate (not yet built): `cgauto/submissions/candidate-swap-r1.rs`.

---

## 1. The seam as it stands, read from the base

Line numbers are the base file's.

1. `command_by_id` — parses `MOVE id x y` out of `commands` and maps **id → index**. Only MOVEs.
2. `projections` — per moving unit: `(id, index, current, target, landing)`, where
   `landing = next_cell(walkable, current, target, movement_speed)`.
3. `moving_ids` — ids whose `landing != current`.
4. `occupied_now` — every own unit's current cell.
5. `reserved` — initialised to the cells of own units **not** in `moving_ids`: the stationary
   ones. This is the set that blocks a swap today.
6. Any projection with `landing == current` is rewritten to `WAIT`.
7. `movers` sorted: priority ids first, then **descending id** (the engine's highest-id-wins rule).
8. Per mover, in that order:
   - if the landing is neither forbidden nor reserved → take it, `reserved.insert(landing)`;
   - else pick a **detour**: an orthogonal neighbour that is walkable, not reserved, not
     `occupied_now`, forbidden-legal, minimising BFS distance to the target;
   - else `WAIT`.

**The hole is step 8's `else`.** A mover blocked by a stationary own unit has exactly two
outcomes today, detour or `WAIT`, and in a 1-wide corridor there is no detour — so it is always
`WAIT`, forever. The engine would have allowed the exchange all along
(`docs/mechanics.md:54-56`; `rust/src/game/engine.rs:308-340` resolves circular swaps
per player). The restraint is entirely ours.

## 2. Trigger predicate (exact)

Evaluated **only** inside step 8's `else`, i.e. only for a mover that has already failed to take
its landing. Let `m` be the mover and `L = m.landing`.

α fires iff **all** of:

- **T1 — the blocker is one of ours, and stationary.** There is an own unit `U` with
  `U.cell == L` and `U.id ∉ moving_ids`. (Enemy units never block: they may share our cell, so
  they are not in `reserved` and cannot reach this branch.)
- **T2 — the exchange is a legal single tick for U.**
  `next_cell(walkable, U.cell, m.cell, U.stats.movement_speed) == m.cell`. This reuses the base's
  own projection function rather than asserting adjacency separately; it rejects the
  `movement_speed`-and-geometry cases where `m.cell` is not one step for `U`, which a bare
  adjacency test would wave through.
- **T3 — the landing is not forbidden to m**, and **`m.cell` is not forbidden to U** — the same
  `priority_ids` / `forbidden_for_non_priority` test the base applies, applied to **both**
  participants (§5).
- **T4 — the occasion.** Either
  - **(a) yield:** `U`'s selected command this tick is exactly `WAIT`; **or**
  - **(b) no detour:** the base's detour computation for `m` yields `None`.

T4(a) and T4(b) are the card's two clauses. (a) is 012 and 001 — an idle troll parked on the cell
or the tree the able troll needs. (b) is 005 and 027 — a *working* troll mid-corridor, where the
exchange is the only resolution.

**Ordering, and the one place α changes an unblocked outcome.** Under T4(a) the swap is taken
**before** the detour is tried; under T4(b) only after the detour has been shown not to exist.
So on a tick where `U` is idle **and** a detour exists, α now swaps where the base detoured.
That is a deliberate behaviour change, it is the yield rule, and it is **declared here** rather
than discovered at G-1: it is the one class of tick where α is not merely filling in a `WAIT`.
If codex_1 rules that α should be strictly detour-first, the change is one line (drop T4(a) from
the pre-detour position and let both clauses fall through to post-detour) — but then 012 and 001
are only cured on maps with no detour, which I read as against the rule's intent. **Flagging
this as the single design decision I most want ruled on.**

## 3. The emission

On a fire, both commands are rewritten in the same tick:

```
commands[m.index] = "MOVE {m.id} {L.0} {L.1}"        // m onto U's cell
commands[U.index] = "MOVE {U.id} {m.cell.0} {m.cell.1}"   // U onto m's cell
reserved.insert(L)          // already present (U was stationary); kept for clarity
reserved.insert(m.cell)     // NEW — m's vacated cell is now U's landing
swapped_ids.insert(U.id)    // U is no longer available as a swap partner this tick
```

`reserved.insert(m.cell)` is load-bearing: `m.cell` was **not** reserved (m is a mover), so
without it a third own unit could legally detour into the cell U is about to occupy, and the
engine would resolve the contest by highest id — silently discarding the yield.

`swapped_ids` prevents a second mover from choosing the same `U` as its partner later in the
same sorted pass. A unit that has already been swapped is not stationary any more, and treating
it as though it were would emit two MOVEs for one unit.

## 4. What happens to U's displaced command

`U`'s command for this tick — `CHOP`, `HARVEST`, `WAIT`, whatever `select` chose — is
**overwritten** by the exchange MOVE. It is not queued, deferred or remembered: the planner is
stateless per tick and re-plans `U` from the new board next tick.

- Under T4(a) nothing is lost: the displaced command *is* `WAIT`.
- Under T4(b) one tick of work is lost, and the card's expectation is that `U` is back on its
  tree within two ticks. **That expectation is measured at G-1, not assumed** — the trigger
  report will carry, per fire, the turn `U` resumed its displaced verb, so "2 ticks" is a
  number in the artifact and not a sentence in this note.

**Finding U's index — and the fail-closed check that makes it safe.** `commands` carries no unit
id for `WAIT`, so `command_by_id` (MOVE-only) cannot locate `U`. The usable invariant is
positional: `MoisanBot::select` builds from a `BTreeMap<i32, Vec<Candidate>>` and emits **exactly
one command per own unit in ascending id order** — the 1-unit path, the 2-unit pair path and the
general loop all do (the general loop's `unwrap_or_else(Self::wait)` guarantees no id is
skipped), and `resolve_move_conflicts` is handed that slice with no prefix, so
`commands[i]` belongs to the i-th own unit by ascending id.

That invariant is a property of a *different* function, so α does not trust it blindly. Before
any swap is considered, α builds the positional map and **verifies it against the ids it can
actually read**: for every index whose command parses as `MOVE id …`, the parsed `id` must equal
the positionally-derived id. On any disagreement α **disables itself for that tick** and the
base's detour/`WAIT` path runs unchanged. A cure that silently rewrites the wrong troll's command
is worse than no cure, and this is the cheapest construction where that outcome is impossible
rather than merely unlikely.

## 5. Interaction with `priority_ids` / `forbidden_for_non_priority` (door unblocking)

`force_unique_door_clear` sets a priority troll and forbids the door cells to everyone else. α
must not become a back door through it.

- The **mover** keeps the base's exact test: `!priority_ids.contains(&m.id) &&
  forbidden_for_non_priority.contains(&L)` → α does not fire.
- The **partner** gets the *same* test on **its** landing: if `U` is not a priority id and
  `m.cell` is forbidden for non-priority units, α does not fire. The base never had to ask this
  because `U` was not moving; α makes it move, so α owes the check. **This is the hole I would
  most expect a pre-build review to find, and it is closed by construction, not by ordering.**
- Sort order is untouched: priority movers are still served first, so a priority troll reaches
  its landing before any non-priority troll can swap into it.

## 6. Explicitly NOT touched

Candidate generation (`main_candidates`, `endgame_candidates`, `early_candidates`,
`chop_candidates`, `idle_harvest_candidates`); `MoisanBot::select` and its pair/compatibility
logic; `force_unique_door_clear`; every score and tie-break; the generator's fallbacks; the
replant block and its conjuncts; the opening and training deadline; `next_cell`, `bfs_distances`,
`ortho_neighbors`. β (teammate-aware routing, tree reservation — OSC-010, OSC-030) and γ
(OSC-026's goal flip) are **out of scope and will not be touched**. All edits are inside
`resolve_move_conflicts_with_priority_and_forbidden` plus one private helper beside it; if
anything outside proves unavoidable I stop and declare it rather than widening quietly.

## 7. Inertness, and how G-1 will prove it

On any tick where T1–T4 do not all hold, every write α can perform is skipped and the command
stream is byte-identical to the base's. The claim is structural — α only ever executes inside
step 8's `else`, and the base's own `else` outcomes (detour, then `WAIT`) remain the fallbacks —
but structure is not evidence, so G-1 measures it: over all 34 frozen fixtures, full games,
every tick on which the trigger did not fire must be byte-identical to the base's stream, and
the per-fixture trigger counts are reported (expected to fire on 005, 027, 012, 001; expected
zero on most of the rest).

**A trigger count of zero on a fixture is only meaningful if the counter can be non-zero**, so
the G-1 artifact reports the count on every fixture, not just the four, and the run fails if the
total across the corpus is zero — an α that never fires would pass a byte-identical parity check
perfectly.

## 8. Risks I can name now

1. **The swap oscillates.** m swaps past U; next tick U's re-plan sends it back through m. Two
   trolls could trade cells indefinitely — a *new* D-1 dance created by the dance cure. G-1
   reports, per fire, whether the same unordered pair swaps again within the following 4 ticks;
   a non-zero count is a design failure, not a tuning matter, and I bring it back rather than
   damping it with a cooldown I invented.
2. **The 2 % kill rule.** The card stops the cure if the exchange fires on more than 2 % of
   unit-turns across the panel. My reading: that is a *trigger-breadth* alarm — it would mean T1
   is matching ordinary crowding rather than "blocked by our own troll" — so if it trips I report
   the trigger histogram and stop, rather than tightening T1 to get under the bar.
3. **Displaced-work cost.** T4(b) costs `U` a tick of chopping. On a 20-hp apple that is real,
   and it is why the card's expectations are modest. Measured at G-1, carried into G-3.
4. **The positional-index invariant** (§4) — closed fail-closed, listed here so the ruling can
   disagree with the construction rather than only with the risk.

## 9. What I am asking codex_1 to rule on

1. **T4(a)'s position** — swap-before-detour when U is idle (§2). The one intentional change to
   an otherwise-unblocked outcome. This is the decision I most want overturned-or-confirmed
   before any code exists.
2. Whether the **partner's** forbidden-cell test (§5) is the right closure of the door-unblocking
   interaction, or whether α should simply decline to fire whenever `priority_ids` is non-empty.
3. Whether the **fail-closed positional map** (§4) is acceptable, or whether α should instead
   require a threaded id→index map from `select` (a change outside the seam, which I would then
   declare under §6).
4. Whether the **re-swap detector** (§8.1) belongs at G-1 as I propose, or is a G-3 panel matter.

No code will be written against any of this until the ruling lands.
