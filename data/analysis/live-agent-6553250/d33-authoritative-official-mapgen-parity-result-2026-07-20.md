# D33 authoritative official-map generator parity — result (2026-07-20)

## Verdict

**Pass as the default map substrate for new experiments.**  The separate Rust
`generate_official(seed: i64)` path matches all three development states and all 120 untouched
archived confirmation states with zero grid, inventory, plant-state, unit, dimension, invariant,
or trailing-newline failures.  Every frozen gate passes.

This validates map generation only.  It does not rehabilitate D29/D32, validate the old opponent
zoo, authorize a candidate, or authorize an Arena submission.  The historical
`generate_bronze` path remains unchanged so old artifacts retain their original semantics.

## Gate result

| Gate | Result |
|---|:---:|
| Deterministic 120-game outcome-blind manifest | pass |
| Three development states, two executions each | 3/3 pass |
| Source/binary identity frozen before confirmation | pass |
| Untouched archived confirmation | **120/120 pass** |
| Point symmetry and official terrain/economy/state invariants | 123/123 pass |
| Focused Python tests | 20/20 pass |
| Complete Rust library tests | 58/58 pass |

The manifest contains 120 unique games and seeds in ascending game-ID order, zero overlap with
the 171-row resident checkpoint or six D32a games, zero seed-zero cases, and exact raw replay and
turn-one hashes.  Independent manifest regeneration is byte-identical.

## Two development corrections

Both corrections were frozen from primary source before any confirmation text was opened.

1. **D33a — actual RNG.**  The board stores a `Random`, but game-engine 4.7.8 supplies
   `SecureRandom.getInstance("SHA1PRNG")`.  A direct 48-bit `java.util.Random` port failed all
   three development maps.  The SUN SHA1PRNG port reproduces the signed-long seed encoding,
   SHA-1 state, remainder stream, signed-byte state update, and inherited bounded `nextInt`
   behavior.  It immediately made every map, inventory, plant state, and unit exact.
2. **D33b — replay evidence order.**  Archived replay diffs serialize plants through a Java
   `HashMap`, so their reconstructed order is not the `ArrayList` order sent to players.  All
   development plant lines were exact as multisets while replay order differed.  The gate therefore
   compares the exact prefix, duplicate-preserving seven-field plant multiset, and exact unit
   suffix, while independently requiring the live type-grouped first/mirror order dictated by
   `Board.placeTree`.

These are source-backed corrections to the evidence model, not tuning to confirmation examples.
The held-out 120-map gate was executed once after the corrected implementation and hashes were
frozen.

## Analysis at different abstractions

1. **Mechanics:** local terrain and initial ecosystem state can now be generated exactly from an
   Arena seed.  D30's dominant water shift is removed at its cause rather than normalized away.
2. **Simulation:** dimensions, random-walk rivers, inventory, shacks, iron, rocks, trees, initial
   water-aware aging, validity rejection, and rejected-attempt RNG consumption all match the
   referee.  This removes the largest known static simulator-to-field mismatch.
3. **Representation:** models trained on new official maps will no longer learn that water count
   is a six-cell constant.  This does not solve dynamic opponent shift or policy-label validity.
4. **Replay methodology:** archived states preserve plant content but not live plant list order.
   Order-sensitive replay continuations must reconstruct the board's type/pair order or explicitly
   prove command invariance.  D31's 80/80 exact warmed root commands remain valid evidence for its
   roots, but replay order must not be assumed generally.
5. **Project strategy:** the bottleneck moves from map fidelity to complete-policy and opponent
   transfer.  The next experiment should measure candidate architectures on this substrate before
   any further PPO-scale training or field submission.

## Reproducibility

- machine result SHA-256:
  `f28820abcf79651fa3212599d42f2854eb96c709643d617dffb8e2748220f71f`;
- confirmation manifest SHA-256:
  `159a79cae7014ca32449496994e20d8e7ba52f1a41d2e00ed5f3064d171e5a0d`;
- official generator source SHA-256:
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`;
- renderer source SHA-256:
  `b1ed91c419f21b04dc1fc1cda87fc5cffbd0bf0ae5ca7d64b14985da7a45c3d0`;
- release binary SHA-256:
  `14d8cc5b2393820d67efc7959e37563fc4f394004ca390f71f1ba84752783e5e`;
- analyzer source SHA-256 at confirmation:
  `b4541930312e8b961543909c601ae8e45552475dafd5fc43ff3bfa12455cb753`;
- game-engine 4.7.8 source artifact SHA-256:
  `bf9e8b8a253626f5fa307bdedb5c732e96251a7aa8ec554416debfa27d63e7ab`.

## Next experiment

D34 must run an official-map policy-transfer census: compare complete controller families and
opponent interactions on fresh official seeds, measure whether the old zoo's macro conclusions
change, and select one architecture that preserves resident suppression while adding renewable
production.  It is a discriminator and architecture-selection step, not a parameter sweep.

