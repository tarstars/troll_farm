"""Tests for the sender-side outbox lint (transport schema v2, pre-publication).

The lint applies the same v2 validation the receiving sweep applies, minus the
canonical-remote-presence check (the message is not pushed yet), so a sender
discovers schema violations before they land on the immutable bus.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from tests.test_inbox_sweep import (
    ME,
    PEER,
    TransportRepo,
    handoff_fields,
    legacy_message,
    msg_path,
    publish_v2,
    v2_message,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
LINT = REPO_ROOT / "scripts" / "lint_outbox.py"

STAMP = "20260807T120000Z"


@pytest.fixture()
def repo(tmp_path: pathlib.Path) -> TransportRepo:
    return TransportRepo(tmp_path)


def lint(repo: TransportRepo, me: str = ME, *args: str):
    return subprocess.run(
        [sys.executable, str(LINT), "--me", me, *args],
        cwd=repo.work,
        capture_output=True,
        text=True,
    )


def stage(repo: TransportRepo, sender: str, kind: str, task: str = "task-a",
          **kwargs) -> str:
    """Write one unpublished v2 message into the sender's worktree namespace."""
    path = msg_path(sender, STAMP, task, kind)
    repo.write_worktree(
        path, v2_message(path, kind=kind, task=task, sender=sender, **kwargs)
    )
    return path


def test_valid_unpublished_message_passes(repo):
    stage(repo, ME, "update", to=PEER, requires_ack=False)

    result = lint(repo)
    assert result.returncode == 0
    assert "errors (0)" in result.stdout


def test_unknown_kind_fails_with_suggestion(repo):
    path = stage(repo, ME, "finding", to=PEER, requires_ack=False)

    result = lint(repo)
    assert result.returncode == 2
    assert "unknown v2 message kind" in result.stdout
    assert "'progress'" in result.stdout
    assert path in result.stdout


def test_correction_with_empty_supersedes_fails(repo):
    stage(repo, ME, "correction", to=PEER)

    result = lint(repo)
    assert result.returncode == 2
    assert "empty supersedes" in result.stdout


def test_ack_target_must_exist_on_authoritative_refs(repo):
    ghost = msg_path(PEER, "20260801T000000Z", "task-x", "question")
    stage(repo, ME, "ack", to=PEER, requires_ack=False, ack_for=(ghost,))

    result = lint(repo)
    assert result.returncode == 2
    assert "not found on any authoritative remote ref" in result.stdout

    real = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    path = msg_path(ME, "20260807T130000Z", "task-a", "ack")
    repo.write_worktree(
        path,
        v2_message(path, kind="ack", task="task-a", sender=ME, to=PEER,
                   requires_ack=False, ack_for=(real,)),
    )
    result = lint(repo)
    # The first bad ack still fails; the new one referencing a real target is
    # the only file without errors.
    assert result.returncode == 2
    assert path not in result.stdout


def test_message_id_mismatch_fails(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    repo.write_worktree(
        path,
        v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                   requires_ack=False,
                   overrides={"message_id": "coordination/messages/x/wrong.md"}),
    )

    result = lint(repo)
    assert result.returncode == 2
    assert "message_id" in result.stdout


