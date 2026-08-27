#!/usr/bin/env python3
"""Smoke: full local games of the floor arm on REAL ladder maps against the panel's scripted
opponents, read only for the mechanics -- not a value gate. Adapted from
`local_claude_1/apple-farm/smoke.py`.

For every sampled map (from `data/processed/maps.jsonl`, the corpus of real ladder maps: rows,
shacks, iron, initial trees with their exact sizes/health/fruits/cooldowns) the same game is
played by the arm and by the resident (the champion of record), 300 turns, one opponent troll
driven by the pipeline referee's `harvester` or `chopper_aggressor` policy, both players starting
with the same 2..10 fruit/iron draw (seeded per map, as the real referee draws them).

Questions, per arm game:
  trains      the arm issues a TRAIN and the referee has two own trolls afterwards;
  floored     that TRAIN is never weaker than speed 2 / carry 2 / chop 2 (harvest 0);
  plays       a command line on every turn, no referee error kinds;
  telemetry   the v6 line decodes on every turn.
Reported as facts: the arm's and the resident's second troll (spec and turn) on the same map, the
resident's share of below-floor trolls on the sample, and the own scores of both.

    python3 local_claude_1/the-floor/smoke.py [--maps 24] [--turns 300] [--seed 0]
    python3 local_claude_1/the-floor/smoke.py --write-records slice.jsonl   # for a peer
    python3 local_claude_1/the-floor/smoke.py --records slice.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate6", "claude_1/cure3"):
    sys.path.insert(0, str(REPO / _p))

import fuzz_panel as fp             # noqa: E402
import regression_tests as rt       # noqa: E402
import semantic_harness as sh       # noqa: E402
import narrate6 as n6               # noqa: E402

ARM = HERE / "champion-the-floor-v6-instrument.rs"
RESIDENT = REPO / "local_claude_1" / "denial-ablation" / "champion-denial-off-v6-instrument.rs"
MAPS = REPO / "data" / "processed" / "maps.jsonl"
MAPS_FALLBACK = Path("/home/tarstars/prj/troll_farm/data/processed/maps.jsonl")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def make_referee(rec, inventory, profile):
    plants = {}
    for t in rec["trees0"]:
        plants[(t["x"], t["y"])] = {"kind": t["type"], "size": t["size"], "health": t["health"],
                                    "fruits": t["fruits"], "cd": t["cur_cd"]}
    p0, p1 = tuple(rec["shacks"]["p0"]), tuple(rec["shacks"]["p1"])
    units = {
        0: {"player": 0, "cell": p0, "speed": 1, "cap": 1, "harvest": 1, "chop": 1, "carry": [0] * 6},
        1: {"player": 1, "cell": p1, "speed": 1, "cap": 1, "harvest": 1, "chop": 1, "carry": [0] * 6},
    }
    ref = fp.FuzzReferee(rec["rows"], list(inventory), plants, units, profile)
    ref.opp_inv = list(inventory)
    return ref


def own_score(inv):
    return sum(inv[0:4]) + 4 * inv[5]


def first_train(lines):
    """The first TRAIN in our command stream: turn and 'speed carry harvest chop'."""
    for turn, line in enumerate(lines, 1):
        for frag in line.split(";"):
            fields = frag.split()
            if fields and fields[0] == "TRAIN" and len(fields) >= 5:
                return {"turn": turn, "spec": " ".join(fields[1:5]),
                        "stats": [int(v) for v in fields[1:5]]}
    return None


def floored(train):
    return train is not None and train["stats"][0] >= 2 and train["stats"][1] >= 2 and train["stats"][3] >= 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", type=int, default=24)
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--write-records", type=Path, default=None,
                    help="sample from the corpus, write the sampled maps with their draws and "
                         "opponent profiles as JSON lines to this path, and exit without playing")
    ap.add_argument("--records", type=Path, default=None,
                    help="play the maps in this JSON-lines slice instead of sampling the corpus")
    args = ap.parse_args()
    if args.records is not None:
        plan = []
        with open(args.records) as fh:
            for line in fh:
                item = json.loads(line)
                plan.append((item["rec"], item["draw"], item["profile"]))
        corpus = None
        print(f"maps from the slice {args.records}: {len(plan)}")
    else:
        maps_path = MAPS if MAPS.exists() else MAPS_FALLBACK
        rng = random.Random(args.seed)
        records = []
        with open(maps_path) as fh:
            for line in fh:
                records.append(json.loads(line))
        corpus = len(records)
        rng.shuffle(records)
        sample = records[:args.maps]
        print(f"maps in the corpus: {corpus}; sampled {len(sample)}")
        plan = []
        for i, rec in enumerate(sample):
            draw = [rng.randint(2, 10) for _ in range(5)] + [0]   # plum lemon apple banana iron wood
            profile = ["harvester", "chopper_aggressor"][i % 2]
            plan.append((rec, draw, profile))
        if args.write_records is not None:
            with open(args.write_records, "w") as out:
                for rec, draw, profile in plan:
                    out.write(json.dumps({"rec": rec, "draw": draw, "profile": profile},
                                         sort_keys=True) + "\n")
            print(f"  wrote {len(plan)} records to {args.write_records}; not playing (--write-records)")
            return 0

    arm_text, res_text = ARM.read_text(), RESIDENT.read_text()
    rows_out = []
    with tempfile.TemporaryDirectory(prefix="floor-smoke-") as wd:
        wd = Path(wd)
        arm_bin, res_bin = wd / "arm.bin", wd / "res.bin"
        sh.compile_text(arm_text, arm_bin, crate="the_floor_smoke_arm")
        sh.compile_text(res_text, res_bin, crate="the_floor_smoke_resident")
        for rec, draw, profile in plan:
            row = {"map_hash": rec["map_hash"], "profile": profile, "start_inventory": draw}
            for label, binary in (("arm", arm_bin), ("resident", res_bin)):
                ref = make_referee(rec, draw, profile)
                transcript, commands = rt.run_binary_custom(binary, ref, args.turns)
                lines = commands.rstrip("\n").split("\n")
                own_units = {uid: u for uid, u in ref.units.items() if u["player"] == 0}
                train = first_train(lines)
                r = {
                    "turns_answered": len(lines),
                    "referee_errors": dict(ref.error_counts),
                    "own_score": own_score(ref.inv),
                    "opp_score": own_score(ref.opp_inv),
                    "own_inventory": list(ref.inv),
                    "own_units": len(own_units),
                    "train": train,
                    "floored": floored(train),
                }
                if label == "arm":
                    census = n6.new_census()
                    import trace_detectors as td
                    tr = td.build_trace(transcript, commands)
                    r["telemetry_errors"] = n6.check_telemetry(rec["map_hash"], tr, lines, census, rule_off=True)
                    r["trains"] = train is not None and len(own_units) >= 2
                    r["plays"] = len(lines) == args.turns and not ref.error_counts
                row[label] = r
            rows_out.append(row)
            a, b = row["arm"], row["resident"]
            ok = a["plays"] and a["trains"] and a["floored"] and not a["telemetry_errors"]
            ta, tb = a["train"] or {}, b["train"] or {}
            print(f"  {'OK ' if ok else 'BAD'} {rec['map_hash']} {profile:<18} draw {draw[:5]}  "
                  f"arm TRAIN {ta.get('spec')} @{ta.get('turn')}  resident {tb.get('spec')} @{tb.get('turn')}"
                  f"{'' if b['floored'] else ' (below the floor)'}  own {a['own_score']} vs {b['own_score']}  "
                  f"telemetry {len(a['telemetry_errors'])}")

    n = len(rows_out)
    good = sum(1 for r in rows_out if r["arm"]["plays"] and r["arm"]["trains"] and r["arm"]["floored"]
               and not r["arm"]["telemetry_errors"])
    margin = sum(r["arm"]["own_score"] - r["resident"]["own_score"] for r in rows_out)
    res_below = [r["map_hash"] for r in rows_out if r["resident"]["train"] and not r["resident"]["floored"]]
    changed = [r for r in rows_out if r["map_hash"] in res_below]
    margin_changed = sum(r["arm"]["own_score"] - r["resident"]["own_score"] for r in changed)
    arm_turns = sorted(r["arm"]["train"]["turn"] for r in rows_out if r["arm"]["train"])
    res_turns = sorted(r["resident"]["train"]["turn"] for r in rows_out if r["resident"]["train"])
    report = {
        "what": "smoke on real ladder maps: mechanics only, not a value gate",
        "arm": str(ARM.relative_to(REPO)), "arm_sha256": sha(arm_text),
        "resident": str(RESIDENT.relative_to(REPO)), "resident_sha256": sha(res_text),
        "maps_in_corpus": corpus, "maps_played": n, "turns": args.turns,
        "seed": args.seed, "records": str(args.records) if args.records else None,
        "all_mechanics_ok": good,
        "resident_below_floor_maps": res_below,
        "own_score_sum_arm_minus_resident": margin,
        "own_score_sum_arm_minus_resident_on_resident_below_floor_maps": margin_changed,
        "arm_train_turn_median": arm_turns[len(arm_turns) // 2] if arm_turns else None,
        "resident_train_turn_median": res_turns[len(res_turns) // 2] if res_turns else None,
        "rows": rows_out,
        "status": "PASS" if good == n else "FAIL",
    }
    out = HERE / "results" / "smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\n  {report['status']}  mechanics ok on {good}/{n} maps; the resident trained below the "
          f"floor on {len(res_below)}/{n}; training turn median arm {report['arm_train_turn_median']} "
          f"vs resident {report['resident_train_turn_median']}; own-score sum arm − resident = "
          f"{margin:+d} over {n} games ({margin_changed:+d} on the {len(changed)} changed maps) "
          f"(a fact, not a verdict)  -> {out}")
    return 0 if good == n else 1


if __name__ == "__main__":
    sys.exit(main())
