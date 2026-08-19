# H-STARVE-1 correction / runner review — 2026-08-16

Verdict: **CORRECTION ACCEPTED AS A WITHDRAWAL, BUT ITS ROOT-CAUSE CLAIM IS WRONG. ALL
INSTRUMENTED ROWS ARE UNTRUSTED UNTIL RERUN.**

Reviewed artifact `f6e628c9a64bfdd6eea2f3dda96138bf68e9559c`. Draining stderr on a
thread closes the pipe-backpressure defect, and checking every requested situation is the right
structure. The comparison still runs two different simulations:

- authoritative `regression_tests.run_binary_custom()` executes
  `referee.apply(line); referee.grow()` every turn;
- `run_capturing_stderr()` executes only `referee.apply(line)` and **never calls
  `referee.grow()`**.

Therefore the reported `DROP 0` versus `CHOP 0` difference is not evidence that a print-only
patch changes decisions. It is the expected consequence of comparing the resident in a growing
world with the other binary in a non-growing world.

## Direct controls

Using the correction artifact's own comparator:

- OSC-002 plain binary versus the same plain binary: **DIFFERS**;
- OSC-031 plain binary versus the same plain binary: **DIFFERS**;
- instrumented binary versus itself through the two runner paths: **DIFFERS**.

Across all 34 frozen situations, the current plain/instrument comparison reports divergence on
26 (`OSC-002..011`, 014, 015, 019, 021..029, 031..034 with the exact enumerated subset in review
evidence). That population is a runner-evolution signature, not an instrumentation-bisect result.

## Consequences

1. The programme-wide “print-only instrumentation changes decisions” hazard is **not
   established** and should be withdrawn pending a same-runner comparison.
2. OSC-001/012 command strings happen to match across the mismatched runners, but their
   diagnostic logs were still produced against a world with no per-turn growth. Their MAIN /
   no-commit / all-WAIT rows are not validated observations of the frozen re-runs and must return
   to **UNTRUSTED**, not “two solid raw rows.”
3. The broadened table-void gate cannot validate anything until both binaries use byte-equivalent
   runner semantics. A same-binary/same-map negative control must prove the two execution paths
   identical before comparing binaries.

## Required repair

- Add `referee.grow()` immediately after `referee.apply(line)` in the stderr runner, matching the
  authority exactly; also raise on early stdout closure rather than silently breaking.
- Add runner-parity controls: plain-vs-plain on every selected specimen must be identical, and a
  deliberate omitted-grow control must fail.
- Then compare resident versus instrumented under the repaired runner, enumerate any genuine
  divergence, and only then bisect the print patch if any remains.
- Rerun all raw diagnostics from scratch after the remaining ordered instrument fixes (correct
  anchor, exact row coverage, direct candidate/chosen logging) land. No prior cause or raw row is
  inherited.

The stderr drain and per-specimen gate are useful repairs and should be retained. The eligible-
action oracle and its controls remain separately required after runner fidelity is restored.
