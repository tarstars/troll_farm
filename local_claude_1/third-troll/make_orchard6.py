#!/usr/bin/env python3
"""Build "orchard 6": orchard 5 with the orchard on the cells ADJACENT to the tent (owner
2026-08-28 ~11:2xZ: "no lemon and plum are planted on adjacent to tent cells. It's the fastest
way to provide resources"). The orchard had kept the shack's doors free because a troll waiting
on a tree in a doorway once blocked its partner; now the doors ARE the orchard -- the far ones
first, water-side first -- and ONE door, the one nearest the enemy, is kept free for traffic and
for the fruit pick-up; ring-2 cells only fill what the adjacency lacks. The pick-up door is the
nearest free door without a tree.

THE EDIT: orchard 5's forty replacements followed by three more (the reserved door and the
adjacency-first order in `orchard_cells`; the pick-up door's preference in `orchard_candidates`).

    python3 local_claude_1/third-troll/make_orchard6.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_third_troll as mk       # noqa: E402
import make_three_heroes as th      # noqa: E402
import make_orchard as mo           # noqa: E402
import make_orchard2 as mo2         # noqa: E402
import make_orchard3 as mo3         # noqa: E402
import make_orchard4 as mo4         # noqa: E402
import make_orchard5 as mo5         # noqa: E402

REPL_RESERVED = dict(
    name="orchard_cells: the doors are the orchard; one door (nearest the enemy) stays free",
    anchor=(
        "                // Never on a door: a troll waiting on a tree in a doorway blocks the shack.\n"
        "                let doors = Self::doors_of(view, view.shacks[0]);\n"
    ),
    text=(
        "                // The doors are the orchard (owner 2026-08-28: adjacent to the tent is the\n"
        "                // fastest); one door -- the one nearest the enemy -- stays free for traffic\n"
        "                // and the fruit pick-up, so a troll waiting on a tree never blocks the shack.\n"
        "                let by_farness = Self::doors_by_farness(view);\n"
        "                let doors: Vec<Cell> = if by_farness.len() >= 2 {\n"
        "                    by_farness[by_farness.len() - 1..].to_vec()\n"
        "                } else {\n"
        "                    Vec::new()\n"
        "                };\n"
    ),
)

REPL_ADJACENT_FIRST = dict(
    name="orchard_cells: adjacent cells first",
    anchor=(
        "                        .map(|(cell, d)| {\n"
        "                            let wet = view.water.iter().any(|water| is_adjacent(*water, *cell));\n"
        "                            (*d, !wet, *cell)\n"
        "                        })\n"
        "                        .collect();\n"
        "                    near.sort();\n"
        "                    for (_, _, cell) in near {\n"
    ),
    text=(
        "                        .map(|(cell, d)| {\n"
        "                            let wet = view.water.iter().any(|water| is_adjacent(*water, *cell));\n"
        "                            let adjacent = is_adjacent(*cell, view.shacks[0]);\n"
        "                            (!adjacent, *d, !wet, *cell)\n"
        "                        })\n"
        "                        .collect();\n"
        "                    near.sort();\n"
        "                    for (_, _, _, cell) in near {\n"
    ),
)

REPL_NEAR_TYPE = dict(
    name="orchard_cells: the sort key's type",
    anchor="                    let mut near: Vec<(i32, bool, Cell)> = from_door\n",
    text="                    let mut near: Vec<(bool, i32, bool, Cell)> = from_door\n",
)

REPL_PICKUP = dict(
    name="orchard_candidates: the pick-up door prefers no tree",
    anchor=(
        "                        .filter_map(|door| from_unit.get(&door).map(|d| (*d, door)))\n"
        "                        .min()?\n"
        "                        .1;\n"
    ),
    text=(
        "                        .filter_map(|door| {\n"
        "                            from_unit\n"
        "                                .get(&door)\n"
        "                                .map(|d| (view.plant_at(door).is_some(), *d, door))\n"
        "                        })\n"
        "                        .min()?\n"
        "                        .2;\n"
    ),
)

ORCHARD6 = (REPL_RESERVED, REPL_ADJACENT_FIRST, REPL_NEAR_TYPE, REPL_PICKUP)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = (tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + mo2.ORCHARD2 + mo3.ORCHARD3
                       + mo4.ORCHARD4 + mo5.ORCHARD5 + ORCHARD6)
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard6-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard6-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard6-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard6-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard6.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("the third troll variant (b) 2/2/0/2", "candidate-third-troll-2202-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs"),
                        ("orchard 2", "candidate-orchard2-v6-instrument.rs"),
                        ("orchard 3", "candidate-orchard3-v6-instrument.rs"),
                        ("orchard 4", "candidate-orchard4-v6-instrument.rs"),
                        ("orchard 5", "candidate-orchard5-v6-instrument.rs")):
        mk.OTHERS_LIST.append((label, mk.REPO / "cgauto" / "submissions" / name))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = "orchard 6 (the third troll card: orchard 5 with the orchard on the cells adjacent to the tent, one door kept free)"
        report["bot"] = "orchard 5; the shack's doors are the orchard (far ones first, water-side first), the door nearest the enemy stays free; ring-2 fills the rest"
        report["edit"]["what"] = "forty-four replacements: orchard 5's forty + orchard 6's four"
        for path in (mk.REPORT, HERE / "results" / "build-orchard6.json"):
            path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        stray = HERE / "results" / "build-v6.json"
        if stray.exists():
            stray.unlink()
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except mk.BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
