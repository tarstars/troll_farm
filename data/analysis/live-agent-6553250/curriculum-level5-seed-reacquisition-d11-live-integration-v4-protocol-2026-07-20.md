# Curriculum Level 5 D11 live integration V4 protocol — frozen 2026-07-20

## Hypothesis and sole change

The curriculum persistently retains a tracked crop coordinate after own removal; V3 retained it for
only one transition.  A persistent provenance bit derived from the already witnessed own CHOP
should reproduce that update order without new information or policy changes.

Starting from V3 source SHA-256
`40a163cb3c7f97a9618d73bb41f61511382875c37d1ab849a5aa073d40cd1c4a`, generate exactly one V4
source that:

1. adds one `own_removed_crop` Boolean, initially false;
2. sets it true when a pending own CHOP on the tracked coordinate is followed by that crop being
   absent;
3. while true and the tracked crop remains absent, retains the coordinate without requiring a new
   CHOP witness;
4. resets it false whenever the tracked crop exists, or whenever a successful pending own BANANA
   plant assigns `created_crop`; and
5. otherwise preserves V3's missing-crop clear and all V2 pending-harvest semantics.

No other source, tracker field, parser, observation, mask, action, weight, recipe, compiler flag, or
threshold may change.

## Frozen gates

1. Reproducible diagnostic-free `rustc --edition=2021 -O` source strictly below 100,000 bytes.
2. One exact interactive audit on disjoint D11 bank `[7700300,7700364)`: every observation/mask
   hash, phase, legal action, and command must match; all processes/stderr must be clean; aggregate
   training, crop, renewable-harvest, and opponent-destruction mechanisms must activate.
3. Every first response <=1,000 ms; all warm responses p95/max <=45/50 ms.
4. Only a full pass opens the unchanged 16-map x both-seat x 300-turn production safety screen with
   32/32 clean processes, exactly 300 lines, complete own-worker commands, and valid TRAIN syntax.

Failure closes V4 and its bank.  Success qualifies only fixed-recipe integration and opens a
separate autonomous recipe experiment; Arena remains unauthorized.

## Anchors

- V3 result SHA-256 is to be recorded before generation;
- V3 protocol SHA-256:
  `dfb95a39bc2f2c4b6e3cf245940c53f718ffaf8ee33e4d6089ac31b3c5731f80`;
- K2 qualification SHA-256:
  `d561307f3bd684e0f7bcc1d61adaf1667f38b3beb57301cfffcc0acbc09298fd`;
- payload SHA-256:
  `eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`.

