#!/usr/bin/env python3
"""Replay one smoke map with the arm and the resident and print, turn by turn, the own trolls'
commands and the shack's stock, so an idle troll can be explained from the game state down.

    python3 local_claude_1/third-troll/probe.py <map_hash> [--from 1] [--to 300] [--idle-only]
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import smoke                        # noqa: E402
import regression_tests as rt       # noqa: E402
import semantic_harness as sh       # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("map_hash")
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--to", dest="end", type=int, default=300)
    ap.add_argument("--idle-only", action="store_true")
    ap.add_argument("--resident", action="store_true", help="probe the resident instead of the arm")
    ap.add_argument("--arm", type=Path, default=None, help="another arm file to probe")
    args = ap.parse_args()
    plan = None
    with open(HERE / "smoke-maps-seed0.jsonl") as fp:
        for line in fp:
            item = json.loads(line)
            if item["rec"]["map_hash"].startswith(args.map_hash):
                plan = (item["rec"], item["draw"], item["profile"])
    assert plan, "map not in the slice"
    rec, draw, profile = plan
    src = smoke.RESIDENT if args.resident else (args.arm or smoke.ARM)
    with tempfile.TemporaryDirectory(prefix="probe-") as wd:
        binary = Path(wd) / "bot.bin"
        sh.compile_text(src.read_text(), binary, crate="probe_bot")
        ref = smoke.make_referee(rec, draw, profile)
        transcript, commands = rt.run_binary_custom(binary, ref, 300)
    lines = commands.rstrip("\n").split("\n")
    print(f"map {rec['map_hash']} {profile} draw {draw}  iron cells {len(rec.get('iron', []))}  "
          f"trees0 {len(rec['trees0'])}: " +
          ", ".join(f"{t['type']}@{t['x']},{t['y']}" for t in rec["trees0"]))
    # The transcript carries the referee's per-turn input; find the inventory lines if present.
    turns = transcript.split("\n")
    for turn in range(args.start, min(args.end, len(lines)) + 1):
        line = lines[turn - 1]
        frags = [f for f in line.split(";") if not f.startswith("MSG")]
        msg = [f for f in line.split(";") if f.startswith("MSG")]
        units = " ".join(tok for tok in (msg[0].split() if msg else []) if tok.startswith("u"))
        stock = ""
        if args.idle_only and "WAIT" not in line:
            continue
        print(f"t{turn:>3}  {' ; '.join(frags):<60} {units}{stock}")
    own = {uid: u for uid, u in ref.units.items() if u["player"] == 0}
    print("end units:", {uid: (u["cell"], u["speed"], u["cap"], u["harvest"], u["chop"], u["carry"])
                         for uid, u in own.items()})
    print("end inventory:", ref.inv, "score", smoke.own_score(ref.inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
