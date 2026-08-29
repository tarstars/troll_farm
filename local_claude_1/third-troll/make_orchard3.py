#!/usr/bin/env python3
"""Build "orchard 3": orchard 2 with the owner's two further rules (2026-08-28 ~10:1xZ):
  1. PLANT FIRST. "lemon was planted like on 90th game step. It's late. We are to start with
     planting lemon, lemon, plum near the shack and then start collecting resources" -- the
     starting troll plants the orchard from the first turns (turn 1 keeps the training check),
     from the starting stock, no reserve; funding (the second troll's bill, then the third's)
     comes after the orchard stands.
  2. CONCURRENT PICKING. "taking depleting resources with focus on one resource makes it longer.
     What do you think in concurrent picking lemon, plum, ore?" -- each troll works a different
     resource of the bill: the missing items ordered by deficit, the i-th own troll (by id) takes
     the i-th; when one kind is all that is left, everybody goes for it. Iron is mined while
     fruit is harvested instead of after; a lemon tree's regrowth is no longer the clock.

THE EDIT: orchard 2's thirty-one replacements followed by two more:
  32. `orchard_candidates`  -- planting from the first turns, no reserve (the "after the second
                               troll" gate of the orchard is removed);
  33. `early_candidates`    -- the bill's missing items split between the trolls by deficit.

    python3 local_claude_1/third-troll/make_orchard3.py
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

REPL_PLANT_FIRST = dict(
    name="orchard_candidates: plant first, from the first turns, no reserve",
    anchor=(
        "                // After the second troll only (its bill and its turns come first).\n"
        "                if view.units.iter().filter(|unit| unit.player == 0).count() < 2 {\n"
        "                    return None;\n"
        "                }\n"
        "                let (cell, kind) = *MoisanBot::orchard_plan(view).first()?;\n"
    ),
    text=(
        "                // Plant first (owner 2026-08-28): the orchard goes in from the first turns,\n"
        "                // from the starting stock, before any collecting.\n"
        "                let (cell, kind) = *MoisanBot::orchard_plan(view).first()?;\n"
    ),
)

REPL_CONCURRENT = dict(
    name="early_candidates: each troll works a different resource of the bill",
    anchor=(
        "                let fetches_fruit = unit.stats.harvest_power > 0;\n"
        "                let fetches_iron = true;\n"
        "                for item in [PLUM, LEMON, APPLE, IRON] {\n"
        "                    if cost[item] <= view.inventories[0][item] {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if (item == IRON && !fetches_iron) || (item != IRON && !fetches_fruit) {\n"
        "                        continue;\n"
        "                    }\n"
    ),
    text=(
        "                let fetches_fruit = unit.stats.harvest_power > 0;\n"
        "                // Concurrent picking (owner 2026-08-28): the missing items ordered by deficit,\n"
        "                // the i-th own troll (by id) takes the i-th; one kind left -> everybody.\n"
        "                let mut missing: Vec<usize> = [PLUM, LEMON, APPLE, IRON]\n"
        "                    .into_iter()\n"
        "                    .filter(|&item| {\n"
        "                        cost[item] > view.inventories[0][item] && (item == IRON || fetches_fruit)\n"
        "                    })\n"
        "                    .collect();\n"
        "                missing.sort_by_key(|&item| (-(cost[item] - view.inventories[0][item]), item));\n"
        "                let mut own: Vec<i32> =\n"
        "                    view.units.iter().filter(|u| u.player == 0).map(|u| u.id).collect();\n"
        "                own.sort();\n"
        "                let rank = own.iter().position(|id| *id == unit.id).unwrap_or(0);\n"
        "                let mine: Vec<usize> = if missing.len() > 1 && own.len() > 1 {\n"
        "                    vec![missing[rank % missing.len()]]\n"
        "                } else {\n"
        "                    missing.clone()\n"
        "                };\n"
        "                for item in [PLUM, LEMON, APPLE, IRON] {\n"
        "                    if !mine.contains(&item) {\n"
        "                        continue;\n"
        "                    }\n"
    ),
)

ORCHARD3 = (REPL_PLANT_FIRST, REPL_CONCURRENT)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + mo2.ORCHARD2 + ORCHARD3
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard3-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard3-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard3-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard3-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard3.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("the third troll variant (b) 2/2/0/2", "candidate-third-troll-2202-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs"),
                        ("orchard 2", "candidate-orchard2-v6-instrument.rs")):
        mk.OTHERS_LIST.append((label, mk.REPO / "cgauto" / "submissions" / name))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = ("orchard 3 (the third troll card, design round 5, owner 2026-08-28 ~10:1xZ: plant "
                          "first -- lemon, lemon, plum by the shack, then collect; each troll on a different "
                          "resource of the bill)")
        report["bot"] = ("orchard 2 with the orchard planted from the first turns (no reserve) and the bill's "
                         "missing items split between the trolls by deficit")
        report["edit"]["what"] = "thirty-three replacements: orchard 2's thirty-one + orchard 3's two"
        for path in (mk.REPORT, HERE / "results" / "build-orchard3.json"):
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
