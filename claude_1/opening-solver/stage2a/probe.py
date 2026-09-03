#!/usr/bin/env python3
"""Play one smoke record with the arm and print the opening turn by turn (the command line, the
own stock, the roster) -- a reading aid, not a gate.

    python3 claude_1/opening-solver/stage2a/probe.py [--index 0] [--turns 90] [--arm FILE]
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "third-troll"))
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2", "claude_1/narrate6", "claude_1/cure3"):
    sys.path.insert(0, str(REPO / _p))
import smoke                        # noqa: E402
import regression_tests as rt       # noqa: E402
import semantic_harness as sh       # noqa: E402


DEBUG_TABLE = (
    "                        for t in &tasks {\n"
    "                            eprintln!(\"t{} u{} at {:?} carry {:?} need {:?}  {:.4} {} -> {:?}\", view.turn, unit.id, unit.cell, unit.carry, need, t.value, t.command, t.target);\n"
    "                        }\n"
)
DEBUG_PRINT = (
    "                    if let Some(t) = task.as_ref() {\n"
    "                        eprintln!(\"t{} u{} CHOSEN {:.4} {} -> {:?} train {:?}\", view.turn, unit.id, t.value, t.command, t.target, train);\n"
    "                    }\n"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--turns", type=int, default=90)
    ap.add_argument("--arm", type=Path, default=HERE / "champion-opening-dispatcher-v6-instrument.rs")
    ap.add_argument("--records", type=Path, default=REPO / "local_claude_1" / "third-troll" / "smoke-maps-seed0.jsonl")
    ap.add_argument("--resident", action="store_true", help="play the resident instead")
    ap.add_argument("--debug", type=Path, default=None,
                    help="write the dispatcher's task table per turn (a throwaway build with a stderr print) here")
    args = ap.parse_args()
    plan = [json.loads(l) for l in open(args.records) if l.strip()]
    item = plan[args.index]
    rec, draw, profile = item["rec"], item["draw"], item["profile"]
    text = (smoke.RESIDENT if args.resident else args.arm).read_text()
    if args.debug is not None:
        anchor = "                    let (command, target) = match task {\n"
        assert text.count(anchor) == 1, "debug anchor"
        text = text.replace(anchor, DEBUG_PRINT + anchor, 1)
        anchor2 = "                        let last = self.opening_targets.get(&unit.id).copied();\n"
        assert text.count(anchor2) == 1, "debug anchor 2"
        text = text.replace(anchor2, anchor2 + DEBUG_TABLE, 1)
    with tempfile.TemporaryDirectory(prefix="probe-") as wd:
        binary = Path(wd) / "bot.bin"
        sh.compile_text(text, binary, crate="probe_bot")
        ref = smoke.make_referee(rec, draw, profile)
        if args.debug is not None:
            import subprocess
            old_popen = subprocess.Popen
            log = open(args.debug, "w")
            def popen(*a, **kw):
                kw["stderr"] = log
                return old_popen(*a, **kw)
            subprocess.Popen = popen
        transcript, commands = rt.run_binary_custom(binary, ref, args.turns)
        if args.debug is not None:
            subprocess.Popen = old_popen
            log.close()
    lines = commands.rstrip("\n").split("\n")
    print(f"map {rec['map_hash']} seat 0, draw {draw}, opponent {profile}, iron cells {len(rec.get('iron', []))}")
    print("\n".join(rec["rows"]))
    for turn, line in enumerate(lines, 1):
        frags = [f for f in line.split(";") if not f.startswith("MSG")]
        print(f"t{turn:3d}  " + " ; ".join(frags))
    print("trains:", smoke.all_trains(lines))
    print("own units:", {uid: [u["speed"], u["cap"], u["harvest"], u["chop"]] for uid, u in ref.units.items() if u["player"] == 0})
    print("own stock:", ref.inv, "score", smoke.own_score(ref.inv), "errors", dict(ref.error_counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
