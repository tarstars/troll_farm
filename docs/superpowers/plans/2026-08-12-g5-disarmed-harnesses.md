# G5 Disarmed-Harness Sweep and Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every place where a check runs and its result is discarded either gates loudly or is
recorded with a reason it need not — covering shell invocation patterns, not just code
(task: `coordination/tasks/20260810-guards-that-cannot-fail.md` §G5).

**Architecture:** Three structural fixes (run_mutations.py exit semantics; a canonical
publish wrapper whose lint cannot be disarmed by invocation style; a pre-push hook backstop)
plus a swept-and-classified findings report so nothing is silently skipped.

**Tech Stack:** Python 3.10 + pytest (repo suite), bash, git hooks via `core.hooksPath`.

## Global Constraints

- Tooling and tests only. **No bot source, no candidate, no detector predicate change, no gate
  change, no Arena action.** (task §Boundaries)
- `rust/src/bin/yamo_orchard_live.rs` stays byte-exact `fff6669b…`.
- **A new test is not finished until it has been observed failing.** Break the subject, watch it
  fail, restore, state in the commit what you broke. (task §Standing rule)
- `python3 -m pytest tests/ -q` green at the end of the sub-item (full-suite gate runs on
  project_host only — 64 modules read `/home/tarstars/prj/troll_farm/cgauto/cg_session.txt`).
- Never `git add -A` (concurrent agents); stage explicit paths.
- Worktree `/home/tarstars/prj/troll_farm-local_claude_1`, branch `agent/local_claude_1`.
- `claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py` is a cross-namespace edit:
  allowed (G5 explicitly owns instance 5), must be flagged in the closing message. Do NOT
  regenerate any existing `detector-mutation-results` JSON — they pin the old `runner_sha256`
  by design.

---

### Task 1: Sweep and findings report

**Files:**
- Create: `local_claude_1/verification/g5-disarmed-harness-sweep-2026-08-12.md`

**Interfaces:**
- Produces: a numbered findings table later tasks cite by id (F1, F2, …). Columns:
  `id | site | pattern | class | armed? | disposition`.

- [ ] **Step 1: Run the bounded sweep** (each command's full output goes into the report's
  appendix; triage in the table):

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1
# (a) subprocess results possibly discarded, harness surface only
grep -rn "subprocess\.run\|check_output\|subprocess\.call\|os\.system" \
  scripts/ cgauto/ data/scripts/ --include="*.py" | grep -v "check=True"
# (b) pipelines that can eat a gate's exit code, all tracked shell
grep -rnE '\|\s*(tail|head|grep|wc|sed|awk)' --include="*.sh" . --exclude-dir=.git --exclude-dir=target
# (c) documented ritual commands that pipe a gate
grep -rnE '(lint|pytest|sweep|verify|validate)[^|]*\|\s*(tail|head)' \
  --include="*.md" coordination/ docs/ | grep -v "coordination/messages/"
# (d) swallowed failures
grep -rn "|| true\|except:\s*pass\|except Exception:\s*pass" \
  scripts/ cgauto/ data/scripts/ --include="*.py" --include="*.sh"
