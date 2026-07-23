# Curriculum Level 5 D11 live integration V5 protocol — frozen 2026-07-20

## Hypothesis and sole change

V4 proves exact live semantics across 21,695 decisions and fails only one 64.275 ms response.  It
allocates observation, mask, and logit vectors once per worker phase.  Persisting these fixed-size
buffers should remove allocator tail exposure and pass the unchanged 50 ms maximum without any
semantic change.

Starting from V4 source SHA-256
`ba93357bfcb6e201ed04a0b9c32e1304f1a64104f83649009fa3551fb2bec581`, generate exactly one V5
source that:

1. adds controller-owned buffers of `OBS_C*AREA` u8, `ACTIONS` u8, and `ACTIONS` f32;
2. allocates them once during controller construction;
3. temporarily takes, fills, uses, and restores those buffers in each worker phase so the existing
   observer and actor borrow rules remain unchanged; and
4. removes the three per-phase vector allocations and no other allocation or operation.

All tracker, parser, observation/mask bytes, K2 operations, action/command output, recipes, compiler
flags, and gates remain fixed.

## Frozen gates

1. Reproducible, diagnostic-free `rustc --edition=2021 -O`, source <100,000 bytes.
2. One exact interactive audit on new D11 bank `[7700400,7700464)`: exact observation/mask hashes,
   legal actions, exact phase/command mapping, clean processes/stderr, and aggregate training/crop/
   renewable/destruction activation.
3. Every first response <=1,000 ms and complete warm response p95/max <=45/50 ms.
4. Only a full pass opens the unchanged production screen: seeds 0--15, both seats, waiting
   opponent, exactly 300 turns, 32/32 clean processes, 300 output lines each, complete own-worker
   command count, valid action syntax, and valid TRAIN syntax.

Failure closes V5 and its bank without rerun.  Success qualifies fixed-recipe live integration and
opens autonomous recipe/first-move selection; it does not authorize Arena submission.

## Anchors

- V4 result and audit SHA-256 values are recorded before V5 generation;
- V4 protocol SHA-256:
  `7cef1c1bc8cc5e19a6271e953d2260695279658ab1c029ff38f1d0cb324363d4`;
- K2 qualification SHA-256:
  `d561307f3bd684e0f7bcc1d61adaf1667f38b3beb57301cfffcc0acbc09298fd`;
- payload SHA-256:
  `eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`.

