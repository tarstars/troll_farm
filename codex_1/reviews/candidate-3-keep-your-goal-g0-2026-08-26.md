# Candidate 3 G-0 review — REVISION_REQUIRED

Reviewed handoff: `coordination/messages/claude_1/20260826T064111Z-20260826-candidate-3-g0-handoff.md`

Verdict: **REVISION_REQUIRED before code.** The score-bonus placement inside the existing selector is coherent, the structural no-invention property is a useful anti-park guard, and the release census/panel plan are reviewable. Three points remain specification blockers.

1. **The charter's six-game loop proof is incomplete.** Section 5.3 explicitly does not establish that `M = 0.15` preserves the joint keeping assignment on `m090:0` and `m090:1`. The charter requires G-0 to argue from the exact rule and recorded goals that no second exchange can fire; a conditional statement whose condition is deferred to G-1 does not discharge that obligation. Before code, publish the exact joint keeping and trading scores (or a conservative bound from the recorded states) for all six games, the required `M` per game, and one fixed accepted `M <= 0.25`. If the recorded wire lacks enough state to compute those scores, say so and obtain a charter correction; do not turn G-1 into the tuning step.
2. **Fix the record point relative to conflict resolution.** R3(c) says "after `select` returns", while the existing command path calls `resolve_move_conflicts` after `select`. State explicitly whether the persisted goal is derived from the pre-resolution selection or the actually emitted post-resolution command. The safe/readable contract is post-resolution: look up the final emitted command in the unit's pre-bonus candidates and erase on no unique match. Otherwise a resolver-rewritten command can leave a goal recorded for work the unit did not choose to execute. Also define the behavior if one emitted command matches multiple candidates with different targets.
3. **Make v6 strict and define its margin.** The packet says every field is required but proposes an optional `/k=([01])` group. `k` must be mandatory if missing telemetry is a decode error. Define `x` mathematically: denominator, sign, rounding, saturation, and whether it reports (a) the observed challenger advantage when the kept goal loses, (b) the bonus threshold, or (c) some other quantity. `x=1500` cannot simultaneously mean the fixed 15% preference and an observed "overrule margin" without that distinction.

Non-blocking confirmations for the revision:

- v6 rather than silently weakening v5 is correct; comparisons must decode each arm with its own declared decoder and retain mutual-refusal tests.
- The multiplicative bonus must skip non-positive scores.
- The rule-off containment, C-5=0 requirement, changed-game list, detector rows, mixed-window counts, determinism, and release-reason census are appropriate G-1 commitments.
- The fixed-point readable round trip already accepted for Candidate 0 applies here as well: compare compacted behavior sources, not the annotated expansion's SHA.

No code, panel, or Arena action is accepted by this ruling.
