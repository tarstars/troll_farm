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
