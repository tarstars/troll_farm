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

from scripts import inbox_sweep
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
    assert "is not a message and is not an allowed namespace file" in result.stdout


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


# --- TQ-4: Git publishes the index, not the worktree ---

def test_staged_invalid_message_is_caught_even_when_worktree_is_valid(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    valid = v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                       requires_ack=False)
    invalid = v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                         requires_ack=False,
                         overrides={"message_id": "coordination/messages/x/wrong.md"})
    repo.write_worktree(path, invalid)
    repo._git("add", path)
    repo.write_worktree(path, valid)  # worktree now looks clean

    assert lint(repo).returncode == 0  # worktree mode is fooled, by design
    staged = lint(repo, ME, "--staged")
    assert staged.returncode == 2
    assert "message_id" in staged.stdout


def test_staged_mode_reports_deletion_of_a_committed_message(repo):
    path = msg_path(ME, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                      requires_ack=False)
    repo.write_worktree(path, body)
    repo._git("add", path)
    repo._git("commit", "-q", "-m", "publish")
    repo._git("rm", "-q", "--cached", path)

    result = lint(repo, ME, "--staged")
    assert result.returncode == 2
    assert "committing this tree would delete it" in result.stdout
    assert path in result.stdout


def test_peer_messages_absent_from_my_branch_are_not_deletions(repo):
    # Linting a peer's namespace from my own worktree must not report their
    # newest messages as deletions merely because my branch lacks them.
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               to=ME, requires_ack=False)

    result = lint(repo, PEER, "--all")
    assert result.returncode == 0
    assert "would delete" not in result.stdout


# --- TQ-5: the sender namespace is closed by default ---

def test_non_digit_prefixed_file_in_the_namespace_fails(repo):
    repo.write_worktree(f"coordination/messages/{ME}/notes.md", "scratch\n")

    result = lint(repo)
    assert result.returncode == 2
    assert "is not a message and is not an allowed namespace file" in result.stdout


def test_wrong_extension_in_the_namespace_fails(repo):
    repo.write_worktree(
        f"coordination/messages/{ME}/20260807T120000Z-task-a-update.txt", "x\n"
    )

    result = lint(repo)
    assert result.returncode == 2
    assert "is not a message and is not an allowed namespace file" in result.stdout


# --- TQ-6: the lint must reproduce the receiver's collision error ---

