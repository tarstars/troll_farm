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
   record instead of correcting it;
5. WIP limit (owner decision 2026-08-17): a NEW handoff is rejected while the
   sender's previous ack-requiring handoff for the same task is still awaiting
   acknowledgement — publish after the ack lands, or name the pending handoff
   in `supersedes`. Sender-side only: published messages are immutable, so this
   can never fire retroactively;
6. evidence gate (owner decision 2026-08-17): a NEW handoff whose body asserts
   a registered cause label (`CAUSE_LABEL_TOKENS`) must carry a `review_ref:`
   front-matter field naming a review file that exists on an authoritative
   remote ref — cause claims travel only with their accepted instrument review.

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
import re
import sys

try:  # invoked as `python3 scripts/lint_outbox.py`
    import inbox_sweep
except ImportError:  # invoked as `python3 -m scripts.lint_outbox`
    from scripts import inbox_sweep


# The namespace is closed: anything that is not a message must be listed here
# explicitly, or it is an error. Silently skipping unrecognised files hid typo'd
# filenames, which never get delivered and are never reported (finding TQ-5).
NAMESPACE_ALLOWLIST = frozenset({"README.md"})


def worktree_namespace(root: pathlib.Path, me: str) -> dict[str, str]:
    """Every regular file in my namespace → its text, from the worktree."""
    base = root / inbox_sweep.NAMESPACE / me
    if not base.is_dir():
        return {}
    return {
        str(p.relative_to(root)): p.read_text(encoding="utf-8")
        for p in sorted(base.rglob("*"))
        if p.is_file()
    }


def staged_namespace(me: str) -> dict[str, str]:
    """Every file in my namespace → its text, from the Git index.

    Git publishes the index, not the worktree, so this is what a commit would
    actually deliver (finding TQ-4).
    """
    prefix = f"{inbox_sweep.NAMESPACE}{me}/"
    out: dict[str, str] = {}
    for line in inbox_sweep.git("ls-files", "-s", "--", prefix).splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) != 3 or not path:
            continue
        out[path] = inbox_sweep.git("cat-file", "blob", parts[1])
    return out


def head_namespace(me: str) -> set[str]:
    """Message paths my namespace currently has in HEAD (empty on unborn HEAD)."""
    prefix = f"{inbox_sweep.NAMESPACE}{me}/"
    listing = inbox_sweep.run_git("ls-tree", "-r", "--name-only", "HEAD", "--", prefix)
    if listing.returncode != 0:
        return set()
    return {
        line.strip() for line in listing.stdout.splitlines()
        if line.strip() and classify(line.strip()) == "message"
    }


def classify(path: str) -> str:
    """`message`, `allowed` (documentation) or `foreign` (a namespace error)."""
    name = pathlib.Path(path).name
    if inbox_sweep.MSG_RE.match(name):
        return "message"
    if name in NAMESPACE_ALLOWLIST:
        return "allowed"
    return "foreign"


def published_bodies(per_path: dict[str, dict[str, list[str]]], path: str) -> list[str]:
    return [inbox_sweep.git("cat-file", "blob", oid) for oid in per_path[path]]


# ---------------------------------------------------------------------------
# Iteration-pool gates (owner decision 2026-08-17). Sender-side ONLY: published
# messages are immutable, so neither check can ever fire retroactively.
# ---------------------------------------------------------------------------

# The chartered cause vocabulary of the standing-troll audit
# (coordination/tasks/20260816-h-starve-1-standing-troll-audit.md). A handoff
# asserting any of these is making a causal claim, and causal claims travel
# only with the review that accepted the instrument producing them. Extend the
# set when a task charters new cause labels.
CAUSE_LABEL_TOKENS = frozenset({
    # Legacy first-instrument vocabulary (withdrawn tables; kept so older
    # threads stay gated):
    "GENERATOR_GAP", "NO_WORK_ON_MAP", "UNIT_CANNOT_REACH_WORK",
    "STUCK_COMMITMENT", "ALL_WAIT_CAUSE_UNDETERMINED",
    # Pool-#3 vocabulary (owner's three-level taxonomy, iteration 2026-08-17;
    # gap found by codex_1's gates review — the new labels could bypass the
    # gate entirely). Cause tables MUST serialize with exactly these tokens:
    "NO_GOAL_ASSIGNED", "GOAL_SPLIT_WRONG", "WORLD_INTERACTION",
    "CANNOT_USE_WORK", "NOT_STARVED",
})


