#!/usr/bin/env python3
"""Authoritative inbox sweep over remote Git refs — transport schema v2.

Origin story: ported from icfpc2026's `scripts/inbox_sweep.py`, then hardened per
`coordination/tasks/20260805-coordination-transport-hardening.md` after the 2026-08-05
banana-R2 incident (stale watermark + unpushed-ACK false negatives + task/time ACK
pairing forced a synthetic timestamp).

Transport rules implemented here:

1. Only `refs/remotes/origin/**` is authoritative for cross-agent delivery and
   acknowledgement. Local branches and the working tree are shown only behind
   `--include-local`, labeled diagnostic/unpublished, and never change counts or
   exit status.
2. `--fetch` is checked: on failure the tool prints Git stderr, labels the inbox
   `STALE / NOT AUTHORITATIVE`, and exits 2 without claiming any message state.
3. The same immutable message path with different bytes on two authoritative remote
   refs is an immutable-path collision (exit 2). Identical copies deduplicate.
4. Messages declaring `schema_version: 2` (or higher) are validated strictly:
   `message_id` must equal the repository-relative path, `from` must equal the
   sender namespace, `ack_for`/`supersedes` are single-line JSON arrays parsed via
   `json.loads` (no PyYAML), the message must be present on canonical
   `refs/remotes/origin/agent/<from>`, ACK/correction targets must be exact
   existing message paths, and a handoff's `artifact_commit` must be a full 40-hex
   object reachable from `origin/<artifact_ref>` containing every entry of a
   non-empty `artifact_paths` array.
   Malformed or incomplete addressed messages appear under `delivery errors` and
   make the command exit 2.
5. Legacy messages (no `schema_version`, or < 2) keep the old parsing rules
   indefinitely. A legacy task/time ACK covers only earlier legacy messages of the
   same task and never acknowledges a v2 message; a v2 ACK acknowledges exactly the
   paths listed in `ack_for` and nothing else.
6. Newness is exact-path membership in agent-owned `<agent-id>/inbox-seen.json`
   (atomic, deterministic writes). A missing seen-state file falls back once to the
   legacy `<agent-id>/inbox-watermark.txt` as a migration hint; the legacy file is
   never rewritten or deleted. Marking seen never acknowledges anything.

Usage:
    python3 scripts/inbox_sweep.py --me claude_1                    # report
    python3 scripts/inbox_sweep.py --me claude_1 --fetch            # checked fetch first
    python3 scripts/inbox_sweep.py --me claude_1 --mark             # record seen paths
    python3 scripts/inbox_sweep.py --me claude_1 --task <task-id>   # exact-task filter
    python3 scripts/inbox_sweep.py --me claude_1 --sender <peer>    # exact-sender filter
    python3 scripts/inbox_sweep.py --me claude_1 --include-local    # + diagnostics

Exit status: 0 healthy and nothing unacknowledged; 1 healthy with unacknowledged
ack-required messages in the current selection; 2 transport/schema/delivery errors
(failed fetch, immutable-path collision, malformed or incomplete addressed message).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable

NAMESPACE = "coordination/messages/"
REMOTE_PREFIX = "refs/remotes/origin/"
ACK_REQUIRED_KINDS = {
    "claim", "question", "blocker", "policy", "stop", "takeover", "handoff", "correction",
}
V2_KNOWN_KINDS = {
    "claim", "progress", "question", "blocker", "policy", "stop", "takeover",
    "handoff", "ack", "release", "integrated", "update", "correction",
}
V2_REQUIRED_FIELDS = (
    "schema_version", "type", "task_id", "from", "to", "cc", "message_id",
    "requires_ack", "ack_for", "supersedes", "created_utc",
)
V2_HANDOFF_FIELDS = ("artifact_ref", "artifact_commit", "artifact_paths")
MSG_RE = re.compile(r"^(?P<stamp>\d{8}T\d{6}Z)-(?P<task>.+)-(?P<kind>[a-z]+)\.md$")
YAML_FIELD_RE = re.compile(
    r"^[ \t]*(?P<key>[A-Za-z_][A-Za-z0-9_-]*)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*$"
)
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
SEEN_STATE_SCHEMA_VERSION = 1


class GitError(RuntimeError):
    """A git invocation failed; stderr is preserved in the message."""


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, errors="replace"
    )


def git(*args: str) -> str:
    """Checked git call: never silently converts a failure into an empty string."""
    out = run_git(*args)
    if out.returncode != 0:
        raise GitError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout


def git_ok(*args: str) -> bool:
    return run_git(*args).returncode == 0


def commit_exists(commit: str) -> bool:
    return git_ok("cat-file", "-e", f"{commit}^{{commit}}")


def is_ancestor(commit: str, ref: str) -> bool:
    return git_ok("merge-base", "--is-ancestor", commit, ref)


def path_in_commit(commit: str, path: str) -> bool:
    return git_ok("cat-file", "-e", f"{commit}:{path}")


# ---------------------------------------------------------------------------
# Front-matter / legacy parsing (unchanged legacy semantics)
# ---------------------------------------------------------------------------

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
    """Explicit metadata is authoritative; filenames embed arbitrary extra words."""
    yaml = yaml_front_matter(body)
    if "task_id" in yaml:
        return scalar_value(yaml["task_id"]) or fallback
    legacy = legacy_values(body, "Task")
    if legacy:
        return scalar_value(legacy[0]) or fallback
    return fallback


def recipient_tokens(value: str) -> set[str]:
    """Tokenize ids exactly, including YAML/JSON list and comma-separated forms."""
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
    """Normalize the YAML type vocabulary, falling back to the filename kind."""
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
        "progress": "progress",
        "integrated": "integrated",
        "correction": "correction",
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


def schema_version_of(fields: dict[str, str]) -> tuple[int, str | None]:
    """Return (version, error). Version 0 means legacy (field absent)."""
    if "schema_version" not in fields:
        return 0, None
    raw = scalar_value(fields["schema_version"])
    try:
        return int(raw), None
    except ValueError:
        return 2, f"schema_version is not an integer: {raw!r}"


def parse_json_list(value: str) -> list[str]:
    """Parse a single-line JSON array of strings (spec: json.loads, no PyYAML)."""
    data = json.loads(value)
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise ValueError("not a JSON array of strings")
    return data


# ---------------------------------------------------------------------------
# Message records and remote scanning
# ---------------------------------------------------------------------------

def sender_of(path: str) -> str:
    """Sender namespace: the first component after `coordination/messages/`."""
    return path[len(NAMESPACE):].split("/", 1)[0]


class Message:
    """One immutable message as observed on a set of refs."""

    def __init__(self, path: str, ref: str, body: str) -> None:
        self.path = path
        self.ref = ref
        self.body = body
        name = pathlib.Path(path).name
        m = MSG_RE.match(name)
        self.stamp = m["stamp"] if m else ""
        self.filename_task = m["task"] if m else ""
        self.filename_kind = m["kind"] if m else ""
        self.sender = sender_of(path)
        self.fields = yaml_front_matter(body)
        self.kind = message_kind(body, self.filename_kind)
        self.task = task_of(body, self.filename_task)
        self.schema, self.schema_error = schema_version_of(self.fields)

    @property
    def is_v2(self) -> bool:
        return self.schema >= 2 or self.schema_error is not None


def remote_refs() -> list[str]:
    names = [
        r.strip()
        for r in git("for-each-ref", "--format=%(refname)", REMOTE_PREFIX.rstrip("/")).splitlines()
    ]
    return [r for r in names if r and not r.endswith("/HEAD")]


def local_refs() -> list[str]:
    names = [
        r.strip()
        for r in git("for-each-ref", "--format=%(refname)", "refs/heads").splitlines()
    ]
    return [r for r in names if r]


def tree_messages(ref: str) -> dict[str, str]:
    """Return path -> blob oid for every message file visible at ref."""
    out: dict[str, str] = {}
    for line in git("ls-tree", "-r", ref, "--", NAMESPACE).splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) != 3 or parts[1] != "blob":
            continue
        if MSG_RE.match(pathlib.Path(path).name):
            out[path] = parts[2]
    return out


def scan_authoritative() -> tuple[list[str], dict[str, dict[str, list[str]]]]:
    """Scan refs/remotes/origin/** only.

    Returns (refs, per_path) where per_path maps message path -> {oid: [refs]}.
    """
    refs = remote_refs()
    per_path: dict[str, dict[str, list[str]]] = {}
    for ref in refs:
        for path, oid in tree_messages(ref).items():
            per_path.setdefault(path, {}).setdefault(oid, []).append(ref)
    return refs, per_path


def display_ref(path: str, refs_for_path: list[str], sender: str) -> str:
    canonical = f"{REMOTE_PREFIX}agent/{sender}"
    return canonical if canonical in refs_for_path else sorted(refs_for_path)[0]


def messages_in_worktree(root: pathlib.Path) -> list[tuple[str, str]]:
    base = root / NAMESPACE
    if not base.is_dir():
        return []
    return [
        (str(p.relative_to(root)), "worktree")
        for p in base.rglob("*.md")
        if MSG_RE.match(p.name)
    ]


# ---------------------------------------------------------------------------
# v2 validation
# ---------------------------------------------------------------------------

def validate_v2(
    msg: Message,
    authoritative_paths: set[str],
    canonical_paths_by_agent: dict[str, set[str]],
    remote_ref_names: set[str],
) -> list[str]:
    """Return a list of human-readable validation errors for a v2 message."""
    errors: list[str] = []
    if msg.schema_error:
        errors.append(msg.schema_error)

    for field in V2_REQUIRED_FIELDS:
        if field not in msg.fields:
            errors.append(f"missing required v2 field: {field}")
    if errors:
        return errors

    message_id = scalar_value(msg.fields["message_id"])
    if message_id != msg.path:
        errors.append(
            f"message_id {message_id!r} does not equal message path {msg.path!r}"
        )
    sender_field = scalar_value(msg.fields["from"])
    if sender_field != msg.sender:
        errors.append(
            f"from {sender_field!r} does not equal sender namespace {msg.sender!r}"
        )
    if msg.kind not in V2_KNOWN_KINDS:
        errors.append(f"unknown v2 message kind: {msg.fields.get('type', '')!r}")
    if parse_boolean(msg.fields["requires_ack"]) is None:
        errors.append(f"requires_ack is not a boolean: {msg.fields['requires_ack']!r}")
    if not scalar_value(msg.fields["created_utc"]):
        errors.append("created_utc is empty")

    lists: dict[str, list[str]] = {}
    for field in ("ack_for", "supersedes"):
        try:
            lists[field] = parse_json_list(msg.fields[field])
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{field} is not a single-line JSON array of strings: {exc}")
    for field, targets in lists.items():
        for target in targets:
            if not target.startswith(NAMESPACE):
                errors.append(f"{field} target is not a message path: {target!r}")
            elif target not in authoritative_paths:
                errors.append(
                    f"{field} target not found on any authoritative remote ref: {target!r}"
                )

    if msg.kind == "ack" and not lists.get("ack_for", []) and "ack_for" in lists:
        errors.append("v2 ack has an empty ack_for array")
    if msg.kind == "correction" and not lists.get("supersedes", []) and "supersedes" in lists:
        errors.append("v2 correction has an empty supersedes array")

    # Canonical presence: a v2 message is delivered only from the sender's
    # canonical branch refs/remotes/origin/agent/<from>.
    canonical = canonical_paths_by_agent.get(msg.sender, set())
    if msg.path not in canonical:
        errors.append(
            f"message not present on canonical {REMOTE_PREFIX}agent/{msg.sender}"
        )

    if msg.kind == "handoff":
        errors.extend(validate_v2_handoff(msg, remote_ref_names))
    return errors


def validate_v2_handoff(msg: Message, remote_ref_names: set[str]) -> list[str]:
    errors: list[str] = []
    for field in V2_HANDOFF_FIELDS:
        if field not in msg.fields:
            errors.append(f"handoff missing required field: {field}")
    if errors:
        return errors

    artifact_ref = scalar_value(msg.fields["artifact_ref"])
    commit = scalar_value(msg.fields["artifact_commit"])
    try:
        artifact_paths = parse_json_list(msg.fields["artifact_paths"])
    except (ValueError, json.JSONDecodeError) as exc:
        return errors + [
            f"artifact_paths is not a single-line JSON array of strings: {exc}"
        ]

    if not artifact_paths:
        errors.append(
            "handoff artifact_paths is empty; a v2 handoff must list at least "
            "one concrete artifact path or manifest"
        )
    if artifact_ref != f"agent/{msg.sender}":
        errors.append(
            f"artifact_ref {artifact_ref!r} is not the sender's canonical branch "
            f"agent/{msg.sender}; task branches cannot satisfy a v2 handoff"
        )
    if not HEX40_RE.match(commit):
        errors.append(f"artifact_commit is not a full 40-hex object name: {commit!r}")
        return errors
    full_ref = REMOTE_PREFIX + artifact_ref
    if full_ref not in remote_ref_names:
        errors.append(f"artifact_ref has no authoritative remote ref: {full_ref}")
        return errors
    if not commit_exists(commit):
        errors.append(f"artifact_commit does not exist: {commit}")
        return errors
    if not is_ancestor(commit, full_ref):
        errors.append(
            f"artifact_commit {commit} is not reachable from {full_ref}"
        )
    for path in artifact_paths:
        if not path_in_commit(commit, path):
            errors.append(f"artifact path missing from {commit}: {path}")
    return errors


# ---------------------------------------------------------------------------
# Acknowledgement pairing
# ---------------------------------------------------------------------------

def acknowledged_by_later_ack(
    task: str, message_stamp: str, latest_ack_stamp_by_task: dict[str, str]
) -> bool:
    """Legacy fallback: a strictly later same-task ACK covers a legacy message."""
    return latest_ack_stamp_by_task.get(task, "") > message_stamp


def collect_my_acks(
    my_messages: Iterable[Message],
    authoritative_paths: set[str],
    canonical_paths_by_agent: dict[str, set[str]],
    remote_ref_names: set[str],
) -> tuple[set[str], dict[str, str], list[str]]:
    """Return (exact acked paths, legacy latest-ack-stamp-by-task, warnings).

    Only authoritative remote messages participate: an unpushed or local-branch
    ACK never acknowledges anything.
    """
    acked_paths: set[str] = set()
    legacy_latest: dict[str, str] = {}
    warnings: list[str] = []
    for msg in my_messages:
        if msg.kind != "ack":
            continue
        if msg.is_v2:
            errors = validate_v2(
                msg, authoritative_paths, canonical_paths_by_agent, remote_ref_names
            )
            if errors:
                warnings.append(
                    f"my v2 ack {msg.path} is invalid and acknowledges nothing: "
                    + "; ".join(errors)
                )
                continue
            acked_paths.update(parse_json_list(msg.fields["ack_for"]))
        else:
            if msg.stamp:
                legacy_latest[msg.task] = max(legacy_latest.get(msg.task, ""), msg.stamp)
    return acked_paths, legacy_latest, warnings


def is_acknowledged(
    msg: Message, acked_paths: set[str], legacy_latest: dict[str, str]
) -> bool:
    if msg.path in acked_paths:
        return True
    if msg.is_v2:
        # A legacy task/time ACK must never acknowledge a v2 message.
        return False
    return acknowledged_by_later_ack(msg.task, msg.stamp, legacy_latest)


# ---------------------------------------------------------------------------
# Seen state (exact-path membership; replaces the timestamp watermark)
# ---------------------------------------------------------------------------

def seen_state_file(root: pathlib.Path, me: str) -> pathlib.Path:
    return root / me / "inbox-seen.json"


def legacy_watermark(root: pathlib.Path, me: str) -> str:
    watermark_file = root / me / "inbox-watermark.txt"
    if watermark_file.exists():
        return watermark_file.read_text(encoding="utf-8").strip()
    return ""


def load_seen_state(
    root: pathlib.Path, me: str, addressed_msgs: Iterable[Message]
) -> tuple[set[str], str, str]:
    """Return (seen paths, migrated watermark, source description).

    If `<me>/inbox-seen.json` exists it is the only source of truth: newness is
    exact-path membership. If it does not exist, the legacy watermark (if any) is
    read as a one-time migration hint: addressed messages currently existing at or
    before the watermark are treated as seen. The legacy file is never rewritten.

    Raises ValueError on a malformed seen-state file — wrong or missing
    `schema_version` (exactly 1 is supported), a `migrated_watermark` that is not
    a string or null, or bad `seen_message_paths` (loud, exit 2 upstream).
    """
    state_file = seen_state_file(root, me)
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("seen-state is not a JSON object")
            version = data.get("schema_version")
            if isinstance(version, bool) or version != SEEN_STATE_SCHEMA_VERSION:
                raise ValueError(
                    f"schema_version {version!r} is not the supported version "
                    f"{SEEN_STATE_SCHEMA_VERSION}"
                )
            migrated = data.get("migrated_watermark")
            if migrated is not None and not isinstance(migrated, str):
                raise ValueError(
                    f"migrated_watermark is not a string or null: {migrated!r}"
                )
            paths = data["seen_message_paths"]
            if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
                raise ValueError("seen_message_paths is not a list of strings")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"malformed seen-state file {state_file}: {exc}") from exc
        return set(paths), migrated or "", f"{me}/inbox-seen.json"
    watermark = legacy_watermark(root, me)
    if watermark:
        migrated_seen = {
            msg.path for msg in addressed_msgs if msg.stamp and msg.stamp <= watermark
        }
        return (
            migrated_seen,
            watermark,
            f"{me}/inbox-seen.json missing; migrating legacy watermark {watermark}",
        )
    return set(), "", f"{me}/inbox-seen.json missing; no legacy watermark"


def write_seen_state(
    root: pathlib.Path, me: str, seen_paths: set[str], migrated_watermark: str
) -> pathlib.Path:
    """Deterministic (sorted, stable indentation) atomic write via temp sibling."""
    state_file = seen_state_file(root, me)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SEEN_STATE_SCHEMA_VERSION,
        "migrated_watermark": migrated_watermark or None,
        "seen_message_paths": sorted(seen_paths),
    }
    text = json.dumps(payload, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=state_file.parent, prefix=state_file.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, state_file)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return state_file


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--me", required=True, help="my agent id, e.g. claude_1")
    ap.add_argument(
        "--mark",
        action="store_true",
        help="record the selected addressed authoritative paths as seen",
    )
    ap.add_argument("--fetch", action="store_true", help="checked git fetch origin first")
    ap.add_argument(
        "--include-local",
        action="store_true",
        help="also show local-branch/worktree messages as non-authoritative diagnostics",
    )
    ap.add_argument(
        "--task",
        action="append",
        default=[],
        metavar="TASK_ID",
        help="exact task id filter; repeatable (affects display and --mark only)",
    )
    ap.add_argument(
        "--sender",
        action="append",
        default=[],
        metavar="AGENT_ID",
        help="exact sender agent id filter; repeatable (affects display and --mark only)",
    )
    args = ap.parse_args()

    try:
        root = pathlib.Path(git("rev-parse", "--show-toplevel").strip())
    except GitError as exc:
        print(f"not inside a git repository: {exc}", file=sys.stderr)
        return 2

    if args.fetch:
        fetch = run_git("fetch", "origin")
        if fetch.returncode != 0:
            print("git fetch origin failed:", file=sys.stderr)
            print(fetch.stderr.rstrip(), file=sys.stderr)
            print("inbox: STALE / NOT AUTHORITATIVE")
            return 2

    try:
        refs, per_path = scan_authoritative()
    except GitError as exc:
        print(f"git error while scanning remote refs: {exc}", file=sys.stderr)
        print("inbox: STALE / NOT AUTHORITATIVE")
        return 2
    remote_ref_names = set(refs)

    # Immutable-path collision detection (rule 3).
    collisions: list[tuple[str, dict[str, list[str]]]] = []
    for path in sorted(per_path):
        if len(per_path[path]) > 1:
            collisions.append((path, per_path[path]))
    collided = {path for path, _ in collisions}

    # Materialize authoritative messages (one body per unique path).
    messages: dict[str, Message] = {}
    for path in sorted(per_path):
        if path in collided:
            continue
        (oid, refs_for_path), = per_path[path].items()
        body = git("cat-file", "blob", oid)
        messages[path] = Message(
            path, display_ref(path, refs_for_path, sender_of(path)), body
        )

    authoritative_paths = set(messages) | collided
    # Canonical presence is derived from the single authoritative scan above —
    # no second per-ref tree lookup.
    canonical_paths_by_agent: dict[str, set[str]] = {}
    agent_ref_prefix = REMOTE_PREFIX + "agent/"
    for path, oids in per_path.items():
        for refs_for_oid in oids.values():
            for ref in refs_for_oid:
                if ref.startswith(agent_ref_prefix):
                    agent = ref[len(agent_ref_prefix):]
                    if "/" not in agent:
                        canonical_paths_by_agent.setdefault(agent, set()).add(path)

    my_msgs = [m for m in messages.values() if m.sender == args.me]
    acked_paths, legacy_latest, ack_warnings = collect_my_acks(
        my_msgs, authoritative_paths, canonical_paths_by_agent, remote_ref_names
    )

    # Addressed messages: validation runs on every addressed message; --task and
    # --sender affect display and --mark only (rule 6).
    addressed = [
        m
        for m in messages.values()
        if m.sender != args.me and addressed_to_me(m.body, args.me)
    ]
    delivery_errors: list[tuple[str, str]] = []
    for msg in addressed:
        if msg.is_v2:
            for error in validate_v2(
                msg, authoritative_paths, canonical_paths_by_agent, remote_ref_names
            ):
                delivery_errors.append((msg.path, error))

    try:
        seen_paths, migrated_watermark, seen_source = load_seen_state(
            root, args.me, addressed
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    def selected(msg: Message) -> bool:
        if args.task and msg.task not in args.task:
            return False
        if args.sender and msg.sender not in args.sender:
            return False
        return True

    selection = sorted((m for m in addressed if selected(m)), key=lambda m: m.path)
    new_items = [m for m in selection if m.path not in seen_paths]
    unacked = [
        m
        for m in selection
        if requires_ack(m.body, m.kind)
        and not is_acknowledged(m, acked_paths, legacy_latest)
    ]

    v2_count = sum(1 for m in messages.values() if m.is_v2)
    print(f"agent: {args.me}")
    print(
        f"authority: {REMOTE_PREFIX}** ({len(refs)} remote refs); "
        f"scanned {len(authoritative_paths)} authoritative messages "
        f"({len(messages) - v2_count} legacy, {v2_count} v2)"
    )
    print(f"seen-state: {seen_source}")
    if args.task or args.sender:
        print(
            "filters: "
            + " ".join(
                [f"task={t}" for t in args.task] + [f"sender={s}" for s in args.sender]
            )
        )

    print(f"\nimmutable-path collisions ({len(collisions)}):")
    for path, oids in collisions:
        print(f"  {path}")
        for oid, oid_refs in sorted(oids.items()):
            print(f"    {oid} on {', '.join(sorted(oid_refs))}")

    print(f"\ndelivery errors ({len(delivery_errors)}):")
    for path, error in delivery_errors:
        print(f"  {path}: {error}")

    for warning in ack_warnings:
        print(f"\nwarning: {warning}")

    print(f"\nnew (unseen) ({len(new_items)}):")
    for msg in new_items:
        print(f"  {msg.path}   [{msg.ref}]")

    print(f"\nunacknowledged, ack required ({len(unacked)}):")
    for msg in unacked:
        print(f"  {msg.path}   [{msg.ref}]")

    if args.include_local:
        diagnostics: list[tuple[str, str]] = []
        for ref in local_refs():
            for path in tree_messages(ref):
                if path not in authoritative_paths:
                    diagnostics.append((path, ref))
        for path, src in messages_in_worktree(root):
            if path not in authoritative_paths:
                diagnostics.append((path, src))
        unique = sorted(set(diagnostics))
        print(
            f"\nlocal diagnostics — unpublished, NOT authoritative ({len(unique)}):"
        )
        for path, src in unique:
            print(f"  {path}   [{src}]")

    transport_broken = bool(collisions or delivery_errors)

    if args.mark:
        if transport_broken:
            print("\nmark skipped: transport/delivery errors present (exit 2)")
        else:
            marked = {m.path for m in selection}
            state_file = write_seen_state(
                root, args.me, seen_paths | marked, migrated_watermark
            )
            print(
                f"\nmarked {len(marked)} selected addressed paths seen in "
                f"{state_file.relative_to(root)}"
            )

    if transport_broken:
        return 2
    return 1 if unacked else 0


if __name__ == "__main__":
    sys.exit(main())
