# v1.57.0-ringtune builder brief — fix the as-built ringfarm (E1 + E2 + banana no-carry)

**Base:** current session HEAD = v1.56.0-ringfarm (the ring is built, validated: 3-5 cells
planted by turn 20 vs baseline 0). This candidate TUNES it per the code review (E1/E2) + a user
game-watch finding (banana no-carry). No new capability — refine the existing ring logic.
Bump VERSION to "1.57.0-ringtune". Preserve all champion consts.

## Three fixes (all in planner.rs candidates() + the ring/plant logic; tactics.rs if needed)

### FIX 1 — E1: fund the chopper BEFORE building the ring
The build-ring-pick(78) currently outranks the funding bands (58-65), so in the opening the
starter stocks the ring INSTEAD of funding the existential chopper (the review's diagnosis of
the boss 0/4). `Plan.want_chopper` (tactics.rs:84) is the signal.
FIX: while `plan.want_chopper` is true, SUPPRESS the build-ring-pick band (do not emit the 78
pick, and do not emit the ring-plant that depends on a picked banana) — fund the chopper first.
Once `!want_chopper` (chopper funded/trained), the ring builds normally. Keep the ORDINARY plant
(a banana already in carry) available so a troll that harvested a banana can still plant it — the
suppression targets the PICK-from-tent-to-build-ring, not all planting. Verify: with want_chopper
true + tent bananas + empty ring, the starter's top task is the FUNDING/iron/chop-help work, not
the ring pick.

### FIX 2 — E2: diagonal-priority placement
`plant_cell` (planner.rs ring path) picks the NEAREST empty ring cell by `min(d[c], tie)`.
Orthogonals are map-distance 1, diagonals 2 (tent impassable), so nearest-first fills all
orthogonals first and refills cut orthogonals ahead of ever planting a diagonal — the diagonal
fruit/seed engine (the scheme's whole point) builds last.
FIX: prioritize DIAGONAL ring cells over orthogonal when choosing the plant target. Concretely
sort empty ring cells by `(role_rank, d[c], tie)` where role_rank = 0 for Diagonal, 1 for
Orthogonal — so an empty diagonal is always chosen before an empty orthogonal, and within a role
the nearest wins. (Keep determinism: canonical tie.) Verify: on an empty ring the first plant
targets are diagonals.

### FIX 3 — banana NO-CARRY-IN-ADVANCE (user, watching as-built)
The anti-pattern: PICK a banana from the tent, then CARRY it (walking, sometimes BACKTRACKING to
the tent to grab it, and passing ripe banana trees) to a plant cell. User principle: never pick
from the tent in advance. Two valid modes ONLY:
  (a) pick from tent -> PLANT IMMEDIATELY: only PICK when an empty ring cell is ADJACENT to the
      troll's current position (pick this turn, step onto/next-to the cell, plant next turn — no
      travelling far with a held banana). Concretely: gate the build-ring-pick on
      `nearest_empty_ring_cell is within 1-2 steps of the troll AND of the tent` (i.e. the pick
      is immediately actionable), not merely "the ring has an empty cell somewhere".
  (b) pick up ON THE WAY: prefer HARVESTING a ripe banana the troll is at/adjacent to over
      PICKing tent stock — a harvested banana can then be seeded (planted) or banked. I.e. if a
      ripe banana is harvestable at/near the troll, that outranks a tent PICK.
FIX: (i) the build-ring-pick fires only when the plant is immediate (adjacent empty ring cell);
(ii) harvesting a ripe/adjacent banana is preferred over a tent PICK when both are available.
This also cures the BACKTRACKING (the troll no longer returns to the tent to grab a banana it
will carry away). Verify: a troll NOT adjacent to an empty ring cell does NOT PICK from the tent
(it does other work); a troll passing a ripe banana harvests it rather than PICKing tent stock.

## CUT SIZE — leave at 2 (unchanged)
Orthogonal cut-bananas stay felled at the live `farm_fell=2` (GE_FARM_FELL=3 is dead code). The
user's size-2-vs-3 question is deferred to a separate decision; do NOT change it here.

## Tests (TDD, RED first — reuse the ringfarm fixtures where possible)
1. `ringtune_fund_chopper_before_ring`: want_chopper=true + tent bananas + empty ring -> top task
   is funding/chop work, NOT the ring pick. RED (pre-fix the 78 pick wins). When want_chopper=false,
   the ring pick returns (guard against over-suppression).
2. `ringtune_diagonal_planted_first`: empty ring, banana available, troll positioned so both a
   diagonal and orthogonal empty cell are reachable -> plant target is the DIAGONAL. RED (pre-fix
   nearest orthogonal wins).
3. `ringtune_no_pick_when_plant_not_immediate`: troll far from any empty ring cell + tent has a
   banana -> troll does NOT PICK (no carry-in-advance). RED (pre-fix picks whenever ring has a gap).
4. `ringtune_harvest_ripe_over_tent_pick`: a ripe banana adjacent to the troll AND tent stock ->
   the troll HARVESTS the ripe banana, not a tent PICK. RED.
5. Existing ringfarm tests (7) + full suite stay green; adjust any ringfarm test whose premise the
   tuning changes, documenting why. Self-determinism equality 8 seeds.

## Gates + validation
- Standard builder gates (cargo test, bundle/rustc/minify<100KB, freeze artifacts + debug probe).
- Candidate validation: play vs boss + Crouistiti (6479836) with a DEBUG probe. REPORT: (a) is the
  chopper trained EARLIER than the as-built ringfarm (E1 working)? (b) are diagonals planted before
  orthogonals (E2)? (c) do PICK-from-tent-then-carry chains / backtracking disappear (FIX 3)? (d)
  wood not cratered, boss win-rate vs as-built. If the play-API overloads, commit + stop cleanly.
- COMMIT PER FIX (resilience: API has dropped subagents today) — Fix1, Fix2, Fix3, tests, gates as
  separate commits with the trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

Report: status, commit hashes, test summary (RED evidence each), the three fixes' exact gate
conditions, the validation (chopper-timing / diagonal-first / no-backtrack / wood), self-equality,
artifact sizes, concerns.
