# Candidate v1.47.0-ripefund - Local Reject

**Task:** test D3 funding-stall robustness by adding chopper-funding ripeness anticipation.

## What Was Tried

Two local variants were tested:

- Broad form: while the chopper was pending, a starter could pre-position for any soon-ripe
  deficit PLUM/LEMON/APPLE at band 57, below already-ripe funding band 58 and above printer
  work.
- Narrowed form, frozen in this candidate artifact: pre-position only when that one harvest
  could complete the chopper fruit wallet and the other fruit costs were already covered.

The intent was to reduce fruit-poor starts where the second troll trains late because funding
only sees already-ripe deficit fruit.

## Gates

For the narrowed frozen form:

- `cargo test --release --test funding_anticipation`: `2 passed`.
- `cargo test --release --test phase_hoard`: `7 passed`.
- `cargo test --release`: all active tests passed.
- Self equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- Bundled equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- Minified equality: `EQUAL: 16 games (8 seeds x 2 seats)`.
- Minified size: `61761` bytes.

## Frozen Artifacts

- `data/candidates/v1.47.0-ripefund/v1.47.0-ripefund.rs`
- `data/candidates/v1.47.0-ripefund/v1.47.0-ripefund.min.rs`
- `data/candidates/v1.47.0-ripefund/v1.47.0-ripefund.debug.rs`
- `data/candidates/v1.47.0-ripefund/v1.47.0-ripefund.debug.min.rs`
- `cgauto/submissions/v1.47.0-ripefund.rs`
- `cgauto/submissions/v1.47.0-ripefund.min.rs`

## Mini-Gate Results

Broad form:

- Boss 8: `1/8 wins | our wood 47 | opp wood 60`; ramp t300 `-13.5`.
- plcc (`6480966`): `0/1 wins | our wood 48 | opp wood 83` (one play failed HTTP 422).
- mikdiet (`6480914`): `0/2 wins | our wood 34 | opp wood 52`.

The broad form was rejected because it cratered the `6480914` probe that v1.46 had won `2/2`.

Narrowed frozen form:

- Boss 8: `1/8 wins | our wood 44 | opp wood 62`; ramp t300 `-18.1`.
- plcc (`6480966`): `0/1 wins | our wood 78 | opp wood 107` (one play failed HTTP 422).
- mikdiet (`6480914`): `0/1 wins | our wood 62 | opp wood 106` (one play failed HTTP 422).

## Verdict

**LOCAL REJECT / NOT SUBMITTED.** Both variants made field probes worse, and the narrowed form
lost the modest Boss wood lift from the broad form. Do not submit this artifact. Do not retry
simple chopper-funding ripeness anticipation at band 57; it appears to delay or misallocate the
opening economy against production-heavy field bots.

Active source was restored to `v1.46.0-splitclaims` behavior after the rejection. The live arena
slot was not touched.
