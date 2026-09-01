#!/usr/bin/env python3
"""Decode the champion's 160 ladder games into a per-turn observation corpus.

This is the SPEC-WRITER'S INSTRUMENT for card 20260901-cleanroom-champion.  It is
deliberately NOT part of `cleanroom/package/` -- the implementer never sees it.

Source: local_claude_1/denial-ablation/games-41202036/  (agent 6667789,
submission 41202036, the champion of record; 160 ladder games, 2026-08-27).

THE MSG RULE.  The champion of record is the diagnostics build: every turn it
prints a `MSG NARRATE v6 ...` line that names its own internal roles, intents
and counters.  That is a direct architecture leak into a document that is
supposed to be written from observable play only.  This module DROPS every MSG
command before anything else can see it, and `commands()` never returns one.
A behavioural claim in the package may rest on a unit's position, carry,
inventory, the board, and the verb/arguments of a non-MSG command -- nothing else.

State decoding uses the repository's audited replay decoder
(`cgauto.recent_resident_field_census.decoded_states`); its documented
reconstruction boundary is that plant clocks (cooldown/health/stage) are
inferred from the visual diff rather than read from it.  Anything a claim rests
on there is marked INFERRED in the package, not OBSERVED.
"""
from __future__ import annotations

import gzip
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)

from cgauto.recent_resident_field_census import decoded_states  # noqa: E402

GAMES = os.path.join(ROOT, "local_claude_1", "denial-ablation", "games-41202036",
                     "games-agent6667789-submission41202036.jsonl.gz")
CHAMPION_AGENT = 6667789
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")


class CorpusError(RuntimeError):
    pass


def split_commands(stdout: str):
    """Parsed command list for one seat-turn, with MSG removed at the source."""
    out = []
    for chunk in (stdout or "").replace("\n", ";").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split()
        verb = parts[0]
        if verb == "MSG":
            continue
        out.append((verb, [int(p) if p.lstrip("-").isdigit() else p for p in parts[1:]]))
    return out


def games(limit=None):
    """Yield one decoded game at a time.  Fail closed on any decoder complaint."""
    count = 0
    with gzip.open(GAMES, "rt") as handle:
        for line in handle:
            game = json.loads(line)
            seats = {int(a["agentId"]): int(a["index"]) for a in game["agents"]}
            if CHAMPION_AGENT not in seats:
                raise CorpusError("game %s has no champion seat" % game.get("gameId"))
            seat = seats[CHAMPION_AGENT]
            frames = game["frames"]
            if len(frames) < 3 or len(frames) % 2 != 1:
                raise CorpusError("game %s: %d frames" % (game.get("gameId"), len(frames)))
            turns = (len(frames) - 1) // 2
            traj = [{"commands0": frames[2 * t - 1].get("stdout") or "",
                     "commands1": frames[2 * t].get("stdout") or ""}
                    for t in range(1, turns + 1)]
            static, states, unknown = decoded_states(game, traj)
            if unknown:
                raise CorpusError("game %s: %d unknown diff updates" % (game.get("gameId"), unknown))
            if len(states) != turns + 1:
                raise CorpusError("game %s: %d states for %d turns"
                                  % (game.get("gameId"), len(states), turns))
            for index, state in enumerate(states):
                if int(state.get("resolved_turn", -1)) != index:
                    raise CorpusError("game %s: state %d out of order" % (game.get("gameId"), index))
            opponent = [a for a in game["agents"] if int(a["agentId"]) != CHAMPION_AGENT][0]
            yield {
                "game_id": int(game["gameId"]),
                "seat": seat,
                "turns": turns,
                "opponent_agent": int(opponent["agentId"]),
                "opponent_rating": opponent.get("score"),
                "own_rating": seats and [a for a in game["agents"]
                                         if int(a["agentId"]) == CHAMPION_AGENT][0].get("score"),
                "width": static["width"],
                "height": static["height"],
                "rows": list(static["rows"]),
                # states[t] is the state BEFORE turn t+1 is applied.
                "states": states,
                # commands[t] is what the champion printed on turn t+1.
                "commands": [split_commands(row["commands%d" % seat]) for row in traj],
                "opp_commands": [split_commands(row["commands%d" % (1 - seat)]) for row in traj],
            }
            count += 1
            if limit and count >= limit:
                return


def shack(game, seat):
    """(x, y) of a seat's shack, from the map alphabet ('0' = seat 0, '1' = seat 1)."""
    mark = str(seat)
    for y, row in enumerate(game["rows"]):
        x = row.find(mark)
        if x >= 0:
            return (x, y)
    raise CorpusError("game %s: no shack '%s' on the map" % (game["game_id"], mark))


def own_units(state, seat):
    return [u for u in state["units"] if int(u["player"]) == seat]


def unit_by_id(state, uid):
    for u in state["units"]:
        if int(u["id"]) == uid:
            return u
    return None


def plant_at(state, x, y):
    for p in state["plants"]:
        if int(p["x"]) == x and int(p["y"]) == y:
            return p
    return None


# --- geometry helpers (the referee's own distance: BFS over GRASS) ----------

def walkable_set(game):
    cells = set()
    for y, row in enumerate(game["rows"]):
        for x, ch in enumerate(row):
            if ch == ".":
                cells.add((x, y))
    return cells


def bfs(walkable, sources):
    """Distances from `sources`; sources are seeded at 0 even if unwalkable."""
    from collections import deque
    dist = {s: 0 for s in sources}
    queue = deque(sources)
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nxt = (cx + dx, cy + dy)
            if nxt in dist or nxt not in walkable:
                continue
            dist[nxt] = dist[(cx, cy)] + 1
            queue.append(nxt)
    return dist
