"""Tests for the authoritative inbox sweep (transport schema v2).

Covers the 17 required areas of
coordination/tasks/20260805-coordination-transport-hardening.md with temporary
Git repositories (tempfile + `git init --bare` fake origin) plus the retained
legacy parsing unit tests. Integration tests run the CLI as a subprocess and
assert exit codes and authoritative counts from its output.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

from scripts import inbox_sweep

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "inbox_sweep.py"

ME = "local_codex_1"
PEER = "claude_1"
THIRD = "chatgpt_1"


# ---------------------------------------------------------------------------
# Fixture: temporary origin + clone with plumbing-based multi-branch publishing
# ---------------------------------------------------------------------------

class TransportRepo:
    def __init__(self, tmp_path: pathlib.Path) -> None:
        self.origin = tmp_path / "origin.git"
        self.work = tmp_path / "work"
        subprocess.run(
            ["git", "init", "-q", "--bare", str(self.origin)], check=True
        )
        subprocess.run(
            ["git", "clone", "-q", str(self.origin), str(self.work)],
            check=True,
            capture_output=True,
        )
        self._git("config", "user.name", "test")
        self._git("config", "user.email", "test@example.invalid")
        self.tips: dict[str, str] = {}

    def _git(self, *args: str, env: dict | None = None) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=self.work,
            capture_output=True,
            text=True,
            env=env,
        )
        assert proc.returncode == 0, f"git {args} failed: {proc.stderr}"
        return proc.stdout.strip()

    def commit(
        self,
        branch: str,
        files: dict[str, str],
        message: str = "msg",
        push: bool = True,
    ) -> str:
        """Commit files onto `branch` (chained per branch) via plumbing.

        push=True publishes to the fake origin and fetches, so the content
        appears under refs/remotes/origin/<branch>. push=False leaves a
        local-only branch ref.
        """
        env = dict(
            os.environ,
            GIT_INDEX_FILE=str(
                self.work / ".git" / ("idx-" + branch.replace("/", "-"))
            ),
        )
        parent = self.tips.get(branch)
        if parent:
            self._git("read-tree", parent, env=env)
        else:
            self._git("read-tree", "--empty", env=env)
        for path, content in files.items():
            blob = subprocess.run(
                ["git", "hash-object", "-w", "--stdin"],
                cwd=self.work,
                input=content,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            self._git(
                "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}",
                env=env,
            )
        tree = self._git("write-tree", env=env)
        args = ["commit-tree", tree, "-m", message]
        if parent:
            args += ["-p", parent]
        commit = self._git(*args)
        self.tips[branch] = commit
        if push:
            self._git("push", "-q", "--force", "origin", f"{commit}:refs/heads/{branch}")
            self._git("fetch", "-q", "origin")
        else:
            self._git("update-ref", f"refs/heads/{branch}", commit)
        return commit

    def write_worktree(self, path: str, content: str) -> None:
        full = self.work / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")

    def sweep(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.work,
            capture_output=True,
            text=True,
        )

    def seen_file(self, me: str = ME) -> pathlib.Path:
        return self.work / me / "inbox-seen.json"


@pytest.fixture()
def repo(tmp_path: pathlib.Path) -> TransportRepo:
    return TransportRepo(tmp_path)


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------

def msg_path(sender: str, stamp: str, task: str, kind: str) -> str:
    return f"coordination/messages/{sender}/{stamp}-{task}-{kind}.md"


def v2_message(
    path: str,
    *,
    kind: str,
    task: str,
    sender: str,
    to: str = ME,
    requires_ack: bool | None = None,
    ack_for: tuple[str, ...] = (),
    supersedes: tuple[str, ...] = (),
    extra_fields: dict[str, str] | None = None,
    overrides: dict[str, str] | None = None,
) -> str:
    if requires_ack is None:
        requires_ack = kind in inbox_sweep.ACK_REQUIRED_KINDS
    fields = {
        "schema_version": "2",
        "type": kind,
        "task_id": task,
        "from": sender,
        "to": to,
        "cc": "[]",
        "message_id": path,
        "requires_ack": "true" if requires_ack else "false",
        "ack_for": json.dumps(list(ack_for)),
        "supersedes": json.dumps(list(supersedes)),
        "created_utc": "2026-08-05T10:00:00Z",
    }
    fields.update(extra_fields or {})
    fields.update(overrides or {})
    lines = ["---"] + [f"{k}: {v}" for k, v in fields.items()] + ["---", "", "# body", ""]
    return "\n".join(lines)


def legacy_message(task: str, to: str = ME, requires: str = "yes") -> str:
    return (
        f"# message: {task}\n\n"
        f"- To: {to}\n"
        f"- Task: {task}\n"
        f"- Requires acknowledgement: {requires}\n\n"
        "body\n"
    )


def counts(stdout: str) -> dict[str, int]:
    found = {}
    for label in (
        "immutable-path collisions",
        "delivery errors",
        "quarantine errors",
        "quarantined",
        "new (unseen)",
        "unacknowledged, ack required",
        "local diagnostics — unpublished, NOT authoritative",
    ):
        m = re.search(re.escape(label) + r" \((\d+)\):", stdout)
        if m:
            found[label] = int(m.group(1))
    return found


def publish_v2(
    repo: TransportRepo,
    sender: str,
    stamp: str,
    task: str,
    kind: str,
    branch: str | None = None,
    push: bool = True,
    **kwargs,
) -> str:
    """Publish one v2 message on the sender's canonical branch (by default)."""
    path = msg_path(sender, stamp, task, kind)
    body = v2_message(path, kind=kind, task=task, sender=sender, **kwargs)
    repo.commit(branch or f"agent/{sender}", {path: body}, push=push)
    return path


