# 20260802-e7a-half-size-logical-simplification: halve live source without leaving top 15

- Status: superseded_by_owner_rescope
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: pending
- Integrator: local_codex_1
- Area: owner-directed deployment simplification
- Base commit: c123a551c0d9ce7bc7c9c0cf0e1edd494b949d65
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-08-02T19:52:10Z
- Last updated UTC: 2026-08-03T04:42:38Z

## Outcome

Reduce the exact 62,820-byte live E7a source to at most 31,410 bytes by removing or
replacing inefficient logical blocks—not identifier shortening, encoding tricks, or
obfuscation—then demonstrate a live rank no worse than 15 after reconvergence.

## Frozen protocol

`docs/e7a-half-size-logical-simplification-protocol-2026-08-02.md`

## Exclusive write set

- `docs/e7a-half-size-logical-simplification-protocol-2026-08-02.md`
- `local_codex_1/e7a-half-size-logical-simplification/`
- `data/analysis/live-agent-6553250/e7a-half-size-*`
- new paths matching `cgauto/submissions/candidate-e7a-half-size-*`
- `coordination/tasks/20260802-e7a-half-size-logical-simplification.md`
- `coordination/messages/local_codex_1/*20260802-e7a-half-size-logical-simplification*`
- `coordination/status/local_codex_1.md`

## Shared read-only paths

- exact E7a and stable-parent submission artifacts
- `cgauto/slim_live_source.py` and existing validators/runners
- current public replay inventory and decoded audit
- open local evaluation substrates and already-open maps
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, live ledger, promotion runbook

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred)
- every existing `cgauto/submissions/*` artifact
- `data/raw/games/`, the 05:17 cron, and sealed/confirmation map ranges
- Arena mutation endpoints before a recorded qualifying candidate and controller preflight

## Deliverables

- Byte-attribution report naming live logical blocks and their removable sizes.
- Readable candidate source(s), deletion/replacement manifest, builder, and hashes.
- Compile, legality, liveness, command-difference, open-panel value, size, and latency evidence.
- At most one active Arena mutation at a time, fully recorded if a candidate qualifies.
- Mature live checkpoint proving both source bytes <=31,410 and rank <=15.

## Acceptance checks

- `wc -c <candidate>` is at most 31,410 (50% of 62,820).
- A mechanical audit proves no identifier-renaming or compression/minification pass.
- The candidate compiles as standalone optimized Rust and passes malformed/empty-input checks.
- The candidate passes the frozen semantic, liveness, open-panel, and latency gates.
- Arena exact-source recovery matches the candidate SHA-256.
- Mature Arena room read reports rank <=15 for that recovered exact agent identity.
- Sacred source and raw-game cache remain unchanged.

## Arena authority

Read-only platform access: allowed. Platform mutation: only the sole controller
`local_codex_1`, after the frozen local qualification and promotion preflight. The user has
set the terminal live objective (rank <=15), but this record does not waive serialization,
identity, health, or no-ambiguous-retry rules.

## Handoff

Exact candidate, source-size proof, non-obfuscation audit, full validation evidence, live
identity/checkpoint, and final requirement-by-requirement audit.

## Progress 2026-08-02T20:21:09Z

`INTEGRATED_HALF r5` is 30,949 bytes (50.73% below the exact 62,820-byte baseline), SHA-256
`6692fa59...`; standalone optimized compile, empty input, dead-code lint, baseline hash, and
sacred hash gates pass. Static report:
`data/analysis/live-agent-6553250/e7a-half-size-r5-static-qualification-2026-08-02.md`.
Behavioral, liveness, latency, and value qualification remain in progress; no Arena action.

## Progress 2026-08-02T21:12:00Z

r5 failed the 16-game closed-loop smoke (-262.5 mean paired margin; 14/16 catastrophes).
Repairs through r18 restored the same smoke to -6.625 with 3/16 catastrophes and maximum
period-2 target run 3, but r18 is 35,146 bytes, 3,736 over the ceiling.  r19's larger chop
forecast regressed to -11.4375 and was rejected.  Reproducible runner, exact r18/r19 JSON,
and the negative iteration report are prepared for publication; no Arena action.