def parse_published_messages(
    per_path: dict[str, list[str]]
) -> list["inbox_sweep.Message"]:
    """Parse every single-body authoritative message. Collision paths (more
    than one body) are already reported elsewhere and are skipped here."""
    out = []
    for path, oid_map in sorted(per_path.items()):
        # per_path maps path -> {blob oid -> refs}; >1 oid is a collision,
        # reported elsewhere.
        if len(oid_map) != 1:
            continue
        try:
            body = inbox_sweep.git("cat-file", "blob", next(iter(oid_map)))
        except inbox_sweep.GitError:
            continue
        out.append(inbox_sweep.Message(path, "authoritative", body))
    return out


def _own_supersedes(msg: "inbox_sweep.Message") -> set[str]:
    try:
        return set(inbox_sweep.parse_json_list(msg.fields.get("supersedes", "[]")))
    except Exception:
        return set()


def wip_limit_errors(
    msg: "inbox_sweep.Message",
    published_msgs: list["inbox_sweep.Message"],
    batch_msgs: list["inbox_sweep.Message"],
) -> list[str]:
    """One in-flight ack-requiring handoff per sender per task.

    A prior handoff is retired when ANY published message names it in `ack_for`
    or `supersedes`, or when the staged message itself supersedes it. The
    protocol's canonical retirement is the integrator's ack; the lint accepts
    any published ack because it is a tripwire, not a court.
    """
    if msg.kind != "handoff":
        return []
    retired: set[str] = set()
    for m in published_msgs:
        for field in ("ack_for", "supersedes"):
            try:
                retired |= set(inbox_sweep.parse_json_list(m.fields.get(field, "[]")))
            except Exception:
                continue
    retired |= _own_supersedes(msg)
    pending = [
        m.path
        for m in published_msgs + batch_msgs
        if m.kind == "handoff" and m.sender == msg.sender and m.task == msg.task
        and m.path != msg.path and m.stamp < msg.stamp
        and inbox_sweep.requires_ack(m.body, m.kind)
        and m.path not in retired
    ]
    if pending:
        return [
            f"WIP limit: prior ack-requiring handoff for task {msg.task!r} is still "
            f"awaiting acknowledgement ({pending[-1]!r}); publish after it is acked, "
            "or name it in `supersedes` (owner decision 2026-08-17)"
        ]
    return []


def evidence_gate_errors(
    msg: "inbox_sweep.Message", remote_ref_names: set[str]
) -> list[str]:
    """A handoff asserting a chartered cause label must carry `review_ref:`
    naming a review file that exists on an authoritative remote ref."""
    if msg.kind != "handoff":
        return []
    tokens = sorted(t for t in CAUSE_LABEL_TOKENS if t in msg.body)
    if not tokens:
        return []
    review_ref = msg.fields.get("review_ref", "").strip().strip('"').strip("'")
    if not review_ref:
        return [
            f"evidence gate: handoff asserts cause label(s) {', '.join(tokens)} "
            "without a `review_ref:` front-matter field naming the accepted "
            "instrument review (owner decision 2026-08-17)"
        ]
    for ref in sorted(remote_ref_names):
        if inbox_sweep.run_git("cat-file", "-e", f"{ref}:{review_ref}").returncode == 0:
            return []
    return [
        f"evidence gate: review_ref {review_ref!r} not found on any "
        "authoritative remote ref — publish the review before the claim"
    ]


def cross_task_reference_errors(
    msg: "inbox_sweep.Message", published_msgs: list["inbox_sweep.Message"]
) -> list[str]:
    """`supersedes`/`ack_for` entries must belong to this message's task.

    A syntactically valid path to a REAL message of a DIFFERENT task passes
    every shape and existence check; on 2026-08-18 such an entry falsely
    superseded an unrelated August-15 handoff (built by substring search over
    two tasks sharing a "phase1-handoff" name). The comparison is by the
    referenced message's front-matter `task_id`, never by filename, because
    filename middles are not full task ids. Escape hatch: an explicit
    `cross-task:` marker in the body naming why the reference is deliberate.
    Sender-side only, like every gate here.
    """
    if "cross-task:" in msg.body:
        return []
    own_task = msg.fields.get("task_id", "").strip()
    if not own_task:
        return []
    by_path = {m.path: m for m in published_msgs}
    errors: list[str] = []
    for field in ("supersedes", "ack_for"):
        try:
            entries = inbox_sweep.parse_json_list(msg.fields.get(field, "[]"))
        except Exception:
            continue  # malformed arrays are validate_v2's finding, not ours
        for entry in entries:
            ref_msg = by_path.get(entry)
            if ref_msg is None or not ref_msg.is_v2:
                continue  # existence is validate_v2's job; legacy has no task_id
            ref_task = ref_msg.fields.get("task_id", "").strip()
            if ref_task and ref_task != own_task:
                errors.append(
                    f"cross-task reference: `{field}` names {entry!r} of task "
                    f"{ref_task!r}, not this message's task {own_task!r}; "
                    "same-task references only, or carry an explicit "
                    "`cross-task:` marker in the body naming why "
                    "(lint hardening 2026-08-18)"
                )
    return errors


