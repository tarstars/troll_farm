# Coordination Control Plane (P0 + P1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the spec's P0 cleanup (doc diet, stale pointers, three new guards, ack amnesty) and build `coordd`/`coordctl` (P1) ready for shadow mode — per `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md`.

**Architecture:** A single-file stdlib-only HTTP+SQLite service (`scripts/coordd.py`) exposing atomic claims, leases with fencing generations, server-time events/acks, and git-verified handoffs; a thin CLI client (`scripts/coordctl.py`) with a `doctor` aggregating local guards; P0 guards are standalone scripts testable in isolation.

**Tech Stack:** Python 3.10+, stdlib only (`sqlite3`, `http.server`, `urllib`, `subprocess`), pytest (existing suite), git, systemd (deploy artifacts only).

## Global Constraints

- Python for `coordd`/`coordctl`/guards: **stdlib only, no new dependencies** (spec §3).
- Run tests: `.venv/bin/python3 -m pytest <file> -q -p no:randomly` from `/home/tarstars/prj/troll_farm`.
- Work on branch `session-2026-07-01` in `/home/tarstars/prj/troll_farm`. After each task's commit: `git branch -f main HEAD && git push origin session-2026-07-01 main` (Task 6 is the one exception — it publishes on `agent/local_claude_1` from the worktree `/home/tarstars/prj/troll_farm-local_claude_1`).
- Stage **exact paths only** — `git add -A`/`-u` is forbidden (concurrent agents).
- End every commit message with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Never touch: `rust/src/bin/yamo_orchard_live.rs`, `rust/src/d171a_control_resident_snapshot.rs` (byte-sacred, SHA prefix `fff6669b`), `data/raw/games/`, `cgauto/submissions/`, sealed map ranges. Never run formatters over `rust/src/bin/` or `cgauto/`.
- No CI anywhere in this plan (owner ruling 2026-08-10) — all checks are local scripts/tests.
- Task/lease constants (spec §3): lease TTL **900 s**, heartbeat interval 300 s, task states exactly `open|claimed|review|blocked|done|dropped`, default port **7077**, bind `127.0.0.1`.
- Out of scope (follow-up plan after shadow mode): P2 authority switch, the new ≤1-page protocol document (written when it takes force at P2), P3 pre-push hook + `coordctl check` full suite, generated-roster config, retiring the sweep. Pending owner decisions, not tasks: B7 (3 failing pinned-verdict tests), B9 (`data/raw` tracking), e7a 375-vs-586 definition.

---

## Part A — P0 cleanup

### Task 1: Doc-budget test + STATE.md diet

**Files:**
- Test: `tests/test_doc_budgets.py` (create)
- Create: `docs/archive/STATE-2026-08-10-pre-diet.md` (copy of current STATE.md)
- Modify: `docs/STATE.md` (360 lines → ≤150)
- Modify: `docs/archive/INDEX.md` (one pointer line)

**Interfaces:**
- Produces: the budget test that later doc work must keep green; budget constant `STATE_BUDGET = 150`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_doc_budgets.py
"""Doc budgets from docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md §5.
A budget violation is a real failure: STATE.md's own header has declared a 150-line
budget since 2026-07-29 and reached 360 lines with nothing enforcing it."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE_BUDGET = 150

def test_state_md_within_budget():
    lines = (REPO / "docs" / "STATE.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= STATE_BUDGET, (
        f"docs/STATE.md is {len(lines)} lines, budget {STATE_BUDGET}. "
        "Move history to the ledger/archive instead of appending here."
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python3 -m pytest tests/test_doc_budgets.py -q -p no:randomly`
Expected: FAIL with "docs/STATE.md is 360 lines, budget 150"

- [ ] **Step 3: Archive the current file, then rewrite STATE.md within budget**

```bash
cp docs/STATE.md docs/archive/STATE-2026-08-10-pre-diet.md
```

Append to `docs/archive/INDEX.md`:

```markdown
- `STATE-2026-08-10-pre-diet.md` — full 360-line STATE as of the 2026-08-10 doc diet; superseded by the ≤150-line rewrite, no facts were dropped, only history moved here.
```

Rewrite `docs/STATE.md` using the current file (now at the archive path) as source. Exact per-section rules — line numbers refer to the archived copy:

1. **Header (archive lines 1–4):** keep, set `Last updated: 2026-08-10 (doc diet; see docs/archive/STATE-2026-08-10-pre-diet.md for the pre-diet text)`.
2. **§1 Live identity:** keep the banner line 8, the identity table (lines 36–44) verbatim, the PROMOTION-RUNBOOK warning (lines 53–56) verbatim, and condense lines 10–34 to exactly this paragraph:

```markdown
Owner ruled **KEEP** — `6604529`/`41113243` is the resident, restore target `98628e98…`.
Terminal read 160/160: **22.46, rank 35/139**, clean. The same bytes scored 24.76 the
prior run — a 2.30 spread; registry median 23.61. A sub-1.5-point mature delta is
unresolvable at one run per arm (difference SD 1.552, §3). Cycle closed; submitting a
new candidate is unblocked under §3.
Task record: `coordination/tasks/20260812-readable-no-orchard-rerun-arena.md` (its "08-12"
dates are the fabricated-clock session of 2026-08-09; trust `git log`).
```

   Drop lines 58–82 (displaced-resident detail and corpus history) — replace with the two lines: `Displaced: `6594200`/`41090606` (`2caac7c6…`), settled 22.81/32/137, eroded 22.7/35/139.` and `Corpus: 14,930 games / 582 agents / 279 names, 0 parse failures (verified 2026-08-12-labelled session).`
3. **§2 Goal (lines 84–103):** keep verbatim.
4. **§3 Standing rules (lines 105–190):** keep every bullet but compress the noise-band material (lines 119–157) to:

```markdown
- ★★ **OWNER 2026-08-12 (real date 2026-08-09): the noise-band gate is REMOVED.** The ladder
  is an information channel; submissions are the cheap instrument. QUALIFIED-verdict
  correctness bar stands; magnitude bar is gone; runbook in full; owner told before and
  after each cycle; every id and terminal response logged.
- ★ **σ = 1.098** (CI [0.707, 2.418]; 4 families / 10 deployments / 6 d.o.f.;
  `cgauto/arena_noise_band.py`). Difference SD at n=1 per arm = 1.552; SE 0.5 needs
  10 runs/arm (~40 h). Re-submission draws an independent sample (zero duplicate scores
  across 10 deployments). A mature 160-game read takes **~2 h**. Prefer interleaved
  A/B/A/B over blocked runs. Re-run the estimator after every new mature deployment.
```

   Replace the coordination bullet (lines 178–182) with:

```markdown
- **Coordination is migrating to a control plane** — spec
  `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md` (approved
  2026-08-10; no CI this iteration). Until P2 switches authority, the existing protocol
  `coordination/multi-agent-protocol.md` remains in force. Coordinator/integrator/Arena
  controller = `local_claude_1` (owner reassignment 2026-08-06). §7 hazards bind everyone:
  byte-sacred `fff6669b` dev copy, no formatters over hash-locked sources, `data/raw/games/`
  and the 05:17 cron untouchable.
```

5. **§4 Open thread:** replace lines 192–348 entirely with:

```markdown
## 4. Open thread

- **Transport CLEAN 2026-08-10** — delivery errors 0, quarantine errors 0, quarantined 10
  for all three active agents; the half-done self-quarantine was found unpushed and landed
  (`4de33b8c`, trunk `8c01c6ad`).
- **Control-plane migration is the live programme.** Spec approved; plan
  `docs/superpowers/plans/2026-08-10-coordination-control-plane.md` (P0+P1). P2/P3 follow
  shadow-mode verification.
- **Iteration-3 carries (designed, unstarted):** CBF conditional banana farm
  (`docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`; note the strict
  no-banana-before-second-troll rule and D-9(a) UNPINNED status) and D89a
  leak-repairability follow-up (claude_1 returned NOT_REPAIRABLE; review pending).
- **P0 tooling-integrity task** `20260810-guards-that-cannot-fail` (G1–G6; G6 owner-gated).
- **σ task** `20260810-arena-noise-band-measurement` — unowned; Q2–Q4 open; blocked
  ordering cannot separate our variance from ladder drift, only interleaved A/B/A/B can.
- **Needs the owner:** B7 (3 failing pinned-verdict tests), B9 (325 tracked files under
  gitignored `data/raw/`), e7a 375-vs-586 canonical formatting definition, G6 go-ahead.
- History: 2026-07-29 terminal synthesis closed all eight resident levers; A2 stopped at
  Phase-1 K1; N1 closed passive maturity; the full pre-diet record is
  `docs/archive/STATE-2026-08-10-pre-diet.md` and the ledger volumes.
```

6. **§5 Reading order (lines 349–360):** keep verbatim, but replace item 4's
   `coordination/README.md + inbox sweep` line with
   `coordination/README.md + inbox sweep — mandatory until P2; see the control-plane spec.`

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python3 -m pytest tests/test_doc_budgets.py -q -p no:randomly`
Expected: PASS

- [ ] **Step 5: Sanity-check nothing load-bearing vanished**

Run: `grep -c '98628e98\|fff6669b\|25.40\|1.098' docs/STATE.md`
Expected: ≥4 total matches (resident SHA, sacred prefix, goal, σ all still present).

- [ ] **Step 6: Commit**

```bash
git add tests/test_doc_budgets.py docs/STATE.md docs/archive/STATE-2026-08-10-pre-diet.md docs/archive/INDEX.md
git commit -m "docs: STATE diet to <=150 lines, budget enforced by test (P0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 2: Fix the three stale authority documents

**Files:**
- Modify: `AGENTS.md:13-14`
- Modify: `coordination/README.md:35-37` and `coordination/README.md:60-61`
- Modify: `coordination/ENVIRONMENTS.md:1-14`

**Interfaces:**
- Consumes: nothing. Produces: consistent human docs; no code contract.

- [ ] **Step 1: Fix AGENTS.md integrator line**

Replace (at `AGENTS.md:13-14`):

```markdown
- One worktree and `agent/<id>` branch per writing agent; never share a worktree. One
  integrator; one arena controller (both `claude_1` by default).
```

with:

```markdown
- One worktree and `agent/<id>` branch per writing agent; never share a worktree. One
  integrator; one arena controller (both `local_claude_1` since the 2026-08-06 owner
  reassignment — `coordination/roster.json` on `origin/main` is the authority, not this line).
```

- [ ] **Step 2: Fix coordination/README.md handover pointer and the broken fast-check**

Replace (at `coordination/README.md:35-37`):

```markdown
Current handover brief:
[`HANDOVER-2026-08-06-local_codex_1-to-local_claude_1.md`](HANDOVER-2026-08-06-local_codex_1-to-local_claude_1.md).
Prior handovers remain historical evidence.
```

with:

```markdown
Current handover briefs (2026-08-10):
[`HANDOVER-2026-08-10-local_claude_1-session-close.md`](HANDOVER-2026-08-10-local_claude_1-session-close.md)
and [`HANDOVER-2026-08-10-coordination-audit-and-cleanup.md`](HANDOVER-2026-08-10-coordination-audit-and-cleanup.md).
The role-transfer brief is `HANDOVER-2026-08-06-local_codex_1-to-local_claude_1.md`; prior
handovers remain historical evidence. Note: the two files named `2026-08-12` were written
by a fabricated-clock session on 2026-08-09.
```

Replace (at `coordination/README.md:60-61`):

```markdown
# active tasks
grep -l 'Status: active' coordination/tasks/*.md 2>/dev/null
```

with:

```markdown
# tasks NOT marked closed/complete (Status is free text — grep for 'active' finds 2 of ~26
# open records; this inverse filter over-reports slightly, which is the safe direction)
grep -L -iE '^- Status:.*(closed|complete|integrated|superseded)' coordination/tasks/*.md
```

- [ ] **Step 3: Banner + current reality in ENVIRONMENTS.md**

Insert after `coordination/ENVIRONMENTS.md:3` (the "Last updated" line):

```markdown
> ⚠ **STALE TABLE (2026-08-02) — roster changed since.** Current reality, 2026-08-10:
> `local_claude_1` runs on `project_host` (coordinator/integrator/Arena controller);
> **`claude_1` and `codex_1` run on the owner's Yandex Cloud VM** (owner statement
> 2026-08-10) — this VM is the planned host for `coordd`, see
> `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md`;
> `local_codex_1` dormant; `chatgpt_1`/`chatgpt_2` unreachable (owner ruling). The rows
> below are preserved capability evidence for environments that may no longer exist; the
> control plane's `agents` table replaces this file at P2.
```

- [ ] **Step 4: Verify by grep**

Run: `grep -n 'local_claude_1' AGENTS.md | head -2 && grep -n 'Yandex' coordination/ENVIRONMENTS.md && grep -n '2026-08-10' coordination/README.md | head -2`
Expected: each command prints at least one line.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md coordination/README.md coordination/ENVIRONMENTS.md
git commit -m "docs: fix the three stale authority documents (P0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 3: `check_clock.py` — fabricated-date guard

**Files:**
- Create: `scripts/check_clock.py`
- Test: `tests/test_check_clock.py`

**Interfaces:**
- Produces: `python3 scripts/check_clock.py [--repo DIR]` → exit 0 sane, exit 2 if the newest commit across all refs is in the future vs the system clock (>1 h skew). `main(repo, now)` importable for tests, returns the exit code.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_check_clock.py
"""Guard for the fabricated-date hazard: a 2026-08-09 session stamped itself 2026-08-12
across filenames, task ids, and rulings. The one machine-checkable symptom is a commit
dated in the future."""
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_clock


def _mkrepo(tmp_path, author_date):
    repo = tmp_path / "r"
    repo.mkdir()
    def g(*a, **kw):
        env = {"GIT_AUTHOR_DATE": author_date, "GIT_COMMITTER_DATE": author_date,
               "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "HOME": str(tmp_path)}
        return subprocess.run(["git", "-C", str(repo), *a], env=env, check=True,
                              capture_output=True, text=True)
    g("init", "-q")
    (repo / "f").write_text("x")
    g("add", "f")
    g("commit", "-q", "-m", "c")
    return repo


def test_sane_repo_exits_0(tmp_path):
    now = datetime.now(timezone.utc)
    repo = _mkrepo(tmp_path, (now - timedelta(days=1)).isoformat())
    assert check_clock.main(repo=str(repo), now=lambda: now) == 0


def test_future_commit_exits_2(tmp_path):
    now = datetime.now(timezone.utc)
    repo = _mkrepo(tmp_path, (now + timedelta(days=3)).isoformat())
    assert check_clock.main(repo=str(repo), now=lambda: now) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_check_clock.py -q -p no:randomly`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'check_clock'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# scripts/check_clock.py
"""Fail (exit 2) when the newest commit on any ref is more than 1 hour in the future
relative to the system clock. Catches the fabricated-clock session class (a 2026-08-09
session that believed it was 2026-08-12). Run at session start; also part of
`coordctl doctor`."""
import argparse
import subprocess
import sys
from datetime import datetime, timezone

SKEW_LIMIT_S = 3600


def newest_commit_utc(repo):
    out = subprocess.run(
        ["git", "-C", repo, "for-each-ref", "--sort=-committerdate",
         "--count=1", "--format=%(committerdate:iso-strict)"],
        capture_output=True, text=True, check=True).stdout.strip()
    return datetime.fromisoformat(out).astimezone(timezone.utc)


def main(repo=".", now=None):
    now_dt = (now or (lambda: datetime.now(timezone.utc)))()
    newest = newest_commit_utc(repo)
    skew = (newest - now_dt).total_seconds()
    print(f"system now : {now_dt.isoformat()}")
    print(f"newest ref : {newest.isoformat()}")
    if skew > SKEW_LIMIT_S:
        print(f"CLOCK HAZARD: newest commit is {skew/3600:.1f} h in the FUTURE. "
              "Either the system clock is wrong or a session fabricated dates. "
              "Trust `git log`, fix the clock, do not stamp new artifacts until resolved.")
        return 2
    print("clock sane")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=".")
    sys.exit(main(repo=p.parse_args().repo))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_check_clock.py -q -p no:randomly`
Expected: PASS (2 passed)

- [ ] **Step 5: Run against the real repo**

Run: `.venv/bin/python3 scripts/check_clock.py; echo "exit=$?"`
Expected: `clock sane`, `exit=0`

- [ ] **Step 6: Commit**

```bash
git add scripts/check_clock.py tests/test_check_clock.py
git commit -m "guards: check_clock fails on future-dated commits (P0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 4: `check_cron_health.py` — collector watchdog

**Files:**
- Create: `scripts/check_cron_health.py`
- Test: `tests/test_check_cron_health.py`

**Interfaces:**
- Produces: `main(log_path, now, max_age_h=48)` → 0 healthy, 2 if last run failed / log missing / last run older than `max_age_h`. CLI: `python3 scripts/check_cron_health.py [--log data/raw/collect_wide.log]`. Parses the wrapper's end markers by regex `(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*exit=(\d+)` — the last match wins.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_check_cron_health.py
"""The 05:17 collector's last run before 2026-08-10 failed on a TLS timeout (exit=1) and
nothing noticed. This watchdog is the 'noticing'."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_cron_health as cch

