# Legend top-five common-seed bank v1 — A/A result (2026-07-19)

## Verdict

**The five-block exact-determinism gate fails.**  Seed control fixes the map in 5/5 blocks, but
fixed top-agent code is not universally trajectory-deterministic.  Keep three independently exact
blocks for diagnostic use; treat the other two as map-blocked stochastic observations.  Do not
call the full bank exactly paired.

All infrastructure integrity checks pass: ten unique completed games, exact bank hash
`47f4bb7e2c993623bb19bd9e58603a07898df9f7f7429d08686980dd4d890dc6`, identical exact-resident
sources, exact options echoes, and zero diagnostics.

## Per-opponent result

| Opponent | Map identical | Scores A1 / A2 | Our stdout | Opponent stdout | Frozen block gate |
|---|:---:|---:|:---:|:---:|:---:|
| delineate | yes | 148-92 / 148-92 | exact | exact | pass |
| wala | yes | 107-258 / 107-258 | exact | 2 movement frames differ | fail |
| norxondor | yes | 124-232 / 117-315 | diverges from turn 50 | behavioral divergence from turn 22 | fail |
| Escdemon | yes | 225-249 / 225-249 | exact | exact | pass |
| laconic | yes | 165-193 / 165-193 | exact | exact | pass |

Wala's two differing commands occur at turns 54--55 and reconverge without changing our complete
command stream, inventories, workforce, or result.  This is still a formal failure because the
protocol required complete opponent stdout identity.

Norxondor prints runtime telemetry every turn and its timing strings differ immediately, but the
difference is not cosmetic.  Excluding `MSG`, its actions first diverge at turn 22 and differ on
272/300 turns.  The shared state then changes our resident's first choice at turn 50 and 243/300
of our command frames differ.  The opponent scores differ by 83 points.  A fixed map therefore
does not provide common opponent randomness for this agent.

## What remains valid

1. `gameOptions` controls map and initial state exactly for every tested opponent.
2. Delineate, Escdemon, and laconic provide exact deterministic blocks on the frozen seeds.
3. Wala is map-controlled with small observed policy randomness; its identical A/A outcome is
   descriptive, not proof of deterministic pairing.
4. Norxondor requires replicated map-blocked samples or explicit uncertainty.  One A/B result
   cannot be interpreted as a candidate effect.

The evaluation architecture is therefore layered:

- exact within-block deltas on independently deterministic opponents;
- map-blocked, interleaved comparisons with uncertainty on stochastic opponents;
- a separately frozen confirmation bank after a candidate is frozen; and
- arena promotion only after field safety, never from a five-map development score alone.

## Reference-game architecture signal

The first A row of each block also confirms the strategic residual without relying on local
models.  Resident beats compact delineate by 56, narrowly loses to two-worker Escdemon and
laconic by 24 and 28, and loses to worker-rich wala by 151.  In the first norxondor realization it
loses by 108.  The resident remains two-worker throughout; wala reaches four.  Norxondor and
laconic score substantial fruit as well as wood, while some resident games finish with essentially
wood-only score.  The next candidate must change complete score flow or role allocation, not just
add an isolated TRAIN or target bonus.

Artifacts:

- `legend-top5-common-seed-bank-aa-protocol-2026-07-19.md`;
- `legend-top5-common-seed-bank-v1.json`;
- `data/panels/legend-top5-common-seed-bank-v1-aa-20260719.json`;
- `legend-top5-common-seed-bank-aa-result-2026-07-19.json`.