## Progress 2026-08-02T21:45:15Z

r32 is frozen at 31,387 bytes, SHA-256 `abb202db...`: 23 bytes under the ceiling and a
50.034% real logical reduction. Strict optimized compilation, empty input, sacred hash,
and all 10 semantic fixtures pass. Motion smoke is -6.625 with equal catastrophes and
maximum period-2 target run 3 versus 6. The one-map continued-referee smoke is negative
(-9.9167) but has 12/12 worker-two coverage and zero median delay; one/four-thread task rows
are byte-identical. The exact 43-map/516-task command is now published and locked. No Arena
action; full value and exact live-counterexample liveness gates remain pending.

## Progress 2026-08-02T21:50:00Z

The frozen full panel completed once and terminally rejects r32: mean paired margin
-53.6609, bootstrap lower -69.2539, catastrophes 19 -> 64, negative mass 4,138 -> 15,143,
all six families negative, and both seats negative. Worker-two timing, latency, integrity,
and the local period-2 gate pass, but value does not. No Arena action. r32 will not be tuned
on its evaluated panel; a distinct successor and untouched validation range are required.

## Progress 2026-08-02T22:06:14Z

Already-consumed-panel attribution localizes the loss. Removing only the orchard while
retaining the exact inner core is -7.6434 at 48,644 bytes. Retaining the exact Moisan
forecast/banking/selector/movement beneath the focused Yamo yields -27.4535 at 33,167
bytes, versus r18 -46.4864 and r32 -53.6609. The next route is not further r32 trimming:
it must restore focused-Yamo regeneration/endgame value while removing another 1,757 named
bytes. Seeds 9,854,043--9,854,127 remain untouched; no Arena action.

## Progress 2026-08-02T22:34:10Z

Two consumed-panel ablations recover most of the focused-Yamo loss. Deleting the
unconditional 10,000-point current-tree commitment improves the 516-task mean from
-27.4535 to -20.6298 while shrinking 33,167 -> 32,819 bytes. Restoring the exact tuned
opening then improves it to -9.8101 at 36,059 bytes. A fixed worker, approximate all-profile
search, partial-wood banking, score-aware endgame boundary, and blunt liveness router were
rejected on 96-task probes. The remaining problem is to specialize the exact opening
decisions and remove 4,649 bytes without losing their value. Untouched seeds remain closed;
no Arena action.

## Progress 2026-08-02T23:00:27Z

A distinct size-qualified successor now exists at 31,401 bytes (50.014% reduction),
SHA-256 `923395d8...`. It preserves exact initial tuned-opening decisions and exact Moisan
economics while deleting general policy, priority-router, N-worker, unused trait, and
unused protocol logic. Adding `WAIT` to bank routes repairs an empty-pair single-door case
and improves the 516-task mean to -6.9574, bootstrap lower -13.0213, catastrophes 19 -> 22,
and negative mass 4,138 -> 5,012. Size/compile/latency pass; value and liveness do not, so
the source is not frozen for untouched validation and no Arena action is allowed.

## Progress 2026-08-03T00:04:17Z

A structural-specialization successor is now 31,337 bytes, 73 below the ceiling, SHA-256
`7fd755c2...`. It deletes unused runtime state and zero-harvest/training/rule/target/container
generality without renaming or formatting compression. Standalone compile and empty input pass.
Its 96 non-latency task rows are byte-identical to the prior wait-on-conflict smoke: +6.03125
mean, +0.88542 lower, and zero period-2 episodes >=6. Full 516-task consumed evaluation is the
next phase; untouched maps remain closed and no Arena action is allowed.

## Progress 2026-08-03T00:10:33Z

The exact 31,337-byte successor passes every full 516-task consumed gate: mean +5.5310,
lower +1.8178, catastrophes 19 -> 11, negative mass 4,138 -> 3,695, six/six positive
families, both seats positive, worker-two coverage 100% with delay 0, and period-2 >=6
115 -> 0. Candidate and evaluator hashes are locked. Fresh seeds 9,854,043--9,854,085
were unopened before the lock and are now reserved for transfer validation. No Arena action.