NOW = datetime(2026, 8, 10, 12, 0, 0, tzinfo=timezone.utc)


def _write(tmp_path, *lines):
    p = tmp_path / "collect_wide.log"
    p.write_text("\n".join(lines) + "\n")
    return p


def test_recent_success_exits_0(tmp_path):
    p = _write(tmp_path, "start", "2026-08-10T05:20:01Z end exit=0")
    assert cch.main(log_path=p, now=lambda: NOW) == 0


def test_last_run_failed_exits_2(tmp_path):
    p = _write(tmp_path, "2026-08-09T05:20:01Z end exit=0",
               "2026-08-10T02:18:09Z end exit=1")
    assert cch.main(log_path=p, now=lambda: NOW) == 2


def test_stale_log_exits_2(tmp_path):
    p = _write(tmp_path, "2026-08-07T05:20:01Z end exit=0")
    assert cch.main(log_path=p, now=lambda: NOW) == 2


def test_missing_log_exits_2(tmp_path):
    assert cch.main(log_path=tmp_path / "absent.log", now=lambda: NOW) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_check_cron_health.py -q -p no:randomly`
Expected: FAIL/ERROR with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# scripts/check_cron_health.py
"""Exit 2 unless the last 05:17 collector run both finished with exit=0 and is recent.
The collector (data/scripts/collect_wide_cron.sh) appends '<ISO-Z> ... exit=N' markers to
data/raw/collect_wide.log. Read-only; never touches data/raw/games/."""
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MARK = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*exit=(\d+)")


def main(log_path="data/raw/collect_wide.log", now=None, max_age_h=48):
    now_dt = (now or (lambda: datetime.now(timezone.utc)))()
    p = Path(log_path)
    if not p.exists():
        print(f"CRON HAZARD: {p} does not exist"); return 2
    last = None
    for line in p.read_text(errors="replace").splitlines():
        m = MARK.search(line)
        if m:
            last = m
    if last is None:
        print(f"CRON HAZARD: no 'exit=N' marker found in {p}"); return 2
    ts = datetime.strptime(last.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    code = int(last.group(2))
    age_h = (now_dt - ts).total_seconds() / 3600
    print(f"last run: {last.group(1)} exit={code} age={age_h:.1f}h")
    if code != 0:
        print("CRON HAZARD: last collector run FAILED"); return 2
    if age_h > max_age_h:
        print(f"CRON HAZARD: last successful run older than {max_age_h}h"); return 2
    print("cron healthy")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="data/raw/collect_wide.log")
    sys.exit(main(log_path=ap.parse_args().log))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_check_cron_health.py -q -p no:randomly`
Expected: PASS (4 passed)

- [ ] **Step 5: Run against the real log and report honestly**

Run: `.venv/bin/python3 scripts/check_cron_health.py; echo "exit=$?"`
Expected: whatever the truth is — if the collector has not succeeded since the 2026-08-10 TLS failure this prints `CRON HAZARD` with `exit=2`. Record the observed output in the commit message body; do NOT "fix" the guard to make it pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/check_cron_health.py tests/test_check_cron_health.py
git commit -m "guards: collector cron watchdog (P0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 5: `check_ref_census.py` — unpushed-work guard

**Files:**
- Create: `scripts/check_ref_census.py`
- Test: `tests/test_check_ref_census.py`

**Interfaces:**
- Produces: `main(repo, remote="origin")` → 0 when every local branch tip is reachable from some remote ref, 2 otherwise (prints branch and unpushed count); dirty worktrees print a warning without changing the exit code. Session-close guard: it would have flagged the `4de33b8c` unpushed quarantine on 2026-08-10.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_check_ref_census.py
"""'Substantial work reachable from no pushed ref' guard (spec P0). The 2026-08-10
quarantine fix sat committed-but-unpushed on the coordinator's own branch."""
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_ref_census as crc

ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def _g(repo, *a, env_home):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True,
                          text=True, env={**ENV, "HOME": str(env_home)})


