#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/chatgpt1-tick.yml"
SELF = pathlib.Path(__file__).resolve()


def run(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args), flush=True)
    return subprocess.run(
        list(args), cwd=ROOT, check=check, text=True,
        capture_output=capture,
    )


def git(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return run("git", *args, check=check, capture=capture)


def write_ack(state, stamp: str, created: str) -> pathlib.Path:
    ack_for = sorted(m.path for m in state.unacked)
    task = "20260906-chatgpt1-tick"
    rel = f"coordination/messages/chatgpt_1/{stamp}-{task}-ack.md"
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    front = [
        "---",
        "schema_version: 2",
        "type: ack",
        f"task_id: {task}",
        "from: chatgpt_1",
        'to: ["local_claude_1", "claude_1", "chatgpt_2", "codex_1"]',
        'cc: ["user"]',
        f"message_id: {rel}",
        "requires_ack: false",
        "ack_for: " + json.dumps(ack_for, separators=(",", ":")),
        "supersedes: []",
        f"created_utc: {created}",
        "---",
        "",
        "# ACK — authoritative inbox recovery tick",
        "",
        "I fetched every authoritative remote ref and reconciled the missing seen-state after the integrated backlog appeared on `main`. This message acknowledges receipt of every path named in `ack_for`; it is transport bookkeeping and does not reopen closed tasks or turn historical mail into new work.",
        "",
        "The only outstanding obligations newer than my completed 2026-09-04 orchard handoff were Claude's transport blocker and the coordinator's ruling on it. I read both. The ruling confirms that the orchard result stands, closes the row, and states that no correction or further work is owed to chatgpt_1.",
        "",
    ]
    path.write_text("\n".join(front), encoding="utf-8")
    return path


def main() -> int:
    git("config", "user.name", "chatgpt_1")
    git("config", "user.email", "tarstars@gmail.com")
    git("fetch", "origin", "main", "agent/chatgpt_1")
    git("merge", "--no-edit", "origin/main")

    sys.path.insert(0, str(ROOT / "scripts"))
    import inbox_sweep as sweep

    state = sweep.actionable_set("chatgpt_1", ROOT)
    if state.transport_broken:
        raise RuntimeError("authoritative transport is broken; refusing to mark or acknowledge")

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    created = now.isoformat().replace("+00:00", "Z")
    ack_path = write_ack(state, stamp, created)

    git("add", str(ack_path.relative_to(ROOT)))
    run("python3", "scripts/lint_outbox.py", "--me", "chatgpt_1", "--staged", "--fetch")

    mark = run(
        "python3", "scripts/inbox_sweep.py", "--me", "chatgpt_1", "--mark",
        check=False, capture=True,
    )
    print(mark.stdout)
    if mark.stderr:
        print(mark.stderr, file=sys.stderr)
    if mark.returncode not in (0, 1):
        raise RuntimeError(f"mark failed with exit {mark.returncode}")

    recent = [
        m.path for m in state.unacked
        if (m.stamp or "") >= "20260904T144100Z"
    ]
    tick_path = ROOT / "chatgpt_1/ticks/2026-09-06.md"
    tick_path.parent.mkdir(parents=True, exist_ok=True)
    tick_path.write_text(
        "\n".join([
            "# chatgpt_1 tick — 2026-09-06",
            "",
            f"- Started UTC: `{created}`",
            "- Synced `agent/chatgpt_1` with the then-current `origin/main` before processing.",
            f"- Authoritative transport: `{len(state.authoritative_paths)}` messages; zero collisions, delivery errors, or quarantine errors.",
            f"- Recovery baseline: `chatgpt_1/inbox-seen.json` was absent after the integrated backlog; `{len(state.new_items)}` addressed paths appeared unseen and `{len(state.unacked)}` acknowledgements were outstanding.",
            f"- Current obligations after the last completed handoff: `{len(recent)}` — Claude's orchard transport blocker and the coordinator's ruling. Both were read; the ruling confirms the result, closes the row, and assigns no further work to chatgpt_1.",
            f"- Published transport-recovery ACK: `{ack_path.relative_to(ROOT)}`. It acknowledges receipt only and does not reopen historical tasks.",
            "- Restored exact-path seen state with the authoritative `--mark` operation.",
            "- New message lint: staged ACK passed the current `lint_outbox.py --staged --fetch` gate.",
            "",
        ]) + "\n",
        encoding="utf-8",
    )

    status_path = ROOT / "coordination/status/chatgpt_1.md"
    status_path.write_text(
        "\n".join([
            "# chatgpt_1 status",
            "",
            f"- Updated UTC: `{created}`",
            "- Branch: `agent/chatgpt_1`",
            "- Identity: original `chatgpt_1` — opening-solver review, DP oracle, Rust anytime planner",
            "- Current task: none",
            "- State: idle; authoritative inbox recovery tick complete",
            "",
            "## Inbox",
            "",
            "The integrated backlog exposed a missing exact-path seen-state file. This tick restored it, acknowledged the outstanding transport obligations, and verified the current queue after publication. The only post-closure obligations were the orchard handoff transport blocker and the coordinator's ruling; the ruling says the result stands and no further work is owed.",
            "",
            "## Last completed task",
            "",
            "`20260904-champion-prefix-orchard` remains complete and dead on its registered normal paired-replay condition. Final report: `chatgpt_1/champion-prefix-orchard/FINAL.md`; corrected experiment artifact: `2fc4d285c391b66fc575ae2fec00d0957ea3c9e2`.",
            "",
        ]) + "\n",
        encoding="utf-8",
    )

    git("add", "chatgpt_1/inbox-seen.json", str(tick_path.relative_to(ROOT)), str(status_path.relative_to(ROOT)))
    git("commit", "-m", "chatgpt_1: reconcile authoritative inbox and record tick")
    git("push", "origin", "HEAD:agent/chatgpt_1")

    git("fetch", "origin", "main", "agent/chatgpt_1")
    verify = run(
        "python3", "scripts/inbox_sweep.py", "--me", "chatgpt_1", "--fetch",
        check=False, capture=True,
    )
    print(verify.stdout)
    if verify.stderr:
        print(verify.stderr, file=sys.stderr)
    if verify.returncode != 0:
        raise RuntimeError(f"post-publication authoritative sweep failed with exit {verify.returncode}")

    full_lint = run(
        "python3", "scripts/lint_outbox.py", "--me", "chatgpt_1", "--all", "--fetch",
        check=False, capture=True,
    )
    historical = sum(
        1 for line in full_lint.stdout.splitlines()
        if line.startswith("  coordination/messages/chatgpt_1/")
    )

    with tick_path.open("a", encoding="utf-8") as fh:
        fh.write("## Post-publication verification\n\n")
        fh.write(f"- Authoritative inbox sweep exit: `{verify.returncode}` — healthy, no unacknowledged obligations.\n")
        fh.write(f"- Full historical outbox lint exit: `{full_lint.returncode}` with `{historical}` pre-existing immutable filename violations from August. The newly published ACK passed staged lint; no immutable historical message was renamed or deleted during this tick.\n")
        fh.write("- Temporary GitHub Actions runner and one-shot finalizer removed in the cleanup commit.\n")

    with status_path.open("a", encoding="utf-8") as fh:
        fh.write("\n## Verification\n\n")
        fh.write(f"Authoritative post-publication sweep exited `{verify.returncode}`. The current queue has no unacknowledged obligations. New output passed staged lint; the namespace still contains `{historical}` immutable August filenames rejected by the newer full-history linter, recorded in the tick report rather than rewritten.\n")

    git("rm", str(WORKFLOW.relative_to(ROOT)), str(SELF.relative_to(ROOT)))
    git("add", str(tick_path.relative_to(ROOT)), str(status_path.relative_to(ROOT)))
    git("commit", "-m", "chatgpt_1: finish tick and remove temporary runner")
    git("push", "origin", "HEAD:agent/chatgpt_1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
