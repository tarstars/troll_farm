#!/usr/bin/env python3
"""Build "three heroes": the third-troll bot redesigned after its ladder look (owner 2026-08-28
06:2xZ: "three trolls bot has extremely low rating and it's quite obvious why. The second troll
starts to chop trees immediately and chops down trees with resources for the third troll. Can we
train the second troll with 1 harvest capacity and introduce rule that two trolls collect
resources (no chopping) until the third troll appears, or we detect that the third troll is
unreachable" -- design accepted "ok"). Card `coordination/tasks/20260828-third-troll.md`, design
round 2.

THE RULE (owner, plain words), on top of the third troll's nine replacements (`make_third_troll.py`):
  1. The second troll gets harvest power 1: the same choice machinery (grid, 15-turn horizon,
     turn-35 deadline), every option with harvest 1 instead of 0 (one apple more on its price).
  2. After the second troll both trolls collect the third troll's bill -- fruits and iron alike,
     the joint choice keeps them off the same tree; carried goods are banked first -- and NOBODY
     CHOPS while the bill is being collected.
  3. The third troll (2/3/0/3) is trained the turn the bill is paid; then all three play as now.
  4. "Unreachable" ends the funding and normal play resumes: a missing fruit of the bill has no
     living reachable tree of its kind, or fewer than 100 turns remain (computed every turn from
     the game state; iron is never the blocker -- on a map without iron the price ignores it).

THE EDIT: the nine replacements of `make_third_troll.py` (imported) followed by six more, each
anchored on text that occurs exactly once in BOTH files after the nine:
  10. `opening_options`       -- the grid's harvest power 0 -> 1;
  11. `choose_second_troll`   -- the baseline 1/1/0/1 -> 1/1/1/1;
  12. `fallback_second_troll` -- 1/1/0/1 -> 1/1/1/1;
  13. `early_candidates`      -- both trolls fetch iron too (the split by ability is gone);
  14. `commands`: reachable   -- `third_reachable` from the game state, and the funding mode runs
                                 while the third troll is wanted AND reachable;
  15. `commands`: per troll   -- in the funding mode every troll gets the funding list only (no
                                 fall-back to normal play, hence no chopping).

Same chain as `make_third_troll.py` (base hashes, anchors once, compile, compact, round trip,
distinct from every bot, the readable diff with its +/- counts asserted). Outputs:
  local_claude_1/third-troll/champion-three-heroes-v6-instrument.rs (+ .sha256)
  local_claude_1/third-troll/three-heroes-readable.rs (+ .sha256)
  cgauto/submissions/candidate-three-heroes-v6-instrument.rs (+ .sha256)
  readable/diffs/three-heroes.diff, readable/reports/candidate-three-heroes-v6-instrument.round-trip.json

    python3 local_claude_1/third-troll/make_three_heroes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_third_troll as mk   # noqa: E402

REPL_GRID_HARVEST = dict(
    name="opening_options: the second troll's grid gets harvest power 1",
    anchor=(
        "                            let stats = Stats {\n"
        "                                movement_speed,\n"
        "                                carry_capacity,\n"
        "                                harvest_power: 0,\n"
        "                                chop_power,\n"
        "                            };\n"
    ),
    text=(
        "                            let stats = Stats {\n"
        "                                movement_speed,\n"
        "                                carry_capacity,\n"
        "                                harvest_power: 1,\n"
        "                                chop_power,\n"
        "                            };\n"
    ),
)

REPL_BASELINE_HARVEST = dict(
    name="choose_second_troll: the baseline troll gets harvest power 1",
    anchor=(
        "                            Stats {\n"
        "                                movement_speed: 1,\n"
        "                                carry_capacity: 1,\n"
        "                                harvest_power: 0,\n"
        "                                chop_power: 1,\n"
        "                            },\n"
    ),
    text=(
        "                            Stats {\n"
        "                                movement_speed: 1,\n"
        "                                carry_capacity: 1,\n"
        "                                harvest_power: 1,\n"
        "                                chop_power: 1,\n"
        "                            },\n"
    ),
)

REPL_FALLBACK_HARVEST = dict(
    name="fallback_second_troll: 1/1/0/1 -> 1/1/1/1",
    anchor=(
        "            fn fallback_second_troll() -> Stats {\n"
        "                Stats {\n"
        "                    movement_speed: 1,\n"
        "                    carry_capacity: 1,\n"
        "                    harvest_power: 0,\n"
        "                    chop_power: 1,\n"
        "                }\n"
        "            }\n"
    ),
    text=(
        "            fn fallback_second_troll() -> Stats {\n"
        "                Stats {\n"
        "                    movement_speed: 1,\n"
        "                    carry_capacity: 1,\n"
        "                    harvest_power: 1,\n"
        "                    chop_power: 1,\n"
        "                }\n"
        "            }\n"
    ),
)

REPL_BOTH_FETCH = dict(
    name="early_candidates: both trolls fetch fruits and iron alike",
    anchor=(
        "                // With two trolls the bill is split by ability: the troll that can harvest\n"
        "                // fetches the missing fruits, the one that cannot mines the missing iron. With\n"
        "                // one troll (the second troll's bill) it fetches everything, as before.\n"
        "                let fetches_fruit = unit.stats.harvest_power > 0;\n"
        "                let fetches_iron = n < 2 || unit.stats.harvest_power <= 0;\n"
    ),
    text=(
        "                // Every troll fetches whatever is missing -- fruits if it can harvest, iron\n"
        "                // always; the joint choice keeps two trolls off the same tree (three heroes).\n"
        "                let fetches_fruit = unit.stats.harvest_power > 0;\n"
        "                let fetches_iron = true;\n"
    ),
)

REPL_REACHABLE = dict(
    name="commands: third_reachable from the game state; funding while wanted and reachable",
    anchor=(
        "                let third_wanted =\n"
        "                    own_trolls == 2 && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON;\n"
    ),
    text=(
        "                let third_wanted =\n"
        "                    own_trolls == 2 && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON;\n"
        "                // Reachable: every fruit of the bill still missing has a living tree of its\n"
        "                // kind that an own troll can walk to (iron is never the blocker: on a map\n"
        "                // without iron the price ignores it). Otherwise the funding ends for now.\n"
        "                let third_reachable = third_wanted && {\n"
        "                    let cost = training_cost(2, Self::third_troll().tuple());\n"
        "                    let scout = view.units.iter().find(|unit| unit.player == 0);\n"
        "                    [(PLUM, PlantKind::Plum), (LEMON, PlantKind::Lemon), (APPLE, PlantKind::Apple)]\n"
        "                        .into_iter()\n"
        "                        .all(|(item, kind)| {\n"
        "                            cost[item] <= view.inventories[0][item]\n"
        "                                || scout.map_or(false, |unit| {\n"
        "                                    !MoisanBot::fruit_candidates(view, unit, kind, 0.0).is_empty()\n"
        "                                })\n"
        "                        })\n"
        "                };\n"
    ),
)

REPL_EARLY_REACHABLE = dict(
    name="commands: the funding mode runs while the third troll is wanted and reachable",
    anchor=(
        "                let early =\n"
        "                    !self.opening_abandoned && (my_units.len() < 2 || third_wanted) && !train_now;\n"
    ),
    text=(
        "                let early = !self.opening_abandoned\n"
        "                    && (my_units.len() < 2 || third_reachable)\n"
        "                    && !train_now;\n"
    ),
)

REPL_NO_CHOP = dict(
    name="commands: in the funding mode every troll gets the funding list only (no chopping)",
    anchor=(
        "                    } else if early {\n"
        "                        // With two trolls, a troll whose part of the bill is complete gets\n"
        "                        // only the WAIT back from the funding list: it plays normally.\n"
        "                        let funding = MoisanBot::early_candidates(view, unit, desired);\n"
        "                        if own_trolls < 2 || funding.len() > 1 {\n"
        "                            funding\n"
        "                        } else {\n"
        "                            Self::main_candidates(\n"
        "                                view,\n"
        "                                unit,\n"
        "                                self.type_to_cut,\n"
        "                                self.idle_regeneration,\n"
        "                                self.persistent_regeneration,\n"
        "                                self.opponent_eta_penalty,\n"
        "                            )\n"
        "                        }\n"
        "                    } else {\n"
    ),
    text=(
        "                    } else if early {\n"
        "                        // Three heroes: while the bill is collected nobody chops -- every\n"
        "                        // troll gets the funding list and nothing else.\n"
        "                        MoisanBot::early_candidates(view, unit, desired)\n"
        "                    } else {\n"
    ),
)

EXTRA = (REPL_GRID_HARVEST, REPL_BASELINE_HARVEST, REPL_FALLBACK_HARVEST, REPL_BOTH_FETCH,
         REPL_REACHABLE, REPL_EARLY_REACHABLE, REPL_NO_CHOP)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = tuple(mk.REPLACEMENTS) + EXTRA
    mk.STACKED = True
    mk.ARM = HERE / "champion-three-heroes-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "three-heroes-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-three-heroes-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-three-heroes-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "three-heroes.diff"
    mk.OTHERS_LIST.append(("the third troll (a) 2/3/0/3",
                           mk.REPO / "cgauto" / "submissions" / "candidate-third-troll-v6-instrument.rs"))
    mk.OTHERS_LIST.append(("the third troll variant (b) 2/2/0/2",
                           mk.REPO / "cgauto" / "submissions" / "candidate-third-troll-2202-v6-instrument.rs"))
    rc = mk.main()
    if rc == 0:
        for path in (mk.REPORT, HERE / "results" / "build-heroes.json"):
            report = json.loads(mk.REPORT.read_text())
            report["task"] = ("three heroes (the third troll, design round 2, owner 2026-08-28 06:2xZ: "
                              "second troll with harvest 1; both trolls collect, nobody chops, until "
                              "the third troll or unreachable)")
            report["bot"] = ("the champion of record; second troll harvest 1; after it both trolls "
                             "collect a 2/3/0/3 third troll's bill with no chopping until it is "
                             "trained or unreachable; select chooses jointly for any number of trolls")
            report["edit"]["what"] = "sixteen replacements: the third troll's nine + three heroes' seven"
            path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except mk.BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
