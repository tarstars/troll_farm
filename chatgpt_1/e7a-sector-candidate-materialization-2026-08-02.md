# E7a sector-conditioned `typeToCut` candidate materialization

- Task: `20260802-e7a-sector-candidate`
- Owner: user
- Work owner: `chatgpt_1`
- Parent: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
- Parent SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- Candidate path:
  `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- Branch: `agent/chatgpt_1-e7a-sector-candidate`

## Purpose

Materialize the strongest established resident with the frozen exploratory E7a sign-sector
rule. This is candidate construction and semantic validation, not a new selector fit and not
a value qualification.

## Frozen rule

The existing parent computes, once at initialization, the sum of BFS distances from the
resident shack's walkable orthogonal doors to all initial LEMON trees and all initial PLUM
trees. It chooses the lower-distance species, with LEMON winning ties.

The candidate changes that binary return only when:

```text
lemon_distance_sum <= plum_distance_sum
AND
plum_distance_sum - lemon_distance_sum <= 8
```

In that case it returns PLUM. In every other initial state it returns the exact parent
choice. The threshold, species, comparison direction, distance definition, unreachable-cell
penalty (`10_000`), doors, BFS, and one-time persistence are frozen from the published
analysis and source.

## Transformation contract

The builder must:

1. verify the complete parent SHA-256;
2. find exactly one complete `MoisanBot::focus_type` anchor;
3. replace only that anchor;
4. prove one-step inverse replacement recreates the parent bytes;
5. emit a candidate whose source difference is confined to the one declared function;
6. preserve the sacred development source and every existing submission artifact.

No announcement, score, scheduler, candidate grammar, opening, orchard, banking, movement,
training, denial weight, ETA, or endgame behavior changes.

## Validation gates

### G1 — static provenance

- parent hash exact;
- old anchor count exactly one;
- candidate anchor count exactly one;
- inverse equality exact;
- candidate SHA and byte count recorded.

### G2 — frozen sector reproduction

Using `chatgpt_1/e7a-initial-sector-sign-preflight-2026-08-02.csv`:

- 60 unique roots;
- exactly 13 roots selected by the frozen rule;
- exactly 10 selected roots have positive original E7 FLIP sign;
- exactly 3 selected roots have non-positive sign;
- precision `10/13` is descriptive only.

### G3 — standalone compilation

`rustc -O` must compile the generated single-file source without warnings promoted to errors
or source preprocessing.

### G4 — exact two-arm bridge

On a deterministic representative replay set containing sector and non-sector roots, both
seats, and an immutable local opponent:

- inside sector, candidate policy command-stream hash, opponent stream, terminal state,
  score/margin, command counts, and runtime integrity equal the original E7 full-FLIP arm;
- outside sector, the same fields equal unchanged control;
- no malformed command, stderr, or runtime signal;
- any mismatch is terminal and candidate publication fails closed.

This is semantic materialization evidence, not terminal value evidence. Replays are used only
to prove the candidate is exactly one of the two previously defined arms on each initial
state.

## Disposition vocabulary

- `MATERIALIZED_EXACT_BRIDGE`: all gates pass; technically ready for the controller to inspect.
- `BLOCKED_PARENT_OR_ANCHOR`: provenance/transform failure.
- `BLOCKED_COMPILE`: standalone compilation failure.
- `BLOCKED_SECTOR_REPRODUCTION`: the frozen 13/60, 10/13 census does not reproduce.
- `BLOCKED_BRIDGE`: candidate is not exactly control or FLIP as required.

Even `MATERIALIZED_EXACT_BRIDGE` remains **unqualified for Arena value**. The exploratory rule
was selected from consumed E7 labels, the broad ridge model failed, and terminal-margin
magnitudes/generalization have not cleared a fresh three-arm protocol. Only the sole Arena
controller may decide whether the owner's request warrants a later serialized live override.