# ---------------------------------------------------------------------------
# 1. checked fetch failure prints stderr and exits 2
# ---------------------------------------------------------------------------

def test_fetch_failure_prints_stderr_and_exits_2(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    repo._git("remote", "set-url", "origin", str(repo.work / "does-not-exist"))

    result = repo.sweep("--me", ME, "--fetch")

    assert result.returncode == 2
    assert result.stderr.strip()  # git stderr surfaced
    assert "STALE / NOT AUTHORITATIVE" in result.stdout
    # No message or ACK state claimed.
    assert "unacknowledged" not in result.stdout


# ---------------------------------------------------------------------------
# 2. an unpushed working-tree ACK does not acknowledge a remote handoff
# ---------------------------------------------------------------------------

def test_worktree_ack_does_not_acknowledge_remote_message(repo):
    q = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    ack_path = msg_path(ME, "20260805T110000Z", "task-a", "ack")
    repo.write_worktree(
        ack_path,
        v2_message(ack_path, kind="ack", task="task-a", sender=ME, to=PEER,
                   ack_for=(q,)),
    )

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 1
    assert c["unacknowledged, ack required"] == 1
    assert q in result.stdout

    # Visible only as a diagnostic, never changing counts or exit status.
    diag = repo.sweep("--me", ME, "--include-local")
    dc = counts(diag.stdout)
    assert diag.returncode == 1
    assert dc["unacknowledged, ack required"] == 1
    assert dc["local diagnostics — unpublished, NOT authoritative"] == 1
    assert f"{ack_path}   [worktree]" in diag.stdout


# ---------------------------------------------------------------------------
# 3. a local-branch-only ACK does not acknowledge a remote handoff
# ---------------------------------------------------------------------------

def test_local_branch_ack_does_not_acknowledge_remote_message(repo):
    q = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    publish_v2(
        repo, ME, "20260805T110000Z", "task-a", "ack",
        to=PEER, ack_for=(q,), push=False,
    )

    result = repo.sweep("--me", ME)
    assert result.returncode == 1
    assert counts(result.stdout)["unacknowledged, ack required"] == 1


# ---------------------------------------------------------------------------
# 4./5. exact ack_for acknowledges only the listed paths; same-task messages
#       are independent unless both paths are listed
# ---------------------------------------------------------------------------

def test_remote_v2_ack_covers_exactly_the_listed_paths(repo):
    q1 = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    q2 = publish_v2(repo, PEER, "20260805T100100Z", "task-a", "question")
    publish_v2(repo, ME, "20260805T110000Z", "task-a", "ack", to=PEER, ack_for=(q1,))

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 1
    assert c["delivery errors"] == 0
    assert c["unacknowledged, ack required"] == 1
    assert q2 in result.stdout
    assert f"  {q1}   [" not in result.stdout.split("unacknowledged")[1]

    publish_v2(
        repo, ME, "20260805T120000Z", "task-a", "ack", to=PEER, ack_for=(q1, q2),
    )
    result = repo.sweep("--me", ME)
    assert result.returncode == 0
    assert counts(result.stdout)["unacknowledged, ack required"] == 0


# ---------------------------------------------------------------------------
# 6. a legacy task/time ACK covers only an earlier legacy message,
#    and never a v2 message
# ---------------------------------------------------------------------------

def test_legacy_ack_covers_only_earlier_legacy_messages(repo):
    early = msg_path(PEER, "20260805T090000Z", "task-a", "handoff")
    late = msg_path(PEER, "20260805T130000Z", "task-a", "question")
    repo.commit(f"agent/{PEER}", {early: legacy_message("task-a")})
    repo.commit(f"agent/{PEER}", {late: legacy_message("task-a")})
    ack = msg_path(ME, "20260805T100000Z", "task-a", "ack")
    repo.commit(f"agent/{ME}", {ack: legacy_message("task-a", to=PEER, requires="no")})

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 1
    assert c["unacknowledged, ack required"] == 1
    assert late in result.stdout
    assert f"  {early}" not in result.stdout.split("unacknowledged")[1]


def test_legacy_ack_never_acknowledges_a_v2_message(repo):
    v2 = publish_v2(repo, PEER, "20260805T090000Z", "task-a", "question")
    ack = msg_path(ME, "20260805T100000Z", "task-a", "ack")
    repo.commit(f"agent/{ME}", {ack: legacy_message("task-a", to=PEER, requires="no")})

    result = repo.sweep("--me", ME)
    assert result.returncode == 1
    assert counts(result.stdout)["unacknowledged, ack required"] == 1
    assert v2 in result.stdout


# ---------------------------------------------------------------------------
# 7. a v2 message with an older timestamp is new when its path is unseen
# ---------------------------------------------------------------------------

def test_out_of_order_older_timestamp_is_new_when_path_unseen(repo):
    seen = publish_v2(repo, PEER, "20260805T120000Z", "task-a", "update",
                      requires_ack=False)
    repo.seen_file().parent.mkdir(parents=True, exist_ok=True)
    repo.seen_file().write_text(
        json.dumps({
            "schema_version": 1,
            "migrated_watermark": None,
            "seen_message_paths": [seen],
        }) + "\n",
        encoding="utf-8",
    )
    older = publish_v2(repo, PEER, "20260801T000000Z", "task-b", "update",
                       requires_ack=False)

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 0
    assert c["new (unseen)"] == 1
    assert older in result.stdout


# ---------------------------------------------------------------------------
# 8. --mark records selected addressed remote paths only, unacked unchanged
# ---------------------------------------------------------------------------

def test_mark_records_only_selected_addressed_remote_paths(repo):
    p1 = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    p2 = publish_v2(repo, PEER, "20260805T100100Z", "task-b", "question")

    result = repo.sweep("--me", ME, "--task", "task-a", "--mark")
    assert result.returncode == 1  # marking seen does not acknowledge
    assert counts(result.stdout)["unacknowledged, ack required"] == 1

    state = json.loads(repo.seen_file().read_text(encoding="utf-8"))
    assert state["seen_message_paths"] == [p1]

    follow = repo.sweep("--me", ME)
    c = counts(follow.stdout)
    assert follow.returncode == 1
    assert c["new (unseen)"] == 1
    assert p2 in follow.stdout
    assert c["unacknowledged, ack required"] == 2


# ---------------------------------------------------------------------------
# 9. first-run migration honors the legacy watermark without rewriting it
# ---------------------------------------------------------------------------

def test_first_run_migration_honors_legacy_watermark(repo):
    old = publish_v2(repo, PEER, "20260801T000000Z", "task-old", "update",
                     requires_ack=False)
    new = publish_v2(repo, PEER, "20260805T100000Z", "task-new", "update",
                     requires_ack=False)
    watermark_file = repo.work / ME / "inbox-watermark.txt"
    watermark_file.parent.mkdir(parents=True, exist_ok=True)
    watermark_file.write_text("20260803T000000Z\n", encoding="utf-8")

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 0
    assert c["new (unseen)"] == 1
    assert new in result.stdout
    assert watermark_file.read_text(encoding="utf-8") == "20260803T000000Z\n"
    assert not repo.seen_file().exists()

    marked = repo.sweep("--me", ME, "--mark")
    assert marked.returncode == 0
    state = json.loads(repo.seen_file().read_text(encoding="utf-8"))
    assert state["migrated_watermark"] == "20260803T000000Z"
    assert state["seen_message_paths"] == sorted([old, new])
    # Legacy watermark file untouched.
    assert watermark_file.read_text(encoding="utf-8") == "20260803T000000Z\n"


# ---------------------------------------------------------------------------
# 9b. seen-state schema is validated strictly (integrator revision 2):
#     schema_version must be exactly 1 and migrated_watermark string-or-null;
#     malformed state exits 2 without marking anything.
# ---------------------------------------------------------------------------

def write_seen_state_file(repo: TransportRepo, payload: dict) -> str:
    repo.seen_file().parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload) + "\n"
    repo.seen_file().write_text(text, encoding="utf-8")
    return text


