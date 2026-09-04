#!/usr/bin/env python3
"""Build "the wood-charging gate" (task `20260904-wood-charging-gate`): the champion of record
with ONE variable added -- a third troll that is funded only while a forecast made from the live
board says the troll beats the wood its funding costs, and abandoned the turn it stops winning.
The owner's rule, in the owner's words: "we are going to predict two outcomes: with troll and
without, and if 'with' wins, we do it."

THE BASE is the champion of record (owner ruling 2026-08-27 09:05Z), as every build in this
project is made: its diagnostics arm `local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs`
(sha256 32172393...) whose compacted form IS the ladder resident `41202036`
(`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha256 0e92f8fa...), and
its readable form `readable/denial-off-champion.rs` (sha256 4ce3d1e8...). The v6 diagnostics
line is untouched. The chain is `local_claude_1/third-troll/make_third_troll.py`'s (imported and
configured, not copied): every anchor occurs exactly once in BOTH files, both edited files
compile (rustc --edition=2021 -O), the compacted submission round-trips to the arm's token
stream, the submission differs from every other bot, the readable diff's +/- counts equal the
replacements'.

THE CHAMPION HAS NO THIRD TROLL. It trains exactly one (`can_train` refuses once two stand;
`early_candidates` runs only while fewer than two exist), so "the moment a troll would commit to
a trip that funds the third troll" does not exist in the base. The one variable is therefore the
gated funding pathway as a whole: the bill, the trips that collect it, the TRAIN, and the
forecast that admits or declines them. The funding trips are the champion's own opening code
for the second troll's bill (`early_candidates`: fruit and iron trips above chopping while an
item is missing, carried loads banked first), split by ability as the third-troll instrument of
2026-08-28 split them (the starter, the only troll that can harvest, fetches the fruit; the
trained troll mines the iron). When the gate declines, the bot is the champion byte for byte.
NOT carried from that instrument: the joint three-troll `select` -- the card says one variable,
so after the third troll the champion's own greedy id-order pass at three trolls plays, as it
would have.

THE EDIT, seven replacements:
  1. `can_train`            -- the roster cap 2 -> 3 (the third-troll instrument's, verbatim);
  2. the gate               -- `gate.rs.in` (this directory), placed before
                               `fallback_second_troll`: THIRD_TROLL_HORIZON (a third troll is
                               wanted only while 100 turns remain), the door chop rate, the
                               funding times, the 27 shapes, the two futures, the decision;
  3. `commands`: desired    -- with two trolls the wanted build is the gate's shape of the turn,
                               if any; `train_now` follows and cannot fire a second "second";
  4. `commands`: early      -- the funding mode runs while the gate admits (the instrument's);
  5. `commands`: per troll  -- a funding troll with nothing of its part left plays normally
                               (the instrument's);
  6. `early_candidates`     -- the bill split by ability (the instrument's);
  7. `early_candidates`     -- the chop fallback for the one-troll case only (the instrument's).

    python3 claude_1/wood-charging-gate/make_wood_gate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "third-troll"))
import make_third_troll as mk       # noqa: E402

GATE = (HERE / "gate.rs.in").read_text()

REPL_GATE = dict(
    name="the wood-charging gate (before fallback_second_troll)",
    anchor="            fn fallback_second_troll() -> Stats {\n",
    text=GATE + "            fn fallback_second_troll() -> Stats {\n",
)

REPL_DESIRED = dict(
    name="commands: with two trolls the wanted build is the gate's shape of the turn, if any",
    anchor=(
        "                let desired = self\n"
        "                    .desired_second\n"
        "                    .map(|objective| objective.stats)\n"
        "                    .unwrap_or_else(Self::fallback_second_troll);\n"
        "                let train_now = !self.opening_abandoned && MoisanBot::can_train(view, desired);\n"
    ),
    text=(
        "                let own_trolls = view.units.iter().filter(|unit| unit.player == 0).count();\n"
        "                // The wood-charging gate decides every turn with two trolls while the horizon\n"
        "                // holds; Some(shape) admits the funding of that troll, None declines it.\n"
        "                let third_plan = if own_trolls == 2\n"
        "                    && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON\n"
        "                {\n"
        "                    Self::wood_gate(view)\n"
        "                } else {\n"
        "                    None\n"
        "                };\n"
        "                let third_wanted = third_plan.is_some();\n"
        "                let desired = match third_plan {\n"
        "                    Some(stats) => stats,\n"
        "                    None => self\n"
        "                        .desired_second\n"
        "                        .map(|objective| objective.stats)\n"
        "                        .unwrap_or_else(Self::fallback_second_troll),\n"
        "                };\n"
        "                let train_now = !self.opening_abandoned\n"
        "                    && (own_trolls < 2 || third_wanted)\n"
        "                    && MoisanBot::can_train(view, desired);\n"
    ),
)

REPLACEMENTS = (mk.REPL_CAP, REPL_GATE, REPL_DESIRED, mk.REPL_EARLY, mk.REPL_PER_TROLL,
                mk.REPL_SPLIT, mk.REPL_CHOP_FALLBACK)

NAME = "candidate-wood-gate-v6-instrument.rs"


def main() -> int:
    mk.REPLACEMENTS = REPLACEMENTS
    mk.STACKED = False
    mk.ARM = HERE / "champion-wood-gate-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "wood-gate-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / NAME
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-wood-gate-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "wood-gate.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs"),
                        ("orchard 6", "candidate-orchard6-v6-instrument.rs"),
                        ("orchard 8", "candidate-orchard8-v6-instrument.rs"),
                        ("the opening dispatcher (stage 2A)",
                         "candidate-opening-dispatcher-v6-instrument.rs")):
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
        report["task"] = ("the wood-charging gate (20260904-wood-charging-gate: a third troll funded "
                          "only while a live-board forecast says it beats the wood its funding costs)")
        report["board_row"] = "20260904-wood-charging-gate"
        report["bot"] = ("the champion of record; with two trolls, every turn while 100 turns remain, "
                         "the gate forecasts WITH (the third troll's wood to the end, the smaller of its "
                         "uncontested rate and its forest-share gain, minus the bill's fruit at face "
                         "value) and WITHOUT (the gathering trolls' wood over the same turns) for 27 "
                         "shapes; the best admitted shape is funded as the champion funds its second "
                         "troll, abandoned the turn WITH stops beating WITHOUT; declined = the champion "
                         "byte for byte")
        report["edit"]["what"] = "seven replacements: the wood-charging gate"
        report["verdict"] = "CHAMPION_WOOD_GATE_V6_INSTRUMENT_ROUND_TRIP_EXACT"
        mk.REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        (HERE / "results").mkdir(exist_ok=True)
        (HERE / "results" / "build.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        stray = mk.HERE / "results" / "build-v6.json"
        if stray.exists():
            stray.unlink()
        diff = mk.DIFF.read_text().replace("(the third troll)", "(the wood-charging gate)", 1)
        mk.DIFF.write_text(diff)
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except mk.BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