## Progress 2026-08-03T00:15:16Z

The locked exact source is terminally rejected on the reserved 516-task fresh block. Mean
remains +3.3043 and period-2 >=6 remains zero, but bootstrap lower is -6.3450 and negative
mass increases 4,385 -> 4,891. Roots 9,854,062 and 9,854,065 account for +643 negative mass,
but regressions span multiple families. No Arena action and no tuning on the fresh block; a
new logical successor and newly reserved untouched range are required.

## Progress 2026-08-03T01:13:00Z

A distinct 31,398-byte successor, SHA-256 `ec4b3140...`, repairs both traced transfer
mechanisms without threshold tuning: front-to-back bank convoy priority prevents a faster rear
wood carrier from pinning the front carrier, and a mixed-door orchard is admitted only when a
third home door remains available. Standalone optimized compile and empty input pass. Ten/ten
semantic fixtures now reference the exact live E7a training choices and pass; the 16-game motion
packet has candidate maximum period-2 run four and one fewer catastrophe.

On consumed seeds 9,854,000--042 it passes all 516-task gates at +9.033 mean / +3.789 lower,
catastrophes 19 -> 12, negative mass 4,138 -> 3,853, all families and seats positive, worker-two
coverage 100%, delay zero, and no long period-2 episode. Replaying the already-opened rejected
block is diagnostic only but also passes (+9.079 / +1.052; negative mass 4,385 -> 3,968), closing
the two observed failure mechanisms.

Exact-token/history/artifact-name collision checks selected unrecorded seeds
**9,863,000--9,863,042** for the required 43-map/516-task untouched gate. The dedicated launcher
exposes no range arguments and compiled successfully without generating a map. Source, range,
runner transformation, evaluator, thresholds, families, seats, bootstrap, and one-shot rule are
frozen in `focused-yamo-bank-convoy-spare-door-orchard-fresh-lock.json`. At this marker the new
range remains unopened. The lock must be committed and pushed before execution; no Arena action.

## Progress 2026-08-03T02:06:05Z

The 31,398-byte source passed its untouched 9,863,000--042 gate at +5.5465 mean / +1.2868
lower with all frozen gates green, but it is superseded: exact live replay 897830380 exposed an
empty selector panic, and the totalized safe selector still reproduced period-2 runs >=6 in
10/25 exact live counterexamples. The consumed range remains valid only for its old exact hash.

A distinct 31,405-byte successor, SHA-256 `9a202242...`, adds a two-slot A-B-A landing guard and
funds it by deleting speculative simultaneous-PICK stock reservation, redundant funded-shack
evacuation checks, terminal occupied-door prefiltering, and a dead live-tree health predicate.
No renaming or compression is used. It passes ten semantic fixtures, the 25/25 exact live
counterexample packet with maximum period-2 two, and all 516 consumed-panel gates at +9.4535
mean / +4.0426 lower, catastrophes 19 -> 13, negative mass 4,138 -> 3,855, six/six positive
families, both seats positive, worker-two coverage 100%, and zero long period-2 episodes.

The exact source is development-qualified, not transfer-qualified. A new untouched range must
be collision-audited and locked before one-shot execution. No Arena action.

## Progress 2026-08-03T02:13:08Z

Exact-token, task-tree, tracked-filename, Git-history, and verified external-root filename
checks found no recorded collision for seeds 9,864,000--9,864,042. The dedicated evaluator
hard-codes 43 maps, eight threads, 50,000 bootstrap samples, both seats, and the six frozen
families; it exposes only output paths and refuses pre-existing outputs. Compile-only preflight
passes with generated runner SHA-256 `1dee8d70...` and no map generation. Candidate, range,
evaluator, generated runner, shared analyzer, library, evidence hashes, gates, and exact command
are frozen in the new lock. The range remains unopened until the lock commit is pushed.

## Progress 2026-08-03T02:18:23Z

