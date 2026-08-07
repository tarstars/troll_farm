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