def test_lint_reports_an_immutable_path_collision(repo):
    path = msg_path(ME, "20260805T100000Z", "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                      requires_ack=False)
    repo.commit(f"agent/{ME}", {path: body})
    repo.commit(f"agent/{ME}-side", {path: body + "tampered\n"})
    repo.write_worktree(path, body)  # matches one side of the collision

    result = lint(repo, ME, "--all")
    assert result.returncode == 2
    assert "immutable-path collision" in result.stdout


# --- claude_1's F9: lint must reproduce the sweep's verdicts ---

def test_new_legacy_message_is_caught_by_lint_not_only_by_the_sweep(repo):
    # F9a: lint ignored the frozen legacy baseline entirely, so a new no-schema
    # message linted clean and then became a permanent delivery error.
    old = msg_path(ME, "20260101T000000Z", "task-old", "handoff")
    repo.commit(f"agent/{ME}", {old: legacy_message("task-old", to=PEER)})
    repo.commit(f"agent/{inbox_sweep_coordinator()}", {
        inbox_sweep.LEGACY_BASELINE_FILE: json.dumps(
            {"schema_version": 1, "frozen_at": repo.tips[f"agent/{ME}"],
             "paths": {old: repo.blob_oid(old)}}, indent=2) + "\n"})
    repo.commit("main", {inbox_sweep.ROSTER_FILE: json.dumps(
        {"schema_version": 1, "coordinator": inbox_sweep_coordinator()}) + "\n"})

    # The real gap: a no-schema message that is ALREADY published and outside
    # the baseline. An unpublished one is caught by the schema check; this one
    # linted clean with --all while the sweep rejected it permanently.
    forgery = msg_path(ME, "20260729T090000Z", "task-forged", "claim")
    body = legacy_message("task-forged", to=PEER)
    repo.commit(f"agent/{ME}", {forgery: body})
    repo.write_worktree(forgery, body)

    result = lint(repo, ME, "--all")
    assert result.returncode == 2
    assert "not in the frozen legacy baseline" in result.stdout
    assert forgery in result.stdout


def test_lint_warns_when_head_is_not_my_canonical_branch(repo):
    # F9b: the repository's actual failure mode. A structurally perfect message
    # published from a task branch is clean to lint and a permanent delivery
    # error to the sweep. Lint must say so at the moment a sender runs it.
    repo._git("checkout", "-q", "-b", f"agent/{ME}-taskwork")
    stage(repo, ME, "claim", to=PEER)

    result = lint(repo)
    assert result.returncode == 2
    assert "canonical branch" in result.stdout
    assert f"agent/{ME}-taskwork" in result.stdout


def test_lint_is_quiet_on_the_canonical_branch(repo):
    stage(repo, ME, "claim", to=PEER)  # fixture HEAD is already agent/ME

    result = lint(repo)
    assert result.returncode == 0


def test_branch_warning_does_not_fire_when_nothing_is_unpublished(repo):
    # Linting a peer's namespace from my worktree is diagnostic, not a
    # pre-publish check: everything there is already on a remote ref.
    publish_v2(repo, PEER, "20260805T100000Z", "task-a", "update",
               to=ME, requires_ack=False)
    repo._git("checkout", "-q", "-b", f"agent/{ME}-taskwork")

    result = lint(repo, PEER, "--all")
    assert result.returncode == 0
    assert "canonical branch" not in result.stdout


def inbox_sweep_coordinator():
    return "local_claude_1"


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


# ---------------------------------------------------------------------------
# Iteration-pool gates (owner decision 2026-08-17): WIP limit + evidence gate.
# Both are sender-side tripwires on NEW handoffs; each is observed FIRING here
# (the standing rule: every new check observed failing first).
# ---------------------------------------------------------------------------

def _valid_handoff_extra(repo, sender=ME):
    artifacts = {f"{sender}/example/artifact.md": "artifact\n"}
    commit = repo.commit(f"agent/{sender}", artifacts)
    return handoff_fields(f"agent/{sender}", commit, sorted(artifacts))


def test_wip_limit_blocks_second_handoff_while_first_unacked(repo):
    extra = _valid_handoff_extra(repo)
    publish_v2(repo, ME, "20260807T110000Z", "task-a", "handoff", to=PEER,
               extra_fields=extra)
    path = msg_path(ME, STAMP, "task-a", "handoff")
    repo.write_worktree(path, v2_message(
        path, kind="handoff", task="task-a", sender=ME, to=PEER,
        extra_fields=extra))

    result = lint(repo)
    assert result.returncode == 2
    assert "WIP limit" in result.stdout


def test_wip_limit_releases_after_ack(repo):
    extra = _valid_handoff_extra(repo)
    prior = publish_v2(repo, ME, "20260807T110000Z", "task-a", "handoff",
                       to=PEER, extra_fields=extra)
    publish_v2(repo, PEER, "20260807T113000Z", "task-a", "ack", to=ME,
               requires_ack=False, ack_for=(prior,))
    path = msg_path(ME, STAMP, "task-a", "handoff")
    repo.write_worktree(path, v2_message(
        path, kind="handoff", task="task-a", sender=ME, to=PEER,
        extra_fields=extra))

    result = lint(repo)
    assert result.returncode == 0, result.stdout


def test_wip_limit_superseding_handoff_allowed(repo):
    extra = _valid_handoff_extra(repo)
    prior = publish_v2(repo, ME, "20260807T110000Z", "task-a", "handoff",
                       to=PEER, extra_fields=extra)
    path = msg_path(ME, STAMP, "task-a", "handoff")
    repo.write_worktree(path, v2_message(
        path, kind="handoff", task="task-a", sender=ME, to=PEER,
        supersedes=(prior,), extra_fields=extra))

    result = lint(repo)
    assert result.returncode == 0, result.stdout


def test_wip_limit_other_task_unaffected(repo):
    extra = _valid_handoff_extra(repo)
    publish_v2(repo, ME, "20260807T110000Z", "task-a", "handoff", to=PEER,
               extra_fields=extra)
    path = msg_path(ME, STAMP, "task-b", "handoff")
    repo.write_worktree(path, v2_message(
        path, kind="handoff", task="task-b", sender=ME, to=PEER,
        extra_fields=extra))

    result = lint(repo)
    assert result.returncode == 0, result.stdout


def test_evidence_gate_cause_label_without_review_ref_fails(repo):
    extra = _valid_handoff_extra(repo)
    path = msg_path(ME, STAMP, "task-a", "handoff")
    body = v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                      extra_fields=extra)
    repo.write_worktree(path, body + "\ncause table: GENERATOR_GAP on 3 rows\n")

    result = lint(repo)
    assert result.returncode == 2
    assert "evidence gate" in result.stdout
    assert "GENERATOR_GAP" in result.stdout


