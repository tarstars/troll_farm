#!/usr/bin/env python3
"""Derive a referee's implemented-verb manifest from its own dispatcher.

`chatgpt_1`'s I-30 revision 3 review, trust-root blocker 1:

    `ExecutionValidity` validates a harness's self-declaration; it does not
    bind the run to a reviewed referee artifact, derive the verb manifest from
    that dispatcher, or derive executed counts from per-command events. A
    self-consistent silent discard can still pass.

The manifest was a caller-supplied list whose `verb_manifest_sha256` was
computed *from that same list*, so it was self-consistent by construction and
could not disagree with itself. This derives it instead, by reading
`FuzzReferee.VERB_HANDLERS` out of the referee blob **at a pinned commit**, and
writes `reviewed_referees.json`.

The dispatcher is parsed with `ast`, never imported. Importing a referee to ask
what it implements would execute the artifact under review, and a referee that
lied about its own handlers is precisely the thing being guarded against.

    python3 derive_referee_manifest.py --commit <sha> --path <repo/rel/path> \
        --name "c5 two-player phase-merged referee" --reviewed-by <message-path>
    python3 derive_referee_manifest.py --check     # registry matches the blobs
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, "reviewed_referees.json")
DISPATCHER_CLASS = "FuzzReferee"
DISPATCHER_ATTR = "VERB_HANDLERS"


def repo_root():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                         capture_output=True, text=True)
    return out.stdout.strip()


def blob_at(commit: str, path: str) -> bytes:
    proc = subprocess.run(["git", "show", "%s:%s" % (commit, path)],
                          cwd=repo_root(), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit("cannot read %s:%s — %s"
                         % (commit, path, proc.stderr.decode("utf-8", "replace").strip()))
    return proc.stdout


def verbs_from_dispatcher(source: bytes) -> list[str]:
    """Every key of `FuzzReferee.VERB_HANDLERS`, read statically.

    A verb absent from that table is an `unsupported_verb` error in the
    referee, never a silent skip — so the table's keys *are* the set of verbs
    the referee implements. That is the property being mirrored here.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == DISPATCHER_CLASS):
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if DISPATCHER_ATTR not in names:
                continue
            if not isinstance(stmt.value, ast.Dict):
                raise SystemExit("%s.%s is not a dict literal; it cannot be "
                                 "read without executing the referee"
                                 % (DISPATCHER_CLASS, DISPATCHER_ATTR))
            verbs = []
            for key in stmt.value.keys:
                if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                    raise SystemExit("%s.%s has a non-literal key; the manifest "
                                     "would be incomplete"
                                     % (DISPATCHER_CLASS, DISPATCHER_ATTR))
                verbs.append(key.value.upper())
            return sorted(set(verbs))
    raise SystemExit("no %s.%s found in this blob — it is not a referee this "
                     "tool can derive a manifest from"
                     % (DISPATCHER_CLASS, DISPATCHER_ATTR))


def load_registry() -> dict:
    if not os.path.exists(REGISTRY):
        return {"schema": "reviewed-referees/1", "referees": {}}
    with open(REGISTRY, encoding="utf-8") as fh:
        return json.load(fh)


def check(registry: dict) -> int:
    """Every entry must still derive from its own pinned blob."""
    problems = []
    for digest, entry in sorted(registry.get("referees", {}).items()):
        try:
            source = blob_at(entry["commit"], entry["path"])
        except SystemExit as exc:
            problems.append("%s: %s" % (digest[:12], exc))
            continue
        actual = hashlib.sha256(source).hexdigest()
        if actual != digest:
            problems.append("%s: %s:%s now hashes to %s"
                            % (digest[:12], entry["commit"][:12], entry["path"],
                               actual[:12]))
            continue
        derived = verbs_from_dispatcher(source)
        if derived != entry["verb_manifest"]:
            problems.append("%s: dispatcher yields %s, registry records %s"
                            % (digest[:12], derived, entry["verb_manifest"]))
    if problems:
        sys.stderr.write("reviewed-referee registry drift:\n  %s\n"
                         % "\n  ".join(problems))
        return 2
    print("reviewed-referee registry: %d entr%s, each derived from its pinned blob"
          % (len(registry.get("referees", {})),
             "y" if len(registry.get("referees", {})) == 1 else "ies"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit")
    ap.add_argument("--path")
    ap.add_argument("--name")
    ap.add_argument("--reviewed-by", dest="reviewed_by")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    registry = load_registry()
    if args.check:
        return check(registry)
    if not (args.commit and args.path and args.name and args.reviewed_by):
        ap.error("--commit, --path, --name and --reviewed-by are required")

    source = blob_at(args.commit, args.path)
    digest = hashlib.sha256(source).hexdigest()
    registry["referees"][digest] = {
        "name": args.name,
        "commit": args.commit,
        "path": args.path,
        "reviewed_by": args.reviewed_by,
        "verb_manifest": verbs_from_dispatcher(source),
        "derived_from": "%s.%s" % (DISPATCHER_CLASS, DISPATCHER_ATTR),
    }
    with open(REGISTRY, "w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("registered %s… (%s): %s"
          % (digest[:16], args.name, registry["referees"][digest]["verb_manifest"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
