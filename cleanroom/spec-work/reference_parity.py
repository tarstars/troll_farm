#!/usr/bin/env python3
"""Prove the harness's reference binary plays identically to the champion of record.

The champion of record prints one `MSG` on turn 1 naming its internal role
vocabulary -- a leak into a package that is supposed to be written from
observable play only.  The harness therefore ships a binary built from the same
source with that announcement removed.  `MSG` has no effect on the game, so the
edit must be play-neutral; this script proves it rather than asserting it.

Method: play the champion against itself on every frozen map, recording the exact
input each seat received and the exact line it answered; then feed the identical
inputs to the reference binary and compare the answers with `MSG` stripped from
both.  Any difference anywhere fails.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "package", "harness"))
import referee  # noqa: E402


def strip_msg(line):
    return ";".join(c.strip() for c in line.replace("\n", ";").split(";")
                    if c.strip() and c.split()[0].upper() != "MSG")


def record(spec, command, turns):
    """Play `command` against itself, returning [(input_text, answer), ...]."""
    game = referee.Game(spec)
    bots = [referee.Bot(command, "p0"), referee.Bot(command, "p1")]
    log = []
    try:
        first = [referee.initial_text(game, 0), referee.initial_text(game, 1)]
        for turn in range(1, turns + 1):
            game.turn = turn
            parsed = [None, None]
            for seat in (0, 1):
                payload = (first[seat] if turn == 1 else "") + referee.turn_text(game, seat)
                line, _, _ = bots[seat].ask(payload, 10 ** 9)
                log.append((payload, line))
                parsed[seat] = referee.parse(line, game, seat)
            game.apply_turn(parsed)
            over, _ = game.ended()
            if over:
                break
    finally:
        for bot in bots:
            bot.close()
    return log


def replay(log, command):
    """Feed exactly these inputs to `command` (fresh process per seat-stream)."""
    answers = []
    bots = {}
    try:
        for index, (payload, _) in enumerate(log):
            seat = index % 2
            if seat not in bots:
                bots[seat] = referee.Bot(command, "replay%d" % seat)
            line, _, _ = bots[seat].ask(payload, 10 ** 9)
            answers.append(line)
    finally:
        for bot in bots.values():
            bot.close()
    return answers


def main():
    champion, reference, maps = sys.argv[1], sys.argv[2], sys.argv[3]
    files = sorted(f for f in os.listdir(maps) if f.endswith(".json"))
    total = mismatched = 0
    for name in files:
        with open(os.path.join(maps, name)) as handle:
            spec = json.load(handle)
        log = record(spec, champion, 300)
        answers = replay(log, reference)
        for (payload, want), got in zip(log, answers):
            total += 1
            if strip_msg(want) != strip_msg(got):
                mismatched += 1
                if mismatched <= 3:
                    print("MISMATCH on %s:\n  champion : %s\n  reference: %s"
                          % (spec["map_id"], want, got))
        print("%-14s %5d seat-turns compared" % (spec["map_id"], len(log)))
    print("\n%d seat-turns compared over %d maps, %d differ (MSG ignored)"
          % (total, len(files), mismatched))
    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
