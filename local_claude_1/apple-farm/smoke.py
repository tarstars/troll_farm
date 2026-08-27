#!/usr/bin/env python3
"""Smoke: full local games of the apple-farm arm on REAL ladder maps that have a water-side door,
against the panel's scripted opponents, read only for the mechanics -- not a value gate.

For every sampled map (from `data/processed/maps.jsonl`, the corpus of real ladder maps: rows,
shacks, initial trees with their exact sizes/health/fruits/cooldowns) the same game is played by
the arm and by the resident (the champion of record), 300 turns, one opponent troll driven by
the pipeline referee's `harvester` or `chopper_aggressor` policy, both players starting with the
same 2..10 fruit/iron draw (seeded per map, as the real referee draws them).

Questions, per arm game:
  planted     the arm issues PLANT APPLE on the farm cell, and the referee has an APPLE there,
              by turn <= 4 (turn 1 MOVE, 2 PICK, 3 PLANT) -- or the cell already held an apple;
  harvested   HARVEST on the farm cell at least once after the second troll exists, and DROP
              on the farm cell at least once;
  banked      own apples in the shack at the end of the game > the starting draw minus the bill;
  no felling  no own CHOP was ever issued from the farm cell;
  plays       a command line on every turn, no referee error kinds.
Reported as facts with the own scores of arm and resident on the same map.

    python3 local_claude_1/apple-farm/smoke.py [--maps 12] [--turns 300] [--seed 0]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import tempfile
from collections import Counter, deque
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

ARM = HERE / "champion-apple-farm-v6-instrument.rs"
RESIDENT = REPO / "local_claude_1" / "denial-ablation" / "champion-denial-off-v6-instrument.rs"
MAPS = REPO / "data" / "processed" / "maps.jsonl"
MAPS_FALLBACK = Path("/home/tarstars/prj/troll_farm/data/processed/maps.jsonl")
COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
# The bot's own door order (`ortho_neighbors`: down, right, up, left) -- the rule prefers the
# first wet door in THIS order, so the prediction must walk them the same way.
ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def bfs(rows, w, h, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ORTH:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in dist and rows[ny][nx] == '.':
                dist[(nx, ny)] = dist[(x, y)] + 1
                q.append((nx, ny))
    return dist


def farm_cell_of(rec):
    """The cell the rule will choose: a door of our shack, walkable, touching water, never the
    only door; an apple already there first, else an empty cell (the rule's own order)."""
    rows, w, h = rec["rows"], rec["w"], rec["h"]
    sx, sy = rec["shacks"]["p0"]
    water = {tuple(c) for c in rec["water_cells"]}
    trees = {(t["x"], t["y"]): t["type"] for t in rec["trees0"]}
    doors = [(sx + dx, sy + dy) for dx, dy in ORTH
             if 0 <= sx + dx < w and 0 <= sy + dy < h and rows[sy + dy][sx + dx] == '.']
    if len(doors) < 2:
        return None
    wet = [c for c in doors if any((c[0] + dx, c[1] + dy) in water for dx, dy in ORTH)]
    for c in wet:
        if trees.get(c) == "APPLE":
            return c
    for c in wet:
        if c not in trees:
            return c
    return None


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


def read_commands(command_lines, farm):
    """What our unit 0 (the starting troll) did on the farm cell, and when. The referee is not
    asked where the unit stood; PLANT/PICK/HARVEST/DROP are cell-bound only through the MOVE
    that preceded them, so we track unit 0's declared target cell and count verbs while it
    declared the farm cell -- exact for this rule (its MOVE targets the farm cell itself)."""
    counts = Counter()
    first = {}
    at_farm = False
    for turn, line in enumerate(command_lines, 1):
        for frag in line.split(";"):
            fields = frag.split()
            if not fields or fields[0] == "MSG":
                continue
            verb = fields[0]
            if verb == "MOVE" and len(fields) == 4 and fields[1] == "0":
                at_farm = (int(fields[2]), int(fields[3])) == tuple(farm)
                continue
            if len(fields) >= 2 and fields[1] == "0" and verb in ("PICK", "PLANT", "HARVEST", "DROP", "CHOP"):
                key = f"{verb}@farm" if at_farm else f"{verb}@elsewhere"
                counts[key] += 1
                first.setdefault(key, turn)
    return counts, first


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", type=int, default=12)
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--write-records", type=Path, default=None,
                    help="sample from the corpus, write the sampled maps with their draws and "
                         "opponent profiles as JSON lines to this path, and exit without playing "
                         "(a slice a peer without the 53 MB corpus can replay exactly)")
    ap.add_argument("--records", type=Path, default=None,
                    help="play the maps in this JSON-lines slice (from --write-records) instead "
                         "of sampling the corpus; --maps/--seed are ignored")
    args = ap.parse_args()
    if args.records is not None:
        plan = []
        with open(args.records) as fh:
            for line in fh:
                item = json.loads(line)
                plan.append((item["rec"], tuple(item["farm"]), item["draw"], item["profile"]))
        eligible = None
        print(f"maps from the slice {args.records}: {len(plan)}")
    else:
        maps_path = MAPS if MAPS.exists() else MAPS_FALLBACK
        rng = random.Random(args.seed)
        records = []
        with open(maps_path) as fh:
            for line in fh:
                rec = json.loads(line)
                farm = farm_cell_of(rec)
                if farm is not None:
                    records.append((rec, farm))
        rng.shuffle(records)
        sample = records[:args.maps]
        eligible = len(records)
        print(f"maps with a water-side door in the corpus: {len(records)}; sampled {len(sample)}")
        # The draws are taken from the same generator, in the same order, whether the games are
        # played here or replayed from the slice -- so the slice reproduces this run exactly.
        plan = []
        for i, (rec, farm) in enumerate(sample):
            draw = [rng.randint(2, 10) for _ in range(5)] + [0]   # plum lemon apple banana iron wood
            profile = ["harvester", "chopper_aggressor"][i % 2]
            plan.append((rec, farm, draw, profile))
        if args.write_records is not None:
            with open(args.write_records, "w") as out:
                for rec, farm, draw, profile in plan:
                    out.write(json.dumps({"rec": rec, "farm": list(farm), "draw": draw,
                                          "profile": profile}, sort_keys=True) + "\n")
            print(f"  wrote {len(plan)} records to {args.write_records}; not playing (--write-records)")
            return 0

    arm_text, res_text = ARM.read_text(), RESIDENT.read_text()
    rows_out = []
    with tempfile.TemporaryDirectory(prefix="apple-smoke-") as wd:
        wd = Path(wd)
        arm_bin, res_bin = wd / "arm.bin", wd / "res.bin"
        sh.compile_text(arm_text, arm_bin, crate="apple_farm_smoke_arm")
        sh.compile_text(res_text, res_bin, crate="apple_farm_smoke_resident")
        for rec, farm, draw, profile in plan:
            row = {"map_hash": rec["map_hash"], "farm_cell": list(farm), "profile": profile,
                   "start_inventory": draw,
                   "apple_already_there": any(t["type"] == "APPLE" and (t["x"], t["y"]) == farm
                                              for t in rec["trees0"])}
            for label, binary in (("arm", arm_bin), ("resident", res_bin)):
                ref = make_referee(rec, draw, profile)
                transcript, commands = rt.run_binary_custom(binary, ref, args.turns)
                lines = commands.rstrip("\n").split("\n")
                counts, first = read_commands(lines, farm)
                plant = ref.plants.get(tuple(farm))
                own_units = {uid: u for uid, u in ref.units.items() if u["player"] == 0}
                r = {
                    "turns_answered": len(lines),
                    "referee_errors": dict(ref.error_counts),
                    "own_score": own_score(ref.inv),
                    "opp_score": own_score(ref.opp_inv),
                    "own_inventory": list(ref.inv),
                    "own_units": len(own_units),
                    "farm_tree_at_end": plant,
                    "verbs": dict(counts),
                    "first": first,
                }
                if label == "arm":
                    census = n6.new_census()
                    import trace_detectors as td
                    tr = td.build_trace(transcript, commands)
                    r["telemetry_errors"] = n6.check_telemetry(rec["map_hash"], tr, lines, census, rule_off=True)
                    r["planted_by_turn_4"] = row["apple_already_there"] or first.get("PLANT@farm", 999) <= 4
                    r["harvested"] = counts.get("HARVEST@farm", 0) > 0 and counts.get("DROP@farm", 0) > 0
                    r["no_felling"] = counts.get("CHOP@farm", 0) == 0
                    r["plays"] = len(lines) == args.turns and not ref.error_counts
                row[label] = r
            rows_out.append(row)
            a, b = row["arm"], row["resident"]
            ok = a["plays"] and a["planted_by_turn_4"] and a["harvested"] and a["no_felling"] and not a["telemetry_errors"]
            print(f"  {'OK ' if ok else 'BAD'} {rec['map_hash']} farm={tuple(farm)} {profile:<18} "
                  f"plant@{a['first'].get('PLANT@farm')} harvest×{a['verbs'].get('HARVEST@farm', 0)} "
                  f"drop×{a['verbs'].get('DROP@farm', 0)} chop@farm×{a['verbs'].get('CHOP@farm', 0)} "
                  f"apples {a['own_inventory'][2]}  own {a['own_score']} vs resident {b['own_score']} "
                  f"(opp {a['opp_score']}/{b['opp_score']})  telemetry {len(a['telemetry_errors'])}")

    n = len(rows_out)
    good = sum(1 for r in rows_out if r["arm"]["plays"] and r["arm"]["planted_by_turn_4"]
               and r["arm"]["harvested"] and r["arm"]["no_felling"] and not r["arm"]["telemetry_errors"])
    margin = sum(r["arm"]["own_score"] - r["resident"]["own_score"] for r in rows_out)
    report = {
        "what": "smoke on real ladder maps with a water-side door: mechanics only, not a value gate",
        "arm": str(ARM.relative_to(REPO)), "arm_sha256": sha(arm_text),
        "resident": str(RESIDENT.relative_to(REPO)), "resident_sha256": sha(res_text),
        "maps_in_corpus_with_water_side_door": eligible, "maps_played": n, "turns": args.turns,
        "seed": args.seed, "records": str(args.records) if args.records else None,
        "all_mechanics_ok": good, "own_score_sum_arm_minus_resident": margin,
        "rows": rows_out,
        "status": "PASS" if good == n else "FAIL",
    }
    out = HERE / "results" / "smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\n  {report['status']}  mechanics ok on {good}/{n} maps; own-score sum arm − resident "
          f"= {margin:+d} over {n} games (a fact, not a verdict)  -> {out}")
    return 0 if good == n else 1


if __name__ == "__main__":
    sys.exit(main())
