#!/usr/bin/env python3
"""NARRATE **v3** replay decoder — the v2 decoder's discipline, the v3 grammar, IMPORTED.

Task: `20260824-real-game-dance-attribution`, G-1 §3 K4.

The definitions said I would *lift* `claude_1/narrate3/run_gp3_parity.py`'s `decode` into this
file "unchanged in behaviour" and prove equivalence.  I did something strictly stronger and say
so plainly: this module **imports that function** and never copies it, exactly as §1 requires of
`measure_blocker`.  A copy that must be proved equivalent is a copy that can drift between the
proof and the use; an import cannot.  The recorded SHA-256 of the imported function's source is
asserted at import time, so a silent edit upstream halts this module instead of decoding under a
grammar nobody reviewed.

What is NEW here, and is not the grammar: the per-replay wrapper.  `run_gp3_parity.decode` reads
one payload; the v2 module's `decode_game` carries the refusal discipline (seat resolved from the
replay's own `agents` array by agent id, our telemetry asserted present on our seat and absent on
the opponent's, exactly one NARRATE segment per traced turn, `t=` aligned, roster exactly the own
units alive in that turn's state, refuse the game whole rather than decode it partly).  This
wrapper is that discipline applied to v3 payloads; every refusal reason is the v2 reason, so a v3
game is refused for the same causes a v2 game is.

`ABSENT` is never folded into `NONE`: `chosen` and `available` are returned as separate strings in
the v3 spelling, and `available` may be the distinct token `ABSENT`.
"""

from __future__ import annotations

import hashlib
import inspect
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (REPO / "claude_1" / "narrate1", REPO / "claude_1" / "narrate3",
           REPO / "claude_1" / "adapter1", REPO / "claude_1" / "banana-restoration-r2",
           REPO / "claude_1" / "pipeline", REPO / "claude_1" / "t1", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import narrate_decode as nd                     # noqa: E402  (v2 discipline)
import replay_to_trace as rt                    # noqa: E402
import run_gp3_parity as gp3                    # noqa: E402  (the v3 grammar, imported)

#: SHA-256 of `inspect.getsource(run_gp3_parity.decode)` as reviewed on 2026-08-24.
GP3_DECODE_SHA256 = "0537741d53e65da10b10a0a5cb88f6a78fbee5234672488f9dc3a1d68cf293bf"

GRAMMAR_VERSION = "v3"


class Narrate3Error(RuntimeError):
    """Fail-closed refusal: a game decodes whole or not at all."""


def imported_grammar_identity():
    """(sha256, matches_recorded) for the imported payload decoder's source."""
    digest = hashlib.sha256(inspect.getsource(gp3.decode).encode()).hexdigest()
    return digest, digest == GP3_DECODE_SHA256


def assert_grammar_identity():
    digest, ok = imported_grammar_identity()
    if not ok:
        raise Narrate3Error(
            "the imported v3 payload decoder %s.decode has source SHA-256 %s, not the reviewed "
            "%s; refusing to decode under a grammar that was not reviewed"
            % (gp3.__name__, digest, GP3_DECODE_SHA256))


def decode_game(game: dict, agent_id):
    """Return (rows, meta) for one v3 replay, or raise `Narrate3Error`.

    `rows`: one dict per (turn, own unit alive that turn) carrying `chosen` and `available` in
    their v3 spellings, plus the command the adapter parsed.
    """
    assert_grammar_identity()
    if agent_id is None:
        raise Narrate3Error("agent id is required: the seat is resolved from the replay's own "
                            "agents array and never from a position")
    try:
        _transcript, commands, ameta = rt.adapt(game, agent_id=agent_id)
        trace, _tmeta = rt.adapt_to_trace(game, agent_id=agent_id)
    except rt.AdapterError as exc:
        raise Narrate3Error("adapter refused this replay: %s" % exc)

    seat = ameta["seat"]
    rows_text = commands.split("\n")
    while rows_text and rows_text[-1] == "":
        rows_text.pop()
    if len(rows_text) != trace.T:
        raise Narrate3Error("%d command rows against %d traced turns"
                            % (len(rows_text), trace.T))

    leak = nd.opponent_narrate_count(game, seat)
    if leak:
        raise Narrate3Error("NARRATE telemetry appears on the opponent's seat (%d turns of seat "
                            "%d); the seat join is wrong or the opponent is running our "
                            "instrument" % (leak, 1 - seat))

    rows = []
    for t in range(1, trace.T + 1):
        segments = nd.narrate_segments(rows_text[t - 1])
        if len(segments) != 1:
            raise Narrate3Error("turn %d carries %d NARRATE segments; exactly one per turn is "
                                "the grammar" % (t, len(segments)))
        try:
            turn, units, _order, _banner = gp3.decode(segments[0])
        except gp3.GateError as exc:
            raise Narrate3Error("turn %d: %s" % (t, exc))
        if turn != t:
            raise Narrate3Error("turn misalignment: payload says t=%d on traced turn %d"
                                % (turn, t))
        roster = sorted(u.id for u in trace.state(t).own_units())
        if sorted(units) != roster:
            raise Narrate3Error("turn %d roster mismatch: payload %s, state %s (a unit absent "
                                "from the payload is a decode error, never a NONE)"
                                % (t, sorted(units), roster))
        for uid in roster:
            chosen, available = units[uid]
            cmd = trace.cmd_of(uid, t)
            unit = trace.unit(uid, t)
            rows.append({
                "turn": t,
                "unit": uid,
                "unit_cell": list(unit.cell) if unit is not None else None,
                "chosen": chosen,
                "available": available,
                "command_verb": cmd.verb if cmd is not None else None,
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
        "grammar": "NARRATE %s (imported from %s.decode, source sha256 %s)"
                   % (GRAMMAR_VERSION, gp3.__name__, GP3_DECODE_SHA256),
    }
    return rows, meta


def parse_v3_target(text: str):
    """v3 target spelling -> (kind, cell|None).  `ABSENT` is a kind of its own, never `NONE`."""
    if text == "ABSENT":
        return ("ABSENT", None)
    return nd.parse_target(text)


if __name__ == "__main__":
    digest, ok = imported_grammar_identity()
    print("imported v3 payload decoder source sha256: %s (%s)"
          % (digest, "matches reviewed" if ok else "MISMATCH"))
