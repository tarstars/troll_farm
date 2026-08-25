#!/usr/bin/env python3
"""Door-1b charter constraint 3: per-game diagnosis of the five non-P3 de-novo games.

"The panel will tell us" is not a diagnosis. This measures two things per game, from the accepted
Phase-2 artifacts, BEFORE any 1b panel is attempted:

  OPPONENT-STREAM EQUALITY (a measurement, NOT a causal label)
         stream-identical = the opponent issued the same commands as in the floor run.
         stream-diverged  = the opponent issued different commands.

         CORRECTION (codex_1, 2026-08-19): an earlier version of this tool labelled these
         "first-order (same world)" and "second-order (world diverged)". That overstated the
         evidence and the correction is accepted. Equal opponent commands prove only that the
         OPPONENT did the same thing; they do NOT establish that the candidate faced the same
         world, because the candidate's own actions mutate state regardless of what the opponent
         does. The measurement stands; the causal reading has been withdrawn. Establishing
         first- vs second-order cause requires targeted replay, which this tool does not do and
         no longer claims to.

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
            "opponent_stream": "identical" if same_world else "diverged",
            "causal_order": "NOT ESTABLISHED — requires targeted replay (codex_1 correction)",
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
              f"opp-stream={g['opponent_stream']:<9} props={','.join(g['properties'])} "
              f"orchard={g['orchard_eligible']} changed_by_1b={g['changed_by_1b_scope']}")
    print(f"\n  P3 four all orchard-eligible : {out['p3_four_all_orchard_eligible']}")
    print(f"  five none orchard-eligible   : {out['five_none_orchard_eligible']}")
    print(f"  PREDICTED de-novo under 1b   : {out['predicted_denovo_under_1b']} (gate is 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