def assert_malformed_seen_state(repo: TransportRepo, original: str, field: str):
    # Even with --mark, a malformed seen-state file must exit 2, name the bad
    # field loudly, and leave the file byte-identical (nothing marked).
    result = repo.sweep("--me", ME, "--mark")
    assert result.returncode == 2
    assert "malformed seen-state file" in result.stderr
    assert field in result.stderr
    assert repo.seen_file().read_text(encoding="utf-8") == original


def test_seen_state_missing_schema_version_fails(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    original = write_seen_state_file(
        repo, {"migrated_watermark": None, "seen_message_paths": []}
    )
    assert_malformed_seen_state(repo, original, "schema_version")


def test_seen_state_unsupported_schema_version_fails(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    original = write_seen_state_file(
        repo,
        {"schema_version": 2, "migrated_watermark": None, "seen_message_paths": []},
    )
    assert_malformed_seen_state(repo, original, "schema_version")


def test_seen_state_non_string_migrated_watermark_fails(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    original = write_seen_state_file(
        repo,
        {
            "schema_version": 1,
            "migrated_watermark": 20260801,
            "seen_message_paths": [],
        },
    )
    assert_malformed_seen_state(repo, original, "migrated_watermark")


# ---------------------------------------------------------------------------
# 10. different bytes at one immutable path across remote refs exit 2
# ---------------------------------------------------------------------------

def test_immutable_path_collision_across_remote_refs_exits_2(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{PEER}", {path: body})
    repo.commit(f"agent/{PEER}-side", {path: body + "tampered\n"})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["immutable-path collisions"] == 1
    assert path in result.stdout


def test_identical_copies_across_remote_refs_deduplicate(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{PEER}", {path: body})
    repo.commit(f"agent/{PEER}-side", {path: body})

    result = repo.sweep("--me", ME)
    assert result.returncode == 0
    assert counts(result.stdout)["immutable-path collisions"] == 0
    assert counts(result.stdout)["new (unseen)"] == 1


# ---------------------------------------------------------------------------
# 11./12./13. canonical handoff artifact validation
# ---------------------------------------------------------------------------

def handoff_fields(ref: str, commit: str, paths: list[str]) -> dict[str, str]:
    return {
        "artifact_ref": ref,
        "artifact_commit": commit,
        "artifact_paths": json.dumps(paths),
    }


def test_handoff_artifacts_only_on_task_branch_fails(repo):
    artifacts = {"claude_1/example/source.rs": "fn main() {}\n"}
    task_commit = repo.commit(f"agent/{PEER}-task", artifacts)
    repo.commit(f"agent/{PEER}", {"claude_1/README.md": "canonical\n"})
    publish_v2(
        repo, PEER, "20260805T100000Z", "task-a", "handoff",
        extra_fields=handoff_fields(
            f"agent/{PEER}", task_commit, ["claude_1/example/source.rs"]
        ),
    )

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["delivery errors"] >= 1
    assert "not reachable" in result.stdout


def test_handoff_artifact_ref_naming_task_branch_fails(repo):
    artifacts = {"claude_1/example/source.rs": "fn main() {}\n"}
    task_commit = repo.commit(f"agent/{PEER}-task", artifacts)
    publish_v2(
        repo, PEER, "20260805T100000Z", "task-a", "handoff",
        extra_fields=handoff_fields(
            f"agent/{PEER}-task", task_commit, ["claude_1/example/source.rs"]
        ),
    )

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "canonical branch" in result.stdout


def test_canonical_handoff_with_reachable_commit_and_paths_passes(repo):
    artifacts = {
        "claude_1/example/source.rs": "fn main() {}\n",
        "claude_1/example/manifest.json": "{}\n",
    }
    artifact_commit = repo.commit(f"agent/{PEER}", artifacts)
    handoff = publish_v2(
        repo, PEER, "20260805T100000Z", "task-a", "handoff",
        extra_fields=handoff_fields(
            f"agent/{PEER}", artifact_commit, sorted(artifacts)
        ),
    )

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 1  # valid but unacknowledged
    assert c["delivery errors"] == 0
    assert c["unacknowledged, ack required"] == 1
    assert handoff in result.stdout


def test_handoff_missing_commit_nonancestor_and_missing_path_each_fail(repo):
    artifacts = {"claude_1/example/source.rs": "fn main() {}\n"}
    artifact_commit = repo.commit(f"agent/{PEER}", artifacts)
    unrelated_commit = repo.commit(f"agent/{THIRD}", {"chatgpt_1/x.txt": "x\n"})

    cases = {
        "missing": handoff_fields(
            f"agent/{PEER}", "0" * 40, ["claude_1/example/source.rs"]
        ),
        "nonancestor": handoff_fields(
            f"agent/{PEER}", unrelated_commit, ["claude_1/example/source.rs"]
        ),
        "shorthex": handoff_fields(
            f"agent/{PEER}", artifact_commit[:12], ["claude_1/example/source.rs"]
        ),
        "missingpath": handoff_fields(
            f"agent/{PEER}", artifact_commit, ["claude_1/example/absent.rs"]
        ),
    }
    for i, (name, fields) in enumerate(sorted(cases.items())):
        publish_v2(
            repo, PEER, f"20260805T10000{i}Z", f"task-{name}", "handoff",
            extra_fields=fields,
        )

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["delivery errors"] >= 4
    assert "does not exist" in result.stdout
    assert "not reachable" in result.stdout
    assert "40-hex" in result.stdout
    assert "artifact path missing" in result.stdout


def test_empty_artifact_paths_on_otherwise_valid_handoff_fails(repo):
    # Integrator revision 1: an otherwise valid canonical handoff declaring
    # `artifact_paths: []` is a delivery error (exit 2), never a valid handoff.
    artifacts = {"claude_1/example/source.rs": "fn main() {}\n"}
    artifact_commit = repo.commit(f"agent/{PEER}", artifacts)
    handoff = publish_v2(
        repo, PEER, "20260805T100000Z", "task-a", "handoff",
        extra_fields=handoff_fields(f"agent/{PEER}", artifact_commit, []),
    )

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["delivery errors"] == 1
    assert "artifact_paths is empty" in result.stdout
    assert handoff in result.stdout


# ---------------------------------------------------------------------------
# 14. copying a seen handoff path is not a new event; a correction is
# ---------------------------------------------------------------------------

def test_copied_seen_handoff_is_not_new_but_correction_is(repo):
    artifacts = {"claude_1/example/source.rs": "fn main() {}\n"}
    artifact_commit = repo.commit(f"agent/{PEER}", artifacts)
    handoff = publish_v2(
        repo, PEER, "20260805T100000Z", "task-a", "handoff",
        extra_fields=handoff_fields(
            f"agent/{PEER}", artifact_commit, ["claude_1/example/source.rs"]
        ),
    )
    ack = publish_v2(repo, ME, "20260805T110000Z", "task-a", "ack", to=PEER,
                     ack_for=(handoff,))
    marked = repo.sweep("--me", ME, "--mark")
    assert marked.returncode == 0

    # Copy the identical handoff bytes to another remote ref: not a new event.
    handoff_body = v2_message(
        handoff, kind="handoff", task="task-a", sender=PEER,
        extra_fields=handoff_fields(
            f"agent/{PEER}", artifact_commit, ["claude_1/example/source.rs"]
        ),
    )
    repo.commit(f"agent/{PEER}-mirror", {handoff: handoff_body})
    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 0
    assert c["new (unseen)"] == 0
    assert c["immutable-path collisions"] == 0

    # A new correction naming the handoff in supersedes is new and valid.
    correction = publish_v2(
        repo, PEER, "20260805T120000Z", "task-a", "correction",
        supersedes=(handoff,),
    )
    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 1
    assert c["delivery errors"] == 0
    assert c["new (unseen)"] == 1
    assert correction in result.stdout
    assert c["unacknowledged, ack required"] == 1


# ---------------------------------------------------------------------------
# 15. malformed v2 fields fail clearly (exit 2 + delivery errors section)
# ---------------------------------------------------------------------------

def test_malformed_message_id_fails(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False,
                      overrides={"message_id": "coordination/messages/claude_1/wrong.md"})
    repo.commit(f"agent/{PEER}", {path: body})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "message_id" in result.stdout
    assert counts(result.stdout)["delivery errors"] == 1


def test_malformed_from_fails(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False, overrides={"from": THIRD})
    repo.commit(f"agent/{PEER}", {path: body})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "sender namespace" in result.stdout


def test_malformed_json_list_fields_fail(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False,
                      overrides={"ack_for": "not-a-json-array",
                                 "supersedes": '["ok", 3]'})
    repo.commit(f"agent/{PEER}", {path: body})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["delivery errors"] == 2
    assert "ack_for is not a single-line JSON array" in result.stdout
    assert "supersedes is not a single-line JSON array" in result.stdout


def test_empty_ack_for_on_ack_and_empty_supersedes_on_correction_fail(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "ack",
               requires_ack=False)  # empty ack_for
    publish_v2(repo, PEER, "20260805T100100Z", "task-a", "correction")

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "empty ack_for" in result.stdout
    assert "empty supersedes" in result.stdout


def test_ack_target_missing_from_remote_refs_fails(repo):
    ghost = msg_path(PEER, "20260801T000000Z", "task-x", "question")
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "ack",
               requires_ack=False, ack_for=(ghost,))

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "not found on any authoritative remote ref" in result.stdout


def test_v2_message_missing_from_canonical_branch_fails(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{PEER}-task", {path: body})  # task branch only

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "not present on canonical" in result.stdout


# ---------------------------------------------------------------------------
# 16. --task/--sender isolate one message from a large synthetic backlog
# ---------------------------------------------------------------------------

def test_filters_isolate_the_motivating_ack_from_a_backlog(repo):
    files = {}
    for i in range(30):
        p = msg_path(THIRD, f"20260804T{i:02d}0000Z", f"backlog-{i}", "question")
        files[p] = legacy_message(f"backlog-{i}")
    repo.commit(f"agent/{THIRD}", files)
    target = publish_v2(
        repo, PEER, "20260805T083001Z", "20260802-banana-restoration-r2", "ack",
        requires_ack=False,
        ack_for=(),
        overrides={"ack_for": json.dumps(
            [msg_path(THIRD, "20260804T000000Z", "backlog-0", "question")]
        )},
    )

    unfiltered = repo.sweep("--me", ME)
    assert unfiltered.returncode == 1
    assert counts(unfiltered.stdout)["unacknowledged, ack required"] == 30

    filtered = repo.sweep(
        "--me", ME,
        "--task", "20260802-banana-restoration-r2",
        "--sender", PEER,
    )
    c = counts(filtered.stdout)
    assert filtered.returncode == 0  # exit tracks the filtered selection
    assert c["new (unseen)"] == 1
    assert c["unacknowledged, ack required"] == 0
    assert target in filtered.stdout


# ---------------------------------------------------------------------------
# 17. legacy repository messages still parse without mutation (live, read-only)
# ---------------------------------------------------------------------------

def test_legacy_repository_messages_parse_without_mutation():
    fake_me = "test_nobody_transport_suite"
    before = sorted(REPO_ROOT.glob("*/inbox-watermark.txt"))
    before_bytes = {p: p.read_bytes() for p in before}

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--me", fake_me],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode in (0, 1)
    m = re.search(r"scanned (\d+) authoritative messages", result.stdout)
    assert m and int(m.group(1)) > 500
    assert counts(result.stdout)["delivery errors"] == 0
    assert not (REPO_ROOT / fake_me).exists()
    for p, data in before_bytes.items():
        assert p.read_bytes() == data


# ---------------------------------------------------------------------------
# 18. quarantine: coordinator-adjudicated invalid messages stop poisoning the
#     transport (suppressed from delivery errors / selection, listed loudly)
# ---------------------------------------------------------------------------

def write_quarantine(repo: TransportRepo, entries: list[dict], raw: str | None = None):
    payload = raw if raw is not None else json.dumps(
        {"schema_version": 1, "entries": entries}, indent=2
    ) + "\n"
    repo.write_worktree("coordination/quarantine.json", payload)


def test_quarantined_message_suppresses_errors_and_recovers_exit(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    broken = repo.sweep("--me", ME)
    assert broken.returncode == 2
    assert "unknown v2 message kind" in broken.stdout

    adj = publish_v2(repo, ME, "20260805T110000Z", "task-q", "policy", to=PEER)
    write_quarantine(repo, [
        {"path": bad, "reason": "schema-invalid, adjudicated", "adjudicated_by": adj},
    ])

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert result.returncode == 0
    assert c["delivery errors"] == 0
    assert c["quarantine errors"] == 0
    assert c["quarantined"] == 1
    assert c["new (unseen)"] == 0
    assert c["unacknowledged, ack required"] == 0
    quarantined_section = result.stdout.split("quarantined (")[1]
    assert bad in quarantined_section
    assert "schema-invalid, adjudicated" in quarantined_section

    marked = repo.sweep("--me", ME, "--mark")
    assert marked.returncode == 0
    assert repo.seen_file().exists()


def test_quarantine_entry_with_unknown_adjudication_message_fails(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    ghost = msg_path(ME, "20260805T110000Z", "task-q", "policy")
    write_quarantine(repo, [
        {"path": bad, "reason": "r", "adjudicated_by": ghost},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantine errors"] == 1
    assert "adjudicated_by not found on any authoritative remote ref" in result.stdout
    # A broken quarantine file must not suppress anything.
    assert counts(result.stdout)["delivery errors"] >= 1


def test_quarantine_entry_for_nonexistent_message_path_fails(repo):
    adj = publish_v2(repo, ME, "20260805T110000Z", "task-q", "policy", to=PEER)
    ghost = msg_path(PEER, "20260801T000000Z", "task-x", "update")
    write_quarantine(repo, [
        {"path": ghost, "reason": "typo", "adjudicated_by": adj},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "path not found on any authoritative remote ref" in result.stdout


def test_malformed_quarantine_file_fails_loudly(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               requires_ack=False)
    write_quarantine(repo, [], raw="{not json\n")

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "malformed quarantine file" in result.stderr


def test_quarantine_missing_entry_fields_fails_loudly(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               requires_ack=False)
    write_quarantine(repo, raw=json.dumps(
        {"schema_version": 1, "entries": [{"path": "x", "reason": ""}]}
    ) + "\n", entries=[])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "malformed quarantine file" in result.stderr


def test_quarantined_ack_of_mine_acknowledges_nothing(repo):
    q = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    ack = publish_v2(repo, ME, "20260805T110000Z", "task-a", "ack", to=PEER,
                     ack_for=(q,))
    clean = repo.sweep("--me", ME)
    assert clean.returncode == 0

    adj = publish_v2(repo, ME, "20260805T120000Z", "task-q", "policy", to=PEER)
    write_quarantine(repo, [
        {"path": ack, "reason": "fabricated verdict", "adjudicated_by": adj},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 1
    assert counts(result.stdout)["unacknowledged, ack required"] == 1
    assert q in result.stdout


def test_collision_on_quarantined_path_still_fails(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{PEER}", {path: body})
    repo.commit(f"agent/{PEER}-side", {path: body + "tampered\n"})
    adj = publish_v2(repo, ME, "20260805T110000Z", "task-q", "policy", to=PEER)
    write_quarantine(repo, [
        {"path": path, "reason": "r", "adjudicated_by": adj},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["immutable-path collisions"] == 1


def test_self_adjudicated_quarantine_entry_fails(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    write_quarantine(repo, [
        {"path": bad, "reason": "r", "adjudicated_by": bad},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "adjudicated_by is itself quarantined" in result.stdout


# ---------------------------------------------------------------------------
# Retained legacy parsing unit tests (unchanged semantics)
# ---------------------------------------------------------------------------

def yaml_message(fields: str, body: str = "# Message") -> str:
    return f"---\n{fields}\n---\n\n{body}\n"


def test_yaml_front_matter_uses_case_insensitive_exact_keys():
    body = yaml_message(
        "Task_ID: exact-task\n"
        "To: local_codex_1\n"
        "not_task_id: wrong\n"
        "requires_ack_suffix: true"
    )

    assert inbox_sweep.yaml_front_matter(body)["task_id"] == "exact-task"
    assert "task_id_suffix" not in inbox_sweep.yaml_front_matter(body)
    assert inbox_sweep.task_of(body, "filename-task") == "exact-task"
    assert not inbox_sweep.requires_ack(body, "update")


def test_task_precedence_yaml_then_legacy_then_filename():
    mixed = yaml_message(
        "task_id: yaml-task",
        "- Task: `legacy-task`\n- To: local_codex_1",
    )
    legacy = "- Task: `legacy-task`\n- To: local_codex_1\n"

    assert inbox_sweep.task_of(mixed, "filename-task") == "yaml-task"
    assert inbox_sweep.task_of(legacy, "filename-task") == "legacy-task"
    assert inbox_sweep.task_of("# no metadata\n", "filename-task") == "filename-task"


def test_blank_yaml_task_does_not_revive_stale_legacy_task():
    body = yaml_message("task_id: ''", "- Task: stale-task")

    assert inbox_sweep.task_of(body, "filename-task") == "filename-task"


def test_yaml_recipients_are_tokenized_exactly():
    addressed = yaml_message("to: [chatgpt_1, local_codex_1]\ncc: nobody")
    substring = yaml_message("to: local_codex_10")
    special = yaml_message("cc: both")

    assert inbox_sweep.addressed_to_me(addressed, "local_codex_1")
    assert not inbox_sweep.addressed_to_me(substring, "local_codex_1")
    assert inbox_sweep.addressed_to_me(special, "local_codex_1")


def test_yaml_recipient_keys_override_stale_legacy_recipient_lines():
    body = yaml_message("to: chatgpt_1", "- To: local_codex_1\n- CC: all")

    assert not inbox_sweep.addressed_to_me(body, "local_codex_1")


def test_legacy_multiple_recipients_and_exact_keys_remain_supported():
    body = (
        "- Not To: local_codex_1\n"
        "- To: chatgpt_1, local_codex_1\n"
        "- CC Extra: all\n"
    )

    assert inbox_sweep.addressed_to_me(body, "local_codex_1")
    assert not inbox_sweep.addressed_to_me("- To: local_codex_10\n", "local_codex_1")


def test_requires_ack_boolean_legacy_and_kind_rules():
    assert inbox_sweep.requires_ack(yaml_message("requires_ack: TRUE"), "update")
    assert not inbox_sweep.requires_ack(yaml_message("requires_ack: false"), "update")
    assert inbox_sweep.requires_ack(yaml_message("requires_ack: false"), "handoff")
    assert inbox_sweep.requires_ack("- Requires acknowledgement: yes\n", "update")
    assert not inbox_sweep.requires_ack(
        "- Requires acknowledgement suffix: yes\n", "update"
    )


def test_message_kind_uses_known_yaml_type_and_filename_fallback():
    assert inbox_sweep.message_kind(yaml_message("type: ACK"), "handoff") == "ack"
    assert (
        inbox_sweep.message_kind(yaml_message("type: REVIEW_BLOCKER"), "update")
        == "blocker"
    )
    assert inbox_sweep.message_kind(yaml_message("type: NEW_KIND"), "claim") == "claim"
    assert (
        inbox_sweep.message_kind(yaml_message("type: correction"), "update")
        == "correction"
    )


def test_correction_kind_requires_ack_by_default():
    assert "correction" in inbox_sweep.ACK_REQUIRED_KINDS
    assert inbox_sweep.requires_ack(yaml_message("type: correction"), "correction")


def test_ack_must_be_strictly_later_for_the_same_task():
    latest = {
        "same-task": "20260802T120000Z",
        "other-task": "20260802T140000Z",
    }

    assert inbox_sweep.acknowledged_by_later_ack(
        "same-task", "20260802T115959Z", latest
    )
    assert not inbox_sweep.acknowledged_by_later_ack(
        "same-task", "20260802T120000Z", latest
    )
    assert not inbox_sweep.acknowledged_by_later_ack(
        "same-task", "20260802T120001Z", latest
    )
    assert not inbox_sweep.acknowledged_by_later_ack(
        "unacked-task", "20260802T000000Z", latest
    )


def test_parse_json_list_accepts_only_string_arrays():
    assert inbox_sweep.parse_json_list("[]") == []
    assert inbox_sweep.parse_json_list('["a", "b"]') == ["a", "b"]
    for bad in ("{}", '"x"', "[1]", '["a", 2]', "not json"):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            inbox_sweep.parse_json_list(bad)


def test_schema_version_of_legacy_and_v2():
    assert inbox_sweep.schema_version_of({}) == (0, None)
    assert inbox_sweep.schema_version_of({"schema_version": "2"}) == (2, None)
    version, error = inbox_sweep.schema_version_of({"schema_version": "two"})
    assert version >= 2 and error


def test_seen_state_write_is_deterministic_and_atomic(tmp_path):
    inbox_sweep.write_seen_state(tmp_path, "agent_x", {"b", "a"}, "20260801T000000Z")
    first = (tmp_path / "agent_x" / "inbox-seen.json").read_text(encoding="utf-8")
    inbox_sweep.write_seen_state(tmp_path, "agent_x", {"a", "b"}, "20260801T000000Z")
    second = (tmp_path / "agent_x" / "inbox-seen.json").read_text(encoding="utf-8")
    assert first == second
    data = json.loads(first)
    assert data["seen_message_paths"] == ["a", "b"]
    assert data["schema_version"] == 1
    assert first.endswith("\n")
    assert not list((tmp_path / "agent_x").glob("*.tmp"))
