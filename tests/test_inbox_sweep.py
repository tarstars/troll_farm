from scripts import inbox_sweep


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


def test_deduplication_is_by_full_message_path():
    same_path = "coordination/messages/chatgpt_1/20260731T000000Z-task-handoff.md"
    other_sender = "coordination/messages/claude_1/20260731T000000Z-task-handoff.md"

    seen = inbox_sweep.deduplicate_messages(
        [
            (same_path, "refs/heads/one"),
            (same_path, "refs/remotes/origin/one"),
            (other_sender, "refs/heads/two"),
        ]
    )

    assert list(seen) == [same_path, other_sender]
    assert seen[same_path][1] == "refs/heads/one"


def test_mark_preserves_latest_stamp_watermark_behavior(tmp_path, monkeypatch):
    message_path = (
        "coordination/messages/chatgpt_1/"
        "20260731T135607Z-compatibility-update.md"
    )
    full_path = tmp_path / message_path
    full_path.parent.mkdir(parents=True)
    full_path.write_text(
        yaml_message(
            "type: UPDATE\n"
            "task_id: compatibility\n"
            "from: chatgpt_1\n"
            "to: local_codex_1\n"
            "requires_ack: false"
        ),
        encoding="utf-8",
    )

    def fake_git(*args):
        if args == ("rev-parse", "--show-toplevel"):
            return str(tmp_path)
        return ""

    monkeypatch.setattr(inbox_sweep, "git", fake_git)
    monkeypatch.setattr(inbox_sweep, "refs", lambda: [])
    monkeypatch.setattr(
        inbox_sweep,
        "messages_in_worktree",
        lambda root: [(message_path, "worktree")],
    )
    monkeypatch.setattr(
        inbox_sweep.sys,
        "argv",
        ["inbox_sweep.py", "--me", "local_codex_1", "--mark"],
    )

    assert inbox_sweep.main() == 0
    assert (
        tmp_path / "local_codex_1" / "inbox-watermark.txt"
    ).read_text(encoding="utf-8") == "20260731T135607Z\n"
