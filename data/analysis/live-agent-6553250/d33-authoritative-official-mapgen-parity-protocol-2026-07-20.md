# D33 authoritative official-map generator parity — protocol (2026-07-20)

## Purpose

D30 proved that the synthetic generator's three mirrored water pairs are the dominant input shift
for D29, and D32 proved that correcting a selector alone cannot rescue its farm option.  Before
training or evaluating another complete architecture, D33 tests whether the actual referee map
generator can replace the synthetic substrate exactly.

The authoritative board source is `engine.Board.createMap` from
`https://github.com/eulerscheZahl/Troll-Farm`, pinned before implementation at commit
`290129129db7a7539d98739ebdb0ed63ee6ceb50` (2026-05-26).  Its Legend path uses the
game-manager RNG through a `Random`-typed interface, random-walk rivers, mirrored
terrain/resources, validity rejection, and water-aware tree aging.  D33a records the primary-source
discovery that game-engine 4.7.8 supplies SUN SHA1PRNG through that interface.  The port must be
behavioral; no empirical distribution fitting is allowed.

## Frozen samples

### Development witnesses

Use the three exact D32a turn-one inputs for seeds:

- `9213838685008738669`;
- `995889697906457104`; and
- `-1363387433195008244`.

They cover heights 8--11 and were already consumed by D32.  Their raw texts may be used during
implementation.

### Archived confirmation

Before implementation, create a 120-game manifest from `data/raw/games` by ascending game ID.
Eligibility is outcome-blind: a parseable signed `refereeInput` seed, a valid turn-one input at
seat 0, Legend terrain (`~` and `+`), height 8--11, and a seed not already selected.  Exclude all
171 D29 resident-checkpoint game IDs and all D32a game IDs.  Store raw-file hashes.  Once written,
the manifest and selection order are immutable.

The confirmation turn-one texts must not be inspected during implementation.  Only the analyzer
may compare them after the development witnesses are exact and the Rust source hash is frozen.

## Implementation boundary

Add a separate `generate_official(seed: i64)` path.  Do not change `generate_bronze`, existing seed
semantics, old experiment artifacts, or any policy.  The port must implement:

1. Java 17 SUN SHA1PRNG state/seed semantics plus inherited bounded `nextInt` behavior, as frozen
   in the D33a amendment;
2. the exact random-call order across rejected map attempts;
3. 8--11 height and twice-height width;
4. two or three symmetric random-walk rivers and the referee's shared river budget;
5. inventory, shack, iron, rock, and four fruit-type placement order;
6. water-aware initial tree aging and list order; and
7. the referee's connectivity, iron, shack, and maximum-opponent-distance validity rules.

Provide a standalone binary that renders the exact player-0 turn-one protocol input for a signed
seed.  Existing engine/mapgen tests must remain green.

## Frozen gates

All are conjunctive:

1. manifest has exactly 120 unique games and seeds, zero excluded IDs, exact raw-file hashes, and
   deterministic regeneration;
2. all three development states satisfy D33b canonical identity on two independent executions;
3. freeze the Rust source/binary hashes before opening confirmation comparisons;
4. all 120 archived confirmation states satisfy D33b canonical identity, with zero grid,
   inventory, plant-state, unit, dimension, generated-live-order, or trailing-newline mismatches;
5. generated maps satisfy point symmetry, official count ranges, connectivity, and initial state
   invariants; and
6. focused tests plus the existing Rust library test suite pass.

A pass accepts `generate_official` as the default substrate for **new** experiments only.  It does
not rehabilitate D29/D32, validate any opponent model, authorize a candidate, or consume D29
checkpoint rows 81--171.  A confirmation failure closes this exact implementation; confirmation
examples may diagnose the first differing component but may not tune and rerun the same gate.

## Next-step rule

- **Pass:** D34 measures policy/opponent transfer again on authoritative maps and selects a new
  complete architecture before any training-scale run.
- **Fail:** use exact recorded maps as fixtures and separately diagnose the missing game-manager
  seed transform or referee-version drift on a fresh block.
