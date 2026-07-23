# D99a pair-aware batch-action implementation lock

Date: 2026-07-21  
Status: locked before any D99 policy reached terminal state on the frozen outcome maps

The D99 evaluator and its narrow same-turn pair-preview environment extension are frozen after
compilation and three pre-outcome tests:

- all 342 feature slots are finite and the exact segment/interaction layout matches the protocol;
- a previewed first assignment matches the real environment's turn, state hash, next worker,
  observation, and D42 shared context; and
- the zero policy reproduces exact D40 terminal and action-plane behavior on an old non-D99 seed.

The preview API cannot advance a game turn or call the temporary opponent controller: it returns
`None` unless another worker remains, then asserts that the assignment leaves the turn unchanged
and exposes a worker decision. The evaluator additionally validates every committed second state,
worker, observation, reconstructed catalog, and action against its preview at runtime.

Reproducibility anchors:

- outcome-blind population lock SHA-256:
  `78a8048673df9b5c2944452f310757e929a5d1701f1a90835c936121dc3aa58f`;
- evaluator SHA-256 after `rustfmt`:
  `bcb3f340150e8639f862380d8b0492e90683cfef8b7dd1074ac5811a1128d3a1`;
- pair-preview environment SHA-256 after `rustfmt`:
  `1e3af47fe25184790763a7dbf11818944c583794303bb986f1db28708179a2e5`;
- exact-prior kernel SHA-256:
  `632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`.

The implementation is now immutable for D99. A mechanics or integrity defect may be repaired only
under the unchanged protocol, population, reference binary, and outcome maps, with the repair
explicitly logged before repeating all affected rows.
