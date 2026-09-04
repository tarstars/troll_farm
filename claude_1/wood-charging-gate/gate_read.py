#!/usr/bin/env python3
"""The gate read: what the wood-charging gate decided, game by game, on the 24-map smoke slice --
the card's report items the smoke itself cannot see (how often the gate DECLINED the troll and
why, the tuples chosen, the third troll's arrival in GAME TURNS, the wood banked by turns 50 and
100 against the champion's).

How the decisions are read without touching the shipped bot: a throwaway variant of the arm with
one `eprintln!` after the gate's decision (stderr only; the command stream is untouched) plays
each smoke game beside the arm itself and the resident (the champion of record). The variant's
command stream must equal the arm's on every map, turn for turn -- checked, and the read is
refused otherwise -- so every decision read here belongs to the bot that is shipped.

Conventions. A turn is a GAME turn: the 1-based index of the command line the bot answered (the
smoke's own convention; not the referee replay's frame index, which runs two to a game turn).
"declined" on a turn means the gate was evaluated (two trolls, horizon open) and admitted no
shape; a "declined game" is one in which the gate was evaluated on at least one turn and no
third troll was ever trained. Reasons for a decline, from the best forecast of the turn:
  unpayable       no shape's bill can be fetched on this map (no fruit of a kind, or no iron
                  route) -- nothing to decide;
  fruit_not_paid  the best shape's WITH is at or below zero: the troll cannot even repay the
                  fruit it costs;
  wood_wins       WITH is positive but does not beat WITHOUT: the wood the gatherers would bank
                  in the same turns is worth more.

    python3 claude_1/wood-charging-gate/gate_read.py [--arm FILE] [--records FILE] [--turns 300] [--out FILE]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "third-troll"))
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2", "claude_1/narrate6",
           "claude_1/cure3"):
    sys.path.insert(0, str(REPO / _p))
import smoke                        # noqa: E402
import semantic_harness as sh       # noqa: E402

ANCHOR = "                let third_wanted = third_plan.is_some();\n"
DEBUG = (
    "                if own_trolls == 2 && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON {\n"
    "                    if let Some((h, m, rh, rm)) = Self::wood_gate_rates(view) {\n"
    "                        eprintln!(\"RATES t{} harvester {} {} {} {} {:.4} miner {} {} {} {} {:.4}\", view.turn,\n"
    "                            h.movement_speed, h.carry_capacity, h.harvest_power, h.chop_power, rh,\n"
    "                            m.movement_speed, m.carry_capacity, m.harvest_power, m.chop_power, rm);\n"
    "                    }\n"
    "                    match Self::wood_gate_best(view) {\n"
    "                        Some((s, w, wo, a)) => eprintln!(\n"
    "                            \"GATE t{} best {} {} {} {} with {:.3} without {:.3} arrival {} admit {}\",\n"
    "                            view.turn, s.movement_speed, s.carry_capacity, s.harvest_power,\n"
    "                            s.chop_power, w, wo, a, w > wo),\n"
    "                        None => eprintln!(\"GATE t{} none\", view.turn),\n"
    "                    }\n"
    "                }\n"
)
CHECKPOINTS = (50, 100)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def play(binary: Path, ref, turns: int, stderr_path: Path | None):
    """Closed loop as `regression_tests.run_binary_custom`, plus the own inventory after every
    turn and the bot's stderr captured to a file."""
    header = ref.map_header()
    lines, inventories = [], []
    err = open(stderr_path, "w") if stderr_path else subprocess.DEVNULL
    try:
        with subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=err, text=True) as proc:
            proc.stdin.write(header)
            proc.stdin.flush()
            for _ in range(turns):
                proc.stdin.write(ref.turn_text())
                proc.stdin.flush()
                line = proc.stdout.readline()
                if not line:
                    raise RuntimeError("bot closed stdout early")
                lines.append(line.rstrip("\n"))
                ref.apply(lines[-1])
                ref.grow()
                inventories.append(list(ref.inv))
            proc.stdin.close()
    finally:
        if stderr_path:
            err.close()
    return lines, inventories, ref