def _mkpair(tmp_path):
    """origin (bare) + clone with one pushed commit."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    (clone / "f").write_text("x")
    _g(clone, "add", "f", env_home=tmp_path)
    _g(clone, "commit", "-q", "-m", "c1", env_home=tmp_path)
    _g(clone, "push", "-q", "-u", "origin", "HEAD", env_home=tmp_path)
    return clone


def test_all_pushed_exits_0(tmp_path):
    clone = _mkpair(tmp_path)
    assert crc.main(repo=str(clone)) == 0


def test_unpushed_commit_exits_2(tmp_path, capsys):
    clone = _mkpair(tmp_path)
    (clone / "g").write_text("y")
    _g(clone, "add", "g", env_home=tmp_path)
    _g(clone, "commit", "-q", "-m", "c2-unpushed", env_home=tmp_path)
    assert crc.main(repo=str(clone)) == 2
    assert "unpushed" in capsys.readouterr().out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_check_ref_census.py -q -p no:randomly`
Expected: FAIL/ERROR with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# scripts/check_ref_census.py
"""Session-close guard: exit 2 when any local branch holds commits reachable from no
remote ref ('unpushed = unsent' generalized from messages to work — spec P0). Dirty
worktrees are warned about but do not change the exit code (mid-task state is normal;
an unpushed COMMIT at session close is not)."""
import argparse
import subprocess
import sys


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True)


def main(repo=".", remote="origin"):
    branches = [b for b in
                _git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
                .stdout.split() if b]
    bad = []
    for b in branches:
        n = int(_git(repo, "rev-list", "--count", b, "--not",
                     f"--remotes={remote}").stdout.strip() or "0")
        if n:
            bad.append((b, n))
    for wt in _git(repo, "worktree", "list", "--porcelain").stdout.split("\n\n"):
        path = next((l.split(" ", 1)[1] for l in wt.splitlines()
                     if l.startswith("worktree ")), None)
        if path:
            dirty = subprocess.run(["git", "-C", path, "status", "--porcelain"],
                                   capture_output=True, text=True).stdout.strip()
            if dirty:
                print(f"warning: dirty worktree {path} ({len(dirty.splitlines())} paths)")
    if bad:
        for b, n in bad:
            print(f"UNPUSHED: branch {b} has {n} commit(s) reachable from no {remote} ref")
        print("Push them or archive them as tags before closing the session.")
        return 2
    print(f"ref census clean: {len(branches)} local branches, all reachable from {remote}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--remote", default="origin")
    a = ap.parse_args()
    sys.exit(main(repo=a.repo, remote=a.remote))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_check_ref_census.py -q -p no:randomly`
Expected: PASS (2 passed)

- [ ] **Step 5: Run against the real repo**

Run: `.venv/bin/python3 scripts/check_ref_census.py; echo "exit=$?"`
Expected: exit 0 if this plan's commits have been pushed per the global constraint; if it reports `archive/local_codex_1-stranded-20260810` or similar, verify that branch also exists on origin (`git branch -r --contains <branch>`) before judging — do not delete anything.

- [ ] **Step 6: Commit**

```bash
git add scripts/check_ref_census.py tests/test_check_ref_census.py
git commit -m "guards: ref census fails on unpushed local work (P0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 6: Ack amnesty message (publishes on the agent branch)

**Files:**
- Create: `coordination/messages/local_claude_1/<UTC>-20260810-ack-amnesty-unreachable-policy.md` — in the worktree `/home/tarstars/prj/troll_farm-local_claude_1` (branch `agent/local_claude_1`), NOT the session branch.

**Interfaces:**
- Consumes: current transport rules (`scripts/lint_outbox.py`). Produces: a published policy documenting that the ~80-item unacked backlog from `chatgpt_1`, `chatgpt_2`, `local_codex_1` is administratively closed; sweep exit 1 is expected and documented until P2 retires acks entirely.

- [ ] **Step 1: Create the message in the agent worktree**

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1
git fetch origin && git status --short   # must be clean
TS=$(date -u +%Y%m%dT%H%M%SZ)
F=coordination/messages/local_claude_1/${TS}-20260810-ack-amnesty-unreachable-policy.md
echo "$F"
```

Write `$F` with exactly this content, substituting both `<UTC-STAMP>` occurrences with the `$TS` value and `<ISO>` with `date -u +%Y-%m-%dT%H:%M:%SZ` output:

```markdown
---
schema_version: 2
type: policy
task_id: 20260810-ack-amnesty-unreachable
from: local_claude_1
to: ["user"]
cc: []
message_id: coordination/messages/local_claude_1/<UTC-STAMP>-20260810-ack-amnesty-unreachable-policy.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: <ISO>
---

- To: user
- CC: none
- Task: 20260810-ack-amnesty-unreachable
- Requires acknowledgement: no

# Ack amnesty for unreachable and dormant senders

Owner-approved 2026-08-10 as part of the control-plane spec's P0
(`docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md` §6).

Acknowledgement obligations for messages whose sender is on the roster's `unreachable`
or `dormant` lists (`chatgpt_1`, `chatgpt_2`, `local_codex_1`) are administratively
closed. No acks will be published for them; the messages remain immutable history.
The sweep's `unacknowledged` count and exit 1 are expected and documented until the
ack mechanism retires at migration step P2. No message content is suppressed, deleted,
or quarantined by this policy.
```

- [ ] **Step 2: Lint — as its own command, never piped**

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1
git add "$F"
python3 scripts/lint_outbox.py --me local_claude_1 --fetch --staged
echo "lint exit=$?"
```

Expected: `errors (0):`, `lint exit=0`. If nonzero: fix the message, re-stage, re-lint. Do not proceed on nonzero.

- [ ] **Step 3: Commit and push on the canonical branch**

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1
git commit -m "policy: ack amnesty for unreachable/dormant senders (P0)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push origin agent/local_claude_1
```

- [ ] **Step 4: Verify delivery state unchanged for peers**

```bash
cd /home/tarstars/prj/troll_farm
OUT=$(mktemp)
python3 scripts/inbox_sweep.py --me claude_1 --fetch > "$OUT" 2>&1; echo "exit=$?"
grep -E 'delivery errors|quarantine errors' "$OUT"
```

Expected: `exit=1` (not 2), `delivery errors (0)`, `quarantine errors (0)` — the policy adds no unacked burden to any agent because `to` is `["user"]` and `requires_ack: false` on a `policy` kind is overridden by the kind (known `requires_ack()` OR behavior), but "user" runs no sweep; confirm no agent's count grew by re-running `--me codex_1` similarly.

### Task 7: coordd Store — schema and initialization

**Files:**
- Create: `scripts/coordd.py`
- Test: `tests/test_coordd_store.py` (grows over Tasks 7–12)

**Interfaces:**
- Produces (used by every later task): `class Store(db_path, repo_dir=None, now=None)` in `scripts/coordd.py`; `Store.PROTOCOL_VERSION = 1`; `Store.LEASE_TTL = 900`; exceptions `CoordError(msg)` (`.status = 400`), `Denied` (403), `Conflict` (409), `NotFound` (404), `Unverifiable` (422); `store._now_iso()` returns `YYYY-MM-DDTHH:MM:SS.ffffffZ` strings (lexicographically ordered); injectable `now` is a zero-arg callable returning an aware UTC `datetime`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_coordd_store.py
"""Store-level semantics for coordd — the eight guarantees of spec §3, each testable."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd


def mkstore(tmp_path, **kw):
    return coordd.Store(db_path=str(tmp_path / "c.sqlite3"), **kw)


def test_init_creates_schema_in_wal_mode(tmp_path):
    store = mkstore(tmp_path)
    con = sqlite3.connect(store.db_path)
    tables = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"agents", "tasks", "task_paths", "leases", "events", "acks",
            "artifacts", "reviews", "meta"} <= tables
    assert con.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    con.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'coordd'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# scripts/coordd.py
