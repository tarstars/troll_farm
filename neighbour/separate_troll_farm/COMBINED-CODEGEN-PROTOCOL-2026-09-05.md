# Combined compiler diagnostic and explicit selection-rule revision

The prior no-inline, lean-legality and compact-sort experiments remain failures under their
original 25% local compile-time reduction rule. This document does not retroactively pass them.
That heuristic was not calibrated to the platform's unknown compilation deadline. It therefore
cannot establish either deployability or strategic strength, and was too rigid as the only
criterion for deciding whether to gather actual deployment evidence.

New bounded mechanism: combine the independently tested lean legality reporting with compact
stable sorting. Include the remaining movement-priority comparator after manual verification
that its local bindings, BTreeSet membership reads and comparisons are pure. Preserve all game
transitions, critical-error decisions, policy parameters and comparison/tie semantics. Do not
include any no-inline variant or warm-opponent change.

Predeclared working protocol SHA:
`7a239dfb9cd834fe228f593747e02b821b746095a5d016a46973f087467494b1`.
Three paired builds per source, alternating order, six builds maximum, Rust1.90.0 and fixed
crate name. Retain all failures. Require zero diagnostics and at least5% median reduction versus
the contemporaneous control **to advance only to execution checks**. This is the explicitly
revised diagnostic rule, not a competitive gate or evidence that earlier experiments passed.

Execution gates: exact export size and default compilation, executable stable-tie/planner
fixtures, full archived command equivalence, per-turn runtime and open-stdin startup. Only after
all pass may the primary consider and separately freeze one new-source deployment smoke on a
consumed seed. No POST is scheduled by this protocol alone. Such a game would be deployability
evidence, never fresh competitive evidence. Earlier failed requests remain recorded.

The original paired field screen is closed, its confirmation remains unopened, and EVALUATION.md
still governs any later fresh paired comparison, confirmation, publication and mature top-seven
verification. A local compiler improvement does not satisfy the goal.

## Completed compiler measurements

The combined readable source SHA is
`461d0a6a7efc6f668bb77cbbd694070dc87f01e3bd4090cfc9041ca4262920e2`.
Its sorting edits invert byte-for-byte to the frozen lean source; that source differs from the
frozen original only in the documented parity reporting specialization. Twelve stable sorts
are replaced; none of the comparison expressions or unstable sorts is changed.

Paired times (control / combined), seconds: 8.612/8.089, 8.506/7.716, 8.526/7.729.
All six builds succeed without diagnostics. Medians 8.526/7.729, **9.35% reduction**. This passes
the new execution-check selection rule, not the old25% rule and not a platform/strength gate.

The preceding standalone sorting experiment compiled in8.747/8.560/8.187s (control/three
ranked-selector sorts/eleven lexically pure stable sorts). Its initial Rust fixture failed because
the template marker also appeared in a comment. Primary fixed substitution to require exactly
one standalone marker; the real Rust fixture then passed2,560 seeded stable-order checks with
zero diagnostics. Original failed fixture output and all compile results remain archived.

Evidence: `planning/2026-09-05/{combined-codegen,compact-sort-builds,compact-sort-fixture-repair}/`
under project working storage. The matched compiler and model differential evidence are in
`COMPILER-COST-RESULTS-2026-09-05.md`.

## Execution gates passed; platform deployment failed

Exact compact SHA `a08b2e6af6cd9844bdffeed707f2a93472fb76e348f4569953675ed3f2b4655e`,
92,938 UTF-16 units. Default matched-compiler build takes 8.049 seconds, zero diagnostics.
All nine executable planner/rank fixtures pass; full Python suite: 510 passed in 221.26 seconds.
The full 160-stream benchmark covers 43,263 turns with zero changed commands against the frozen
original planner or between readable/compact exports. Maximum readable/compact decision times
43.223/44.304 ms, zero over 50 ms. Separate exact uninstrumented binaries agree on all 160 streams.
All 320 interactive startups produce the expected command, maximum 2.324 ms, zero over 50 ms.

Only after those gates passed, the separately frozen one-request smoke plan was created:
`combined-codegen-smoke/plan.json`, SHA
`5c5b4ffdd97caa2c3cee7d05c13ed0d3827646a9a3bd21fbe57fbc4c5581765d`.
Session 86141 ran once, 12:04:46–12:05:19 UTC, and is terminal exit 75. Game **901561127**,
consumed seed 260905990701, seat 0 versus putibuzu / 6479779: scores -2/22, official ranks 1/0.
Frame zero explicitly reports **compilation timeout before gameplay**, without warning output.
The generic collector message says runtime error; the archived replay establishes compilation
as the actual failure phase. Response and replay are saved despite the manifest's empty rows.

This candidate has **one requested loss, one compilation failure, zero played games**. This
diagnostic is closed and must not be retried. Across the original planner, quiet repair and this
combined source, three candidate requests all failed compilation; none yielded gameplay evidence.
The WAIT-only compiler-environment diagnostic is separate and did play successfully.

The 9.35% local median compile reduction was insufficient for deployment. It is not a basis for
fresh competitive screening or publication. No further POST is scheduled; before more compiler
micro-optimizations, reassess the architecture's cost and attainable strategic effect. Live V439
and canonical files remain unchanged; mature top-seven is still unachieved.
