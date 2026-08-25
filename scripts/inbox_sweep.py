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
7. `coordination/quarantine.json` records coordinator adjudications of immutable
   messages that are permanently invalid (schema violations, fabricated verdicts)
   and that their sender will not repair. A valid quarantine entry names an exact
   message path, a reason, and an `adjudicated_by` message that exists on the
   authoritative remote refs. Quarantined messages are excluded from delivery
   validation, newness, and acknowledgement (a quarantined ACK acknowledges
   nothing) and are listed in their own `quarantined` section instead. The file
   itself is validated strictly: a malformed file or an entry whose path or
   adjudication is unknown is a transport error (exit 2) and suppresses nothing.
   Immutable-path collisions are never suppressed by quarantine. Only the
   coordinator/integrator may modify the quarantine file, and every entry must
   cite a published adjudication message.

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
import dataclasses
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import traceback
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
QUARANTINE_FILE = "coordination/quarantine.json"
QUARANTINE_SCHEMA_VERSION = 2
QUARANTINE_ENTRY_FIELDS = ("path", "reason", "adjudicated_by", "target_blob")
LEGACY_BASELINE_FILE = "coordination/legacy-baseline.json"
LEGACY_BASELINE_SCHEMA_VERSION = 1
# Who the coordinator is must itself be authoritative. Reading it from the
# environment made the authority untrusted input: whoever set the variable
# designated the quarantine authority, and pointing it at a branch with no
# quarantine silently suppressed nothing while reporting zero errors. The
# roster is committed and lives ONLY on the integrated branch, which is the
# shared root of trust — anyone who can write it can already do anything.
ROSTER_FILE = "coordination/roster.json"
ROSTER_REF = REMOTE_PREFIX + "main"
ROSTER_SCHEMA_VERSION = 2


def roster_authorities() -> tuple[str, set[str]] | None:
    """Return current and former coordinators from the authoritative roster.

    None means no roster is reachable, in which case quarantine is disabled —
    fail-safe, because suppressing nothing is always recoverable while
    suppressing wrongly is not.
    """
    found = read_authoritative_blob(ROSTER_REF, ROSTER_FILE)
    if found is None:
        return None
    _, text = found
    where = f"{ROSTER_REF}:{ROSTER_FILE}"
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("roster is not a JSON object")
        version = data.get("schema_version")
        if isinstance(version, bool) or version not in (1, ROSTER_SCHEMA_VERSION):
            raise ValueError(
                f"schema_version {version!r} is not supported (expected 1 or "
                f"{ROSTER_SCHEMA_VERSION})"
            )
        coordinator = data["coordinator"]
        if not isinstance(coordinator, str) or not coordinator.strip():
            raise ValueError("coordinator is not a non-empty string")
        former_raw = data.get("former_coordinators", []) if version == 2 else []
        if (not isinstance(former_raw, list)
                or any(not isinstance(x, str) or not x.strip() for x in former_raw)):
            raise ValueError("former_coordinators is not an array of non-empty strings")
        former = set(former_raw)
        if coordinator in former:
            raise ValueError("current coordinator also appears in former_coordinators")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"malformed roster {where}: {exc}") from exc
    return coordinator, former


def coordinator_agent() -> str | None:
    """Compatibility accessor for callers that need only the current identity."""
    authorities = roster_authorities()
    return authorities[0] if authorities else None


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


def ack_obliged_to_me(body: str, me: str) -> bool:
    """Ack OBLIGATION falls on `to` recipients only (ruling 2026-08-20).

    `cc` is informational: a cc'd agent may ack as courtesy but never OWES
    one — and for CARD:/DEFERRED: messages a cc bystander's ack is actively
    forbidden (it could discharge another agent's queue anchor). Before this
    rule the unacknowledged section demanded acks from every cc recipient,
    which made a policy-clean empty inbox impossible for bystanders
    (codex_1's 20260820T095149Z blocker, item 2).
    """
    yaml = yaml_front_matter(body)
    if "to" in yaml:
        values = [yaml["to"]]
    elif "cc" in yaml:
        values = []
    else:
        values = legacy_values(body, "To")
    targets = set().union(set(), *(recipient_tokens(v) for v in values))
    return bool({me.lower(), "both", "all"} & targets)