DEFERRED_LINE_RE = re.compile(r"^DEFERRED:", re.MULTILINE)


def deferral_shape_errors(msg: "inbox_sweep.Message") -> list[str]:
    """A declared deferral must BE a queue item (owner-adopted 2026-08-18).

    Twice in one day a legitimate deferral left every inbox empty while open
    work existed: the postponement lived in prose, but everyone polls the
    queue. The rule: a message declaring a deferral (a body line starting with
    the canonical marker `DEFERRED:`) must carry `requires_ack: true` and name
    ITS OWN SENDER among `to`, so the deferring agent's next session finds the
    postponed job as its first unacknowledged item and acknowledges it by
    starting. Prose mentions of the word "deferred" mid-line do not trigger;
    only the line-start marker does. Sender-side only, never retroactive.
    """
    if not DEFERRED_LINE_RE.search(msg.body):
        return []
    errors: list[str] = []
    if inbox_sweep.parse_boolean(msg.fields.get("requires_ack", "")) is not True:
        errors.append(
            "deferral shape: body declares `DEFERRED:` but requires_ack is not "
            "true — a deferral must be a queue item, not an announcement "
            "(owner-adopted 2026-08-18)"
        )
    to_raw = msg.fields.get("to", "")
    tokens = inbox_sweep.recipient_tokens(to_raw)
    if msg.sender.lower() not in tokens:
        errors.append(
            f"deferral shape: body declares `DEFERRED:` but `to` {to_raw!r} "
            f"does not include the sender {msg.sender!r} — self-address the "
            "deferral so your own next sweep surfaces it "
            "(owner-adopted 2026-08-18)"
        )
    return errors


CARD_LINE_RE = re.compile(r"^CARD:", re.MULTILINE)


def card_ack_errors(
    msg: "inbox_sweep.Message", published_msgs: list["inbox_sweep.Message"]
) -> list[str]:
    """A `CARD:` message is discharged by delivery or replacement, never by a
    bare receipt-ack (protocol §10, corrected route 2026-08-19).

    `ack_for` is the transport's only discharge mechanism (`supersedes` is
    inert for acknowledgement — proven by claude_1 reading the sweep), so the
    gate sits on the ACK side: a staged message that names a published `CARD:`
    message in `ack_for` must either BE the delivery (kind handoff) or carry
    its own line-start `DEFERRED:` replacement card. Anything else discharges
    standing work while leaving no queue item — the fourth stall shape.
    """
    try:
        targets = inbox_sweep.parse_json_list(msg.fields.get("ack_for", "[]"))
    except Exception:
        return []  # malformed arrays are validate_v2's finding
    if not targets:
        return []
    by_path = {m.path: m for m in published_msgs}
    card_targets = [
        t for t in targets
        if (ref := by_path.get(t)) is not None and ref.is_v2
        and CARD_LINE_RE.search(ref.body)
    ]
    if not card_targets:
        return []
    if msg.kind == "handoff" or DEFERRED_LINE_RE.search(msg.body):
        return []
    return [
        f"card ack: `ack_for` discharges CARD message(s) {card_targets!r} but "
        "this message is neither the delivery handoff nor a DEFERRED: "
        "replacement — bare receipt-acks of cards are forbidden "
        "(protocol §10, 2026-08-19)"
    ]


def current_branch() -> str:
    """Branch HEAD points at, or "" when detached.

    `symbolic-ref`, not `rev-parse --abbrev-ref`: the latter fails outright on
    an unborn branch, which is exactly the state a fresh agent worktree is in
    before its first commit — precisely when this warning is most useful.
    """
    out = inbox_sweep.run_git("symbolic-ref", "--short", "HEAD")
    return out.stdout.strip() if out.returncode == 0 else ""


