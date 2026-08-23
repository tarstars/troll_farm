#!/usr/bin/env python3
"""replay -> Trace adapter (D-1 card, deliverable a of 20260821-corpus-prevalence).

Turns a CodinGame Troll Farm replay (`data/raw/games/<id>.json`) into the exact
pair `trace_detectors.build_trace` already consumes:

    transcript text  = "W H" header + map rows, then one turn block per turn
    commands text    = one line per turn, our own seat's stdout, ';'-joined

and then calls the ACCEPTED parser verbatim.  The adapter emits *text*, not
`Trace` objects, deliberately: every parsing rule (map alphabet, own-side
convention, command grammar, MSG stripping, first-command-per-unit) stays in
`trace_detectors`, so the adapter cannot quietly disagree with the instrument
the panel results were produced by.

Replay layout, measured over all 290 in-repo games (2026-08-23):
  frames = 2T+1; frames[0] is the initial keyframe; frames[2t-1] carries seat
  0's stdout for turn t, frames[2t] seat 1's stdout AND the post-turn keyframe.
  T = 300 in 266 of the 290, and 166..297 in the other 24: T is measured, never
  assumed.

THE ALIGNMENT TRAP.  `decoded_states` yields T+1 states (initial + one per
resolved turn) against T command rows.  `Trace.__init__` truncates to the
common prefix, which on a whole replay happens to be the right answer: state k
is the pre-turn state of turn k+1, and the dropped tail state is the post-game
one.  It is right by luck, and its note is not a guard -- if a keyframe were
missing mid-game the counts would read T and T, the mismatch note would not
fire, and every later state would be one turn early against the commands with
nothing on screen.  So this adapter does the alignment itself, asserts
`len(states) == len(commands) + 1` and asserts `resolved_turn == k` on every
state, and hands `build_trace` two streams that are already the same length.

SEAT.  `trace_detectors` hardcodes own = player 0, own tent = shacks[0], own
inventory = inventories[0]; the replay numbers seats absolutely.  When we
played seat 1 the adapter renumbers: map digits '0'<->'1', inventory lines
swapped, unit `player` flipped.  The seat is required (`--seat`, or resolved
from `--agent-id` against the replay's own agent table) and there is no
default: a wrong seat silently joins our command stream to the opponent's
units and still prints numbers.

TRAILING EMPTY COMMAND ROWS.  A crashed or timed-out seat emits nothing on
its last turn(s); `CommandParser` strips trailing empty lines, which would
shorten the command stream against the states with no note.  The adapter drops
the matching tail states instead and reports the count
(`trailing_empty_command_rows`).  Measured: 1 row in 1 of the 580
game x seat pairs in `data/raw/games/`.

FAIL-CLOSED.  Any of these raises rather than degrades: unknown diff tokens
left over by the decoder, a non-alternating or short frame table, a keyframe
with no payload, a missing per-turn inventory line, a state whose
`resolved_turn` is not its index, a count mismatch after alignment.

Reconstruction that is NOT observation, and which direction it errs:
`DiffDecoder.tick_existing_plants` and `apply_known_chops` infer plant clocks
the visual diff omits.  Plant health/stage/cooldown in the emitted transcript
are therefore reconstructed.  For D-1 this touches exactly one of three
progress tests -- "a plant created or removed at u's cell".  A missed
create/remove event means a missed progress event, which means a window that
should have been broken is not: the error direction is a FALSE dancing
episode, not a missed one.  D-1 counts off replays are an upper bound.
Per-unit carry and own inventory, which carry the other two progress tests,
are read straight from the diff and the inputmodule and are not reconstructed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "banana-restoration-r2"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", ".."))

import trace_detectors as td                      # noqa: E402
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402


class AdapterError(RuntimeError):
    """Fail-closed refusal: never degrade a trace, refuse it."""


ITEM_COUNT = 6


# --- replay reading --------------------------------------------------------

def frame_layout(game: dict) -> int:
    """Return T (turns), after proving the frame table has the shape we assume."""
    frames = game.get("frames") or []
    if len(frames) < 3 or len(frames) % 2 != 1:
        raise AdapterError("frame table is %d frames; expected an odd 2T+1"
                           % len(frames))
    turns = (len(frames) - 1) // 2
    for index, frame in enumerate(frames[1:], 1):
        if frame.get("agentId") != (index - 1) % 2:
            raise AdapterError("frame %d belongs to agent %r, not the "
                               "alternating seat %d"
                               % (index, frame.get("agentId"), (index - 1) % 2))
        if "stdout" not in frame:
            raise AdapterError("frame %d has no stdout" % index)
    keyframes = [i for i, f in enumerate(frames) if f.get("keyframe")]
    if keyframes != [0] + [2 * t for t in range(1, turns + 1)]:
        raise AdapterError("keyframes are not frame 0 plus every even frame")
    return turns


def resolve_seat(game: dict, seat, agent_id) -> int:
    if seat is not None and agent_id is not None:
        raise AdapterError("give --seat or --agent-id, not both")
    if seat is not None:
        if seat not in (0, 1):
            raise AdapterError("seat must be 0 or 1")
        return seat
    if agent_id is None:
        raise AdapterError("seat is required: pass --seat or --agent-id "
                           "(a wrong seat produces numbers, not an error)")
    matches = [a for a in (game.get("agents") or [])
               if int(a.get("agentId", -1)) == int(agent_id)]
    if len(matches) != 1:
        raise AdapterError("agent %s appears %d times in this replay's agent "
                           "table" % (agent_id, len(matches)))
    return int(matches[0]["index"])


def trajectory_from_frames(game: dict, turns: int) -> list[dict]:
    """Rebuild the {commands0, commands1} rows `decoded_states` wants.

    The processed `trajectories/<id>.jsonl` corpus is unreachable from this
    host; the same two fields are in the replay itself, one frame per seat.
    """
    frames = game["frames"]
    rows = []
    for t in range(1, turns + 1):
        rows.append({
            "commands0": frames[2 * t - 1].get("stdout") or "",
            "commands1": frames[2 * t].get("stdout") or "",
        })
    return rows


# --- transcript rendering --------------------------------------------------

def render_map(static: dict, seat: int) -> list[str]:
    rows = list(static["rows"])
    if len(rows) != static["height"]:
        raise AdapterError("map has %d rows, header says %d"
                           % (len(rows), static["height"]))
    if seat == 1:
        swap = str.maketrans({"0": "1", "1": "0"})
        rows = [row.translate(swap) for row in rows]
    return ["%d %d" % (static["width"], static["height"])] + rows


def render_state(state: dict, seat: int) -> list[str]:
    inventories = state["inventories"]
    if len(inventories) != 2 or any(len(inv) != ITEM_COUNT for inv in inventories):
        raise AdapterError("turn %r has malformed inventories %r"
                           % (state.get("resolved_turn"), inventories))
    if seat == 1:
        inventories = [inventories[1], inventories[0]]
    lines = [" ".join(str(int(v)) for v in inv) for inv in inventories]

    plants = state["plants"]
    lines.append(str(len(plants)))
    for plant in plants:
        lines.append("%s %d %d %d %d %d %d" % (
            plant["type"], plant["x"], plant["y"], plant["size"],
            plant["health"], plant["fruits"], plant["cooldown"]))

    units = state["units"]
    lines.append(str(len(units)))
    for unit in units:
        player = unit["player"] ^ seat
        carry = unit["carry"]
        if len(carry) != ITEM_COUNT:
            raise AdapterError("unit %r carries %d slots" % (unit["id"], len(carry)))
        lines.append("%d %d %d %d %d %d %d %d %s" % (
            unit["id"], player, unit["x"], unit["y"], unit["ms"], unit["cc"],
            unit["hp"], unit["chop"],
            " ".join(str(int(c)) for c in carry)))
    return lines


def render_commands(trajectory: list[dict], seat: int) -> str:
    key = "commands%d" % seat
    lines = []
    for row in trajectory:
        raw = (row.get(key) or "").replace("\n", ";")
        parts = [p.strip() for p in raw.split(";")]
        lines.append(";".join(p for p in parts if p))
    return "\n".join(lines) + "\n"


# --- the adapter ------------------------------------------------------------

def adapt(game: dict, seat=None, agent_id=None):
    """Return (transcript_text, commands_text, meta). Raises AdapterError."""
    turns = frame_layout(game)
    seat = resolve_seat(game, seat, agent_id)
    trajectory = trajectory_from_frames(game, turns)

    static, states, unknown = decoded_states(game, trajectory)
    if unknown:
        raise AdapterError("decoder left %d unknown diff updates; the state is "
                           "not exact and will not be traced" % unknown)
    if len(states) != turns + 1:
        raise AdapterError("decoded %d states for %d turns; expected T+1 "
                           "(a dropped keyframe shifts every later state one "
                           "turn early and the length note cannot see it)"
                           % (len(states), turns))
    for index, state in enumerate(states):
        if int(state.get("resolved_turn", -1)) != index:
            raise AdapterError("state %d reports resolved_turn %r; states are "
                               "not contiguous" % (index, state.get("resolved_turn")))

    # A crashed or timed-out agent emits nothing on its final turn(s), and
    # `CommandParser` strips trailing empty lines -- which would silently
    # shorten the command stream against the states.  Drop the matching tail
    # states instead, and record how many, so the loss is on the report rather
    # than in the parser.
    seat_rows = ["" if not (row.get("commands%d" % seat) or "").strip() else "x"
                 for row in trajectory]
    trailing_empty = 0
    while seat_rows and seat_rows[-1] == "":
        seat_rows.pop()
        trailing_empty += 1
    kept = turns - trailing_empty
    if kept < 1:
        raise AdapterError("seat %d issued no commands in any of %d turns"
                           % (seat, turns))
    trajectory = trajectory[:kept]

    # ALIGNMENT: pre-turn states S_1..S_kept are states[0..kept-1]; the
    # post-game state (and any tail dropped just above) goes here, by name,
    # not by Trace's truncation.
    pre_turn = states[:kept]

    lines = render_map(static, seat)
    for state in pre_turn:
        lines.extend(render_state(state, seat))
    transcript = "\n".join(lines) + "\n"
    commands = render_commands(trajectory, seat)

    meta = {
        "game_id": game.get("gameId"),
        "turns": turns,
        "traced_turns": kept,
        "seat": seat,
        "states_decoded": len(states),
        "command_rows": len(trajectory),
        "dropped_post_game_state": True,
        "trailing_empty_command_rows": trailing_empty,
        "unknown_diff_updates": unknown,
    }
    return transcript, commands, meta


def adapt_to_trace(game: dict, seat=None, agent_id=None):
    transcript, commands, meta = adapt(game, seat=seat, agent_id=agent_id)
    trace = td.build_trace(transcript, commands)
    if trace.T != meta["traced_turns"]:
        raise AdapterError("Trace kept %d turns of %d; the streams were not "
                           "aligned before parsing"
                           % (trace.T, meta["traced_turns"]))
    if trace.notes:
        raise AdapterError("Trace raised notes on an aligned pair: %r"
                           % (trace.notes,))
    return trace, meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game-file", required=True)
    ap.add_argument("--seat", type=int)
    ap.add_argument("--agent-id", type=int)
    ap.add_argument("--transcript-out")
    ap.add_argument("--commands-out")
    ap.add_argument("--report")
    args = ap.parse_args(argv)

    with open(args.game_file, encoding="utf-8") as fh:
        game = json.load(fh)
    transcript, commands, meta = adapt(game, seat=args.seat, agent_id=args.agent_id)
    if args.transcript_out:
        with open(args.transcript_out, "w", encoding="utf-8") as fh:
            fh.write(transcript)
    if args.commands_out:
        with open(args.commands_out, "w", encoding="utf-8") as fh:
            fh.write(commands)
    trace = td.build_trace(transcript, commands)
    report = dict(meta, trace_turns=trace.T, trace_notes=trace.notes,
                  own_unit_ids=trace.own_ids, tent=list(trace.tent))
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
