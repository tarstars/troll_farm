# TestSession common-seed A/A capability — result (2026-07-19)

## Verdict

**Pass: deterministic common-seed pairing is available.**  Both controlled games used exact
resident source SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`,
delineate agent `6479768`, player 0, and `seed=-5687447269333978810`.

The games were `896299140` and `896299148`.  Every frozen condition passed:

| Gate | Result |
|---|---|
| complete, two scores, zero diagnostics | pass |
| exact `refereeInput` echo | pass |
| A1/A2 normalized turn-one input identical | pass |
| both match historical replay `896298158` | pass |
| scores | both 340-391 |
| final wood | both 84-91 |
| inventories, turns, workforce histories | byte/value identical |
| player-0 stdout | 300/300 frames identical |
| delineate stdout | 300/300 frames identical |

Both turn-one streams are 528 bytes with SHA-256
`e14d31e1cdb361ccfe50667ff2fb533d73af79c1ba78a079fffbd329262d0240`.  The two player-0
stdout digests are both `d02aa78a5c684bc0c4ffcea1479e35fabb8c278ee901fe1f1b4014e9a8589302`;
the two opponent digests are both
`293d00b072277d1200651a49c41082a4b687b3c9434c6eacbf1362cf6ebcbe19`.

## Consequence

Random-map baseline/candidate rows are no longer the preferred field gate.  A frozen seed and
fixed opponent produce a deterministic block, so one resident reference can be compared exactly
with each future candidate on the same map, side, and opponent behavior.  This removes map and
opponent-trajectory nuisance variance rather than trying to average it away.

The next experiment validates a prospective five-opponent seed bank with A/A resident repeats.
If all blocks are deterministic, future architecture screens need only five candidate platform
games against stored resident references, followed by a larger confirmation bank only after a
prospective pass.

Artifacts:

- `testsession-common-seed-aa-protocol-2026-07-19.md`;
- `data/panels/testsession-common-seed-aa-20260719.json`;
- `testsession-common-seed-aa-result-2026-07-19.json`.