The exact locked command ran once over all 516 tasks and terminally rejects the 31,405-byte
candidate. Mean +9.4574, bootstrap lower +1.7442, all six families and both seats positive,
negative mass 6,149 -> 5,421, worker-two/liveness/latency/integrity gates all pass, but
catastrophes increase 26 -> 27. Nine candidate-only catastrophe rows outweigh eight
baseline-only rescues. The range is consumed; there will be no rerun, threshold relaxation, or
Arena action. A next attempt requires categorical mechanism attribution, a distinct source,
and a new untouched lock.

## Progress 2026-08-03T02:47:04Z

Consumed-panel cumulative attribution isolates the extra catastrophe to the unconditional
funded-shack evacuation simplification. The stock/helper deletion holds catastrophes at 26,
while adding the evacuation collapse produces 27 and exactly reproduces the rejected 31,405-byte
source before its final neutral deletions.

A distinct successor is now 31,248 bytes (50.258% reduction), SHA-256 `a767e362...`. It retains
the original funded-shack evacuation, removes neutral terminal predicates, and replaces the
larger A-B-A history with a previous-observed-cell no-backtrack guard. Rebuild is byte-identical;
optimized compile, empty input, ten semantic fixtures, and the sacred hash pass.

The exact 25-game live counterexample packet passes with maximum period-2 run four and zero games
at or above six. The 516-task consumed development panel passes at +9.1415 mean / +3.8585 lower,
catastrophes 19 -> 14, negative mass 4,138 -> 3,871, six/six positive families, both seats
positive, worker-two coverage 100%, and zero long period-2 runs. Diagnostic replay on the consumed
transfer panel also closes the categorical failure: +10.2597 / +2.6124, catastrophes 26 -> 26,
negative mass 6,149 -> 5,374.

This is development evidence only. A new collision-audited untouched range and immutable lock are
required before one-shot transfer validation. No Arena action.

## Progress 2026-08-03T02:54:31Z

Exact-token searches of scoped live records and the task tree, tracked filenames, Git history,
and filenames beneath all five verified external project roots found no recorded collision for
seeds 9,865,000--9,865,042. No map in the range was generated or inspected.

The dedicated no-backtrack evaluator hard-codes 43 maps, both seats, the six frozen families,
eight threads, and 50,000 bootstrap samples; it exposes only panel/output paths and refuses
pre-existing outputs. Compile-only preflight passes without generating a map. Candidate, range,
evaluator, generated runner, shared analyzer, library, development/diagnostic evidence, gates,
and the exact command are frozen in `focused-yamo-bank-convoy-no-backtrack-fresh-lock.json`.
The range remains unopened until this lock commit is pushed and remotely verified. No Arena
action.

## Progress 2026-08-03T03:00:05Z

The exact locked command ran once over all 516 tasks and terminally rejects the 31,248-byte
candidate. Twelve of thirteen gates pass: mean +3.9167, lower -1.1822, catastrophes 14 -> 8,
negative mass 3,908 -> 3,549, both seats positive, worker-two/liveness/latency/integrity green,
and period-2 >=6 at zero. The family-transfer gate fails because legend-balanced is -2.9884 and
resident is -1.4419; the other four families are positive.

The range is consumed. There will be no rerun, row exclusion, threshold relaxation, or Arena
action. Diagnostic attribution can compare distinct logic on the preserved rows, but another
qualification attempt requires a distinct source and a new untouched lock.

## Progress 2026-08-03T03:53:51Z

Trace comparison rejected opponent-workforce, own-roster, and fixed-role thresholds. The two
largest legend losses were reversals onto or away from a tree, while a resident gain was an open
empty-route correction. A distinct tree-edge source now stops the second consecutive reversal
when either endpoint is a tree and otherwise bounds the episode below six MOVE decisions.

The exact source is 31,407 bytes, three below the ceiling, SHA-256 `acbada47...`; no renaming or
minification is used. Optimized compile, ten semantic fixtures, and the exact 25-game live packet
pass with maximum period-2 five. On the consumed 9,865,000--042 attribution panel all gates pass:
+4.6783 mean / -0.2926 lower, catastrophes 14 -> 8, negative mass 3,908 -> 3,422, five/six
nonnegative families, both seats positive, worker-two delay zero, and period-2 >=6 at zero.

