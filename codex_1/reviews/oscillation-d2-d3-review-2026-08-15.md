# D2 viewer contract and D3 doctrine review — 2026-08-15

Task: `20260815-oscillation-deep-dive`  
Reviewer: `codex_1`  
Subjects: `363f06bd` (D2/D3) and `b4ecdfbd` (P-2 feasibility response)

## Verdict

**REVISION_REQUIRED before owner freeze or viewer implementation.** The static/offline viewer
shape is sound, the correct 34-situation library is identified, and P-2 correctly repairs the
map alphabet, unit-row schema, FULL/PARTIAL mistake, and one-cell stall handling. Two remaining
data-contract claims are too strong, and the descriptive doctrine has four material errors or
omissions.

## D2 — viewer contract

### V1 — command continuity does not make positions exact (blocking)

All 34 windows have a contiguous own-side command line, but a command is not a realized state.
A `MOVE id x y` names a goal. Its landing depends on referee `next_cell` semantics and movement
speed; realized movement can also be affected by simultaneous collision resolution involving
the opponent, whose within-window commands and states are absent. The existing detector work
explicitly distinguishes raw MOVE targets, referee-predicted landings, and realized landings.

Therefore Phase 1 may render:

- the verbatim command (ground truth),
- the command target (ground truth), and
- a command-derived/predicted own position (inference, visibly labelled).

It may not claim that own positions are "exactly reconstructable," call them realized positions,
or use acceptance check 4's "never disagree" language as evidence of game-state accuracy. That
check is circular when the same commands generate and validate the reconstruction. Exact own
positions require per-turn referee states or an exact two-sided replay; neither exists here.

### V2 — Phase-1 side panels are entry snapshots, not current state (blocking)

Inventories, plants, opponent positions, and unit cargo/stats are frozen at episode entry. The
proposal's step-through UI must label them `at entry`, not present them as current-turn values.
Plant growth, removal, cargo changes, and inventories cannot be advanced honestly from own
commands alone.

### Accepted P-2 corrections

- Unit row is `[id, player, x, y, ms, capacity, harvest, chop, carry PLUM..WOOD]`.
- Map alphabet is `# . 0 1 + ~`; unknown characters must fail loudly.
- All 34 situations are `FULL`; OSC-032/033 have one cell, and `kind` is a top-level field.
- Render `kind` explicitly and draw opponent positions with uncertainty encoded in the picture.
- Keep verbatim commands beside any inferred destination or landing.

The blind/reveal control should exist before adjudication starts, not after early judgments have
already been made unblinded. It can hide only Decision Packet material; Phase 1 still provides
the board and frozen evidence.

## D3 — descriptive doctrine

### D1 — C2/C3 are conditional endgame branches, not global bands

C2's 10,000 CHOP overwrite and C3's 9,000/8,000 conversion planting exist only inside
`endgame_candidates`, reached under the bot's endgame routing. C3 is not generic "regeneration";
it is carried-fruit conversion with feasibility guards. State those preconditions in the labels.
Without them the hierarchy falsely implies these actions dominate throughout the game.

### D2 — the 2,400 CHOP statement overclaims its evidence

The cited method packet calls `(0, 2400]` an **assumption-dependent upper bound**, explicitly
not a proved attainable maximum. It depends on the shipped carry-capacity cap of 3 and permits
opponent distance zero, whose legal reachability is unproved. Replace "Proved ceiling 2,400"
with that bounded statement. The useful conclusion remains: under the shipped preset the normal
CHOP score cannot reach the C7 work bands.

### D3 — C7's movement arithmetic is not uniform

HARVEST travel uses `base - (travel + wait)` where travel is speed-normalized; MINE travel uses
`base - raw BFS distance`, not travel turns. The doctrine currently groups them as one band and
says walking "costs turns" off the base. Split or qualify the two formulas.

### D4 — structural overrides are missing from the hierarchy

The bot does not simply choose the globally largest numeric pair. Candidate generation can
return early (cargo safety/banking, endgame conversion), per-unit routing selects different
candidate generators, door clearing replaces candidate lists, and move-conflict resolution can
rewrite selected commands after scoring. These are hierarchy nodes even where they lack a new
score constant. Add a short ordering diagram: routing/forced replacement → candidate scoring and
pair selection → resolver rewrite. Otherwise owner adjudication will attribute final behavior to
the score ladder when the ladder never had authority over it.

## Boundary

No source, frozen library, viewer, policy, candidate, panel, TestSession, or Arena action was
changed. The sacred source remains `fff6669b…`.
