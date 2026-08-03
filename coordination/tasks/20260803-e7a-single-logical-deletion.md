# 20260803-e7a-single-logical-deletion: remove one unreachable live block safely

- Status: in_progress
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: pending
- Integrator: local_codex_1
- Area: owner-rescoped live-source simplification
- Base commit: 8f708f01b1eece651627d2fedbe5fa5eb5a1bd8f
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-08-03T05:03:59Z
- Last updated UTC: 2026-08-03T05:22:27Z

## Outcome

Replace the rigid 50% reduction target with one substantial, named deletion from the exact
62,820-byte live E7a source. Keep the result strictly smaller, readable, behavior-exact on the
supported live roster, and eligible for Arena promotion only after frozen equality gates.

## Frozen protocol

`docs/e7a-single-logical-deletion-protocol-2026-08-03.md`

## Exclusive write set

- `docs/e7a-single-logical-deletion-protocol-2026-08-03.md`
- `local_codex_1/e7a-single-logical-deletion/`
- `data/analysis/live-agent-6553250/e7a-single-logical-deletion-*`
- new paths matching `cgauto/submissions/candidate-e7a-single-logical-deletion-*`
- `coordination/tasks/20260803-e7a-single-logical-deletion.md`
- `coordination/messages/local_codex_1/*20260803-e7a-single-logical-deletion*`
- `coordination/status/local_codex_1.md`

## First candidate

Remove the generic selector for three-or-more friendly trolls. The live policy's own training
cap makes that path unreachable after two trolls; zero-, one-, and two-troll selection remains
byte-exact. Unexpected larger rosters fail safe to one `WAIT` per friendly troll.

## Arena boundary

No Arena action until rebuild, compile, semantic, exact live-replay command equality, full
development equality, untouched equality, and promotion preflight all pass.

## Progress 2026-08-03T05:07:37Z

The exact builder removes 542 bytes, reducing 62,820 -> 62,278 (0.863%) with candidate
SHA-256 `ab0934740171cc7f5f4cd65cdfb8cf879ca92d8236c9505903e4741e0a7c57c2`. It finds one
hard two-troll training cap and one exact generic fallback, replaces only that fallback, and
rebuilds byte-identically. The unexpected roster-above-two state now returns one `WAIT` per
friendly troll.

Optimized standalone compile and empty input pass. A live-baseline-aware validator compiles
both exact sources and reports byte-identical outcomes on all ten frozen semantic fixtures:
focus sector (four cases), training bill, training deadline fallback, wood banking, same-target
assignment, landing collision, and endgame deadline. Exact live-replay command parity and the
516-task development equality panel remain pending. No Arena action.

## Progress 2026-08-03T05:15:20Z

Exact public-live parity passes on 25/25 immutable counterexample games and 7,234 command lines
with zero differing games, zero unknown updates, and zero stderr. The inherited maximum period-2
episode is 128 in both sources; this deletion is behavior-preserving, not a liveness repair.

A generated live-type adapter then ran the full 43-map / both-seat / six-family development
panel. All 516 terminal rows are exact between baseline and candidate: mean/lower 0.0,
catastrophes 19 -> 19, negative mass 4,138 -> 4,138, and zero differences in scores, resources,
turns, training, workers, liveness, or issue fields. Latency passes at p95 ratio 1.0041 and
candidate maximum 6.276 ms.

**Disposition: DEVELOPMENT EXACT-EQUALITY PASS / UNTOUCHED TRANSFER PENDING / NO ARENA
ACTION.** Full evidence is in
`data/analysis/live-agent-6553250/e7a-single-logical-deletion-development-qualification-2026-08-03.md`.

## Progress 2026-08-03T05:22:27Z

Scoped exact-token searches of canonical compact records, the current task tree, tracked
filenames, and Git history found no recorded use of seeds 9,867,000--9,867,042. The broad text
`9,867` has one unrelated byte-count prose match; it is not a map seed. In accordance with the
owner's search-safety instruction, no recursive scan traversed huge mounted bulk repositories.
No map in the range has been generated or inspected.

The dedicated evaluator hard-codes 43 maps, both seats, six families, eight threads, 50,000
bootstrap samples, and exact terminal equality; it exposes only output paths. Compile-only
preflight passes without map generation. Candidate, range, runner transformation, evaluator,
development/live/semantic evidence, hashes, gates, and the one-shot command are frozen in
`candidate-e7a-remove-generic-selector-fresh-lock.json`. The range remains unopened until this
lock is committed, pushed, and remotely verified. No Arena action.
