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
