# N7 dead-accretion removal plan protocol — 2026-07-31

## Question

Can the four source accretions known to be unreachable from the exact live construction
chain—`ScarceIntent`, banana factory, task market, and opponent-crop scoring—be removed
safely, and from which artifact, without violating the sacred source lock or breaking
compile/test consumers?

This is a read-only inventory and removal plan. It does not edit, reformat, delete,
generate, compile, package, submit, or benchmark source.

## Binding artifacts

1. Sacred development/library source
   `rust/src/bin/yamo_orchard_live.rs`, SHA-256
   `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
2. Current live submission source
   `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`,
   SHA-256
   `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
3. The exact `main()` construction chain, library exposure, runner/test imports, and
   submission-default pointer.
4. H13's accepted dead-accretion finding and source/hash constraints.

## Required checks

- Prove each family is disabled from the exact `main()` construction chain; do not infer
  liveness from a constructor merely existing.
- Search only the named worktree roots and exact identifiers. Separate definitions,
  internal references, external compile/test callers, and historical text.
- Determine whether the current live deploy artifact already excludes each family.
- Measure source bytes/lines and a static deletion ceiling without editing either source.
- Identify every hash/API/fixture consequence of touching the sacred source.
- Produce a staged disposition per artifact: keep, derive, archive, deprecate, or
  separately authorize regeneration.

## Frozen verdicts

- `DEPLOYMENT_ALREADY_SLIM`: the current deploy artifact already excludes the four
  families; no live size/performance action exists and the sacred source must remain.
- `PLAN_READY_LOCKED`: removal has a concrete safe target and ordering, but execution is
  separately gated by source/hash/API migration.
- `NOT_DEAD`: at least one family is reachable from the live construction chain.
- `SCOPE_SPLITS`: families have materially different liveness/consumer states and require
  separate tasks.
- `UNIDENTIFIABLE`: named sources/references cannot establish the disposition.

## Acceptance and stop rules

- Produce a per-family liveness/consumer matrix, artifact comparison, deletion ceiling,
  and one verdict.
- “Dead from main” does not mean safe to delete if tests or experiment constructors call
  the family.
- Do not use compile success as permission to change a hash-locked research fixture.
- If the deploy artifact is already slim, close N7 without a cleanup patch.
- Stop after compact JSON/report/manifest, canonical closeout, and peer handoff.
- No source edit, formatter, deletion, generation, compile, test, game, map/range,
  package, candidate, submission, or Arena action.

## Integrity locks

- Keep `rust/src/bin/yamo_orchard_live.rs` byte-exact at
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- Keep the current submission and `cgauto/api_submit.py` default unchanged.
- No Arena action.