def read_gate_log(path: Path):
    per_turn = []
    rates = {}
    for raw in path.read_text().splitlines():
        f = raw.split()
        if f and f[0] == "RATES":
            rates[int(f[1][1:])] = {"harvester": " ".join(f[3:7]), "harvester_trip": float(f[7]),
                                    "miner": " ".join(f[9:13]), "miner_trip": float(f[13])}
            continue
        if not f or f[0] != "GATE":
            continue
        turn = int(f[1][1:])
        if f[2] == "none":
            per_turn.append({"turn": turn, "best": None, "admit": False, "reason": "unpayable",
                             "rates": rates.get(turn)})
            continue
        spec = " ".join(f[3:7])
        with_, without = float(f[8]), float(f[10])
        admit = f[14] == "true"
        reason = None if admit else ("fruit_not_paid" if with_ <= 0 else "wood_wins")
        per_turn.append({"turn": turn, "best": spec, "with": with_, "without": without,
                         "arrival": int(f[12]), "admit": admit, "reason": reason, "rates": rates.get(turn)})
    return per_turn


def summarise_game(per_turn, trains):
    evaluated = len(per_turn)
    admitted = [t for t in per_turn if t["admit"]]
    declined = [t for t in per_turn if not t["admit"]]
    flips = sum(1 for a, b in zip(per_turn, per_turn[1:]) if a["admit"] and not b["admit"])
    reasons = {}
    for t in declined:
        reasons[t["reason"]] = reasons.get(t["reason"], 0) + 1
    third = trains[1] if len(trains) > 1 else None
    return {
        "turns_evaluated": evaluated,
        "turns_admitted": len(admitted),
        "turns_declined": len(declined),
        "first_admit_turn": admitted[0]["turn"] if admitted else None,
        "admit_to_decline_flips": flips,
        "decline_reasons": reasons,
        "first_turn": per_turn[0] if per_turn else None,
        "third_troll_train_turn": third["turn"] if third else None,
        "third_troll_spec": third["spec"] if third else None,
        "declined_game": evaluated > 0 and third is None,
        "never_evaluated": evaluated == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", type=Path, default=HERE / "champion-wood-gate-v6-instrument.rs")
    ap.add_argument("--records", type=Path,
                    default=REPO / "local_claude_1" / "third-troll" / "smoke-maps-seed0.jsonl")
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--out", type=Path, default=HERE / "results" / "gate-read.json")
    args = ap.parse_args()

    arm_text = args.arm.read_text()
    assert arm_text.count(ANCHOR) == 1, "the debug anchor must occur exactly once in the arm"
    debug_text = arm_text.replace(ANCHOR, ANCHOR + DEBUG, 1)
    res_text = smoke.RESIDENT.read_text()
    plan = [json.loads(l) for l in open(args.records) if l.strip()]

    games = []
    with tempfile.TemporaryDirectory(prefix="wood-gate-read-") as wd:
        wd = Path(wd)
        arm_bin, dbg_bin, res_bin = wd / "arm", wd / "dbg", wd / "res"
        sh.compile_text(arm_text, arm_bin, crate="wood_gate_arm")
        sh.compile_text(debug_text, dbg_bin, crate="wood_gate_debug")
        sh.compile_text(res_text, res_bin, crate="wood_gate_resident")
        for i, item in enumerate(plan):
            rec, draw, profile = item["rec"], item["draw"], item["profile"]
            arm_lines, arm_inv, arm_ref = play(arm_bin, smoke.make_referee(rec, draw, profile), args.turns, None)
            log = wd / f"gate-{i}.log"
            dbg_lines, _, _ = play(dbg_bin, smoke.make_referee(rec, draw, profile), args.turns, log)
            res_lines, res_inv, res_ref = play(res_bin, smoke.make_referee(rec, draw, profile), args.turns, None)
            same = arm_lines == dbg_lines
            per_turn = read_gate_log(log)
            trains = smoke.all_trains(arm_lines)
            g = {
                "index": i, "map_hash": rec["map_hash"], "profile": profile, "draw": draw,
                "debug_variant_same_commands": same,
                "trains": trains,
                "gate": summarise_game(per_turn, trains),
                "wood_banked": {str(t): {"arm": arm_inv[t - 1][5], "resident": res_inv[t - 1][5]}
                                for t in CHECKPOINTS if t <= len(arm_inv)},
                "own_score": {"arm": smoke.own_score(arm_ref.inv), "resident": smoke.own_score(res_ref.inv)},
                "opp_score": {"arm": smoke.own_score(arm_ref.opp_inv), "resident": smoke.own_score(res_ref.opp_inv)},
                "gate_turns": per_turn,
                "wood_by_turn": {"arm": [inv[5] for inv in arm_inv], "resident": [inv[5] for inv in res_inv]},
            }
            games.append(g)
            gt = g["gate"]
            print(f"{'OK ' if same else 'BAD'} {rec['map_hash'][:12]} {profile:<18} eval {gt['turns_evaluated']:3d} "
                  f"admit {gt['turns_admitted']:3d} decline {gt['turns_declined']:3d} flips {gt['admit_to_decline_flips']} "
                  f"third {gt['third_troll_train_turn']} {gt['third_troll_spec'] or '-':<8} "
                  f"reasons {gt['decline_reasons']} wood50 {g['wood_banked'].get('50')} wood100 {g['wood_banked'].get('100')} "
                  f"score {g['own_score']['arm']} vs {g['own_score']['resident']}")

    if not all(g["debug_variant_same_commands"] for g in games):
        print("REFUSED: the debug variant's commands differ from the arm's on some map", file=sys.stderr)
        return 2
    with_third = [g for g in games if g["gate"]["third_troll_train_turn"] is not None]
    declined_games = [g for g in games if g["gate"]["declined_game"]]
    never = [g for g in games if g["gate"]["never_evaluated"]]
    reasons = {}
    for g in games:
        for k, v in g["gate"]["decline_reasons"].items():
            reasons[k] = reasons.get(k, 0) + v
    specs = {}
    for g in with_third:
        specs[g["gate"]["third_troll_spec"]] = specs.get(g["gate"]["third_troll_spec"], 0) + 1
    turns3 = sorted(g["gate"]["third_troll_train_turn"] for g in with_third)
    wood = {str(t): {"arm": sum(g["wood_banked"][str(t)]["arm"] for g in games),
                     "resident": sum(g["wood_banked"][str(t)]["resident"] for g in games)}
            for t in CHECKPOINTS}
    summary = {
        "what": "the wood-charging gate's decisions on the smoke slice, read from a stderr-only debug variant "
                "whose commands equal the arm's on every map",
        "arm": str(args.arm.relative_to(REPO)), "arm_sha256": sha(arm_text),
        "resident": str(smoke.RESIDENT.relative_to(REPO)), "resident_sha256": sha(res_text),
        "records": str(args.records.relative_to(REPO)), "turns": args.turns,
        "turn_convention": "game turn = 1-based index of the command line answered (not the replay's frame index)",
        "games": len(games),
        "games_with_third_troll": len(with_third),
        "games_declined": len(declined_games),
        "games_never_evaluated": len(never),
        "games_with_flips": sum(1 for g in games if g["gate"]["admit_to_decline_flips"] > 0),
        "turns_evaluated": sum(g["gate"]["turns_evaluated"] for g in games),
        "turns_admitted": sum(g["gate"]["turns_admitted"] for g in games),
        "turns_declined": sum(g["gate"]["turns_declined"] for g in games),
        "decline_reasons_turns": reasons,
        "third_troll_game_turns": turns3,
        "third_troll_median_game_turn": statistics.median(turns3) if turns3 else None,
        "third_troll_specs": specs,
        "wood_banked_total": wood,
        "own_score_total": {"arm": sum(g["own_score"]["arm"] for g in games),
                            "resident": sum(g["own_score"]["resident"] for g in games)},
        "per_game": games,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_game"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