# (e) verdict-bearing returns nobody reads: call sites of the two known offenders
grep -rn "run_mutations" --include="*.md" --include="*.py" . --exclude-dir=.git | grep -v "\.json"
```

- [ ] **Step 2: Write the report** with the table seeded by the four known rows and every
  triaged hit. Known rows (verified during planning recon 2026-08-12):

```markdown
| id | site | pattern | class | armed? | disposition |
|---|---|---|---|---|---|
| F1 | invocation habit: `lint_outbox \| tail -3 && commit && push` (HANDOVER-2026-08-10:131) | pipeline exit = tail's | disarmed by invocation | NO | Task 3: publish wrapper + pre-push hook + runbook rule |
| F2 | `claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py:310` `return 0 if control_green else 1` | vacuous/partial drive exits 0 | verdict discarded | NO | Task 2: strict exit semantics |
| F3 | `data/scripts/collect_wide_cron.sh` | `set -uo pipefail`, explicit `status=$?` propagation | — | YES | no action; recon head-5 scan false-positived on it — method note: never grep head -N for arming |
| F4 | session ritual `inbox_sweep.py … \| tail -40` (integrator habit, incl. this session) | display pipe eats sweep exit | disarmed by invocation | NO | Task 4: runbook never-pipe rule; page via `> f; tail f` |
| F5 | `chatgpt_1/banana-solve/run_zero_oscillation_gate.sh` | legacy script of a void task, sender unreachable | frozen namespace | n/a | record only; no edits to a peer's dead namespace |
```

  Every additional sweep hit gets a row — disposition `fixed (Task 4)` or
  `accepted: <reason>`. **No hit may be dropped without a row** (no silent caps).

- [ ] **Step 3: Commit**

```bash
git add local_claude_1/verification/g5-disarmed-harness-sweep-2026-08-12.md
git commit -m "G5: disarmed-harness sweep report, findings F1-Fn (report only, fixes follow)"
```

---

### Task 2: run_mutations.py strict exit semantics (fixes F2 / instance 5)

**Files:**
- Modify: `claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py:310` (verdict) and
  its argparse block (new `--allow-partial` flag)
- Test: `tests/test_run_mutations_verdict.py` (new)

**Interfaces:**
- Produces: `drive_verdict(control_green: bool, totals: dict, allow_partial: bool) -> int`
  module-level in `run_mutations.py`; exits: 0 valid drive, 1 control red, 2 preconditions
  (existing), 3 vacuous (zero mutants ran — no flag can allow this), 4 partial
  (patch/compile failures) unless `--allow-partial`.
- G6 depends on this: claude_1's D-9(a) pinning uses this runner; today a drive whose mutants
  all fail to compile still exits 0.

- [ ] **Step 1: Write the failing test**

```python
"""Exit semantics of the bite-test mutation runner (G5 instance 5).

The defect being removed: `return 0 if control_green else 1` — a drive whose
mutants never patched or compiled still reported success.
"""
import importlib.util
import pathlib

RUNNER = (pathlib.Path(__file__).resolve().parents[1]
          / "claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py")
spec = importlib.util.spec_from_file_location("run_mutations_g5", RUNNER)
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)


def _totals(run, patch_failed=0, compile_failed=0):
    return {"mutants_run": run, "patch_failed": patch_failed,
            "compile_failed": compile_failed}


def test_vacuous_drive_zero_mutants_is_exit_3():
    assert rm.drive_verdict(True, _totals(0), allow_partial=False) == 3


def test_vacuous_drive_not_excusable_by_allow_partial():
    assert rm.drive_verdict(True, _totals(0), allow_partial=True) == 3


def test_partial_drive_compile_failures_exit_4_by_default():
    assert rm.drive_verdict(True, _totals(5, compile_failed=2),
                            allow_partial=False) == 4


def test_partial_drive_patch_failures_exit_4_by_default():
    assert rm.drive_verdict(True, _totals(5, patch_failed=1),
                            allow_partial=False) == 4


def test_partial_drive_allowed_with_flag():
    assert rm.drive_verdict(True, _totals(5, patch_failed=1),
                            allow_partial=True) == 0


def test_control_red_is_exit_1_before_anything_else():
    assert rm.drive_verdict(False, _totals(0), allow_partial=False) == 1


def test_clean_full_drive_is_exit_0():
    assert rm.drive_verdict(True, _totals(9), allow_partial=False) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_run_mutations_verdict.py -q`
Expected: FAIL — `AttributeError: module 'run_mutations_g5' has no attribute 'drive_verdict'`
(If instead the import executes a drive: the module lacks a `__main__` guard — add one as
part of this task and note it in the report as an extra finding.)

- [ ] **Step 3: Implement.** In `run_mutations.py`, module level:

```python
def drive_verdict(control_green, totals, allow_partial):
    """Exit status for a drive. 0 only when the drive measured something.

    1 control suite/probe red; 3 vacuous drive (zero mutants ran; never
    excusable); 4 partial drive (patch/compile failures) without
    --allow-partial. Verdicts reflect drive VALIDITY, not kill results —
    surviving mutants are a measurement, not a harness failure.
    """
    if not control_green:
        return 1
    if totals["mutants_run"] == 0:
        return 3
    if (totals["patch_failed"] or totals["compile_failed"]) and not allow_partial:
        return 4
    return 0
