#!/usr/bin/env python3
r"""Every panel-visible behaviour change, NAMED — including the ones that are not de-novo blocks.

The card requires every de-novo game diagnosed and named. Both bases produced **zero** de-novo
blocks, so a report that stopped there would say nothing. This enumerates, keyed `(map_id, seat)`,
every game where the candidate and its matched floor disagree on ANY consequence-bearing field:

- `block`            — the gate verdict itself (healed / de-novo)
- `violations`       — which PROPERTY fired (P1..P4), not merely which detector
- `flags`            — report-tier findings that do not block but are still a behaviour change

so that a change which does not happen to cross the blocking threshold is still on the record,
by name, rather than being invisible because it was not fatal.

Run:  python3 claude_1/picker2/named_changes.py
"""
import collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

PAIRS = {
    "cureC": (HERE / "panel-cureC-cand.json", REPO / "claude_1/chop4c/osc031-phase2-floor.json"),
    "door1": (HERE / "panel-door1-cand.json", HERE / "panel-door1-floor.json"),
}
OUT = HERE / "named-changes-2026-08-20.json"


def props(g):
    return sorted({v.get("property") for v in g["violations"] if v.get("property")})


def flagnames(g):
    return sorted({f.get("flag") for f in (g.get("flags") or [])})


def main():
    report = {}
    for base, (cp, fp) in PAIRS.items():
        cand = {(g["map_id"], g["seat"]): g for g in json.loads(cp.read_text())["games"]}
        floor = {(g["map_id"], g["seat"]): g for g in json.loads(fp.read_text())["games"]}
        rows, kinds = [], collections.Counter()
        for k in sorted(cand):
            c, f = cand[k], floor[k]
            cb, fb = bool(c["block"]), bool(f["block"])
            cpr, fpr, cf, ff = props(c), props(f), flagnames(c), flagnames(f)
            if (cb, cpr, cf) == (fb, fpr, ff):
                continue
            kind = ("DE_NOVO_BLOCK" if cb and not fb else
                    "HEALED_BLOCK" if fb and not cb else
                    "PROPERTY_CHANGE_WITHIN_A_BLOCKED_GAME" if cb and fb else
                    "PROPERTY_OR_FLAG_CHANGE_IN_A_CLEAN_GAME")
            kinds[kind] += 1
            rows.append({"map_id": k[0], "seat": k[1], "kind": kind,
                         "class": c["class"], "profile": c["profile"],
                         "floor_block": fb, "cand_block": cb,
                         "floor_properties": fpr, "cand_properties": cpr,
                         "floor_flags": ff, "cand_flags": cf,
                         "floor_detectors": {d: n for d, n in f["detector_counts"].items() if n},
                         "cand_detectors": {d: n for d, n in c["detector_counts"].items() if n},
                         "new_properties": [p for p in cpr if p not in fpr],
                         "new_flags": [x for x in cf if x not in ff]})
        report[base] = {"changed_games": len(rows), "by_kind": dict(kinds), "games": rows}
        print(f"  {base}: {len(rows)} of 240 keyed games changed  {dict(kinds)}")
        for r in rows:
            if r["kind"] != "HEALED_BLOCK":
                print(f"    NAMED  {r['map_id']} seat {r['seat']} [{r['class']}/{r['profile']}] "
                      f"{r['kind']}  new properties {r['new_properties'] or '-'}  "
                      f"new flags {r['new_flags'] or '-'}")
    OUT.write_text(json.dumps({"task": "20260820-pair-selector-anti-benching", "phase": 2,
                               "keyed_by": "(map_id, seat)", "bases": report}, indent=2,
                              sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
