from __future__ import annotations
import os, subprocess, sys
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

NON_ASCII_TEXT = "em dash — and minus − and en dash –\n"

def test_read_blob_round_trips_non_ascii_content(tmp_path):
    repo = init_repo(tmp_path)
    sha = commit_file(repo, "f.md", NON_ASCII_TEXT)
    assert read_blob(repo, sha, "f.md") == NON_ASCII_TEXT

def test_read_blob_is_locale_independent_under_c_locale(tmp_path):
    """Reproduces the reviewer's failure: under `LC_ALL=C`, decoding git's
    subprocess output without an explicit `encoding="utf-8"` either raises
    UnicodeDecodeError (ascii codec) or silently mis-decodes (latin-1-style
    codecs). Drive read_blob from a real subprocess with LC_ALL=C so the
    locale actually governs stdio decoding, and assert the exact non-ASCII
    string round-trips."""
    repo = init_repo(tmp_path)
    sha = commit_file(repo, "f.md", NON_ASCII_TEXT)
    root = Path(__file__).resolve().parents[1]
    script = (
        "import sys; sys.path.insert(0, %r)\n"
        "from pathlib import Path\n"
        "from cgauto.evidence_git import read_blob\n"
        "sys.stdout.buffer.write(read_blob(Path(%r), %r, 'f.md').encode('utf-8'))\n"
    ) % (str(root), str(repo), sha)
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    # Disable both the C-locale-coercion (PEP 538) and UTF-8-mode (PEP 540)
    # fallbacks that Python normally uses to paper over a "C" locale, so this
    # test actually exercises ascii-codec decoding the way a minimal/older
    # environment would, rather than the auto-coerced-to-UTF-8 sandbox default.
    env["PYTHONCOERCECLOCALE"] = "0"
    env["PYTHONUTF8"] = "0"
    env.pop("PYTHONIOENCODING", None)
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, env=env,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stdout.decode("utf-8") == NON_ASCII_TEXT