def wakes_recipient(msg: "Message", me: str) -> bool:
    """Does this message ring `me`'s doorbell? (protocol §5.1, owner 2026-08-21)

    The actionable set answers "what do I owe"; this answers "is there news".
    Three exclusions, each a measured failure of 2026-08-21, the day claude_1
    woke eight times in 102 minutes with every wake legally mail-triggered:

    1. `msg.sender == me` — an agent has read what it wrote. Its own DEFERRED
       card stays an OBLIGATION in the queue and never rings its own bell.
       Without this the discharge of a card is another card, that card enters
       its author's own set, and a blocked agent wakes itself forever.
    2. not addressed in `to` — a `cc` recipient owes no ack (ruling 2026-08-20),
       so waking it to read what it does not owe contradicts the same ruling.
       It reads the cc on its next real wake.
    3. a courtesy receipt — an `ack` carrying no acknowledgement obligation of
       its own. A verdict, ruling or authorization CHANGES the recipient's
       queue and must be published `requires_ack: true` toward that party (the
       2026-08-18 queue-changing rule); published that way it wakes. Published
       as a bare receipt it is read next wake, and peer receipt ping-pong
       terminates instead of sustaining itself.
    4. a shape-valid `DEFERRED:` card — wakes NOBODY, not even the peers it
       names in `to`. Both live agents address their own cards to each other,
       and a peer cannot discharge another agent's card: only a later message
       of the SAME agent naming it in `ack_for` does. The obligation such a
       card appears to place on a peer is therefore one the peer cannot act
       on, and waking anyone for it is noise by construction. The card stays
       visible to everyone as status — "a deferral is a status, not a
       silence" is about publishing it, never about interrupting a peer.
       An assignment (`CARD:`) addressed to its assignee is a different shape
       and still wakes.
    """
    if msg.sender == me:
        return False
    if not ack_obliged_to_me(msg.body, me):
        return False
    if msg.kind == "ack" and not requires_ack(msg.body, msg.kind):
        return False
    if is_deferral_card(msg):
        return False
    return True


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


DEFERRED_LINE_RE = re.compile(r"^DEFERRED:", re.MULTILINE)


def is_deferral_card(msg: "Message") -> bool:
    """True for the one self-mail shape that is a queue item, not an announcement.

    The deferral rule (owner-adopted 2026-08-18) requires a postponed job to be
    published as `requires_ack: true` and addressed to its own sender, so the
    deferring agent's next sweep surfaces it. `lint_outbox.deferral_shape_errors`
    enforces exactly this shape on the sending side; this is the same predicate
    read back, and the two must not drift.

    It exists because the rule was prose until 2026-08-21: `actionable_set()`
    dropped every self-authored message before addressing could matter, so a
    deferral card sat authoritative, unacked and self-addressed on origin and was
    still absent from its owner's actionable set (claude_1's blocker
    20260821T053322Z, reproduced by codex_1). Ordinary self-mail stays inert —
    only this shape opens the route.
    """
    if not DEFERRED_LINE_RE.search(msg.body):
        return False
    if parse_boolean(msg.fields.get("requires_ack", "")) is not True:
        return False
    return msg.sender.lower() in recipient_tokens(msg.fields.get("to", ""))


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
    require_canonical: bool = True,
) -> list[str]:
    """Return a list of human-readable validation errors for a v2 message.

    `require_canonical=False` skips the canonical-branch presence check for a
    message that is not published yet (`scripts/lint_outbox.py`); every other
    rule is identical, so the sender sees exactly what the receiver will.
    """
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
    # NOTE (2026-08-12): `ack_for` on a non-`ack` kind is deliberately NOT an
    # error.  It used to be inert -- collect_my_acks skipped every kind but
    # `ack`, so a handoff or policy naming ack_for acknowledged nothing while
    # looking to its author exactly like an acknowledgement.  Rejecting it was
    # tried and reverted: 33 already-published immutable messages carry the
    # pattern, mostly `handoff`s that ack the request they answer, and an
    # invalid published message can never be cleared.  The fix went the other
    # way -- collect_my_acks now honours ack_for on every kind -- so the
    # declaration means what its authors always intended.

    # Canonical presence: a v2 message is delivered only from the sender's
    # canonical branch refs/remotes/origin/agent/<from>.
    if require_canonical:
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
        # Any kind may discharge an acknowledgement by naming exact paths in
        # `ack_for`, not only kind `ack`.  Restricting it to `ack` made the
        # declaration silently inert everywhere else: a `handoff` that acks the
        # request it answers, or a `policy` that acks the question it rules on,
        # left its targets ack-required forever while the author believed they
        # were discharged, and the lint could not see it either.  33 published
        # messages already use the pattern.  `ack` still MUST carry a non-empty
        # ack_for (validate_v2); the difference is only that others MAY.
        # Guarded, because parse_json_list RAISES on malformed input and this
        # walks my OWN namespace: an unguarded call let one bad `ack_for` of
        # mine crash my own sweep, and published messages are immutable, so I
        # could not repair it (claude_1 execution review, 2026-08-13).  A
        # malformed declaration must acknowledge nothing and say so, exactly as
        # validate_v2 already treats the same field.
        if msg.kind != "ack":
            try:
                declared = parse_json_list(msg.fields.get("ack_for", "[]"))
            except (ValueError, json.JSONDecodeError) as exc:
                warnings.append(
                    f"my v2 {msg.kind} {msg.path} has a malformed ack_for and "
                    f"acknowledges nothing: {exc}"
                )
                continue
            if not declared:
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
# Quarantine (rule 7: coordinator-adjudicated permanently-invalid messages)
# ---------------------------------------------------------------------------

