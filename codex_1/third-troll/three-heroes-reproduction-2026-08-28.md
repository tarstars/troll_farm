# Three-heroes independent reproduction — 2026-08-28

Verdict: **REPRODUCED**.

Scope: the re-chartered `20260828-third-troll-verify` card, at `main` commit
`9d70455300b12972a3fd5acc3dd0373eed1a1143` or later. I ran each allowed command once.
The retired third-troll (a) was not rerun, and I made no Arena mutation.

## Build

`python3 local_claude_1/third-troll/make_three_heroes.py` reproduced:

- arm SHA-256: `14b2f3906cfd6c2a8001e40659b9562153a618b46b99f2f59851a85389e85e50`
- compacted submission SHA-256: `2abb9fc29c574f330ebf94ddcea3ec4f1968f0961299946777744c831f919f69`
- readable source SHA-256: `be34b3fdcb95f8b1a5ad2bd52baa17258d6cacb9d41651e1bf33cfc569b3ea0f`
- compacted size: 65,508 bytes
- readable diff: +128 / -31
- round trip: exact

After removing the exact untracked scratch output named by the card
(`local_claude_1/third-troll/results/build-v6.json`), tracked generated files were clean.

## Differential bed

The exact absolute-path command from the card reproduced:

- plays: 34/34
- differs from champion: 6/34
- deterministic: 34/34
- compacted equals arm: 34/34
- telemetry errors: 0
- arm trained: 1/34; champion trained: 1/34
- third troll cases: `OSC-010`
- wrong specification: none
- more than three trolls: none

## Smoke

The 24-map smoke reproduced:

- mechanics: PASS 24/24
- a third troll: 20/24
- median third-troll turn: 111
- median funding time: 106 turns
- no third troll: 4 × `bill never paid by turn 200`
- stalled: none
- arm minus resident own score: -1 over all 24; +127 on the 20 third-troll maps

## Readable-diff review

Nothing in `readable/diffs/three-heroes.diff` lets an own troll chop while a reachable
third-troll bill is being collected, train a fourth troll, or keep collecting after a
still-missing fruit has no reachable living tree: funding gives every troll only the
early fruit/iron list, its chop fallback is disabled once two trolls exist, the roster cap
is three, and the reachability guard drops funding as soon as any missing fruit has no
candidate tree.
