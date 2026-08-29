#!/usr/bin/env python3
"""Build "orchard 7": orchard 6 with the three fixes from the owner's read of game 900722253
(2026-08-28 ~18:3xZ): planting first had spent the lemons below the cheapest second-troll bill,
the champion's turn-35 deadline abandoned the opening for good (no second troll in 18 of 320
games, the troll chopping from turn 35), and a plum went on a cell 9 steps around the water.
  1. The deadline never abandons: with nothing affordable at turn 35 the bot takes the strongest
     affordable troll, else keeps waiting for the fallback and keeps collecting (the floor's rule).
  2. Planting keeps a reserve of 2 lemons and 2 plums until the second troll exists (the cheapest
     bill), so the opening can never be starved by the orchard.
  3. An orchard cell must be within ORCHARD_REACH steps on foot of the tent itself; a tree with no
     such cell is skipped, never walked across the map.

THE EDIT: orchard 6's forty-four replacements followed by four more.

    python3 local_claude_1/third-troll/make_orchard7.py
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
import make_orchard6 as mo6         # noqa: E402

REPL_NO_ABANDON = dict(
    name="enforce_training_deadline: never abandon -- the strongest affordable, else keep waiting",
    anchor=(
        "                self.desired_second = Self::strongest_affordable(view, self.opening_policy);\n"
        "                if self.desired_second.is_none() {\n"
        "                    self.opening_abandoned = true;\n"
        "                }\n"
    ),
    text=(
        "                // Never abandon (orchard 7, 2026-08-28): with nothing affordable at the deadline\n"
        "                // the bot keeps waiting for the fallback troll and keeps collecting -- an\n"
        "                // abandoned opening meant no second troll ever and a lone troll chopping.\n"
        "                self.desired_second = Some(\n"
        "                    Self::strongest_affordable(view, self.opening_policy).unwrap_or_else(|| {\n"
        "                        Self::opening_objective(view, Self::fallback_second_troll())\n"
        "                    }),\n"
        "                );\n"
    ),
)

REPL_RESERVE = dict(
    name="orchard_candidates: a reserve of 2 lemons and 2 plums until the second troll exists",
    anchor="                if unit.total_carried() > 0 || train_now || view.inventories[0][item] <= 0 {\n",
    text=(
        "                // The cheapest second troll costs 2 of each fruit: keep that much until it exists.\n"
        "                let reserve = if view.units.iter().filter(|u| u.player == 0).count() < 2 { 2 } else { 0 };\n"
        "                if unit.total_carried() > 0 || train_now || view.inventories[0][item] <= reserve {\n"
    ),
)

REPL_TENT_REACH = dict(
    name="orchard_cells: a cell must be within reach of the tent itself",
    anchor="                let by_farness = Self::doors_by_farness(view);\n",
    text=(
        "                // Within reach of the tent itself (orchard 7): never a cell reached only by a\n"
        "                // walk around the water; a tree with no such cell is skipped.\n"
        "                let from_tent = bfs_distances(&view.walkable, &Self::doors_of(view, view.shacks[0]));\n"
        "                let by_farness = Self::doors_by_farness(view);\n"
    ),
)

REPL_TENT_FILTER = dict(
    name="orchard_cells: the reach filter",
    anchor=(
        "                        .filter(|(cell, d)| {\n"
        "                            **d <= Self::ORCHARD_REACH\n"
    ),
    text=(
        "                        .filter(|(cell, d)| {\n"
        "                            **d <= Self::ORCHARD_REACH\n"
        "                                && from_tent.get(cell).is_some_and(|t| *t + 1 <= Self::ORCHARD_REACH)\n"
    ),
)

ORCHARD7 = (REPL_NO_ABANDON, REPL_RESERVE, REPL_TENT_REACH, REPL_TENT_FILTER)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = (tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + mo2.ORCHARD2 + mo3.ORCHARD3
                       + mo4.ORCHARD4 + mo5.ORCHARD5 + mo6.ORCHARD6 + ORCHARD7)
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard7-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard7-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard7-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard7-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard7.diff"
    for n in ("third-troll", "third-troll-2202", "three-heroes", "orchard", "orchard2", "orchard3",
              "orchard4", "orchard5", "orchard6"):
        mk.OTHERS_LIST.append((n, mk.REPO / "cgauto" / "submissions" / f"candidate-{n}-v6-instrument.rs"))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = "orchard 7 (the third troll card: orchard 6 + never abandon the opening, a fruit reserve for the second troll, orchard cells within reach of the tent)"
        report["bot"] = "orchard 6; the deadline keeps waiting instead of abandoning; planting keeps 2 lemons + 2 plums until the second troll; orchard cells within 2 steps of the tent"
        report["edit"]["what"] = "forty-eight replacements: orchard 6's forty-four + orchard 7's four"
        for path in (mk.REPORT, HERE / "results" / "build-orchard7.json"):
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
