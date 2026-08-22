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


def _with_origin(rdir):
    # a remote named "origin" (pointing at the repo itself is enough) makes
    # register_handoff's `git fetch` guard fire.
    subprocess.run(["git", "-C", str(rdir), "remote", "add", "origin", str(rdir)],
                   check=True, capture_output=True)


def test_handoff_fetch_has_a_timeout(tmp_path, repo, monkeypatch):
    rdir, commit = repo
    _with_origin(rdir)
    store, gen = _store(tmp_path, rdir)

    orig_run = coordd.subprocess.run
    calls = []

    def spy_run(cmd, **kwargs):
        if "fetch" in cmd:
            calls.append(kwargs)
        return orig_run(cmd, **kwargs)

    monkeypatch.setattr(coordd.subprocess, "run", spy_run)
    store.register_handoff("a1", "t1", gen, "agent/a1", commit, ["result.md"])
    assert calls, "expected a `git fetch` subprocess call"
    assert calls[0].get("timeout") == 60


def test_handoff_survives_fetch_timeout(tmp_path, repo, monkeypatch):
    rdir, commit = repo
    _with_origin(rdir)
    store, gen = _store(tmp_path, rdir)

    orig_run = coordd.subprocess.run

    def flaky_run(cmd, **kwargs):
        if "fetch" in cmd:
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 60))
        return orig_run(cmd, **kwargs)

    monkeypatch.setattr(coordd.subprocess, "run", flaky_run)
    # must not raise: fetch timeout falls back to verifying against the
    # existing clone state instead of failing the handoff outright.
    got = store.register_handoff("a1", "t1", gen, "agent/a1", commit, ["result.md"])
    assert got["verified"] is True