def lint_message(
    path: str,
    text: str,
    authoritative_paths: set[str],
    remote_ref_names: set[str],
    published: bool,
    legacy_baseline: dict[str, str] | None = None,
    baseline_present: bool = False,
) -> list[str]:
    msg = inbox_sweep.Message(path, "worktree", text)
    if not msg.is_v2:
        # Transport rule 5 grandfathers legacy messages, but only the exact
        # paths pinned in the frozen baseline. The lint ignored the baseline
        # entirely, so a NEW no-schema message linted clean and then became a
        # permanent delivery error at the receiver (finding F9a).
        if not published:
            return ["missing `schema_version: 2` front matter; new messages "
                    "must be schema v2"]
        if baseline_present and path not in (legacy_baseline or {}):
            return ["legacy message not in the frozen legacy baseline; messages "
                    "published after the v2 migration must declare "
                    "schema_version: 2"]
        return []
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
    ap.add_argument(
        "--staged",
        action="store_true",
        help="lint the Git index — the bytes a commit would actually publish",
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

    # The frozen legacy baseline lives on the coordinator's canonical ref; the
    # lint must apply it or it clears messages the sweep permanently rejects.
    legacy_baseline: dict[str, str] = {}
    baseline_present = False
    try:
        coordinator = inbox_sweep.coordinator_agent()
        if coordinator:
            legacy_baseline, baseline_present = inbox_sweep.load_legacy_baseline(
                f"{inbox_sweep.REMOTE_PREFIX}agent/{coordinator}")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    tree = staged_namespace(args.me) if args.staged else worktree_namespace(root, args.me)
    source = "index (staged)" if args.staged else "worktree"
    errors: list[tuple[str, str]] = []
    linted = 0

    # Iteration-pool gates (owner decision 2026-08-17) need the published
    # corpus parsed once, plus the new messages of this very batch so two
    # same-task handoffs staged together cannot slip past the WIP limit.
    published_msgs = parse_published_messages(per_path)
    batch_msgs = [
        inbox_sweep.Message(p, source, t)
        for p, t in sorted(tree.items())
        if classify(p) == "message" and p not in authoritative_paths
    ]

    # A v2 message is delivered only from `agent/<sender>`. The lint cannot check
    # that for an unpublished message — but it CAN check that publishing from
    # HERE would satisfy it. Three of the six real quarantine entries exist
    # because messages were published to task branches (finding F9b).
    # Only when something is actually unpublished: with everything already on a
    # remote ref there is nothing to publish from the wrong branch, and firing
    # then would make diagnostic lints of a peer's namespace noisy.
    branch = current_branch()
    canonical_branch = f"agent/{args.me}"
    unpublished = [p for p in tree
                   if p not in authoritative_paths and classify(p) == "message"]
    if unpublished and branch and branch != canonical_branch:
        errors.append((
            f"{inbox_sweep.NAMESPACE}{args.me}",
            f"HEAD is {branch!r}, not your canonical branch {canonical_branch!r}; "
            "a message published from here is not delivered and becomes a "
            "permanent delivery error only the coordinator can clear",
        ))
    for path, text in sorted(tree.items()):
        kind = classify(path)
        if kind == "allowed":
            continue
        if kind == "foreign":
            errors.append((
                path,
                f"{pathlib.Path(path).name!r} is not a message and is not an allowed "
                "namespace file; a message is <UTC-stamp>-<task-id>-<kind>.md "
                f"(allowed: {', '.join(sorted(NAMESPACE_ALLOWLIST))})",
            ))
            continue
        published = path in authoritative_paths
        if published:
            # The receiver treats differing bodies at one path as a collision;
            # matching one side of it is not immutability (finding TQ-6).
            if len(per_path[path]) != 1:
                errors.append((
                    path,
                    "immutable-path collision: this path has different bytes on "
                    f"{len(per_path[path])} authoritative refs",
                ))
                continue
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
                path, text, authoritative_paths, remote_ref_names, published,
                legacy_baseline, baseline_present
            )
        )
        if not published:
            gate_msg = inbox_sweep.Message(path, source, text)
            if gate_msg.is_v2:
                errors.extend(
                    (path, error)
                    for error in wip_limit_errors(gate_msg, published_msgs, batch_msgs)
                )
                errors.extend(
                    (path, error)
                    for error in evidence_gate_errors(gate_msg, remote_ref_names)
                )
                errors.extend(
                    (path, error)
                    for error in cross_task_reference_errors(gate_msg, published_msgs)
                )
                errors.extend(
                    (path, error) for error in deferral_shape_errors(gate_msg)
                )
                errors.extend(
                    (path, error)
                    for error in card_ack_errors(gate_msg, published_msgs)
                )

    # A message present in HEAD but absent from the proposed tree would be
    # deleted by this commit. Enumerating only existing files hid that entirely
    # (finding TQ-4). The baseline is HEAD, not every authoritative ref: a peer's
    # newest messages legitimately are not on my branch, and comparing against
    # all refs reports those as deletions.
    for path in sorted(head_namespace(args.me)):
        if path not in tree:
            errors.append((
                path,
                f"message is in HEAD but missing from the {source}; committing this "
                "tree would delete it, and published messages are immutable",
            ))

    print(f"agent: {args.me}")
    print(
        f"outbox: {inbox_sweep.NAMESPACE}{args.me} from {source} "
        f"({len(tree)} files, {linted} linted, "
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
