# Legend top-five common-seed bank v1 — A/A protocol (frozen 2026-07-19)

## Purpose

Validate a prospective deterministic field block for candidate screening.  The bank was generated
before any of its games: for each opponent, interpret the first eight bytes of
`SHA-256("legend-top3-field-bank-v1|" + opponent)` as a signed big-endian int64.

The exact blocks are frozen in `legend-top5-common-seed-bank-v1.json`.  No seed may be replaced
after seeing a map or outcome.  This is measurement validation, not policy qualification.

## Execution

- exact resident source in both A columns, SHA-256
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- five fixed Legend snapshots: delineate, wala, norxondor, Escdemon, laconic;
- one unique frozen seed per opponent;
- A1 then A2 for each block, resident always player 0;
- ten total `TestSession/play` calls, one-second throttle, zero arena writes;
- stop immediately after any transport, compilation, runtime, degenerate-score, or seed-echo
  failure.

## Frozen gates

For all five blocks:

1. both games complete with two scores and zero player-0 diagnostics;
2. both responses echo the block's requested `seed=<value>\n` exactly;
3. normalized player-0 turn-one inputs are byte-identical within block;
4. scores, final inventories, turn counts, workforce histories, and both agents' complete stdout
   streams are identical within block.

All five blocks must pass.  Partial success does not authorize a top-five paired claim.

## Consequence

On pass, freeze the first A row of each block as the resident reference.  Future discovery
candidates receive exactly one game per bank block.  Evaluate within-block own-score, opponent-
score, margin, wood, workforce, and mechanism deltas.  A candidate that was altered after seeing
bank outcomes cannot claim prospective discovery evidence; confirmation must use a separately
frozen bank.

On failure, retain only the opponent blocks that independently prove deterministic for diagnostic
use, and design a replacement prospective bank before candidate generation.
