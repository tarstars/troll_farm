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