def test_legacy_message_without_schema_version_fails(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    repo.write_worktree(path, "- To: claude_1\n- Task: task-a\n\nbody\n")

    result = lint(repo)
    assert result.returncode == 2
    assert "schema_version: 2" in result.stdout


def test_published_legacy_message_is_grandfathered_under_all(repo):
    # Transport rule 5: legacy messages keep the old parsing rules indefinitely.
    # The v2 requirement binds new messages only, so --all must not flag the
    # hundreds of already-published legacy messages in the historical record.
    path = msg_path(ME, "20260805T100000Z", "task-a", "update")
    body = legacy_message("task-a", to=PEER, requires="no")
    repo.commit(f"agent/{ME}", {path: body})
    repo.write_worktree(path, body)

    result = lint(repo, ME, "--all")
    assert result.returncode == 0
    assert "errors (0)" in result.stdout


def test_malformed_message_filename_fails(repo):
    # A typo'd stamp or kind silently stops being a message: the sweep's
    # scanner skips it, so it is never delivered and never reported missing.
    repo.write_worktree(
        f"coordination/messages/{ME}/20260807T1200Z-task-a-update.md", "x\n"
    )

    result = lint(repo)
    assert result.returncode == 2
    assert "does not match the message filename pattern" in result.stdout


def test_namespace_readme_is_not_treated_as_a_message(repo):
    # Each namespace carries a README; only digit-prefixed files are messages.
    repo.write_worktree(
        f"coordination/messages/{ME}/README.md", f"# messages/{ME}/\n"
    )

    result = lint(repo)
    assert result.returncode == 0
    assert "errors (0)" in result.stdout


def test_published_messages_skipped_by_default_but_linted_with_all(repo):
    # A published (authoritative) invalid message is the sweep's problem, not
    # the outbox lint's — unless --all is requested.
    path = publish_v2(repo, ME, "20260805T100000Z", "task-a", "finding",
                      to=PEER, requires_ack=False)
    repo.write_worktree(
        path,
        v2_message(path, kind="finding", task="task-a", sender=ME, to=PEER,
                   requires_ack=False),
    )

    result = lint(repo)
    assert result.returncode == 0
    assert "errors (0)" in result.stdout

    result_all = lint(repo, ME, "--all")
    assert result_all.returncode == 2
    assert "unknown v2 message kind" in result_all.stdout


def test_handoff_with_missing_artifact_commit_fails(repo):
    repo.commit(f"agent/{ME}", {f"{ME}/seed.md": "seed\n"})
    path = msg_path(ME, STAMP, "task-a", "handoff")
    repo.write_worktree(
        path,
        v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                   extra_fields=handoff_fields(
                       f"agent/{ME}", "0" * 40, [f"{ME}/artifact.md"]
                   )),
    )

    result = lint(repo)
    assert result.returncode == 2
    assert "artifact_commit does not exist" in result.stdout


def test_stale_remote_refs_are_refreshed_with_fetch(repo):
    real = publish_v2(repo, PEER, "20260805T100000Z", "task-a", "question")
    # Stale remote-tracking state: the ack target is on origin, not in this clone.
    repo._git("update-ref", "-d", f"refs/remotes/origin/agent/{PEER}")
    path = msg_path(ME, STAMP, "task-a", "ack")
    repo.write_worktree(
        path,
        v2_message(path, kind="ack", task="task-a", sender=ME, to=PEER,
                   requires_ack=False, ack_for=(real,)),
    )

    stale = lint(repo)
    assert stale.returncode == 2
    assert "not found on any authoritative remote ref" in stale.stdout

    fresh = lint(repo, ME, "--fetch")
    assert fresh.returncode == 0
    assert "errors (0)" in fresh.stdout


def test_editing_an_already_published_message_is_flagged(repo):
    path = publish_v2(repo, ME, "20260805T100000Z", "task-a", "update",
                      to=PEER, requires_ack=False)
    repo.write_worktree(
        path,
        v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                   requires_ack=False) + "tampered\n",
    )

    result = lint(repo)
    assert result.returncode == 2
    assert "already published with different bytes" in result.stdout


def test_valid_handoff_with_pushed_artifact_passes(repo):
    artifacts = {f"{ME}/example/artifact.md": "artifact\n"}
    artifact_commit = repo.commit(f"agent/{ME}", artifacts)
    path = msg_path(ME, STAMP, "task-a", "handoff")
    repo.write_worktree(
        path,
        v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                   extra_fields=handoff_fields(
                       f"agent/{ME}", artifact_commit, sorted(artifacts)
                   )),
    )

    result = lint(repo)
    assert result.returncode == 0
    assert "errors (0)" in result.stdout
