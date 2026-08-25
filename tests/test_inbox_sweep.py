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
COORDINATOR = "local_claude_1"


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
        # A real agent worktree sits on its own canonical branch; the outbox
        # lint checks that, so the fixture must reflect it.
        self._git("checkout", "-q", "-b", f"agent/{ME}")
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

    def sweep(self, *args: str, env_coordinator: str | None = None
              ) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        # Only set to prove the sweep IGNORES it; the authority is the roster.
        if env_coordinator is not None:
            env["TROLL_FARM_COORDINATOR"] = env_coordinator
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.work,
            capture_output=True,
            text=True,
            env=env,
        )

    def seen_file(self, me: str = ME) -> pathlib.Path:
        return self.work / me / "inbox-seen.json"

    def blob_oid(self, path: str) -> str:
        sender = path[len("coordination/messages/"):].split("/", 1)[0]
        return self._git("rev-parse", f"origin/agent/{sender}:{path}")


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
    body: str = "# body",
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
    lines = ["---"] + [f"{k}: {v}" for k, v in fields.items()] + ["---", "", body, ""]
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
    assert q1 not in section_paths(result.stdout, "unacknowledged, ack required")

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
    assert early not in section_paths(result.stdout, "unacknowledged, ack required")


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


def test_my_own_malformed_ack_for_does_not_crash_the_sweep(repo):
    """A malformed ack_for in MY namespace must fail soft, not kill the sweep.

    Regression for the 2026-08-13 execution review. Honouring ack_for on every
    kind made collect_my_acks parse my own non-ack messages, and the parse was
    unguarded -- so one bad declaration of my own raised JSONDecodeError and
    took the whole sweep down. Messages are immutable, so I could not repair
    it: my inbox stayed unreadable until the coordinator quarantined it.

    test_malformed_json_list_fields_fail covers the same field but publishes as
    PEER, which routes through the guarded validate_v2 path and never touches
    this branch. 92 tests passed across the change that introduced the crash.
    """
    mine = msg_path(ME, "20260805T110000Z", "task-a", "handoff")
    body = v2_message(mine, kind="handoff", task="task-a", sender=ME,
                      requires_ack=False,
                      overrides={"ack_for": "not-a-json-array"})
    repo.commit(f"agent/{ME}", {mine: body})

    result = repo.sweep("--me", ME)
    assert "Traceback" not in result.stderr
    assert result.returncode == 0
    assert "malformed ack_for and acknowledges nothing" in result.stdout


def test_non_ack_kind_discharges_exactly_its_declared_target(repo):
    """RQ-1: the positive case the whole change exists for, and it had no test.

    `collect_my_acks` now honours `ack_for` on every kind, not only `ack` -- a
    `handoff` that acks the request it answers, or a `policy` that acks the
    question it rules on, discharges its declared targets. The only test added
    with that change covered the MALFORMED case, so the crash fix was guarded
    and the feature itself was not (codex_1 second review, RQ-1).

    Exactness matters as much as discharge: a kind that swept up same-task
    messages it never named would silently clear real obligations, which is the
    objection the change had to answer.
    """
    q1 = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    q2 = publish_v2(repo, PEER, "20260805T100100Z", "task-a", "question")
    # A `policy`, not a `handoff`: handoffs additionally require artifact_ref /
    # artifact_commit / artifact_paths, and an incomplete one is invalid and
    # would acknowledge nothing -- which is a different code path from the one
    # under test. `policy` is also the real case: three of my own rulings
    # carried ack_for on that kind.
    publish_v2(repo, ME, "20260805T110000Z", "task-a", "policy", to=PEER,
               ack_for=(q1,))

    result = repo.sweep("--me", ME)
    c = counts(result.stdout)
    assert c["delivery errors"] == 0
    # q1 discharged by the handoff; q2 named nowhere and still outstanding.
    assert c["unacknowledged, ack required"] == 1
    # Read the section, not "everything after the word". The slice below used
    # to work only because the unacknowledged list happened to be printed last;
    # adding the wake set (§5.1) after it exposed the assumption.
    outstanding = section_paths(result.stdout, "unacknowledged, ack required")
    assert q2 in outstanding
    assert q1 not in outstanding


def test_tool_drift_warns_on_mismatch_and_is_quiet_when_in_sync(repo):
    """RQ-2: `tool_drift()` had only manual verification, which is not a test.

    I checked it by hand in both directions and reported that as evidence --
    the same uncommitted-control pattern this programme keeps criticising.

    The precondition has to be BUILT: `tool_drift()` compares the running file
    against `origin/main:scripts/inbox_sweep.py`, and the fixture never
    published `scripts/` at all, so the comparison silently returns None and
    every assertion about it would have been vacuous. Writing this test without
    noticing that would have produced a guard that cannot fail -- exactly the
    defect under review.
    """
    running = pathlib.Path(inbox_sweep.__file__).read_text()

    # In sync: origin/main carries byte-identical source.
    repo.commit("main", {"scripts/inbox_sweep.py": running})
    assert "TOOL DRIFT" not in repo.sweep("--me", ME).stdout

    # Drifted: origin/main carries a different byte sequence.
    repo.commit("main", {"scripts/inbox_sweep.py": running + "\n# newer\n"})
    drifted = repo.sweep("--me", ME)
    assert "TOOL DRIFT" in drifted.stdout
    assert "MAY BE WRONG" in drifted.stdout


