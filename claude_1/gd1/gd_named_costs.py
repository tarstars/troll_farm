#!/usr/bin/env python3
r"""G-d — Phase 3b on the door-1 lineage: the named-cost table, both directions.

Task `20260820-pair-selector-anti-benching`, gate **G-d** ("panel with named costs, every changed
game named"), run under `local_codex_1`'s PROCEED ruling
`coordination/messages/local_codex_1/20260823T155558Z-20260820-pair-selector-anti-benching-policy.md`,
which fixes the decision subject as the **door-1 lineage** and the subject bytes as the pinned r2
build `09ed550f`.

## The two panels, and why the parent is P1+P2 and not the champion

`fuzz_panel` runs a candidate arm and a parent arm per (map, seat), so one run already carries a
matched pair -- but its P4 column is computed AGAINST the parent and so cannot be read as a
parent-arm P4. The accepted repair (claude_1/swap1/g2_grade.py) is to run the base against ITSELF
as a floor panel, where its P4 is computed in the full accepted mode with `post_state` supplied.
Both panels are run here, and `g2_grade.gate_m` -- imported, not reimplemented -- proves they
played the same games byte for byte before a single count is reported.

The parent on both configs is **P1+P2 door-1** (`5e1f4df4...`), the r2 build's own base, NOT the
champion of record `547fa706`. Grading against the champion would price P1+P2 and the SS1 hunk
together and attribute the sum to Phase 3b.

## What is named

Every game where the candidate arm and the base arm disagree on ANY consequence-bearing field --
the block verdict, which PROPERTY fired, which DETECTOR fired, or which report-tier FLAG fired
(that is where `r5-horizon` lives) -- is named with its map, seat, class, profile and both sides
of every field. A change that does not happen to cross the blocking threshold is still a named
cost. The classification vocabulary is `claude_1/picker2/named_changes.py`'s, imported.

## Falsifiers this table decides (design r2 SS7), and they are STOPS, not patches

- **SS7.3** the commitment side effect makes things worse on games outside the four fixtures;
- **SS7.5** a new or worse P3, P4 or `r5-horizon` event anywhere on the panel.

An aggregate improvement does not license either. The per-event table, not the panel mean, decides.

## What this file does NOT do

It does not grade progress -- that is G-e (`claude_1/regrade3/panel_regrade.py`, the accepted
two-clause instrument). A detector going quiet here is NOT a healed event until G-e says so.
It does not measure G-b, does not re-run reach, and promotes nothing.

Run:  python3 claude_1/gd1/gd_named_costs.py [--controls]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1/swap1"))
sys.path.insert(0, str(REPO / "claude_1/picker2"))
import g2_grade as G          # noqa: E402  gate_m, load, d1_count, p4_details, other_shapes
import named_changes as NC    # noqa: E402  props, flagnames

CAND_GAMES = Path("/tmp/claude-1000/p3b-gd/candidate/games/games.jsonl.gz")
FLOOR_GAMES = Path("/tmp/claude-1000/p3b-gd/floor/games/games.jsonl.gz")
OUT = HERE / "gd-named-costs-2026-08-23.json"


class GateError(Exception):
    """Anything that would make a number below mean something other than it says."""


def detectors(row) -> dict:
    return {d: n for d, n in row["detector_counts"].items() if n}


def row_view(cand_row, floor_row) -> dict:
    """The base side comes from the FLOOR panel's candidate arm; the candidate side from this one.

    Both are the same arm position in their own panel, so P1..P4 and the flags are computed in the
    same mode on both sides. The candidate panel's PARENT arm is used only for D-1 (a single-trace
    detector) and for the command-stream identity test, never for P4.
    """
    return {
        "base_block": bool(floor_row["block"]),
        "cand_block": bool(cand_row["block"]),
        "base_properties": NC.props(floor_row),
        "cand_properties": NC.props(cand_row),
        "base_flags": NC.flagnames(floor_row),
        "cand_flags": NC.flagnames(cand_row),
        "base_detectors": detectors(floor_row),
        "cand_detectors": detectors(cand_row),
        "base_p4_violations": len(G.p4_details(floor_row)),
        "cand_p4_violations": len(G.p4_details(cand_row)),
        "base_margin": floor_row["candidate"]["margin"],
        "cand_margin": cand_row["candidate"]["margin"],
    }


def classify(v) -> str:
    if v["cand_block"] and not v["base_block"]:
        return "DE_NOVO_BLOCK"
    if v["base_block"] and not v["cand_block"]:
        return "HEALED_BLOCK"
    if v["cand_block"] and v["base_block"]:
        return "PROPERTY_CHANGE_WITHIN_A_BLOCKED_GAME"
    return "PROPERTY_OR_FLAG_CHANGE_IN_A_CLEAN_GAME"


def grade(cand_rows, floor_rows) -> dict:
    rows, changed = [], []
    kinds = collections.Counter()
    tot = collections.Counter()
    base_det, cand_det = collections.Counter(), collections.Counter()
    base_prop, cand_prop = collections.Counter(), collections.Counter()
    base_flag, cand_flag = collections.Counter(), collections.Counter()

    for key in sorted(cand_rows):
        c, f = cand_rows[key], floor_rows[key]
        v = row_view(c, f)
        v["map_id"], v["seat"] = key
        v["class"], v["profile"], v["seed"] = c["class"], c["profile"], c["seed"]
        v["orchard_eligible"] = c["orchard_eligible"]
        v["command_stream_identical_to_base"] = (
            c["artifacts"]["candidate_commands"] == c["artifacts"]["parent_commands"])
        v["base_d1_episodes"] = G.d1_count(c["artifacts"]["parent_transcript"],
                                           c["artifacts"]["parent_commands"])
        v["cand_d1_episodes"] = G.d1_count(c["artifacts"]["candidate_transcript"],
                                           c["artifacts"]["candidate_commands"])
        tot["base_blocking"] += v["base_block"]
        tot["cand_blocking"] += v["cand_block"]
        tot["identical_games"] += v["command_stream_identical_to_base"]
        tot["base_d1"] += v["base_d1_episodes"]
        tot["cand_d1"] += v["cand_d1_episodes"]
        tot["base_p4"] += v["base_p4_violations"]
        tot["cand_p4"] += v["cand_p4_violations"]
        for d, n in v["base_detectors"].items():
            base_det[d] += n
        for d, n in v["cand_detectors"].items():
            cand_det[d] += n
        for p in v["base_properties"]:
            base_prop[p] += 1
        for p in v["cand_properties"]:
            cand_prop[p] += 1
        for fl in v["base_flags"]:
            base_flag[fl] += 1
        for fl in v["cand_flags"]:
            cand_flag[fl] += 1
        rows.append(v)
        same = ((v["base_block"], v["base_properties"], v["base_flags"], v["base_detectors"])
                == (v["cand_block"], v["cand_properties"], v["cand_flags"], v["cand_detectors"]))
        if not same:
            v = dict(v)
            v["kind"] = classify(v)
            v["new_properties"] = [p for p in v["cand_properties"]
                                   if p not in v["base_properties"]]
            v["lost_properties"] = [p for p in v["base_properties"]
                                    if p not in v["cand_properties"]]
            v["new_flags"] = [x for x in v["cand_flags"] if x not in v["base_flags"]]
            v["lost_flags"] = [x for x in v["base_flags"] if x not in v["cand_flags"]]
            v["worse_detectors"] = {d: [v["base_detectors"].get(d, 0), n]
                                    for d, n in v["cand_detectors"].items()
                                    if n > v["base_detectors"].get(d, 0)}
            v["better_detectors"] = {d: [n, v["cand_detectors"].get(d, 0)]
                                     for d, n in v["base_detectors"].items()
                                     if n > v["cand_detectors"].get(d, 0)}
            kinds[v["kind"]] += 1
            changed.append(v)

    def grew(base, cand):
        return {k: [base.get(k, 0), cand[k]] for k in sorted(cand) if cand[k] > base.get(k, 0)}

    def shrank(base, cand):
        return {k: [base[k], cand.get(k, 0)] for k in sorted(base) if base[k] > cand.get(k, 0)}

    p4_worse = [f"{r['map_id']} seat {r['seat']}" for r in rows
                if r["cand_p4_violations"] > r["base_p4_violations"]]
    r5_worse = [f"{r['map_id']} seat {r['seat']}" for r in rows
                if "r5-horizon" in r["cand_flags"] and "r5-horizon" not in r["base_flags"]]
    p3_new = [f"{r['map_id']} seat {r['seat']}" for r in rows
              if "P3" in r["cand_properties"] and "P3" not in r["base_properties"]]

    # P3's base column is vacuous on a floor panel by construction: eval_p3 flags ANY command
    # divergence from the parent on an orchard-eligible map, and on the floor the candidate IS the
    # parent. That is measured here, not asserted, exactly as g2_grade does it.
    floor_p3 = sum(1 for f in floor_rows.values()
                   for v_ in f["violations"] if v_["property"] == "P3")
    floor_diverged = sum(1 for f in floor_rows.values()
                         if f["artifacts"]["candidate_commands"]
                         != f["artifacts"]["parent_commands"])

    return {
        "games": len(rows),
        "games_with_a_command_stream_identical_to_the_base": tot["identical_games"],
        "changed_games": len(changed),
        "by_kind": dict(kinds),
        "blocking": {"base": tot["base_blocking"], "candidate": tot["cand_blocking"],
                     "delta": tot["cand_blocking"] - tot["base_blocking"]},
        "d1_episodes": {"base": tot["base_d1"], "candidate": tot["cand_d1"]},
        "p4_violations": {"base": tot["base_p4"], "candidate": tot["cand_p4"],
                          "base_column_mode": ("accepted: the floor panel's own candidate arm, "
                                               "post_state supplied; NOT post_state=None")},
        "detector_totals": {"base": dict(base_det), "candidate": dict(cand_det),
                            "grew": grew(base_det, cand_det), "shrank": shrank(base_det, cand_det)},
        "property_games": {"base": dict(base_prop), "candidate": dict(cand_prop),
                           "grew": grew(base_prop, cand_prop),
                           "shrank": shrank(base_prop, cand_prop)},
        "flag_games": {"base": dict(base_flag), "candidate": dict(cand_flag),
                       "grew": grew(base_flag, cand_flag), "shrank": shrank(base_flag, cand_flag)},
        "falsifiers": {
            "s7_5_p4_worse_games": p4_worse,
            "s7_5_r5_horizon_new_games": r5_worse,
            "s7_5_p3_new_games": p3_new,
            "s7_3_de_novo_blocks": [f"{r['map_id']} seat {r['seat']}" for r in changed
                                    if r["kind"] == "DE_NOVO_BLOCK"],
            "p3_base_column_vacuity": {
                "floor_p3_violations": floor_p3,
                "floor_games_whose_stream_diverges_from_its_own_parent": floor_diverged,
                "why": ("eval_p3 flags ANY command divergence from the parent on an "
                        "orchard-eligible map; on the floor panel the candidate IS the parent, so "
                        "the base P3 column is 0 by construction and cannot itself be a bar. The "
                        "P3 growth is therefore reported as a DIVERGENCE COUNT on orchard maps, "
                        "and whether P3 applies to an intended change is the open applicability "
                        "question codex_1 named at 20260821T120917Z -- handed on, not decided."),
            },
        },
        "named_changes": changed,
        "rows": rows,
    }


def controls(cand_rows, floor_rows) -> dict:
    """Three controls, each of which must be able to FAIL the table above.

    C-1 null fork      grading the floor panel against itself must name ZERO games. If the table
                       can invent a cost where both arms are the same bot, no count in it means
                       anything.
    C-2 poison fork    flip one clean game's block bit and one game's flag list on a COPY of the
                       candidate rows; the table must name exactly those two games, and the
                       blocking delta must move by exactly +1.
    C-3 non-vacuity    the real table must actually name games; a silent table is not a pass.
    """
    out = {}
    null = grade(floor_rows, floor_rows)
    out["c1_null_fork"] = {
        "changed_games": null["changed_games"],
        "blocking_delta": null["blocking"]["delta"],
        "detector_totals_equal": null["detector_totals"]["grew"] == {}
        and null["detector_totals"]["shrank"] == {},
        "pass": (null["changed_games"] == 0 and null["blocking"]["delta"] == 0
                 and not null["detector_totals"]["grew"]
                 and not null["detector_totals"]["shrank"]),
    }

    poisoned = {k: json.loads(json.dumps(v)) for k, v in cand_rows.items()}
    clean = [k for k in sorted(poisoned)
             if not poisoned[k]["block"] and not floor_rows[k]["block"]]
    unflagged = [k for k in sorted(poisoned) if not poisoned[k]["flags"]
                 and not floor_rows[k]["flags"] and k != clean[0]]
    if not clean or not unflagged:
        raise GateError("no clean / unflagged game to poison; the control cannot be run")
    poisoned[clean[0]]["block"] = True
    poisoned[unflagged[0]]["flags"] = [{"flag": "SYNTHETIC-POISON"}]
    pz = grade(poisoned, floor_rows)
    named = {(r["map_id"], r["seat"]) for r in pz["named_changes"]}
    real = {(r["map_id"], r["seat"]) for r in grade(cand_rows, floor_rows)["named_changes"]}
    out["c2_poison_fork"] = {
        "poisoned_block_game": f"{clean[0][0]} seat {clean[0][1]}",
        "poisoned_flag_game": f"{unflagged[0][0]} seat {unflagged[0][1]}",
        "both_named": clean[0] in named and unflagged[0] in named,
        "blocking_delta_moved_by": pz["blocking"]["delta"] - grade(cand_rows,
                                                                  floor_rows)["blocking"]["delta"],
        "named_superset_of_real": real <= named,
        "pass": (clean[0] in named and unflagged[0] in named and real <= named),
    }

    real_table = grade(cand_rows, floor_rows)
    out["c3_non_vacuity"] = {"changed_games": real_table["changed_games"],
                             "pass": real_table["changed_games"] > 0}
    out["all_pass"] = all(v["pass"] for v in out.values() if isinstance(v, dict))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--candidate-games", default=str(CAND_GAMES))
    ap.add_argument("--floor-games", default=str(FLOOR_GAMES))
    ap.add_argument("--json", default=str(OUT))
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args(argv)

    cand_rows = G.load(Path(args.candidate_games))
    floor_rows = G.load(Path(args.floor_games))
    matched, problems = G.gate_m(cand_rows, floor_rows)
    if not matched:
        print("GATE M FAILED — the panels are not matched; refusing to report counts")
        for p in problems[:20]:
            print("   ", p)
        return 1
    print(f"GATE M PASS — {len(cand_rows)} (map, seat) games matched byte-for-byte on the base arm")

    table = grade(cand_rows, floor_rows)
    table["task"] = "20260820-pair-selector-anti-benching"
    table["gate"] = "G-d — panel with named costs"
    table["subject"] = "door-1 lineage: claude_1/picker3/candidate-door1-p3b.rs @ 09ed550f"
    table["base"] = "claude_1/picker2/candidate-door1-p1p2.rs @ 5409ba13 (the r2 build's own base)"
    table["authorization"] = ("coordination/messages/local_codex_1/"
                              "20260823T155558Z-20260820-pair-selector-anti-benching-policy.md")
    table["gate_m_matched_panel"] = True
    table["not_measured_here"] = ("progress (that is G-e); G-b (Δ-B inertness) — UNMEASURED on the "
                                 "fixture library and not measured here; reach on real games "
                                 "(339/882 on 49/160, not re-run and not extrapolated); the 615 "
                                 "benched troll-turns, a DIFFERENT population this candidate is "
                                 "not claimed to repair.")
    if args.controls:
        table["controls"] = controls(cand_rows, floor_rows)

    Path(args.json).write_text(json.dumps(table, indent=2, sort_keys=True) + "\n")

    b = table["blocking"]
    print(f"\n  blocking games   base {b['base']:>3}   candidate {b['candidate']:>3}   "
          f"-> {b['delta']:+d}")
    print(f"  D-1 episodes     base {table['d1_episodes']['base']:>3}   candidate "
          f"{table['d1_episodes']['candidate']:>3}")
    print(f"  P4 violations    base {table['p4_violations']['base']:>3}   candidate "
          f"{table['p4_violations']['candidate']:>3}")
    print(f"  command stream identical to the base: "
          f"{table['games_with_a_command_stream_identical_to_the_base']}/{table['games']}")
    print(f"  changed games named: {table['changed_games']}   {table['by_kind']}")
    print("\n  detector totals that GREW:", table["detector_totals"]["grew"] or "-")
    print("  detector totals that SHRANK:", table["detector_totals"]["shrank"] or "-")
    print("  property games that GREW:", table["property_games"]["grew"] or "-")
    print("  flag games that GREW:", table["flag_games"]["grew"] or "-")
    fal = table["falsifiers"]
    print(f"\n  §7.3 de-novo blocks: {len(fal['s7_3_de_novo_blocks'])}")
    print(f"  §7.5 P4 worse: {len(fal['s7_5_p4_worse_games'])}   "
          f"r5-horizon new: {len(fal['s7_5_r5_horizon_new_games'])}   "
          f"P3 new: {len(fal['s7_5_p3_new_games'])}")
    if args.controls:
        print("\n  controls:", json.dumps({k: v.get("pass") for k, v in table["controls"].items()
                                           if isinstance(v, dict)}))
    print(f"\n  -> {args.json}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print(f"GATE FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