```

Argparse block, next to `--allow-drift`:

```python
    parser.add_argument("--allow-partial", action="store_true",
                        help="exit 0 even if some mutants failed to patch or "
                             "compile (they still count as not-run in totals)")
```

Replace the final `return 0 if control_green else 1` with:

```python
    verdict = drive_verdict(control_green, doc["totals"], args.allow_partial)
    if verdict:
        sys.stderr.write(
            "DRIVE INVALID exit=%d: control_green=%s run=%d patch_failed=%d "
            "compile_failed=%d\n" % (
                verdict, control_green, doc["totals"]["mutants_run"],
                doc["totals"]["patch_failed"], doc["totals"]["compile_failed"]))
    return verdict
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_run_mutations_verdict.py -q`
Expected: 7 passed

- [ ] **Step 5: Check no caller depends on the old semantics** — step 1(e)'s sweep output;
  any doc citing "exit 0" for partial drives gets a row + fix in Task 4.

- [ ] **Step 6: Commit**

```bash
git add claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py tests/test_run_mutations_verdict.py
git commit -m "G5/F2: run_mutations exits 3 on vacuous and 4 on partial drives

What was broken for the red run: drive_verdict absent (AttributeError); the
defect removed is 'return 0 if control_green else 1', under which a drive
whose mutants never patched or compiled reported success. Cross-namespace
edit of claude_1's runner under G5 instance-5 ownership; existing result
JSONs keep their pinned old runner_sha256 and are not regenerated."
```

---

### Task 3: Publish wrapper + pre-push hook (fixes F1 / instance 4)

**Files:**
- Create: `scripts/publish_outbox.sh` (mode 755)
- Create: `.githooks/pre-push` (mode 755)
- Create: `scripts/install_hooks.sh` (mode 755)
- Test: `tests/test_publish_outbox_wrapper.py` (new)

**Interfaces:**
- Produces: `scripts/publish_outbox.sh <agent-id> <commit-message>` — lints the staged
  outbox with the lint's own exit code as the gate (never piped), then commit → push →
  remote-verify. `scripts/install_hooks.sh` sets `core.hooksPath .githooks`.

- [ ] **Step 1: Write the failing test**

```python
"""The publish wrapper's lint gate cannot be disarmed by invocation (G5 F1).

The defect being removed lived in how the lint was CALLED:
`lint | tail -3 && commit && push` gated on tail, not the lint. The wrapper
owns the call; these tests prove the gate blocks and that publish works.
"""
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WRAPPER = REPO / "scripts" / "publish_outbox.sh"


def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd,
                          capture_output=True, text=True)


def _setup(tmp_path, lint_exit):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    work = tmp_path / "work"
    work.mkdir()
    for args in (("init", "-q"), ("checkout", "-q", "-b", "agent/testbot"),
                 ("remote", "add", "origin", str(origin)),
                 ("config", "user.email", "t@example.com"),
                 ("config", "user.name", "t")):
        assert _git(*args, cwd=work).returncode == 0
    (work / "scripts").mkdir()
    shutil.copy(WRAPPER, work / "scripts" / "publish_outbox.sh")
    shim = work / "scripts" / "lint_outbox.py"
    shim.write_text("import sys\nsys.stderr.write('shim lint\\n')\n"
                    "sys.exit(%d)\n" % lint_exit)
    (work / "msg.md").write_text("payload\n")
    assert _git("add", "msg.md", "scripts", cwd=work).returncode == 0
    return work


def _run_wrapper(work):
    return subprocess.run(
        ["bash", "scripts/publish_outbox.sh", "testbot", "published by test"],
        cwd=work, capture_output=True, text=True)


def test_lint_failure_blocks_commit_and_push(tmp_path):
    work = _setup(tmp_path, lint_exit=1)
    result = _run_wrapper(work)
    assert result.returncode != 0
    assert _git("log", "-1", cwd=work).returncode != 0  # no commit exists
    ls = _git("ls-remote", "origin", "agent/testbot", cwd=work)
    assert ls.stdout.strip() == ""  # nothing pushed


