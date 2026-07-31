# S3 putibuzu-shaped rollout-plus-beam scope protocol — 2026-07-31

## Question

Does putibuzu's public contest-final search description identify a materially distinct
search architecture outside the project's closed rollout, residual, and overlay families?
If it does, is the description and current runtime/model substrate sufficient to authorize
a separate feasibility experiment?

This is a written-evidence scope audit. It does not measure the public bot, reproduce it,
or establish that its search caused rank #2.

## Frozen public shape

The primary source is putibuzu's 2026-05-25 post in the CodinGame Troll Farm
feedback/strategies thread:

`https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/5`

The post describes:

- about 30 joint candidate combinations from each troll's top-three tree targets plus
  local actions;
- one greedy policy used for action generation and for both-side continuations;
- candidate evaluation at turns 3, 5, 7, 9, and 12, averaged;
- a three-ply beam on large maps, summarized as `5→3→all`;
- explicit opponent candidates and maximin payoff selection on small maps;
- a composite evaluation using score differential, distance-discounted carried
  resources, ownership/proximity of trees, and future production;
- a distinct opponent training order inside the otherwise shared greedy continuation.

Treat this as an architectural shape, not exact source. The post does not freeze weights,
tie-breaking, candidate deduplication, precise beam semantics, simulator chance handling,
or the map-size boundary.

## Canonical comparison set

Only these named sources may support the adjudication:

1. Phases 3–8: terminal turn-one option rollout, live rejection, robust 29-option
   follow-up, and opponent-model calibration.
2. Phase 11: two complete macro continuations from one shared turn-three state.
3. Phase 16: resident-backed one-MOVE residual with 4-turn screening, four finalists,
   16-turn continuation, and two fixed ambiguity models.
4. The GoldElite residual-search iteration: the nearest two-stage bounded search
   ancestor, including its raw-engine and integrated timing evidence.
5. D36: repeated resident-anchored joint bundle overlays at completion boundaries.
6. D82–D84: threatened-own-crop semantic arms and truncated 1/2/4/8/16/32-decision
   counterfactuals.
7. S1: exact last-N-turn branching and cloneability scope audit.
8. H5's public-source synthesis and the primary forum post above.

No frozen ledger outside the named archive documents may be loaded.

## Required comparison axes

For every family record:

- root timing and activation scope;
- candidate/action grammar and jointness;
- whether direct work can change;
- rollout/decision horizon and terminal measure;
- continuation and opponent treatment;
- sequence selection rule, including beam/maximin use;
- exact-resident versus substitute-policy ownership;
- observed value, latency, transfer result, and binding closure;
- strict-subset, overlap-only, or distinct relation to the public S3 shape.

## Frozen verdicts

- `DUPLICATE_CLOSED`: every claimed distinguishing component is a strict subset of,
  or equivalent to, a closed tested family.
- `DISTINCT_FEASIBILITY_READY`: the combination is materially distinct, sufficiently
  specified, has a defensible opponent/value model, and has evidence of a plausible
  route to the 50 ms warm-turn budget.
- `DISTINCT_SPECIFICATION_GATED`: it is distinct but the public description is too
  underdetermined to define a reproducible intervention.
- `DISTINCT_MODEL_GATED`: it is distinct but no defensible continuation/opponent/value
  model supports a prospective comparison.
- `DISTINCT_RUNTIME_GATED`: it is distinct but current measured lower bounds or exact
  integrated timings rule out the proposed breadth under the 50 ms contract.
- `DISTINCT_MULTI_GATED`: it is distinct and at least two of specification, model, and
  runtime remain binding.
- `UNIDENTIFIABLE`: the named evidence cannot distinguish overlap from novelty.

A gate may be reported as provisional when current evidence is only a nearest-neighbour
measurement. Do not convert a provisional gate into an impossibility claim.

## Acceptance and stop rules

- Produce a complete comparison matrix with exact citations and numbers.
- Separate "this project tested a subset" from "the public combination was tested."
- Separate raw simulator throughput from integrated continuation cost.
- Do not infer putibuzu latency, causal value, or exact implementation from rank.
- A successor may be named only as a peer-review-gated scope item with a blocker-specific
  preflight. This audit itself authorizes no source edit, simulator, map, seed, panel,
  candidate, packaging, submission, or Arena action.
- Stop after compact JSON/report/manifest, canonical closeout, and peer handoff.

## Integrity locks

- Exact resident control:
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
- Sacred library-visible source:
  `rust/src/bin/yamo_orchard_live.rs`,
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- No Arena action.
