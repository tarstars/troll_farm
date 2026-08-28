#!/usr/bin/env python3
"""Build "orchard 2": the orchard after the owner's read of the game against ghhttt (2026-08-28
~09:4xZ: "ore is extremely far ... either decline third troll, or decrease its properties";
"enemy started to attack our orchard, we should stop planting"; "one lemon and one plum is
enough" -> agreed at 2 + 1; "ok"). Card `coordination/tasks/20260828-third-troll.md`, design
round 4.

THE RULE (owner, plain words), on top of the orchard (make_orchard.py):
  1. The third troll's chop follows the iron. Iron costs n + chop^2 and a troll carries two per
     trip, so far iron means a cheaper axe: chop 3 with the nearest iron within 5 steps on foot
     of our doors, chop 2 within 10, chop 1 within 16, and NO third troll (and no orchard)
     beyond -- iron already in the shack counts against the bill (enough iron in stock for a
     chop means that chop regardless of distance). A map without iron charges no iron for a
     troll (the referee's rule the bot already mirrors), so there the third troll is 2/3/0/3.
  2. The orchard raided: while the third troll is wanted we never fell an orchard tree, so an
     orchard tree seen last turn and gone this turn was felled by the enemy -- planting stops
     for the rest of the game (the trees still standing are harvested; nothing is replanted).
     One remembered flag in the bot.
  3. The orchard is two lemons and one plum (was four and two).

THE EDIT: the orchard's twenty-one replacements followed by eight more, each anchored on text
that occurs exactly once in BOTH files after the twenty-one:
  22. the orchard's size 4+2 -> 2+1;
  23. two fields on the bot (`orchard_seen`, `orchard_raided`) and 24. their initial values;
  25. `iron_steps` + `third_troll_for` in YamoBot (the chop that follows the iron);
  26. `commands`: the wanted third troll is `third_troll_for`; none -> no third troll;
  27. `third_reachable` prices the wanted troll;
  28. `orchard_protected`: only while a third troll is wanted on this map;
  29. `commands`: the raid check each turn, and 30. `orchard_candidates` stops when raided.

    python3 local_claude_1/third-troll/make_orchard2.py
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

REPL_SIZE = dict(
    name="the orchard's size: 4 lemons + 2 plums -> 2 + 1",
    anchor=(
        "            const ORCHARD_LEMONS: usize = 4;\n"
        "            const ORCHARD_PLUMS: usize = 2;\n"
    ),
    text=(
        "            const ORCHARD_LEMONS: usize = 2;\n"
        "            const ORCHARD_PLUMS: usize = 1;\n"
    ),
)

REPL_FIELDS = dict(
    name="YamoBot: the orchard's memory (orchard_seen, orchard_raided)",
    anchor="            regeneration_commitments: BTreeMap<i32, PlantKind>,\n",
    text=(
        "            regeneration_commitments: BTreeMap<i32, PlantKind>,\n"
        "            // The orchard's memory: the orchard cells that held our tree last turn, and\n"
        "            // whether the enemy has felled one (then planting stops for good).\n"
        "            orchard_seen: BTreeSet<Cell>,\n"
        "            orchard_raided: bool,\n"
    ),
)

REPL_INIT = dict(
    name="YamoBot::with_opening_policy: the new fields' initial values",
    anchor="                    regeneration_commitments: BTreeMap::new(),\n",
    text=(
        "                    regeneration_commitments: BTreeMap::new(),\n"
        "                    orchard_seen: BTreeSet::new(),\n"
        "                    orchard_raided: false,\n"
    ),
)

REPL_IRON = dict(
    name="iron_steps + third_troll_for: the third troll's chop follows the iron",
    anchor="            fn fallback_second_troll() -> Stats {\n",
    text=(
        "            // The third troll's chop follows the iron (owner 2026-08-28): iron costs n + chop^2\n"
        "            // and a troll carries two per trip, so far iron means a cheaper axe -- chop 3 with\n"
        "            // the nearest iron within 5 steps on foot of our doors, 2 within 10, 1 within 16,\n"
        "            // none beyond; iron already in the shack counts against the bill. A map without\n"
        "            // iron charges no iron (the referee's rule `can_train` mirrors): chop 3 there.\n"
        "            const IRON_STEPS_FOR_CHOP: [(i32, i32); 3] = [(5, 3), (10, 2), (16, 1)];\n"
        "            fn iron_steps(view: &GameState) -> Option<i32> {\n"
        "                let doors = MoisanBot::doors_of(view, view.shacks[0]);\n"
        "                let from_doors = bfs_distances(&view.walkable, &doors);\n"
        "                view.iron\n"
        "                    .iter()\n"
        "                    .flat_map(|iron| ortho_neighbors(*iron))\n"
        "                    .filter_map(|cell| from_doors.get(&cell).copied())\n"
        "                    .min()\n"
        "            }\n"
        "            fn third_troll_for(view: &GameState) -> Option<Stats> {\n"
        "                if view.iron.is_empty() {\n"
        "                    return Some(Self::third_troll());\n"
        "                }\n"
        "                let steps = Self::iron_steps(view);\n"
        "                let stock = view.inventories[0][IRON];\n"
        "                for (limit, chop) in Self::IRON_STEPS_FOR_CHOP {\n"
        "                    let needed = 2 + chop * chop - stock;\n"
        "                    if needed <= 0 || steps.is_some_and(|s| s <= limit) {\n"
        "                        return Some(Stats {\n"
        "                            movement_speed: 2,\n"
        "                            carry_capacity: 3,\n"
        "                            harvest_power: 0,\n"
        "                            chop_power: chop,\n"
        "                        });\n"
        "                    }\n"
        "                }\n"
        "                None\n"
        "            }\n"
        "            fn fallback_second_troll() -> Stats {\n"
    ),
)

REPL_WANTED = dict(
    name="commands: the wanted third troll is third_troll_for; none -> no third troll",
    anchor=(
        "                let third_wanted =\n"
        "                    own_trolls == 2 && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON;\n"
    ),
    text=(
        "                let third_troll = Self::third_troll_for(view);\n"
        "                let third_wanted = own_trolls == 2\n"
        "                    && third_troll.is_some()\n"
        "                    && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON;\n"
    ),
)

REPL_DESIRED2 = dict(
    name="commands: desired = the wanted third troll",
    anchor=(
        "                let desired = if own_trolls >= 2 {\n"
        "                    Self::third_troll()\n"
        "                } else {\n"
    ),
    text=(
        "                let desired = if own_trolls >= 2 {\n"
        "                    third_troll.unwrap_or_else(Self::third_troll)\n"
        "                } else {\n"
    ),
)

REPL_REACH2 = dict(
    name="third_reachable prices the wanted troll",
    anchor="                    let cost = training_cost(2, Self::third_troll().tuple());\n",
    text="                    let cost = training_cost(2, third_troll.unwrap_or_else(Self::third_troll).tuple());\n",
)

REPL_PROTECT2 = dict(
    name="orchard_protected: only while a third troll is wanted on this map",
    anchor=(
        "                trolls < 3 && TOTAL_TURNS - view.turn >= YamoBot::THIRD_TROLL_HORIZON\n"
    ),
    text=(
        "                trolls < 3\n"
        "                    && TOTAL_TURNS - view.turn >= YamoBot::THIRD_TROLL_HORIZON\n"
        "                    && YamoBot::third_troll_for(view).is_some()\n"
    ),
)

REPL_RAID = dict(
    name="commands: the raid check each turn",
    anchor="                self.enforce_training_deadline(view);\n",
    text=(
        "                self.enforce_training_deadline(view);\n"
        "                // The orchard raided (owner 2026-08-28): while the third troll is wanted we never\n"
        "                // fell an orchard tree, so one seen last turn and gone now was the enemy's doing;\n"
        "                // planting stops for the rest of the game.\n"
        "                let standing: BTreeSet<Cell> = MoisanBot::orchard_cells(view)\n"
        "                    .into_iter()\n"
        "                    .filter(|cell| MoisanBot::orchard_tree(view, *cell))\n"
        "                    .collect();\n"
        "                if MoisanBot::orchard_protected(view)\n"
        "                    && self.orchard_seen.iter().any(|cell| !standing.contains(cell))\n"
        "                {\n"
        "                    self.orchard_raided = true;\n"
        "                }\n"
        "                self.orchard_seen = standing;\n"
    ),
)

REPL_STOP = dict(
    name="orchard_candidates: no planting once raided",
    anchor=(
        "                if !MoisanBot::orchard_protected(view)\n"
        "                    || MoisanBot::orchard_unit(view) != Some(unit.id)\n"
        "                {\n"
    ),
    text=(
        "                if !MoisanBot::orchard_protected(view)\n"
        "                    || self.orchard_raided\n"
        "                    || MoisanBot::orchard_unit(view) != Some(unit.id)\n"
        "                {\n"
    ),
)

ORCHARD2 = (REPL_SIZE, REPL_FIELDS, REPL_INIT, REPL_IRON, REPL_WANTED, REPL_DESIRED2, REPL_REACH2,
            REPL_PROTECT2, REPL_RAID, REPL_STOP)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + ORCHARD2
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard2-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard2-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard2-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard2-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard2.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("the third troll variant (b) 2/2/0/2", "candidate-third-troll-2202-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs")):
        mk.OTHERS_LIST.append((label, mk.REPO / "cgauto" / "submissions" / name))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = ("orchard 2 (the third troll card, design round 4, owner 2026-08-28 ~09:4xZ after the "
                          "game against ghhttt: the chop follows the iron, stop planting when raided, 2 + 1; 'ok')")
        report["bot"] = ("the orchard with the third troll's chop set by the iron's walking distance (3/2/1/none), "
                         "planting stopped for good once the enemy fells an orchard tree, two lemons and one plum")
        report["edit"]["what"] = "thirty-one replacements: the orchard's twenty-one + orchard 2's ten"
        for path in (mk.REPORT, HERE / "results" / "build-orchard2.json"):
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
