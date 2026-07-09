# Candidate v1.48.0-localprinter - Local Reject

**Task:** D8 local-printer demotion. The hypothesis was that the premium printer seed-tree band
was too strong when the only ripe banana/water-apple was far from the farm. The candidate kept
band 52 for seed trees inside the farm ring (`farm_d <= farm_r`) but let distant ripe fruit stay
available through the lower idle-fruit band 38.

## What changed

- `VERSION` was bumped to `1.48.0-localprinter`.
- `planner.rs` printer band 52 gained a farm-ring gate for ripe banana / water-adjacent apple
  seed sources.
- `nanaflow.rs` temporarily gained focused tests proving local seed-tree priority, far seed-tree
  demotion below tent stock, and far-fruit fallback through idle-fruit.
- A reusable read-only analyzer was added at `cgauto/battle_taxonomy.py`; it counts command types
  from recent arena `gameResult` frames.

## Code Gates

- Focused suites during the candidate:
  - `cargo test --release --test nanaflow`: `4 passed`.
  - `cargo test --release --test split_tree_claims`: `3 passed`.
  - `cargo test --release --test idlefruit`: `3 passed`.
- Full release suite: all active tests passed.
- Self equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- Bundled equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- Minified equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- Minified size: `59759` bytes.
- DEBUG smoke equality: `EQUAL: 4 games (2 seeds x 2 seats)`.

## Frozen Artifacts

- `data/candidates/v1.48.0-localprinter/v1.48.0-localprinter.rs`
- `data/candidates/v1.48.0-localprinter/v1.48.0-localprinter.min.rs`
- `data/candidates/v1.48.0-localprinter/v1.48.0-localprinter.debug.rs`
- `data/candidates/v1.48.0-localprinter/v1.48.0-localprinter.debug.min.rs`
- `cgauto/submissions/v1.48.0-localprinter.rs`
- `cgauto/submissions/v1.48.0-localprinter.min.rs`

## Mini-Gate

Boss 8:

- `2/8` wins.
- Formal ramp: t75 `+4.5`, t150 `+3.1`, t225 `-4.5`, t300 `-13.4`.
- Final wood: us `41.2`, boss `54.6`.
- Late gain: us `+8.0`, boss `+16.9`.

Field probes:

- mikdiet (`6480914`): `1/2`, wood `72-51`. This is worse than v1.46's `2/2`, wood `72-26`.
- plcc (`6480966`): `0/1`, wood `72-117`.

## Verdict

**LOCAL REJECT / NOT SUBMITTED.** The Boss headline did not crater, but the mechanism worsened
the mikdiet field probe and did not help the plcc gatekeeper. It also reduced our Boss final wood
relative to the v1.46 watchlist. Do not retry the simple "premium printer only local" demotion.

Active source was restored to `v1.46.0-splitclaims` after the rejection. Restore verification:

- `cargo test --release`: all active tests passed.
- `./rust/target/release/equality rust/target/release/bot rust/target/release/bot 8 300 rust/target/release/bot`:
  `EQUAL: 16 games`.
