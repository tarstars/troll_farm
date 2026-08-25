"""The publish wrapper's lint gate cannot be disarmed by invocation (G5 F1).

The defect being removed lived in how the lint was CALLED:
``lint | tail -3 && commit && push`` gated on tail, not the lint. The wrapper
owns the call; these tests prove the gate blocks and that publish works,
against a local bare origin and a lint shim whose exit code is the fixture.
"""
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WRAPPER = REPO / "scripts" / "publish_outbox.sh"


def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd,
                          capture_output=True, text=True)


def _setup(tmp_path, lint_exit):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    work = tmp_path / "work"
    work.mkdir()
    for args in (("init", "-q"), ("checkout", "-q", "-b", "agent/testbot"),
                 ("remote", "add", "origin", str(origin)),
                 ("config", "user.email", "t@example.com"),
                 ("config", "user.name", "t")):
        assert _git(*args, cwd=work).returncode == 0
    (work / "scripts").mkdir()
    shutil.copy(WRAPPER, work / "scripts" / "publish_outbox.sh")
    shim = work / "scripts" / "lint_outbox.py"
    shim.write_text("import sys\nsys.stderr.write('shim lint\\n')\n"
                    "sys.exit(%d)\n" % lint_exit)
    (work / "msg.md").write_text("payload\n")
    assert _git("add", "msg.md", "scripts", cwd=work).returncode == 0
    return work


def _run_wrapper(work):
    return subprocess.run(
        ["bash", "scripts/publish_outbox.sh", "testbot", "published by test"],
        cwd=work, capture_output=True, text=True)


def test_lint_failure_blocks_commit_and_push(tmp_path):
    work = _setup(tmp_path, lint_exit=1)
    result = _run_wrapper(work)
    assert result.returncode != 0
    assert _git("log", "-1", cwd=work).returncode != 0  # no commit exists
    ls = _git("ls-remote", "origin", "agent/testbot", cwd=work)
    assert ls.stdout.strip() == ""  # nothing pushed


def test_lint_pass_publishes_and_remote_verifies(tmp_path):
    work = _setup(tmp_path, lint_exit=0)
    result = _run_wrapper(work)
    assert result.returncode == 0, result.stderr
    assert "remote verified" in result.stdout
    ls = _git("ls-remote", "origin", "agent/testbot", cwd=work)
    assert ls.stdout.strip() != ""  # branch exists on origin


def test_wrong_branch_refused(tmp_path):
    work = _setup(tmp_path, lint_exit=0)
    assert _git("checkout", "-q", "-b", "main", cwd=work).returncode == 0
    result = _run_wrapper(work)
    assert result.returncode != 0
    assert "refusing" in result.stderr
