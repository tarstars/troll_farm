# L1 delineate-cloning readiness audit protocol — 2026-07-31

## Question

Is the register's L1 proposal—behaviour cloning from rank-one `delineate`
specifically—a scientifically distinct and currently executable learning experiment,
given the expanded replay corpus and the project's prior imitation closures?

This is a read-only substrate and scope audit. It does not export a dataset, fit a
model, alter source, run a game, or authorize a candidate.

## Binding comparison set

1. The current 9,082-game parsed corpus and exact `delineate` replay subset, identified
   by agent ID rather than pseudonym.
2. Phase 9's pooled and per-agent objective imitation, including the old delineate row.
3. Phase 14's compact Norxondor reconstruction and closed-loop covariate-shift result.
4. D41a's D40 behavior-cloning closure and the current imitation constraints.
5. Delineate's public postmortem, including its observation, sequential action, train
   plan, joint-action beam, parameter-count, and runtime descriptions.
6. The L1 register row and current goal/byte/runtime constraints.

No frozen ledger outside the named entries may be loaded.

## Required checks

- Verify exact-agent identity, replay count, seat/opponent coverage, turn count, and
  observable command-label volume in the current parsed corpus.
- Compare current coverage with the 26-game / 17,743-unit-turn delineate slice used by
  Phase 9.
- Separate labels exposed by replays from latent internal variables: primitive spatial
  logits, train-plan choice before TRAIN, per-unit inference order, and joint beam
  alternatives/probabilities.
- Determine whether a deterministic, outcome-blind state/action extractor can be built
  from existing official replays without new play or inferred task labels.
- Classify prior closures by teacher, target, representation, corpus size, and
  validation mode; observational accuracy alone must never override the Phase-14
  closed-loop warning.
- Specify the smallest defensible successor only if the substrate and target are
  materially distinct.

## Frozen verdicts

- `DISTINCT_CORPUS_READY`: a materially expanded, stable exact-agent corpus exposes a
  complete observable cloning target, and prior experiments do not duplicate it.
- `DISTINCT_PRIMITIVE_ONLY`: the expanded corpus supports exact primitive-command
  imitation, but latent plan/joint-action targets are not recoverable; any successor
  must narrow its claim and retain a separate closed-loop value gate.
- `DUPLICATE_AUTOREGRESSIVE_CLOSED`: the proposed target and validation path are already
  covered by a prior teacher-state imitation closure, with no material new discriminator.
- `SUBSTRATE_INSUFFICIENT`: exact-agent coverage or replay materialization is too small,
  mixed-version, or incomplete for the proposed audit.
- `UNIDENTIFIABLE`: the named evidence cannot resolve readiness.

## Acceptance and stop rules

- Produce a prior-work matrix, corpus/label inventory, identifiability boundary, and one
  verdict with exact hashes and paths.
- Corpus scale is a new discriminator only if it expands the same exact agent and
  observable target; it cannot by itself establish policy value.
- A successor may begin only with a deterministic extractor/parity audit on consumed
  replays. Held-game and temporal-block action metrics are diagnostic. Advancement still
  requires frozen closed-loop official-map score/margin and family-transfer gates before
  source integration.
- Stop after compact JSON/report/manifest, canonical closeout, and peer handoff.
- No extractor implementation, bulk write, model, fit, GPU/YT job, TestSession, map or
  range opening, candidate, source change, submission, or Arena action.

## Integrity locks

- Current parsed corpus hash and named prior-result hashes must be recorded.
- Sacred source:
  `rust/src/bin/yamo_orchard_live.rs`,
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- No Arena action.
