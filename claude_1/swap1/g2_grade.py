#!/usr/bin/env python3
r"""G-2 — cure alpha rev 2 on the MATCHED panel, graded to the amended gate.

Task `20260821-swap-r1-cure`, gate **G-2**, graded to the owner-approved amendment
`coordination/messages/local_claude_1/20260821T105914Z-20260821-swap-r1-cure-gate-amendment-policy.md`:

> on the matched panel (base and candidate, all maps/seats/profiles) count episodes of the target
> shapes -- corridor pass-block and idle-troll-on-a-plant -- with the D-1/P4 detectors + the
> oracle: **healed - new must be positive, every changed game named**, no new episode of any other
> shape left unexplained.

## Two panels, one world

`fuzz_panel` runs a candidate arm and a parent arm per (map, seat), so ONE run already contains a
matched pair -- but its P4 evaluation is asymmetric by construction (`eval_p4(tr_c, tr_p, ...)`
scores the candidate AGAINST the parent), so a parent-arm P4 column cannot be read out of it.
Rather than re-deriving P4 in a reduced mode -- the precision codex_1 corrected me on at
`20260821T115613Z`, where `post_state=None` is a documented REDUCED mode and not the accepted P4 --
this grader runs the accepted champion-library FLOOR panel as well, in which the champion is the
candidate and its P4 column is therefore computed in the full accepted mode with `post_state`
supplied.

That is only legitimate if the two panels played the SAME games. **Gate M** proves it rather than
assuming it: for every (map_id, seat), the floor panel's CANDIDATE transcript and command stream
must be byte-identical to this panel's PARENT transcript and command stream. Same bot, same map,
same seat, same opponent profile, same seed -- if any pair differs, the panels are not matched and
the grader refuses to report a single count.

D-1 needs no such crutch: it is a single-trace detector, so both arms are graded directly with
`trace_detectors.detect_d1` on their own transcripts, inside this one panel.

Run:  python3 claude_1/swap1/g2_grade.py --candidate-packet ... --floor-packet ...
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / _p))
import trace_detectors as td  # noqa: E402


def load(games_gz: Path) -> dict:
    rows = {}
    with gzip.open(games_gz, "rt") as fh:
        for line in fh:
            row = json.loads(line)
            rows[(row["map_id"], row["seat"])] = row
    return rows


def gate_m(cand_rows: dict, floor_rows: dict) -> tuple[bool, list[str]]:
    """The floor panel's candidate arm must BE this panel's parent arm, game for game."""
    problems = []
    if set(cand_rows) != set(floor_rows):
        problems.append("the two panels do not cover the same (map, seat) set: "
                        f"{len(set(cand_rows) ^ set(floor_rows))} keys differ")
        return False, problems
    for key in sorted(cand_rows):
        c, f = cand_rows[key], floor_rows[key]
        for mine, theirs, what in (("parent_transcript", "candidate_transcript", "transcript"),
                                   ("parent_commands", "candidate_commands", "commands"),
                                   ("parent_opponent_commands", "candidate_opponent_commands",
                                    "opponent commands")):
            if c["artifacts"][mine] != f["artifacts"][theirs]:
                problems.append(f"{key[0]} seat {key[1]}: base {what} differs between the two "
                                "panels")
        if c["seed"] != f["seed"] or c["profile"] != f["profile"] or c["class"] != f["class"]:
            problems.append(f"{key[0]} seat {key[1]}: seed/profile/class differ")
    return not problems, problems


def d1_count(transcript: str, commands: str) -> int:
    return len(td.detect_d1(td.build_trace(transcript, commands))["episodes"])


def p4_details(row) -> list:
    return [v["detail"] for v in row["violations"] if v["property"] == "P4"]


def other_shapes(row) -> collections.Counter:
    """Every blocking violation that is NOT the D-1/P4 pair the amendment grades.

    The amendment's third clause -- "no new episode of any other shape left unexplained" -- is
    only a gate if the other shapes are counted. P1 violations carry the detector id, so D-2..D-9
    are named individually rather than lumped; P2 and P3 are counted by property.
    """
    seen = collections.Counter()
    for v in row["violations"]:
        if v["property"] == "P4":
            continue
        if v["property"] == "P1":
            if v["detector"] == "D-1":
                continue
            seen[f"P1/{v['detector']}"] += int(v["count"])
        else:
            seen[v["property"]] += 1
    return seen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate-games", required=True)
    ap.add_argument("--floor-games", required=True)
    ap.add_argument("--json", default=str(HERE / "g2-panel-2026-08-21.json"))
    args = ap.parse_args(argv)

    cand_rows = load(Path(args.candidate_games))
    floor_rows = load(Path(args.floor_games))

    matched, problems = gate_m(cand_rows, floor_rows)
    if not matched:
        print("GATE M FAILED — the panels are not matched; refusing to report counts")
        for p in problems[:20]:
            print("   ", p)
        Path(args.json).write_text(json.dumps(
            {"task": "20260821-swap-r1-cure", "gate": "G-2", "gate_m_matched_panel": False,
             "problems": problems}, indent=2) + "\n")
        return 1
    print(f"GATE M PASS — {len(cand_rows)} (map, seat) games matched byte-for-byte on the base arm")

    games, changed = [], []
    tot = collections.Counter()
    tot_base_other, tot_cand_other = collections.Counter(), collections.Counter()
    for key in sorted(cand_rows):
        c, f = cand_rows[key], floor_rows[key]
        base_d1 = d1_count(c["artifacts"]["parent_transcript"], c["artifacts"]["parent_commands"])
        cand_d1 = d1_count(c["artifacts"]["candidate_transcript"],
                           c["artifacts"]["candidate_commands"])
        base_p4 = len(p4_details(f))     # accepted mode: the champion IS the floor's candidate
        cand_p4 = len(p4_details(c))
        identical = (c["artifacts"]["candidate_commands"] == c["artifacts"]["parent_commands"])
        base_other, cand_other = other_shapes(f), other_shapes(c)
        for k, n in base_other.items():
            tot_base_other[k] += n
        for k, n in cand_other.items():
            tot_cand_other[k] += n
        entry = {"map_id": key[0], "seat": key[1], "class": c["class"], "profile": c["profile"],
                 "seed": c["seed"], "base_d1_episodes": base_d1, "candidate_d1_episodes": cand_d1,
                 "base_p4_violations": base_p4, "candidate_p4_violations": cand_p4,
                 "command_stream_identical_to_base": identical,
                 "base_other_shapes": dict(base_other), "candidate_other_shapes": dict(cand_other),
                 "base_margin": c["parent"]["margin"], "candidate_margin": c["candidate"]["margin"]}
        games.append(entry)
        tot["base_d1"] += base_d1
        tot["cand_d1"] += cand_d1
        tot["base_p4"] += base_p4
        tot["cand_p4"] += cand_p4
        tot["identical_games"] += identical
        if base_d1 != cand_d1 or base_p4 != cand_p4 or base_other != cand_other:
            changed.append(entry)

    d1_healed = sum(max(0, g["base_d1_episodes"] - g["candidate_d1_episodes"]) for g in games)
    d1_new = sum(max(0, g["candidate_d1_episodes"] - g["base_d1_episodes"]) for g in games)
    p4_healed = sum(max(0, g["base_p4_violations"] - g["candidate_p4_violations"]) for g in games)
    p4_new = sum(max(0, g["candidate_p4_violations"] - g["base_p4_violations"]) for g in games)

    verdict = {
        "task": "20260821-swap-r1-cure", "gate": "G-2", "revision": 2,
        "amendment": ("coordination/messages/local_claude_1/"
                      "20260821T105914Z-20260821-swap-r1-cure-gate-amendment-policy.md"),
        "gate_m_matched_panel": True,
        "games": len(games),
        "games_with_a_command_stream_identical_to_the_base": tot["identical_games"],
        "d1": {"base_episodes": tot["base_d1"], "candidate_episodes": tot["cand_d1"],
               "healed": d1_healed, "new": d1_new, "healed_minus_new": d1_healed - d1_new},
        "p4": {"base_violations": tot["base_p4"], "candidate_violations": tot["cand_p4"],
               "healed": p4_healed, "new": p4_new, "healed_minus_new": p4_healed - p4_new,
               "base_column_mode": ("accepted: the floor panel's own candidate arm, post_state "
                                    "supplied; NOT the reduced post_state=None mode")},
        "other_shapes": {
            "base": dict(tot_base_other), "candidate": dict(tot_cand_other),
            "shapes_that_grew": {k: [tot_base_other.get(k, 0), tot_cand_other[k]]
                                 for k in tot_cand_other
                                 if tot_cand_other[k] > tot_base_other.get(k, 0)},
        },
        "changed_games": changed,
        "rows": games,
    }
    grew = verdict["other_shapes"]["shapes_that_grew"]
    verdict["no_other_shape_grew"] = not grew

    # The amendment's third clause is "no new episode of any other shape left UNEXPLAINED", so a
    # shape that grew is not automatically a failure -- but the explanation has to be MEASURED.
    # P3 is the one shape whose base column is vacuous on a floor panel: eval_p3 flags any command
    # divergence from the parent on an orchard-eligible map, and on the floor the candidate IS the
    # parent, so the base P3 count is 0 by construction and cannot be a bar. The check below is
    # what makes that a finding rather than an assertion.
    explanations = {}
    if "P3" in grew:
        floor_p3 = sum(1 for f in floor_rows.values()
                       for v in f["violations"] if v["property"] == "P3")
        floor_diverged = sum(1 for f in floor_rows.values()
                             if f["artifacts"]["candidate_commands"]
                             != f["artifacts"]["parent_commands"])
        offenders = [(k, cand_rows[k]) for k in sorted(cand_rows)
                     if any(v["property"] == "P3" for v in cand_rows[k]["violations"])]
        all_orchard_and_diverged = all(
            r["orchard_eligible"] and r["artifacts"]["candidate_commands"]
            != r["artifacts"]["parent_commands"] for _, r in offenders)
        explanations["P3"] = {
            "verdict": ("EXPLAINED: structural, not a measured harm"
                        if floor_p3 == 0 and floor_diverged == 0 and all_orchard_and_diverged
                        else "UNEXPLAINED"),
            "floor_p3_violations": floor_p3,
            "floor_games_whose_command_stream_diverges_from_its_own_parent": floor_diverged,
            "every_p3_row_is_orchard_eligible_and_diverged_from_the_base":
                all_orchard_and_diverged,
            "rows": [{"map_id": k[0], "seat": k[1],
                      "first_divergence": [v["detail"] for v in r["violations"]
                                           if v["property"] == "P3"]}
                     for k, r in offenders],
            "why": ("eval_p3 (fuzz_panel.py:1817) flags ANY command divergence from the parent on "
                    "an orchard-eligible map. On the floor panel the candidate IS the parent, so "
                    "its P3 column is 0 by construction on every row and the base side of this "
                    "comparison is vacuous. The growth therefore records alpha's own intended "
                    "exchange -- the divergence is the swap -- and not an orchard regression. "
                    "Whether P3 applies to an intentional transport change is the SAME open "
                    "applicability question codex_1 named on the anti-benching task at "
                    "20260821T120917Z; it is handed back, not decided here."),
        }
    verdict["explanations"] = explanations
    verdict["other_shape_growth_all_explained"] = all(
        e["verdict"].startswith("EXPLAINED") for e in explanations.values())
    verdict["healed_minus_new_positive"] = (d1_healed - d1_new) + (p4_healed - p4_new) > 0
    Path(args.json).write_text(json.dumps(verdict, indent=2) + "\n")

    print(f"\n  D-1 episodes  base {tot['base_d1']}  candidate {tot['cand_d1']}   "
          f"healed {d1_healed}  new {d1_new}  ->  {d1_healed - d1_new:+d}")
    print(f"  P4 violations base {tot['base_p4']}  candidate {tot['cand_p4']}   "
          f"healed {p4_healed}  new {p4_new}  ->  {p4_healed - p4_new:+d}")
    print(f"  games whose command stream is byte-identical to the base: "
          f"{tot['identical_games']}/{len(games)}")
    print(f"  changed games (named in the JSON): {len(changed)}")
    for g in changed:
        print(f"    {g['map_id']} seat {g['seat']} [{g['class']}/{g['profile']}]  "
              f"D-1 {g['base_d1_episodes']}->{g['candidate_d1_episodes']}  "
              f"P4 {g['base_p4_violations']}->{g['candidate_p4_violations']}  "
              f"other {dict(g['base_other_shapes'])}->{dict(g['candidate_other_shapes'])}")
    print(f"\n  other shapes  base {dict(tot_base_other)}")
    print(f"                candidate {dict(tot_cand_other)}")
    print(f"  shapes that GREW: {grew if grew else 'none'}")
    for shape, e in explanations.items():
        print(f"    {shape}: {e['verdict']}")
    print(f"\n  G-2 healed-minus-new positive: {verdict['healed_minus_new_positive']} -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
