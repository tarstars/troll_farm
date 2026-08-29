# Orchard independent reproduction — 2026-08-28

Verdict: **REPRODUCED**.

Scope: the orchard re-charter of `20260828-third-troll-verify`, pinned by the coordinator at
`4ccb6f00a1d10c1ddead0bcfdc87d0b87f0daac5`. I ran each allowed command once. I did not rerun
three heroes or the retired third-troll variant, and I made no Arena mutation.

## Build

`python3 local_claude_1/third-troll/make_orchard.py` reproduced:

- arm SHA-256: `e6dd87cce442047d7a6a2915d7b2f475b9dc0341eb7b9f2e07d6b88e42bf2102`
- compacted submission SHA-256: `8e0c0244a05abd3f6792aacca6ecabd38fcc522ad4a1761f863cc5feb96cd528`
- compacted size: 69,477 bytes
- readable diff: +313 / -32
- round trip: exact

The generated tracked files and result files remained byte-clean.

## Differential bed

The exact absolute-path command from the card reproduced:

- plays: 34/34
- differs from champion: 11/34
- deterministic: 34/34
- compacted equals arm: 34/34
- telemetry errors: 0
- arm trained: 2/34; champion trained: 1/34
- third troll cases: `OSC-010`
- wrong specification: none
- more than three trolls: none

## Smoke

The 24-map smoke reproduced:

- mechanics: PASS 24/24
- a third troll: 21/24
- median third-troll turn: 119
- median funding time: 103 turns
- no third troll: 3 x `bill never paid by turn 200`
- stalled: none
- arm minus resident own score: +1193 over all 24; +1298 on the 21 third-troll maps

## Readable-diff review

Nothing in `readable/diffs/orchard.diff` can plant on a door of our shack or on either shack,
let an own troll chop an orchard tree while the third troll is wanted, plant before the second
troll is trained, or let a troll chop while the bill is being collected: the orchard-cell filter
excludes both shacks and every own-shack door, orchard protection removes its live lemon/plum
trees from chop candidates, planting requires at least two own trolls, and the two-troll funding
phase exposes only fruit-and-iron collection candidates with its chop fallback disabled.
