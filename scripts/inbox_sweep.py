#!/usr/bin/env python3
"""Report coordination messages that are new or still awaiting my acknowledgement.

Ported from icfpc2026's `scripts/inbox_sweep.py`, parameterized for this repo. The
original hardcoded a single peer id, which once hid a third agent working on another
branch for a day — so this sweeps *every* ref it can see plus the working tree, and never
assumes who the peers are.

Transport note: this repository's origin is far behind the local session branch, so remote
refs may be absent. The sweep therefore covers local branches and the working tree as
well; when the repo is pushed, remote refs are picked up with no change here.

Usage:
    python3 scripts/inbox_sweep.py --me claude_1            # report
    python3 scripts/inbox_sweep.py --me claude_1 --mark     # advance the watermark
    python3 scripts/inbox_sweep.py --me claude_1 --fetch    # git fetch first

Exit status is 1 if anything addressed to me is unacknowledged, else 0.

Acknowledgements are task-scoped but time-ordered: an ACK only covers messages for the
same task whose immutable filename timestamp is strictly earlier than the ACK.  This
prevents an old ACK from hiding a later question or blocker that reused the task id.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from collections.abc import Iterable

NAMESPACE = "coordination/messages/"
ACK_REQUIRED_KINDS = {"claim", "question", "blocker", "policy", "stop", "takeover", "handoff"}
MSG_RE = re.compile(r"^(?P<stamp>\d{8}T\d{6}Z)-(?P<task>.+)-(?P<kind>[a-z]+)\.md$")
YAML_FIELD_RE = re.compile(
    r"^[ \t]*(?P<key>[A-Za-z_][A-Za-z0-9_-]*)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*$"
)


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else ""


def refs() -> list[str]:
    names = [r.strip() for r in git("for-each-ref", "--format=%(refname)").splitlines()]
    return [r for r in names if r.startswith(("refs/heads/", "refs/remotes/"))]


def messages_on(ref: str) -> list[tuple[str, str]]:
    """Return (path, ref) for every message file visible at ref."""
    listing = git("ls-tree", "-r", "--name-only", ref, NAMESPACE)
    return [(p, ref) for p in listing.splitlines() if MSG_RE.match(pathlib.Path(p).name)]


def messages_in_worktree(root: pathlib.Path) -> list[tuple[str, str]]:
    base = root / NAMESPACE
    if not base.is_dir():
        return []
    return [
        (str(p.relative_to(root)), "worktree")
        for p in base.rglob("*.md")
        if MSG_RE.match(p.name)
    ]


def body_of(path: str, ref: str, root: pathlib.Path) -> str:
    if ref == "worktree":
        try:
            return (root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
    return git("show", f"{ref}:{path}")


def yaml_front_matter(body: str) -> dict[str, str]:
    """Return flat fields from an optional leading YAML front matter block."""
    lines = body.splitlines()
    start = 0
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines) or lines[start].strip() != "---":
        return {}

    fields: dict[str, str] = {}
    for line in lines[start + 1:]:
        if line.strip() == "---":
            return fields
        match = YAML_FIELD_RE.match(line)
        if match:
            fields[match["key"].lower()] = match["value"].strip()
    return {}


def legacy_values(body: str, key: str) -> list[str]:
    """Return exact `- Key:` values without accepting longer key prefixes."""
    field = re.compile(
        rf"^[ \t]*-[ \t]*{re.escape(key)}[ \t]*:[ \t]*(.*?)[ \t]*$",
        re.IGNORECASE,
    )
    return [
        match.group(1)
        for line in body.splitlines()
        if (match := field.match(line))
    ]


def scalar_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'`":
        return value[1:-1].strip()
    return value


def task_of(body: str, fallback: str) -> str:
    """Explicit metadata is authoritative; filenames embed arbitrary extra words.

    Pairing acks on filename segments broke twice in practice: a sender whose message was
    named `...-iteration2-backlog-ack-n1-claim.md` yields the filename task
    `iteration2-backlog-ack-n1`, which no reasonably-named ack will ever match.
    """
    yaml = yaml_front_matter(body)
    if "task_id" in yaml:
        return scalar_value(yaml["task_id"]) or fallback
    legacy = legacy_values(body, "Task")
    if legacy:
        return scalar_value(legacy[0]) or fallback
    return fallback


def recipient_tokens(value: str) -> set[str]:
    """Tokenize ids exactly, including YAML list and comma-separated forms."""
    return {token.lower() for token in re.findall(r"[A-Za-z0-9_]+", value)}


def addressed_to_me(body: str, me: str) -> bool:
    yaml = yaml_front_matter(body)
    if "to" in yaml or "cc" in yaml:
        values = [yaml[key] for key in ("to", "cc") if key in yaml]
    else:
        values = legacy_values(body, "To") + legacy_values(body, "CC")
    targets = set().union(*(recipient_tokens(value) for value in values))
    return bool({me.lower(), "both", "all"} & targets)


def parse_boolean(value: str) -> bool | None:
    normalized = scalar_value(value).lower()
    if normalized in {"true", "yes", "1", "on"}:
        return True
    if normalized in {"false", "no", "0", "off"}:
        return False
    return None


def message_kind(body: str, fallback: str) -> str:
    """Normalize the current YAML type vocabulary, falling back to the filename."""
    raw = scalar_value(yaml_front_matter(body).get("type", "")).lower().replace("-", "_")
    aliases = {
        "ack": "ack",
        "acknowledgement": "ack",
        "review_ack": "ack",
        "blocker": "blocker",
        "review_blocker": "blocker",
        "handoff": "handoff",
        "review_handoff": "handoff",
        "claim": "claim",
        "question": "question",
        "policy": "policy",
        "stop": "stop",
        "takeover": "takeover",
        "update": "update",
        "release": "release",
    }
    return aliases.get(raw, fallback)


def requires_ack(body: str, kind: str) -> bool:
    yaml = yaml_front_matter(body)
    yaml_required = parse_boolean(yaml["requires_ack"]) if "requires_ack" in yaml else None
    legacy_required = bool(
        re.search(
            r"requires[ \t]+acknowledgement[ \t]*:[ \t]*yes\b",
            body,
            re.IGNORECASE,
        )
    )
    return yaml_required is True or legacy_required or kind in ACK_REQUIRED_KINDS


def deduplicate_messages(
    locations: Iterable[tuple[str, str]],
) -> dict[str, tuple[str, str]]:
    """Deduplicate the same immutable path across refs, not filename stems."""
    seen: dict[str, tuple[str, str]] = {}
    for path, ref in locations:
        seen.setdefault(path, (path, ref))
    return seen


def acknowledged_by_later_ack(
    task: str, message_stamp: str, latest_ack_stamp_by_task: dict[str, str]
) -> bool:
    """Return whether a strictly later ACK exists for this task message."""
    return latest_ack_stamp_by_task.get(task, "") > message_stamp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--me", required=True, help="my agent id, e.g. claude_1")
    ap.add_argument("--mark", action="store_true", help="advance the watermark to now")
    ap.add_argument("--fetch", action="store_true", help="git fetch origin first")
    args = ap.parse_args()

    root = pathlib.Path(git("rev-parse", "--show-toplevel").strip() or ".")
    if args.fetch:
        git("fetch", "-q", "origin")

    locations: list[tuple[str, str]] = []
    for ref in refs():
        locations.extend(messages_on(ref))
    locations.extend(messages_in_worktree(root))
    seen = deduplicate_messages(locations)

    my_prefix = f"{NAMESPACE}{args.me}/"
    latest_ack_stamp_by_task: dict[str, str] = {}
    for path, ref in seen.values():
        if not path.startswith(my_prefix):
            continue
        m = MSG_RE.match(pathlib.Path(path).name)
        if not m:
            continue
        body = body_of(path, ref, root)
        if message_kind(body, m["kind"]) != "ack":
            continue
        task = task_of(body, m["task"])
        latest_ack_stamp_by_task[task] = max(
            latest_ack_stamp_by_task.get(task, ""), m["stamp"]
        )

    watermark_file = root / args.me / "inbox-watermark.txt"
    watermark = ""
    if watermark_file.exists():
        watermark = watermark_file.read_text(encoding="utf-8").strip()

    new_items, unacked = [], []
    for path, ref in sorted(seen.values()):
        m = MSG_RE.match(pathlib.Path(path).name)
        if not m:
            continue
        sender = path[len(NAMESPACE):].split("/", 1)[0]
        if sender == args.me:
            continue
        body = body_of(path, ref, root)
        if not addressed_to_me(body, args.me):
            continue
        if m["stamp"] > watermark:
            new_items.append((path, ref))
        needs_ack = requires_ack(body, message_kind(body, m["kind"]))
        task = task_of(body, m["task"])
        if needs_ack and not acknowledged_by_later_ack(
            task, m["stamp"], latest_ack_stamp_by_task
        ):
            unacked.append((path, ref))

    print(f"agent: {args.me}   watermark: {watermark or '(none)'}   scanned: {len(seen)} messages")
    print(f"\nnew since watermark ({len(new_items)}):")
    for path, ref in new_items:
        print(f"  {path}   [{ref}]")
    print(f"\nunacknowledged, ack required ({len(unacked)}):")
    for path, ref in unacked:
        print(f"  {path}   [{ref}]")

    if args.mark:
        stamps = [MSG_RE.match(pathlib.Path(p).name)["stamp"] for p, _ in seen.values()
                  if MSG_RE.match(pathlib.Path(p).name)]
        if stamps:
            watermark_file.parent.mkdir(parents=True, exist_ok=True)
            watermark_file.write_text(max(stamps) + "\n", encoding="utf-8")
            print(f"\nwatermark advanced to {max(stamps)}")

    return 1 if unacked else 0


if __name__ == "__main__":
    sys.exit(main())
