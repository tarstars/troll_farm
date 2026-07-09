# v1.50.1-latethreat

Local verdict: **REJECT / NOT SUBMITTED** on 2026-07-09 02:21 MSK.

## Idea

Respond to observed late cross-half raids without repeating the rejected static early-roam
variant. The chopper gets an emergency own-half fell candidate when an enemy wood-capable troll
is already near one of our fellable own-half trees.

Two forms were tried:

- `v1.50.0-threatfell`: broad trigger at any turn.
- `v1.50.1-latethreat`: narrowed trigger with `state.turn >= 150`.

Final narrowed mechanism:

- `VERSION` -> `1.50.1-latethreat`.
- `GE_MAX_TROLLS` remains `2`.
- Add a chopper-only emergency candidate:
  - tree is fellable by the normal `fell_ok` rule;
  - tree is on our half;
  - enemy wood-capable troll is within Manhattan distance `<= 2`;
  - current turn is `>= 150`;
  - existing `race()` still rejects trees the enemy will finish before we arrive.
- Emergency travel uses band 71, above ordinary travel-fell band 70 and below standing
  `ChopHere` band 72.

## Code Gates

Passed:

- `cargo test --manifest-path rust/Cargo.toml --release --test threatfell`
  - `4 passed`.
- `cargo test --manifest-path rust/Cargo.toml --release`
  - all active tests passed.
- Self equality:
  - `EQUAL: 16 games`.
- Bundle/minify:
  - bundled source: `100,866` bytes, over the 100 KB submission cap;
  - minified source: `60,930` bytes, submission-safe;
  - DEBUG minified source: `60,929` bytes.
- Bundled equality:
  - `EQUAL: 16 games`.
- Minified equality:
  - `EQUAL: 16 games`.

Frozen narrowed artifacts:

- `data/candidates/v1.50.1-latethreat/v1.50.1-latethreat.rs`
- `data/candidates/v1.50.1-latethreat/v1.50.1-latethreat.min.rs`
- `data/candidates/v1.50.1-latethreat/v1.50.1-latethreat.debug.rs`
- `data/candidates/v1.50.1-latethreat/v1.50.1-latethreat.debug.min.rs`
- `cgauto/submissions/v1.50.1-latethreat.rs`
- `cgauto/submissions/v1.50.1-latethreat.min.rs`

Broad pre-gate artifacts also exist under `v1.50.0-threatfell`; they should not be submitted.

## Local Gates

### Broad v1.50.0-threatfell

Boss 8 looked initially promising:

- `2/8` wins.
- Final wood `40.8-48.8`.
- Ramp t75 `+4.2`, t150 `+4.2`, t225 `-0.9`, t300 `-8.0`.
- Late quarter: us `+10.5`, boss `+17.6`.

But field probes showed the trigger was too broad:

- `mikdiet` (`6480914`): `1/2`, wood `40-41`.
- `plcc` (`6480966`): `0/2`, wood `85-134`.

Verdict on the broad form: too loose; do not submit.

### Narrowed v1.50.1-latethreat

Boss 8 remained watchlist-positive:

- `2/8` wins.
- Final wood `46.9-59.6`.
- Ramp t75 `+1.2`, t150 `-0.5`, t225 `-6.5`, t300 `-12.8`.
- Late quarter: us `+11.2`, boss `+17.5`.
- Stored baseline line for this gate: `14%` wins, final wood `38.7`, t300 delta `-15.3`,
  late gain us about `+12`, boss about `+23`.

Field probes rejected it:

- `mikdiet` (`6480914`): `2/2`, wood `68-60`.
- `plcc` (`6480966`): `0/2`, wood `30-77`, including one severe `18-97` game.

The narrowed trigger avoids the broad variant's `mikdiet` crater but still fails the harsh
rank-gate field probe badly. It is not safe to submit.

## Verdict

**LOCAL REJECT / NOT SUBMITTED.**

The idea can reduce Boss late gain, but the field probe shows that emergency defending pulls the
chopper into bad work on at least one production-heavy rank-gate opponent. Do not retry simple
enemy-near-tree emergency fell priority. A future late-raid response needs stronger selectivity,
probably tied to actual opponent cross-half position and remaining tree economics, not just
enemy proximity to one own-half tree.

Active source was restored to `v1.46.0-splitclaims` behavior:

- `VERSION` back to `1.46.0-splitclaims`.
- emergency band 71 removed from active planner.
- `threatfell` tests parked with `#[ignore]`.
- `cargo test --manifest-path rust/Cargo.toml --release` passed.
- Restored release bot equals frozen `v1.46.0-splitclaims.min.rs`:
  `EQUAL: 16 games`.

Arena was not touched. `cgauto/api_submit.py` default remains the promoted
`v1.43.0-yield` artifact.
