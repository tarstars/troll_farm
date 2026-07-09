# v1.51.0-standclaim

Local verdict: **REJECT / NOT SUBMITTED** on 2026-07-09 MSK.

## Idea

Follow-up to the `v1.50.1-latethreat` `plcc` blowout. The severe `18-97` field loss was not
caused by late threat targeting alone: `motion_analyze.py` found `91/265` blocked intended moves
(`34.3%`). The repeated block was chopper `id=2` at `(2,7)` trying to enter `(2,6)` while
starter/gatherer `id=0` stayed on `(2,6)` harvesting fruit for roughly 90 turns.

`v1.51.0-standclaim` changed split fruit-vs-wood claims so a fruit claimant already standing on
the target tree made the same tree exclusive for that turn. Travelling fruit-vs-wood split claims
were still allowed.

## Code Gates

Passed:

- `cargo test --manifest-path rust/Cargo.toml --release --test split_tree_claims`
- `cargo test --manifest-path rust/Cargo.toml --release`
- Self equality: `EQUAL: 16 games`
- Bundled equality: `EQUAL: 16 games`
- Minified equality: `EQUAL: 16 games`

Artifacts were frozen:

- `data/candidates/v1.51.0-standclaim/v1.51.0-standclaim.rs`
- `data/candidates/v1.51.0-standclaim/v1.51.0-standclaim.min.rs`
- `data/candidates/v1.51.0-standclaim/v1.51.0-standclaim.debug.rs`
- `data/candidates/v1.51.0-standclaim/v1.51.0-standclaim.debug.min.rs`
- `cgauto/submissions/v1.51.0-standclaim.rs`
- `cgauto/submissions/v1.51.0-standclaim.min.rs`

Minified size: `59626` bytes. DEBUG minified size: `59625` bytes.

## Local Gate

Boss 8:

- `1/8` wins.
- Final wood: us `47.4`, boss `56.1`.
- Ramp: t75 `+4.6`, t150 `+0.8`, t225 `-3.6`, t300 `-8.8`.
- Late quarter: us `+11.2`, boss `+16.4`.

Field probes:

- `plcc` (`6480966`): `0/2`, wood `74-106`.
  - The collapse was fixed: new block rates were `3.1%` and `1.4%`, versus `34.3%` in the
    rejected `v1.50.1` severe loss.
- `mikdiet` (`6480914`): `1/2`, wood `75-65`.

## Verdict

**LOCAL REJECT / NOT SUBMITTED.**

The mechanism fixed the stall, but the field score was not better enough to submit. The matcher
often resolved the new conflict by moving the fruit worker away from the ripe tree so the
chopper could take it, which looked too wood-biased and did not improve the rank-gate field
shape.

This led to the narrower follow-up `v1.51.1-fruitstand`.

