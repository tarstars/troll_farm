#!/usr/bin/env python3
"""Calibrate WOOD_GATE_KAPPA_STARTER and WOOD_GATE_KAPPA_TRAINED: the ratio of the wood a troll
really banks per troll-turn to the gate's trip rate (the champion's own valuation of the best tree
from the door, wood per turn of one round trip).

Why a ratio is needed at all: the v1 gate used the trip rate as the rate itself and never admitted a
troll in 4,593 evaluated turns -- its WITHOUT (the gatherers' foregone wood) was two to four times the
record's measured 11 points a game for a 1/1/0/1 bill, because a troll does not chop the best tree
back to back all game: it walks part loads home, waits on contested trees, replants and harvests.

The realised rates are the record's, from 320 real ladder games of the champion
(`claude_1/cheap-third-troll/READ-2026-09-03.md`, wood banked per troll-turn alive):
  the starter 1/1/1/1  0.029 in turns 1-100 (0.042 pooled over the game);
  the trained troll     0.142 pooled over its shapes (0.150 for a 2/2/0/2).
The trip rates come from the calibration read (`gate_read.py` on the arm built with both kappas at
1.0): the RATES line the debug variant prints on every evaluated turn. kappa_starter = 0.029 / the
mean harvester trip rate over evaluated turns <= 100; kappa_trained = 0.142 / the mean miner trip
rate over every evaluated turn (the third troll, a chop-only troll like the trained one, is scaled by
the same kappa). As a consistency check the resident's realised pair rate on the same 24 smoke games
(wood banked between the second TRAIN and turn 100, per troll-turn) is printed beside the record's
0.171 (0.029 + 0.142).

    python3 claude_1/wood-charging-gate/calibrate_kappa.py [--read results/gate-read-kappa1.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
STARTER_REALISED_P1_100 = 0.029
TRAINED_REALISED_POOLED = 0.142


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", type=Path, default=HERE / "results" / "gate-read-kappa1.json")
    ap.add_argument("--out", type=Path, default=HERE / "results" / "kappa.json")
    args = ap.parse_args()
    read = json.loads(args.read.read_text())
    harvester_early, miner_all, pair_realised, per_game = [], [], [], []
    for g in read["per_game"]:
        turns = [t for t in g["gate_turns"] if t.get("rates")]
        h = [t["rates"]["harvester_trip"] for t in turns if t["turn"] <= 100]
        m = [t["rates"]["miner_trip"] for t in turns]
        harvester_early.extend(h)
        miner_all.extend(m)
        trains = g["trains"]
        t2 = trains[0]["turn"] if trains else None
        realised = None
        if t2 is not None and t2 < 100:
            wood = g["wood_by_turn"]["resident"]
            realised = (wood[99] - wood[t2 - 1]) / (2 * (100 - t2))
            pair_realised.append(realised)
        per_game.append({"map_hash": g["map_hash"], "second_troll_turn": t2,
                         "harvester_trip_mean_to_100": statistics.mean(h) if h else None,
                         "miner_trip_mean": statistics.mean(m) if m else None,
                         "resident_pair_realised_to_100": realised})
    kappa_starter = STARTER_REALISED_P1_100 / statistics.mean(harvester_early)
    kappa_trained = TRAINED_REALISED_POOLED / statistics.mean(miner_all)
    out = {
        "what": "kappa = realised wood per troll-turn (the record's) / the gate's trip rate (this slice's)",
        "read": str(args.read.relative_to(HERE.parent.parent)),
        "starter_realised_turns_1_100": STARTER_REALISED_P1_100,
        "trained_realised_pooled": TRAINED_REALISED_POOLED,
        "harvester_trip_mean_to_100": statistics.mean(harvester_early),
        "harvester_trip_turns": len(harvester_early),
        "miner_trip_mean": statistics.mean(miner_all),
        "miner_trip_turns": len(miner_all),
        "kappa_starter": kappa_starter,
        "kappa_trained": kappa_trained,
        "consistency_resident_pair_realised_to_100_mean": statistics.mean(pair_realised),
        "consistency_record_pair": STARTER_REALISED_P1_100 + TRAINED_REALISED_POOLED,
        "consistency_games": len(pair_realised),
        "per_game": per_game,
    }
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_game"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
