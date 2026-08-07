#!/usr/bin/env python3
"""Freeze the pre-v2 legacy message baseline (transport rule 5, TQ-3 repair).

Transport rule 5 grandfathers legacy (no `schema_version`) messages
indefinitely. Left open-ended that is an enforcement bypass: a sender who omits
`schema_version` skips v2 validation entirely, and a backdated filename defeats
any date cutoff. `scripts/inbox_sweep.py` therefore grandfathers only the exact
paths pinned here, by blob.

Run ONCE at migration and commit the result to the coordinator's canonical
branch. It is a frozen artifact: a legitimately new legacy message is a
contradiction in terms, so regenerating it to "fix" a delivery error would
re-open the very hole it closes. Re-run it only to audit drift with `--check`.

Usage:
    python3 scripts/build_legacy_baseline.py            # write the baseline
    python3 scripts/build_legacy_baseline.py --check    # audit, write nothing
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

try:
    import inbox_sweep
except ImportError:  # invoked as `python3 -m scripts.build_legacy_baseline`
    from scripts import inbox_sweep


def collect_legacy(per_path: dict[str, dict[str, list[str]]]) -> dict[str, str]:
    """Return path → blob oid for every currently-legacy authoritative message."""
    baseline: dict[str, str] = {}
    for path in sorted(per_path):
        oids = per_path[path]
        if len(oids) != 1:
            # An immutable-path collision is a transport error in its own right;
            # never pin one, or the baseline would bless one side of it.
            continue
        (oid, _), = oids.items()
        body = inbox_sweep.git("cat-file", "blob", oid)
        if not inbox_sweep.Message(path, "baseline", body).is_v2:
            baseline[path] = oid
    return baseline


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="compare against the committed baseline; write nothing")
    args = ap.parse_args()

    root = pathlib.Path(inbox_sweep.git("rev-parse", "--show-toplevel").strip())
    _, per_path = inbox_sweep.scan_authoritative()
    baseline = collect_legacy(per_path)
    target = root / inbox_sweep.LEGACY_BASELINE_FILE

    payload = {
        "schema_version": inbox_sweep.LEGACY_BASELINE_SCHEMA_VERSION,
        "note": (
            "Frozen at the schema-v2 migration. Exactly these paths are "
            "grandfathered as pre-v2; every other message must declare "
            "schema_version: 2. Do not regenerate to clear a delivery error."
        ),
        "paths": dict(sorted(baseline.items())),
    }
    text = json.dumps(payload, indent=2, sort_keys=False) + "\n"

    if args.check:
        if not target.exists():
            print(f"baseline absent: {target}", file=sys.stderr)
            return 2
        committed = json.loads(target.read_text(encoding="utf-8")).get("paths", {})
        added = sorted(set(baseline) - set(committed))
        removed = sorted(set(committed) - set(baseline))
        changed = sorted(
            p for p in set(baseline) & set(committed) if baseline[p] != committed[p]
        )
        print(f"committed {len(committed)} pinned paths; observed {len(baseline)}")
        for label, items in (("new legacy (must be v2)", added),
                             ("missing from refs", removed),
                             ("blob changed", changed)):
            print(f"  {label}: {len(items)}")
            for path in items[:10]:
                print(f"    {path}")
        return 2 if (added or removed or changed) else 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"wrote {target.relative_to(root)} with {len(baseline)} pinned paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