def test_unexpected_failure_exits_2_not_1(monkeypatch, capsys):
    """RQ-3: exit 1 means "healthy, you have mail" -- a crash must not claim it.

    An uncaught traceback exits 1 in Python, colliding exactly with this
    protocol's "healthy inbox with unacknowledged messages", so anything gating
    on exit status would read a crash as a normal result. The wrapper was added
    on that argument and never exercised, because it lived inline in the
    `__main__` block where no test could reach it. It is now `run_cli()`.
    """
    def boom() -> int:
        raise RuntimeError("simulated unexpected failure")

    monkeypatch.setattr(inbox_sweep, "main", boom)
    assert inbox_sweep.run_cli() == 2, "a crash must not exit 1"
    assert "sweep FAILED" in capsys.readouterr().err

    # And a normal exit code is passed through untouched.
    monkeypatch.setattr(inbox_sweep, "main", lambda: 1)
    assert inbox_sweep.run_cli() == 1


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
    m = re.search(r"scanned (\d+) authoritative messages", result.stdout)
    assert m and int(m.group(1)) > 500
    parsed_counts = counts(result.stdout)
    assert parsed_counts["delivery errors"] == 0
    assert result.returncode == (
        1 if parsed_counts["unacknowledged, ack required"] else 0
    )
    assert not (REPO_ROOT / fake_me).exists()
    for p, data in before_bytes.items():
        assert p.read_bytes() == data


# ---------------------------------------------------------------------------
# 18. quarantine: coordinator-adjudicated invalid messages stop poisoning the
#     transport. Authority is origin/main, and an
#     adjudication must actually adjudicate the target (findings TQ-1/TQ-2).
# ---------------------------------------------------------------------------

def publish_adjudication(
    repo: TransportRepo,
    quarantines: tuple[str, ...],
    stamp: str = "20260805T105000Z",
    task: str = "task-q",
    sender: str = COORDINATOR,
) -> str:
    """Publish a coordinator policy that machine-names the paths it quarantines.

    Addressed to the peer, not to ME: an adjudication is itself an ack-required
    policy, and routing it to ME would add an unacknowledged item to the very
    inbox under test.
    """
    path = msg_path(sender, stamp, task, "policy")
    body = v2_message(
        path, kind="policy", task=task, sender=sender, to=PEER,
        extra_fields={"quarantines": json.dumps(list(quarantines))},
    )
    repo.commit(f"agent/{sender}", {path: body})
    return path


def publish_quarantine(
    repo: TransportRepo,
    entries: list[dict],
    raw: str | None = None,
    branch: str | None = None,
    with_roster: bool = True,
):
    """Quarantine is authoritative only on origin/main.

    The roster is published alongside by default because it is a precondition:
    without one there is no authority, so a quarantine means nothing. Pass
    `with_roster=False` to exercise that case.
    """
    payload = raw if raw is not None else json.dumps(
        {"schema_version": 2, "entries": entries}, indent=2
    ) + "\n"
    repo.commit(branch or "main",
                {"coordination/quarantine.json": payload})
    if with_roster:
        publish_roster(repo)


def quarantine_entry(repo: TransportRepo, path: str, adjudicated_by: str,
                     reason: str = "schema-invalid, adjudicated") -> dict:
    return {
        "path": path,
        "reason": reason,
        "adjudicated_by": adjudicated_by,
        "target_blob": repo.blob_oid(path),
    }


def publish_roster(repo: TransportRepo, coordinator: str = COORDINATOR,
                   former_coordinators: tuple[str, ...] = ()):
    """The roster names the coordinator, and lives only on origin/main."""
    repo.commit("main", {
        inbox_sweep.ROSTER_FILE: json.dumps(
            {"schema_version": 2, "coordinator": coordinator,
             "former_coordinators": list(former_coordinators)}, indent=2
        ) + "\n"
    })


def test_authority_comes_from_the_roster_not_the_environment(repo):
    # claude_1's finding: resolving the coordinator from an unvalidated env var
    # let whoever set it designate the quarantine authority.
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)])
    publish_roster(repo)

    clean = repo.sweep("--me", ME)
    assert clean.returncode == 0
    assert counts(clean.stdout)["quarantined"] == 1

    attacked = repo.sweep("--me", ME, env_coordinator=THIRD)
    assert attacked.returncode == 0
    assert counts(attacked.stdout)["quarantined"] == 1  # env is ignored entirely


