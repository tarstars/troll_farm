#!/usr/bin/env python3
"""Smoke: full local games of the third-troll arm on REAL ladder maps against the panel's scripted
opponents, read only for the mechanics -- not a value gate. Adapted from
`local_claude_1/the-floor/smoke.py`.

For every sampled map (from `data/processed/maps.jsonl`, the corpus of real ladder maps) the same
game is played by the arm and by the resident (the champion of record), 300 turns, one opponent
troll driven by the pipeline referee's `harvester` or `chopper_aggressor` policy, both players
starting with the same 2..10 fruit/iron draw (seeded per map).

Questions, per arm game (the card's "done means" 3):
  plays        a command line on every turn, no referee error kinds;
  telemetry    the v6 line decodes on every turn;
  third        whether a third troll is trained, at which turn, with which talents (must be
               2 3 0 3), and how many turns the two trolls spent funding it (from the second
               TRAIN to the third);
  no stall     during the funding window (and after the horizon closes without a third troll,
               turn > 200) no own troll idles STALL_TURNS consecutive turns more than the resident's
               longest idle run over the same window on the same map -- a troll that never resumes
               work is a defect, a map with no trees left is not (both bots wait there);
  never four   no fourth TRAIN.
Reported as facts: the arm's and the resident's TRAINs on the same map, the share of games with a
third troll and its median turn (the top four: 56-84 % of games, median turn 95-118), and the own
scores of both (a sanity margin, not a value gate).

    python3 local_claude_1/third-troll/smoke.py [--maps 24] [--turns 300] [--seed 0]
    python3 local_claude_1/third-troll/smoke.py --write-records slice.jsonl   # for a peer
    python3 local_claude_1/third-troll/smoke.py --records slice.jsonl
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

ARM = HERE / "champion-third-troll-v6-instrument.rs"
RESIDENT = REPO / "local_claude_1" / "denial-ablation" / "champion-denial-off-v6-instrument.rs"
MAPS = REPO / "data" / "processed" / "maps.jsonl"
MAPS_FALLBACK = Path("/home/tarstars/prj/troll_farm/data/processed/maps.jsonl")
THIRD_SPEC = "2 3 0 3"
HORIZON_LAST_TURN = 200      # the third troll is wanted while >= 100 of 300 turns remain
STALL_TURNS = 20


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


def all_trains(lines):
    """Every TRAIN in our command stream: [{turn, spec, stats}, ...] in order."""
    out = []
    for turn, line in enumerate(lines, 1):
        for frag in line.split(";"):
            fields = frag.split()
            if fields and fields[0] == "TRAIN" and len(fields) >= 5:
                out.append({"turn": turn, "spec": " ".join(fields[1:5]),
                            "stats": [int(v) for v in fields[1:5]]})
    return out


def acting_ids(line):
    """The unit ids that received a command other than WAIT on this line (MSG/TRAIN carry none)."""
    ids = set()
    for frag in line.split(";"):
        fields = frag.split()
        if len(fields) >= 2 and fields[0] in ("MOVE", "HARVEST", "CHOP", "MINE", "PLANT", "DROP",
                                              "PICK"):
            try:
                ids.add(int(fields[1]))
            except ValueError:
                pass
    return ids


def idle_streaks(lines, unit_ids, first_turn, last_turn):
    """Per unit, the longest run of consecutive turns in [first_turn, last_turn] without a command."""
    best = {uid: 0 for uid in unit_ids}
    run = {uid: 0 for uid in unit_ids}
    for turn in range(first_turn, min(last_turn, len(lines)) + 1):
        acting = acting_ids(lines[turn - 1])
        for uid in unit_ids:
            if uid in acting:
                run[uid] = 0
            else:
                run[uid] += 1
                best[uid] = max(best[uid], run[uid])
    return best


def read_game(lines, ref, turns):
    own_units = {uid: u for uid, u in ref.units.items() if u["player"] == 0}
    trains = all_trains(lines)
    second = trains[0] if trains else None
    third = trains[1] if len(trains) > 1 else None
    r = {
        "turns_answered": len(lines),
        "referee_errors": dict(ref.error_counts),
        "own_score": own_score(ref.inv),
        "opp_score": own_score(ref.opp_inv),
        "own_inventory": list(ref.inv),
        "own_units": len(own_units),
        "own_unit_stats": {str(uid): [u["speed"], u["cap"], u["harvest"], u["chop"]]
                           for uid, u in sorted(own_units.items())},
        "trains": trains,
        "plants": [(turn, frag.split()[2]) for turn, line in enumerate(lines, 1)
                   for frag in line.split(";") if frag.split()[:1] == ["PLANT"] and len(frag.split()) >= 3],
        "second_troll": second,
        "third_troll": third,
        "funding_turns": (third["turn"] - second["turn"]) if second and third else None,
    }
    # The funding window: from the second TRAIN to the third TRAIN, or to the horizon's end.
    if second is not None:
        window_end = third["turn"] if third else min(HORIZON_LAST_TURN, turns)
        ids_in_window = sorted(uid for uid in own_units
                               if uid != (max(own_units) if third else None))
        r["funding_window"] = [second["turn"] + 1, window_end]
        r["funding_idle_streaks"] = idle_streaks(lines, ids_in_window, second["turn"] + 1, window_end)
        if third is None and turns > HORIZON_LAST_TURN:
            after = idle_streaks(lines, ids_in_window, HORIZON_LAST_TURN + 1, turns - 20)
            r["after_horizon_idle_streaks"] = after
    return r


def main() -> int:
    global THIRD_SPEC
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", type=int, default=24)
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--write-records", type=Path, default=None,
                    help="sample from the corpus, write the sampled maps with their draws and "
                         "opponent profiles as JSON lines to this path, and exit without playing")
    ap.add_argument("--records", type=Path, default=None,
                    help="play the maps in this JSON-lines slice instead of sampling the corpus")
    ap.add_argument("--arm", type=Path, default=ARM, help="another arm to smoke (a variant study)")
    ap.add_argument("--out", type=Path, default=HERE / "results" / "smoke.json")
    ap.add_argument("--third-spec", default=THIRD_SPEC, help="the expected third troll's talents")
    args = ap.parse_args()
    THIRD_SPEC = args.third_spec
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

    arm_text, res_text = args.arm.read_text(), RESIDENT.read_text()
    rows_out = []
    with tempfile.TemporaryDirectory(prefix="third-troll-smoke-") as wd:
        wd = Path(wd)
        arm_bin, res_bin = wd / "arm.bin", wd / "res.bin"
        sh.compile_text(arm_text, arm_bin, crate="third_troll_smoke_arm")
        sh.compile_text(res_text, res_bin, crate="third_troll_smoke_resident")
        for rec, draw, profile in plan:
            row = {"map_hash": rec["map_hash"], "profile": profile, "start_inventory": draw}
            for label, binary in (("arm", arm_bin), ("resident", res_bin)):
                ref = make_referee(rec, draw, profile)
                transcript, commands = rt.run_binary_custom(binary, ref, args.turns)
                lines = commands.rstrip("\n").split("\n")
                r = read_game(lines, ref, args.turns)
                if label == "resident" and "funding_window" in row["arm"]:
                    a = row["arm"]
                    w0, w1 = a["funding_window"]
                    ids = sorted(uid for uid, u in ref.units.items() if u["player"] == 0)[:2]
                    r["idle_streaks_over_arm_window"] = idle_streaks(lines, ids, w0, w1)
                    if "after_horizon_idle_streaks" in a:
                        r["after_horizon_idle_streaks"] = idle_streaks(
                            lines, ids, HORIZON_LAST_TURN + 1, args.turns - 20)
                    arm_max = max(list(a["funding_idle_streaks"].values()) or [0])
                    res_max = max(list(r["idle_streaks_over_arm_window"].values()) or [0])
                    arm_after = max(list(a.get("after_horizon_idle_streaks", {}).values()) or [0])
                    res_after = max(list(r.get("after_horizon_idle_streaks", {}).values()) or [0])
                    a["idle_max_funding_arm_vs_resident"] = [arm_max, res_max]
                    a["idle_max_after_horizon_arm_vs_resident"] = [arm_after, res_after]
                    a["stalled"] = (arm_max - res_max >= STALL_TURNS) or (arm_after - res_after >= STALL_TURNS)
                    a["mechanics_ok"] = a["mechanics_ok_before_stall_check"] and not a["stalled"]
                if label == "arm":
                    census = n6.new_census()
                    import trace_detectors as td
                    tr = td.build_trace(transcript, commands)
                    r["telemetry_errors"] = n6.check_telemetry(rec["map_hash"], tr, lines, census,
                                                               rule_off=True)
                    r["plays"] = len(lines) == args.turns and not ref.error_counts
                    third = r["third_troll"]
                    r["third_spec_ok"] = third is None or third["spec"] == THIRD_SPEC
                    r["third_within_horizon"] = third is None or third["turn"] <= HORIZON_LAST_TURN
                    r["never_four"] = len(r["trains"]) <= 2 and r["own_units"] <= 3
                    r["third_counted_by_referee"] = third is None or r["own_units"] == 3
                    r["stalled"] = False
                    r["mechanics_ok_before_stall_check"] = (
                        r["plays"] and not r["telemetry_errors"] and r["third_spec_ok"]
                        and r["third_within_horizon"] and r["never_four"]
                        and r["third_counted_by_referee"])
                    r["mechanics_ok"] = r["mechanics_ok_before_stall_check"]
                row[label] = r
            rows_out.append(row)
            a, b = row["arm"], row["resident"]
            t2, t3 = a["second_troll"] or {}, a["third_troll"] or {}
            rb = b["second_troll"] or {}
            print(f"  {'OK ' if a['mechanics_ok'] else 'BAD'} {rec['map_hash']} {profile:<18} "
                  f"draw {draw[:5]}  arm 2nd {t2.get('spec')} @{t2.get('turn')}  "
                  f"3rd {t3.get('spec') or '-'} @{t3.get('turn') or '-'} "
                  f"(funding {a['funding_turns']} turns, idle max arm/resident "
                  f"{a.get('idle_max_funding_arm_vs_resident')} after horizon "
                  f"{a.get('idle_max_after_horizon_arm_vs_resident')})  "
                  f"plants {len(a['plants'])} (first @{a['plants'][0][0] if a['plants'] else '-'})  "
                  f"resident 2nd {rb.get('spec')} @{rb.get('turn')}  "
                  f"own {a['own_score']} vs {b['own_score']}  telemetry {len(a['telemetry_errors'])}")

    n = len(rows_out)
    good = sum(1 for r in rows_out if r["arm"]["mechanics_ok"])
    with_third = [r for r in rows_out if r["arm"]["third_troll"]]
    third_turns = sorted(r["arm"]["third_troll"]["turn"] for r in with_third)
    funding = sorted(r["arm"]["funding_turns"] for r in with_third)
    margin = sum(r["arm"]["own_score"] - r["resident"]["own_score"] for r in rows_out)
    margin_third = sum(r["arm"]["own_score"] - r["resident"]["own_score"] for r in with_third)
    stalled = [r["map_hash"] for r in rows_out if r["arm"]["stalled"]]
    no_third_reason = {}
    for r in rows_out:
        a = r["arm"]
        if a["third_troll"] is None:
            key = "no second troll" if a["second_troll"] is None else "bill never paid by turn 200"
            no_third_reason[key] = no_third_reason.get(key, 0) + 1
    report = {
        "what": "smoke on real ladder maps: mechanics only, not a value gate",
        "arm": str(args.arm), "arm_sha256": sha(arm_text), "third_spec_expected": THIRD_SPEC,
        "resident": str(RESIDENT.relative_to(REPO)), "resident_sha256": sha(res_text),
        "maps_in_corpus": corpus, "maps_played": n, "turns": args.turns,
        "seed": args.seed, "records": str(args.records) if args.records else None,
        "all_mechanics_ok": good,
        "games_with_third_troll": len(with_third),
        "third_troll_turn_median": third_turns[len(third_turns) // 2] if third_turns else None,
        "third_troll_turns": third_turns,
        "funding_turns_median": funding[len(funding) // 2] if funding else None,
        "no_third_troll_reasons": no_third_reason,
        "stalled_maps": stalled,
        "own_score_sum_arm_minus_resident": margin,
        "own_score_sum_arm_minus_resident_on_third_troll_maps": margin_third,
        "rows": rows_out,
        "status": "PASS" if good == n else "FAIL",
    }
    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\n  {report['status']}  mechanics ok on {good}/{n} maps; a third troll in "
          f"{len(with_third)}/{n} games, median turn {report['third_troll_turn_median']}, funding "
          f"median {report['funding_turns_median']} turns; no third troll: {no_third_reason}; "
          f"stalled: {stalled}; own-score sum arm − resident = {margin:+d} over {n} games "
          f"({margin_third:+d} on the {len(with_third)} third-troll maps) (a fact, not a verdict)"
          f"  -> {out}")
    return 0 if good == n else 1


if __name__ == "__main__":
    sys.exit(main())