def read_authoritative_blob(ref: str, path: str) -> tuple[str, str] | None:
    """Return (blob_oid, text) for `path` at `ref`, or None if absent."""
    probe = run_git("rev-parse", f"{ref}:{path}")
    if probe.returncode != 0:
        return None
    oid = probe.stdout.strip()
    return oid, git("cat-file", "blob", oid)


def tool_drift() -> str | None:
    """Report if the running sweep differs from the authoritative copy.

    A sweep that is itself stale reports confidently wrong inbox state, and it
    is the one error the sweep cannot otherwise surface: every other check it
    performs is only as current as the code performing it.  This bit twice in
    one cycle -- `claude_1` synced `scripts/` from `main`, published the digest,
    and was stale again within the day because `main` moved under it; the prior
    occurrence nearly reported 56 unacknowledged messages against a true 16, and
    the second silently dropped an acknowledgement it had genuinely made.

    Suggested by `claude_1` (2026-08-13) and it costs one blob read, since
    `origin/main` is already consulted for the roster.

    Returns None when the tool matches, or when the comparison cannot be made --
    absent ref, unreadable blob, running from stdin.  Never fatal: a tool that
    refused to run because it could not verify itself would be worse than one
    that runs and says so.
    """
    try:
        mine = pathlib.Path(__file__).read_bytes()
    except (OSError, NameError):
        return None
    found = read_authoritative_blob(ROSTER_REF, "scripts/inbox_sweep.py")
    if found is None:
        return None
    _, authoritative = found
    mine_digest = hashlib.sha256(mine).hexdigest()
    theirs_digest = hashlib.sha256(authoritative.encode()).hexdigest()
    if mine_digest == theirs_digest:
        return None
    return (
        f"running {mine_digest[:8]}…, {ROSTER_REF} has {theirs_digest[:8]}… — "
        "THIS SWEEP MAY BE WRONG. Sync scripts/ before trusting anything below."
    )


def load_quarantine() -> tuple[list[dict[str, str]], str]:
    """Load the quarantine blob from origin/main (rule 7).

    Returns (entries, blob_oid). The worktree copy is never authoritative; the
    caller compares it for drift and reports, but never uses it. Reading shared
    inbox truth from a mutable local file was finding TQ-1.
    """
    found = read_authoritative_blob(ROSTER_REF, QUARANTINE_FILE)
    if found is None:
        return [], ""
    oid, text = found
    where = f"{ROSTER_REF}:{QUARANTINE_FILE}"
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("quarantine is not a JSON object")
        version = data.get("schema_version")
        if isinstance(version, bool) or version != QUARANTINE_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version {version!r} is not the supported version "
                f"{QUARANTINE_SCHEMA_VERSION}"
            )
        entries = data["entries"]
        if not isinstance(entries, list):
            raise ValueError("entries is not a list")
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f"entry {i} is not an object")
            for field in QUARANTINE_ENTRY_FIELDS:
                value = entry.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"entry {i} field {field!r} is not a non-empty string"
                    )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"malformed quarantine file {where}: {exc}") from exc
    return entries, oid


