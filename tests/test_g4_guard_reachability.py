"""G4 — guards that no test previously reached (guards task 20260810, G4).

Three groups: coordctl's UNREADABLE-origin branch (G5 F8), check_ref_census's
dead-worktree branch (G5 F9) — both previously demonstrated live only — and
coordd_mirror's CLI wiring, whose URL/env resolution lived unreachable inside
the ``__main__`` body (the instance-2 class from the task table).
"""
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_ref_census as crc
import coordctl
import coordd_mirror

ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def _g(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True,
                          capture_output=True, text=True, env=dict(ENV))


def _one_commit_repo(tmp_path, name="r"):
    repo = tmp_path / name
    (repo / "rust/src/bin").mkdir(parents=True)
    (repo / "scripts").mkdir()
    (repo / "rust/src/bin/yamo_orchard_live.rs").write_text("dummy\n")
    (repo / "scripts/inbox_sweep.py").write_text("dummy\n")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _g(repo, "add", "-A")
    _g(repo, "commit", "-qm", "fixture")
    return repo


def test_doctor_reports_unreadable_origin_distinctly(tmp_path, capsys):
    """F8: no origin/main must read UNREADABLE, not a fake DRIFT."""
    repo = _one_commit_repo(tmp_path)
    rc = coordctl._doctor(str(repo))
    out = capsys.readouterr().out
    assert rc == 2
    assert "UNREADABLE origin/main" in out
    assert "DRIFT" not in out


def test_census_shouts_when_worktree_uninspectable(tmp_path, capsys):
    """F9: a stale worktree entry must be reported, not silently skipped."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    repo = _one_commit_repo(tmp_path)
    _g(repo, "remote", "add", "origin", str(origin))
    _g(repo, "push", "-q", "origin", "HEAD:main")
    wt = tmp_path / "stale-wt"
    _g(repo, "worktree", "add", "--detach", "-q", str(wt))
    subprocess.run(["rm", "-rf", str(wt)], check=True)
    crc.main(repo=str(repo), remote="origin")
    out = capsys.readouterr().out
    assert "could not inspect worktree" in out
    assert str(wt) in out


def test_mirror_cli_url_resolution_env_then_flag(tmp_path, monkeypatch, capsys):
    """coordd_mirror: env COORDD_URL is honored and --url overrides it."""
    seen = []
    monkeypatch.setattr(coordd_mirror, "_default_post_factory",
                        lambda url, token: seen.append((url, token)) or (lambda p: None))
    root = tmp_path / "messages"
    root.mkdir()
    cursor = tmp_path / "cursor.json"

    monkeypatch.setenv("COORDD_URL", "http://from-env:1")
    rc = coordd_mirror.cli(["--root", str(root), "--cursor", str(cursor)])
    assert rc == 0
    assert seen[-1] == ("http://from-env:1", None)
    assert "mirrored 0 new message(s)" in capsys.readouterr().out

    rc = coordd_mirror.cli(["--root", str(root), "--cursor", str(cursor),
                            "--url", "http://from-flag:2", "--token", "tk"])
    assert rc == 0
    assert seen[-1] == ("http://from-flag:2", "tk")
