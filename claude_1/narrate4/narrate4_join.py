#!/usr/bin/env python3
"""Join the **v4** wire payload to the adapter's trace — the v3 join, unchanged in shape.

Task: `20260825-dance-cure-candidate-1-hold`, G-2 grading.

`claude_1/dance1/narrate3_decode.decode_game` is the accepted v3 join: it adapts the replay,
checks command rows against traced turns, refuses a payload on the opponent's seat, refuses a
roster mismatch, and emits one row per (turn, own unit alive that turn).  This module is that
function with **one** substitution — `narrate4.decode` in place of the v3 grammar — and two
additions that exist only because v4 carries them: the per-unit `branch`/`blocked` fields and the
per-turn `pz`/`sp`/`wc` meta.

Nothing here relaxes a v3 check.  A missing unit is still a decode error and never a `NONE`; a
turn whose payload says `t=` something else is still a misalignment; `MSG NARRATE` on the other
seat is still a refusal of the whole game.  The version token is checked by `narrate4.decode`
itself, so a v3 replay handed to this joiner is REFUSED rather than silently read with `r=`
reported absent.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (HERE, REPO / "claude_1" / "adapter1", REPO / "claude_1" / "narrate1", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import narrate4 as n4                 # noqa: E402
import narrate_decode as nd           # noqa: E402
import replay_to_trace as rt          # noqa: E402


class Narrate4Error(Exception):
    """Anything that would make a v4 row mean something other than it says."""


def decode_game(game: dict, agent_id):
    """Return (rows, meta) for one v4 replay, or raise `Narrate4Error`.

    `rows`: one dict per (turn, own unit alive that turn) with the v3 fields
    (`turn`, `unit`, `unit_cell`, `chosen`, `available`, `command_verb`) plus `branch` (`r=`) and
    `blocked` (`b=`).  `meta["per_turn"]` maps turn -> {pz, sp, wc}.
    """
    if agent_id is None:
        raise Narrate4Error("agent id is required: the seat is resolved from the replay's own "
                            "agents array and never from a position")
    try:
        _transcript, commands, ameta = rt.adapt(game, agent_id=agent_id)
        trace, _tmeta = rt.adapt_to_trace(game, agent_id=agent_id)
    except rt.AdapterError as exc:
        raise Narrate4Error("adapter refused this replay: %s" % exc)

    seat = ameta["seat"]
    rows_text = commands.split("\n")
    while rows_text and rows_text[-1] == "":
        rows_text.pop()
    if len(rows_text) != trace.T:
        raise Narrate4Error("%d command rows against %d traced turns"
                            % (len(rows_text), trace.T))

    leak = nd.opponent_narrate_count(game, seat)
    if leak:
        raise Narrate4Error("NARRATE telemetry appears on the opponent's seat (%d turns of seat "
                            "%d); the seat join is wrong or the opponent is running our "
                            "instrument" % (leak, 1 - seat))

    rows = []
    per_turn = {}
    longest_line = 0
    for t in range(1, trace.T + 1):
        longest_line = max(longest_line, len(rows_text[t - 1]))
        segments = nd.narrate_segments(rows_text[t - 1])
        if len(segments) != 1:
            raise Narrate4Error("turn %d carries %d NARRATE segments; exactly one per turn is "
                                "the grammar" % (t, len(segments)))
        try:
            turn, units, _order, _banner, meta = n4.decode(segments[0])
        except n4.GateError as exc:
            raise Narrate4Error("turn %d: %s" % (t, exc))
        if turn != t:
            raise Narrate4Error("turn misalignment: payload says t=%d on traced turn %d"
                                % (turn, t))
        roster = sorted(u.id for u in trace.state(t).own_units())
        if sorted(units) != roster:
            raise Narrate4Error("turn %d roster mismatch: payload %s, state %s (a unit absent "
                                "from the payload is a decode error, never a NONE)"
                                % (t, sorted(units), roster))
        per_turn[t] = dict(meta)
        for uid in roster:
            chosen, available, branch, blocked = units[uid]
            cmd = trace.cmd_of(uid, t)
            unit = trace.unit(uid, t)
            rows.append({
                "turn": t,
                "unit": uid,
                "unit_cell": list(unit.cell) if unit is not None else None,
                "chosen": chosen,
                "available": available,
                "command_verb": cmd.verb if cmd is not None else None,
                "branch": branch,
                "blocked": blocked,
            })

    meta = {
        "game_id": game.get("gameId"),
        "agent_id": int(agent_id),
        "seat": seat,
        "turns": ameta["turns"],
        "traced_turns": trace.T,
        "own_unit_ids": trace.own_ids,
        "join_rows": len(rows),
        "opponent_narrate_turns": leak,
        "longest_command_line_chars": longest_line,
        "per_turn": per_turn,
        "grammar": "NARRATE v4 (imported from narrate4.decode)",
    }
    return rows, meta
