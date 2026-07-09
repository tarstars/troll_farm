# v1.51.1-fruitstand

Local verdict: **REJECT / NOT SUBMITTED** on 2026-07-09 MSK.

## Idea

Narrow `v1.51.0-standclaim`: preserve the original `v1.46.0-splitclaims` travelling
fruit-vs-wood benefit, but prevent only the concrete stall shape. A wood candidate skips a tree
when one of our other trolls is already standing on that tree, the tree has ripe fruit, and that
troll can harvest it this turn.

This should let the fruit worker keep harvesting instead of being reassigned away, while still
preventing the chopper from trying to enter the occupied tree cell.

## Code Gates

Passed:

- `cargo test --manifest-path rust/Cargo.toml --release --test split_tree_claims`
- `cargo test --manifest-path rust/Cargo.toml --release`
- Self equality: `EQUAL: 16 games`
- Bundled equality: `EQUAL: 16 games`
- Minified equality: `EQUAL: 16 games`

Artifacts were frozen:

- `data/candidates/v1.51.1-fruitstand/v1.51.1-fruitstand.rs`
- `data/candidates/v1.51.1-fruitstand/v1.51.1-fruitstand.min.rs`
- `data/candidates/v1.51.1-fruitstand/v1.51.1-fruitstand.debug.rs`
- `data/candidates/v1.51.1-fruitstand/v1.51.1-fruitstand.debug.min.rs`
- `cgauto/submissions/v1.51.1-fruitstand.rs`
- `cgauto/submissions/v1.51.1-fruitstand.min.rs`

Minified size: `60245` bytes. DEBUG minified size: `60244` bytes.

## Local Gate

Boss 8:

- `0/8` wins.
- Final wood: us `48.1`, boss `59.1`.
- Ramp: t75 `+5.4`, t150 `+3.2`, t225 `-2.5`, t300 `-11.0`.
- Late quarter: us `+12.9`, boss `+21.4`.

Field probes:

- `plcc` (`6480966`): `0/2`, wood `60-91`.
  - The stall was fixed: new block rates were `0.0%` and `0.5%`.
  - Score shape was basically back to v1.46-level, not an improvement.
- `mikdiet` (`6480914`): `0/2`, wood `80-92`.

## Verdict

**LOCAL REJECT / NOT SUBMITTED.**

The exact stall mechanism is real and now understood, but "standing fruit worker protects the
tree from wood" is not profitable. It removes the block without increasing the field score and
craters the `mikdiet` probe. Do not retry simple standing fruit-vs-wood claim exclusivity as the
next rank push.

Active source was restored to `v1.46.0-splitclaims` after rejection:

- `VERSION` back to `1.46.0-splitclaims`.
- The standing-fruit wood-skip rule removed.
- The v1.51 standing-claim regression test parked with `#[ignore]`.
- `cargo test --manifest-path rust/Cargo.toml --release` passed.
- Restored release bot equals frozen `v1.46.0-splitclaims.min.rs`: `EQUAL: 16 games`.

Arena was not touched. `cgauto/api_submit.py` default remains the promoted
`v1.43.0-yield` artifact.

