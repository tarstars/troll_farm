#!/usr/bin/env python3
"""Two-truths pre-build exposure analysis, from the accepted Phase-2 artifacts.

The charter's item 3 says the broader orchard rule's divergences "fail only where games become
blocking". This measures what that means for P3 specifically, because P3 does not work like the
other properties: it is VIEW-LEVEL and ABSOLUTE. `eval_p3` (fuzz_panel.py:1817) raises a violation
whenever an orchard-eligible view's candidate command stream differs from the parent's AT ALL, and
a violation blocks. So on that population "divergence" and "blocking" are the same event.

Second structural fact: a self-judged floor compares a bot against itself, so its command streams
are identical by construction and its P3 count is necessarily ZERO. Every P3 violation is
therefore de-novo unless the floor blocks that same game for some other reason.
"""
import json, sys
from pathlib import Path

FIVE = [("m021", 0), ("m040", 0), ("m063", 1), ("m078", 1), ("m090", 1)]


def rows(p):
    return {(g["map_id"], g["seat"]): g for g in json.loads(Path(p).read_text())["games"]}


def main():
    cand, floor = rows(sys.argv[1]), rows(sys.argv[2])
    oe = sorted(k for k, g in cand.items() if g["orchard_eligible"])
    floor_p3 = sum(1 for k in oe if any(v.get("property") == "P3" for v in floor[k]["violations"]))
    absorbed = [k for k in oe if floor[k]["block"]]
    exposed = [k for k in oe if not floor[k]["block"]]
    out = {
        "note": __doc__.strip(),
        "orchard_eligible_games": len(oe),
        "floor_p3_violations": floor_p3,
        "floor_p3_is_structurally_zero": floor_p3 == 0,
        "absorbed_by_floor_blocking": [{"map_id": k[0], "seat": k[1]} for k in absorbed],
        "exposed_clean_orchard_views": [{"map_id": k[0], "seat": k[1]} for k in exposed],
        "five_non_p3_denovo_untouchable": [{"map_id": k[0], "seat": k[1]} for k in FIVE],
        "denovo_lower_bound": len(FIVE),
        "denovo_upper_bound": len(FIVE) + len(exposed),
        "frozen_gate": 0,
        "reading": (
            f"Two-truths item 1 (delete the flat-1 fiction) is BYTE-IDENTICAL to what Door-1 "
            f"already did, so the {len(FIVE)} non-P3 de-novo games are reproduced exactly: they "
            f"are the lower bound, not an estimate. Item 2 (exclude orchard trees from chop "
            f"candidacy) ADDS divergence on precisely the population P3 polices, where the parent "
            f"does not exclude; each clean orchard view whose commands change becomes a NEW "
            f"de-novo. Range {len(FIVE)}-{len(FIVE) + len(exposed)} against a frozen gate of 0."
        ),
    }
    Path(sys.argv[3]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"  orchard-eligible games: {len(oe)}   floor P3 violations: {floor_p3} "
          f"(structurally zero: {floor_p3 == 0})")
    print(f"  absorbed (floor already blocks): {len(absorbed)}")
    print(f"  exposed  (floor clean -> new P3 becomes DE-NOVO): {len(exposed)}")
    print(f"  de-novo under two-truths: LOWER {len(FIVE)}  UPPER {len(FIVE) + len(exposed)}  "
          f"(frozen gate 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
