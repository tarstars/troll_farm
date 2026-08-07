#!/usr/bin/env python3
"""Single-use, idempotent migration: pin record citations to the commit that authored them.

Touches only `source` sub-objects and `schema_version`. Never alters claims or prose.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.evidence_git import GitLookupError, read_blob

START = "<!-- DECISION-EVIDENCE-JSON"
END = "END-DECISION-EVIDENCE-JSON -->"

def last_commit_touching(repo: Path, rel: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), "log", "--format=%H", "-1", "--", rel],
        capture_output=True, text=True,
    )
    sha = r.stdout.strip()
    if not sha:
        raise SystemExit(f"no commit found for {rel}")
    return sha

def iter_sources(payload: dict):
    for claim in payload.get("decisive_claims", []):
        yield claim.get("source")
    for ev in payload.get("textual_evidence", []):
        yield ev.get("source")
    cp = payload.get("constraint_projection")
    if isinstance(cp, dict):
        yield cp.get("source")
    pf = payload.get("premise_failure")
    if isinstance(pf, dict):
        yield pf.get("source")

def excerpt_at(repo: Path, commit: str, source: dict) -> str | None:
    locator = source.get("locator")
    if not locator or not locator.startswith("lines "):
        return None
    a, b = (int(x) for x in locator.removeprefix("lines ").split("-"))
    try:
        lines = read_blob(repo, commit, source["path"]).splitlines()
    except GitLookupError:
        return None
    if b > len(lines):
        return None
    return "\n".join(lines[a - 1:b]).strip()

def migrate_record_text(repo: Path, text: str, commit: str) -> str:
    head, rest = text.split(START, 1)
    body, tail = rest.split(END, 1)
    payload = json.loads(body.strip())
    dirty = False
    if payload.get("schema_version") != 2:
        payload["schema_version"] = 2
        dirty = True
    for source in iter_sources(payload):
        if not isinstance(source, dict):
            continue
        if not source.get("commit"):
            source["commit"] = commit
            dirty = True
        if not source.get("quote"):
            quote = excerpt_at(repo, source["commit"], source)
            if quote:
                source["quote"] = quote
                dirty = True
    if not dirty:
        return text
    return (
        head + START + "\n"
        + json.dumps(payload, indent=2, sort_keys=True) + "\n"
        + END + tail
    )

def migrate_repo(repo: Path) -> int:
    changed = 0
    for path in sorted((repo / "docs/evidence/records").glob("*.md")):
        rel = path.relative_to(repo).as_posix()
        commit = last_commit_touching(repo, rel)
        original = path.read_text(encoding="utf-8")
        updated = migrate_record_text(repo, original, commit)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=ROOT)
    args = p.parse_args()
    print(json.dumps({"migrated": migrate_repo(args.repo_root)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