"""coordd — coordination control plane (spec: docs/superpowers/specs/
2026-08-10-coordination-control-plane-design.md). Single file, stdlib only.
Store = all semantics over SQLite (WAL). HTTP layer and CLI modes are added in
later tasks of the same plan; keep them thin — semantics live here so they are
testable without a socket."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import sqlite3

TASK_STATES = ("open", "claimed", "review", "blocked", "done", "dropped")

SCHEMA = """
CREATE TABLE IF NOT EXISTS agents(
  id TEXT PRIMARY KEY, role TEXT NOT NULL DEFAULT 'contributor',
  tool_digest TEXT, protocol_version INTEGER NOT NULL,
  capabilities TEXT NOT NULL DEFAULT '[]', last_seen TEXT NOT NULL,
  compatible INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(
  id TEXT PRIMARY KEY, title TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN
    ('open','claimed','review','blocked','done','dropped')),
  priority INTEGER NOT NULL DEFAULT 2, owner TEXT,
  created TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS task_paths(
  task_id TEXT NOT NULL, prefix TEXT NOT NULL, PRIMARY KEY(task_id, prefix));
CREATE TABLE IF NOT EXISTS leases(
  task_id TEXT PRIMARY KEY, owner TEXT NOT NULL, generation INTEGER NOT NULL,
  expires TEXT NOT NULL, last_heartbeat TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(
  seq INTEGER PRIMARY KEY AUTOINCREMENT, server_time TEXT NOT NULL,
  type TEXT NOT NULL, actor TEXT NOT NULL, task_id TEXT,
  payload TEXT NOT NULL DEFAULT '{}', idempotency_key TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS acks(
  event_seq INTEGER NOT NULL, agent TEXT NOT NULL, server_time TEXT NOT NULL,
  PRIMARY KEY(event_seq, agent));
CREATE TABLE IF NOT EXISTS artifacts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
  generation INTEGER NOT NULL, git_ref TEXT NOT NULL, commit_hex TEXT NOT NULL,
  paths TEXT NOT NULL, verified INTEGER NOT NULL, server_time TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reviews(
  id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
  reviewer TEXT NOT NULL, verdict TEXT NOT NULL, evidence TEXT,
  artifact_generation INTEGER, server_time TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


class CoordError(Exception):
    status = 400


class Denied(CoordError):
    status = 403


class NotFound(CoordError):
    status = 404


class Conflict(CoordError):
    status = 409


class Unverifiable(CoordError):
    status = 422


class Store:
    PROTOCOL_VERSION = 1
    LEASE_TTL = 900  # seconds; spec §3: 15-minute lease

    def __init__(self, db_path, repo_dir=None, now=None):
        self.db_path = db_path
        self.repo_dir = repo_dir
        self._now = now or (lambda: datetime.now(timezone.utc))
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript(SCHEMA)
        con.commit()
        con.close()

    def _now_iso(self):
        return self._now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @contextmanager
    def _tx(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.execute("PRAGMA busy_timeout=10000")
        try:
            con.execute("BEGIN IMMEDIATE")
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def _read(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        return con
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_store.py
git commit -m "coordd: Store schema and init, SQLite WAL (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 8: Agent registration and the compatibility gate

**Files:**
- Modify: `scripts/coordd.py` (add `Store.register`)
- Test: `tests/test_coordd_store.py` (append)

**Interfaces:**
- Produces: `store.register(agent, role="contributor", tool_digest=None, protocol_version=1, capabilities=()) -> {"agent": str, "compatible": bool}`. Incompatible agents exist in the table but are refused claims (checked in Task 9).

- [ ] **Step 1: Write the failing tests** (append to `tests/test_coordd_store.py`)

```python
def test_register_compatible_and_incompatible(tmp_path):
    store = mkstore(tmp_path)
    ok = store.register("claude_1", role="contributor", tool_digest="abc",
                        protocol_version=coordd.Store.PROTOCOL_VERSION)
    assert ok == {"agent": "claude_1", "compatible": True}
    old = store.register("chatgpt_1", protocol_version=0)
    assert old["compatible"] is False


def test_register_is_upsert(tmp_path):
    store = mkstore(tmp_path)
    store.register("claude_1", protocol_version=0)
    assert store.register("claude_1", protocol_version=1)["compatible"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: 2 new FAILs with `AttributeError: 'Store' object has no attribute 'register'`

- [ ] **Step 3: Implement** (add to `Store`)

```python
    def register(self, agent, role="contributor", tool_digest=None,
                 protocol_version=1, capabilities=()):
        compatible = int(protocol_version == self.PROTOCOL_VERSION)
        with self._tx() as con:
            con.execute(
                "INSERT INTO agents(id, role, tool_digest, protocol_version,"
                " capabilities, last_seen, compatible)"
                " VALUES(?,?,?,?,?,?,?)"
                " ON CONFLICT(id) DO UPDATE SET role=excluded.role,"
                " tool_digest=excluded.tool_digest,"
                " protocol_version=excluded.protocol_version,"
                " capabilities=excluded.capabilities,"
                " last_seen=excluded.last_seen, compatible=excluded.compatible",
                (agent, role, tool_digest, protocol_version,
                 json.dumps(list(capabilities)), self._now_iso(), compatible))
        return {"agent": agent, "compatible": bool(compatible)}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_store.py
git commit -m "coordd: agent registration with compatibility gate (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 9: Tasks, atomic claim, write-set overlap, 20-thread race

**Files:**
- Modify: `scripts/coordd.py` (add `create_task`, `set_state`, `tasks`, `claim`, `_active_lease`, `_overlap`)
- Test: `tests/test_coordd_store.py` (append)

**Interfaces:**
- Produces: `store.create_task(task_id, title, priority=2)`; `store.set_state(task_id, state, actor)` (validates enum); `store.tasks(state=None) -> list[dict]`; `store.claim(agent, task_id, prefixes, idempotency_key=None) -> {"task_id", "generation": int, "expires": str}` raising `Denied` (unregistered/incompatible), `NotFound` (no task), `Conflict` (live lease held by другой agent, or write-set overlap with another active lease). Prefix overlap rule: `a.startswith(b) or b.startswith(a)`.

- [ ] **Step 1: Write the failing tests** (append)

```python
import threading


def _reg(store, *agents):
    for a in agents:
        store.register(a, protocol_version=coordd.Store.PROTOCOL_VERSION)


def test_claim_requires_registered_compatible_agent_and_task(tmp_path):
    store = mkstore(tmp_path)
    store.create_task("t1", "demo")
    import pytest
    with pytest.raises(coordd.Denied):
        store.claim("ghost", "t1", ["docs/"])
    store.register("old", protocol_version=0)
    with pytest.raises(coordd.Denied):
        store.claim("old", "t1", ["docs/"])
    _reg(store, "a1")
    with pytest.raises(coordd.NotFound):
        store.claim("a1", "missing", ["docs/"])


def test_claim_sets_owner_state_generation(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    got = store.claim("a1", "t1", ["rust/src/bin/x.rs"])
    assert got["generation"] == 1
    task = store.tasks(state="claimed")[0]
    assert (task["id"], task["owner"]) == ("t1", "a1")


def test_second_claim_conflicts_and_overlap_blocks(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    _reg(store, "a1", "a2")
    store.create_task("t1", "demo")
    store.create_task("t2", "demo2")
    store.claim("a1", "t1", ["docs/reports/"])
    with pytest.raises(coordd.Conflict):
        store.claim("a2", "t1", ["docs/reports/"])          # same task
    with pytest.raises(coordd.Conflict):
        store.claim("a2", "t2", ["docs/"])                  # prefix overlap
    store.claim("a2", "t2", ["cgauto/"])                    # disjoint proceeds


def test_twenty_simultaneous_claims_one_owner(tmp_path):
    store = mkstore(tmp_path)
    agents = [f"a{i}" for i in range(20)]
    _reg(store, *agents)
    store.create_task("t1", "contested")
    wins, errs = [], []

    def worker(name):
        try:
            wins.append((name, store.claim(name, "t1", ["docs/x"])["generation"]))
        except coordd.Conflict:
            errs.append(name)

    threads = [threading.Thread(target=worker, args=(a,)) for a in agents]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(wins) == 1 and len(errs) == 19
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: new FAILs with `AttributeError: ... 'create_task'`

- [ ] **Step 3: Implement** (add to `Store`)

```python
    def create_task(self, task_id, title, priority=2):
        now = self._now_iso()
        with self._tx() as con:
            con.execute(
                "INSERT INTO tasks(id, title, state, priority, created, updated)"
                " VALUES(?,?,?,?,?,?)",
                (task_id, title, "open", priority, now, now))
        return {"task_id": task_id, "state": "open"}

    def set_state(self, task_id, state, actor):
        if state not in TASK_STATES:
            raise CoordError(f"unknown state {state!r}; allowed: {TASK_STATES}")
        with self._tx() as con:
            cur = con.execute("UPDATE tasks SET state=?, updated=? WHERE id=?",
                              (state, self._now_iso(), task_id))
            if cur.rowcount == 0:
                raise NotFound(f"no task {task_id!r}")
            self._event(con, "state", actor, task_id, {"state": state})
        return {"task_id": task_id, "state": state}

    def tasks(self, state=None):
        con = self._read()
        try:
            q = "SELECT * FROM tasks" + (" WHERE state=?" if state else "")
            rows = con.execute(q, (state,) if state else ()).fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()

    @staticmethod
    def _overlap(a, b):
        return a.startswith(b) or b.startswith(a)

    def _require_agent(self, con, agent):
        row = con.execute("SELECT compatible FROM agents WHERE id=?",
                          (agent,)).fetchone()
        if row is None or not row[0]:
            raise Denied(f"agent {agent!r} not registered as compatible"
                         f" (protocol {self.PROTOCOL_VERSION} required)")

    def claim(self, agent, task_id, prefixes, idempotency_key=None):
        if not prefixes:
            raise CoordError("a claim must declare at least one write-set prefix")
        now = self._now_iso()
        with self._tx() as con:
            self._require_agent(con, agent)
            trow = con.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone()
            if trow is None:
                raise NotFound(f"no task {task_id!r}")
            lease = con.execute(
                "SELECT owner, generation, expires FROM leases WHERE task_id=?",
                (task_id,)).fetchone()
            if lease and lease[2] > now and lease[0] != agent:
                raise Conflict(f"task {task_id!r} owned by {lease[0]}"
                               f" until {lease[2]} (gen {lease[1]})")
            for other_task, prefix in con.execute(
                    "SELECT l.task_id, tp.prefix FROM leases l"
                    " JOIN task_paths tp ON tp.task_id = l.task_id"
                    " WHERE l.task_id != ? AND l.expires > ?", (task_id, now)):
                if any(self._overlap(p, prefix) for p in prefixes):
                    raise Conflict(f"write-set overlap: {prefix!r} held by"
                                   f" active task {other_task!r}")
            gen = (lease[1] + 1) if lease else 1
            expires = (self._now() + timedelta(seconds=self.LEASE_TTL)) \
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            con.execute("INSERT OR REPLACE INTO leases VALUES(?,?,?,?,?)",
                        (task_id, agent, gen, expires, now))
            con.execute("DELETE FROM task_paths WHERE task_id=?", (task_id,))
            con.executemany("INSERT INTO task_paths VALUES(?,?)",
                            [(task_id, p) for p in prefixes])
            con.execute("UPDATE tasks SET state='claimed', owner=?, updated=?"
                        " WHERE id=?", (agent, now, task_id))
            self._event(con, "claim", agent, task_id,
                        {"generation": gen, "prefixes": list(prefixes)},
                        idempotency_key)
        return {"task_id": task_id, "generation": gen, "expires": expires}

    def _event(self, con, type_, actor, task_id, payload, idempotency_key=None):
        try:
            cur = con.execute(
                "INSERT INTO events(server_time, type, actor, task_id, payload,"
                " idempotency_key) VALUES(?,?,?,?,?,?)",
                (self._now_iso(), type_, actor, task_id,
                 json.dumps(payload or {}), idempotency_key))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            row = con.execute("SELECT seq FROM events WHERE idempotency_key=?",
                              (idempotency_key,)).fetchone()
            return row[0]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: PASS (7 passed) — the 20-thread race must report exactly 1 win / 19 conflicts.

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_store.py
git commit -m "coordd: tasks, atomic claim, write-set overlap; 20-way race passes (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 10: Leases — heartbeat, expiry, takeover, fencing

**Files:**
- Modify: `scripts/coordd.py` (add `heartbeat`, `release`, `_require_lease`)
- Test: `tests/test_coordd_store.py` (append)

**Interfaces:**
- Produces: `store.heartbeat(agent, task_id, generation) -> {"expires": str}`; `store.release(agent, task_id, generation, outcome)` with `outcome ∈ {"open","review","blocked","done","dropped"}` → clears the lease and sets task state; both raise `Conflict` on wrong owner, stale generation, or expired lease. Takeover = a fresh `claim` after expiry bumps the generation; the superseded owner's calls then fail.

- [ ] **Step 1: Write the failing tests** (append)

```python
from datetime import timedelta


class Clock:
    def __init__(self):
        self.t = datetime(2026, 8, 10, 12, 0, 0, tzinfo=timezone.utc)
    def __call__(self):
        return self.t
    def advance(self, seconds):
        self.t += timedelta(seconds=seconds)


def test_heartbeat_extends_and_fences(tmp_path):
    import pytest
    clock = Clock()
    store = mkstore(tmp_path, now=clock)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    gen = store.claim("a1", "t1", ["docs/x"])["generation"]
    clock.advance(600)
    exp1 = store.heartbeat("a1", "t1", gen)["expires"]
    assert exp1 > clock().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    with pytest.raises(coordd.Conflict):
        store.heartbeat("a1", "t1", gen + 5)      # stale/foreign generation
    with pytest.raises(coordd.Conflict):
        store.heartbeat("a2", "t1", gen)          # not the owner


def test_expired_lease_takeover_rejects_stale_owner(tmp_path):
    import pytest
    clock = Clock()
    store = mkstore(tmp_path, now=clock)
    _reg(store, "a1", "a2")
    store.create_task("t1", "demo")
    g1 = store.claim("a1", "t1", ["docs/x"])["generation"]
    clock.advance(coordd.Store.LEASE_TTL + 1)
    g2 = store.claim("a2", "t1", ["docs/x"])["generation"]   # takeover
    assert g2 == g1 + 1
    with pytest.raises(coordd.Conflict):
        store.heartbeat("a1", "t1", g1)                       # fenced out
    with pytest.raises(coordd.Conflict):
        store.release("a1", "t1", g1, "done")                 # fenced out


def test_release_clears_lease_and_sets_state(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    gen = store.claim("a1", "t1", ["docs/x"])["generation"]
    with pytest.raises(coordd.CoordError):
        store.release("a1", "t1", gen, "claimed")             # invalid outcome
    store.release("a1", "t1", gen, "review")
    assert store.tasks(state="review")[0]["id"] == "t1"
    _reg(store, "a2")
    store.claim("a2", "t1", ["docs/x"])                       # lease is free again
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: new FAILs with `AttributeError: ... 'heartbeat'`

- [ ] **Step 3: Implement** (add to `Store`)

```python
    RELEASE_OUTCOMES = ("open", "review", "blocked", "done", "dropped")

    def _require_lease(self, con, agent, task_id, generation):
        row = con.execute(
            "SELECT owner, generation, expires FROM leases WHERE task_id=?",
            (task_id,)).fetchone()
        if row is None:
            raise Conflict(f"no lease on {task_id!r}")
        owner, gen, expires = row
        if owner != agent or gen != generation:
            raise Conflict(f"stale generation for {task_id!r}: lease is"
                           f" {owner}@gen{gen}, caller {agent}@gen{generation}")
        if expires <= self._now_iso():
            raise Conflict(f"lease on {task_id!r} expired at {expires}")

    def heartbeat(self, agent, task_id, generation):
        now = self._now_iso()
        with self._tx() as con:
            self._require_lease(con, agent, task_id, generation)
            expires = (self._now() + timedelta(seconds=self.LEASE_TTL)) \
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            con.execute("UPDATE leases SET expires=?, last_heartbeat=?"
                        " WHERE task_id=?", (expires, now, task_id))
        return {"expires": expires}

    def release(self, agent, task_id, generation, outcome):
        if outcome not in self.RELEASE_OUTCOMES:
            raise CoordError(f"outcome {outcome!r} not in {self.RELEASE_OUTCOMES}")
        with self._tx() as con:
            self._require_lease(con, agent, task_id, generation)
            con.execute("DELETE FROM leases WHERE task_id=?", (task_id,))
            owner = None if outcome in ("open", "dropped") else agent
            con.execute("UPDATE tasks SET state=?, owner=?, updated=? WHERE id=?",
                        (outcome, owner, self._now_iso(), task_id))
            self._event(con, "release", agent, task_id,
                        {"generation": generation, "outcome": outcome})
        return {"task_id": task_id, "state": outcome}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: PASS (10 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_store.py
git commit -m "coordd: leases with heartbeat, expiry takeover, fencing (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 11: Events, idempotency, acks, reviews

**Files:**
- Modify: `scripts/coordd.py` (add `add_event`, `events`, `ack`, `add_review`, `reviews`)
- Test: `tests/test_coordd_store.py` (append)

**Interfaces:**
- Produces: `store.add_event(actor, type_, task_id=None, payload=None, idempotency_key=None) -> {"seq": int}` (same key → same seq, no duplicate row); `store.events(since=0) -> list[dict]` ordered by seq; `store.ack(agent, event_seq) -> {"ok": True}` (duplicate ack harmless; unknown seq → `NotFound`); `store.add_review(task_id, reviewer, verdict, evidence=None, artifact_generation=None)`; `store.reviews(task_id) -> list[dict]`.

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_event_idempotency_and_order(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    s1 = store.add_event("a1", "note", payload={"n": 1}, idempotency_key="k1")["seq"]
    s2 = store.add_event("a1", "note", payload={"n": 1}, idempotency_key="k1")["seq"]
    s3 = store.add_event("a1", "note", payload={"n": 2})["seq"]
    assert s1 == s2 and s3 > s1
    seqs = [e["seq"] for e in store.events(since=0)]
    assert seqs == sorted(seqs) and len([e for e in store.events()
                                         if e["type"] == "note"]) == 2


def test_ack_exact_and_duplicate_harmless(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    _reg(store, "a1", "a2")
    seq = store.add_event("a1", "question", payload={})["seq"]
    assert store.ack("a2", seq) == {"ok": True}
    assert store.ack("a2", seq) == {"ok": True}
    with pytest.raises(coordd.NotFound):
        store.ack("a2", 99999)


def test_reviews_roundtrip(tmp_path):
    store = mkstore(tmp_path)
    store.create_task("t1", "demo")
    store.add_review("t1", "codex_1", "REVISION_REQUIRED",
                     evidence="claude_1/x.md", artifact_generation=2)
    got = store.reviews("t1")
    assert got[0]["verdict"] == "REVISION_REQUIRED" and got[0]["reviewer"] == "codex_1"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: new FAILs with `AttributeError: ... 'add_event'`

- [ ] **Step 3: Implement** (add to `Store`)

```python
    def add_event(self, actor, type_, task_id=None, payload=None,
                  idempotency_key=None):
        with self._tx() as con:
            seq = self._event(con, type_, actor, task_id, payload, idempotency_key)
        return {"seq": seq}

    def events(self, since=0):
        con = self._read()
        try:
            rows = con.execute(
                "SELECT * FROM events WHERE seq > ? ORDER BY seq", (since,)).fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["payload"] = json.loads(d["payload"])
                out.append(d)
            return out
        finally:
            con.close()

    def ack(self, agent, event_seq):
        with self._tx() as con:
            if con.execute("SELECT 1 FROM events WHERE seq=?",
                           (event_seq,)).fetchone() is None:
                raise NotFound(f"no event {event_seq}")
            con.execute("INSERT OR IGNORE INTO acks VALUES(?,?,?)",
                        (event_seq, agent, self._now_iso()))
        return {"ok": True}

    def add_review(self, task_id, reviewer, verdict, evidence=None,
                   artifact_generation=None):
        with self._tx() as con:
            con.execute(
                "INSERT INTO reviews(task_id, reviewer, verdict, evidence,"
                " artifact_generation, server_time) VALUES(?,?,?,?,?,?)",
                (task_id, reviewer, verdict, evidence, artifact_generation,
                 self._now_iso()))
            self._event(con, "review", reviewer, task_id, {"verdict": verdict})
        return {"ok": True}

    def reviews(self, task_id):
        con = self._read()
        try:
            return [dict(r) for r in con.execute(
                "SELECT * FROM reviews WHERE task_id=? ORDER BY id", (task_id,))]
        finally:
            con.close()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py -q -p no:randomly`
Expected: PASS (13 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_store.py
git commit -m "coordd: events with idempotency, exact acks, reviews (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 12: Handoff artifact validation against git

**Files:**
- Modify: `scripts/coordd.py` (add `register_handoff`, `_git_ok`)
- Test: `tests/test_coordd_git.py` (create)

**Interfaces:**
- Produces: `store.register_handoff(agent, task_id, generation, git_ref, commit_hex, paths) -> {"verified": True, "artifact_id": int}`; raises `Unverifiable` (422) when the commit is missing, not reachable from `git_ref`, or any path is absent at that commit; raises `CoordError` when `repo_dir` is unset. Ref resolution order: `refs/remotes/origin/<ref>` then `<ref>` (supports both a fetched clone and a `--mirror` clone). Runs `git fetch --all --prune --quiet` first when `origin` exists; verification failure records no artifact row.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_coordd_git.py
"""Spec §3 guarantee 6: a handoff must name a reachable commit and existing paths —
the one strict validation carried over from transport v2."""
import subprocess
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd

ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    def g(*a):
        return subprocess.run(["git", "-C", str(r), *a], check=True,
                              capture_output=True, text=True,
                              env={**ENV, "HOME": str(tmp_path)})
    g("init", "-q", "-b", "agent/a1")
    (r / "result.md").write_text("evidence")
    g("add", "result.md")
    g("commit", "-q", "-m", "work")
    commit = g("rev-parse", "HEAD").stdout.strip()
    return r, commit


def _store(tmp_path, repo_dir):
    s = coordd.Store(db_path=str(tmp_path / "c.sqlite3"), repo_dir=str(repo_dir))
    s.register("a1", protocol_version=coordd.Store.PROTOCOL_VERSION)
    s.create_task("t1", "demo")
    return s, s.claim("a1", "t1", ["result.md"])["generation"]


def test_valid_handoff_verifies(tmp_path, repo):
    rdir, commit = repo
    store, gen = _store(tmp_path, rdir)
    got = store.register_handoff("a1", "t1", gen, "agent/a1", commit, ["result.md"])
    assert got["verified"] is True


def test_missing_path_and_bad_commit_rejected(tmp_path, repo):
    rdir, commit = repo
    store, gen = _store(tmp_path, rdir)
    with pytest.raises(coordd.Unverifiable):
        store.register_handoff("a1", "t1", gen, "agent/a1", commit, ["absent.md"])
    with pytest.raises(coordd.Unverifiable):
        store.register_handoff("a1", "t1", gen, "agent/a1", "f" * 40, ["result.md"])
    con = coordd.sqlite3.connect(store.db_path)
    assert con.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_git.py -q -p no:randomly`
Expected: FAIL with `AttributeError: ... 'register_handoff'`

- [ ] **Step 3: Implement** (add to `Store`, plus `import subprocess` at the top of the file)

```python
    def _git_ok(self, *args):
        r = subprocess.run(["git", "-C", self.repo_dir, *args],
                           capture_output=True, text=True)
        return r.returncode == 0

    def register_handoff(self, agent, task_id, generation, git_ref, commit_hex,
                         paths):
        if not self.repo_dir:
            raise CoordError("server has no repo_dir configured for verification")
        if self._git_ok("remote", "get-url", "origin"):
            subprocess.run(["git", "-C", self.repo_dir, "fetch", "--all",
                            "--prune", "--quiet"], capture_output=True)
        if not self._git_ok("cat-file", "-e", f"{commit_hex}^{{commit}}"):
            raise Unverifiable(f"commit {commit_hex} not present")
        full_ref = next(
            (r for r in (f"refs/remotes/origin/{git_ref}", git_ref)
             if self._git_ok("rev-parse", "--verify", "--quiet", r)), None)
        if full_ref is None:
            raise Unverifiable(f"ref {git_ref!r} not found")
        if not self._git_ok("merge-base", "--is-ancestor", commit_hex, full_ref):
            raise Unverifiable(f"{commit_hex} not reachable from {full_ref}")
        missing = [p for p in paths
                   if not self._git_ok("cat-file", "-e", f"{commit_hex}:{p}")]
        if missing:
            raise Unverifiable(f"paths absent at {commit_hex[:12]}: {missing}")
        with self._tx() as con:
            self._require_lease(con, agent, task_id, generation)
            cur = con.execute(
                "INSERT INTO artifacts(task_id, generation, git_ref, commit_hex,"
                " paths, verified, server_time) VALUES(?,?,?,?,?,1,?)",
                (task_id, generation, git_ref, commit_hex, json.dumps(list(paths)),
                 self._now_iso()))
            self._event(con, "handoff", agent, task_id,
                        {"commit": commit_hex, "paths": list(paths),
                         "generation": generation})
            return {"verified": True, "artifact_id": cur.lastrowid}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_git.py tests/test_coordd_store.py -q -p no:randomly`
Expected: PASS (15 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_git.py
git commit -m "coordd: git-verified handoffs, reject unreachable/missing (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 13: HTTP layer with bearer-token auth

**Files:**
- Modify: `scripts/coordd.py` (add `make_server`, `Handler`, `serve` CLI mode)
- Test: `tests/test_coordd_http.py` (create)

**Interfaces:**
- Produces: `coordd.make_server(store, token, host="127.0.0.1", port=0) -> ThreadingHTTPServer` (port 0 = ephemeral, actual port at `srv.server_address[1]`); JSON POST endpoints `/register /claim /heartbeat /release /task /task_state /event /ack /handoff /review` mapping 1:1 to Store methods (`/task` → `create_task`, `/task_state` → `set_state`); GET `/health` → `{"ok": true, "time": ...}` (no auth), `/tasks?state=`, `/events?since=`, `/reviews?task_id=` (auth). Auth: `Authorization: Bearer <token>` else 401. `CoordError` subclasses map to their `.status`; body `{"error": str}`. CLI: `python3 scripts/coordd.py serve --db PATH --repo DIR --token-file FILE --port 7077`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_coordd_http.py
import json
import threading
import urllib.request
import urllib.error
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd


@pytest.fixture
def server(tmp_path):
    store = coordd.Store(db_path=str(tmp_path / "c.sqlite3"))
    srv = coordd.make_server(store, token="sekret", port=0)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _call(base, path, payload=None, token="sekret"):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_health_needs_no_token(server):
    assert _call(server, "/health", token=None)["ok"] is True


def test_bad_token_401(server):
    with pytest.raises(urllib.error.HTTPError) as e:
        _call(server, "/tasks", token="wrong")
    assert e.value.code == 401


def test_register_claim_conflict_flow(server):
    _call(server, "/register", {"agent": "a1", "protocol_version": 1})
    _call(server, "/register", {"agent": "a2", "protocol_version": 1})
    _call(server, "/task", {"task_id": "t1", "title": "demo"})
    got = _call(server, "/claim", {"agent": "a1", "task_id": "t1",
                                   "prefixes": ["docs/x"]})
    assert got["generation"] == 1
    with pytest.raises(urllib.error.HTTPError) as e:
        _call(server, "/claim", {"agent": "a2", "task_id": "t1",
                                 "prefixes": ["docs/x"]})
    assert e.value.code == 409
    assert _call(server, "/tasks?state=claimed")[0]["id"] == "t1"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_http.py -q -p no:randomly`
Expected: FAIL with `AttributeError: module 'coordd' has no attribute 'make_server'`

- [ ] **Step 3: Implement** (add to `scripts/coordd.py`; new imports: `argparse`, `sys`, `from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer`, `from urllib.parse import urlparse, parse_qs`)

```python
POST_ROUTES = {
    "/register": ("register", ["agent"], ["role", "tool_digest",
                                          "protocol_version", "capabilities"]),
    "/task": ("create_task", ["task_id", "title"], ["priority"]),
    "/task_state": ("set_state", ["task_id", "state", "actor"], []),
    "/claim": ("claim", ["agent", "task_id", "prefixes"], ["idempotency_key"]),
    "/heartbeat": ("heartbeat", ["agent", "task_id", "generation"], []),
    "/release": ("release", ["agent", "task_id", "generation", "outcome"], []),
    "/event": ("add_event", ["actor", "type_"], ["task_id", "payload",
                                                 "idempotency_key"]),
    "/ack": ("ack", ["agent", "event_seq"], []),
    "/handoff": ("register_handoff", ["agent", "task_id", "generation",
                                      "git_ref", "commit_hex", "paths"], []),
    "/review": ("add_review", ["task_id", "reviewer", "verdict"],
                ["evidence", "artifact_generation"]),
}


def make_server(store, token, host="127.0.0.1", port=7077):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authed(self):
            return self.headers.get("Authorization") == f"Bearer {token}"

        def do_GET(self):
            url = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            if url.path == "/health":
                return self._send(200, {"ok": True, "time": store._now_iso()})
            if not self._authed():
                return self._send(401, {"error": "bad token"})
            if url.path == "/tasks":
                return self._send(200, store.tasks(state=q.get("state")))
            if url.path == "/events":
                return self._send(200, store.events(since=int(q.get("since", 0))))
            if url.path == "/reviews":
                return self._send(200, store.reviews(q["task_id"]))
            if url.path == "/status":
                return self._send(200, {"error": "dashboard added in Task 14"})
            return self._send(404, {"error": f"no route {url.path}"})

        def do_POST(self):
            if not self._authed():
                return self._send(401, {"error": "bad token"})
            route = POST_ROUTES.get(urlparse(self.path).path)
            if route is None:
                return self._send(404, {"error": f"no route {self.path}"})
            method, required, optional = route
            try:
                n = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(n) or b"{}")
                missing = [k for k in required if k not in payload]
                if missing:
                    raise CoordError(f"missing fields: {missing}")
                kwargs = {k: payload[k] for k in required + optional
                          if k in payload}
                return self._send(200, getattr(store, method)(**kwargs))
            except CoordError as e:
                return self._send(e.status, {"error": str(e)})
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                return self._send(400, {"error": str(e)})

    return ThreadingHTTPServer((host, port), Handler)


def _cli(argv=None):
    ap = argparse.ArgumentParser(prog="coordd")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--db", required=True)
    s.add_argument("--repo", default=None)
    s.add_argument("--token-file", required=True)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=7077)
    a = ap.parse_args(argv)
    if a.cmd == "serve":
        token = open(a.token_file).read().strip()
        store = Store(db_path=a.db, repo_dir=a.repo)
        srv = make_server(store, token, host=a.host, port=a.port)
        print(f"coordd serving on {a.host}:{srv.server_address[1]} db={a.db}")
        srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
```

Note: `set_state`'s keyword is `state`/`actor` and `add_event`'s type parameter is named `type_` — the route table above matches the Store signatures exactly; do not rename either side.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_http.py tests/test_coordd_store.py tests/test_coordd_git.py -q -p no:randomly`
Expected: PASS (18 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_http.py
git commit -m "coordd: HTTP layer, bearer auth, serve mode (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 14: Dashboard, audit export, restart durability

**Files:**
- Modify: `scripts/coordd.py` (add `render_status`, `export_audit`, `dump` CLI modes; wire `/status`)
- Test: `tests/test_coordd_http.py` and `tests/test_coordd_store.py` (append)

**Interfaces:**
- Produces: GET `/status` (auth) → HTML page containing every non-`done`/`dropped` task id, owner, state, lease expiry, and registered agents with compatibility; `store.export_audit(out_path) -> int` (count of newly exported events; appends JSON lines `{"seq", "server_time", "type", "actor", "task_id", "payload"}`, cursor kept in `meta` key `audit_cursor`, idempotent); CLI modes `export-audit --db X --out F` and `dump --db X --out F` (uses `sqlite3 .backup` via the Python API).

- [ ] **Step 1: Write the failing tests** (append; HTML test to `tests/test_coordd_http.py`, export/durability to `tests/test_coordd_store.py`)

```python
# append to tests/test_coordd_http.py
def test_status_page_lists_live_tasks(server):
    _call(server, "/register", {"agent": "a1", "protocol_version": 1})
    _call(server, "/task", {"task_id": "t-status", "title": "visible"})
    _call(server, "/claim", {"agent": "a1", "task_id": "t-status",
                             "prefixes": ["docs/x"]})
    req = urllib.request.Request(server + "/status",
                                 headers={"Authorization": "Bearer sekret"})
    html = urllib.request.urlopen(req).read().decode()
    assert "t-status" in html and "a1" in html
```

```python
# append to tests/test_coordd_store.py
def test_export_audit_idempotent(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.add_event("a1", "note", payload={"n": 1})
    out = tmp_path / "audit.jsonl"
    assert store.export_audit(str(out)) == 1
    assert store.export_audit(str(out)) == 0          # cursor advanced
    store.add_event("a1", "note", payload={"n": 2})
    assert store.export_audit(str(out)) == 1
    assert len(out.read_text().splitlines()) == 2


def test_restart_preserves_everything(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    gen = store.claim("a1", "t1", ["docs/x"])["generation"]
    reopened = coordd.Store(db_path=store.db_path)      # fresh instance, same file
    assert reopened.tasks(state="claimed")[0]["owner"] == "a1"
    reopened.heartbeat("a1", "t1", gen)                 # lease+generation survived
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py tests/test_coordd_http.py -q -p no:randomly`
Expected: `test_status_page_lists_live_tasks` fails on the placeholder JSON; `test_export_audit_idempotent` fails with `AttributeError`; the restart test may already pass (it exercises Task 7–10 code — keep it as the spec's restart acceptance check).

- [ ] **Step 3: Implement** (add to `Store` and the HTTP/CLI layers)

```python
    def render_status(self):
        con = self._read()
        try:
            tasks = con.execute(
                "SELECT t.id, t.state, t.priority, t.owner, l.expires"
                " FROM tasks t LEFT JOIN leases l ON l.task_id = t.id"
                " WHERE t.state NOT IN ('done','dropped')"
                " ORDER BY t.priority, t.id").fetchall()
            agents = con.execute(
                "SELECT id, role, compatible, last_seen FROM agents"
                " ORDER BY id").fetchall()
        finally:
            con.close()
        rows = "".join(
            f"<tr><td>{t['id']}</td><td>{t['state']}</td><td>{t['owner'] or ''}"
            f"</td><td>{t['expires'] or ''}</td></tr>" for t in tasks)
        arows = "".join(
            f"<tr><td>{a['id']}</td><td>{a['role']}</td>"
            f"<td>{'yes' if a['compatible'] else 'NO'}</td>"
            f"<td>{a['last_seen']}</td></tr>" for a in agents)
        return ("<html><body><h1>coordd</h1>"
                f"<p>server time {self._now_iso()}</p>"
                "<h2>live tasks</h2><table border=1>"
                "<tr><th>task</th><th>state</th><th>owner</th><th>lease expires"
                f"</th></tr>{rows}</table>"
                "<h2>agents</h2><table border=1>"
                "<tr><th>agent</th><th>role</th><th>compatible</th><th>last seen"
                f"</th></tr>{arows}</table></body></html>")

    def export_audit(self, out_path):
        with self._tx() as con:
            row = con.execute("SELECT value FROM meta WHERE key='audit_cursor'"
                              ).fetchone()
            cursor = int(row[0]) if row else 0
            rows = con.execute(
                "SELECT seq, server_time, type, actor, task_id, payload"
                " FROM events WHERE seq > ? ORDER BY seq", (cursor,)).fetchall()
            if rows:
                with open(out_path, "a", encoding="utf-8") as f:
                    for seq, st, ty, actor, task_id, payload in rows:
                        f.write(json.dumps(
                            {"seq": seq, "server_time": st, "type": ty,
                             "actor": actor, "task_id": task_id,
                             "payload": json.loads(payload)}) + "\n")
                con.execute("INSERT OR REPLACE INTO meta VALUES('audit_cursor',?)",
                            (str(rows[-1][0]),))
            return len(rows)
```

In `do_GET`, replace the `/status` placeholder branch with:

```python
            if url.path == "/status":
                body = store.render_status().encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
```

In `_cli`, add the two subcommands:

```python
    e = sub.add_parser("export-audit")
    e.add_argument("--db", required=True)
    e.add_argument("--out", required=True)
    d = sub.add_parser("dump")
    d.add_argument("--db", required=True)
    d.add_argument("--out", required=True)
```

and their dispatch:

```python
    if a.cmd == "export-audit":
        n = Store(db_path=a.db).export_audit(a.out)
        print(f"exported {n} event(s) to {a.out}")
        return 0
    if a.cmd == "dump":
        src = sqlite3.connect(a.db)
        dst = sqlite3.connect(a.out)
        src.backup(dst)
        dst.close(); src.close()
        print(f"dumped {a.db} -> {a.out}")
        return 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_store.py tests/test_coordd_http.py tests/test_coordd_git.py -q -p no:randomly`
Expected: PASS (21 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd.py tests/test_coordd_store.py tests/test_coordd_http.py
git commit -m "coordd: status dashboard, audit export, restart durability (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 15: `coordctl` client CLI with `doctor`

**Files:**
- Create: `scripts/coordctl.py`
- Test: `tests/test_coordctl.py`

**Interfaces:**
- Consumes: coordd HTTP API (Task 13/14), the three P0 guards (Tasks 3–5), `scripts/inbox_sweep.py` presence on `origin/main`.
- Produces: `python3 scripts/coordctl.py <cmd>` with subcommands `register claim heartbeat release task task-state event ack handoff tasks events doctor`; server URL from `--url` or `COORDD_URL` (default `http://127.0.0.1:7077`), token from `--token`, `COORDD_TOKEN`, or `~/.coordd/token`. `main(argv, base_url=None, token=None) -> int` importable. `doctor` runs: `/health` reachability (warn-only in P1 — the service may not be deployed yet), `check_clock.main`, `check_cron_health.main`, `check_ref_census.main`, sacred-source SHA prefix `fff6669b`, and worktree `scripts/inbox_sweep.py` digest vs `origin/main`; exit = max of the mandatory checks' codes.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_coordctl.py
import json
import threading
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd
import coordctl

import pytest


@pytest.fixture
def live(tmp_path):
    store = coordd.Store(db_path=str(tmp_path / "c.sqlite3"))
    srv = coordd.make_server(store, token="sekret", port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_register_task_claim_roundtrip(live, capsys):
    rc = coordctl.main(["register", "--agent", "a1", "--role", "contributor"],
                       base_url=live, token="sekret")
    assert rc == 0 and json.loads(capsys.readouterr().out)["compatible"] is True
    coordctl.main(["task", "--id", "t1", "--title", "demo"],
                  base_url=live, token="sekret")
    rc = coordctl.main(["claim", "--agent", "a1", "--task", "t1",
                        "--prefix", "docs/x"], base_url=live, token="sekret")
    assert rc == 0
    out = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert out["generation"] == 1


def test_conflict_maps_to_exit_1(live, capsys):
    coordctl.main(["register", "--agent", "a1"], base_url=live, token="sekret")
    coordctl.main(["register", "--agent", "a2"], base_url=live, token="sekret")
    coordctl.main(["task", "--id", "t1", "--title", "demo"],
                  base_url=live, token="sekret")
    coordctl.main(["claim", "--agent", "a1", "--task", "t1", "--prefix", "d/"],
                  base_url=live, token="sekret")
    rc = coordctl.main(["claim", "--agent", "a2", "--task", "t1",
                        "--prefix", "d/"], base_url=live, token="sekret")
    assert rc == 1 and "error" in capsys.readouterr().out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordctl.py -q -p no:randomly`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'coordctl'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# scripts/coordctl.py
"""coordctl — thin client for coordd plus the local `doctor` aggregate.
Stdlib only. Exit codes: 0 ok, 1 server refused (4xx/5xx, e.g. claim conflict),
2 transport/guard failure."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:7077"


def _token(explicit):
    if explicit:
        return explicit
    if os.environ.get("COORDD_TOKEN"):
        return os.environ["COORDD_TOKEN"]
    p = Path.home() / ".coordd" / "token"
    return p.read_text().strip() if p.exists() else ""


def _call(base, token, path, payload=None):
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {token}"}
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _doctor(repo):
    sys.path.insert(0, str(Path(repo) / "scripts"))
    import check_clock, check_cron_health, check_ref_census
    codes = [check_clock.main(repo=repo),
             check_cron_health.main(log_path=str(Path(repo) /
                                                 "data/raw/collect_wide.log")),
             check_ref_census.main(repo=repo)]
    sacred = Path(repo) / "rust/src/bin/yamo_orchard_live.rs"
    digest = hashlib.sha256(sacred.read_bytes()).hexdigest()
    ok = digest.startswith("fff6669b")
    print(f"sacred source: {digest[:12]} {'OK' if ok else 'VIOLATED'}")
    codes.append(0 if ok else 2)
    theirs = subprocess.run(
        ["git", "-C", repo, "show", "origin/main:scripts/inbox_sweep.py"],
        capture_output=True).stdout
    mine = (Path(repo) / "scripts/inbox_sweep.py").read_bytes()
    same = hashlib.sha256(mine).hexdigest() == hashlib.sha256(theirs).hexdigest()
    print(f"inbox_sweep digest vs origin/main: {'match' if same else 'DRIFT'}")
    codes.append(0 if same else 2)
    return max(codes)


def main(argv=None, base_url=None, token=None):
    ap = argparse.ArgumentParser(prog="coordctl")
    ap.add_argument("--url", default=None)
    ap.add_argument("--token", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, *specs):
        p = sub.add_parser(name)
        for flag, kw in specs:
            p.add_argument(flag, **kw)
        return p

    add("register", ("--agent", {"required": True}),
        ("--role", {"default": "contributor"}),
        ("--tool-digest", {"default": None}),
        ("--protocol-version", {"type": int, "default": 1}))
    add("task", ("--id", {"required": True}), ("--title", {"required": True}),
        ("--priority", {"type": int, "default": 2}))
    add("task-state", ("--id", {"required": True}),
        ("--state", {"required": True}), ("--actor", {"required": True}))
    add("claim", ("--agent", {"required": True}), ("--task", {"required": True}),
        ("--prefix", {"action": "append", "required": True}))
    add("heartbeat", ("--agent", {"required": True}),
        ("--task", {"required": True}),
        ("--generation", {"type": int, "required": True}))
    add("release", ("--agent", {"required": True}), ("--task", {"required": True}),
        ("--generation", {"type": int, "required": True}),
        ("--outcome", {"required": True}))
    add("event", ("--actor", {"required": True}), ("--type", {"required": True}),
        ("--task", {"default": None}), ("--payload", {"default": "{}"}),
        ("--idempotency-key", {"default": None}))
    add("ack", ("--agent", {"required": True}),
        ("--event-seq", {"type": int, "required": True}))
    add("handoff", ("--agent", {"required": True}), ("--task", {"required": True}),
        ("--generation", {"type": int, "required": True}),
        ("--ref", {"required": True}), ("--commit", {"required": True}),
        ("--path", {"action": "append", "required": True}))
    add("tasks", ("--state", {"default": None}))
    add("events", ("--since", {"type": int, "default": 0}))
    add("doctor", ("--repo", {"default": "."}))

    a = ap.parse_args(argv)
    base = base_url or a.url or os.environ.get("COORDD_URL", DEFAULT_URL)
    tok = _token(token or a.token)

    if a.cmd == "doctor":
        try:
            h = _call(base, tok, "/health")
            print(f"coordd: reachable, server time {h['time']}")
        except (urllib.error.URLError, OSError) as e:
            print(f"coordd: UNREACHABLE ({e}) — warn-only until P2")
        return _doctor(a.repo)

    posts = {
        "register": ("/register", lambda a: {
            "agent": a.agent, "role": a.role, "tool_digest": a.tool_digest,
            "protocol_version": a.protocol_version}),
        "task": ("/task", lambda a: {"task_id": a.id, "title": a.title,
                                     "priority": a.priority}),
        "task-state": ("/task_state", lambda a: {"task_id": a.id,
                                                 "state": a.state,
                                                 "actor": a.actor}),
        "claim": ("/claim", lambda a: {"agent": a.agent, "task_id": a.task,
                                       "prefixes": a.prefix}),
        "heartbeat": ("/heartbeat", lambda a: {"agent": a.agent,
                                               "task_id": a.task,
                                               "generation": a.generation}),
        "release": ("/release", lambda a: {"agent": a.agent, "task_id": a.task,
                                           "generation": a.generation,
                                           "outcome": a.outcome}),
        "event": ("/event", lambda a: {"actor": a.actor, "type_": a.type,
                                       "task_id": a.task,
                                       "payload": json.loads(a.payload),
                                       "idempotency_key": a.idempotency_key}),
        "ack": ("/ack", lambda a: {"agent": a.agent, "event_seq": a.event_seq}),
        "handoff": ("/handoff", lambda a: {
            "agent": a.agent, "task_id": a.task, "generation": a.generation,
            "git_ref": a.ref, "commit_hex": a.commit, "paths": a.path}),
    }
    try:
        if a.cmd in posts:
            path, build = posts[a.cmd]
            print(json.dumps(_call(base, tok, path, build(a))))
        elif a.cmd == "tasks":
            q = f"?state={a.state}" if a.state else ""
            print(json.dumps(_call(base, tok, "/tasks" + q)))
        elif a.cmd == "events":
            print(json.dumps(_call(base, tok, f"/events?since={a.since}")))
        return 0
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": e.read().decode(), "status": e.code}))
        return 1
    except (urllib.error.URLError, OSError) as e:
        print(f"transport failure: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordctl.py -q -p no:randomly`
Expected: PASS (2 passed)

- [ ] **Step 5: Run doctor against the real repo**

Run: `.venv/bin/python3 scripts/coordctl.py doctor --repo .; echo "exit=$?"`
Expected: `coordd: UNREACHABLE ... warn-only`, clock sane, cron status (honest), census result, `sacred source: fff6669b... OK`, sweep digest `match`. Exit reflects the guards, not the unreachable service.

- [ ] **Step 6: Commit**

```bash
git add scripts/coordctl.py tests/test_coordctl.py
git commit -m "coordctl: client CLI and doctor aggregate (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 16: Shadow-mode mirror

**Files:**
- Create: `scripts/coordd_mirror.py`
- Test: `tests/test_coordd_mirror.py`

**Interfaces:**
- Consumes: coordd `/event` endpoint (idempotency keys make re-runs safe).
- Produces: `coordd_mirror.main(messages_root, post, cursor_path) -> int` (count of newly mirrored files). Scans `coordination/messages/*/` recursively, posts one event per new `.md` file: `type_="legacy_message"`, `actor=<sender dir>`, `payload={"path": <repo-relative path>}`, `idempotency_key=<repo-relative path>`; remembers seen paths in a JSON cursor file. CLI: `python3 scripts/coordd_mirror.py --root coordination/messages --cursor ~/.coordd/mirror-cursor.json`. This is the spec's P1 "mirror new git-message traffic into the service" — comparison = `coordctl events` vs `inbox_sweep` output, by hand, during shadow.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_coordd_mirror.py
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd_mirror


def test_mirror_posts_new_files_once(tmp_path):
    root = tmp_path / "messages"
    (root / "claude_1").mkdir(parents=True)
    (root / "claude_1" / "20260810T000000Z-x-progress.md").write_text("hi")
    (root / "claude_1" / "README.md").write_text("not a message")
    cursor = tmp_path / "cursor.json"
    posted = []
    n = coordd_mirror.main(messages_root=root, post=posted.append,
                           cursor_path=cursor)
    assert n == 1 and posted[0]["idempotency_key"].endswith("-x-progress.md")
    assert posted[0]["actor"] == "claude_1"
    n2 = coordd_mirror.main(messages_root=root, post=posted.append,
                            cursor_path=cursor)
    assert n2 == 0 and len(posted) == 1                 # cursor holds

    (root / "claude_1" / "20260810T000001Z-x-ack.md").write_text("hi2")
    assert coordd_mirror.main(messages_root=root, post=posted.append,
                              cursor_path=cursor) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_mirror.py -q -p no:randomly`
Expected: FAIL/ERROR with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
# scripts/coordd_mirror.py
"""Shadow-mode mirror (spec §6 P1): posts each new coordination message file into
coordd as a 'legacy_message' event. Git stays authoritative during shadow; the
idempotency key (the repo-relative path) makes re-runs and restarts harmless."""
import argparse
import json
import re
import sys
from pathlib import Path

MSG_RE = re.compile(r"^\d{8}T\d{6}Z-.+\.md$")


def _default_post_factory(url, token):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import coordctl

    def post(ev):
        rc = coordctl.main(
            ["event", "--actor", ev["actor"], "--type", "legacy_message",
             "--task", ev.get("task_id") or "",
             "--payload", json.dumps(ev["payload"]),
             "--idempotency-key", ev["idempotency_key"]],
            base_url=url, token=token)
        if rc != 0:
            raise RuntimeError(f"mirror post failed rc={rc} for {ev}")
    return post


def main(messages_root, post, cursor_path):
    root = Path(messages_root)
    cursor_path = Path(cursor_path)
    seen = set(json.loads(cursor_path.read_text())) if cursor_path.exists() else set()
    new = 0
    for f in sorted(root.glob("*/*.md")):
        rel = f"{f.parent.name}/{f.name}"
        if rel in seen or not MSG_RE.match(f.name):
            continue
        post({"actor": f.parent.name, "task_id": None,
              "payload": {"path": f"coordination/messages/{rel}"},
              "idempotency_key": f"coordination/messages/{rel}"})
        seen.add(rel)
        new += 1
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    cursor_path.write_text(json.dumps(sorted(seen)))
    return new


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="coordination/messages")
    ap.add_argument("--cursor", default=str(Path.home() / ".coordd" /
                                            "mirror-cursor.json"))
    ap.add_argument("--url", default=None)
    ap.add_argument("--token", default=None)
    a = ap.parse_args()
    import os
    url = a.url or os.environ.get("COORDD_URL", "http://127.0.0.1:7077")
    n = main(messages_root=a.root,
             post=_default_post_factory(url, a.token),
             cursor_path=a.cursor)
    print(f"mirrored {n} new message(s)")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python3 -m pytest tests/test_coordd_mirror.py -q -p no:randomly`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/coordd_mirror.py tests/test_coordd_mirror.py
git commit -m "coordd: shadow-mode message mirror with cursor (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```

### Task 17: Deployment artifacts, shadow runbook, full-suite gate

**Files:**
- Create: `deploy/coordd.service`, `deploy/coordd-tunnel.service`, `deploy/README.md`
- Create: `coordination/coordd-shadow-runbook.md`

**Interfaces:**
- Consumes: everything above. Produces: copy-paste deployment for the owner; the shadow runbook that P2's follow-up plan will cite.

- [ ] **Step 1: Write the systemd units**

```ini
# deploy/coordd.service — install on the Yandex Cloud VM at /etc/systemd/system/
[Unit]
Description=coordd coordination control plane (Troll Farm)
After=network-online.target

[Service]
Type=simple
User=coordd
ExecStart=/usr/bin/python3 /opt/troll_farm/scripts/coordd.py serve \
  --db /var/lib/coordd/coordd.sqlite3 \
  --repo /var/lib/coordd/repo.git \
  --token-file /etc/coordd/token \
  --host 127.0.0.1 --port 7077
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```ini
# deploy/coordd-tunnel.service — user unit on project_host at ~/.config/systemd/user/
[Unit]
Description=SSH tunnel to coordd on the Yandex Cloud VM
After=network-online.target

[Service]
Type=simple
# Replace VM_ALIAS with the ssh config alias for the Yandex Cloud VM.
ExecStart=/usr/bin/ssh -N -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -o ExitOnForwardFailure=yes -L 7077:127.0.0.1:7077 VM_ALIAS
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

- [ ] **Step 2: Write deploy/README.md**

```markdown
# Deploying coordd (P1 shadow mode)

Spec: `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md`.
Order: VM first, tunnel second, shadow runbook third
(`coordination/coordd-shadow-runbook.md`).

## On the Yandex Cloud VM (hosts claude_1 and codex_1)

```bash
sudo useradd -r -m -d /var/lib/coordd coordd
sudo mkdir -p /opt/troll_farm /etc/coordd
sudo git clone git@github.com:tarstars/troll_farm.git /opt/troll_farm   # or update an existing clone
sudo -u coordd git clone --mirror git@github.com:tarstars/troll_farm.git /var/lib/coordd/repo.git
openssl rand -hex 32 | sudo tee /etc/coordd/token >/dev/null
sudo chmod 600 /etc/coordd/token
sudo cp /opt/troll_farm/deploy/coordd.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now coordd
curl -s http://127.0.0.1:7077/health   # {"ok": true, ...}
```

Agents on the VM read the token from `/etc/coordd/token` into `~/.coordd/token`
(per agent user) and use `COORDD_URL=http://127.0.0.1:7077`.

## On project_host (local agents)

```bash
mkdir -p ~/.coordd && scp VM_ALIAS:/etc/coordd/token ~/.coordd/token && chmod 600 ~/.coordd/token
mkdir -p ~/.config/systemd/user
cp deploy/coordd-tunnel.service ~/.config/systemd/user/   # edit VM_ALIAS first
systemctl --user daemon-reload && systemctl --user enable --now coordd-tunnel
curl -s http://127.0.0.1:7077/health
python3 scripts/coordctl.py doctor --repo .
```

## Not done here

No public port, no TLS (the tunnel is the boundary), no CI (owner ruling
2026-08-10), no authority switch — git remains authoritative until the P2 plan.
Daily dump: `python3 scripts/coordd.py dump --db /var/lib/coordd/coordd.sqlite3
--out /var/lib/coordd/backup-$(date -u +%F).sqlite3` (add as a coordd-user cron
on the VM); audit export lands in-repo during P2.
```

- [ ] **Step 3: Write the shadow runbook**

```markdown
# coordd shadow mode — runbook (P1)

While in shadow: **git is authoritative; coordd is being compared against it.**
Nothing about the existing protocol changes yet.

1. Deploy per `deploy/README.md`; verify `/health` from both machines.
2. Register the roster (from any machine):
   `coordctl register --agent local_claude_1 --role coordinator`
   `coordctl register --agent claude_1` · `coordctl register --agent codex_1`
3. Create coordd tasks for every currently-open task record you touch (id = the
   `coordination/tasks/` filename stem), and claim/release in coordd alongside the
   normal git flow.
4. Mirror messages after each fetch:
   `python3 scripts/coordd_mirror.py --root coordination/messages`
5. Weekly comparison, recorded in the task record for the migration:
   - `coordctl tasks --state claimed` vs actually-active work;
   - `coordctl events --since 0 | wc -l` vs new message count in git;
   - any disagreement is a bug in shadow wiring — fix before proposing P2.
6. Exit criteria to propose the P2 plan: two weeks (or three working sessions,
   whichever first) with zero unexplained disagreements, all Task 7–16 tests
   green, and the owner's go-ahead.
```

- [ ] **Step 4: Run the full test suite as the task gate**

Run: `.venv/bin/python3 -m pytest tests/ -q -p no:randomly > /tmp/gate.txt 2>&1; echo "EXIT=$?"; tail -3 /tmp/gate.txt` *(capture-then-page — `pytest | tail` eats the gate's exit; G5 F7, fixed 2026-08-12)*
Expected: `3 failed` (the pre-existing B7 trio: `test_analyze_d102a_complete_macro_resident_transfer`, `test_idle_harvest_probe`, `test_validate_opponent_crop_candidate` — an owner decision, out of scope) and everything else passed, including all new `test_coordd*`, `test_check_*`, `test_doc_budgets` tests. Any other failure blocks this task.

- [ ] **Step 5: Commit**

```bash
git add deploy/coordd.service deploy/coordd-tunnel.service deploy/README.md coordination/coordd-shadow-runbook.md
git commit -m "deploy: coordd systemd units, tunnel, shadow runbook (P1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git branch -f main HEAD && git push origin session-2026-07-01 main
```
