#!/usr/bin/env python3
"""Loader and integrity check for the frozen oscillation situation library.

The library (`oscillation-library/`) is the deliverable of manifest item M3a:
the enumerated, frozen set of situations in which oscillation was observed.
Each situation is one JSON file of literal data -- map rows, plants, units of
both players, inventories, the observed command window -- copied verbatim out
of a referee transcript, so it survives a change to the map generator.

**Freeze means frozen.**  Every file carries `content_sha256`, the SHA-256 of
its own canonical payload with that field removed.  `index.json` repeats every
digest and carries `library_sha256` over the whole set.  `load_library`
recomputes all of them and **fails closed** -- it raises `IntegrityError` and
returns nothing rather than handing back data that has drifted.  A library
that silently drifts is worse than no library.

**Scope.**  This module reads and verifies.  It records, and can record, no
opinion about what the right action in a situation was: that adjudication is
manifest item M3b, is blocked on the Decision Packet, and must be reached
independently of the scorer that produced these situations.

Usage:
    python3 oscillation_library.py [--dir DIR] [--verbose]
    from oscillation_library import load_library
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA_SITUATION = "troll-farm-oscillation-situation-v1"
SCHEMA_INDEX = "troll-farm-oscillation-library-index-v1"

DEFAULT_DIR = Path(__file__).resolve().parent / "oscillation-library"

MECHANISMS = ("M1", "M2", "M3", "UNCLASSIFIED")
BLOCKER_STATES = ("IDLE", "WORKING", "NONE")
KINDS = ("D1_EPISODE", "P4_STALL", "REAL_CORPUS")
COMPLETENESS = ("FULL", "PARTIAL")

# Fields every situation must carry.  A missing field is an integrity failure,
# not a default: a situation that cannot say where it came from is not frozen.
REQUIRED_SITUATION_FIELDS = (
    "schema", "id", "kind", "completeness", "provenance", "classification",
    "window", "world_state_at_entry", "detectors", "multiplicity",
    "unresolved", "content_sha256",
)
REQUIRED_PROVENANCE_FIELDS = (
    "source", "corpus_version", "instrument_version", "bot_source",
    "bot_source_sha256",
)


class IntegrityError(Exception):
    """Raised on any hash, schema or count mismatch.  The loader fails closed:
    no partially-verified library is ever returned."""


# ---------------------------------------------------------------------------
# hashing
# ---------------------------------------------------------------------------

def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def payload_sha256(situation: dict) -> str:
    """SHA-256 over the situation with `content_sha256` removed.

    Canonical JSON (sorted keys, no insignificant whitespace) so the digest is
    a property of the DATA, not of the file's formatting.
    """
    payload = {k: v for k, v in situation.items() if k != "content_sha256"}
    return hashlib.sha256(_canonical(payload)).hexdigest()


def library_sha256(entries) -> str:
    """SHA-256 over the (id, content_sha256) pairs, sorted by id.

    Catches an added or removed situation file, which a per-file digest alone
    cannot.
    """
    pairs = sorted((e["id"], e["content_sha256"]) for e in entries)
    return hashlib.sha256(_canonical(pairs)).hexdigest()


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_index(directory=DEFAULT_DIR) -> dict:
    path = Path(directory) / "index.json"
    if not path.exists():
        raise IntegrityError("library index missing: %s" % path)
    try:
        index = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise IntegrityError("index is not valid JSON: %s" % exc) from exc
    if index.get("schema") != SCHEMA_INDEX:
        raise IntegrityError("index schema is %r, expected %r"
                             % (index.get("schema"), SCHEMA_INDEX))
    return index


def load_library(directory=DEFAULT_DIR, verify=True) -> list:
    """Return the frozen situations, or raise `IntegrityError`.

    Checks, in order -- every one of them fails the whole load, never a
    single situation:

      1. the index parses and declares the expected schema;
      2. the set of `*.json` files on disk (excluding the index) is EXACTLY
         the set the index names -- no extra, no missing;
      3. `index.situation_count` equals both the number of index entries and
         the number of situation files;
      4. every situation parses, declares the expected schema, and carries
         every required field;
      5. every situation's recomputed payload digest equals the
         `content_sha256` stored inside the file;
      6. ... and equals the digest the index records for it;
      7. the recomputed `library_sha256` equals the one the index records;
      8. enumerated fields hold enumerated values, and the id matches the
         file name.
    """
    directory = Path(directory)
    index = load_index(directory)
    entries = index.get("situations")
    if not isinstance(entries, list):
        raise IntegrityError("index has no `situations` list")

    on_disk = sorted(p.name for p in directory.glob("*.json")
                     if p.name != "index.json")
    named = sorted(e.get("file", "") for e in entries)
    if on_disk != named:
        extra = sorted(set(on_disk) - set(named))
        missing = sorted(set(named) - set(on_disk))
        raise IntegrityError(
            "library file set does not match the index: %d files on disk, %d "
            "named; unindexed=%s missing=%s"
            % (len(on_disk), len(named), extra, missing))
    declared = index.get("situation_count")
    if declared != len(entries) or declared != len(on_disk):
        raise IntegrityError(
            "index situation_count=%r but %d index entries and %d files"
            % (declared, len(entries), len(on_disk)))

    if not verify:
        return [json.loads((directory / e["file"]).read_text())
                for e in entries]

    situations = []
    for entry in entries:
        path = directory / entry["file"]
        try:
            sit = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise IntegrityError("%s is not valid JSON: %s"
                                 % (entry["file"], exc)) from exc
        for field in REQUIRED_SITUATION_FIELDS:
            if field not in sit:
                raise IntegrityError("%s: missing required field %r"
                                     % (entry["file"], field))
        if sit["schema"] != SCHEMA_SITUATION:
            raise IntegrityError("%s: schema is %r, expected %r"
                                 % (entry["file"], sit["schema"],
                                    SCHEMA_SITUATION))
        if sit["id"] != entry["id"] or path.name != "%s.json" % sit["id"]:
            raise IntegrityError(
                "%s: id %r does not match index id %r / file name"
                % (entry["file"], sit["id"], entry["id"]))
        digest = payload_sha256(sit)
        if digest != sit["content_sha256"]:
            raise IntegrityError(
                "%s (%s): content hash mismatch -- file records %s, payload "
                "hashes to %s. The frozen situation has been modified; "
                "refusing to load the library."
                % (entry["file"], sit["id"], sit["content_sha256"], digest))
        if digest != entry.get("content_sha256"):
            raise IntegrityError(
                "%s (%s): index records %s, payload hashes to %s"
                % (entry["file"], sit["id"], entry.get("content_sha256"),
                   digest))
        for field, allowed in (("kind", KINDS),
                               ("completeness", COMPLETENESS)):
            if sit[field] not in allowed:
                raise IntegrityError("%s: %s=%r not in %s"
                                     % (entry["file"], field, sit[field],
                                        allowed))
        cls = sit["classification"]
        if cls.get("mechanism") not in MECHANISMS:
            raise IntegrityError("%s: mechanism=%r not in %s"
                                 % (entry["file"], cls.get("mechanism"),
                                    MECHANISMS))
        if cls.get("blocker_state") not in BLOCKER_STATES:
            raise IntegrityError("%s: blocker_state=%r not in %s"
                                 % (entry["file"], cls.get("blocker_state"),
                                    BLOCKER_STATES))
        for field in REQUIRED_PROVENANCE_FIELDS:
            if field not in sit["provenance"]:
                raise IntegrityError("%s: provenance lacks %r"
                                     % (entry["file"], field))
        if sit["completeness"] == "FULL" and not sit["world_state_at_entry"]:
            raise IntegrityError(
                "%s: declared FULL but carries no world state at entry"
                % entry["file"])
        if sit["completeness"] == "PARTIAL" and not sit.get(
                "world_state_absent_reason"):
            raise IntegrityError(
                "%s: declared PARTIAL but gives no reason for the absent "
                "world state" % entry["file"])
        situations.append(sit)

    recomputed = library_sha256(entries)
    if recomputed != index.get("library_sha256"):
        raise IntegrityError(
            "library hash mismatch: index records %s, recomputed %s -- a "
            "situation has been added, removed or replaced."
            % (index.get("library_sha256"), recomputed))
    return situations


# ---------------------------------------------------------------------------
# convenience views (read-only; no adjudication)
# ---------------------------------------------------------------------------

def by_mechanism(situations) -> dict:
    out = {m: [] for m in MECHANISMS}
    for s in situations:
        out[s["classification"]["mechanism"]].append(s)
    return out


def histogram(situations, field="mechanism") -> dict:
    out = {}
    for s in situations:
        key = (s["classification"][field] if field in s["classification"]
               else s[field])
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def find(situations, **criteria):
    """Situations matching every criterion.  Keys may name a top-level field,
    a classification field, or a provenance field."""
    def match(s, k, v):
        for scope in (s, s["classification"], s["provenance"], s["window"]):
            if isinstance(scope, dict) and k in scope:
                return scope[k] == v
        return False
    return [s for s in situations
            if all(match(s, k, v) for k, v in criteria.items())]


def episode_count(situations) -> int:
    """Total episodes represented, counting multiplicity."""
    return sum(s["multiplicity"]["episodes"] for s in situations)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="verify the frozen library")
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    try:
        sits = load_library(args.dir)
    except IntegrityError as exc:
        print("oscillation_library: INTEGRITY FAILURE: %s" % exc,
              file=sys.stderr)
        return 1
    index = load_index(args.dir)
    print("oscillation_library: OK -- %d situations, %d episodes, "
          "library_sha256 %s"
          % (len(sits), episode_count(sits), index["library_sha256"]))
    print("  mechanism:", histogram(sits, "mechanism"))
    print("  blocker:  ", histogram(sits, "blocker_state"))
    print("  kind:     ", histogram(sits, "kind"))
    if args.verbose:
        for s in sits:
            print("  %s %-12s %-4s %-8s x%-3d %s"
                  % (s["id"], s["kind"], s["classification"]["mechanism"],
                     s["classification"]["blocker_state"],
                     s["multiplicity"]["episodes"],
                     s["provenance"].get("map_id")
                     or s["provenance"].get("game_id")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
