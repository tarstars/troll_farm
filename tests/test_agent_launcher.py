"""Tests for the launcher's wake decision (protocol §5.1).

The launcher had no tests at all until 2026-08-21 — which is how it went on
ringing for the whole actionable queue after self-addressed cards entered it,
and how a blocked agent came to wake itself eight times in 102 minutes. The
decision is one pure function over the sweep's own report, so it is testable
without git, a clone, or an agent.
"""
from __future__ import annotations

import importlib.util
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_launcher():
    spec = importlib.util.spec_from_file_location(
        "agent_launcher", REPO_ROOT / "scripts" / "agent_launcher.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launcher = _load_launcher()

CARD = "coordination/messages/claude_1/20260821T142035Z-task-card.md"
RECEIPT = "coordination/messages/codex_1/20260821T131344Z-task-ack.md"
RULING = "coordination/messages/codex_1/20260821T140000Z-task-policy.md"
QUARANTINED = "coordination/messages/chatgpt_1/20260806T153000Z-old-handoff.md"


def report(wake_lines: list[str]) -> str:
    """A sweep report in the real shape: a blocked agent plus one real ruling."""
    wake_body = "".join(f"  {p}   [refs/remotes/origin/agent/codex_1]\n"
                        for p in wake_lines)
    return (
        "agent: claude_1\n"
        "authority: refs/remotes/origin/** (9 remote refs)\n"
        "\n"
        "quarantined (1):\n"
        f"  {QUARANTINED}: permanently invalid   [coordination/messages/x/y.md]\n"
        "\n"
        "new (unseen) (3):\n"
        f"  {CARD}   [refs/remotes/origin/agent/claude_1]\n"
        f"  {RECEIPT}   [refs/remotes/origin/agent/codex_1]\n"
        f"  {RULING}   [refs/remotes/origin/agent/codex_1]\n"
        "\n"
        "unacknowledged, ack required (1):\n"
        f"  {CARD}   [refs/remotes/origin/agent/claude_1]\n"
        "\n"
        f"wake set ({len(wake_lines)}):\n"
        + wake_body
    )


def test_only_the_wake_section_is_read():
    """The card is owed and the receipt is unread — neither may ring the bell."""
    paths = launcher.parse_wake_paths(report([RULING]))

    assert paths == [RULING]
    assert CARD not in paths, "the agent's own standing card reached the doorbell"
    assert RECEIPT not in paths, "a courtesy receipt reached the doorbell"
    assert QUARANTINED not in paths, "a quarantine reason line parsed as a path"


def test_an_empty_wake_set_means_no_wake():
    """The blocked steady state: work owed, nothing new, nobody woken."""
    assert launcher.parse_wake_paths(report([])) == []


def test_the_report_the_launcher_used_to_read_would_have_woken_on_the_card():
    """The regression this replaced, pinned so it cannot come back quietly.

    Reading `new (unseen)` and `unacknowledged, ack required` — the two sections
    the launcher matched until 2026-08-21 — returns the agent's own card, which
    is what made a blocked agent self-sustaining.
    """
    import re

    old_section_re = re.compile(
        r"new \(unseen\) \((\d+)\):|unacknowledged, ack required \((\d+)\):"
    )
    text, paths, take = report([]), [], False
    for line in text.splitlines():
        m = old_section_re.match(line.strip())
        if m is not None:
            take = int(m.group(1) or m.group(2)) > 0
            continue
        if take:
            stripped = line.strip()
            if stripped.startswith("coordination/messages/"):
                paths.append(stripped.split()[0])
            elif not stripped:
                take = False

    assert CARD in paths, "fixture drift: the old parser must see the card"
    assert launcher.parse_wake_paths(text) == [], "the new parser must not"
