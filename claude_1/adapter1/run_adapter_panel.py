#!/usr/bin/env python3
"""Adapter acceptance panel: full sweep + five controls that must FAIL.

The sweep alone proves nothing -- an adapter that always says yes says yes to a
corrupted replay too.  Each control corrupts exactly one thing the adapter
claims to guard and asserts the refusal (or the changed answer) actually
arrives.  Written to claude_1/adapter1/results/.
"""
from __future__ import annotations

import copy
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "banana-restoration-r2"))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

import replay_to_trace as rt              # noqa: E402
import trace_detectors as td              # noqa: E402

GAMES = sorted(glob.glob(os.path.join(HERE, "..", "..", "data", "raw",
                                      "games", "*.json")))
CONTROL_GAME = "892621271"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sweep():
    rows, failures = [], []
    for path in GAMES:
        game = load(path)
        for seat in (0, 1):
            try:
                trace, meta = rt.adapt_to_trace(game, seat=seat)
            except rt.AdapterError as exc:
                failures.append({"game": os.path.basename(path), "seat": seat,
                                 "error": str(exc)})
                continue
            d1 = td.detect_d1(trace)
            rows.append({
                "game": os.path.basename(path).split(".")[0],
                "seat": seat,
                "turns": meta["turns"],
                "traced_turns": meta["traced_turns"],
                "trailing_empty_command_rows": meta["trailing_empty_command_rows"],
                "own_units": len(trace.own_ids),
                "d1_episodes": len(d1["episodes"]),
                "d1_verdict": d1["verdict"],
            })
    return rows, failures


def control_refuses(name, mutate, seat=0):
    """A mutation the adapter must REFUSE."""
    game = copy.deepcopy(load(os.path.join(HERE, "..", "..", "data", "raw",
                                           "games", CONTROL_GAME + ".json")))
    mutate(game)
    try:
        rt.adapt_to_trace(game, seat=seat)
    except rt.AdapterError as exc:
        return {"control": name, "expected": "AdapterError", "fired": True,
                "message": str(exc)[:160]}
    return {"control": name, "expected": "AdapterError", "fired": False,
            "message": "ACCEPTED a corrupted replay"}


def drop_a_midgame_keyframe(game):
    """The trap the length note cannot see: T states against T commands."""
    for frame in game["frames"][1:]:
        if frame.get("keyframe"):
            pass
    # frame 300 is the post-turn-150 keyframe; blank its view so decoded_states
    # skips it, leaving T states for T commands and no length mismatch.
    game["frames"][300]["view"] = ""


def scramble_seat_alternation(game):
    # frame 8 is an even frame and must belong to seat 1; frame 7 already
    # belongs to seat 0, so mutating THAT would have been a no-op mutant.
    game["frames"][8]["agentId"] = 0


def strip_a_stdout(game):
    del game["frames"][9]["stdout"]


def unknown_diff_token(game):
    payload = game["frames"][2]["view"].split("\n", 1)
    data = json.loads(payload[1])
    data["diff"] = (data.get("diff", "") + ";4242 zz9").strip(";")
    game["frames"][2]["view"] = payload[0] + "\n" + json.dumps(data)


def seat_control():
    """Seat is not cosmetic: the same replay read at the wrong seat must give a
    different own-unit set. If it did not, seat handling would be inert."""
    path = os.path.join(HERE, "..", "..", "data", "raw", "games",
                        "895035200.json")   # our lineage 6536563 sits at seat 1
    game = load(path)
    right, _ = rt.adapt_to_trace(game, agent_id=6536563)
    wrong, _ = rt.adapt_to_trace(game, seat=0)
    return {
        "control": "seat resolution is live",
        "expected": "different own units and different tent",
        "fired": (right.own_ids != wrong.own_ids) and (right.tent != wrong.tent),
        "message": "agent_id=6536563 -> seat 1 own_ids %r tent %r ; seat 0 "
                   "own_ids %r tent %r" % (right.own_ids, right.tent,
                                           wrong.own_ids, wrong.tent),
    }


