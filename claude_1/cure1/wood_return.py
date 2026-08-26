#!/usr/bin/env python3
"""R-C / disposition 3 — the thing D-4 is a PROXY for: how long a wood return actually takes.

D-4 (`trace_detectors.detect_d4`, *abandoned carried-wood return*) fires on two consecutive turns
without a decrease of the unit's distance to a bank door inside a wood-committed interval. A
deliberate two-turn hold IS exactly that shape, so the detector reads the cure as the disease. The
coordinator's ruling (2026-08-25T09:42:00Z, disposition 3) refuses both the waiver and the
detector edit and orders the underlying quantity measured instead:

    per wood-committed interval, turns from commitment to bank, base vs candidate, paired by game;
    if the candidate's mean return is slower, that is a NAMED COST on the sheet.

Commitment start is D-4's own rule (A5 / I-19 / I-21), read from the same trace object the
detector uses, so the two measurements cannot disagree about what "committed" means: a unit
carrying wood that is either at full capacity, or issues a MOVE whose target is a bank door, or
issues a DROP while standing on one. The interval ENDS when the wood is banked -- the carried
cargo reaches zero. An interval that never banks (the game ends first, the unit dies, the door
becomes unreachable) is UNRESOLVED and is reported separately rather than folded into a mean with
an invented duration.

Pairing is by (map_id, seat), and the headline is the paired mean of per-game means, so one game
with many intervals cannot dominate. A game with no completed interval in either arm contributes
nothing.

    python3 claude_1/cure1/wood_return.py
"""
from __future__ import annotations

import argparse
import gzip
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "banana-restoration-r2"))
import trace_detectors as td        # noqa: E402

CAND = "/tmp/claude-1000/cure1/cure1-candidate/games/games.jsonl.gz"
FLOOR = "/tmp/claude-1000/cure1/cure1-floor/games/games.jsonl.gz"
OUT = HERE / "results" / "wood-return.json"
WOOD = td.WOOD


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return {(g["map_id"], g["seat"]): g for g in (json.loads(l) for l in fh)}


def intervals(game, arm="candidate"):
    """Completed and unresolved wood-committed intervals for every own unit."""
    tr = td.build_trace(game["artifacts"][f"{arm}_transcript"],
                        game["artifacts"][f"{arm}_commands"])
    done, unresolved = [], 0
    for uid in tr.own_ids:
        committed, start = False, None
        for t in range(1, tr.T + 1):
            u = tr.unit(uid, t)
            if u is None:
                if committed:
                    unresolved += 1
                committed = False
                continue
            cmd = tr.cmd_of(uid, t)
            if committed and u.total_carried() == 0:
                done.append(t - start)
                committed = False
            if committed and tr.door_dist.get(u.cell) is None:
                unresolved += 1
                committed = False
            if not committed and u.carry[WOOD] > 0:
                starts = (u.free_capacity() == 0
                          or (cmd is not None and cmd.verb == "MOVE"
                              and cmd.args[0] in tr.doors)
                          or (cmd is not None and cmd.verb == "DROP"
                              and u.cell in tr.doors))
                if starts:
                    committed, start = True, t
        if committed:
            unresolved += 1
    return done, unresolved


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--candidate-games", default=CAND)
    ap.add_argument("--floor-games", default=FLOOR)
    ap.add_argument("--json", default=str(OUT))
    args = ap.parse_args(argv)

    cand, floor = load(Path(args.candidate_games)), load(Path(args.floor_games))
    if set(cand) != set(floor):
        print("REFUSED: the two archives do not cover the same (map, seat) set")
        return 2

    paired, slower, faster = [], [], []
    c_all, b_all = [], []
    c_unres = b_unres = 0
    for key in sorted(cand):
        c_done, cu = intervals(cand[key])
        b_done, bu = intervals(floor[key])
        c_unres += cu
        b_unres += bu
        c_all += c_done
        b_all += b_done
        if not c_done or not b_done:
            continue
        cm, bm = statistics.fmean(c_done), statistics.fmean(b_done)
        paired.append({"map_id": key[0], "seat": key[1],
                       "candidate_mean_turns": round(cm, 4), "base_mean_turns": round(bm, 4),
                       "delta_turns": round(cm - bm, 4),
                       "candidate_intervals": len(c_done), "base_intervals": len(b_done)})
        if cm > bm + 1e-9:
            slower.append(paired[-1])
        elif cm < bm - 1e-9:
            faster.append(paired[-1])

    deltas = [r["delta_turns"] for r in paired]
    mean_delta = statistics.fmean(deltas) if deltas else 0.0
    report = {
        "measurement": "turns from wood commitment to bank, per interval, paired by (map, seat)",
        "ruling": ("coordination/messages/local_claude_1/"
                   "20260825T094200Z-20260825-dance-cure-candidate-1-hold-policy.md "
                   "(disposition 3)"),
        "commitment_rule": "trace_detectors.detect_d4's own A5/I-19/I-21 start rule",
        "end_rule": "the carried cargo reaches zero (banked); anything else is UNRESOLVED",
        "games_paired": len(paired),
        "candidate_completed_intervals": len(c_all),
        "base_completed_intervals": len(b_all),
        "candidate_unresolved_intervals": c_unres,
        "base_unresolved_intervals": b_unres,
        "candidate_mean_turns_all_intervals": round(statistics.fmean(c_all), 4) if c_all else None,
        "base_mean_turns_all_intervals": round(statistics.fmean(b_all), 4) if b_all else None,
        "paired_mean_delta_turns": round(mean_delta, 4),
        "games_slower": len(slower), "games_faster": len(faster),
        "slowest_games": sorted(slower, key=lambda r: -r["delta_turns"])[:10],
        "named_cost": mean_delta > 0,
        "verdict": ("NAMED COST: the candidate's mean wood return is slower"
                    if mean_delta > 0 else
                    "no cost: the candidate's mean wood return is not slower than the base's"),
        "per_game": paired,
    }
    Path(args.json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  games paired {len(paired)}   completed intervals: base {len(b_all)}, "
          f"candidate {len(c_all)}   unresolved: base {b_unres}, candidate {c_unres}")
    print(f"  mean return turns: base {report['base_mean_turns_all_intervals']}, "
          f"candidate {report['candidate_mean_turns_all_intervals']}")
    print(f"  paired mean delta {mean_delta:+.4f} turns   slower on {len(slower)} games, "
          f"faster on {len(faster)}")
    print(f"  -> {report['verdict']}")
    print(f"  -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