def test_evidence_gate_review_ref_must_exist_on_remote(repo):
    extra = {**_valid_handoff_extra(repo),
             "review_ref": "codex_1/reviews/missing.md"}
    path = msg_path(ME, STAMP, "task-a", "handoff")
    body = v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                      extra_fields=extra)
    repo.write_worktree(path, body + "\nGENERATOR_GAP\n")

    result = lint(repo)
    assert result.returncode == 2
    assert "not found on any" in result.stdout


def test_evidence_gate_passes_with_published_review(repo):
    review = {f"{PEER}/reviews/instrument-review.md": "ACCEPTED\n"}
    repo.commit(f"agent/{PEER}", review)
    extra = {**_valid_handoff_extra(repo),
             "review_ref": f"{PEER}/reviews/instrument-review.md"}
    path = msg_path(ME, STAMP, "task-a", "handoff")
    body = v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                      extra_fields=extra)
    repo.write_worktree(path, body + "\nGENERATOR_GAP with review\n")

    result = lint(repo)
    assert result.returncode == 0, result.stdout


def test_evidence_gate_fires_on_pool3_vocabulary(repo):
    # codex_1 gates-review catch 2026-08-17: the new three-level taxonomy
    # could bypass the gate because only legacy tokens were registered.
    extra = _valid_handoff_extra(repo)
    path = msg_path(ME, STAMP, "task-a", "handoff")
    body = v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                      extra_fields=extra)
    repo.write_worktree(path, body + "\ncause: NO_GOAL_ASSIGNED (12 rows)\n")

    result = lint(repo)
    assert result.returncode == 2
    assert "evidence gate" in result.stdout
    assert "NO_GOAL_ASSIGNED" in result.stdout


def test_evidence_gate_releases_pool3_vocabulary_with_review(repo):
    review = {f"{PEER}/reviews/instrument-review.md": "ACCEPTED\n"}
    repo.commit(f"agent/{PEER}", review)
    extra = {**_valid_handoff_extra(repo),
             "review_ref": f"{PEER}/reviews/instrument-review.md"}
    path = msg_path(ME, STAMP, "task-a", "handoff")
    body = v2_message(path, kind="handoff", task="task-a", sender=ME, to=PEER,
                      extra_fields=extra)
    repo.write_worktree(path, body + "\ncause: NO_GOAL_ASSIGNED, NOT_STARVED\n")

    result = lint(repo)
    assert result.returncode == 0, result.stdout


# ---------------------------------------------------------------------------
# Cross-task reference gate (lint hardening 2026-08-18): supersedes/ack_for
# must reference the message's own task unless the body carries an explicit
# `cross-task:` marker. The defective real case was well-formed and pointed at
# a real file, so the check compares front-matter task_id, not shape or
# existence — and the fixture set includes a LEGITIMATE cross-task supersession
# so the marker path is exercised, not just the rejection path.
# ---------------------------------------------------------------------------