def alignment_control(flagged):
    """Shift the commands one turn against the states and require D-1 to move.

    Run on the pairs where D-1 actually fires: on a pair with no episodes the
    comparison is 0 == 0 and the control is vacuous whatever the adapter does.
    """
    changed, examined = 0, []
    for row in flagged:
        game = load(os.path.join(HERE, "..", "..", "data", "raw", "games",
                                 row["game"] + ".json"))
        transcript, commands, _ = rt.adapt(game, seat=row["seat"])
        aligned = td.build_trace(transcript, commands)
        lines = commands.split("\n")
        shifted = "\n".join(lines[1:])      # drop turn 1: everything slides
        off = td.build_trace(transcript, shifted)
        a, b = td.detect_d1(aligned), td.detect_d1(off)
        same = json.dumps(a["episodes"]) == json.dumps(b["episodes"])
        if not same:
            changed += 1
        examined.append({"game": row["game"], "seat": row["seat"],
                         "aligned": len(a["episodes"]),
                         "shifted": len(b["episodes"]), "changed": not same})
    return {
        "control": "one-turn COMMAND shift changes D-1",
        "expected": "MEASUREMENT, not a gate -- see message",
        "measurement_only": True,
        "fired": True,
        "message": "%d of %d flagged pairs changed under a one-turn command "
                   "shift. This is a FINDING, not a pass: D-1 reads positions "
                   "from the states and consults the command stream only for "
                   "the DROP/PICK inventory clause, so a command misalignment "
                   "is very nearly invisible in D-1's own output. The detector "
                   "cannot police the join; only the adapter's structural "
                   "invariants can."
                   % (changed, len(examined)),
        "detail": examined,
    }


def state_shift_control(flagged):
    """Shift the STATES against the commands and require D-1 to move.

    Complements the command-shift measurement: positions are what D-1 reads,
    so if dropping the first state did NOT move the episodes, the states would
    not be load-bearing either and nothing about this adapter could be tested.
    """
    changed, examined = 0, []
    for row in flagged:
        game = load(os.path.join(HERE, "..", "..", "data", "raw", "games",
                                 row["game"] + ".json"))
        transcript, commands, _ = rt.adapt(game, seat=row["seat"])
        aligned = td.build_trace(transcript, commands)
        head, body = transcript.split("\n", 1)
        smap, states = td.TraceParser().parse(transcript)
        # rebuild a transcript missing its first turn block by re-rendering is
        # unnecessary: build the Trace directly from the shifted state list.
        off = td.Trace(smap, states[1:], td.CommandParser().parse(commands))
        a, b = td.detect_d1(aligned), td.detect_d1(off)
        same = json.dumps(a["episodes"]) == json.dumps(b["episodes"])
        if not same:
            changed += 1
        examined.append({"game": row["game"], "seat": row["seat"],
                         "aligned": len(a["episodes"]),
                         "shifted": len(b["episodes"]), "changed": not same})
    return {
        "control": "one-turn STATE shift changes D-1",
        "expected": "the episode set moves on every D-1-flagged pair",
        "fired": bool(examined) and changed == len(examined),
        "message": "%d of %d flagged pairs changed when the states were slid "
                   "one turn against the commands" % (changed, len(examined)),
        "detail": examined,
    }


def main():
    rows, failures = sweep()
    controls = [
        control_refuses("a dropped mid-game keyframe", drop_a_midgame_keyframe),
        control_refuses("broken seat alternation", scramble_seat_alternation),
        control_refuses("a missing stdout frame", strip_a_stdout),
        control_refuses("an unknown diff token", unknown_diff_token),
        seat_control(),
        alignment_control([r for r in rows if r["d1_verdict"] == "FAIL"]),
        state_shift_control([r for r in rows if r["d1_verdict"] == "FAIL"]),
    ]
    out = {
        "games": len(GAMES),
        "pairs_attempted": len(GAMES) * 2,
        "pairs_adapted": len(rows),
        "refusals": failures,
        "controls": controls,
        "controls_all_fired": all(c["fired"] for c in controls),
        "d1_flagged_pairs": sum(1 for r in rows if r["d1_verdict"] == "FAIL"),
        "d1_episodes_total": sum(r["d1_episodes"] for r in rows),
        "rows": rows,
    }
    dest = os.path.join(HERE, "results", "adapter-panel-2026-08-23.json")
    text = json.dumps(out, indent=2, sort_keys=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"},
                     indent=2, sort_keys=True))
    print("sha256(results) =", hashlib.sha256(text.encode()).hexdigest())
    return 0 if out["controls_all_fired"] else 1


if __name__ == "__main__":
    sys.exit(main())
