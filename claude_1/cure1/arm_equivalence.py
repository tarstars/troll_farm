#!/usr/bin/env python3
"""The other half of codex_1's parity definition: **candidate against the instrument arm**.

Definition 4 has two halves. `alpha_parity.py`/`panel_parity.py` run the first (rule-off against
the champion). This runs the second: the candidate arm (hold ON, no `MSG`) and the instrument arm
(hold ON, v4 telemetry) must play the SAME game — ordered gameplay-token equality after the
single `MSG` fragment is stripped — on all 240 panel games.

It is what licenses reading the instrument's telemetry as an explanation of the candidate's
behaviour. Without it, every branch count from the instrument would describe a bot nobody is
proposing to submit.

    python3 claude_1/cure1/arm_equivalence.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate4"))
import narrate4 as n4               # noqa: E402

CAND = Path("/tmp/claude-1000/cure1/cure1-candidate/games/games.jsonl.gz")
INST = Path("/tmp/claude-1000/cure1/cure1-instrument/games/games.jsonl.gz")
OUT = HERE / "results" / "arm-equivalence.json"


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return {(g["map_id"], g["seat"]): g for g in (json.loads(l) for l in fh)}


def main() -> int:
    cand, inst = load(CAND), load(INST)
    if set(cand) != set(inst):
        print("REFUSED: the two panels do not cover the same games")
        return 2
    rows, differing = [], []
    for key in sorted(cand):
        a = [n4.strip_msg(l) for l in cand[key]["artifacts"]["candidate_commands"]
             .rstrip("\n").split("\n")]
        b = [n4.strip_msg(l) for l in inst[key]["artifacts"]["candidate_commands"]
             .rstrip("\n").split("\n")]
        same = a == b
        first = None
        if not same:
            for i, (x, y) in enumerate(zip(a, b), 1):
                if x != y:
                    first = {"turn": i, "candidate": x, "instrument": y}
                    break
            differing.append({"map_id": key[0], "seat": key[1], "first_divergence": first})
        rows.append({"map_id": key[0], "seat": key[1], "identical": same})
    ok = not differing
    report = {
        "gate": "codex_1 definition 4, second half — candidate arm == instrument arm in play",
        "task": "20260825-dance-cure-candidate-1-hold",
        "candidate_games": str(CAND), "instrument_games": str(INST),
        "games": len(rows), "identical": sum(1 for r in rows if r["identical"]),
        "differing": differing, "verdict": "PASS" if ok else "FAIL", "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  candidate == instrument in play: {report['identical']}/{report['games']} games "
          f"-> {report['verdict']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
