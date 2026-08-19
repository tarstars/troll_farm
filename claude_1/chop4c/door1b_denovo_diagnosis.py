#!/usr/bin/env python3
"""Door-1b charter constraint 3: per-game diagnosis of the five non-P3 de-novo games.

"The panel will tell us" is not a diagnosis. This measures two things per game, from the accepted
Phase-2 artifacts, BEFORE any 1b panel is attempted:

  ORDER  first-order  = the opponent's command stream is IDENTICAL to the floor's, so the world
                        the candidate faced was the same and the divergence is the candidate's own
                        choice -- the evidence rule acting directly.
         second-order = the opponent's stream DIFFERS, so the candidate changed the world and the
                        opponent reacted; the block may be a consequence of that changed world
                        rather than of the rule at the blocking site.
         The discriminator is necessary, not sufficient: identical opponent commands cannot prove
         the internal cause, only that the world was not the cause. Stated so the limit traveIs
         with the number.

  SCOPE  does Door-1b's bound change this game? The 1b design alters behaviour ONLY on
         orchard-eligible views. A game whose view is not orchard-eligible is bit-for-bit
         unaffected: 1b == Door-1 there, the corpus is fixed, and games are independent.
"""
import json, sys
from pathlib import Path

FIVE = [("m021", 0), ("m040", 0), ("m063", 1), ("m078", 1), ("m090", 1)]
P3_FOUR = [("m025", 0), ("m035", 0), ("m054", 0), ("m104", 0)]


def rows(p):
    return {(g["map_id"], g["seat"]): g for g in json.loads(Path(p).read_text())["games"]}


def main():
    cand, floor = rows(sys.argv[1]), rows(sys.argv[2])
    out = {"games": [], "note": __doc__.strip()}
    for k in FIVE:
        c, f = cand[k], floor[k]
        same_world = c["opponent_commands_sha256"] == f["opponent_commands_sha256"]
        props = sorted({v.get("property") for v in c["violations"] if v.get("property")})
        out["games"].append({
            "map_id": k[0], "seat": k[1], "class": c["class"], "profile": c["profile"],
            "orchard_eligible": c["orchard_eligible"],
            "opponent_stream_identical_to_floor": same_world,
            "order": "first-order (same world)" if same_world else "second-order (world diverged)",
            "properties": props,
            "detectors": {d: n for d, n in c["detector_counts"].items() if n},
            "changed_by_1b_scope": bool(c["orchard_eligible"]),
        })
    unaffected = [g for g in out["games"] if not g["changed_by_1b_scope"]]
    out["p3_four_all_orchard_eligible"] = all(cand[k]["orchard_eligible"] for k in P3_FOUR)
    out["five_none_orchard_eligible"] = not any(g["orchard_eligible"] for g in out["games"])
    out["predicted_denovo_under_1b"] = len(unaffected)
    out["prediction"] = (
        f"Door-1b erases the 4 P3 de-novo games by construction (all orchard-eligible) and changes "
        f"NONE of the {len(unaffected)} non-P3 de-novo games (none orchard-eligible). Predicted "
        f"de-novo under Door-1b: {len(unaffected)}, against a frozen gate of ZERO. On this "
        f"evidence the chartered 1b design does not reach ready-with-gates."
    )
    Path(sys.argv[3]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for g in out["games"]:
        print(f"  {g['map_id']} s{g['seat']} [{g['class']}/{g['profile']}] "
              f"{g['order']:<28} props={','.join(g['properties'])} "
              f"orchard={g['orchard_eligible']} changed_by_1b={g['changed_by_1b_scope']}")
    print(f"\n  P3 four all orchard-eligible : {out['p3_four_all_orchard_eligible']}")
    print(f"  five none orchard-eligible   : {out['five_none_orchard_eligible']}")
    print(f"  PREDICTED de-novo under 1b   : {out['predicted_denovo_under_1b']} (gate is 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
