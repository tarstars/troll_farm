#!/usr/bin/env python3
"""Card 1 item (3b): process-count parity — the 240 rows must not depend on `processes`.

Compares the 8-process candidate arm against the 1-process arm row by row, keyed (map_id, seat).
Wall-clock fields are excluded by name and the exclusion is PRINTED, so nothing is quietly
dropped from the comparison; everything else must be identical, including the full violation
records and every command-error list.
"""
import json, sys
from pathlib import Path

# Excluded because they are timing, not result. Named explicitly rather than filtered by guesswork.
EXCLUDED = {"attempt"}


def rows(path):
    return {(g["map_id"], g["seat"]): g for g in json.loads(Path(path).read_text())["games"]}


def main():
    a, b = rows(sys.argv[1]), rows(sys.argv[2])
    if set(a) != set(b):
        print(f"PARITY FAIL: key sets differ by {len(set(a) ^ set(b))}")
        return 1
    print(f"  excluded from comparison (timing, not result): {sorted(EXCLUDED)}")
    diffs, compared = [], 0
    for k in sorted(a):
        ra, rb = a[k], b[k]
        fields = (set(ra) | set(rb)) - EXCLUDED
        for f in sorted(fields):
            compared += 1
            if json.dumps(ra.get(f), sort_keys=True) != json.dumps(rb.get(f), sort_keys=True):
                diffs.append((k, f))
    ok = not diffs
    print(f"  compared {len(a)} rows x {len(fields)} fields = {compared} field comparisons")
    print(f"  process-count parity (8-proc vs 1-proc): {'IDENTICAL' if ok else 'DIFFERS'}")
    for k, f in diffs[:20]:
        print(f"    differs: {k} field {f!r}")
    out = {"rows": len(a), "field_comparisons": compared, "excluded_fields": sorted(EXCLUDED),
           "identical": ok, "differing": [{"map_id": k[0], "seat": k[1], "field": f}
                                          for k, f in diffs]}
    # argv[3] optional so a later task can reuse THIS comparison rather than copy it; the
    # OSC-031 default is unchanged, so existing invocations behave exactly as before.
    Path(sys.argv[3] if len(sys.argv) > 3
         else "claude_1/chop4c/osc031-phase2-parity-2026-08-19.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
