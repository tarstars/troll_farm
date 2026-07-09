# v1.52.0-lateseedhome

Arena status: **REJECTED / REVERTED** on 2026-07-09 MSK.

## Idea

Recent phase-binned arena losses showed the decisive gap after t150: our CHOP count falls while
opponents keep a sustained PICK/PLANT/DROP/CHOP loop alive. DEBUG replays showed a concrete
local cause: many Tempo games reach late turns with `farm=0` and banked banana seeds still in
the tent, while the starter walks to remote ripe seed trees because tree-first printer band 52
outranks tent PICK/Park band 50.

This candidate keeps early `v1.37.0-nanaflow` tree-first behavior intact, but after t150 under
live Tempo, if the farm is below the protected seed-reserve floor (`base_trees < 2`) and a
plantable cell exists, tent banana pickup is raised to band 54. Once the starter carries the
banana, existing band 88 plants it. No third troll, no roam change, no global printer demotion.

## Code Gates

Passed:

- `cargo test --manifest-path rust/Cargo.toml --release --test lateseedhome`
- `cargo test --manifest-path rust/Cargo.toml --release`
- Bundled equality: `EQUAL: 16 games`
- Minified equality: `EQUAL: 16 games`
- `git diff --check` on edited source/test files

Artifacts:

- `data/candidates/v1.52.0-lateseedhome/v1.52.0-lateseedhome.rs`
- `data/candidates/v1.52.0-lateseedhome/v1.52.0-lateseedhome.min.rs`
- `data/candidates/v1.52.0-lateseedhome/v1.52.0-lateseedhome.debug.rs`
- `data/candidates/v1.52.0-lateseedhome/v1.52.0-lateseedhome.debug.min.rs`
- `cgauto/submissions/v1.52.0-lateseedhome.rs`
- `cgauto/submissions/v1.52.0-lateseedhome.min.rs`

Minified size: `59968` bytes. DEBUG minified size: `59967` bytes.

## Local Gate

Boss 8:

- `1/8` wins.
- Final wood: us `47.9`, boss `55.1`.
- Ramp: t75 `+5.0`, t150 `+3.4`, t225 `+3.2`, t300 `-7.2`.
- Late quarter: us `+11.9`, boss `+22.4`.
- Farm-zero rate in t151-225 improved in the sampled Boss 8 to `43%` versus the older Tempo
  aggregate around `74%`.

Field candidate probes:

- `plcc` (`6480966`): `1/2`, score `232-279`, wood `56-68`.
- `mikdiet` (`6480914`): `1/2`, score `202-204`, wood `48-48`.
- `kurigen` (`6480824`): `1/2`, score `299-232`, wood `69-55`.
- Aggregate: `3/6`, score `244.3-238.0`, wood `57.8-57.0`.

Direct frozen `v1.46.0-splitclaims` comparison collected immediately after:

- `plcc`: `1/2`, score `250-193`, wood `56-44`.
- `mikdiet`: `1/2`, score `175-167`, wood `38-26`.
- `kurigen`: `0/2`, score `273-346`, wood `63-86`.
- Aggregate: `2/6`, score `232.7-235.2`, wood `52.3-52.5`.

Verdict from local gate: **arena-worthy but risky**. It improves Boss ramp and direct aggregate
field score, but `plcc` is worse on opponent wood. Submit, monitor tightly, and do not promote
default unless the arena policy bar is met.

## Arena

Bracket before submit:

- `v1.46.0-splitclaims` live slot: `127/527 Gold @17.4`, agentId `6543815`.
- `cgauto/api_submit.py` default remains promoted champion `v1.43.0-yield.min.rs`.

Submit:

- `uv run --no-sync python cgauto/api_submit.py cgauto/submissions/v1.52.0-lateseedhome.min.rs`
- Submit id: `40970510`.
- Landed as agentId `6543941`.
- First landed arena-room read: `521/527 @0.0` (fresh low; not a verdict).

Arena reads:

- Landed: `521/527 @0.0`, agentId `6543941`.
- Climb reads: `426/527 @10.7`, `261/527 @13.9`, `226/527 @15.1`.
- +20-ish: `211/527 @15.3`.
- Later reads: `180/528 @15.9`, `172/528 @16.2`.

Final arena verdict: **REJECT / REVERT**. Against bracket `17.4`, the decisive read was
delta `-1.2`, well past the policy v2 revert bar (`<= -0.5`).

Revert:

- Resubmitted prior live baseline `cgauto/submissions/v1.46.0-splitclaims.min.rs`.
- Revert submit id: `40971048`.
- Revert landed as agentId `6544763` with first fresh-low read `256/528 @14.2`.
- Active source restored to `v1.46.0-splitclaims`.
- `cargo test --manifest-path rust/Cargo.toml --release` passed after restore.
- Restored release bot equals frozen `v1.46.0-splitclaims.min.rs`: `EQUAL: 16 games`.
- `lateseedhome` tests are parked with `#[ignore]`.

Do not retry simple late tent-seed priority as-is. It improves local Boss/farm diagnostics but
does not survive arena scoring.
