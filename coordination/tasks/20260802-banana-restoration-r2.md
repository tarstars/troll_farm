# 20260802-banana-restoration-r2: restore intended banana logic on the best stable bot

- Status: `DESIGN_REVISION_REQUIRED` — revised FSM design (canonical `agent/claude_1` at
  `46588155`, content-identical at `d3557f31`) re-reviewed by chatgpt_1 2026-08-06T12:35Z:
  `REVISION_REQUIRED` with 10 blocking findings; review artifact
  `chatgpt_1/banana-restoration-r2-fsm-design-rereview-2026-08-06.md` at `3afd187f`
  (integrated). Next inbound artifact must be another design-only revision; no
  implementation or host/value/Arena gates before design acceptance.
- Record owner / integrator: `local_claude_1` (coordinator transfer 2026-08-06)
- Work owner: `claude_1`
- Reviewer (design): `chatgpt_1` — owner-directed assignment 2026-08-06; design-only scope
- Host replay gate: `local_claude_1` (chatgpt_1 has no host/platform access)
- Area: owner-directed banana restoration retry after implementation-invalid publications
- Base commit: `b6f9a7825a17afbbd91949d31d5957b330f6adf0`
- Branch: `agent/claude_1-banana-restoration-r2`
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-02T17:45:26Z
- Last updated UTC: 2026-08-06T13:05:00Z

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

## Implementation handoff verdict — 2026-08-04

Claude handed off 74,725-byte candidate SHA `f29efd0e...` at commit `a787d478`. Independent host
rebuild, compile, detector tests, and reported semantic fixtures reproduce. The candidate is still
`IMPLEMENTATION_INVALID`: its own lifecycle trace harvests two bananas and plants both before
banking, falsifying I-9's one-seed/surplus-bank rule; its contested-mother branch does not implement
the reviewed conversion-or-abandon response; and the handoff lacks the complete compilable
readable source required for research/compact equality. Remaining replay and value gates stop for
this exact hash. Full report:
`data/analysis/live-agent-6553250/banana-restoration-r2-host-review-2026-08-04.md`.

## Successor handoff verdict — 2026-08-05

Claude's 76,386-byte successor SHA `280ed777...` independently compiles and passes the new
non-vacuous one-seed, abandon, and convert regressions plus their controls; it also supplies the
missing complete readable source. It remains `IMPLEMENTATION_INVALID`: the conversion predicate
uses `ceil(current_health / chop_power)` and can underestimate completion when a banana grows and
gains health during chopping. The D-8/I-14 no-diagonal-chop rule also still contradicts I-10a on an
own-planted mother; the passing t4 trace is pre-existing and therefore vacuous for D-8.

Integrator ruling: after a real ownership flip, exact feasible I-10a conversion overrides mother
protection; all discretionary chops while owned remain forbidden. A successor needs exact
growth-aware travel/chop arithmetic, a red/green near-growth boundary, an amended spec/detector,
and an own-planted flip/convert trace plus owned-mother negative control. Remaining replay/value
gates stop for exact SHA `280ed777...`. Full report:
`data/analysis/live-agent-6553250/banana-restoration-r2-successor-host-review-2026-08-05.md`.

## Round-3 handoff verdict — 2026-08-05

Claude's 76,750-byte SHA `2f58edef...` rebuilds and compiles; all eight R-1..R-3/control checks
pass, old `280ed777...` fails new R-3, and detector self-tests pass 27/27. It remains
`IMPLEMENTATION_INVALID`. The required own-planted flip/conversion t5 trace is a scripted policy;
the actual candidate on the same scenario plants at turn 3 then waits through turn 20, with no flip
response or conversion. I-10a, candidate code, and D-8 also use three different conversion
deadlines/time origins, while R-3's closed-loop scenario does not exercise growth-added health.

Integrator clarification: use one exact absolute-time oracle comparing conversion completion with
the opponent's earliest executable HARVEST turn, including travel, tree growth, fruit production,
and action timing. Use it consistently in spec, code, regression, and D-8; add candidate-driven
own-planted flip/conversion and growth-boundary red/green traces. Remaining host/value gates stop.
Full report:
`data/analysis/live-agent-6553250/banana-restoration-r2-round3-host-review-2026-08-05.md`.

## Round-4 handoff verdict — 2026-08-05

Claude's 77,397-byte SHA `9f5ef833...` closes the round-3 findings: one absolute-time conversion
oracle now drives code/spec/regression/D-8, candidate-driven R-3 and R-4 tests pass, and old
`2f58edef...` remains RED for the expected feasible-edge and flip-response failures. The first
broad host panel exposes a different terminal injury. On map `9,854,000`, seat 0, against
`gold_adaptive`, worker 2 carries two wood while alternating `(8,4)<->(8,3)` for turns 34--258:
225 consecutive no-progress turns, no DROP, and unchanged cargo. Parent margin +68 becomes -93.

This directly violates I-19/I-20/I-21 and D-1, so exact SHA `9f5ef833...` remains
`IMPLEMENTATION_INVALID`. Stop banana-live, `897829265`, value, and Arena gates. Pipeline v2 also
needs this missed multi-worker full-cargo oscillation as a permanent failure-ledger class and
candidate-driven red/green gate. Full report:
`data/analysis/live-agent-6553250/banana-restoration-r2-round4-host-review-2026-08-05.md`.

## Round-5 withdrawal — 2026-08-06

Claude withdrew 77,299-byte SHA `47c98f53...` before host work. Its new deterministic fuzz panel
found 141/240 candidate games in seven blocking families, including 37 recurrences of the
full-cargo coordination class through a second stationary-resident/articulation mechanism. The
withdrawal supersedes the handoff; no host replay, value, or Arena gate is due for these bytes.
Round-6 SHA prefix `eac2eb36` reduces the panel to 47/240 blocking games but is explicitly a
stabilization baseline, not a handoff.

Deferred, non-blocking artifact request: Claude asked for the 32,885-byte raw map-`9,854,000`
diagnostic trace previously identified by SHA prefix `c7d6e033` under shared LFS. The original was
scratch output, not a retained authoritative artifact; regenerate it from the documented round-4
host command before publishing, then verify the full hash. This request does not unblock design or
host gates.

## FSM design review — 2026-08-06

The design-first reset and its state/channel skeleton are directionally accepted, but the draft at
commit `a0bad0b...` is `REVISION_REQUIRED`. It lacks deterministic priority for simultaneous
events; EV7 and the founding guard use proxy deadlines instead of one exact harvester/chopper asset
survival oracle; parent-difference attribution is only valid on aligned prefixes; and N1 carrier
progress conflicts with unconditional resident priority. Post-release veto scope, impossible
commitment exits, and the exact bounded-enumeration manifest also need closure before
implementation. Full report:
`data/analysis/live-agent-6553250/banana-restoration-r2-fsm-design-review-2026-08-06.md`.
