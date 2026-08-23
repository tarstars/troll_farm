#!/usr/bin/env python3
"""NARRATE v2 decoder: replay -> our seat's per-turn intention, joined to the Trace.

Card: `local_claude_1` 20260823T103000Z (20260823-narrate-real-game-telemetry),
`coordination/GOAL.md` item 2.  A replay goes in; what comes out is, for every
traced turn and every own unit alive that turn, **what was intended**
(`Target::{None,Shack,Bank(c),Cell(c),Tree(c)}` as the instrument emitted it) beside
**what happened** (the command the accepted replay->`Trace` adapter parsed).

SEAT.  There is no seat parameter and there will not be one.  The card's first
requirement is that a mis-joined seat be *impossible to express*, not merely
unlikely -- the coordinator's first pass used the battle listing's `position`,
mis-joined 4 of 10 games and reported 1,074 confident "decode errors" that were
nothing of the kind.  So the only identity this module accepts is `agent_id`,
which `replay_to_trace.resolve_seat` resolves against the replay's own `agents`
array (the entry whose `agentId` is ours carries `index`, and that index is the
frame `agentId`).  On top of that the decoder asserts, per game, that our
telemetry is present on that seat and **absent** on the other; a game where the
NARRATE lines sit on the opposite seat is REFUSED, not decoded.  Passing the
opponent's agent id therefore raises rather than returning numbers.

REFUSE, NEVER PARTIALLY DECODE.  Every defect below is a `NarrateError` carrying a
reason, in the adapter's own style: a game either decodes whole or is refused.
  - the replay/adapter refuses it at all (an `AdapterError` is re-raised as a refusal);
  - a traced turn carries no `MSG ... NARRATE ...` segment, or carries more than one;
  - the version token is not `v2` (an unrecognised grammar is refused, never guessed);
  - `t=` disagrees with the turn index the state/command streams are aligned on;
  - a unit token is malformed, or a unit id repeats within a turn;
  - the payload roster is not *exactly* the set of own units alive in that turn's
    state -- a unit missing from the payload is a decode error, never a `NONE`;
  - our telemetry appears on the opponent's seat, or is missing from ours.

GRAMMAR (frozen, `claude_1/narrate1/msg-intention-grammar-spec-v2-2026-08-23.md`,
as codex_1 ruled it and G-P verified):

    turn 1 :  MSG <banner> NARRATE v2 t=1 u0=TREE(3,10) u2=NONE
    turn t :  MSG NARRATE v2 t=137 u0=TREE(3,10) u2=NONE u4=SHACK u5=BANK(7,2)

    payload := "NARRATE" SP "v2" SP "t=" turn { SP unit }
    unit    := "u" id "=" kind [ "(" x "," y ")" ]
    kind    := "NONE" | "SHACK" | "BANK" | "CELL" | "TREE"

Reading starts at the `NARRATE` token, so the turn-1 banner needs no special case;
`NONE` and `SHACK` take no cell, `BANK`/`CELL`/`TREE` require one.

WHAT THIS IS NOT.  The instrument only.  No grading of dancing, blocking or
idleness, no prevalence number, no cure claim -- explicitly out of scope per the
card.  `intended` is the target the selection pass recorded for the command it
issued; a join row asserts nothing about whether the intention was good.
"""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "adapter1"))
sys.path.insert(0, os.path.join(HERE, "..", "banana-restoration-r2"))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

import replay_to_trace as rt                      # noqa: E402

GRAMMAR_VERSION = "v2"
CELL_KINDS = ("BANK", "CELL", "TREE")
BARE_KINDS = ("NONE", "SHACK")


class NarrateError(RuntimeError):
    """Fail-closed refusal: a game decodes whole or not at all."""


# --- payload grammar --------------------------------------------------------

