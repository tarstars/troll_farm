# Curriculum Level 5 D11 live integration V3 protocol — frozen 2026-07-20

## Hypothesis and sole change

V2's only discrepancy occurs after the learned own chopper removes the tracked crop.  The
curriculum retains that stale coordinate, whereas live V2 classifies every missing crop as an
opponent destruction.  Remembering a witnessed own CHOP on the tracked cell for one transition
should reproduce the reference distinction exactly.

Starting from V2 source SHA-256
`559ebf54de1af5d91ab5f72ec533e0f56bc2ca65463e72fbb0c287a4ee22f981`, generate one V3 source with
only these changes:

1. add a pending-own-chop cell list to controller state;
2. when a selected action is CHOP and its worker currently occupies the tracked crop cell, record
   that cell for the next official state;
3. if the tracked crop is absent on that next state, retain its coordinate exactly when the same
   cell has the pending-own-chop witness; otherwise clear it as V2 does; and
4. consume all pending-own-chop witnesses after this resolution.

The V2 pending-harvest cell guard remains unchanged.  No other tracker, parser, channel, mask,
weight, action, recipe, compiler flag, source component, or threshold may change.

## Frozen gates

1. Generate reproducibly, compile with diagnostic-free `rustc --edition=2021 -O`, and remain
   strictly below 100,000 UTF-8 bytes.
2. Run exactly one interactive audit on the new bank `[7700200,7700264)` under the same exact D11
   environment and per-seed audit recipe.  Require exact observation and mask hashes in every
   phase, legal actions, exact command/phase mapping, clean process/stderr, and aggregate training,
   crop, renewable-harvest, and opponent-destruction activation.
3. Across that audit require every first response <=1,000 ms and warm complete-response p95/max
   <=45/50 ms.
4. Only a complete pass opens the unchanged 16-map, both-seat, waiting-opponent 300-turn production
   process screen and its 32/32 clean-process, 300-line, command-count, legality, and TRAIN-syntax
   checks.

Any failure closes V3 and its bank.  A pass qualifies only fixed-recipe live integration and opens
autonomous recipe selection plus layered field qualification; it is not Arena authorization.

## Anchors

- V2 result SHA-256 is to be recorded before generation;
- V2 protocol SHA-256:
  `c881c2d0f2a4ed66ec04162d8e0c90d9f822f8f7afef9c29a2ffc403754fb582`;
- K2 qualification SHA-256:
  `d561307f3bd684e0f7bcc1d61adaf1667f38b3beb57301cfffcc0acbc09298fd`;
- payload SHA-256:
  `eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`.

