# Compiler cost and opponent-history diagnostics

Production is still exact V439 / agent 6704418, last verified rank 28/177, rating 23.43.
The top-seven objective is unmet. No gameplay source or canonical publication changed in this
stage. Both prior candidate deployment failures remain recorded separately in
`LOOKAHEAD-FIELD-FAILURE-2026-09-05.md`; neither is retried or reclassified as a played game.

## Measured platform compiler, not an assumed match

One separately frozen noncompetitive diagnostic issued only WAIT and queried compiler version,
architecture and debug-assertion mode. It read no credentials or arbitrary environment variables.
Game **901556584**, consumed seed 260905990701, seat 0 versus putibuzu / agent 6479779:
22/226, official loss, wood 0/50, one requested/played game, zero deployment failures. This is
environment evidence, not a candidate comparison or strength result.

Frame 1 stderr establishes **rustc 1.90.0**, commit
`1159e78c4747b02ef996e55082b704c09b970588`, LLVM **20.1.8**, x86_64 Linux,
`debug_assertions=false`. The executable is `/usr/local/bin/rustc`; `rustc` is absent from PATH.
Exact optimization flags and the compilation deadline remain unverified.

A matching toolchain is installed privately at
`/data/separate_troll_farm-working/toolchains/rustup/toolchains/1.90.0-x86_64-unknown-linux-gnu/bin/rustc`.
The global Rust 1.97.1 toolchain is unchanged. Existing frozen reference rlibs require that local
1.97.1 toolchain; standalone builds can now use the verified platform version independently.

## Closed no-inline experiments

Claude proposed the bounded helper; primary review corrected its scanner's false rejection of
`Option<[f64;2]>` function returns as trait declarations. Executable construction checks cover
that case, trait exclusion and exact recovery after removing inserted annotations. No logic or
source tokens other than the explicit attributes changed.

| Rust 1.97.1 build | No-inline sites | Full compile, seconds | Metadata-only, seconds |
|---|---:|---:|---:|
| Unchanged control | 0 | 8.740 | 0.746 |
| Command wrappers | 7 | 8.622 | 0.733 |
| Rollout and direct-step boundary | 2 | 8.497 | 0.720 |
| Both groups | 9 | 8.512 | 0.746 |
| Large function bodies | 8 | 8.625 | 0.738 |

All compile successfully with zero diagnostics. The small single-shot differences are not a
material improvement. A separately frozen all-boundaries follow-up inserts 216 annotations and
takes **9.673 seconds**, failing its predeclared 25% reduction gate. None is advanced.
The V439 reference builds locally in 6.49 seconds, with six existing warnings.

A diagnostic `-Z time-passes` build used `RUSTC_BOOTSTRAP=1` only to enable local compiler
instrumentation, not for deployment. Total 8.495 seconds; reported LLVM passes 2.584 seconds,
thin-LTO 4.309 seconds, linker 0.044 seconds. These phases overlap and must not be summed as
independent wall time. Optimized LLVM IR contains 161,096 body lines across 344 definitions;
this is a size diagnostic, not a function CPU profile. Large generic stable-sort instantiations
are a follow-up hypothesis, not yet a demonstrated bottleneck.

## Closed lean-legality compile experiment

Claude proposed a parity-only specialization; primary reviewed guarded replacements and
strengthened failure journaling, snapshot checks, compiler selection and fixed crate naming.
The prototype removes detailed issue records and logging-only command copies/conflict passes,
but retains command accounting and the original fail-closed critical classification. Full
state/engine/direct-MOVE code, the V439 policy prefix and planner suffix are unchanged.

The generated differential retains all original state fixtures, the explicit Java plant-order
oracle correction, and full game-field comparisons. It replaces detailed issue-vector equality
with exact command-count/critical-count equality, since the removed details are intentionally
unavailable. Added unknown-command and supported noncritical fixtures exercise both outcomes.
**8,192 transitions pass**, zero state or retained-legality mismatches, 74 previously documented
reference order repairs; the critical fixture records one critical error as expected.

On matched Rust 1.90.0, lean compile **8.602 seconds**, unchanged control **8.589 seconds**,
both with zero diagnostics. The predeclared 25% relative reduction gate fails. The old 1.97.1
absolute threshold is not transferred across compiler versions. No model replacement, runtime
promotion or platform test follows from this result.

## Opponent-history reproducer

An independent shadow policy receives every observed opponent-relative state from turn one;
the actual cold opponent still first receives turn 220. The shadow never controls a rollout.
Primary strengthened source/binary hash checks, prediction completeness and failure accounting.
Across eight existing archived streams, all output commands remain identical to the frozen
planner. Five games reach turn 220, yielding 391 paired predictions. There are 34 raw differences:
**five display-only MSG differences and 29 gameplay-action differences across four games**.

First action difference: game 901547802, turn 238. Cold predicts `MOVE 0 3 0; MOVE 3 4 1`;
warm predicts `MOVE 0 4 1; MOVE 3 6 1`. No stream fails. This verifies a behavioral modeling
difference, not that warming the opponent improves wins. No gameplay edit has been bundled.

Evidence root: `/data/separate_troll_farm-working/planning/2026-09-05/`, particularly
`compile-cost-{plan-v2,builds}/`, `compile-all-boundaries/`, `compiler-timed-profile.stderr`,
`compiler-environment-probe-{plan.json,run/}`, `lean-legality-matched-01/`, and
`warm-shadow-run1/{report.json,action-differences.json}`. Claude prompts, responses and reviewed
helpers are preserved alongside them. Next bounded work is compact stable-sort code generation;
no further platform request is scheduled.

Follow-up calibration against actual opponent commands on those same consumed streams gives
60/391 exact cold predictions versus61/391 warm predictions. Command-set Jaccard averages are
0.367726 and0.367848 respectively; on the29 changed-action turns,0 versus1 exact prediction.
This is almost no aggregate accuracy improvement, not support for automatically adopting a warm
model. Per-opponent figures and observed commands are retained in
`warm-shadow-run1/prediction-calibration.json`.

The sorting experiment and an explicitly predeclared combined follow-up are now documented in
`COMBINED-CODEGEN-PROTOCOL-2026-09-05.md`, including the failed original25% gate, the reasoning
for revising future diagnostic selection, and contemporaneous paired compilation measurements.
That combined source passed every local execution gate but failed its one platform smoke,
game901561127, with another pre-game compilation timeout. Three planner variants have failed
deployment; no competitive planner evidence was obtained. The combined diagnostic is closed,
no retry or publication is scheduled, and strategic/architectural prioritization is being reviewed.
