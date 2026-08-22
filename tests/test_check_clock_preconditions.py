"""G3 — precondition audit (guards task 20260810): check_clock on a repo
whose precondition (at least one ref) does not hold.

Found while demoing G5 F8: ``check_clock.main`` raised a raw ValueError on a
zero-commit repo, aborting any caller (coordctl's doctor) before the other
checks could report. A guard that crashes on its precondition takes the whole
doctor down with it; it must report and fail closed instead.
"""
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_clock


def test_zero_commit_repo_fails_closed_with_message(tmp_path, capsys):
    repo = tmp_path / "empty"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    rc = check_clock.main(repo=str(repo))
    out = capsys.readouterr().out
    assert rc == 2
    assert "no refs" in out