def test_lint_pass_publishes_and_remote_verifies(tmp_path):
    work = _setup(tmp_path, lint_exit=0)
    result = _run_wrapper(work)
    assert result.returncode == 0, result.stderr
    assert "remote verified" in result.stdout
    ls = _git("ls-remote", "origin", "agent/testbot", cwd=work)
    assert ls.stdout.strip() != ""  # branch exists on origin


def test_wrong_branch_refused(tmp_path):
    work = _setup(tmp_path, lint_exit=0)
    assert _git("checkout", "-q", "-b", "main", cwd=work).returncode == 0
    result = _run_wrapper(work)
    assert result.returncode != 0
    assert "refusing" in result.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_publish_outbox_wrapper.py -q`
Expected: FAIL — `FileNotFoundError` copying the absent `scripts/publish_outbox.sh`

- [ ] **Step 3: Implement `scripts/publish_outbox.sh`**

```bash
#!/usr/bin/env bash
# Canonical outbox publish: lint (armed) -> commit -> push -> remote-verify.
# The lint is NEVER piped; its exit code is the gate. This exists because
# `lint | tail -3 && commit && push` gated on tail for a whole session and
# published an invalid immutable message (guards task, instance 4).
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "usage: publish_outbox.sh <agent-id> <commit-message>" >&2
    exit 2
fi
AGENT="$1"
MSG="$2"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "agent/$AGENT" ]; then
    echo "refusing: on branch '$BRANCH', expected 'agent/$AGENT'" >&2
    exit 2
fi

python3 scripts/lint_outbox.py --me "$AGENT" --staged

git commit -m "$MSG"
git push origin "$BRANCH"
git fetch origin "$BRANCH"
if [ "$(git rev-parse HEAD)" != "$(git rev-parse "origin/$BRANCH")" ]; then
    echo "remote-verify FAILED: origin/$BRANCH != HEAD" >&2
    exit 1
