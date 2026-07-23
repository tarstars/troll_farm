# Curriculum Level 5 D11 live integration V2 protocol — frozen 2026-07-20

## Hypothesis and sole change

V1's only observed ABI discrepancy is an overcounted renewable harvest when own HARVEST and
opponent destruction affect the same tracked crop in one referee transition.  Remembering the
pending harvest cell and requiring it to equal the post-transition tracked crop should reproduce
the curriculum's update order exactly without changing parsing, observation definitions, legal
masks, actor inference, actions, or ordinary play.

Starting from closed source SHA-256
`61a276360e053fa23abe9a71b611a59eff3de0852bdd23d5ac89205556bce41e`, generate one V2 source with
only these mechanical changes:

1. change every pending-harvest record from `(unit id, prior BANANA carry)` to
   `(unit id, prior BANANA carry, harvest cell)`;
2. retain the existing post-state update order: clear a missing tracked crop, accept any successful
   pending BANANA plant, then inspect pending harvests; and
3. increment renewable-harvest count only if carry increased **and** the current tracked crop equals
   the recorded harvest cell.

No other tracker rule, threshold, recipe, source component, weight, compiler flag, or action rule
may change.  V1's `[7700000,7700064)` bank is closed.

## Frozen gates

1. Generate byte-reproducibly, compile directly with `rustc --edition=2021 -O` without diagnostics,
   and remain strictly below 100,000 UTF-8 bytes.
2. Run exactly one interactive D11 audit on the new disjoint bank `[7700100,7700164)`, selecting
   the frozen per-seed recipe only through the audit interface.  Require exact FNV-1a equality for
   every complete observation and legal mask in every phase, legal actions, exact command decoding,
   exact phase counts, no process/stderr/protocol failure, and aggregate activation of training,
   crop creation, renewable harvest, and opponent crop destruction.
3. Require complete interactive response latency, including parser/observer/one-or-two forwards/
   formatting/IPC, at <=1,000 ms for every first response, <=45 ms p95 after first turns, and <=50
   ms for every warm response.
4. Only that pass opens the unchanged production-mode 300-turn safety screen on 16 generated maps,
   both seats, against a waiting opponent: 32/32 clean processes, 300 command lines each, no stderr,
   one command per own worker per turn, and valid TRAIN syntax.

Any failure closes V2 without rerun or tolerance revision.  A complete pass qualifies the
fixed-recipe integration skeleton but does not select a high-level recipe, create an Arena
candidate, or authorize submission.

## Anchors

- V1 result SHA-256 is to be recorded before V2 generation;
- integration V1 protocol SHA-256:
  `f7d05facb1f5fffd08f484a72ce58b6604d91e165451c2b5e67f0da0fe703fb7`;
- K2 qualification SHA-256:
  `d561307f3bd684e0f7bcc1d61adaf1667f38b3beb57301cfffcc0acbc09298fd`;
- payload SHA-256:
  `eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`;
- release library SHA-256:
  `381ba5623afb13d77fed09a80dbc2fabc0dd483781a56e9f3c65477783a1dab7`.

