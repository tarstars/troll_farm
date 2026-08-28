#!/usr/bin/env python3
"""Build "the orchard": three heroes plus an orchard at the far gate (owner 2026-08-28 ~09:0xZ
"let's do orchard"; amended "we are to use gates logic ... plant farm near one gate and it should
be the farthest gate from the enemy camp"; design accepted "ok"). Card
`coordination/tasks/20260828-third-troll.md`, design round 3 (the orchard card).

THE RULE (owner, plain words), on top of three heroes (harvest-1 second troll; both trolls collect
the third troll's bill and nobody chops until the 2/3/0/3 third troll is trained or unreachable):
  1. The gate: our shack's doors are its walkable orthogonal neighbours; the orchard's gate is
     the door with the largest WALKING distance from the enemy's doors (unreachable = farthest).
  2. The orchard: the first six free cells within two steps on foot of the gate (the gate cell
     included; both shacks excluded), nearest first, water-side first (a water-side lemon fruits
     in 12 turns instead of 32 and regrows every 3 instead of 8); if the gate has fewer than six,
     the next-farthest doors' cells follow. Four lemons and two plums; a lemon or plum already
     standing on an orchard cell counts.
  3. The starting troll plants (PICK the fruit beside the shack -> walk -> PLANT), from turn 2 on
     (turn 1 stays the training check), whenever it carries nothing, the shack holds the fruit
     beyond the reserve (5 plums / 5 lemons kept for the second troll's bill until it is trained;
     no reserve after), and the third troll is still wanted (fewer than three trolls, >= 100 turns
     left). A tree the opponent fells is replanted by the same rule (stateless).
  4. No own troll fells an orchard tree while the third troll is wanted; after it (or after the
     horizon) they are wood like any tree.
  5. The dance fix: a troll walking to a fruit tree no longer reserves the tree (the MOVE carries
     no target), so two trolls may head for the same tree and the second harvests after the
     first instead of freezing with nothing to do; the move resolver still keeps them off one
     cell.

THE EDIT: the sixteen replacements of three heroes followed by five more, each anchored on text
that occurs exactly once in BOTH files after the sixteen:
  17. `chop_candidates`     -- skip a protected orchard tree;
  18. helpers in MoisanBot  -- orchard_gate, orchard_cells, orchard_plan, orchard_tree,
                               orchard_protected, orchard_unit;
  19. `fruit_candidates`    -- the dance fix (MOVE to a fruit tree carries Target::None);
  20. `orchard_candidates`  -- in YamoBot: the starter's planting turn;
  21. `commands` hook       -- the orchard owns the starter's turn when it has something to plant.

Outputs (same chain as `make_third_troll.py`):
  local_claude_1/third-troll/champion-orchard-v6-instrument.rs (+ .sha256)
  local_claude_1/third-troll/orchard-readable.rs (+ .sha256)
  cgauto/submissions/candidate-orchard-v6-instrument.rs (+ .sha256)
  readable/diffs/orchard.diff, readable/reports/candidate-orchard-v6-instrument.round-trip.json

    python3 local_claude_1/third-troll/make_orchard.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_third_troll as mk       # noqa: E402
import make_three_heroes as th      # noqa: E402

REPL_CHOP_SKIP = dict(
    name="chop_candidates: skip a protected orchard tree",
    anchor=(
        "                for plant in &view.plants {\n"
        "                    if plant.health <= 0 || !from_unit.contains_key(&plant.cell) {\n"
        "                        continue;\n"
        "                    }\n"
        "                    let travel_turns =\n"
    ),
    text=(
        "                for plant in &view.plants {\n"
        "                    if plant.health <= 0 || !from_unit.contains_key(&plant.cell) {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if Self::orchard_protected(view) && Self::orchard_tree(view, plant.cell) {\n"
        "                        continue;\n"
        "                    }\n"
        "                    let travel_turns =\n"
    ),
)

REPL_HELPERS = dict(
    name="orchard helpers (impl MoisanBot), before wait()",
    anchor="            fn wait() -> Candidate {\n",
    text=(
        "            // --------------------------------------------------------------------------\n"
        "            // The orchard (owner 2026-08-28): four lemons and two plums at the far gate.\n"
        "            //\n"
        "            // The gate is the door of our shack (a walkable orthogonal neighbour) with the\n"
        "            // largest walking distance from the enemy's doors. The orchard cells are the first\n"
        "            // six free cells within two steps on foot of the gate (the gate included, the\n"
        "            // shacks excluded), nearest first, water-side first; if the gate has fewer, the\n"
        "            // next-farthest doors' cells follow. Planted by the starting troll while the third\n"
        "            // troll is wanted; protected from our own axes for as long.\n"
        "            // --------------------------------------------------------------------------\n"
        "            const ORCHARD_LEMONS: usize = 4;\n"
        "            const ORCHARD_PLUMS: usize = 2;\n"
        "            const ORCHARD_REACH: i32 = 2;\n"
        "            fn doors_of(view: &GameState, shack: Cell) -> Vec<Cell> {\n"
        "                ortho_neighbors(shack)\n"
        "                    .into_iter()\n"
        "                    .filter(|cell| view.walkable.contains(cell))\n"
        "                    .collect()\n"
        "            }\n"
        "            // Our doors, farthest from the enemy first (walking distance; unreachable = farthest).\n"
        "            fn doors_by_farness(view: &GameState) -> Vec<Cell> {\n"
        "                let from_enemy = bfs_distances(&view.walkable, &Self::doors_of(view, view.shacks[1]));\n"
        "                let mut doors = Self::doors_of(view, view.shacks[0]);\n"
        "                doors.sort_by_key(|door| {\n"
        "                    (-from_enemy.get(door).copied().unwrap_or(i32::MAX), *door)\n"
        "                });\n"
        "                doors\n"
        "            }\n"
        "            fn orchard_gate(view: &GameState) -> Option<Cell> {\n"
        "                Self::doors_by_farness(view).first().copied()\n"
        "            }\n"
        "            fn orchard_cells(view: &GameState) -> Vec<Cell> {\n"
        "                let size = Self::ORCHARD_LEMONS + Self::ORCHARD_PLUMS;\n"
        "                let mut cells: Vec<Cell> = Vec::new();\n"
        "                for door in Self::doors_by_farness(view) {\n"
        "                    if cells.len() >= size {\n"
        "                        break;\n"
        "                    }\n"
        "                    let from_door = bfs_distances(&view.walkable, &[door]);\n"
        "                    let mut near: Vec<(i32, bool, Cell)> = from_door\n"
        "                        .iter()\n"
        "                        .filter(|(cell, d)| {\n"
        "                            **d <= Self::ORCHARD_REACH\n"
        "                                && **cell != view.shacks[0]\n"
        "                                && **cell != view.shacks[1]\n"
        "                                && !cells.contains(cell)\n"
        "                        })\n"
        "                        .map(|(cell, d)| {\n"
        "                            let wet = view.water.iter().any(|water| is_adjacent(*water, *cell));\n"
        "                            (*d, !wet, *cell)\n"
        "                        })\n"
        "                        .collect();\n"
        "                    near.sort();\n"
        "                    for (_, _, cell) in near {\n"
        "                        if cells.len() >= size {\n"
        "                            break;\n"
        "                        }\n"
        "                        cells.push(cell);\n"
        "                    }\n"
        "                }\n"
        "                cells\n"
        "            }\n"
        "            // The empty orchard cells with the kind to plant on each: lemons first, then plums,\n"
        "            // minus the lemon and plum trees already standing on orchard cells.\n"
        "            fn orchard_plan(view: &GameState) -> Vec<(Cell, PlantKind)> {\n"
        "                let cells = Self::orchard_cells(view);\n"
        "                let standing = |kind: PlantKind| {\n"
        "                    cells\n"
        "                        .iter()\n"
        "                        .filter(|cell| {\n"
        "                            view.plant_at(**cell).is_some_and(|index| {\n"
        "                                view.plants[index].kind == kind && view.plants[index].health > 0\n"
        "                            })\n"
        "                        })\n"
        "                        .count()\n"
        "                };\n"
        "                let mut lemons = Self::ORCHARD_LEMONS.saturating_sub(standing(PlantKind::Lemon));\n"
        "                let mut plums = Self::ORCHARD_PLUMS.saturating_sub(standing(PlantKind::Plum));\n"
        "                let mut plan = Vec::new();\n"
        "                for cell in cells {\n"
        "                    if view.plant_at(cell).is_some() {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if lemons > 0 {\n"
        "                        lemons -= 1;\n"
        "                        plan.push((cell, PlantKind::Lemon));\n"
        "                    } else if plums > 0 {\n"
        "                        plums -= 1;\n"
        "                        plan.push((cell, PlantKind::Plum));\n"
        "                    }\n"
        "                }\n"
        "                plan\n"
        "            }\n"
        "            fn orchard_tree(view: &GameState, cell: Cell) -> bool {\n"
        "                Self::orchard_cells(view).contains(&cell)\n"
        "                    && view.plant_at(cell).is_some_and(|index| {\n"
        "                        matches!(view.plants[index].kind, PlantKind::Lemon | PlantKind::Plum)\n"
        "                            && view.plants[index].health > 0\n"
        "                    })\n"
        "            }\n"
        "            // While the third troll is wanted: fewer than three own trolls and the horizon open.\n"
        "            fn orchard_protected(view: &GameState) -> bool {\n"
        "                let trolls = view.units.iter().filter(|unit| unit.player == 0).count();\n"
        "                trolls < 3 && TOTAL_TURNS - view.turn >= YamoBot::THIRD_TROLL_HORIZON\n"
        "            }\n"
        "            // The planting troll: the starting troll (the harvester with the lowest id).\n"
        "            fn orchard_unit(view: &GameState) -> Option<i32> {\n"
        "                view.units\n"
        "                    .iter()\n"
        "                    .filter(|unit| unit.player == 0 && unit.stats.harvest_power > 0)\n"
        "                    .map(|unit| unit.id)\n"
        "                    .min()\n"
        "            }\n"
        "            fn wait() -> Candidate {\n"
    ),
)

REPL_DANCE = dict(
    name="fruit_candidates: the dance fix -- a walk to a fruit tree reserves no target",
    anchor=(
        "                    out.push(Candidate {\n"
        "                        command: format!(\"MOVE {} {} {}\", unit.id, plant.cell.0, plant.cell.1),\n"
        "                        score: base_score - (travel + wait) as f64,\n"
        "                        target: Target::Tree(plant.cell),\n"
        "                    });\n"
    ),
    text=(
        "                    // No target on the walk (the dance fix, 2026-08-28): two trolls may head\n"
        "                    // for the same tree and the second harvests after the first instead of\n"
        "                    // freezing; the move resolver still keeps them off one cell.\n"
        "                    out.push(Candidate {\n"
        "                        command: format!(\"MOVE {} {} {}\", unit.id, plant.cell.0, plant.cell.1),\n"
        "                        score: base_score - (travel + wait) as f64,\n"
        "                        target: Target::None,\n"
        "                    });\n"
    ),
)

REPL_ORCHARD_TURN = dict(
    name="orchard_candidates (impl YamoBot), before endgame()",
    anchor="            fn endgame(view: &GameState) -> bool {\n",
    text=(
        "            // --------------------------------------------------------------------------\n"
        "            // The orchard: the starting troll's planting turn. Returns its whole candidate\n"
        "            // list when it has a tree to plant and the shack can spare the fruit; None when\n"
        "            // it carries something (banked the normal way first), when nothing is missing,\n"
        "            // or when the third troll is no longer wanted.\n"
        "            // --------------------------------------------------------------------------\n"
        "            fn orchard_candidates(\n"
        "                &mut self,\n"
        "                view: &GameState,\n"
        "                unit: &Unit,\n"
        "                train_now: bool,\n"
        "            ) -> Option<Vec<Candidate>> {\n"
        "                if !MoisanBot::orchard_protected(view)\n"
        "                    || MoisanBot::orchard_unit(view) != Some(unit.id)\n"
        "                {\n"
        "                    return None;\n"
        "                }\n"
        "                let (cell, kind) = *MoisanBot::orchard_plan(view).first()?;\n"
        "                let item = if kind == PlantKind::Lemon { LEMON } else { PLUM };\n"
        "                let trolls = view.units.iter().filter(|unit| unit.player == 0).count();\n"
        "                let reserve = if trolls < 2 { 5 } else { 0 };\n"
        "                let act = |command: String, target: Target| Candidate {\n"
        "                    command,\n"
        "                    score: 50_000.0,\n"
        "                    target,\n"
        "                };\n"
        "                let mut out = vec![MoisanBot::wait()];\n"
        "                if unit.carry[item] > 0 {\n"
        "                    out.push(if unit.cell == cell {\n"
        "                        act(format!(\"PLANT {} {}\", unit.id, kind.as_str()), Target::Cell(cell))\n"
        "                    } else {\n"
        "                        act(format!(\"MOVE {} {} {}\", unit.id, cell.0, cell.1), Target::Cell(cell))\n"
        "                    });\n"
        "                    self.regeneration_commitments.remove(&unit.id);\n"
        "                    return Some(out);\n"
        "                }\n"
        "                if unit.total_carried() > 0 || train_now || view.inventories[0][item] <= reserve {\n"
        "                    return None;\n"
        "                }\n"
        "                if is_adjacent(unit.cell, view.shacks[0]) {\n"
        "                    out.push(act(format!(\"PICK {} {}\", unit.id, kind.as_str()), Target::Cell(unit.cell)));\n"
        "                } else {\n"
        "                    let gate = MoisanBot::orchard_gate(view)?;\n"
        "                    out.push(act(format!(\"MOVE {} {} {}\", unit.id, gate.0, gate.1), Target::Cell(gate)));\n"
        "                }\n"
        "                self.regeneration_commitments.remove(&unit.id);\n"
        "                Some(out)\n"
        "            }\n"
        "            fn endgame(view: &GameState) -> bool {\n"
    ),
)

REPL_HOOK = dict(
    name="commands: the orchard owns the starter's turn when it has something to plant",
    anchor="                    by_id.insert(unit.id, candidates);\n",
    text=(
        "                    if let Some(orchard) = self.orchard_candidates(view, unit, train_now) {\n"
        "                        candidates = orchard;\n"
        "                    }\n"
        "                    by_id.insert(unit.id, candidates);\n"
    ),
)

ORCHARD = (REPL_CHOP_SKIP, REPL_HELPERS, REPL_DANCE, REPL_ORCHARD_TURN, REPL_HOOK)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = tuple(mk.REPLACEMENTS) + th.EXTRA + ORCHARD
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("the third troll variant (b) 2/2/0/2", "candidate-third-troll-2202-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs")):
        mk.OTHERS_LIST.append((label, mk.REPO / "cgauto" / "submissions" / name))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = ("the orchard (the third troll card, design round 3, owner 2026-08-28 ~09:0xZ: "
                          "'let's do orchard' + the far-gate amendment, 'ok')")
        report["bot"] = ("three heroes + an orchard of four lemons and two plums at the gate farthest "
                         "from the enemy, planted by the starter while the third troll is wanted and "
                         "protected from our own axes; the dance fix on fruit walks")
        report["edit"]["what"] = "twenty-one replacements: the third troll's nine + three heroes' seven + the orchard's five"
        for path in (mk.REPORT, HERE / "results" / "build-orchard.json"):
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
