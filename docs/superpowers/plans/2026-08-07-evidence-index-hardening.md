# Evidence Index Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make evidence citations permanent by pinning them to git commits, and add a lightweight hypothesis tier so open questions and reviewer conflicts become a pullable backlog.

**Architecture:** A new `cgauto/evidence_git.py` resolves `(commit, path)` pairs to file content via `git show`, replacing working-tree reads. The validator gains a warning channel (drift, pending integration) separate from its existing hard errors. A new `cgauto/evidence_hypotheses.py` handles a six-field open-question tier stored in `docs/evidence/hypotheses/`, rendered into a generated `OPEN-QUESTIONS.md` backlog view.

**Tech Stack:** Python 3.12, stdlib only (`subprocess`, `json`, `re`, `pathlib`), pytest.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-08-07-evidence-index-hardening-design.md`.
- Python stdlib only. No new dependencies. Repo has no `requirements.txt` for these tools.
- Never hand-edit anything under `docs/evidence/generated/` — it is produced by the builder.
- Never modify `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, or `docs/STATE.md`. This system cites them.
- Never modify `rust/src/bin/yamo_orchard_live.rs` (sacred, SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`).
- Never run a formatter over `cgauto/`.
- Run tests with `python3 -m pytest -q` from the repo root.
- Existing suite is `tests/test_decision_evidence_index.py` (25 tests) and must stay green throughout.
- New hypothesis IDs use the `Q<n>` namespace. `D`, `H`, `N` prefixes are already taken.
- Commit after each task.

---

## File Structure

| File | Responsibility |
|---|---|
| `cgauto/evidence_git.py` (create) | Resolve blobs at a pinned commit; commit existence and ancestry checks. Pure git access, no schema knowledge. |
| `cgauto/evidence_hypotheses.py` (create) | Load and validate the six-field hypothesis tier. Separate schema, separate lifecycle. |
| `cgauto/migrate_evidence_locators.py` (create) | Single-use, idempotent migration: pin existing records and capture quotes. |
| `cgauto/check_decision_evidence_index.py` (modify) | Schema v2 validation, warning channel, hypothesis integration. |
| `cgauto/build_decision_evidence_index.py` (modify) | Render `OPEN-QUESTIONS.md` and the `Drifted` section. |
| `docs/evidence/SCHEMA.md` (modify) | Document schema v2 and both tiers. |
| `tests/test_evidence_git.py` (create) | Git blob reader unit tests. |
| `tests/test_evidence_hypotheses.py` (create) | Hypothesis tier tests. |
| `tests/test_decision_evidence_index.py` (modify) | Git fixture helper; pinned-locator and warning cases. |

---

### Task 1: Git blob reader

**Files:**
- Create: `cgauto/evidence_git.py`
- Test: `tests/test_evidence_git.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `GitLookupError`, `commit_resolves(repo: Path, commit: str) -> bool`, `read_blob(repo: Path, commit: str, path: str) -> str`, `ref_exists(repo: Path, ref: str) -> bool`, `is_ancestor(repo: Path, commit: str, ref: str) -> bool`, `COMMIT_RE`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_evidence_git.py`:

```python
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.evidence_git import (
    GitLookupError, commit_resolves, read_blob, ref_exists, is_ancestor,
)

def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    return repo

def commit_file(repo: Path, name: str, text: str) -> str:
    (repo / name).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", f"add {name}")
    return git(repo, "rev-parse", "HEAD").strip()

def test_read_blob_returns_content_at_that_commit(tmp_path):
    repo = init_repo(tmp_path)
    first = commit_file(repo, "f.md", "original\n")
    commit_file(repo, "f.md", "rewritten\n")
    assert read_blob(repo, first, "f.md") == "original\n"

def test_commit_resolves(tmp_path):
    repo = init_repo(tmp_path)
    sha = commit_file(repo, "f.md", "x\n")
    assert commit_resolves(repo, sha) is True
    assert commit_resolves(repo, "0" * 40) is False

def test_read_blob_missing_path_raises(tmp_path):
    repo = init_repo(tmp_path)
    sha = commit_file(repo, "f.md", "x\n")
    with pytest.raises(GitLookupError):
        read_blob(repo, sha, "nope.md")

def test_ancestry(tmp_path):
    repo = init_repo(tmp_path)
    first = commit_file(repo, "f.md", "a\n")
    second = commit_file(repo, "g.md", "b\n")
    assert ref_exists(repo, "HEAD") is True
    assert ref_exists(repo, "refs/heads/nonexistent") is False
    assert is_ancestor(repo, first, second) is True
    assert is_ancestor(repo, second, first) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_evidence_git.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cgauto.evidence_git'`

- [ ] **Step 3: Write minimal implementation**

Create `cgauto/evidence_git.py`:

```python
#!/usr/bin/env python3
"""Resolve file content at pinned git commits. No schema knowledge lives here."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

class GitLookupError(ValueError):
    pass

def _run(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )

def commit_resolves(repo: Path, commit: str) -> bool:
    if not COMMIT_RE.match(commit or ""):
        return False
    return _run(repo, ["cat-file", "-e", f"{commit}^{{commit}}"]).returncode == 0

def read_blob(repo: Path, commit: str, path: str) -> str:
    result = _run(repo, ["show", f"{commit}:{path}"])
    if result.returncode != 0:
        raise GitLookupError(f"{path} is absent at commit {commit[:12]}")
    return result.stdout

def ref_exists(repo: Path, ref: str) -> bool:
    return _run(repo, ["rev-parse", "--verify", "--quiet", ref]).returncode == 0

def is_ancestor(repo: Path, commit: str, ref: str) -> bool:
    return _run(repo, ["merge-base", "--is-ancestor", commit, ref]).returncode == 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_evidence_git.py -q`
Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```bash
git add cgauto/evidence_git.py tests/test_evidence_git.py
git commit -m "feat(evidence): add git blob reader for pinned citations"
```

---

### Task 2: Git-pinned locator validation (schema v2)

**Files:**
- Modify: `cgauto/check_decision_evidence_index.py` (`validate_source`, `validate_record`)
- Modify: `tests/test_decision_evidence_index.py` (add git fixture helper)

**Interfaces:**
- Consumes: `read_blob`, `commit_resolves`, `COMMIT_RE` from Task 1.
- Produces: `validate_source(repo, source, context)` now requires `source["commit"]` and reads at that commit; records must declare `schema_version: 2`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_decision_evidence_index.py` (after the existing imports):

```python
import subprocess

def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def git_init_and_commit(repo: Path) -> str:
    """Make `repo` a git repo and commit everything currently in it."""
    if not (repo / ".git").exists():
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "t@example.com")
        git(repo, "config", "user.name", "t")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "fixture")
    return git(repo, "rev-parse", "HEAD").strip()