def load_legacy_baseline() -> tuple[dict[str, str], bool]:
    """Frozen path→blob map of messages grandfathered as pre-v2 (rule 5).

    Returns (mapping, present). When absent, legacy messages are accepted as
    before so an un-migrated repository still works; the sweep says so loudly.

    `frozen_at` is required: without it the baseline is a v2-enforcement waiver
    list that anyone able to write it can extend, letting an arbitrary new
    message escape validation (finding F5). With it the list is verifiable —
    `verify_legacy_baseline` rejects any path that did not exist at that commit.
    """
    found = read_authoritative_blob(ROSTER_REF, LEGACY_BASELINE_FILE)
    if found is None:
        return {}, False
    _, text = found
    where = f"{ROSTER_REF}:{LEGACY_BASELINE_FILE}"
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("baseline is not a JSON object")
        version = data.get("schema_version")
        if isinstance(version, bool) or version != LEGACY_BASELINE_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version {version!r} is not the supported version "
                f"{LEGACY_BASELINE_SCHEMA_VERSION}"
            )
        paths = data["paths"]
        if not isinstance(paths, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in paths.items()
        ):
            raise ValueError("paths is not an object of path→blob strings")
        frozen_at = data.get("frozen_at")
        if not isinstance(frozen_at, str) or not HEX40_RE.match(frozen_at):
            raise ValueError(
                "frozen_at is not a full 40-hex commit; without it the baseline "
                "is an unverifiable waiver list"
            )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"malformed legacy baseline {where}: {exc}") from exc
    return paths, True


def verify_legacy_baseline(baseline: dict[str, str]) -> list[str]:
    """Every pinned path must have existed, with those bytes, at the freeze.

    One `ls-tree` of the namespace at `frozen_at` rather than a lookup per path:
    the live baseline pins 691 paths.
    """
    found = read_authoritative_blob(ROSTER_REF, LEGACY_BASELINE_FILE)
    if found is None:
        return []
    frozen_at = json.loads(found[1]).get("frozen_at", "")
    if not commit_exists(frozen_at):
        return [f"frozen_at commit does not exist: {frozen_at}"]
    at_freeze: dict[str, str] = {}
    for line in git("ls-tree", "-r", frozen_at, "--", NAMESPACE).splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob":
            at_freeze[path] = parts[2]
    errors: list[str] = []
    for path, blob in sorted(baseline.items()):
        if path not in at_freeze:
            errors.append(
                f"baselined path did not exist at the freeze commit "
                f"{frozen_at[:12]}: {path}"
            )
        elif at_freeze[path] != blob:
            errors.append(
                f"baselined blob differs from the freeze commit for {path}: "
                f"pinned {blob[:12]}, frozen {at_freeze[path][:12]}"
            )
    return errors


def validate_quarantine(
    entries: list[dict[str, str]],
    authoritative_paths: set[str],
    messages: dict[str, "Message"],
    blob_by_path: dict[str, str],
    coordinator: str,
    former_coordinators: set[str] | None = None,
    canonical_paths_by_agent: dict[str, set[str]] | None = None,
    collided: set[str] | None = None,
) -> list[str]:
    """Return errors for entries that are not properly authorized.

    An adjudication must be a valid v2 message authored by the coordinator, on
    the coordinator's own canonical branch, that machine-names the exact target
    in its `quarantines` array. Existence of a path is never sufficient — that
    was finding TQ-2, under which any unrelated message (including one authored
    by the quarantined agent itself) authorized suppression.
    """
    errors: list[str] = []
    quarantined_paths = {entry["path"] for entry in entries}
    seen: set[str] = set()
    for entry in entries:
        path, adjudicator = entry["path"], entry["adjudicated_by"]
        if path in seen:
            errors.append(f"duplicate quarantine path: {path!r}")
        seen.add(path)
        for label, target in (("path", path), ("adjudicated_by", adjudicator)):
            if not target.startswith(NAMESPACE):
                errors.append(f"{label} is not a message path: {target!r}")
            elif target not in authoritative_paths:
                errors.append(
                    f"{label} not found on any authoritative remote ref: {target!r}"
                )
        if adjudicator in quarantined_paths:
            errors.append(f"adjudicated_by is itself quarantined: {adjudicator!r}")
        if collided and path in collided:
            # The pin was silently skipped exactly when bytes are ambiguous,
            # which is when it matters most (finding F8). A collided path can
            # never be quarantined: there is no single blob to pin.
            errors.append(
                f"path {path!r} collides across authoritative refs; a collided "
                "path has no single blob to pin and cannot be quarantined"
            )
        elif path in blob_by_path and entry["target_blob"] != blob_by_path[path]:
            errors.append(
                f"target_blob does not match the message at {path!r}: "
                f"{entry['target_blob']!r} != {blob_by_path[path]!r}"
            )
        # Quarantining an ACK withdraws it, which silently re-opens every
        # obligation it discharged for its sender (finding F4). That may be
        # correct — a fabricated ACK should be withdrawn — but it must be
        # declared, not discovered later by the agent whose work reappears.
        target = messages.get(path)
        if target is not None and target.kind == "ack":
            try:
                discharged = parse_json_list(target.fields.get("ack_for", "[]"))
            except (ValueError, json.JSONDecodeError):
                discharged = []
            declared = entry.get("reopens")
            declared = declared if isinstance(declared, list) else []
            undeclared = [p for p in discharged if p not in declared]
            if undeclared:
                errors.append(
                    f"quarantining the ACK {path!r} re-opens obligations it "
                    "discharged; list them in this entry's `reopens` field: "
                    + ", ".join(sorted(undeclared))
                )
        if adjudicator not in authoritative_paths:
            continue
        adjudicator_agent = sender_of(adjudicator)
        authorized = {coordinator} | (former_coordinators or set())
        if adjudicator_agent not in authorized:
            errors.append(
                f"adjudicated_by is not authored by the current or former "
                f"coordinators {sorted(authorized)!r}: "
                f"{adjudicator!r}"
            )
            continue
        # Protocol §10.2 requires the adjudication to be a valid v2 message ON
        # the coordinator's canonical ref. Being in the coordinator's namespace
        # somewhere is not that: a side branch would do, and code enforced only
        # the namespace (finding F7).
        canonical = (canonical_paths_by_agent or {}).get(adjudicator_agent, set())
        if adjudicator not in canonical:
            errors.append(
                f"adjudicated_by is not present on its author's canonical "
                f"ref {REMOTE_PREFIX}agent/{adjudicator_agent}: {adjudicator!r}"
            )
            continue
        msg = messages.get(adjudicator)
        if msg is None or not msg.is_v2:
            errors.append(f"adjudicated_by is not a valid v2 message: {adjudicator!r}")
            continue
        try:
            named = parse_json_list(msg.fields.get("quarantines", "[]"))
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(
                f"adjudicated_by has an unparseable quarantines array: {exc}"
            )
            continue
        if path not in named:
            errors.append(
                f"adjudicated_by {adjudicator!r} does not name {path!r} in its "
                "quarantines array"
            )
    return errors


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

