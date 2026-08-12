# G5 — disarmed-harness sweep · findings and dispositions

- Task: `coordination/tasks/20260810-guards-that-cannot-fail.md` §G5 (owner `local_claude_1`)
- Date: 2026-08-12 · Plan: `docs/superpowers/plans/2026-08-12-g5-disarmed-harnesses.md`
- Scope: places where a check runs and its result is discarded — code AND shell/document
  invocation patterns. Bounded surface: `scripts/`, `cgauto/`, `data/scripts/`, tracked
  `*.sh`, live coordination/handover/plan documents. Analysis-only tools of closed
  experiments are out of scope (they gate nothing); their subprocess hits are listed in
  the appendix untriaged, with this sentence as the recorded reason.

## Findings

| id | site | pattern | class | armed? | disposition |
|---|---|---|---|---|---|
| F1 | invocation habit `lint_outbox \| tail -3 && commit && push` (`HANDOVER-2026-08-10-local_claude_1-session-close.md:131`) | pipeline exits with `tail`'s status | disarmed by invocation | NO | **FIXED (Task 3):** `scripts/publish_outbox.sh` (lint unpiped = the gate) + `.githooks/pre-push` backstop + runbook rule |
| F2 | `claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py:310` `return 0 if control_green else 1` | drive with zero run/compiled mutants exits 0 | verdict discarded | NO | **FIXED (Task 2):** `drive_verdict()` — exit 3 vacuous (no override), exit 4 partial unless `--allow-partial`; G6's D-9(a) drives depend on this |
| F3 | `data/scripts/collect_wide_cron.sh` | `set -uo pipefail`, explicit `status=$?` propagated to exit | — | YES | no action. Recon note: a `head -5`-window scan false-positived it as unarmed — see method notes |
| F4 | session ritual `inbox_sweep.py … \| tail -40` (integrator habit, used again 2026-08-12 this session) | display pipe eats the sweep's exit code | disarmed by invocation | NO | **FIXED (Task 4):** runbook never-pipe rule; page via `cmd > f; echo EXIT=$?; tail f` |
| F5 | `chatgpt_1/banana-solve/run_zero_oscillation_gate.sh` | legacy gate script of the voided banana-r2 closeout; sender unreachable | frozen namespace | n/a | record only — no edits to a peer's dead namespace; the task it served was declared void 2026-08-07 |
| F6 | `coordination/HANDOVER-2026-08-10-control-plane-execution-to-vm.md:42` | live instruction: VM baseline via `pytest … 2>&1 \| tail -3` — same doc says "never pipe a guard" at :99 | disarmed by documented ritual | NO | **FIXED (Task 4):** command rewritten to capture-then-page with explicit `EXIT=$?` |
| F7 | `docs/superpowers/plans/2026-08-10-coordination-control-plane.md:2387` (task-gate step) | full-suite gate piped to `tail -3`; plan still operative for remaining phases (shadow deploy pending) | disarmed by documented ritual | NO | **FIXED (Task 4):** gate line rewritten armed; claude_1 notified in the G5 close message |
| F8 | `scripts/coordctl.py:48` — `git show origin/main:scripts/inbox_sweep.py` result unchecked | on subprocess failure `stdout=b""` → digest mismatch → prints `DRIFT`, exit 2 | fails CLOSED, mislabeled | YES (direction) | **FIXED (Task 4):** returncode checked; unreadable ref now reports `UNREADABLE origin/main` distinctly, still exit 2 |
| F9 | `scripts/check_ref_census.py:29` — dirty-worktree probe result unchecked | a dead/unreadable worktree path silently skips the dirty warning | fails SILENT (advisory path) | NO | **FIXED (Task 4):** probe failure prints a loud `warning: could not inspect worktree …`, census exit unchanged (advisory) |
| F10 | `scripts/check_clock.py:15` | `check=True` present on continuation line | — | YES | no action; line-grep false positive — see method notes |
| F11 | executed historical plans (`2026-07-23-lab-notes-reorg.md:517`, `2026-07-24-data-footprint-cleanup.md:82,308`) with `pytest \| tail` steps | piped gates in already-executed records | historical document | n/a | no action — records of past execution, not live rituals; do not edit history |

## Method notes (why naive scans lie — twice today)

1. A `head -5`-window check for `pipefail` reported the cron wrapper unarmed; the `set
   -uo pipefail` is on line 9. Never scan a fixed prefix window for arming.
2. A line-grep for `subprocess.run…check=True` false-positived `check_clock.py` because
   the `check=True` sits on a continuation line. Multi-line calls defeat line-greps;
   every hit was context-read before classification (the guards task file's own warning:
   its naive bare-`assert` scan was 92% false positive).

## Observed-failing demonstrations

- **F2** — `tests/test_run_mutations_verdict.py`: red run observed (7 failed,
  `AttributeError: drive_verdict` absent) before implementation; 7 passed after. The
  removed defect is stated in the commit.
- **F1 wrapper** — `tests/test_publish_outbox_wrapper.py`: red run observed (3 failed,
  wrapper absent). With the lint shim forced to exit 1 the gate blocks commit AND push
  (asserted against a local bare origin). 3 passed after. Extra defect found by the red
  cycle itself: `git rev-parse --abbrev-ref HEAD` dies on an unborn branch — replaced
  with `symbolic-ref` + explicit detached-HEAD refusal.
- **F1 hook, live demo 2026-08-12** — `install_hooks.sh` set `core.hooksPath`; a
  deliberately invalid outbox file made `bash .githooks/pre-push` exit **2** with
  `errors (1)` (the exact output the original incident printed while the pipeline
  ignored it); after removal, exit **0**. Break → fire → restore, recorded.

## Appendix — sweep commands and raw yield

- (a) subprocess/os.system without same-line `check=True` in `scripts/ cgauto/
  data/scripts/`: 40 hits; triaged: 6 gate-path files context-read (`check_clock`,
  `coordctl`, `check_ref_census`, `coordd` — armed at :320, `inbox_sweep` — armed at
  :147 via captured result consumed by caller, `evidence_git` — armed throughout);
  remainder are analysis tools of closed experiments (out of scope per §Scope).
- (b) pipelines in tracked `*.sh`: 0 hits beyond the two files' internals; both files
  context-read (F3, F5).
- (c) documented rituals piping a gate in `coordination/ docs/`: 15 hits → F1 (narration
  ×4: two handovers, task file, backlog — descriptions of the defect, not instructions),
  F6, F7, F11, and this plan's own quotations.
- (d) `|| true` / bare `except: pass` in harness surface: 0 hits.
- (e) `run_mutations` callers: its docstring, the audit record (pins audit-time
  `runner_sha256 c6924745…` — historical, stays), chatgpt_1's r2 review (recommends
  fresh `--out` runs — compatible with strict exits). No caller depends on exit 0 for
  partial drives.
