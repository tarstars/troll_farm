#!/usr/bin/env python3
"""Build "orchard 5": orchard 4 with the return trip charged in the funding scores (owner
2026-08-28 ~11:0xZ, the game against migcuk: "trolls collect farthest from shack fruits").
The fruit score charged the walk TO the tree and the wait for a fruit but forgot the walk BACK
to the shack with it; the ore score forgot it too. A far tree with a fruit now beat a tree next
door whose fruit came a little later. Both scores now charge the way home.

THE EDIT: orchard 4's thirty-six replacements followed by four more in `fruit_candidates` and
`iron_candidates` (a walking-distance map home from the shack's doors; the way back in the score).

    python3 local_claude_1/third-troll/make_orchard5.py
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

REPL_FRUIT_HOME = dict(
    name="fruit_candidates: the walking distance home from the shack's doors",
    anchor=(
        "                let dist = bfs_distances(&view.walkable, &[unit.cell]);\n"
        "                for plant in &view.plants {\n"
        "                    if plant.kind != kind || plant.health <= 0 || !dist.contains_key(&plant.cell) {\n"
    ),
    text=(
        "                let dist = bfs_distances(&view.walkable, &[unit.cell]);\n"
        "                // The way home counts too (orchard 5, 2026-08-28): a fruit is worth its trip\n"
        "                // there AND back to the shack.\n"
        "                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])\n"
        "                    .into_iter()\n"
        "                    .filter(|cell| view.walkable.contains(cell))\n"
        "                    .collect();\n"
        "                let home = bfs_distances(&view.walkable, &doors);\n"
        "                for plant in &view.plants {\n"
        "                    if plant.kind != kind || plant.health <= 0 || !dist.contains_key(&plant.cell) {\n"
    ),
)

REPL_FRUIT_SCORE = dict(
    name="fruit_candidates: the way back in the score",
    anchor=(
        "                    let wait = (Self::ticks_until_fruit(view, plant) - travel).max(0);\n"
    ),
    text=(
        "                    let wait = (Self::ticks_until_fruit(view, plant) - travel).max(0);\n"
        "                    let back = home\n"
        "                        .get(&plant.cell)\n"
        "                        .map(|d| Self::ceil_div(*d + 1, unit.stats.movement_speed))\n"
        "                        .unwrap_or(100);\n"
    ),
)

REPL_FRUIT_SCORE2 = dict(
    name="fruit_candidates: the score line",
    anchor="                        score: base_score - (travel + wait) as f64,\n",
    text="                        score: base_score - (travel + wait + back) as f64,\n",
)

REPL_IRON_HOME = dict(
    name="iron_candidates: the way back in the score",
    anchor=(
        "                let dist = bfs_distances(&view.walkable, &[unit.cell]);\n"
        "                for iron in &view.iron {\n"
        "                    for cell in ortho_neighbors(*iron) {\n"
        "                        if !view.walkable.contains(&cell) {\n"
        "                            continue;\n"
        "                        }\n"
        "                        if let Some(d) = dist.get(&cell) {\n"
        "                            out.push(Candidate {\n"
        "                                command: format!(\"MOVE {} {} {}\", unit.id, cell.0, cell.1),\n"
        "                                score: base_score - *d as f64,\n"
    ),
    text=(
        "                let dist = bfs_distances(&view.walkable, &[unit.cell]);\n"
        "                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])\n"
        "                    .into_iter()\n"
        "                    .filter(|cell| view.walkable.contains(cell))\n"
        "                    .collect();\n"
        "                let home = bfs_distances(&view.walkable, &doors);\n"
        "                for iron in &view.iron {\n"
        "                    for cell in ortho_neighbors(*iron) {\n"
        "                        if !view.walkable.contains(&cell) {\n"
        "                            continue;\n"
        "                        }\n"
        "                        if let Some(d) = dist.get(&cell) {\n"
        "                            // The way home counts too (orchard 5).\n"
        "                            let back = home.get(&cell).copied().unwrap_or(100);\n"
        "                            out.push(Candidate {\n"
        "                                command: format!(\"MOVE {} {} {}\", unit.id, cell.0, cell.1),\n"
        "                                score: base_score - (*d + back) as f64,\n"
    ),
)

ORCHARD5 = (REPL_FRUIT_HOME, REPL_FRUIT_SCORE, REPL_FRUIT_SCORE2, REPL_IRON_HOME)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = (tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + mo2.ORCHARD2 + mo3.ORCHARD3
                       + mo4.ORCHARD4 + ORCHARD5)
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard5-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard5-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard5-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard5-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard5.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("the third troll variant (b) 2/2/0/2", "candidate-third-troll-2202-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs"),
                        ("orchard 2", "candidate-orchard2-v6-instrument.rs"),
                        ("orchard 3", "candidate-orchard3-v6-instrument.rs"),
                        ("orchard 4", "candidate-orchard4-v6-instrument.rs")):
        mk.OTHERS_LIST.append((label, mk.REPO / "cgauto" / "submissions" / name))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = "orchard 5 (the third troll card: orchard 4 with the way home charged in the fruit and ore scores)"
        report["bot"] = "orchard 4; a fruit or ore trip is scored there and back, so near sources win over far ones"
        report["edit"]["what"] = "forty replacements: orchard 4's thirty-six + orchard 5's four"
        for path in (mk.REPORT, HERE / "results" / "build-orchard5.json"):
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