def test_missing_roster_disables_quarantine_loudly(repo):
    # Fail safe: with no authoritative roster, nothing is suppressed.
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)], with_roster=False)

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0
    assert "no authoritative roster" in result.stdout


def test_role_transfer_preserves_prior_adjudications_through_succession_list(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)])
    publish_roster(repo, coordinator=THIRD, former_coordinators=(COORDINATOR,))

    result = repo.sweep("--me", ME)
    assert result.returncode == 0
    assert counts(result.stdout)["quarantined"] == 1
    assert f"adjudicated by former coordinator {COORDINATOR}" in result.stdout


def test_role_transfer_without_succession_list_fails_loudly(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)])
    publish_roster(repo, coordinator=THIRD)

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0
    assert counts(result.stdout)["quarantine errors"] == 1


def test_malformed_roster_fails_loudly(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               requires_ack=False)
    repo.commit("main", {inbox_sweep.ROSTER_FILE: "{not json\n"})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "malformed roster" in result.stderr


# --- claude_1's F7/F8/F4: spec-versus-code gaps in the quarantine contract ---

def test_adjudication_only_on_a_side_branch_is_rejected(repo):
    # F7: protocol 10.2 requires the adjudication to be on the coordinator's
    # canonical ref. Being in the coordinator's namespace somewhere is not that.
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = msg_path(COORDINATOR, "20260805T105000Z", "task-q", "policy")
    body = v2_message(adj, kind="policy", task="task-q", sender=COORDINATOR,
                      to=PEER, extra_fields={"quarantines": json.dumps([bad])})
    repo.commit(f"agent/{COORDINATOR}-side", {adj: body})  # side branch only
    publish_quarantine(repo, [
        {"path": bad, "reason": "r", "adjudicated_by": adj,
         "target_blob": repo.blob_oid(bad)},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0
    assert "not present on its author's canonical ref" in result.stdout


def test_blob_pin_is_enforced_even_when_the_path_collides(repo):
    # F8: the pin was silently skipped exactly when bytes are ambiguous.
    path = msg_path(PEER, "20260805T100000Z", "task-a", "finding")
    body = v2_message(path, kind="finding", task="task-a", sender=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{PEER}", {path: body})
    repo.commit(f"agent/{PEER}-side", {path: body + "tampered\n"})
    adj = publish_adjudication(repo, (path,))
    publish_quarantine(repo, [
        {"path": path, "reason": "r", "adjudicated_by": adj,
         "target_blob": "0" * 40},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "collides" in result.stdout


def test_quarantining_an_ack_must_declare_what_it_reopens(repo):
    # F4: quarantining an ACK silently re-opens obligations a peer discharged.
    q = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    ack = publish_v2(repo, ME, "20260805T110000Z", "task-a", "ack", to=PEER,
                     ack_for=(q,))
    adj = publish_adjudication(repo, (ack,), stamp="20260805T120000Z")
    publish_quarantine(repo, [
        quarantine_entry(repo, ack, adj, reason="fabricated verdict"),
    ])

    undeclared = repo.sweep("--me", ME)
    assert undeclared.returncode == 2
    assert "re-opens" in undeclared.stdout
    assert q in undeclared.stdout

    entry = quarantine_entry(repo, ack, adj, reason="fabricated verdict")
    entry["reopens"] = [q]
    publish_quarantine(repo, [entry])
    declared = repo.sweep("--me", ME)
    assert declared.returncode == 1  # q is unacknowledged again, as intended
    assert counts(declared.stdout)["quarantine errors"] == 0
    assert counts(declared.stdout)["unacknowledged, ack required"] == 1


def publish_baseline(repo: TransportRepo, paths: dict[str, str],
                     frozen_at: str | None = None):
    """`frozen_at` defaults to the tip carrying the baselined messages."""
    repo.commit("main", {
        inbox_sweep.LEGACY_BASELINE_FILE: json.dumps(
            {"schema_version": 1,
             "frozen_at": frozen_at or repo.tips[f"agent/{PEER}"],
             "paths": paths}, indent=2
        ) + "\n"
    })
    publish_roster(repo)


def test_quarantined_message_suppresses_errors_and_recovers_exit(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    broken = repo.sweep("--me", ME)
    assert broken.returncode == 2
    assert "unknown v2 message kind" in broken.stdout

    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)])

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
    # TQ-1: the authority actually used must be reported.
    assert f"{inbox_sweep.ROSTER_REF}:{inbox_sweep.QUARANTINE_FILE}" in result.stdout

    marked = repo.sweep("--me", ME, "--mark")
    assert marked.returncode == 0
    assert repo.seen_file().exists()


# --- TQ-1: quarantine truth comes from the coordinator ref, not the worktree ---

def test_worktree_quarantine_alone_suppresses_nothing(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    # Structurally perfect, but only in the local worktree.
    repo.write_worktree("coordination/quarantine.json", json.dumps(
        {"schema_version": 2,
         "entries": [quarantine_entry(repo, bad, adj)]}, indent=2) + "\n")

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0
    assert counts(result.stdout)["delivery errors"] >= 1


def test_local_quarantine_drift_from_authority_is_loud(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)])
    repo.write_worktree("coordination/quarantine.json",
                        '{"schema_version": 2, "entries": []}\n')

    result = repo.sweep("--me", ME)
    assert "local quarantine differs from the authoritative blob" in result.stdout
    # The authoritative copy still governs.
    assert counts(result.stdout)["quarantined"] == 1


def test_well_formed_quarantine_on_any_agent_ref_is_ignored(repo):
    bad = publish_v2(repo, THIRD, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)],
                       branch=f"agent/{COORDINATOR}")

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0


