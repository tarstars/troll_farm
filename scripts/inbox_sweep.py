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
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

NAMESPACE = "coordination/messages/"
ACK_REQUIRED_KINDS = {"claim", "question", "blocker", "policy", "stop", "takeover", "handoff"}
MSG_RE = re.compile(r"^(?P<stamp>\d{8}T\d{6}Z)-(?P<task>.+)-(?P<kind>[a-z]+)\.md$")


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


def addressed_to_me(body: str, me: str) -> bool:
    for line in body.splitlines():
        low = line.lower()
        if low.startswith(("- to:", "- cc:")):
            targets = low.split(":", 1)[1]
            if me in targets or "both" in targets or "all" in targets:
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--me", required=True, help="my agent id, e.g. claude_1")
    ap.add_argument("--mark", action="store_true", help="advance the watermark to now")
    ap.add_argument("--fetch", action="store_true", help="git fetch origin first")
    args = ap.parse_args()

    root = pathlib.Path(git("rev-parse", "--show-toplevel").strip() or ".")
    if args.fetch:
        git("fetch", "-q", "origin")

    seen: dict[str, tuple[str, str]] = {}  # filename stem -> (path, ref)
    for ref in refs():
        for path, r in messages_on(ref):
            seen.setdefault(pathlib.Path(path).stem, (path, r))
    for path, r in messages_in_worktree(root):
        seen.setdefault(pathlib.Path(path).stem, (path, r))

    my_prefix = f"{NAMESPACE}{args.me}/"
    my_acks = {
        stem.split("-", 1)[1].rsplit("-", 1)[0]
        for stem, (path, _) in seen.items()
        if path.startswith(my_prefix) and stem.endswith("-ack")
    }

    watermark_file = root / args.me / "inbox-watermark.txt"
    watermark = ""
    if watermark_file.exists():
        watermark = watermark_file.read_text(encoding="utf-8").strip()

    new_items, unacked = [], []
    for stem, (path, ref) in sorted(seen.items()):
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
        needs_ack = (
            "requires acknowledgement: yes" in body.lower()
            or m["kind"] in ACK_REQUIRED_KINDS
        )
        if needs_ack and m["task"] not in my_acks:
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
