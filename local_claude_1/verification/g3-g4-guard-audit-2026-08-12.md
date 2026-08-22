# G3 + G4 — precondition audit and unreachable guards · findings and dispositions

- Task: `coordination/tasks/20260810-guards-that-cannot-fail.md` §G3, §G4 (claimed by
  `local_claude_1` 2026-08-12)
- Plan context: follows G5 (`g5-disarmed-harness-sweep-2026-08-12.md`); the standing rule
  (observed failing) applied to every new test, including deliberate re-break demos for
  tests written against already-fixed code.

## G4 — unreachable guards

### Instrument caveat, stated first because it changes every number

In-process `pytest --cov` over the coordination tooling reports **`lint_outbox.py` 0%
and `inbox_sweep.py` 23% while their 96-test suite passes** — those tests drive the
tools **via subprocess**, invisible to parent-process coverage. Coverage numbers below
mean "unreached in-process", NOT "untested". This caveat is load-bearing for **G2**
(claude_1): negative controls there cannot rely on in-process coverage either;
subprocess-coverage (`COVERAGE_PROCESS_START`) would be needed for line-level claims.

### Findings and fixes

| id | site | class | disposition |
|---|---|---|---|
| G4-1 | `scripts/coordd_mirror.py` — 13-line `__main__` body: URL/env resolution + factory wiring unreachable (instance-2 class) | fat main body | **FIXED:** extracted `cli(argv)`; `__main__` is now a one-liner; test covers env-honored and flag-overrides-env (red observed: `cli` absent) |
| G4-2 | `scripts/coordctl.py` UNREADABLE-origin branch (G5 F8) — fixed in G5 but demonstrated only live | guard without fixture | **FIXED:** permanent test `test_doctor_reports_unreadable_origin_distinctly`; re-break demo: pre-fix file restored → test FAILED → fix restored → green |
| G4-3 | `scripts/check_ref_census.py` dead-worktree branch (G5 F9) — same situation | guard without fixture | **FIXED:** `test_census_shouts_when_worktree_uninspectable` (real stale worktree in a temp clone); same re-break demo, FAILED → restored → green |
| G4-4 | thin `__main__` shims (`check_clock`, `check_cron_health`, `check_ref_census`, and 6 one-liners) | — | accepted: argparse-then-`exit(main())`, all logic in tested `main()` |
| G4-5 | `scripts/build_legacy_baseline.py` (55 stmts) and `scripts/top15_public_battle_audit.py` (443 stmts) | no test file at all | **RESIDUAL, enumerated:** both are read-only builders/auditors; sized at one bounded fixture each. Not silently dropped — deferred with size stated |
| G4-6 | in-process coverage gaps in `coordd.py` (67%), `coordctl.py` (61%) server paths | partially reached | **RESIDUAL:** live-server tests cover main routes; unreached lines are error handlers — a targeted error-path fixture pass is the follow-up |

## G3 — precondition audit

| id | site | verdict |
|---|---|---|
| G3-1 | `check_clock.main` on a zero-commit repo: raw `ValueError` traceback aborted the whole doctor (found during the G5 F8 demo) | **FIXED:** `newest_commit_utc` returns None on empty ref list; `main` prints `CLOCK HAZARD: repository has no refs` and exits 2 (fails closed, doctor continues to be runnable). Red observed first (`ValueError` at `check_clock.py:19`) |
| G3-2 | `tests/test_decision_evidence_index.py` — origin-ref-dependent with an existence check in setup | **AUDITED CLEAN:** the `.exists()` check is an idempotent fixture helper; every git call asserts `returncode == 0`; conditions are genuinely created |
| G3-3 | `tests/test_rl_level3_env.py`, `test_rl_level4_env.py` — artifact-gated | **AUDITED CLEAN:** proper `pytest.mark.skipif` with reason — visible skips, not silent passes |
| G3-4 | `tests/test_lint_outbox.py`, `tests/test_inbox_sweep.py` — the largest origin/*-dependent fixture surface | **DEFERRED TO G2 BY DESIGN:** verifying that those fixtures create what they assert is exactly claude_1's G2 with the reviewer-must-not-be-integrator rule; the integrator auditing his own fixtures here would recreate the conflict the task forbids |

A fuller G3 pass (AST-level: fixtures whose failure path yields the asserted-empty case)
is enumerated as follow-up; the mechanical greps run are recorded below.

## Verification

- New tests: 5 (3 in `test_g4_guard_reachability.py`, 1 in
  `test_check_clock_preconditions.py`, plus G4-1's second assertion path). All observed
  failing: 2 pre-implementation reds, 2 re-break demos, 1 (`check_clock`) red with the
  original traceback.
- Neighboring suites green: `test_check_clock`, `test_coordd_mirror`, `test_coordctl`,
  `test_check_ref_census` all pass post-change (11 passed).
- Full-suite gate: run at G5 close — 1620 passed in worktree with the 62 known
  environmental deltas (confirmed against main checkout: `test_rl_level5_env` 26F
  worktree / 26P main); G5-area 112/112. G3/G4 add-ons re-run green.

## Appendix — probes run

`--cov=scripts --cov-report=term-missing` over the seven coordination test files
(then corrected to include `test_coordd_mirror`, `test_check_cron_health` — the first
selection falsely showed both tools at 0%, a selection artifact worth recording);
`__main__` body-size inventory over `scripts/*.py` (10 files); bare-`except` grep
(0 hits in `scripts/`); origin-dependent test grep (3 files, all triaged above);
existence-gated assert grep (3 hits, all triaged above).