class SweepFailure(Exception):
    """A transport failure that stops the sweep before any inbox state exists.

    Carries the exact stderr text and whether the inbox must additionally be
    labeled stale on stdout, so that `main()` reproduces byte-for-byte the
    output it printed when this computation lived inline in `main()`
    (claude_1, 2026-08-21: behaviour-preserving extraction of
    `actionable_set()`).
    """

    def __init__(self, detail: str, *, stale: bool = False) -> None:
        super().__init__(detail)
        self.detail = detail
        self.stale = stale


@dataclasses.dataclass(frozen=True)
class SweepState:
    """Everything one authoritative sweep computed, before any printing.

    `new_items` and `unacked` together with `transport_broken` ARE the
    actionability predicate. Anything that needs to know whether an agent has
    work -- the sweep's own report, a wake-on-work sentinel -- must read them
    from here rather than re-compose the primitives, because a second
    implementation of the predicate that disagrees with the sweep is worse
    than none: it wakes agents for work the sweep does not show, or stays
    silent on work it does (coordinator ruling, 2026-08-21).
    """

    me: str
    root: pathlib.Path
    refs: list[str]
    authoritative_paths: set[str]
    messages: dict[str, Message]
    collisions: list[tuple[str, dict[str, list[str]]]]
    delivery_errors: list[tuple[str, str]]
    coordinator: str | None
    former_coordinators: set[str]
    coordinator_ref: str
    quarantine_blob: str
    quarantine_errors: list[str]
    quarantined: dict[str, dict[str, str]]
    quarantine_drift: str
    legacy_baseline: dict[str, str]
    baseline_present: bool
    ack_warnings: list[str]
    seen_paths: set[str]
    seen_source: str
    migrated_watermark: str
    selection: list[Message]
    new_items: list[Message]
    unacked: list[Message]
    wake_items: list[Message]

    @property
    def transport_broken(self) -> bool:
        return bool(self.collisions or self.delivery_errors or self.quarantine_errors)

    @property
    def actionable_paths(self) -> list[str]:
        """Selected message paths that are unread or owe an acknowledgement."""
        return sorted({m.path for m in self.new_items} | {m.path for m in self.unacked})

    @property
    def wake_paths(self) -> list[str]:
        """The subset of `actionable_paths` that may WAKE this agent (§5.1).

        Always a subset: nothing wakes an agent that the sweep would not also
        show it. What it drops is the agent's own mail, `cc`-only mail, and
        courtesy receipts — see `wakes_recipient`.
        """
        return sorted({m.path for m in self.wake_items})

    @property
    def is_actionable(self) -> bool:
        """True when this agent has something to do: mail, or a broken transport.

        A broken transport counts: exit 2 means no inbox state above it can be
        trusted, which is itself work.
        """
        return bool(self.actionable_paths) or self.transport_broken


