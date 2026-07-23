# D61a safe-balanced anchor amendment (2026-07-21)

## Quarantine trigger

The first byte-identical D61 matrices reached analysis, but the analyzer stopped at the frozen
anchor gate before computing population summaries or oracle value. `safe_balanced` differs from
direct D40 in at least one task. The first reported mismatch is seed 9,801,000, seat 0,
`script_boss`.

The repeated pre-amendment matrices have SHA-256
`2c228beeae675462bfb89d3ae8f18a8c151f7a52beff12d68e50f97521bb35a1` and are quarantined. Their
score, margin, population, oracle, opponent, workforce, crop, and policy-selection fields may not
be summarized or used.

## Cause

The frozen text simultaneously required:

1. `safe_balanced` to reproduce direct D40 exactly; and
2. every option-layer Rate decision to skip a D40-ranked `FELL_BANK` on the last live own crop.

D40 can itself rank such a fell first. The implementation therefore changed the balanced anchor
while correctly applying the renewable filter. Both requirements cannot hold for that state; this
is an anchor-definition contradiction, not a policy-value result.

## Sole repair

Treat `safe_balanced` as the exact no-option anchor it was intended to be:

- `d40_control` and `safe_balanced` both execute `teacher_index` directly at every decision;
- `safe_balanced` retains option-boundary telemetry but does not apply renewable candidate
  filtering;
- `safe_harvest`, `safe_renew`, `safe_fell`, and all 64 linear policies retain the original
  establishment lock and last-own-crop fell filter unchanged; and
- feature schema, population weights, random seed, semantic modes, maps, opponents, threads,
  telemetry, gates, and decision rules remain unchanged.

This makes anchor equality well-defined without changing any learned-function-class probe. The
balanced anchor remains crop-safe empirically only if direct D40 creates a crop in every task, as
already required by the all-policy crop gate.

## Recovery rule

Add a focused test that exercises an exact direct/safe-balanced episode. Produce two new corrected
matrices under distinct filenames, require byte identity, and rerun the original analyzer with
this amendment pinned. If anchor parity still fails, stop again; do not weaken parity fields.

No field from the quarantined matrices can satisfy a gate, and no platform action is authorized.
