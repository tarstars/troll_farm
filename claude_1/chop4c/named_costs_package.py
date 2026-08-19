#!/usr/bin/env python3
"""CARD 1 under owner ruling B: assemble the named-costs package from ACCEPTED artifacts.

Nothing here is newly measured. Every number is read from artifacts already reproduced
independently by codex_1 (decomposition byte-identical at acd7283d, exposure at 636efdb8). The
deliverable is a complete and honest COST SHEET: each de-novo game named with its one-line
diagnosis, the healed set, the aggregate, latency and parity.

Cost lines are DERIVED from each game's recorded properties and detectors, not hand-written, so a
game cannot acquire a friendlier description than its evidence supports.
"""
import json, sys
from pathlib import Path

# One-line mechanism per property, applied to whatever the game's record actually contains.
PROP = {
    "P1": "oscillation detector episode (D-1 two-cell alternation)",
    "P2": "R-5 full-cargo two-cell alternation without a cargo change",
    "P3": "orchard-dormancy divergence: candidate commands differ from the parent on an "
          "orchard-eligible view, where byte-equality is required",
    "P4": "liveness floor: no own-inventory/own-cargo progress in a rolling window while work "
          "remained",
}


def rows(p):
    return {(g["map_id"], g["seat"]): g for g in json.loads(Path(p).read_text())["games"]}


def cost_line(g):
    props = sorted({v.get("property") for v in g["violations"] if v.get("property")})
    dets = {d: n for d, n in g["detector_counts"].items() if n}
    why = "; ".join(PROP[p] for p in props if p in PROP)
    p3 = [v for v in g["violations"] if v.get("property") == "P3"]
    detail = ""
    if p3 and isinstance(p3[0].get("detail"), dict):
        d = p3[0]["detail"]
        detail = (f" first divergence turn {d.get('first_divergence_turn')}: "
                  f"candidate {d.get('candidate')!r} vs parent {d.get('parent')!r}")
    return {"map_id": g["map_id"], "seat": g["seat"], "class": g["class"], "profile": g["profile"],
            "orchard_eligible": g["orchard_eligible"], "properties": props, "detectors": dets,
            "diagnosis": why + detail}


def main():
    cand, floor = rows(sys.argv[1]), rows(sys.argv[2])
    dec = json.loads(Path(sys.argv[3]).read_text())
    lat = json.loads(Path(sys.argv[4]).read_text())
    par = json.loads(Path(sys.argv[5]).read_text())

    costs = [cost_line(cand[(r["map_id"], r["seat"])]) for r in dec["de_novo"]]
    healed = [{"map_id": r["map_id"], "seat": r["seat"], "class": r["class"],
               "floor_properties": sorted({v.get("property")
                                           for v in floor[(r["map_id"], r["seat"])]["violations"]
                                           if v.get("property")})}
              for r in dec["healed"]]
    pkg = {
        "regime": "named-costs gate (owner ruling B, 2026-08-19). Zero-de-novo remains the gate "
                  "for surgical additions; behaviour-changing candidates are judged on the M-1 "
                  "paired night with their costs named.",
        "candidate_sha256": dec["candidate_sha256"],
        "floor_sha256": dec["floor_sha256"],
        "candidate_is": "the Door-1 PURE DELETION: the resident's flat-1 fictional-decay block at "
                        ":514-520 replaced by 0. One hunk, no additions, no predicate, net-simpler.",
        "corpus": dec["corpus_version"], "instrument": dec["instrument_version"],
        "games_per_arm": dec["games_per_arm"],
        "named_costs": costs, "named_cost_count": len(costs),
        "healed": healed, "healed_count": len(healed),
        "aggregate": dec["aggregate_context_only"],
        "latency": {k: v for k, v in lat.items() if not k.startswith("_")},
        "latency_limits": lat.get("_limits"),
        "parity": {"rows": par["rows"], "field_comparisons": par["field_comparisons"],
                   "identical": par["identical"], "excluded_fields": par["excluded_fields"]},
        "nothing_newly_measured": True,
        "causal_order_status": "opponent-stream equality is reported as a MEASUREMENT only; "
                               "first/second-order causal labels were withdrawn (codex_1 "
                               "correction, 2026-08-19) and establishing cause needs targeted "
                               "replay not performed here.",
    }
    Path(sys.argv[6]).write_text(json.dumps(pkg, indent=2, sort_keys=True) + "\n")
    print(f"  named costs: {len(costs)}   healed: {len(healed)}   "
          f"aggregate cand {pkg['aggregate']['candidate_blocking']} vs floor "
          f"{pkg['aggregate']['floor_blocking']}")
    for c in costs:
        print(f"    {c['map_id']} s{c['seat']} [{c['class']}] {','.join(c['properties'])}: "
              f"{c['diagnosis'][:96]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
