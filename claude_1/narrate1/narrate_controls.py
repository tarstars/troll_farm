#!/usr/bin/env python3
"""Controls for the NARRATE decoder: prove every refusal can FIRE before believing
the 149/149 sweep.

A decoder that always says yes says yes to a mis-joined seat too -- which is the
exact defect this card exists because of.  Each control below corrupts exactly one
thing the decoder claims to refuse, **on a real recorded Arena replay**, and asserts
the refusal arrives with the right reason.  The baseline runs first: if the
unmutated game did not decode clean, every "fired" below would prove nothing.

Controls, in the card's order:
  1. clean case            -- the unmutated replay decodes (baseline)
  2. wrong seat            -- the opponent's agent id must REFUSE, not renumber
  3. opponent's MSG        -- a NARRATE injected on the other seat must REFUSE
  4. dropped turn          -- a turn with no NARRATE segment must REFUSE
  5. corrupted grammar     -- version, unit token, target shape, duplicate unit
  6. turn misalignment     -- t= shifted by one
  7. roster incompleteness -- a live unit missing from the payload
  8. unknown agent id      -- an id absent from the agents array must REFUSE
"""

from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import narrate_decode as nd                       # noqa: E402

AGENT_ID = 6652424
OPPONENT_FIELD = "agentId"


def our_frames(game, seat):
    """Indices of the frames carrying our seat's stdout, in turn order."""
    return [i for i, f in enumerate(game["frames"])
            if i > 0 and f.get(OPPONENT_FIELD) == seat]


def mutate_turn(game, seat, turn_index, fn):
    """Apply `fn` to our seat's stdout on the (0-based) `turn_index`-th turn."""
    out = copy.deepcopy(game)
    idx = our_frames(out, seat)[turn_index]
    out["frames"][idx]["stdout"] = fn(out["frames"][idx]["stdout"])
    return out


def refuses(game, agent_id, expect_substr):
    try:
        nd.decode_game(game, agent_id)
    except nd.NarrateError as exc:
        return {"fired": expect_substr in str(exc), "reason": str(exc)[:200]}
    return {"fired": False, "reason": "DECODED -- the control did not fire"}


def main(argv=None):
    games_dir = argv[0] if argv else os.path.expanduser(
        "~/.cache/troll-farm/narrate-games")
    path = os.path.join(games_dir, "900089738.json.gz")
    game = nd.load_game(path)
    rows, meta = nd.decode_game(game, AGENT_ID)
    seat = meta["seat"]
    opponent_id = [a["agentId"] for a in game["agents"]
                   if int(a["agentId"]) != AGENT_ID][0]

    controls = []

    controls.append({
        "control": "clean case: the unmutated replay decodes",
        "expected": "accepted",
        "fired": bool(rows) and meta["traced_turns"] > 0,
        "reason": "%d join rows over %d turns, seat %d, leak %d"
                  % (len(rows), meta["traced_turns"], seat,
                     meta["opponent_narrate_turns"]),
    })

    # 2 -- the failure this card was written about.  There is no seat parameter to
    # get wrong; the only way to express the wrong seat is the wrong agent id, and
    # that must refuse rather than produce numbers.
    controls.append(dict(
        control="wrong seat: decoding as the opponent's agent id",
        expected="opponent's seat", **refuses(game, opponent_id, "opponent's seat")))

    # 3 -- the opponent's MSG mistaken for ours.
    opp_frames = [i for i, f in enumerate(game["frames"])
                  if i > 0 and f.get(OPPONENT_FIELD) == 1 - seat]
    injected = copy.deepcopy(game)
    idx = opp_frames[5]
    injected["frames"][idx]["stdout"] = (
        "MSG NARRATE v2 t=6 u1=NONE;" + (injected["frames"][idx]["stdout"] or ""))
    controls.append(dict(
        control="opponent's MSG mistaken for ours",
        expected="opponent's seat", **refuses(injected, AGENT_ID, "opponent's seat")))

    # 4 -- a dropped turn.
    dropped = mutate_turn(game, seat, 40, lambda s: ";".join(
        p for p in s.replace("\n", ";").split(";") if "NARRATE" not in p))
    controls.append(dict(
        control="dropped turn: a turn with no NARRATE segment",
        expected="0 NARRATE segments", **refuses(dropped, AGENT_ID,
                                                 "0 NARRATE segments")))

    # 4b -- two segments in one turn is equally a grammar breach.
    doubled = mutate_turn(game, seat, 41,
                          lambda s: "MSG NARRATE v2 t=42 u0=NONE;" + s)
    controls.append(dict(
        control="two NARRATE segments in one turn",
        expected="2 NARRATE segments", **refuses(doubled, AGENT_ID,
                                                 "2 NARRATE segments")))

    # 5 -- corrupted grammar, four separate corruptions.
    bad_version = mutate_turn(game, seat, 10,
                              lambda s: s.replace("NARRATE v2", "NARRATE v3"))
    controls.append(dict(
        control="corrupted grammar: unrecognised version token",
        expected="unrecognised NARRATE grammar version",
        **refuses(bad_version, AGENT_ID, "unrecognised NARRATE grammar version")))

    bad_unit = mutate_turn(game, seat, 11, lambda s: s.replace("u0=", "x0=", 1))
    controls.append(dict(
        control="corrupted grammar: malformed unit token",
        expected="malformed unit token",
        **refuses(bad_unit, AGENT_ID, "malformed unit token")))

    bad_target = mutate_turn(game, seat, 12,
                             lambda s: s.replace("=CELL(", "=FIELD(", 1)
                             .replace("=TREE(", "=FIELD(", 1)
                             .replace("=NONE", "=FIELD", 1))
    controls.append(dict(
        control="corrupted grammar: unknown target shape",
        expected="target", **refuses(bad_target, AGENT_ID, "target")))

    def duplicate(s):
        parts = s.replace("\n", ";").split(";")
        for i, p in enumerate(parts):
            if "NARRATE" in p:
                toks = p.split()
                parts[i] = p + " " + toks[-1]
        return ";".join(parts)
    dup = mutate_turn(game, seat, 13, duplicate)
    controls.append(dict(
        control="corrupted grammar: a unit id twice in one payload",
        expected="appears twice", **refuses(dup, AGENT_ID, "appears twice")))

    # 6 -- turn misalignment: the check that does not depend on the detector noticing.
    shifted = mutate_turn(game, seat, 20, lambda s: s.replace("t=21", "t=22"))
    controls.append(dict(
        control="turn misalignment: t= shifted by one",
        expected="turn misalignment", **refuses(shifted, AGENT_ID,
                                                "turn misalignment")))

    # 7 -- roster incompleteness: absence must never read as an intention.
    def drop_unit(s):
        parts = s.replace("\n", ";").split(";")
        for i, p in enumerate(parts):
            if "NARRATE" in p:
                toks = p.split()
                parts[i] = " ".join(toks[:-1])
        return ";".join(parts)
    thin = mutate_turn(game, seat, 200, drop_unit)
    controls.append(dict(
        control="roster incompleteness: a live unit missing from the payload",
        expected="roster mismatch", **refuses(thin, AGENT_ID, "roster mismatch")))

    # 8 -- an identity the replay does not know.
    controls.append(dict(
        control="unknown agent id",
        expected="adapter refused", **refuses(game, 1, "adapter refused")))

    report = {
        "control_game": os.path.basename(path),
        "agent_id": AGENT_ID,
        "seat": seat,
        "controls": controls,
        "fired": sum(1 for c in controls if c["fired"]),
        "total": len(controls),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["fired"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