def test_cross_task_supersedes_fails(repo):
    target = publish_v2(repo, ME, "20260807T110000Z", "task-a", "update", to=PEER)
    path = msg_path(ME, STAMP, "task-b", "correction")
    body = v2_message(path, kind="correction", task="task-b", sender=ME,
                      to=PEER, supersedes=(target,))
    repo.write_worktree(path, body)

    result = lint(repo)
    assert result.returncode == 2
    assert "cross-task reference" in result.stdout
    assert "task-a" in result.stdout and "task-b" in result.stdout


def test_cross_task_ack_for_fails(repo):
    target = publish_v2(repo, ME, "20260807T110100Z", "task-a", "update", to=PEER)
    path = msg_path(ME, STAMP, "task-b", "ack")
    body = v2_message(path, kind="ack", task="task-b", sender=ME,
                      to=PEER, ack_for=(target,))
    repo.write_worktree(path, body)

    result = lint(repo)
    assert result.returncode == 2
    assert "cross-task reference" in result.stdout
    assert "`ack_for`" in result.stdout


def test_cross_task_marker_allows_deliberate_supersession(repo):
    target = publish_v2(repo, ME, "20260807T110200Z", "task-a", "update", to=PEER)
    path = msg_path(ME, STAMP, "task-b", "correction")
    body = v2_message(path, kind="correction", task="task-b", sender=ME,
                      to=PEER, supersedes=(target,))
    body = body.replace(
        "# body",
        "# body\n\ncross-task: deliberate supersession of the task-a update "
        "(owner-approved consolidation)",
    )
    repo.write_worktree(path, body)

    result = lint(repo)
    assert result.returncode == 0, result.stdout


def test_same_task_supersedes_clean(repo):
    target = publish_v2(repo, ME, "20260807T110300Z", "task-a", "update", to=PEER)
    path = msg_path(ME, STAMP, "task-a", "correction")
    body = v2_message(path, kind="correction", task="task-a", sender=ME,
                      to=PEER, supersedes=(target,))
    repo.write_worktree(path, body)

    result = lint(repo)
    assert result.returncode == 0, result.stdout


# ---------------------------------------------------------------------------
# Deferral-shape gate (owner-adopted 2026-08-18): a message declaring a
# deferral (line-start `DEFERRED:` marker) must be a queue item — ack-required
# and self-addressed — so the deferring agent's own next sweep surfaces the
# postponed job. Twice in one day a prose-only deferral left every inbox empty
# beside open work; both times the owner caught it before the system did.
# ---------------------------------------------------------------------------

def _deferral_body(path: str, *, requires_ack: bool, to: str) -> str:
    body = v2_message(path, kind="update", task="task-a", sender=ME, to=to,
                      requires_ack=requires_ack)
    return body.replace(
        "# body",
        "# body\n\nDEFERRED: predicate comparison — fresh session needed\n",
    )


def test_deferred_without_ack_fails(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    repo.write_worktree(path, _deferral_body(path, requires_ack=False,
                                             to=f'["{ME}"]'))
    result = lint(repo)
    assert result.returncode == 2
    assert "deferral shape" in result.stdout
    assert "requires_ack" in result.stdout


def test_deferred_without_self_recipient_fails(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    repo.write_worktree(path, _deferral_body(path, requires_ack=True,
                                             to=f'["{PEER}"]'))
    result = lint(repo)
    assert result.returncode == 2
    assert "deferral shape" in result.stdout
    assert "self-address" in result.stdout


def test_deferred_self_addressed_clean(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    repo.write_worktree(path, _deferral_body(path, requires_ack=True,
                                             to=f'["{ME}", "{PEER}"]'))
    result = lint(repo)
    assert result.returncode == 0, result.stdout


def test_deferred_prose_mention_not_flagged(repo):
    path = msg_path(ME, STAMP, "task-a", "update")
    body = v2_message(path, kind="update", task="task-a", sender=ME, to=PEER,
                      requires_ack=False)
    body = body.replace(
        "# body",
        "# body\n\nthe comparison was deferred yesterday; status: deferred "
        "work resumes next session\n",
    )
    repo.write_worktree(path, body)
    result = lint(repo)
    assert result.returncode == 0, result.stdout
