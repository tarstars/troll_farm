# v1.49.0-farmhand

Local verdict: **REJECT / NOT SUBMITTED** on 2026-07-09 01:57 MSK.

## Idea

Re-test the old third-hand lever with the narrowest version suggested by the v1.35.0-thand
postmortem: train a cheap pure farm hand, but keep that hand's fruit errands local so it does
not become the old map-crossing tourist.

Mechanism:

- `VERSION` -> `1.49.0-farmhand`.
- `GE_MAX_TROLLS` 2 -> 3.
- Farmhand role filter in `planner.rs`:
  - `plan.n >= 3`
  - `u.chop_power == 0`
  - `u.harvest_power > 0`
- Only that role was restricted:
  - printer seed-tree band 52 required `farm_d <= farm_r`;
  - idle-fruit band 38 required `farm_d <= farm_r`.
- Starter and chopper behavior stayed as in `v1.46.0-splitclaims`.

## Code Gates

Passed:

- `cargo test --manifest-path rust/Cargo.toml --release --test tactics_scale`
  - `7 passed`, with old T-hand tests re-enabled for this candidate.
- `cargo test --manifest-path rust/Cargo.toml --release`
  - all active tests passed.
- Self equality:
  - `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
- Bundle/minify:
  - bundled artifact: `99,500` bytes by `wc -c`;
  - minified artifact: `59,973` bytes;
  - debug minified probe: `59,972` bytes.
- Bundled equality:
  - `EQUAL: 16 games`.
- Minified equality:
  - `EQUAL: 16 games`.

Frozen artifacts:

- `data/candidates/v1.49.0-farmhand/v1.49.0-farmhand.rs`
- `data/candidates/v1.49.0-farmhand/v1.49.0-farmhand.min.rs`
- `data/candidates/v1.49.0-farmhand/v1.49.0-farmhand.debug.rs`
- `data/candidates/v1.49.0-farmhand/v1.49.0-farmhand.debug.min.rs`
- `cgauto/submissions/v1.49.0-farmhand.rs`
- `cgauto/submissions/v1.49.0-farmhand.min.rs`

## Local Gate

Boss 8 DEBUG probe using
`data/candidates/v1.49.0-farmhand/v1.49.0-farmhand.debug.min.rs`:

- Games: `895527137`, `895527157`, `895527162`, `895527165`, `895527170`,
  `895527172`, `895527175`, `895527191`.
- Result: `0/8`.
- Average wood: us `46.4`, boss `63.8`.
- Ramp:
  - t75: `+3.1`
  - t150: `+1.0`
  - t225: `-5.0`
  - t300: `-17.4`
- Late quarter t225 -> t300:
  - us `+11.5`
  - boss `+23.9`

The ramp script's stored baseline line for this gate was `14%` wins, final wood `38.7`,
t300 delta `-15.3`, late gain us about `+12` vs boss about `+23`. The candidate improved our
own final wood but worsened the final delta and scored zero wins.

## Mechanism Check

The change was not a no-op. The third hand trained in 7 of 8 Boss games:

- first `n=3` at t85: `895527165`, `895527175`
- first `n=3` at t115: `895527162`
- first `n=3` at t140: `895527172`
- first `n=3` at t145: `895527170`
- first `n=3` at t150: `895527137`
- first `n=3` at t175: `895527157`

The final build summaries show the added troll as `1.1.1.0` in those games. The extra hand
therefore engaged, but it did not repay its training bill or close the late wood-ramp gap.

## Verdict

**LOCAL REJECT / NOT SUBMITTED.**

Do not submit this candidate. Do not retry simple "farm-ring-restricted cheap third hand" as
the next workforce lever. If extra workforce is revisited, it needs a materially different
economic role or late-ramp plan, not just local fruit errands for a pure gatherer.

Active source was restored to `v1.46.0-splitclaims` behavior after rejection:

- `VERSION` back to `1.46.0-splitclaims`.
- `GE_MAX_TROLLS` back to `2`.
- farmhand-only planner filters removed.
- v1.49-specific tests parked with `#[ignore]`.
- `cargo test --manifest-path rust/Cargo.toml --release` passed.
- Restored release bot equals frozen `v1.46.0-splitclaims.min.rs`:
  `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.

Arena was not touched. `cgauto/api_submit.py` default remains the promoted
`v1.43.0-yield` artifact.