def parse_target(text: str):
    """`NONE` | `SHACK` | `KIND(x,y)` -> (kind, cell|None). Raises NarrateError."""
    if text in BARE_KINDS:
        return (text, None)
    if not text.endswith(")") or "(" not in text:
        raise NarrateError("target %r is not a known shape (%s or %s(x,y))"
                           % (text, "/".join(BARE_KINDS), "/".join(CELL_KINDS)))
    kind, _, rest = text[:-1].partition("(")
    if kind not in CELL_KINDS:
        raise NarrateError("target kind %r is not one of %s"
                           % (kind, "/".join(CELL_KINDS)))
    parts = rest.split(",")
    if len(parts) != 2:
        raise NarrateError("target %r does not carry exactly one (x,y)" % text)
    try:
        cell = (int(parts[0]), int(parts[1]))
    except ValueError:
        raise NarrateError("target %r has a non-integer coordinate" % text)
    return (kind, cell)


def parse_payload(segment: str):
    """One `MSG ...` segment -> (turn, {unit_id: (kind, cell|None)})."""
    tokens = segment.split()
    if not tokens or tokens[0] != "MSG":
        raise NarrateError("not an MSG segment: %r" % segment)
    try:
        start = tokens.index("NARRATE")
    except ValueError:
        raise NarrateError("MSG segment carries no NARRATE token: %r" % segment)
    body = tokens[start + 1:]
    if not body:
        raise NarrateError("NARRATE payload is empty: %r" % segment)
    if body[0] != GRAMMAR_VERSION:
        raise NarrateError("unrecognised NARRATE grammar version %r (this decoder "
                           "reads %s only and refuses rather than guessing)"
                           % (body[0], GRAMMAR_VERSION))
    if len(body) < 2 or not body[1].startswith("t="):
        raise NarrateError("NARRATE payload has no t= field: %r" % segment)
    try:
        turn = int(body[1][2:])
    except ValueError:
        raise NarrateError("NARRATE t= is not an integer: %r" % body[1])
    intents = {}
    for token in body[2:]:
        if not token.startswith("u") or "=" not in token:
            raise NarrateError("malformed unit token %r" % token)
        uid_text, _, target_text = token[1:].partition("=")
        try:
            uid = int(uid_text)
        except ValueError:
            raise NarrateError("malformed unit id in %r" % token)
        if uid in intents:
            raise NarrateError("unit %d appears twice in one payload" % uid)
        intents[uid] = parse_target(target_text)
    return turn, intents


def narrate_segments(row: str):
    """The `MSG ... NARRATE ...` segments of one ';'-joined command row."""
    out = []
    for raw in row.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        tokens = raw.split()
        if tokens[0] == "MSG" and "NARRATE" in tokens:
            out.append(raw)
    return out


# --- the seat control -------------------------------------------------------

def opponent_narrate_count(game: dict, seat: int) -> int:
    """Turns on the OTHER seat carrying a NARRATE token.

    This is a control, not a measurement: it is what caught the coordinator's
    inverted join, whose "decode error" count equalled it exactly.
    """
    count = 0
    for index, frame in enumerate(game.get("frames") or []):
        if index == 0:
            continue
        if frame.get("agentId") != 1 - seat:
            continue
        if narrate_segments((frame.get("stdout") or "").replace("\n", ";")):
            count += 1
    return count


# --- the decoder ------------------------------------------------------------

