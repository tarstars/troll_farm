"""Independent verifier for claim (a): every schedule under claude_1/opening-solver/schedules/
is referee-exact.

This does NOT import or call claude_1's replay.py. It only reads replay.py (already done, by
hand) to learn the schedule JSON format and how the initial GameState is built from a panel
record. The state-construction logic below was independently cross-checked against the raw
panel JSON (rec['shacks'], rec['iron_cells'], rec['water_cells'] all cross-verified against the
ASCII 'rows' before trusting the '0'/'1'/'+'/'~'/'.' character mapping).

For each of the 400 schedule files and each variant inside it (free, chop2, chop1, same where
present): replay `commands` turn by turn through the real sim/engine.py `step()`, our seat's
commands only, opponent fed an empty list. Track newly-appearing units for our seat and compare
the resulting (turn, talents, id) triples against the schedule's own `trains` field. Also
cross-check final inventory/score against inventory_at_done/score_at_done/referee_score.

sim/engine.py has NO exception/error-reporting path for illegal commands (read in full): every
action is guarded by an `if` that silently no-ops on an illegal command (insufficient funds,
occupied cell, unknown unit id, zero chop, etc). So "no referee error is reported" is trivially
true for any input. The operational stand-in used here is: does the *intended* effect (a TRAIN
producing a unit on the claimed turn, with the claimed talents) actually occur, and does the
resulting inventory/score match. A silently-no-op'd illegal command would desync one of these.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time
import traceback

ROOT = "/home/tarstars/prj/troll_farm-local_claude_1"
sys.path.insert(0, ROOT)
from sim.state import GameState, SimUnit, SimPlant   # noqa: E402
from sim.engine import step                          # noqa: E402

SCHED_DIR = "/tmp/claude-1001/-home-tarstars-prj-troll-farm/ffb31f30-1b59-4b2c-a314-45d19f2fbb61/scratchpad/solver-verify/claude_1/opening-solver/schedules"
PANEL_PATH = os.path.join(ROOT, "claude_1/h2h-panel/panel-200-seed1.jsonl")


def load_panel():
    recs = []
    with open(PANEL_PATH) as f:
        for line in f:
            recs.append(json.loads(line))
    return recs


def build_state(rec, draw):
    """Independently-written mirror of replay.py's referee_state (verified against the raw
    panel fields, not trusted blind): '0'/'1' = shacks, '+' = iron, '~' = water, '.' = walkable,
    anything else (rock) is none of these."""
    rows = rec["rows"]
    walk, iron, water = set(), set(), set()
    shacks = [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "0":
                shacks[0] = (x, y)
            elif ch == "1":
                shacks[1] = (x, y)
            elif ch == "+":
                iron.add((x, y))
            elif ch == "~":
                water.add((x, y))
            elif ch == ".":
                walk.add((x, y))
    units = [SimUnit(p, p, shacks[p][0], shacks[p][1], 1, 1, 1, 1, [0] * 6) for p in (0, 1)]
    plants = [SimPlant(t["type"], t["x"], t["y"], t["size"], t["health"], t["fruits"], t["cur_cd"])
              for t in rec["trees0"]]
    return GameState(width=len(rows[0]), height=len(rows), walkable=walk, shacks=shacks,
                      inventories=[list(draw), list(draw)], units=units, plants=plants,
                      scores=[0, 0], turn=1, next_id=2, iron=iron, water=water)


def replay_one(rec, draw, seat, commands):
    """Steps the real referee (sim/engine.py) through `commands` (ours only; opponent idle).
    Returns dict with observed_trains, final inventory/score, and any exception."""
    g = build_state(rec, draw)
    observed_trains = []
    for t, line in enumerate(commands, start=1):
        before_ids = {u.id for u in g.units if u.player == seat}
        if seat == 0:
            step(g, line, [])
        else:
            step(g, [], line)
        for u in g.units:
            if u.player == seat and u.id not in before_ids:
                observed_trains.append([t, [u.ms, u.cc, u.hp, u.chop], u.id])
    return {
        "observed_trains": observed_trains,
        "final_inventory": list(g.inventories[seat]),
        "final_score": g.scores[seat],
        "final_unit_count": sum(1 for u in g.units if u.player == seat),
    }


def main():
    t0 = time.time()
    panel = load_panel()
    files = sorted(glob.glob(os.path.join(SCHED_DIR, "*.json")))
    assert len(files) == 400, f"expected 400 schedule files, found {len(files)}"

    n_agree = 0
    n_disagree = 0
    n_errors = 0
    n_variants_checked = 0
    disagreements = []
    errors = []
    flagged_incomplete = []  # (map_hash, seat, variant) where done=False or missing 'same'
    variant_counts = {"free": 0, "chop2": 0, "chop1": 0, "same": 0}

    for fn in files:
        base = os.path.basename(fn)
        hash_part, seat_part = base[:-5].rsplit("-s", 1)
        seat = int(seat_part)
        with open(fn) as f:
            sched = json.load(f)

        assert sched["map_hash"] == hash_part, f"{base}: map_hash field {sched['map_hash']} != filename"
        assert sched["seat"] == seat, f"{base}: seat field {sched['seat']} != filename"

        idx = sched["index"]
        panel_rec = panel[idx]
        assert panel_rec["rec"]["map_hash"] == hash_part, (
            f"{base}: panel[{idx}] map_hash {panel_rec['rec']['map_hash']} != {hash_part}")
        assert panel_rec["draw"] == sched["draw"], f"{base}: panel draw != schedule draw"

        rec = panel_rec["rec"]
        draw = sched["draw"]

        for variant in ("free", "chop2", "chop1", "same"):
            if variant not in sched["solves"]:
                if variant == "same":
                    continue  # orchard6 never reached a 3rd troll on this map-seat; not a claim
                errors.append((hash_part, seat, variant, "MISSING VARIANT KEY"))
                n_errors += 1
                continue
            entry = sched["solves"][variant]
            if not entry.get("done"):
                flagged_incomplete.append((hash_part, seat, variant, entry.get("done")))
                continue  # explicitly flagged incomplete by claude_1 -- not counted as a claim

            variant_counts[variant] += 1
            n_variants_checked += 1
            expected_trains = entry["trains"]
            commands = entry["commands"]

            try:
                result = replay_one(rec, draw, seat, commands)
            except Exception as e:
                n_errors += 1
                errors.append((hash_part, seat, variant, f"EXCEPTION: {e!r}"))
                traceback.print_exc()
                continue

            problems = []
            if result["observed_trains"] != expected_trains:
                problems.append(("trains", expected_trains, result["observed_trains"]))
            if result["final_unit_count"] != 3:
                problems.append(("final_unit_count", 3, result["final_unit_count"]))
            if result["final_inventory"] != entry["inventory_at_done"]:
                problems.append(("inventory", entry["inventory_at_done"], result["final_inventory"]))
            if result["final_score"] != entry["score_at_done"]:
                problems.append(("score_at_done", entry["score_at_done"], result["final_score"]))
            if "referee_score" in entry and result["final_score"] != entry["referee_score"]:
                problems.append(("referee_score", entry["referee_score"], result["final_score"]))
            # the specific claim: third troll trained on the turn `trains` says
            expected_third_turn = entry.get("third_turn")
            observed_third_turn = result["observed_trains"][-1][0] if result["observed_trains"] else None
            if expected_third_turn != observed_third_turn:
                problems.append(("third_turn", expected_third_turn, observed_third_turn))

            if problems:
                n_disagree += 1
                disagreements.append({
                    "map_hash": hash_part, "seat": seat, "variant": variant,
                    "problems": problems,
                })
            else:
                n_agree += 1

    dt = time.time() - t0
    out = {
        "n_schedule_files": len(files),
        "n_variants_checked": n_variants_checked,
        "variant_counts_done_true": variant_counts,
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "n_errors": n_errors,
        "n_flagged_incomplete_same": len(flagged_incomplete),
        "flagged_incomplete": flagged_incomplete,
        "errors": errors,
        "disagreements": disagreements,
        "elapsed_seconds": dt,
    }
    with open("/tmp/claude-1001/-home-tarstars-prj-troll-farm/ffb31f30-1b59-4b2c-a314-45d19f2fbb61/scratchpad/solver-verify/replay_result.json", "w") as f:
        json.dump(out, f, indent=2, default=str)

    print(f"schedule files: {len(files)}")
    print(f"variants checked (done=True): {n_variants_checked}  breakdown: {variant_counts}")
    print(f"agree: {n_agree}  disagree: {n_disagree}  errors: {n_errors}")
    print(f"flagged incomplete ('same', done=False or absent-but-orchard6-had-a-third): see below")
    print(f"  -> explicit done=False entries: {flagged_incomplete}")
    print(f"elapsed: {dt:.1f}s")
    if disagreements:
        print("\nDISAGREEMENTS:")
        for d in disagreements:
            print(" ", d)
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(" ", e)


if __name__ == "__main__":
    main()
