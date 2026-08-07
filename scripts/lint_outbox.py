#!/usr/bin/env python3
"""Sender-side outbox lint for transport schema v2 — run BEFORE pushing.

`scripts/inbox_sweep.py` validates messages on the receiving side, after they
are already published and immutable: a violation discovered there costs a
superseding correction and shows up as a delivery error in every peer's inbox
until the coordinator adjudicates it. This lint applies the same v2 rules to the
messages still sitting in the sender's worktree, where they can simply be fixed.

Checks, for every `coordination/messages/<me>/**.md`:

1. the filename matches `<UTC-stamp>-<task-id>-<kind>.md`;
2. the message declares `schema_version: 2` — new messages are never legacy;
3. every rule `inbox_sweep.validate_v2` enforces except canonical-branch
   presence, which an unpublished message cannot satisfy: `message_id` equals
   the path, `from` equals the sender namespace, the kind is one of the
   canonical kinds, `ack_for`/`supersedes` are single-line JSON string arrays
   naming published messages, and a handoff's `artifact_commit` is a full 40-hex
   object reachable from the sender's canonical remote ref containing every
   entry of a non-empty `artifact_paths` (artifacts are published before the
   message announcing them);
4. a message whose path is already published is byte-identical to what was
   published — published messages are immutable, and editing one rewrites the
   record instead of correcting it.

Already-published messages are otherwise the sweep's business and are skipped
unless `--all` is given. Because ack/handoff targets are validated against
`refs/remotes/origin/**`, run with `--fetch` (or fetch first) when the clone's
remote-tracking refs may be stale — otherwise a target published by a peer looks
missing.

Usage:
    python3 scripts/lint_outbox.py --me local_claude_1
    python3 scripts/lint_outbox.py --me local_claude_1 --fetch  # refresh refs first
    python3 scripts/lint_outbox.py --me local_claude_1 --all    # published too

Exit status: 0 clean; 2 lint errors, an unusable Git transport, or a failed fetch.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

try:  # invoked as `python3 scripts/lint_outbox.py`
    import inbox_sweep
except ImportError:  # invoked as `python3 -m scripts.lint_outbox`
    from scripts import inbox_sweep


def outbox_paths(root: pathlib.Path, me: str) -> list[str]:
    """Candidate messages in my own namespace, published or not.

    A message filename always begins with its UTC stamp, so a digit-prefixed
    file is one and must parse as one — that is how a typo'd stamp or kind gets
    caught instead of silently never being delivered. Everything else in the
    namespace (`README.md`) is documentation and is not a message.
    """
    base = root / inbox_sweep.NAMESPACE / me
    if not base.is_dir():
        return []
    return sorted(
        str(p.relative_to(root))
        for p in base.rglob("*.md")
        if p.is_file() and p.name[:1].isdigit()
    )


def published_bodies(per_path: dict[str, dict[str, list[str]]], path: str) -> list[str]:
    return [inbox_sweep.git("cat-file", "blob", oid) for oid in per_path[path]]


def lint_message(
    path: str,
    text: str,
    authoritative_paths: set[str],
    remote_ref_names: set[str],
    published: bool,
) -> list[str]:
    name = pathlib.Path(path).name
    if not inbox_sweep.MSG_RE.match(name):
        return [
            f"{name!r} does not match the message filename pattern "
            "<UTC-stamp>-<task-id>-<kind>.md"
        ]
    msg = inbox_sweep.Message(path, "worktree", text)
    if not msg.is_v2:
        # Transport rule 5 grandfathers legacy messages indefinitely, so this
        # binds new messages only — a published legacy message stays valid.
        return [] if published else [
            "missing `schema_version: 2` front matter; new messages must be schema v2"
        ]
    return inbox_sweep.validate_v2(
        msg, authoritative_paths, {}, remote_ref_names, require_canonical=False
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--me", required=True, help="my agent id, e.g. local_claude_1")
    ap.add_argument("--fetch", action="store_true", help="checked git fetch origin first")
    ap.add_argument(
        "--all",
        action="store_true",
        help="also lint messages already published on an authoritative remote ref",
    )
    args = ap.parse_args()

    try:
        root = pathlib.Path(inbox_sweep.git("rev-parse", "--show-toplevel").strip())
    except inbox_sweep.GitError as exc:
        print(f"not inside a git repository: {exc}", file=sys.stderr)
        return 2

    if args.fetch:
        fetch = inbox_sweep.run_git("fetch", "origin")
        if fetch.returncode != 0:
            print("git fetch origin failed:", file=sys.stderr)
            print(fetch.stderr.rstrip(), file=sys.stderr)
            print("outbox: NOT LINTED (remote refs stale)")
            return 2

    try:
        refs, per_path = inbox_sweep.scan_authoritative()
    except inbox_sweep.GitError as exc:
        print(f"git error while scanning remote refs: {exc}", file=sys.stderr)
        return 2
    authoritative_paths = set(per_path)
    remote_ref_names = set(refs)

    paths = outbox_paths(root, args.me)
    errors: list[tuple[str, str]] = []
    linted = 0
    for path in paths:
        text = (root / path).read_text(encoding="utf-8")
        published = path in authoritative_paths
        if published:
            if text not in published_bodies(per_path, path):
                errors.append((
                    path,
                    "already published with different bytes; published messages are "
                    "immutable — publish a correction naming it in `supersedes`",
                ))
                continue
            if not args.all:
                continue
        linted += 1
        errors.extend(
            (path, error)
            for error in lint_message(
                path, text, authoritative_paths, remote_ref_names, published
            )
        )

    print(f"agent: {args.me}")
    print(
        f"outbox: {inbox_sweep.NAMESPACE}{args.me} "
        f"({len(paths)} files, {linted} linted, "
        f"{len(refs)} authoritative remote refs)"
    )
    print(f"\nerrors ({len(errors)}):")
    for path, error in errors:
        print(f"  {path}: {error}")
    if any("unknown v2 message kind" in error for _, error in errors):
        kinds = ", ".join(repr(k) for k in sorted(inbox_sweep.V2_KNOWN_KINDS))
        print(f"  hint: use one of the canonical v2 kinds: {kinds}")

    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