fi
echo "published $(git rev-parse --short HEAD) on $BRANCH — lint armed, remote verified"
```

- [ ] **Step 4: Implement `.githooks/pre-push`** (backstop; wrapper remains canonical)

```bash
#!/usr/bin/env bash
# Pre-push backstop for agent branches: lint the outbox, never piped.
# Bypassable with --no-verify by design; scripts/publish_outbox.sh is the
# canonical path. Installed via scripts/install_hooks.sh (core.hooksPath).
set -euo pipefail
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
case "$BRANCH" in
    agent/*) AGENT="${BRANCH#agent/}" ;;
    *) exit 0 ;;
esac
cd "$(git rev-parse --show-toplevel)"
python3 scripts/lint_outbox.py --me "$AGENT"
```

- [ ] **Step 5: Implement `scripts/install_hooks.sh`**

```bash
#!/usr/bin/env bash
# Point this clone at the tracked hooks. Safe to re-run.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
chmod +x .githooks/* 2>/dev/null || true
git config core.hooksPath .githooks
echo "core.hooksPath -> .githooks ($(git rev-parse --show-toplevel))"
```

- [ ] **Step 6: chmod and run tests**

Run: `chmod +x scripts/publish_outbox.sh .githooks/pre-push scripts/install_hooks.sh && python3 -m pytest tests/test_publish_outbox_wrapper.py -q`
Expected: 3 passed

- [ ] **Step 7: Install the hook in this worktree and observe it fire — locally only.**
  Never push demo branches to the shared origin: peers' sweeps scan
  `refs/remotes/origin/**`, so a throwaway agent branch with an invalid message is
  transport pollution. Instead: run `bash scripts/install_hooks.sh`; then place a
  deliberately schema-invalid message file (`type: bogus`) into the working-tree outbox,
  run `bash .githooks/pre-push` directly — it must exit nonzero with the lint error;
  delete the bad file, run again — exit 0. Record both observations in the report.

- [ ] **Step 8: Commit**

```bash
git add scripts/publish_outbox.sh scripts/install_hooks.sh .githooks/pre-push tests/test_publish_outbox_wrapper.py
git commit -m "G5/F1: canonical publish wrapper + pre-push lint backstop

What was broken for the red run: the wrapper did not exist (FileNotFoundError);
with the lint shim forced to exit 1 the gate blocks commit and push. The
defect removed is invocation-style disarming (lint | tail && push)."
```

---

### Task 4: Ritual documentation + residual findings

**Files:**
- Modify: `coordination/coordd-shadow-runbook.md` (publish ritual + never-pipe rule)
- Modify: `local_claude_1/verification/g5-disarmed-harness-sweep-2026-08-12.md` (final
  dispositions)
- Modify: any Task 1 hits classed `fixed (Task 4)`

- [ ] **Step 1: Runbook entry** (append to the runbook's known-items/ritual section):

```markdown
**Publish ritual (G5, 2026-08-12):** publish outbox messages ONLY via
`scripts/publish_outbox.sh <me> "<msg>"` — it runs the lint unpiped, gates on its exit
code, pushes, and remote-verifies. Never pipe `lint_outbox.py` or `inbox_sweep.py` into
`tail`/`head`/`grep` in a gating position: a pipeline exits with the LAST command's
status, which disarmed the lint for a whole session (guards instance 4). To page long
output: `cmd > /tmp/out; tail /tmp/out` — check `$?` of `cmd` first. Backstop:
`scripts/install_hooks.sh` installs a pre-push lint hook (bypassable with --no-verify;
the wrapper is canonical).
```

- [ ] **Step 2: Fix every remaining Task 1 finding** classed `fixed (Task 4)`, each with its
  own observed-failing demonstration recorded in the report (break subject → see the guard
  fail → restore → note what was broken in the commit).

- [ ] **Step 3: Full suite**

Run: `python3 -m pytest tests/ -q`
Expected: green (≥1679 passed at G1 close, plus the 10 new G5 tests), 0 failed

- [ ] **Step 4: Commit**

```bash
git add coordination/coordd-shadow-runbook.md local_claude_1/verification/g5-disarmed-harness-sweep-2026-08-12.md
git commit -m "G5: publish ritual in runbook; sweep dispositions final; suite green"
```

---

### Task 5: Close G5 through the transport (dogfooding the wrapper)

**Files:**
- Create: `coordination/messages/local_claude_1/<UTC>-20260810-guards-that-cannot-fail-g5-progress.md`
- Modify: `coordination/tasks/20260810-guards-that-cannot-fail.md` (G5 section: DONE line)

- [ ] **Step 1: Update the guards task record** — append under §G5:

```markdown
**✅ DONE 2026-08-12.** Findings F1–Fn in
`local_claude_1/verification/g5-disarmed-harness-sweep-2026-08-12.md`; F2 fix is a
cross-namespace edit of claude_1's mutation runner (strict exits 3/4, `--allow-partial`);
F1 fix is structural (`scripts/publish_outbox.sh` + pre-push backstop). Every fix observed
failing; suite green.
```

- [ ] **Step 2: Write the v2 progress message** (to claude_1+codex_1, cc user;
  requires_ack false; flag the cross-namespace run_mutations edit to claude_1 explicitly
  and note G6's dependency on the new exit semantics; offer codex_1 a review of the
  wrapper since the integrator authored both it and the incident).

- [ ] **Step 3: Publish via the new wrapper itself**

```bash
git add coordination/messages/local_claude_1/<UTC>-20260810-guards-that-cannot-fail-g5-progress.md coordination/tasks/20260810-guards-that-cannot-fail.md
bash scripts/publish_outbox.sh local_claude_1 "G5 done: sweep F1-Fn, strict mutation-drive exits, canonical publish wrapper"
```

Expected: `published <sha> on agent/local_claude_1 — lint armed, remote verified`

---

## Self-Review (done at planning time)

- **Spec coverage:** instance 4 → Tasks 3+4; instance 5 → Task 2; "shell invocation
  patterns, not just code" → Task 1 sweeps docs/rituals, Task 4 fixes the runbook; task
  acceptance (observed failing / no silent deletion / suite green) → per-task steps.
- **Placeholder scan:** none; all code inline.
- **Type consistency:** `drive_verdict(control_green, totals, allow_partial)` used
  identically in Task 2 test and implementation; wrapper name `publish_outbox.sh`
  consistent across Tasks 3/4/5.
- **Known risk:** `run_mutations.py` may lack a `__main__` guard (import would execute a
  drive) — Task 2 Step 2 states the expected failure and the repair if so.