def actionable_set(
    me: str,
    root: pathlib.Path,
    tasks: Iterable[str] = (),
    senders: Iterable[str] = (),
) -> SweepState:
    """Compute one authoritative sweep for `me` and return its full state.

    Pure computation over `refs/remotes/origin/**` plus `me`'s seen-state file:
    it fetches nothing, prints nothing and writes nothing. Raises
    `SweepFailure` where the sweep cannot know its own state at all.

    `tasks`/`senders` are the exact-match display filters; per transport rule 6
    they affect the selection (and therefore `--mark`), never validation.
    """
    tasks = list(tasks)
    senders = list(senders)

    try:
        refs, per_path = scan_authoritative()
    except GitError as exc:
        raise SweepFailure(
            f"git error while scanning remote refs: {exc}", stale=True
        ) from exc
    remote_ref_names = set(refs)

    # Immutable-path collision detection (rule 3).
    collisions: list[tuple[str, dict[str, list[str]]]] = []
    for path in sorted(per_path):
        if len(per_path[path]) > 1:
            collisions.append((path, per_path[path]))
    collided = {path for path, _ in collisions}
    authoritative_paths = set(per_path)

    # Materialize authoritative messages (one body per unique path). This runs
    # before quarantine because an adjudication is itself a message that must be
    # parsed and validated before it can authorize anything.
    messages: dict[str, Message] = {}
    blob_by_path: dict[str, str] = {}
    for path in sorted(per_path):
        if path in collided:
            continue
        (oid, refs_for_path), = per_path[path].items()
        blob_by_path[path] = oid
        body = git("cat-file", "blob", oid)
        messages[path] = Message(
            path, display_ref(path, refs_for_path, sender_of(path)), body
        )

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

    # Quarantine (rule 7). Authority is the coordinator's canonical ref, never
    # the worktree: a local file must not be able to change shared inbox truth.
    try:
        roster = roster_authorities()
    except ValueError as exc:
        raise SweepFailure(str(exc)) from exc
    if roster is None:
        coordinator, former_coordinators = None, set()
        coordinator_ref = ROSTER_REF
        quarantine_entries, quarantine_blob = [], ""
        legacy_baseline, baseline_present = {}, False
    else:
        coordinator, former_coordinators = roster
        coordinator_ref = ROSTER_REF
        try:
            quarantine_entries, quarantine_blob = load_quarantine()
            legacy_baseline, baseline_present = load_legacy_baseline()
        except ValueError as exc:
            raise SweepFailure(str(exc)) from exc
    quarantine_errors = validate_quarantine(
        quarantine_entries, authoritative_paths, messages, blob_by_path,
        coordinator, former_coordinators, canonical_paths_by_agent, collided
    )
    if baseline_present:
        quarantine_errors.extend(
            verify_legacy_baseline(legacy_baseline))
    # A broken or unauthorized quarantine suppresses nothing.
    quarantined: dict[str, dict[str, str]] = (
        {} if quarantine_errors else {e["path"]: e for e in quarantine_entries}
    )
    for path in quarantined:
        messages.pop(path, None)

    local_quarantine = root / QUARANTINE_FILE
    quarantine_drift = ""
    if local_quarantine.exists():
        local_oid = run_git("hash-object", str(local_quarantine))
        if local_oid.returncode == 0 and local_oid.stdout.strip() != quarantine_blob:
            quarantine_drift = (
                f"local quarantine differs from the authoritative blob "
                f"({local_oid.stdout.strip()[:12] or 'none'} vs "
                f"{quarantine_blob[:12] or 'none'}); the authoritative copy governs"
            )
    elif quarantine_blob:
        quarantine_drift = (
            "local quarantine differs from the authoritative blob (absent locally); "
            "the authoritative copy governs"
        )
    my_msgs = [m for m in messages.values() if m.sender == me]
    acked_paths, legacy_latest, ack_warnings = collect_my_acks(
        my_msgs, authoritative_paths, canonical_paths_by_agent, remote_ref_names
    )

    # Addressed messages: validation runs on every addressed message; --task and
    # --sender affect display and --mark only (rule 6).
    # Self-authored mail is inert with ONE exception: a shape-valid deferral
    # card, which the deferral rule defines as its own sender's queue item.
    addressed = [
        m
        for m in messages.values()
        if (m.sender != me or is_deferral_card(m)) and addressed_to_me(m.body, me)
    ]
    delivery_errors: list[tuple[str, str]] = []
    for msg in addressed:
        if msg.is_v2:
            for error in validate_v2(
                msg, authoritative_paths, canonical_paths_by_agent, remote_ref_names
            ):
                delivery_errors.append((msg.path, error))
        elif baseline_present:
            # Rule 5 grandfathers historical legacy messages, but only the exact
            # pinned ones: otherwise a sender bypasses v2 entirely by omitting
            # `schema_version`, and a backdated filename defeats a date cutoff
            # (finding TQ-3).
            pinned = legacy_baseline.get(msg.path)
            if pinned is None:
                delivery_errors.append((
                    msg.path,
                    "legacy message not in the frozen legacy baseline; messages "
                    "published after the v2 migration must declare schema_version: 2",
                ))
            elif pinned != blob_by_path.get(msg.path, ""):
                delivery_errors.append((
                    msg.path,
                    f"legacy baseline blob mismatch: pinned {pinned[:12]} but found "
                    f"{blob_by_path.get(msg.path, '')[:12]}",
                ))

    try:
        seen_paths, migrated_watermark, seen_source = load_seen_state(
            root, me, addressed
        )
    except ValueError as exc:
        raise SweepFailure(str(exc)) from exc

    def selected(msg: Message) -> bool:
        if tasks and msg.task not in tasks:
            return False
        if senders and msg.sender not in senders:
            return False
        return True

    selection = sorted((m for m in addressed if selected(m)), key=lambda m: m.path)
    # An agent has read what it wrote, so its own deferral card is never
    # "new". Its only actionable route is the outstanding obligation below —
    # otherwise one --mark would retire a job that is still undone.
    new_items = [
        m for m in selection if m.path not in seen_paths and m.sender != me
    ]
    unacked = [
        m
        for m in selection
        if requires_ack(m.body, m.kind)
        and ack_obliged_to_me(m.body, me)
        and not is_acknowledged(m, acked_paths, legacy_latest)
    ]
    # The doorbell (protocol §5.1). A strict subset of the actionable set:
    # what is NEWS from someone else, as opposed to what I merely owe.
    wake_seen: set[str] = set()
    wake_items: list[Message] = []
    for msg in [*new_items, *unacked]:
        if msg.path in wake_seen or not wakes_recipient(msg, me):
            continue
        wake_seen.add(msg.path)
        wake_items.append(msg)
    wake_items.sort(key=lambda m: m.path)

    return SweepState(
        me=me,
        root=root,
        refs=refs,
        authoritative_paths=authoritative_paths,
        messages=messages,
        collisions=collisions,
        delivery_errors=delivery_errors,
        coordinator=coordinator,
        former_coordinators=former_coordinators,
        coordinator_ref=coordinator_ref,
        quarantine_blob=quarantine_blob,
        quarantine_errors=quarantine_errors,
        quarantined=quarantined,
        quarantine_drift=quarantine_drift,
        legacy_baseline=legacy_baseline,
        baseline_present=baseline_present,
        ack_warnings=ack_warnings,
        seen_paths=seen_paths,
        seen_source=seen_source,
        migrated_watermark=migrated_watermark,
        selection=selection,
        new_items=new_items,
        unacked=unacked,
        wake_items=wake_items,
    )


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
        state = actionable_set(args.me, root, args.task, args.sender)
    except SweepFailure as failure:
        print(failure.detail, file=sys.stderr)
        if failure.stale:
            print("inbox: STALE / NOT AUTHORITATIVE")
        return 2

    messages = state.messages
    v2_count = sum(1 for m in messages.values() if m.is_v2)
    print(f"agent: {args.me}")
    print(
        f"authority: {REMOTE_PREFIX}** ({len(state.refs)} remote refs); "
        f"scanned {len(state.authoritative_paths)} authoritative messages "
        f"({len(messages) - v2_count} legacy, {v2_count} v2)"
    )
    print(f"seen-state: {state.seen_source}")
    drift = tool_drift()
    if drift:
        print(f"\n*** TOOL DRIFT: {drift}\n")
    if args.task or args.sender:
        print(
            "filters: "
            + " ".join(
                [f"task={t}" for t in args.task] + [f"sender={s}" for s in args.sender]
            )
        )

    print(f"\nimmutable-path collisions ({len(state.collisions)}):")
    for path, oids in state.collisions:
        print(f"  {path}")
        for oid, oid_refs in sorted(oids.items()):
            print(f"    {oid} on {', '.join(sorted(oid_refs))}")

    print(f"\ndelivery errors ({len(state.delivery_errors)}):")
    for path, error in state.delivery_errors:
        print(f"  {path}: {error}")

    if state.coordinator is None:
        print(
            f"\nquarantine authority: NONE — no authoritative roster at "
            f"{ROSTER_REF}:{ROSTER_FILE}; quarantine is DISABLED and nothing is "
            "suppressed"
        )
    else:
        print(
            f"\nquarantine authority: coordinator {state.coordinator!r} per "
            f"{ROSTER_REF}:{ROSTER_FILE}; {state.coordinator_ref}:{QUARANTINE_FILE} "
            f"blob {state.quarantine_blob[:12] or 'absent'}; legacy baseline "
            + (f"{len(state.legacy_baseline)} pinned paths" if state.baseline_present
               else "ABSENT — legacy messages are not pinned")
        )
    if state.quarantine_drift:
        print(f"warning: {state.quarantine_drift}")

    print(f"\nquarantine errors ({len(state.quarantine_errors)}):")
    for error in state.quarantine_errors:
        print(f"  {QUARANTINE_FILE}: {error}")

    print(f"\nquarantined ({len(state.quarantined)}):")
    for path in sorted(state.quarantined):
        entry = state.quarantined[path]
        print(f"  {path}: {entry['reason']}   [{entry['adjudicated_by']}]")
        adjudicator_agent = sender_of(entry["adjudicated_by"])
        if adjudicator_agent in state.former_coordinators:
            print(
                f"    adjudicated by former coordinator {adjudicator_agent} "
                "(honoured; new entries by former coordinators are refused at integration)"
            )

    for warning in state.ack_warnings:
        print(f"\nwarning: {warning}")

    print(f"\nnew (unseen) ({len(state.new_items)}):")
    for msg in state.new_items:
        print(f"  {msg.path}   [{msg.ref}]")

    print(f"\nunacknowledged, ack required ({len(state.unacked)}):")
    for msg in state.unacked:
        print(f"  {msg.path}   [{msg.ref}]")

    # The doorbell, protocol §5.1: the subset of everything above that may WAKE
    # this agent. Read by scripts/agent_launcher.py; the rest of this report is
    # the queue, which is a different question.
    print(f"\nwake set ({len(state.wake_items)}):")
    for msg in state.wake_items:
        print(f"  {msg.path}   [{msg.ref}]")

    if args.include_local:
        diagnostics: list[tuple[str, str]] = []
        for ref in local_refs():
            for path in tree_messages(ref):
                if path not in state.authoritative_paths:
                    diagnostics.append((path, ref))
        for path, src in messages_in_worktree(root):
            if path not in state.authoritative_paths:
                diagnostics.append((path, src))
        unique = sorted(set(diagnostics))
        print(
            f"\nlocal diagnostics — unpublished, NOT authoritative ({len(unique)}):"
        )
        for path, src in unique:
            print(f"  {path}   [{src}]")

    transport_broken = state.transport_broken

    if args.mark:
        if transport_broken:
            print("\nmark skipped: transport/delivery errors present (exit 2)")
        else:
            marked = {m.path for m in state.selection}
            state_file = write_seen_state(
                root, args.me, state.seen_paths | marked, state.migrated_watermark
            )
            print(
                f"\nmarked {len(marked)} selected addressed paths seen in "
                f"{state_file.relative_to(root)}"
            )

    if transport_broken:
        return 2
    return 1 if state.unacked else 0


def run_cli() -> int:
    """Run main(), mapping any unexpected failure to exit 2.

    Exit 1 is defined by this protocol as "healthy inbox, unacknowledged
    ack-required messages present", so an uncaught traceback -- which Python
    also exits 1 -- is indistinguishable from a normal result to anything
    gating on exit status, which this project mandates.  Any unexpected
    failure is exit 2, the same status every other hard error here uses
    (claude_1 execution review, 2026-08-13).

    Extracted from the `__main__` block so it can be tested: inline there it
    was unreachable by any test, which is how it shipped unexercised
    (codex_1 second review, RQ-3).
    """
    try:
        return main()
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else (0 if code is None else 1)
    except BaseException:
        traceback.print_exc()
        print(
            "\nsweep FAILED with an unexpected error (exit 2). This is not "
            "'you have mail' -- no inbox state above should be trusted.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(run_cli())