This is diagnostic evidence only. The ordinary consumed development panel and motion packet are
pending; afterward a new collision-audited untouched lock is required. No Arena action.

## Progress 2026-08-03T04:02:08Z

The exact 31,407-byte tree-edge source passes every gate on consumed development seeds
9,854,000--042: +8.2248 mean / +3.0155 lower, catastrophes 19 -> 12, negative mass 4,138 ->
3,864, six/six positive families, both seats positive, worker-two coverage 100% with delay zero,
and period-2 >=6 at zero. The 32-game motion discriminator is liveness-clean at maximum four but
mildly adverse; it is not a promotion gate.

**Disposition: DEVELOPMENT-QUALIFIED / TRANSFER UNTESTED / NO ARENA ACTION.** A new untouched
range must be collision-audited and remotely locked before one-shot execution.

## Progress 2026-08-03T04:11:44Z

Exact-token searches of scoped live records and the task tree, current and historical tracked
filenames, Git content history, and filenames beneath all five verified external project roots
found no recorded collision for seeds 9,866,000--9,866,042. No map was generated or inspected.

The dedicated tree-edge evaluator hard-codes 43 maps, both seats, the six frozen families, eight
threads, and 50,000 bootstrap samples; it exposes only panel/output paths and refuses pre-existing
outputs. Compile-only preflight passes without map generation. Candidate, range, evaluator,
generated runner, shared analyzer, library, development/diagnostic evidence, gates, and exact
command are frozen in `focused-yamo-bank-convoy-tree-edge-reversal-fresh-lock.json`. The range
remains unopened until this lock commit is pushed and remotely verified. No Arena action.

## Progress 2026-08-03T04:17:29Z

The exact locked command ran once over all 516 tasks and terminally rejects the 31,407-byte
tree-edge candidate. Eleven of thirteen gates pass: mean +6.2926, lower -1.3469, five/six
nonnegative families, both seats positive, worker-two/liveness/latency/integrity green, and
period-2 >=6 at zero. The tail gates fail because catastrophes worsen 12 -> 16 and negative mass
worsens 4,567 -> 4,826.

The range is consumed. There will be no rerun, row exclusion, threshold relaxation, or Arena
action for this hash. Diagnostic attribution may compare distinct logic on the preserved rows;
another qualification attempt requires a distinct source and newly locked untouched range.

## Progress 2026-08-03T04:42:38Z

Consumed-row diagnostics show the fresh tail is not caused by the tree-edge rule, stock
reservation deletion, or terminal-door deletion alone. On the exact 9,866,000--042 rows,
strict no-backtrack, a five-step guard, tree-edge reversal, an over-limit exact-logic control,
and a stock-retaining control all remain positive at +6.22 to +6.53 mean but fail tail gates.
Tree-edge improves strict no-backtrack by three catastrophes and 191 negative-mass points.

Exact command traces for the worst task, seed 9,866,014 / seat 0 / gold-adaptive, first diverge
strategically when the half-size parent returns home and activates its compact APPLE orchard
while the baseline continues toward a natural tree. Globally deleting the orchard is falsified:
the readable 28,517-byte no-orchard control falls to -38.717 mean, catastrophes 12 -> 48, and
negative mass 4,567 -> 15,719. The next source should preserve orchard value while making
activation fail closed or closer to the exact parent decision.

A seven-page beginner-readable report now records the full session, test vocabulary,
chronological approaches, current results, evidence boundary, and next work:
`data/analysis/live-agent-6553250/e7a-half-size-last-eight-hours-report-2026-08-03.pdf`.
Its SHA-256 is `c61b07b907d1044f71b8a468cae69feaffa68703d05178102a32bd8b7600e447`.
No Arena action.

## Progress 2026-08-03T05:03:59Z

The owner softened the requirement from an exact 50% reduction to deleting one meaningful
logical block. This task is superseded by `20260803-e7a-single-logical-deletion`; all prior
half-size candidates and their fresh verdicts remain immutable evidence. The live bot is
unchanged.
