# Independent review — watchdog-test job (G6)

Date: 2026-08-14

Reviewer: `codex_1`

Integrated subject: `origin/main` at `227ec044`

Handoff artifact: `bb845da522bc0904f45a6e149c08d137ee3c4c61`

## Owner summary

Seventeen previously unproven safety checks now demonstrably catch the failures they claim to
watch. Two other checks cannot affect any result because the surrounding code already guarantees
their condition. The technical work is sound, but the published “51 of 62” score is one commit
ahead of the repository: only the first untestable check has actually been removed from the
denominator. The second removal must be encoded and rerun before this job closes.

## Verdict

**REVISION_REQUIRED — apply the already-approved D4-M6 exclusion mechanically.** All other G6
substance is accepted.

## Independent execution

From a detached worktree at `origin/main` `227ec044`:

- `python3 -m unittest test_trace_detectors`: 67 tests pass.
- Audit self-tests: 13 tests pass.
- Full `run_mutations.py`: control green; 65 manifest entries attempted; 63 mutants included;
  zero patch, compile, or probe errors; **51 caught / 12 survived**; all 51 caught by a declared
  owner class; none caught only by another detector.
- `render_branch_ledger.py --check`: all five prose/data axes agree across 47 rows.
- Sacred source remains byte-exact at SHA-256 `fff6669b0bc0b15b…`.

## Both-halves fixture discipline

Sampled every G6 fixture group on the unmutated control:

- D-7: 7 tests pass.
- D-8: 7 tests pass.
- D-5: 7 tests pass.
- D-6: 7 tests pass.
- Final D-1 / D-3 / D-4 groups: 3 / 2 / 3 tests pass.

The sampled classes contain both a limiting innocent case that stays silent and a deliberate
violation that fires. The full mutant rerun then observes the corresponding owner class fail
against each deliberately broken subject.

## Incidental catches

All nine reported incidental catches are honestly attributed in the machine-readable manifest:
`D7-M8`, `D8-M7`, `D5-M2`, `D5-M3`, `D5-M7`, `D6-M5`, `D6-M2`, `D6-M8`, and `D1-M7`.
Each is caught in the rerun, each has `caught_by_expected=true`, and each fails its declared G6
owner class. No incidental catch relies only on a different detector.

## Equivalent guards

Both equivalence findings are accepted.

- `D8-M8`: the checked plant comes from `alive_per_turn[t]`, which is built from the same state
  using the same `BANANA` filter. A non-banana cannot reach the guard. Mutating the guard changes
  zero of 416 probe traces.
- `D4-M6`: a door-cell `DROP` starts commitment, is not a banned verb, and immediately clears
  commitment through `executed_drop` before state can carry forward. Its only initialization,
  `nd_run=0`, is common to every commitment start. Mutating the branch changes zero of 416 traces.

## Required repository update

The coordinator has approved excluding `D4-M6`, but current trunk still records:

- `D4-M6.excluded_from_totals = false`;
- its ledger row as `NO_FIXTURE` rather than `EQUIVALENT_GUARD_UNTESTABLE`;
- full-run totals of 63 included mutants and 51 caught;
- only `D8-M8` and the historical retired mutant in `excluded_entries`.

Apply the same four conditions already used for `D8-M8`: manifest-level exclusion with both
proofs, distinct ledger label, all denominators stated visibly, and no detector predicate change.
Then regenerate the ledger/results and run the entire manifest. Acceptance requires the machine
output itself to report 62 included mutants, 51 caught, zero infrastructure failures, and prose
matching data. Until then, **51/63 is verified; 51/62 is approved but not implemented**.
