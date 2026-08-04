# 20260802-banana-restoration-r2: restore intended banana logic on the best stable bot

- Status: implementation in progress — invariant/seam review returned with required corrections
- Record owner / integrator: `local_codex_1`
- Work owner: `claude_1`
- Reviewer / host replay gate: `local_codex_1`
- Area: owner-directed banana restoration retry after implementation-invalid publications
- Base commit: `b6f9a7825a17afbbd91949d31d5957b330f6adf0`
- Branch: `agent/claude_1-banana-restoration-r2`
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-02T17:45:26Z
- Last updated UTC: 2026-08-04T17:48:49Z

## Outcome

Produce a minimal, inspectable restoration of the intended banana lifecycle on the exact strongest
repeated stable parent, without inheriting the implementation injuries in the ChatGPT-authored
unbounded factory or bounded-ring lineage. Return `IMPLEMENTATION_VALID`, `IMPLEMENTATION_INVALID`,
or a precise blocker. Value testing starts only after `IMPLEMENTATION_VALID`.

Parent:
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes,
SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

## Scientific correction

The live outcomes of `6590083` / `41081195` and `6590136` / `41081465` are classified as
**implementation-invalid banana trials**, not tests rejecting banana production. The first used an
unbounded farm and failed the owner's lifecycle/collection/geometry contract. The second showed
repeated period-2 movement in exact live replays, including worker 2 alternating `(10,4)<->(11,4)`
on turns 20--29 and `(8,2)<->(8,3)` on turns 269--280 of game `897829265`. Focused smoke and a
small equality panel did not protect against those failures.

## Intended behavior to restore

- early planted bananas form a self-reproducing orchard;
- late ripe fruit is converted into wood;
- harvested fruit is collected/banked when the resident owns the resource;
- do not create fruit the opponent can harvest before us;
- use gate-aware, bounded placement rather than an unbounded field;
- preserve second-worker funding before denial work;
- a worker that commits to bank carried wood continues to the tent until `DROP` or loss of cargo;
- workers never chase each other's occupied tree/cell;
- target selection has commitment/hysteresis sufficient to prevent `A->B->A` loops.

Claude must first restate any ambiguity in this contract as explicit invariants. Do not silently
copy the previous wrapper as the specification.

## Exclusive write set

- `claude_1/banana-restoration-r2/**`
- `coordination/status/claude_1.md`
- `coordination/messages/claude_1/*20260802-banana-restoration-r2*`

Use task-private source/build/test artifacts. The integrator will materialize any accepted final
candidate under shared submission paths after review.

## Shared read-only inputs

- the exact parent source above;
- `origin/agent/chatgpt_1-banana-factory-restoration` for intent/history only;
- commit `2ee6941412b6b3c70db0136c4375dea89cc92816` on
  `origin/agent/local_codex_1`, containing the bounded-ring implementation and gates;
- `coordination/tasks/20260802-banana-ring-b100-successor.md`;
- exact live counterexample game IDs supplied in this record; local provides host replay execution
  after Claude publishes a deterministic probe/validator.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (must remain byte-exact SHA prefix `fff6669b`);
- `cgauto/submissions/`, `cgauto/api_submit.py`, shared docs, task records, or another agent's
  namespace;
- `data/raw/games/`, the 05:17 cron, sealed maps, official holdout, or H3a artifacts;
- Arena/TestSession mutation.

## Acceptance checks

1. Verify the parent SHA, unique transform seam, and byte-exact inverse transform.
2. Keep an independently readable research source; derive any compact source mechanically.
3. Prove research/compact command equality on a broad open panel and on every supplied banana-live
   replay, not only eight inherited streams; any mismatch is terminal.
4. Outside the declared banana activation states, commands equal the stable parent exactly.
5. Add deterministic detectors for repeated `A->B->A`, repeated PICK/DROP, same-target/occupied-cell
   contention, abandoned carried-wood return, unbounded planting, opponent-favored fruit creation,
   lost harvested fruit, diagonal-mother chop, and second-worker TRAIN displacement.
6. Game `897829265` must have zero multi-turn period-2 episodes attributable to the candidate and
   must make task progress through both cited windows. Local will run this host-only gate.
7. Semantic tests cover bootstrap, renewable harvest/replant, bounded placement, late conversion,
   banking, enemy ETA suppression, two-worker arbitration, and destroyed/occupied target recovery.
8. Standalone optimized compile, empty-input exit, zero stderr, source below 100,000 bytes, sacred
   source exact, and runtime below the established fast gate.
9. Report telemetry separately from value. No local smoke score or live banana score may qualify
   the algorithm until all implementation gates pass.

## Arena authority

Read-only platform access: not required for Claude; local owns exact replay fetching and execution.
Platform mutation: forbidden. An `IMPLEMENTATION_VALID` handoff is not publication authorization.

## Handoff

Push the exact source(s), generator/transform, tests, manifest, hashes, deterministic host-run
command, and a report that maps every intended invariant to evidence. Send an ACK first, then a
progress message at the first reproducible result. `local_codex_1` performs counterexample replay
and independent review before any value protocol is proposed.

## Integrator review checkpoint — 2026-08-04

Claude published 29 invariants, nine trace detectors, an instrument layer, and an insert-only
wrapper seam. The bounded ring, conservative ETA rule, exclusive apple/banana activation, and
initial hysteresis constants are directionally accepted. The seam is not yet approved because it
selects a non-starter although the contract assigns the starter as resident, cannot decide apple
eligibility before the first inner call initializes orchard state, and lacks the protected-mother
set claimed by I-29. Mother counting, designated-harvester ownership, the dynamic lifetime-safety
response, single-door serialization, and the non-proof wording of the hysteresis claim also need
correction. Exact review message:
`coordination/messages/local_codex_1/20260804T194501Z-20260802-banana-restoration-r2-ack.md`.