def test_pinned_locator_survives_later_line_drift(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 1-2",
    }
    record["constraint_projection"]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 1-2",
    }
    record["decisive_claims"][0]["source"] = {
        "path": "evidence.json", "commit": sha, "json_pointer": "/value",
    }
    write_record(repo, record)
    # Prepend lines so every old line number is wrong in the working tree.
    (repo / "source.md").write_text(
        "PREPENDED\nPREPENDED\n" + (repo / "source.md").read_text()
    )
    build(repo)
    validate_repository(repo, require_pilot=False, check_generated=True)

def test_unresolvable_commit_is_hard_error(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    for src in (
        record["textual_evidence"][0]["source"],
        record["constraint_projection"]["source"],
        record["decisive_claims"][0]["source"],
    ):
        src["commit"] = "0" * 40
    write_record(repo, record)
    build(repo)
    with pytest.raises(ValidationError, match="does not resolve"):
        validate_repository(repo, require_pilot=False, check_generated=False)

def test_path_absent_at_pinned_commit_is_hard_error(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    record["textual_evidence"][0]["source"] = {
        "path": "later.md", "commit": sha, "locator": "lines 1-1",
    }
    record["constraint_projection"]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 1-2",
    }
    record["decisive_claims"][0]["source"] = {
        "path": "evidence.json", "commit": sha, "json_pointer": "/value",
    }
    (repo / "later.md").write_text("created after the pin\n")
    write_record(repo, record)
    build(repo)
    with pytest.raises(ValidationError, match="absent at commit"):
        validate_repository(repo, require_pilot=False, check_generated=False)
```

Add one more test proving the token check still fires against the pinned excerpt:

```python
def test_missing_tokens_at_pinned_commit_is_hard_error(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    # Claim asserts a number the pinned excerpt does not contain.
    record["textual_evidence"][0]["claim"] = "Fixture text shows +99.9 improvement."
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 2-2",
    }
    for src in (record["constraint_projection"]["source"],
                record["decisive_claims"][0]["source"]):
        src.setdefault("commit", sha)
    write_record(repo, record)
    build(repo)
    with pytest.raises(ValidationError, match="omits content tokens"):
        validate_repository(repo, require_pilot=False, check_generated=False)
```

Also update `make_repo` so it can skip generation (it already accepts `build_generated`), and update `base_record()` to set `"schema_version": 2` and add `"commit"` keys — do this in Step 3 together with the implementation so the existing 25 tests move to v2 in one edit.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_decision_evidence_index.py -q -k pinned`
Expected: FAIL — `ValidationError: ...: source.commit required` is not yet raised; instead the record fails on `schema_version must be 1`.

- [ ] **Step 3: Write minimal implementation**

In `cgauto/check_decision_evidence_index.py`, add the import after the existing `from cgauto.build_decision_evidence_index import ...` line:

```python
from cgauto.evidence_git import (
    COMMIT_RE, GitLookupError, commit_resolves, is_ancestor, read_blob, ref_exists,
)
```

Replace `validate_source` (lines 69-91) with:

```python
def validate_source(repo: Path, source: dict[str, Any], context: str) -> Any:
    if not isinstance(source, dict) or not source.get("path"):
        raise ValidationError(f"{context}: source.path required")
    rel = source["path"]
    if Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValidationError(f"unsafe repository path: {rel}")
    commit = source.get("commit")
    if not commit or not COMMIT_RE.match(commit):
        raise ValidationError(f"{context}: source.commit must be a 40-character sha")
    if not commit_resolves(repo, commit):
        raise ValidationError(f"{context}: commit {commit[:12]} does not resolve")
    try:
        text = read_blob(repo, commit, rel)
    except GitLookupError as exc:
        raise ValidationError(f"{context}: {exc}") from None
    locator = source.get("locator")
    pointer = source.get("json_pointer")
    if bool(locator) == bool(pointer):
        raise ValidationError(f"{context}: exactly one of locator/json_pointer required")
    if locator:
        m = LINE_RE.match(locator)
        if not m:
            raise ValidationError(f"{context}: locator must be 'lines N-M'")
        a, b = map(int, m.groups())
        if a < 1 or b < a:
            raise ValidationError(f"{context}: invalid line range")
        lines = text.splitlines()
        if b > len(lines):
            raise ValidationError(f"{context}: line range exceeds {rel} ({len(lines)})")
        return "\n".join(lines[a - 1:b])
    if Path(rel).suffix.lower() != ".json":
        raise ValidationError(f"{context}: JSON pointer requires .json source")
    return resolve_pointer(json.loads(text), pointer)
```

In `validate_record`, change the schema check (line 114-115) to:

```python
    if record["schema_version"] != 2:
        raise ValidationError(f"{rid}: schema_version must be 2")
```

Delete the now-unused `safe_path` calls for evidence sources, but keep `safe_path` itself — line 180 still uses it for discussions.

**Do not touch the numeric-token checks.** `validate_record` calls
`require_excerpt_tokens(...)` and `require_constraints_identity(...)` at four sites (decisive
claims, textual evidence, premise failure, constraint projection). Those remain exactly as they
are and stay **hard errors** — they are what detected all nine rotted records. The only change is
that the excerpt they receive now comes from the pinned commit instead of the working tree.

In `tests/test_decision_evidence_index.py`, update `base_record()`: set `"schema_version": 2`, and give each of the three `source` dicts a `"commit"` key whose value is filled by the fixture. Change `make_repo` to git-init and commit before writing records, then stamp the resulting SHA into the record:

```python
def make_repo(tmp_path: Path, record=None, build_generated=True) -> Path:
    repo = tmp_path
    (repo / "docs/evidence/discussions").mkdir(parents=True, exist_ok=True)
    (repo / "docs/evidence/generated").mkdir(parents=True, exist_ok=True)
    (repo / "source.md").write_text(
        "Fixture value is +1.0 on 4/4 tasks. [T1]\nFixture text.\n"
    )
    (repo / "evidence.json").write_text(json.dumps({"value": 1.0}))
    sha = git_init_and_commit(repo)
    rec = record or base_record()
    for src in (
        rec["textual_evidence"][0]["source"],
        rec["constraint_projection"]["source"],
        rec["decisive_claims"][0]["source"],
    ):
        src.setdefault("commit", sha)
    write_record(repo, rec)
    if build_generated:
        build(repo)
    return repo
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_decision_evidence_index.py tests/test_evidence_git.py -q`
Expected: PASS — all existing tests plus the 3 new ones.

- [ ] **Step 5: Commit**

```bash
git add cgauto/check_decision_evidence_index.py tests/test_decision_evidence_index.py
git commit -m "feat(evidence): pin citations to git commits (schema v2)"
```

---

### Task 3: Warning channel — drift and pending integration

**Files:**
- Modify: `cgauto/check_decision_evidence_index.py`
- Modify: `tests/test_decision_evidence_index.py`

**Interfaces:**
- Consumes: `is_ancestor`, `ref_exists` from Task 1.
- Produces: `validate_repository(...) -> tuple[list[dict], list[str]]` — returns `(records, warnings)`. Callers in Task 5 and the test suite must unpack two values.

- [ ] **Step 1: Write the failing test**

```python
def test_quote_drift_warns_but_does_not_fail(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 2-2",
        "quote": "Fixture text.",
    }
    for src in (record["constraint_projection"]["source"],
                record["decisive_claims"][0]["source"]):
        src.setdefault("commit", sha)
    write_record(repo, record)
    (repo / "source.md").write_text("Fixture value is +1.0 on 4/4 tasks. [T1]\nREWORDED.\n")
    build(repo)
    _records, warnings = validate_repository(repo, require_pilot=False, check_generated=True)
    assert any("drift" in w for w in warnings), warnings

def test_quote_present_in_current_file_produces_no_drift_warning(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 2-2",
        "quote": "Fixture text.",
    }
    for src in (record["constraint_projection"]["source"],
                record["decisive_claims"][0]["source"]):
        src.setdefault("commit", sha)
    write_record(repo, record)
    build(repo)
    _records, warnings = validate_repository(repo, require_pilot=False, check_generated=True)
    assert not [w for w in warnings if "drift" in w], warnings
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_decision_evidence_index.py -q -k drift`
Expected: FAIL — `TypeError: cannot unpack non-sequence` (validate_repository returns a list).

- [ ] **Step 3: Write minimal implementation**

In `check_decision_evidence_index.py`, add a module-level constant and a collector. Change `validate_source` to accept a warnings list and append drift findings, then thread it through.

Add near the top, after `LINE_RE`:

```python
INTEGRATION_REF = "refs/remotes/origin/main"
```

Change `validate_source`'s signature to
`def validate_source(repo, source, context, warnings=None):`
and append these checks immediately before each `return`:

```python
    if warnings is not None:
        if ref_exists(repo, INTEGRATION_REF) and not is_ancestor(repo, commit, INTEGRATION_REF):
            warnings.append(f"{context}: commit {commit[:12]} pending integration into main")
        quote = source.get("quote")
        if quote:
            current = repo / rel
            if not current.exists() or quote not in current.read_text(
                encoding="utf-8", errors="replace"
            ):
                warnings.append(f"{context}: quote drift — evidence no longer in current {rel}")
```

To avoid duplicating that block before two `return` statements, compute the excerpt into a variable named `result` and place the warning block once before a single trailing `return result`.

Thread `warnings` through `validate_record(repo, record, ids, warnings)` — pass it to each of the four `validate_source(...)` call sites (premise_failure, decisive_claims, textual_evidence, constraint_projection).

Change `validate_repository` to build the list and return it:

```python
def validate_repository(repo, require_pilot=True, check_generated=True):
    ...
    warnings: list[str] = []
    for r in records:
        validate_record(repo, r, idset, warnings)
    ...
    return records, warnings
```

Update `main()` to unpack and print warnings:

```python
    records, warnings = validate_repository(...)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(json.dumps({
        "records": len(records),
        "warnings": len(warnings),
        "closures_excluding_void": sum(r["status"] in {"closed","invalidated"} for r in records),
        "void_premise": sum(r["status"]=="void-premise" for r in records),
        "status": "ok",
    }, sort_keys=True))
    return 0
```

Update every existing call of `validate_repository` in `tests/test_decision_evidence_index.py` that binds a result to unpack two values. Calls inside `pytest.raises` blocks need no change.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/ -q -k "evidence"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add cgauto/check_decision_evidence_index.py tests/test_decision_evidence_index.py
git commit -m "feat(evidence): warn on quote drift and pending integration"
```

---

### Task 4: Migration script

**Files:**
- Create: `cgauto/migrate_evidence_locators.py`
- Test: `tests/test_evidence_migration.py`

**Interfaces:**
- Consumes: `read_blob` from Task 1; `load_records` from the builder.
- Produces: `migrate_record_text(repo, text, commit) -> str` and `main()`. Writes only the `source` sub-objects of each record's JSON block.

- [ ] **Step 1: Write the failing test**

Create `tests/test_evidence_migration.py`:

```python
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.migrate_evidence_locators import migrate_repo
from tests.test_decision_evidence_index import (
    base_record, git_init_and_commit, make_repo, write_record,
)

def test_migration_pins_commit_and_captures_quote_and_is_idempotent(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    record = base_record()
    record["schema_version"] = 1
    for src in (record["textual_evidence"][0]["source"],
                record["constraint_projection"]["source"]):
        src.pop("commit", None)
    record["decisive_claims"][0]["source"].pop("commit", None)
    write_record(repo, record)
    git_init_and_commit(repo)

    changed = migrate_repo(repo)
    assert changed == 1

    text = (repo / "docs/evidence/records/T1.md").read_text()
    payload = json.loads(
        text.split("<!-- DECISION-EVIDENCE-JSON", 1)[1]
            .split("END-DECISION-EVIDENCE-JSON -->", 1)[0]
    )
    assert payload["schema_version"] == 2
    src = payload["textual_evidence"][0]["source"]
    assert len(src["commit"]) == 40
    assert src["quote"] == "Fixture text."

    assert migrate_repo(repo) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_evidence_migration.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cgauto.migrate_evidence_locators'`

- [ ] **Step 3: Write minimal implementation**

Create `cgauto/migrate_evidence_locators.py`:

```python
#!/usr/bin/env python3
"""Single-use, idempotent migration: pin record citations to the commit that authored them.

Touches only `source` sub-objects and `schema_version`. Never alters claims or prose.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.evidence_git import GitLookupError, read_blob

START = "<!-- DECISION-EVIDENCE-JSON"
END = "END-DECISION-EVIDENCE-JSON -->"

def last_commit_touching(repo: Path, rel: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), "log", "--format=%H", "-1", "--", rel],
        capture_output=True, text=True,
    )
    sha = r.stdout.strip()
    if not sha:
        raise SystemExit(f"no commit found for {rel}")
    return sha

def iter_sources(payload: dict):
    for claim in payload.get("decisive_claims", []):
        yield claim.get("source")
    for ev in payload.get("textual_evidence", []):
        yield ev.get("source")
    cp = payload.get("constraint_projection")
    if isinstance(cp, dict):
        yield cp.get("source")
    pf = payload.get("premise_failure")
    if isinstance(pf, dict):
        yield pf.get("source")

def excerpt_at(repo: Path, commit: str, source: dict) -> str | None:
    locator = source.get("locator")
    if not locator or not locator.startswith("lines "):
        return None
    a, b = (int(x) for x in locator.removeprefix("lines ").split("-"))
    try:
        lines = read_blob(repo, commit, source["path"]).splitlines()
    except GitLookupError:
        return None
    if b > len(lines):
        return None
    return "\n".join(lines[a - 1:b]).strip()

def migrate_record_text(repo: Path, text: str, commit: str) -> str:
    head, rest = text.split(START, 1)
    body, tail = rest.split(END, 1)
    payload = json.loads(body.strip())
    dirty = False
    if payload.get("schema_version") != 2:
        payload["schema_version"] = 2
        dirty = True
    for source in iter_sources(payload):
        if not isinstance(source, dict):
            continue
        if not source.get("commit"):
            source["commit"] = commit
            dirty = True
        if not source.get("quote"):
            quote = excerpt_at(repo, source["commit"], source)
            if quote:
                source["quote"] = quote
                dirty = True
    if not dirty:
        return text
    return (
        head + START + "\n"
        + json.dumps(payload, indent=2, sort_keys=True) + "\n"
        + END + tail
    )

def migrate_repo(repo: Path) -> int:
    changed = 0
    for path in sorted((repo / "docs/evidence/records").glob("*.md")):
        rel = path.relative_to(repo).as_posix()
        commit = last_commit_touching(repo, rel)
        original = path.read_text(encoding="utf-8")
        updated = migrate_record_text(repo, original, commit)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=ROOT)
    args = p.parse_args()
    print(json.dumps({"migrated": migrate_repo(args.repo_root)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_evidence_migration.py -q`
Expected: PASS, 1 test.

- [ ] **Step 5: Commit**

```bash
git add cgauto/migrate_evidence_locators.py tests/test_evidence_migration.py
git commit -m "feat(evidence): add idempotent locator migration"
```

---

### Task 5: Run the migration and ratify the 11 records

**Files:**
- Modify: `docs/evidence/records/*.md` (11 files, via the script)
- Modify: `cgauto/check_decision_evidence_index.py` (acceptance states)
- Modify: `docs/evidence/generated/*` (regenerated)

**Interfaces:**
- Consumes: `migrate_repo` from Task 4.
- Produces: 11 records at `schema_version: 2` with pinned commits, `acceptance.state == "accepted"`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_decision_evidence_index.py`:

```python
def test_accepted_state_is_allowed(tmp_path):
    record = base_record()
    record["acceptance"] = {"state": "accepted", "author": "a", "reviewer": "b"}
    repo = make_repo(tmp_path, record=record)
    validate_repository(repo, require_pilot=False, check_generated=True)

def test_unknown_acceptance_state_rejected(tmp_path):
    record = base_record()
    record["acceptance"] = {"state": "rubber-stamped", "author": "a", "reviewer": "b"}
    repo = make_repo(tmp_path, record=record)
    with pytest.raises(ValidationError, match="acceptance state"):
        validate_repository(repo, require_pilot=False, check_generated=False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_decision_evidence_index.py -q -k acceptance`
Expected: FAIL — current code raises `pilot record must be proposed`.

- [ ] **Step 3: Write minimal implementation**

In `check_decision_evidence_index.py`, add near `ALLOWED_STATUS`:

```python
ALLOWED_ACCEPTANCE = {"proposed", "accepted"}
```

Replace lines 129-130:

```python
    if record["acceptance"].get("state") not in ALLOWED_ACCEPTANCE:
        raise ValidationError(f"{rid}: invalid acceptance state")
```

Then run the migration and ratify, from the repo root:

```bash
python3 cgauto/migrate_evidence_locators.py
python3 -c "
import json,pathlib
for p in sorted(pathlib.Path('docs/evidence/records').glob('*.md')):
    t=p.read_text(); s='<!-- DECISION-EVIDENCE-JSON'; e='END-DECISION-EVIDENCE-JSON -->'
    head,rest=t.split(s,1); body,tail=rest.split(e,1)
    d=json.loads(body.strip()); d['acceptance']['state']='accepted'
    p.write_text(head+s+'\n'+json.dumps(d,indent=2,sort_keys=True)+'\n'+e+tail)
print('ratified')
"
python3 cgauto/build_decision_evidence_index.py
python3 cgauto/check_decision_evidence_index.py
```

- [ ] **Step 4: Verify**

Run: `python3 cgauto/check_decision_evidence_index.py`
Expected: exit 0, JSON summary printed, `"records": 11`. Any `warning:` lines on stderr are acceptable and expected for records whose evidence has since been reworded.

Run: `python3 -m pytest tests/ -q -k evidence`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add cgauto/check_decision_evidence_index.py docs/evidence/records docs/evidence/generated tests/test_decision_evidence_index.py
git commit -m "feat(evidence): migrate citations to pinned commits and ratify pilot records"
```

---

### Task 6: Hypothesis tier

**Files:**
- Create: `cgauto/evidence_hypotheses.py`
- Create: `tests/test_evidence_hypotheses.py`
- Create: `docs/evidence/hypotheses/.gitkeep`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `HYPOTHESIS_REQUIRED`, `ALLOWED_HYPOTHESIS_STATUS`, `load_hypotheses(repo) -> list[dict]`, `validate_hypothesis(h, record_ids) -> None`, `HypothesisError`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_evidence_hypotheses.py`:

```python
from __future__ import annotations
import json, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.evidence_hypotheses import (
    HypothesisError, load_hypotheses, validate_hypothesis,
)

START = "<!-- HYPOTHESIS-JSON"
END = "END-HYPOTHESIS-JSON -->"

def base_hypothesis():
    return {
        "id": "Q1",
        "question": "Is v4 the best rebuild base?",
        "origin": ["coordination/messages/chatgpt_1/20260807T112000Z-x.md"],
        "positions": [
            {"agent": "chatgpt_1", "stance": "v4 is least-bad reference"},
            {"agent": "claude_1", "stance": "no independent view"},
        ],
        "status": "open",
        "next_action": "Re-run the panel on v4 and v1 and compare blocking counts.",
    }

def write_hypothesis(repo: Path, h: dict):
    d = repo / "docs/evidence/hypotheses"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{h['id']}.md").write_text(
        f"# {h['id']}\n\n{START}\n{json.dumps(h, indent=2, sort_keys=True)}\n{END}\n"
    )

def test_minimal_hypothesis_validates(tmp_path):
    write_hypothesis(tmp_path, base_hypothesis())
    hs = load_hypotheses(tmp_path)
    assert len(hs) == 1
    validate_hypothesis(hs[0], record_ids=set())

def test_missing_field_rejected(tmp_path):
    h = base_hypothesis()
    del h["next_action"]
    with pytest.raises(HypothesisError, match="next_action"):
        validate_hypothesis(h, record_ids=set())

def test_bad_status_rejected(tmp_path):
    h = base_hypothesis()
    h["status"] = "kinda-open"
    with pytest.raises(HypothesisError, match="status"):
        validate_hypothesis(h, record_ids=set())

def test_resolved_requires_graduation_link(tmp_path):
    h = base_hypothesis()
    h["status"] = "resolved"
    with pytest.raises(HypothesisError, match="graduat"):
        validate_hypothesis(h, record_ids={"D101"})
    h["graduated_to"] = "D101"
    validate_hypothesis(h, record_ids={"D101"})

def test_graduation_target_must_exist(tmp_path):
    h = base_hypothesis()
    h["status"] = "resolved"
    h["graduated_to"] = "NOPE"
    with pytest.raises(HypothesisError, match="unknown record"):
        validate_hypothesis(h, record_ids={"D101"})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_evidence_hypotheses.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'cgauto.evidence_hypotheses'`

- [ ] **Step 3: Write minimal implementation**

Create `cgauto/evidence_hypotheses.py`:

```python
#!/usr/bin/env python3
"""Lightweight open-question tier. Entry cost is deliberately low; rigour is the closing tax."""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any

START = "<!-- HYPOTHESIS-JSON"
END = "END-HYPOTHESIS-JSON -->"
ID_RE = re.compile(r"^Q\d+$")
HYPOTHESIS_REQUIRED = {
    "id", "question", "origin", "positions", "status", "next_action",
}
ALLOWED_HYPOTHESIS_STATUS = {"open", "investigating", "resolved", "void"}

class HypothesisError(ValueError):
    pass

def extract_hypothesis(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise HypothesisError(f"{path}: missing HYPOTHESIS-JSON block")
    return json.loads(text.split(START, 1)[1].split(END, 1)[0].strip())

def load_hypotheses(repo_root: Path) -> list[dict[str, Any]]:
    d = repo_root / "docs/evidence/hypotheses"
    if not d.exists():
        return []
    return sorted(
        (extract_hypothesis(p) for p in sorted(d.glob("*.md"))),
        key=lambda h: int(h["id"][1:]) if ID_RE.match(h.get("id", "")) else 0,
    )

def validate_hypothesis(h: dict[str, Any], record_ids: set[str]) -> None:
    missing = sorted(HYPOTHESIS_REQUIRED - h.keys())
    if missing:
        raise HypothesisError(f"{h.get('id','<unknown>')}: missing fields {missing}")
    hid = h["id"]
    if not ID_RE.match(hid):
        raise HypothesisError(f"{hid}: id must match Q<n>")
    if h["status"] not in ALLOWED_HYPOTHESIS_STATUS:
        raise HypothesisError(f"{hid}: invalid status {h['status']!r}")
    for key in ("question", "next_action"):
        if not isinstance(h[key], str) or not h[key].strip():
            raise HypothesisError(f"{hid}: {key} required")
    for key in ("origin", "positions"):
        if not isinstance(h[key], list) or not h[key]:
            raise HypothesisError(f"{hid}: non-empty {key} required")
    for i, pos in enumerate(h["positions"]):
        if not isinstance(pos, dict) or not pos.get("agent") or not pos.get("stance"):
            raise HypothesisError(f"{hid}.positions[{i}]: agent and stance required")
    if h["status"] == "resolved":
        target = h.get("graduated_to")
        if not target:
            raise HypothesisError(f"{hid}: resolved requires graduated_to record id")
        if target not in record_ids:
            raise HypothesisError(f"{hid}: graduated_to names unknown record {target}")
```

Create `docs/evidence/hypotheses/.gitkeep` (empty file).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_evidence_hypotheses.py -q`
Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add cgauto/evidence_hypotheses.py tests/test_evidence_hypotheses.py docs/evidence/hypotheses/.gitkeep
git commit -m "feat(evidence): add lightweight hypothesis tier"
```

---

### Task 7: Generate OPEN-QUESTIONS.md and wire hypotheses into validation

**Files:**
- Modify: `cgauto/build_decision_evidence_index.py`
- Modify: `cgauto/check_decision_evidence_index.py`
- Modify: `tests/test_evidence_hypotheses.py`

**Interfaces:**
- Consumes: `load_hypotheses`, `validate_hypothesis` from Task 6.
- Produces: generated file `OPEN-QUESTIONS.md`; `render_open_questions(hypotheses) -> str`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_evidence_hypotheses.py`:

```python
from cgauto.build_decision_evidence_index import render_open_questions

def test_open_questions_render_is_deterministic_and_lists_open_first(tmp_path):
    h1 = base_hypothesis()
    h2 = base_hypothesis(); h2["id"] = "Q2"; h2["status"] = "void"
    first = render_open_questions([h1, h2])
    second = render_open_questions([h1, h2])
    assert first == second
    assert "Q1" in first and "Q2" in first
    assert first.index("Q1") < first.index("Q2")
    assert "Is v4 the best rebuild base?" in first
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_evidence_hypotheses.py -q -k open_questions`
Expected: FAIL — `ImportError: cannot import name 'render_open_questions'`

- [ ] **Step 3: Write minimal implementation**

In `build_decision_evidence_index.py`, add to the imports:

```python
from cgauto.evidence_hypotheses import load_hypotheses
```

Add `"OPEN-QUESTIONS.md"` to the `GENERATED` tuple, and add:

```python
STATUS_ORDER = {"open": 0, "investigating": 1, "resolved": 2, "void": 3}

def render_open_questions(hypotheses: list[dict[str, Any]]) -> str:
    ordered = sorted(
        hypotheses,
        key=lambda h: (STATUS_ORDER.get(h["status"], 9), int(h["id"][1:])),
    )
    live = [h for h in ordered if h["status"] in {"open", "investigating"}]
    lines = [
        "# Open questions — the backlog",
        "",
        "Generated from `docs/evidence/hypotheses/`. Do not edit this file by hand.",
        "",
        f"- Live questions: **{len(live)}**",
        f"- Total entries: **{len(ordered)}**",
        "",
        "| ID | Status | Question | Next action |",
        "|---|---|---|---|",
    ]
    for h in ordered:
        q = h["question"].replace("|", "\\|")
        n = h["next_action"].replace("|", "\\|")
        lines.append(
            f"| [{h['id']}](../hypotheses/{h['id']}.md) | `{h['status']}` | {q} | {n} |"
        )
    lines += ["", "## Positions", ""]
    for h in ordered:
        lines.append(f"### {h['id']}")
        for pos in h["positions"]:
            lines.append(f"- **{pos['agent']}** — {pos['stance']}")
        if h.get("graduated_to"):
            lines.append(f"- graduated to [{h['graduated_to']}](../records/{h['graduated_to']}.md)")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
```

Change `expected_outputs` to take hypotheses and include the new file:

```python
def expected_outputs(records, hypotheses=None):
    outputs = {
        "decision-evidence-index.yaml": render_yaml(records),
        "DECISION-EVIDENCE-INDEX.md": render_index(records),
        "CONSTRAINTS-PILOT-PROJECTION.md": render_constraints(records),
        "equivalence-report.md": render_equivalence(records),
    }
    outputs["OPEN-QUESTIONS.md"] = render_open_questions(hypotheses or [])
    return outputs
```

In `build()`, load hypotheses and pass them:

```python
    records = load_records(repo_root)
    hypotheses = load_hypotheses(repo_root)
    outputs = expected_outputs(records, hypotheses)
```

and add `"hypothesis_count": len(hypotheses)` to the manifest dict.

In `check_decision_evidence_index.py`, import and validate them inside `validate_repository`, immediately after the record loop:

```python
from cgauto.evidence_hypotheses import HypothesisError, load_hypotheses, validate_hypothesis
...
    for h in load_hypotheses(repo):
        try:
            validate_hypothesis(h, idset)
        except HypothesisError as exc:
            raise ValidationError(str(exc)) from None
```

and change its `expected_outputs(records)` call to `expected_outputs(records, load_hypotheses(repo))`, plus the manifest check to compare `manifest.get("hypothesis_count")`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/ -q -k evidence`
Expected: PASS.

Run: `python3 cgauto/build_decision_evidence_index.py && python3 cgauto/check_decision_evidence_index.py`
Expected: exit 0; `docs/evidence/generated/OPEN-QUESTIONS.md` now exists.

- [ ] **Step 5: Commit**

```bash
git add cgauto/build_decision_evidence_index.py cgauto/check_decision_evidence_index.py tests/test_evidence_hypotheses.py docs/evidence/generated
git commit -m "feat(evidence): generate OPEN-QUESTIONS backlog view"
```

---

### Task 8: Seed the eight live questions

**Files:**
- Create: `docs/evidence/hypotheses/Q1.md` … `Q8.md`
- Modify: `docs/evidence/generated/OPEN-QUESTIONS.md` (regenerated)

**Interfaces:**
- Consumes: the hypothesis schema from Task 6.
- Produces: eight `Q<n>` entries.

- [ ] **Step 1: Write the seed entries**

Each file follows this exact shape (shown for Q1; repeat the structure for Q2–Q8 with the content below):

```markdown
# Q1 — Is v4 the best rebuild base?

<!-- HYPOTHESIS-JSON
{
  "id": "Q1",
  "question": "Is build_candidate_v4 the best behavioural reference for a minimal banana delta?",
  "origin": [
    "coordination/messages/chatgpt_1/20260807T112000Z-20260807-banana-disposition-review-chatgpt_1-handoff.md",
    "coordination/messages/claude_1/20260807T142000Z-20260807-banana-disposition-review-handoff.md"
  ],
  "positions": [
    {"agent": "chatgpt_1", "stance": "v4 is the least-bad behavioural reference, not a valid base; reapply only the minimal v1/v3/v4 delta."},
    {"agent": "claude_1", "stance": "Records this as a finding it did not independently have; no contrary evidence offered."}
  ],
  "status": "open",
  "next_action": "Run the pinned panel on v1, v3 and v4 against the repaired parent and compare raw D-1/D-4 counts."
}
END-HYPOTHESIS-JSON -->
```

Content for the remaining seven:

| ID | question | status | next_action |
|---|---|---|---|
| Q2 | Is D89a's opponent-production leak repairable without destroying the +79.441 production gain? | investigating | Deliver `20260807-d89a-leak-repairability-scoping`. |
| Q3 | Is raw `D-1 == 0` feasible on this parent given one unlocalised episode (D1-B, 1/35)? | open | Localise D1-B in source, or return `INFEASIBLE` with evidence. |
| Q4 | Do the 29 invariants need a schedule/opponent-production term? | open | Decompose D89a's +82.863 into theft versus opponent own-production and propose an invariant. |
| Q5 | Does `pre_review.py` earn its place? | open | Identify one failure it demonstrably prevented; if none, retire it. |
| Q6 | Are D-2, D-3 and D-8 correct but unexercised, or dead? | open | Write exercising fixtures; if none can be constructed, mark `UNPROVEN` permanently. |
| Q7 | Should terminal D-7 use post-`C_T` referee state instead of command-text inference? | open | Implement the post-`C_T` rule behind a flag and diff blocking counts on the pinned panel. |
| Q8 | Is the P4 world-state calibration ratifiable as standing gate policy? | open | Re-run the floor self-test with and without P4 calibration and compare against known-good behaviour. |

Positions and origins for Q2–Q8 come from `docs/HARDENING-PLAN-CONSOLIDATED-2026-08-07.md` §1 and §3 and the two disposition handoffs; cite the exact message paths already listed there.

- [ ] **Step 2: Verify they validate**

Run: `python3 cgauto/build_decision_evidence_index.py && python3 cgauto/check_decision_evidence_index.py`
Expected: exit 0. `docs/evidence/generated/OPEN-QUESTIONS.md` lists 8 entries, 7 live and Q2 as `investigating`.

- [ ] **Step 3: Run the full suite**

Run: `python3 -m pytest tests/ -q -k evidence`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add docs/evidence/hypotheses docs/evidence/generated
git commit -m "feat(evidence): seed eight live open questions"
```

---

### Task 9: Update SCHEMA.md to version 2

**Files:**
- Modify: `docs/evidence/SCHEMA.md`

**Interfaces:**
- Consumes: everything above.
- Produces: documentation only.

- [ ] **Step 1: Update the schema document**

Change `Version: \`1\`` to `Version: \`2\``. Replace the "Required record fields" numeric-claim bullet list so it documents the pinned source:

```markdown
Every `source` is a git-pinned coordinate:

- `commit` — 40-character SHA. Hard error if it does not resolve; warning
  (`pending integration`) if it resolves but is not yet an ancestor of `origin/main`.
- `path` — repo-relative path as it existed at `commit`.
- exactly one of `locator` (`lines N-M`, interpreted at that commit) or `json_pointer`.
- `quote` — optional verbatim excerpt. Used only for the currency check: if it no longer
  appears in the *current* file, the validator warns. It never fails the build.

Line numbers are meaningless without their commit: `docs/CONSTRAINTS.md` is append-heavy and
every insertion shifts all citations below it. Pinning is what makes a citation permanent.
```

Add a new section documenting the hypothesis tier:

```markdown
## Hypothesis tier

`docs/evidence/hypotheses/Q<n>.md` carries a `HYPOTHESIS-JSON` block with six required fields:
`id`, `question`, `origin` (exact v2 message paths), `positions` (agent + stance),
`status` (`open` / `investigating` / `resolved` / `void`), and `next_action`.

Entry cost is deliberately low — the 21-field record schema is the closing tax, not the entry
tax. A `resolved` hypothesis requires `graduated_to`, naming an existing record id; the
lightweight entry is never deleted, because the trail from question to answer is the product.

`generated/OPEN-QUESTIONS.md` is the backlog view. Like everything in `generated/`, it is
deterministic and must never be hand-edited.
```

- [ ] **Step 2: Verify nothing regressed**

Run: `python3 -m pytest tests/ -q -k evidence && python3 cgauto/check_decision_evidence_index.py`
Expected: PASS and exit 0.

- [ ] **Step 3: Commit**

```bash
git add docs/evidence/SCHEMA.md
git commit -m "docs(evidence): document schema v2 and the hypothesis tier"
```

---

## Final verification

- [ ] `python3 -m pytest tests/ -q` — full repository suite green.
- [ ] `python3 cgauto/check_decision_evidence_index.py` — exit 0, `"records": 11`.
- [ ] `python3 cgauto/build_decision_evidence_index.py --check` — generated outputs match.
- [ ] `sha256sum rust/src/bin/yamo_orchard_live.rs` starts `fff6669b`.
- [ ] `git status --short` clean.