def decode_game(game: dict, agent_id):
    """Return (rows, meta) for one replay, or raise NarrateError.

    `rows`: one dict per (turn, own unit alive that turn) --
        turn, unit, intent_kind, intent_cell, command verb/args (None if the unit
        issued none that turn).
    """
    if agent_id is None:
        raise NarrateError("agent id is required: the seat is resolved from the "
                           "replay's own agents array and never from a position")
    try:
        transcript, commands, ameta = rt.adapt(game, agent_id=agent_id)
        trace, tmeta = rt.adapt_to_trace(game, agent_id=agent_id)
    except rt.AdapterError as exc:
        raise NarrateError("adapter refused this replay: %s" % exc)

    seat = ameta["seat"]
    rows_text = commands.split("\n")
    while rows_text and rows_text[-1] == "":
        rows_text.pop()
    if len(rows_text) != trace.T:
        raise NarrateError("%d command rows against %d traced turns"
                           % (len(rows_text), trace.T))

    leak = opponent_narrate_count(game, seat)
    if leak:
        raise NarrateError("NARRATE telemetry appears on the opponent's seat "
                           "(%d turns of seat %d); the seat join is wrong or the "
                           "opponent is running our instrument" % (leak, 1 - seat))

    rows = []
    for t in range(1, trace.T + 1):
        segments = narrate_segments(rows_text[t - 1])
        if len(segments) != 1:
            raise NarrateError("turn %d carries %d NARRATE segments; exactly one "
                               "per turn is the grammar" % (t, len(segments)))
        turn, intents = parse_payload(segments[0])
        if turn != t:
            raise NarrateError("turn misalignment: payload says t=%d on traced "
                               "turn %d" % (turn, t))
        roster = sorted(u.id for u in trace.state(t).own_units())
        if sorted(intents) != roster:
            raise NarrateError("turn %d roster mismatch: payload %s, state %s "
                               "(a unit absent from the payload is a decode "
                               "error, never a NONE)"
                               % (t, sorted(intents), roster))
        for uid in roster:
            kind, cell = intents[uid]
            cmd = trace.cmd_of(uid, t)
            unit = trace.unit(uid, t)
            rows.append({
                "turn": t,
                "unit": uid,
                "unit_cell": list(unit.cell) if unit is not None else None,
                "intent_kind": kind,
                "intent_cell": list(cell) if cell is not None else None,
                "command_verb": cmd.verb if cmd is not None else None,
                "command_args": [list(a) if isinstance(a, tuple) else a
                                 for a in cmd.args] if cmd is not None else None,
            })

    meta = {
        "game_id": game.get("gameId"),
        "agent_id": int(agent_id),
        "seat": seat,
        "turns": ameta["turns"],
        "traced_turns": trace.T,
        "trailing_empty_command_rows": ameta["trailing_empty_command_rows"],
        "own_unit_ids": trace.own_ids,
        "join_rows": len(rows),
        "opponent_narrate_turns": leak,
        "grammar": "NARRATE %s" % GRAMMAR_VERSION,
    }
    return rows, meta


def load_game(path: str) -> dict:
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def decode_file(path: str, agent_id):
    return decode_game(load_game(path), agent_id)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", help="directory of <gameId>.json[.gz] replays "
                                        "(NEVER data/raw/games: protocol hazard)")
    ap.add_argument("--game-file")
    ap.add_argument("--agent-id", type=int, required=True)
    ap.add_argument("--rows-out", help="write the join rows of a single game as JSON")
    ap.add_argument("--report")
    args = ap.parse_args(argv)

    if bool(args.games_dir) == bool(args.game_file):
        ap.error("give exactly one of --games-dir / --game-file")
    if args.games_dir:
        paths = sorted(glob.glob(os.path.join(args.games_dir, "*.json"))
                       + glob.glob(os.path.join(args.games_dir, "*.json.gz")))
    else:
        paths = [args.game_file]

    decoded, refused = [], []
    all_rows = None
    for path in paths:
        try:
            rows, meta = decode_file(path, args.agent_id)
        except NarrateError as exc:
            refused.append({"game_file": os.path.basename(path), "reason": str(exc)})
            continue
        decoded.append(meta)
        all_rows = rows
    report = {
        "games_seen": len(paths),
        "decoded": len(decoded),
        "refused": len(refused),
        "join_rows": sum(m["join_rows"] for m in decoded),
        "refusals": refused,
        "games": decoded,
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    if args.rows_out and all_rows is not None and len(paths) == 1:
        with open(args.rows_out, "w", encoding="utf-8") as fh:
            json.dump(all_rows, fh, indent=1, sort_keys=True)
    print(text if len(paths) == 1 else json.dumps(
        {k: report[k] for k in ("games_seen", "decoded", "refused", "join_rows",
                                "refusals")}, indent=2, sort_keys=True))
    return 0 if not refused else 1


if __name__ == "__main__":
    sys.exit(main())