# --- TQ-2: the adjudication must actually adjudicate the target ---

def test_unrelated_existing_message_cannot_authorize_quarantine(repo):
    # chatgpt_1's reproduction: mere existence of a path must not suppress.
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    unrelated = publish_v2(repo, COORDINATOR, "20260805T101000Z", "other", "update",
                           to=PEER, requires_ack=False)
    publish_quarantine(repo, [quarantine_entry(repo, bad, unrelated)])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0
    assert "does not name" in result.stdout
    assert counts(result.stdout)["delivery errors"] >= 1


def test_adjudication_from_a_non_coordinator_is_rejected(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    # A peer publishes a well-formed adjudication naming the target.
    adj = publish_adjudication(repo, (bad,), sender=THIRD)
    publish_quarantine(repo, [quarantine_entry(repo, bad, adj)])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantined"] == 0
    assert "not authored by the current or former coordinators" in result.stdout


def test_quarantine_entry_with_unknown_adjudication_message_fails(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    ghost = msg_path(COORDINATOR, "20260805T110000Z", "task-q", "policy")
    publish_quarantine(repo, [
        {"path": bad, "reason": "r", "adjudicated_by": ghost,
         "target_blob": repo.blob_oid(bad)},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["quarantine errors"] >= 1
    assert "adjudicated_by not found on any authoritative remote ref" in result.stdout
    assert counts(result.stdout)["delivery errors"] >= 1


def test_target_blob_must_match_the_quarantined_message(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    adj = publish_adjudication(repo, (bad,))
    entry = quarantine_entry(repo, bad, adj)
    entry["target_blob"] = "0" * 40
    publish_quarantine(repo, [entry])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "target_blob does not match" in result.stdout


def test_quarantine_entry_for_nonexistent_message_path_fails(repo):
    ghost = msg_path(PEER, "20260801T000000Z", "task-x", "update")
    adj = publish_adjudication(repo, (ghost,))
    publish_quarantine(repo, [
        {"path": ghost, "reason": "typo", "adjudicated_by": adj,
         "target_blob": "0" * 40},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "path not found on any authoritative remote ref" in result.stdout


def test_malformed_quarantine_file_fails_loudly(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               requires_ack=False)
    publish_quarantine(repo, [], raw="{not json\n")

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "malformed quarantine file" in result.stderr


def test_quarantine_missing_entry_fields_fails_loudly(repo):
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               requires_ack=False)
    publish_quarantine(repo, [], raw=json.dumps(
        {"schema_version": 2, "entries": [{"path": "x", "reason": ""}]}
    ) + "\n")

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "malformed quarantine file" in result.stderr


def test_quarantined_ack_of_mine_acknowledges_nothing(repo):
    q = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    ack = publish_v2(repo, ME, "20260805T110000Z", "task-a", "ack", to=PEER,
                     ack_for=(q,))
    clean = repo.sweep("--me", ME)
    assert clean.returncode == 0

    adj = publish_adjudication(repo, (ack,), stamp="20260805T120000Z")
    entry = quarantine_entry(repo, ack, adj, reason="fabricated verdict")
    entry["reopens"] = [q]  # required since F4: the re-opening must be declared
    publish_quarantine(repo, [entry])

    result = repo.sweep("--me", ME)
    assert result.returncode == 1
    assert counts(result.stdout)["unacknowledged, ack required"] == 1
    assert q in result.stdout


def test_collision_on_quarantined_path_still_fails(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{PEER}", {path: body})
    oid = repo.blob_oid(path)
    repo.commit(f"agent/{PEER}-side", {path: body + "tampered\n"})
    adj = publish_adjudication(repo, (path,))
    publish_quarantine(repo, [
        {"path": path, "reason": "r", "adjudicated_by": adj, "target_blob": oid},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert counts(result.stdout)["immutable-path collisions"] == 1


def test_self_adjudicated_quarantine_entry_fails(repo):
    bad = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "finding",
                     requires_ack=False)
    publish_quarantine(repo, [
        {"path": bad, "reason": "r", "adjudicated_by": bad,
         "target_blob": repo.blob_oid(bad)},
    ])

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "adjudicated_by is itself quarantined" in result.stdout


# --- TQ-3: legacy grandfathering is a pinned baseline, not an open category ---

def test_new_legacy_message_outside_the_baseline_is_a_delivery_error(repo):
    # A frozen baseline exists; a sender then publishes a NEW no-schema message
    # and skips the advisory lint. The receiver must catch it.
    old = msg_path(PEER, "20260101T000000Z", "task-old", "handoff")
    repo.commit(f"agent/{PEER}", {old: legacy_message("task-old")})
    publish_baseline(repo, {old: repo.blob_oid(old)})
    new = msg_path(PEER, "20260805T100000Z", "task-a", "handoff")
    repo.commit(f"agent/{PEER}", {new: legacy_message("task-a")})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "not in the frozen legacy baseline" in result.stdout
    assert new in result.stdout


def test_backdated_filename_does_not_defeat_the_baseline(repo):
    # A date cutoff would be defeated by backdating; exact-path pinning is not.
    old = msg_path(PEER, "20260101T000000Z", "task-old", "handoff")
    repo.commit(f"agent/{PEER}", {old: legacy_message("task-old")})
    publish_baseline(repo, {old: repo.blob_oid(old)})
    backdated = msg_path(PEER, "20250101T000000Z", "task-ancient", "handoff")
    repo.commit(f"agent/{PEER}", {backdated: legacy_message("task-ancient")})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "not in the frozen legacy baseline" in result.stdout


def test_baselined_legacy_message_is_still_accepted(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "handoff")
    repo.commit(f"agent/{PEER}", {path: legacy_message("task-a")})
    publish_baseline(repo, {path: repo.blob_oid(path)})

    result = repo.sweep("--me", ME)
    assert result.returncode == 1  # valid legacy, merely unacknowledged
    assert counts(result.stdout)["delivery errors"] == 0


def test_baseline_cannot_grandfather_a_message_added_after_the_freeze(repo):
    # F5: the baseline was a v2-enforcement waiver list that required no
    # adjudication — the coordinator could add any message and it escaped
    # validation. Pinning `frozen_at` makes the list verifiable: a path that
    # did not exist at the freeze commit cannot be in it.
    old = msg_path(PEER, "20260101T000000Z", "task-old", "handoff")
    freeze = repo.commit(f"agent/{PEER}", {old: legacy_message("task-old")})
    forgery = msg_path(PEER, "20260729T090000Z", "task-forged", "claim")
    repo.commit(f"agent/{PEER}", {forgery: legacy_message("task-forged")})

    repo.commit("main", {
        inbox_sweep.LEGACY_BASELINE_FILE: json.dumps(
            {"schema_version": 1, "frozen_at": freeze,
             "paths": {old: repo.blob_oid(old),
                       forgery: repo.blob_oid(forgery)}}, indent=2) + "\n"})
    publish_roster(repo)

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "did not exist at the freeze commit" in result.stdout
    assert forgery in result.stdout


def test_baseline_without_frozen_at_is_rejected(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "handoff")
    repo.commit(f"agent/{PEER}", {path: legacy_message("task-a")})
    repo.commit("main", {
        inbox_sweep.LEGACY_BASELINE_FILE: json.dumps(
            {"schema_version": 1, "paths": {path: repo.blob_oid(path)}},
            indent=2) + "\n"})
    publish_roster(repo)

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "malformed legacy baseline" in result.stderr


def test_baselined_legacy_message_with_changed_bytes_is_rejected(repo):
    path = msg_path(PEER, "20260805T100000Z", "task-a", "handoff")
    repo.commit(f"agent/{PEER}", {path: legacy_message("task-a")})
    publish_baseline(repo, {path: "0" * 40})

    result = repo.sweep("--me", ME)
    assert result.returncode == 2
    assert "legacy baseline blob mismatch" in result.stdout


# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Ack obligation falls on `to` recipients only (ruling 2026-08-20): a cc'd
# bystander never OWES an ack, so a policy-clean empty inbox is possible for
# agents that were only informed. `to` recipients still owe as before.
# ---------------------------------------------------------------------------

def _section_paths(stdout: str, label: str) -> str:
    import re as _re
    m = _re.search(_re.escape(label) + r" \(\d+\):\n((?:  \S.*\n)*)", stdout)
    return m.group(1) if m else ""


def test_cc_only_recipient_owes_no_ack(repo):
    path = publish_v2(repo, PEER, "20260807T140000Z", "task-a", "policy",
                      to="third_agent", requires_ack=True,
                      overrides={"cc": f'["{ME}"]'})
    result = repo.sweep("--me", ME)
    assert path not in _section_paths(result.stdout, "unacknowledged, ack required")
    assert path in _section_paths(result.stdout, "new (unseen)")


def test_to_recipient_still_owes_ack(repo):
    path = publish_v2(repo, PEER, "20260807T140100Z", "task-a", "policy",
                      to=ME, requires_ack=True)
    result = repo.sweep("--me", ME)
    assert path in _section_paths(result.stdout, "unacknowledged, ack required")


# ---------------------------------------------------------------------------
# `main()` and `actionable_set()` must be ONE predicate (ruling 2026-08-21).
#
# The sentinel that wakes agents on work reads `actionable_set()`. If it can
# disagree with the sweep the agents actually read, it is worse than no
# sentinel: it wakes on work the sweep does not show, or stays silent on work
# it does. These tests pin the two to the same answer on the same repository,
# including under the display filters, so the extraction cannot drift apart
# later.
# ---------------------------------------------------------------------------

def _busy_inbox(repo: TransportRepo) -> dict[str, str]:
    """Publish an inbox with every actionability outcome represented."""
    published = {}
    published["unacked"] = publish_v2(
        repo, PEER, "20260808T100000Z", "task-a", "policy", to=ME, requires_ack=True
    )
    published["acked"] = publish_v2(
        repo, PEER, "20260808T100100Z", "task-a", "question", to=ME, requires_ack=True
    )
    publish_v2(
        repo, ME, "20260808T100200Z", "task-a", "ack", to=PEER,
        ack_for=(published["acked"],),
    )
    published["no_ack_owed"] = publish_v2(
        repo, THIRD, "20260808T100300Z", "task-b", "progress", to=ME
    )
    published["cc_only"] = publish_v2(
        repo, THIRD, "20260808T100400Z", "task-b", "policy", to="someone_else",
        requires_ack=True, overrides={"cc": f'["{ME}"]'},
    )
    published["not_mine"] = publish_v2(
        repo, THIRD, "20260808T100500Z", "task-c", "policy", to=PEER,
        requires_ack=True,
    )
    return published


def _listed_paths(stdout: str, label: str) -> list[str]:
    """The message paths a section printed, without their `[ref]` suffix."""
    return sorted(
        line.split()[0] for line in _section_paths(stdout, label).splitlines() if line.strip()
    )


def _state(repo: TransportRepo, monkeypatch, *, tasks=(), senders=()):
    monkeypatch.chdir(repo.work)
    return inbox_sweep.actionable_set(ME, repo.work, tasks, senders)


def test_actionable_set_agrees_with_main_on_a_busy_inbox(repo, monkeypatch):
    published = _busy_inbox(repo)

    result = repo.sweep("--me", ME)
    state = _state(repo, monkeypatch)

    assert result.returncode == 1
    assert [m.path for m in state.new_items] == _listed_paths(
        result.stdout, "new (unseen)"
    )
    assert [m.path for m in state.unacked] == _listed_paths(
        result.stdout, "unacknowledged, ack required"
    )
    # …and the answer is the substantive one, not two identical empties.
    assert state.unacked and [m.path for m in state.unacked] == [published["unacked"]]
    assert published["not_mine"] not in state.actionable_paths
    assert published["cc_only"] in {m.path for m in state.new_items}
    assert published["cc_only"] not in {m.path for m in state.unacked}
    assert state.is_actionable and not state.transport_broken


def test_actionable_set_agrees_with_main_after_mark_and_under_filters(
    repo, monkeypatch
):
    published = _busy_inbox(repo)

    marked = repo.sweep("--me", ME, "--mark")
    assert marked.returncode == 1

    # Marked: nothing is new any more, but the ack is still owed — so the
    # sentinel must still consider this agent actionable.
    state = _state(repo, monkeypatch)
    after = repo.sweep("--me", ME)
    assert counts(after.stdout)["new (unseen)"] == 0
    assert state.new_items == []
    assert [m.path for m in state.unacked] == [published["unacked"]]
    assert state.is_actionable

    # Filters move the selection identically on both paths (transport rule 6).
    filtered_state = _state(repo, monkeypatch, tasks=("task-b",))
    filtered = repo.sweep("--me", ME, "--task", "task-b")
    assert filtered.returncode == 0
    assert filtered_state.unacked == []
    assert not filtered_state.is_actionable
    assert [m.path for m in filtered_state.selection] == sorted(
        [published["no_ack_owed"], published["cc_only"]]
    )

    sender_state = _state(repo, monkeypatch, senders=(THIRD,))
    sender_cli = repo.sweep("--me", ME, "--sender", THIRD)
    assert sender_cli.returncode == 0
    assert [m.path for m in sender_state.selection] == sorted(
        [published["no_ack_owed"], published["cc_only"]]
    )


def test_actionable_set_reports_a_broken_transport_as_actionable(repo, monkeypatch):
    # Same path published with different bytes on two authoritative refs.
    path = publish_v2(repo, PEER, "20260808T110000Z", "task-a", "policy", to=ME)
    repo.commit(
        f"agent/{THIRD}",
        {path: v2_message(path, kind="policy", task="task-a", sender=PEER, to=ME)
             + "\ndivergent\n"},
    )

    result = repo.sweep("--me", ME)
    state = _state(repo, monkeypatch)

    assert result.returncode == 2
    assert state.transport_broken and state.is_actionable
    assert [p for p, _ in state.collisions] == [path]


def test_actionable_set_raises_sweep_failure_where_main_exits_2(repo, monkeypatch):
    publish_v2(repo, PEER, "20260808T120000Z", "task-a", "policy", to=ME)
    write_seen_state_file(repo, {"seen_message_paths": []})  # no schema_version

    result = repo.sweep("--me", ME)
    assert result.returncode == 2

    monkeypatch.chdir(repo.work)
    with pytest.raises(inbox_sweep.SweepFailure):
        inbox_sweep.actionable_set(ME, repo.work)


# ---------------------------------------------------------------------------
# Self-addressed DEFERRED cards: the one self-mail route that is actionable
#
# The deferral rule (owner-adopted 2026-08-18) says a postponed job must BE a
# queue item: `requires_ack: true`, self-addressed, so the deferring agent's
# next sweep surfaces it. That was prose, not mechanism — `actionable_set()`
# dropped every self-authored message before addressing could matter, so two of
# claude_1's wakes reported "queue drained" with live cards outstanding, and the
# sweep agreed. codex_1 reproduced it in the shared predicate and made the
# repair blocking (card-2 review, 2026-08-21): the replacement-card route must
# become visible while ORDINARY self-mail stays inert.
# ---------------------------------------------------------------------------

DEFERRAL_BODY = (
    "# DEFERRED card — the postponed job\n\n"
    "DEFERRED: the instrument, postponed to my next wake.\n"
)


def publish_deferral_card(repo: TransportRepo, sender: str, stamp: str,
                          task: str, **kwargs) -> str:
    """A shape-valid deferral: DEFERRED: marker, requires_ack, self-addressed."""
    return publish_v2(
        repo, sender, stamp, task, "blocker",
        to=sender, requires_ack=True, body=DEFERRAL_BODY, **kwargs
    )


def test_self_addressed_deferral_card_is_actionable_for_its_own_owner(repo, monkeypatch):
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    card = publish_deferral_card(repo, ME, "20260821T060000Z", "task-deferred")

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert card in state.actionable_paths, (
        "a self-addressed DEFERRED card is invisible to the agent it is the "
        "queue item for"
    )
    assert card in {m.path for m in state.unacked}, (
        "the card must stay outstanding until it is discharged, not merely "
        "until it is read once"
    )
    assert card not in {m.path for m in state.new_items}, (
        "an agent has read what it wrote; routing its own card through 'new' "
        "would let a single --mark retire a job that is still undone"
    )


def test_ordinary_self_addressed_mail_is_not_actionable(repo, monkeypatch):
    """The negative control: only the DEFERRED route opens, not all self-mail."""
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    plain = publish_v2(
        repo, ME, "20260821T060100Z", "task-plain", "blocker",
        to=ME, requires_ack=True,
    )

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert plain not in state.actionable_paths, (
        "ordinary self-mail became actionable; an agent must not be able to "
        "put arbitrary work in its own queue by writing to itself"
    )


def test_a_deferral_card_addressed_only_to_a_peer_stays_out_of_my_queue(repo, monkeypatch):
    """Shape alone is not the ticket: the card must be addressed to me."""
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    card = publish_v2(
        repo, ME, "20260821T060200Z", "task-peer", "blocker",
        to=PEER, requires_ack=True, body=DEFERRAL_BODY,
    )

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert card not in state.actionable_paths


def test_self_addressed_deferral_card_is_discharged_by_its_delivery_handoff(repo, monkeypatch):
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    card = publish_deferral_card(repo, ME, "20260821T060300Z", "task-deferred")
    assert card in inbox_sweep.actionable_set(ME, repo.work).actionable_paths

    commit = repo.tips[f"agent/{ME}"]
    delivery = publish_v2(
        repo, ME, "20260821T070000Z", "task-deferred", "handoff",
        to=PEER, ack_for=(card,),
        extra_fields=handoff_fields(f"agent/{ME}", commit, [card]),
    )

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert card not in state.actionable_paths, (
        "the delivery handoff naming the card in ack_for did not discharge it"
    )
    assert delivery not in state.actionable_paths, (
        "my own delivery handoff is not work for me"
    )


# ---------------------------------------------------------------------------
# 18. The wake set — protocol §5.1, owner rule 2026-08-21.
#
# The queue says what I OWE; the doorbell rings only for news from someone
# else. Between 12:39Z and 14:21Z on 2026-08-21 claude_1 woke eight times on
# mail it had written itself, so every exclusion below is a measured failure
# rather than a preference. The wake set is always a subset of the actionable
# set: nothing may wake an agent that the sweep would not also show it.
# ---------------------------------------------------------------------------

def section_paths(stdout: str, label: str) -> list[str]:
    """Message paths under one printed section — what the launcher parses."""
    found: list[str] = []
    take = False
    for line in stdout.splitlines():
        if re.match(re.escape(label) + r" \(\d+\):", line.strip()):
            take = True
            continue
        if take:
            stripped = line.strip()
            if not stripped:
                take = False
            elif stripped.startswith("coordination/messages/"):
                found.append(stripped.split()[0])
    return found


def test_my_own_deferral_card_is_owed_but_never_wakes_me(repo, monkeypatch):
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    card = publish_deferral_card(repo, ME, "20260821T120000Z", "task-blocked")

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert card in state.actionable_paths, "the card is still owed by its author"
    assert card not in state.wake_paths, (
        "an agent's own card rang its own doorbell — the 2026-08-21 treadmill"
    )


def test_cc_only_mail_never_wakes(repo, monkeypatch):
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    bystander = publish_v2(
        repo, PEER, "20260821T121000Z", "task-other", "progress",
        overrides={"to": THIRD, "cc": json.dumps([ME])},
    )

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert bystander in state.actionable_paths, "a cc is still shown as unread"
    assert bystander not in state.wake_paths, (
        "cc owes no ack (§4), so it must not wake its bystander either"
    )


def test_a_courtesy_receipt_does_not_wake_but_a_queue_changing_one_does(
    repo, monkeypatch
):
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    anchor = publish_v2(repo, ME, "20260821T122000Z", "task-x", "progress", to=PEER)
    courtesy = publish_v2(
        repo, PEER, "20260821T123000Z", "task-x", "ack",
        to=ME, requires_ack=False, ack_for=(anchor,),
    )
    verdict = publish_v2(
        repo, PEER, "20260821T124000Z", "task-x", "ack",
        to=ME, requires_ack=True, ack_for=(anchor,),
    )

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert courtesy not in state.wake_paths, (
        "a receipt that authorizes nothing woke its recipient"
    )
    assert verdict in state.wake_paths, (
        "a queue-changing ack must wake — that is what requires_ack: true is for"
    )


def test_a_peers_deferral_card_naming_me_in_to_still_wakes_nobody(
    repo, monkeypatch
):
    """Both live agents address their own cards to each other as well.

    A peer cannot discharge another agent's card — only a later message of the
    SAME agent naming it in `ack_for` does (§10). So the ack obligation such a
    card appears to place on me is one I am unable to act on, and waking me for
    it is noise by construction. It stays visible as status.
    """
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    card = publish_v2(
        repo, PEER, "20260821T132000Z", "task-blocked", "blocker",
        requires_ack=True, body=DEFERRAL_BODY,
        overrides={"to": json.dumps([PEER, ME])},
    )

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert card in state.actionable_paths, "a peer's card is still status I can read"
    assert card not in state.wake_paths, (
        "a peer's standing card woke me for an obligation I cannot discharge"
    )


def test_a_peer_message_addressed_to_me_still_wakes(repo, monkeypatch):
    """The positive control: the rule must not silence real mail."""
    monkeypatch.chdir(repo.work)
    publish_roster(repo)
    ruling = publish_v2(repo, PEER, "20260821T125000Z", "task-y", "policy", to=ME)

    state = inbox_sweep.actionable_set(ME, repo.work)

    assert ruling in state.wake_paths


def test_the_cli_prints_a_wake_set_the_launcher_can_parse(repo):
    publish_roster(repo)
    card = publish_deferral_card(repo, ME, "20260821T130000Z", "task-blocked")
    news = publish_v2(repo, PEER, "20260821T131000Z", "task-y", "policy", to=ME)

    res = repo.sweep("--me", ME)

    wake = section_paths(res.stdout, "wake set")
    owed = section_paths(res.stdout, "unacknowledged, ack required")
    unseen = section_paths(res.stdout, "new (unseen)")
    assert news in wake, "real mail is missing from the printed wake set"
    assert card in owed and card not in wake, (
        "the standing card must be owed and silent"
    )
    assert set(wake) <= set(unseen) | set(owed), (
        "the wake set escaped the actionable set"
    )
