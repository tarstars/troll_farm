#!/usr/bin/env python3
"""Build "the opening dispatcher" (stage 2A of `20260903-opening-solver`): the champion of record
with the offline opening solver's dispatcher, in its deterministic form, as the opening controller
from turn 1 to the third troll's TRAIN; the champion's own play takes over from there, byte for
byte what it is today.

THE BASE is the champion of record (owner ruling 2026-08-27 09:05Z), as the orchard series was
built: its diagnostics arm `local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs`
(sha256 32172393...) whose compacted form IS the ladder resident `41202036`
(`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha256 0e92f8fa...), and its
readable form `readable/denial-off-champion.rs` (sha256 4ce3d1e8...). The v6 diagnostic line is
untouched. The build chain is `local_claude_1/third-troll/make_third_troll.py`'s (imported and
configured, not copied): every anchor occurs exactly once in BOTH files, both edited files compile
(rustc --edition=2021 -O), the compacted submission round-trips to the arm's token stream, the
submission differs from every other bot, the readable diff's +/- counts equal the replacements'.

THE EDIT, five replacements:
  1. `YamoBot`'s fields -- the dispatcher's memory (done; the seed each troll carries and its
     cell; seeds picked so far; each troll's target last turn);
  2. their initial values in `with_opening_policy`;
  3. the dispatcher itself, `dispatcher.rs.in` (this directory), placed before
     `fallback_second_troll`: the second troll's talents from the draw (R1), the third troll's
     shape from the iron (the orchard bots' rule), the task values (R2, R5), the TRAIN on the
     pre-turn stock with no PICK on that turn (R3), the seed's cell (R4);
  4. `commands`: the TRAIN and the wanted talents come from the dispatcher while the opening runs;
  5. `commands`: each troll's candidate list is the dispatcher's one command while the opening runs
     (the champion's select, move resolver and telemetry run unchanged over it).

    python3 claude_1/opening-solver/stage2a/make_opening_dispatcher.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "third-troll"))
import make_third_troll as mk       # noqa: E402

DISPATCHER = (HERE / "dispatcher.rs.in").read_text()

REPL_FIELDS = dict(
    name="YamoBot: the opening dispatcher's memory",
    anchor="            regeneration_commitments: BTreeMap<i32, PlantKind>,\n",
    text=(
        "            regeneration_commitments: BTreeMap<i32, PlantKind>,\n"
        "            // The opening dispatcher's memory (stage 2A): over once three trolls stand;\n"
        "            // the seed each troll carries and the cell it is for; seeds picked so far;\n"
        "            // each troll's target last turn (a small hold against flip-flops).\n"
        "            opening_done: bool,\n"
        "            opening_seeds: BTreeMap<i32, (PlantKind, Cell)>,\n"
        "            opening_seed_count: usize,\n"
        "            opening_targets: BTreeMap<i32, Cell>,\n"
    ),
)

REPL_INIT = dict(
    name="with_opening_policy: the memory's initial values",
    anchor=(
        "                    regeneration_commitments: BTreeMap::new(),\n"
        "                    opponent_eta_penalty: 0,\n"
    ),
    text=(
        "                    regeneration_commitments: BTreeMap::new(),\n"
        "                    opponent_eta_penalty: 0,\n"
        "                    opening_done: false,\n"
        "                    opening_seeds: BTreeMap::new(),\n"
        "                    opening_seed_count: 0,\n"
        "                    opening_targets: BTreeMap::new(),\n"
    ),
)

REPL_DISPATCHER = dict(
    name="the opening dispatcher (before fallback_second_troll)",
    anchor="            fn fallback_second_troll() -> Stats {\n",
    text=DISPATCHER + "            fn fallback_second_troll() -> Stats {\n",
)

REPL_TRAIN = dict(
    name="commands: the TRAIN and the wanted talents from the dispatcher while the opening runs",
    anchor=(
        "                let desired = self\n"
        "                    .desired_second\n"
        "                    .map(|objective| objective.stats)\n"
        "                    .unwrap_or_else(Self::fallback_second_troll);\n"
        "                let train_now = !self.opening_abandoned && MoisanBot::can_train(view, desired);\n"
    ),
    text=(
        "                // The opening dispatcher (stage 2A) owns the TRAIN and every troll's command\n"
        "                // from turn 1 to the third troll; None once the champion's own play resumes.\n"
        "                let opening = self.opening_dispatch(view);\n"
        "                let desired = match opening.as_ref().and_then(|plan| plan.0) {\n"
        "                    Some(stats) => stats,\n"
        "                    None => self\n"
        "                        .desired_second\n"
        "                        .map(|objective| objective.stats)\n"
        "                        .unwrap_or_else(Self::fallback_second_troll),\n"
        "                };\n"
        "                let train_now = match opening.as_ref() {\n"
        "                    Some(plan) => plan.0.is_some(),\n"
        "                    None => !self.opening_abandoned && MoisanBot::can_train(view, desired),\n"
        "                };\n"
    ),
)

REPL_FORCE = dict(
    name="commands: the dispatcher's one command per troll while the opening runs",
    anchor="                    by_id.insert(unit.id, candidates);\n",
    text=(
        "                    if let Some(forced) = opening.as_ref().and_then(|plan| plan.1.get(&unit.id)) {\n"
        "                        candidates = vec![forced.clone()];\n"
        "                    }\n"
        "                    by_id.insert(unit.id, candidates);\n"
    ),
)

REPLACEMENTS = (REPL_FIELDS, REPL_INIT, REPL_DISPATCHER, REPL_TRAIN, REPL_FORCE)


def main() -> int:
    mk.REPLACEMENTS = REPLACEMENTS
    mk.STACKED = False
    mk.ARM = HERE / "champion-opening-dispatcher-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "opening-dispatcher-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-opening-dispatcher-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-opening-dispatcher-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "opening-dispatcher.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs"),
                        ("orchard 6", "candidate-orchard6-v6-instrument.rs"),
                        ("orchard 8", "candidate-orchard8-v6-instrument.rs")):
        path = mk.REPO / "cgauto" / "submissions" / name
        if path.exists():
            mk.OTHERS_LIST.append((label, path))
    rc = mk.main()
    if rc == 0:
        # The build chain writes the sha256 sidecars beside its own files; they belong here.
        for path in (mk.ARM, mk.READABLE_EDITED):
            stray = mk.HERE / (path.name + ".sha256")
            if stray.exists():
                stray.replace(HERE / (path.name + ".sha256"))
        report = json.loads(mk.REPORT.read_text())
        report["task"] = ("the opening dispatcher (20260903-opening-solver, stage 2A: the solver's "
                          "dispatcher in the champion as the opening controller, rules first)")
        report["board_row"] = "20260903-opening-solver, stage 2A"
        report["bot"] = ("the champion of record; from turn 1 to the third troll's TRAIN the opening "
                         "solver's deterministic dispatcher plays (R1-R5, the third troll's chop from "
                         "the iron), then the champion's own play, unchanged")
        report["edit"]["what"] = "five replacements: the opening dispatcher"
        report["verdict"] = "CHAMPION_OPENING_DISPATCHER_V6_INSTRUMENT_ROUND_TRIP_EXACT"
        mk.REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        (HERE / "results").mkdir(exist_ok=True)
        (HERE / "results" / "build.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        stray = mk.HERE / "results" / "build-v6.json"
        if stray.exists():
            stray.unlink()
        diff = mk.DIFF.read_text().replace("(the third troll)", "(the opening dispatcher)", 1)
        mk.DIFF.write_text(diff)
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except mk.BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
