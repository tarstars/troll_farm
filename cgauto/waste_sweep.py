#!/usr/bin/env python3
"""Standing execution-waste detector library + CLI (round-2 dimensions).

Read-only diagnostic tool: it never touches the arena, never edits corpus data, and
never proposes strategy changes.  It measures concrete per-turn/per-episode execution
waste in the resident's own already-played arena replays, reusing this repo's existing
decoders rather than writing a new replay parser:

- ``cgauto.recent_resident_field_census.decoded_states``/``current_player`` -- exact
  official per-turn state reconstruction from ``frame.diff`` data.
- ``cgauto.replay_conformance.action_commands`` -- turn-string -> command-list parsing.
- ``cgauto.top_player_opening_analysis.terrain``/``adjacent``/``bfs``/
  ``assigned_unit_commands`` -- map decoding, door/BFS geometry, and positional command
  attribution.

Six detectors, one signature each (see each ``detect_*`` function's docstring for the
exact per-turn/episode definition used):

1. ``idle_with_work``
2. ``unbanked_carry``
3. ``harvest_slack``
4. ``door_queue``
5. ``late_train_window``
6. ``repeated_failed_command``

Every detection threshold is a module constant (see the "thresholds" section below) --
these define the signatures and are intentionally not CLI-tunable.

CLI usage::

    python3 cgauto/waste_sweep.py --output <path/to/report.json> [--jobs 8] [--limit N]

The report JSON contains, per detector: total episodes, per-game episode counts, a
win/loss/catastrophe breakdown, and the worst (longest-duration) episodes with full
per-episode detail (game id, turn range, and a causality snapshot relative to that
game's margin trajectory and permanent-crossover turn).
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.recent_resident_field_census import current_player, decoded_states
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import adjacent, assigned_unit_commands, bfs, terrain

REPO = Path(__file__).resolve().parent.parent
RAW_GAMES = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
GAMES_INDEX = REPO / "data/processed/games.jsonl"

RESIDENT_AGENT_ID = 6561795

ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ITEM_INDEX = {name: index for index, name in enumerate(ITEMS)}
FRUIT_INDICES = (0, 1, 2, 3)
IRON_INDEX = 4
WOOD_INDEX = 5
UNREACHABLE = 10_000

# ---------------------------------------------------------------------------
# Detection thresholds -- module constants, not CLI-tunable.  These *define* the
# signatures being swept for; changing them changes what counts as an episode.
# ---------------------------------------------------------------------------
CATASTROPHE_MARGIN = -100  # matches the project-wide "catastrophe" definition

UNBANKED_CARRY_MIN_RUN = 8  # turns; spec: "long stretches (>=8 turns)"
UNBANKED_CARRY_DOOR_RADIUS = 2  # BFS walkable-graph distance to nearest own door

HARVEST_SLACK_MIN_RUN = 3  # consecutive turns
HARVEST_SLACK_ADJACENT_RADIUS = 1  # Manhattan distance counted as "adjacent"

LATE_TRAIN_MIN_RUN = 5  # consecutive affordable-but-untrained turns

REPEATED_FAILED_COMMAND_MIN_RUN = 3  # consecutive identical-and-failing turns

WORST_EPISODES_KEPT = 10  # report depth, not a detection threshold


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def carried_value(carry: list[int]) -> int:
    """Bank-equivalent value of a carry vector, using the game's own score formula."""

    return sum(carry[0:4]) + 4 * carry[WOOD_INDEX]


def training_cost(n: int, talents: tuple[int, int, int, int]) -> list[int]:
    """Exact port of ``sim.engine.apply_train``'s cost formula (PLUM/LEMON/APPLE/IRON)."""

    ms, cc, hp, chop = talents
    cost = [0] * 6
    cost[0] = n + ms * ms
    cost[1] = n + cc * cc
    cost[2] = n + hp * hp
    cost[IRON_INDEX] = n + chop * chop
    return cost


def training_pay_indices(iron_present: bool) -> tuple[int, ...]:
    """Iron is only charged when the map actually has iron terrain (``sim.engine
    .apply_train``'s ``pay = (...) if game.iron else (...)``); BANANA/WOOD cost is
    always zero so omitting indices 3/5 never changes the affordability check."""

    return (0, 1, 2, IRON_INDEX) if iron_present else (0, 1, 2)


def training_affordable(n: int, talents: tuple[int, int, int, int], bank: list[int], iron_present: bool) -> bool:
    cost = training_cost(n, talents)
    return all(bank[index] >= cost[index] for index in training_pay_indices(iron_present))


def training_blocked(own_units_before, shack: tuple[int, int]) -> bool:
    """Mirrors ``apply_train``'s ``any(u.pos == game.shacks[player] ...)`` guard."""

    return any((unit["x"], unit["y"]) == shack for unit in own_units_before)


# ---------------------------------------------------------------------------
# Decoded-game data model
# ---------------------------------------------------------------------------


@dataclass
class DecodedGame:
    """Everything the detectors need for one resident game, decoded once."""

    game_id: int
    me: int
    opponent: int
    opponent_name: str
    margin: int
    won: bool
    turns: int  # usable turn count N; states[0..N], trajectory[0..N-1]
    board: dict  # {"walkable","water","iron","shacks"} from top_player_opening_analysis.terrain
    own_shack: tuple[int, int]
    opp_shack: tuple[int, int]
    own_doors: list[tuple[int, int]]
    opp_doors: list[tuple[int, int]]
    own_distance: dict  # BFS distance from any own door, over walkable cells
    opp_distance: dict  # BFS distance from any opponent door, over walkable cells
    iron_present: bool
    states: list[dict]
    trajectory: list[dict]
    margin_series: list[int]  # my_score - opponent_score at each state index 0..N
    crossover_turn: int  # last turn after which margin never returns >= 0 (0 if never ahead)
    train_events: list[dict]  # [{"turn","talents","n_before"}], own successful TRAINs


@dataclass
class TurnFrame:
    """Per-turn context shared by every detector: state at the start and end of one
    turn, the commands the resident issued, and unit-id-keyed positional attribution."""

    turn: int
    my_commands: list[str]
    opp_commands: list[str]
    before_units: dict[int, dict]
    after_units: dict[int, dict]
    assigned: dict[int, str]
    before_plants: dict[tuple[int, int], dict]
    after_plants: dict[tuple[int, int], dict]
    bank_before: list[int]
    bank_after: list[int]


def _crossover_turn(margin_series: list[int]) -> int:
    """Last turn after which margin never returns to >= 0 (project-standard definition,
    reused verbatim from the B3.1/B3.3 resident-catastrophe audits)."""

    for index in range(len(margin_series) - 1, -1, -1):
        if margin_series[index] >= 0:
            return index + 1
    return 0


def _find_train_events(me: int, states: list[dict], trajectory: list[dict]) -> list[dict]:
    """Successful TRAINs: a turn where the resident's own unit count increases and a
    TRAIN command is present in that turn's own commands (talents parsed from the
    command text -- the only ground truth available for what the policy actually
    wanted, since the referee's summary text does not repeat the talent vector)."""

    events = []
    usable = min(len(states) - 1, len(trajectory))
    for turn in range(1, usable + 1):
        before_ids = {unit["id"] for unit in states[turn - 1]["units"] if unit["player"] == me}
        after_ids = {unit["id"] for unit in states[turn]["units"] if unit["player"] == me}
        if len(after_ids) <= len(before_ids):
            continue
        commands = action_commands(trajectory[turn - 1].get(f"commands{me}"))
        talents = None
        for command in commands:
            fields = command.split()
            if fields and fields[0].upper() == "TRAIN" and len(fields) == 5:
                try:
                    talents = tuple(int(value) for value in fields[1:5])
                except ValueError:
                    talents = None
                break
        if talents is not None:
            events.append({"turn": turn, "talents": talents, "n_before": len(before_ids)})
    return events


def build_decoded_game(
    *,
    game_id: int,
    me: int,
    map_rows: list[str],
    states: list[dict],
    trajectory: list[dict],
    scores,
    ranks,
    opponent_name: str = "?",
) -> DecodedGame:
    """Build a :class:`DecodedGame` from already-decoded pieces.  Used both by the real
    file-loading path (:func:`decode_game`) and directly by unit tests with small
    synthetic maps/states/trajectories."""

    opponent = 1 - me
    board = terrain({"rows": map_rows})
    own_shack = board["shacks"][me]
    opp_shack = board["shacks"][opponent]
    own_doors = [cell for cell in adjacent(own_shack) if cell in board["walkable"]]
    opp_doors = [cell for cell in adjacent(opp_shack) if cell in board["walkable"]]
    own_distance = bfs(board["walkable"], own_doors)
    opp_distance = bfs(board["walkable"], opp_doors)
    turns = min(len(states) - 1, len(trajectory))
    margin_series = [
        carried_value(state["inventories"][me]) - carried_value(state["inventories"][opponent])
        for state in states
    ]
    crossover_turn = _crossover_turn(margin_series)
    scores_i = [int(value) for value in scores]
    margin = scores_i[me] - scores_i[opponent]
    won = bool(ranks and len(ranks) == 2 and ranks[me] == 0 and margin > 0)
    train_events = _find_train_events(me, states, trajectory)
    return DecodedGame(
        game_id=game_id,
        me=me,
        opponent=opponent,
        opponent_name=opponent_name,
        margin=margin,
        won=won,
        turns=turns,
        board=board,
        own_shack=own_shack,
        opp_shack=opp_shack,
        own_doors=own_doors,
        opp_doors=opp_doors,
        own_distance=own_distance,
        opp_distance=opp_distance,
        iron_present=bool(board["iron"]),
        states=states,
        trajectory=trajectory,
        margin_series=margin_series,
        crossover_turn=crossover_turn,
        train_events=train_events,
    )


def decode_game(game_id: int) -> DecodedGame:
    """Load one resident game from the on-disk corpus and fully decode it."""

    game = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
    trajectory = [
        json.loads(line)
        for line in (TRAJECTORIES / f"{game_id}.jsonl").read_text().splitlines()
        if line.strip()
    ]
    me = current_player(game)
    if me is None:
        raise ValueError(f"game {game_id}: resident seat not found")
    map_data, states, unknown_updates = decoded_states(game, trajectory)
    if unknown_updates:
        raise ValueError(f"game {game_id}: {unknown_updates} unknown diff updates")
    agents = game.get("agents") or []
    opponent_agent = agents[1 - me] or {} if len(agents) == 2 else {}
    opponent_name = (
        (opponent_agent.get("codingamer") or {}).get("pseudo")
        or (opponent_agent.get("arenaboss") or {}).get("nickname")
        or "?"
    )
    return build_decoded_game(
        game_id=game_id,
        me=me,
        map_rows=map_data["rows"],
        states=states,
        trajectory=trajectory,
        scores=game["scores"],
        ranks=game.get("ranks") or [],
        opponent_name=opponent_name,
    )


def resident_game_ids() -> list[int]:
    """Every game in the processed corpus index that the resident agent played in."""

    ids = []
    with GAMES_INDEX.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if any(int(player["agentId"]) == RESIDENT_AGENT_ID for player in row["players"]):
                ids.append(int(row["gameId"]))
    return sorted(ids)


def iter_turn_frames(game: DecodedGame):
    for turn in range(1, game.turns + 1):
        before = game.states[turn - 1]
        after = game.states[turn]
        row = game.trajectory[turn - 1]
        my_commands = action_commands(row.get(f"commands{game.me}"))
        opp_commands = action_commands(row.get(f"commands{game.opponent}"))
        before_units = {unit["id"]: unit for unit in before["units"] if unit["player"] == game.me}
        after_units = {unit["id"]: unit for unit in after["units"] if unit["player"] == game.me}
        assigned = assigned_unit_commands(my_commands, list(before_units.values()))
        before_plants = {(plant["x"], plant["y"]): plant for plant in before["plants"]}
        after_plants = {(plant["x"], plant["y"]): plant for plant in after["plants"]}
        yield TurnFrame(
            turn=turn,
            my_commands=my_commands,
            opp_commands=opp_commands,
            before_units=before_units,
            after_units=after_units,
            assigned=assigned,
            before_plants=before_plants,
            after_plants=after_plants,
            bank_before=before["inventories"][game.me],
            bank_after=after["inventories"][game.me],
        )


# ---------------------------------------------------------------------------
# Shared legality helpers (used by more than one detector)
# ---------------------------------------------------------------------------


def legal_productive_actions(
    unit: dict, plants_by_cell: dict, bank: list[int], shack: tuple[int, int], walkable: set
) -> set[str]:
    """The productive actions the ``idle_with_work`` task text names as available
    "on its cell or adjacent": harvest ripe fruit, pick (a fruit seed from the bank),
    plant a carried seed, chop a tree sitting on the unit's own cell, or bank cargo at
    an adjacent door.  Evaluated against the unit's position/stats at the *start* of
    the turn (the situation the bot actually saw when it chose this turn's command).
    """

    pos = (unit["x"], unit["y"])
    carry = unit["carry"]
    free = unit["cc"] - sum(carry)
    plant = plants_by_cell.get(pos)
    actions: set[str] = set()
    if plant is not None and plant["fruits"] > 0 and unit["hp"] >= 1 and free > 0:
        actions.add("HARVEST")
    if plant is not None and unit["chop"] > 0:
        actions.add("CHOP")
    if pos in walkable and plant is None and any(carry[index] > 0 for index in FRUIT_INDICES):
        # apply_plant() has no capacity check -- planting spends an already-carried
        # seed, it does not need room for anything new.
        actions.add("PLANT")
    near_shack = manhattan(pos, shack) <= 1
    if near_shack and free > 0 and any(bank[index] > 0 for index in FRUIT_INDICES):
        actions.add("PICK")
    if near_shack and sum(carry) > 0:
        actions.add("BANK")
    return actions


def command_precondition_met(
    verb: str,
    fields: list[str],
    unit: dict,
    plants_by_cell: dict,
    bank: list[int],
    shack: tuple[int, int],
    iron_cells: set,
    walkable: set,
) -> bool | None:
    """Whether ``verb``'s rules-level precondition holds given the unit's position/
    stats/carry at the *start* of the turn.  HARVEST/PICK/PLANT/CHOP/DROP/MINE are
    deterministic once legal (the referee's mechanics grant the effect unconditionally
    once the precondition holds, no RNG involved), so precondition exactly determines
    success -- this avoids the pitfall of diffing post-turn state, where an
    independent same-turn tree-growth tick can mask/mimic a CHOP's health delta.
    MOVE has no such precondition under this bot's own pre-resolved collision handling
    (round-1 confirmed 0% "no_progress" / landed-in-place moves for the resident), so
    it returns ``None`` here; callers judge MOVE from the actual landing instead.
    """

    pos = (unit["x"], unit["y"])
    carry = unit["carry"]
    free = unit["cc"] - sum(carry)
    plant = plants_by_cell.get(pos)
    if verb == "HARVEST":
        return plant is not None and plant["fruits"] > 0 and unit["hp"] >= 1 and free > 0
    if verb == "CHOP":
        return plant is not None and unit["chop"] > 0
    if verb == "PICK":
        if len(fields) < 3 or fields[2] not in ITEM_INDEX:
            return False
        index = ITEM_INDEX[fields[2]]
        return manhattan(pos, shack) <= 1 and free > 0 and bank[index] > 0
    if verb == "PLANT":
        if len(fields) < 3 or fields[2] not in ITEM_INDEX:
            return False
        index = ITEM_INDEX[fields[2]]
        return pos in walkable and plant is None and carry[index] > 0
    if verb == "DROP":
        return manhattan(pos, shack) <= 1 and sum(carry) > 0
    if verb == "MINE":
        return unit["chop"] > 0 and free > 0 and any(manhattan(pos, ore) == 1 for ore in iron_cells)
    return None


# ---------------------------------------------------------------------------
# Generic maximal-run tracker, shared by every episode-based detector
# ---------------------------------------------------------------------------


class RunTracker:
    """Tracks maximal consecutive-turn runs keyed by an arbitrary hashable key.

    Usage per turn: call :meth:`mark` for every key whose flagged condition holds this
    turn, then call :meth:`sweep` with the set of keys marked this turn -- it closes
    (and returns) any previously-open run whose key was *not* marked, i.e. whose
    condition just became false.  Call :meth:`flush` once at the end to collect any
    runs still open when the game ends.
    """

    def __init__(self) -> None:
        self._open: dict = {}

    def mark(self, key, turn: int, detail: dict | None = None) -> None:
        run = self._open.get(key)
        if run is None:
            run = {"key": key, "start": turn, "end": turn, "details": []}
            self._open[key] = run
        else:
            run["end"] = turn
        if detail is not None:
            run["details"].append(detail)

    def sweep(self, active_keys) -> list[dict]:
        finished = []
        for key in list(self._open):
            if key not in active_keys:
                finished.append(self._open.pop(key))
        return finished

    def flush(self) -> list[dict]:
        finished = list(self._open.values())
        self._open.clear()
        return finished


def causality_context(game: DecodedGame, start_turn: int, end_turn: int) -> dict:
    """Cheap causality screen shared by every detector: where does this episode sit
    relative to the game's own permanent margin crossover, and what happened to the
    margin during the episode's own window."""

    margin_before = game.margin_series[start_turn - 1]
    margin_after = game.margin_series[end_turn]
    crossover = game.crossover_turn
    if end_turn < crossover:
        relation = "before_crossover"
    elif start_turn > crossover:
        relation = "after_crossover"
    else:
        relation = "straddles_crossover"
    return {
        "margin_before_episode": margin_before,
        "margin_after_episode": margin_after,
        "margin_delta_during_episode": margin_after - margin_before,
        "crossover_turn": crossover,
        "relation_to_crossover": relation,
        "game_margin": game.margin,
        "game_won": game.won,
        "catastrophe": game.margin <= CATASTROPHE_MARGIN,
    }


def _episode(game: DecodedGame, detector: str, run: dict, *, extra_key: dict, detail: dict) -> dict:
    duration = run["end"] - run["start"] + 1
    episode = {
        "game_id": game.game_id,
        "detector": detector,
        "start_turn": run["start"],
        "end_turn": run["end"],
        "duration": duration,
        "detail": detail,
    }
    episode.update(extra_key)
    episode["causality"] = causality_context(game, run["start"], run["end"])
    return episode


# ---------------------------------------------------------------------------
# Detector 1: idle_with_work
# ---------------------------------------------------------------------------


def detect_idle_with_work(game: DecodedGame) -> list[dict]:
    """Turns where an own worker issues WAIT/no-op or a non-productive MOVE while a
    legal productive action existed on its own cell or adjacent to it: harvest ripe
    fruit, pick a seed from the bank, plant a carried seed, chop the tree on its own
    cell, or bank cargo at an adjacent door.  Episode = a maximal run of consecutive
    such turns for the same unit (the spec gives no minimum run length for this
    detector, so every isolated flagged turn is its own 1-turn episode; runs are
    reported so "worst" episodes are meaningful rather than an arbitrary single turn).
    """

    tracker = RunTracker()
    episodes = []
    for frame in iter_turn_frames(game):
        active = set()
        for unit_id, unit in frame.before_units.items():
            command = frame.assigned.get(unit_id)
            verb = command.split()[0].upper() if command else "WAIT"
            if verb not in ("WAIT", "MOVE"):
                continue
            legal = legal_productive_actions(
                unit, frame.before_plants, frame.bank_before, game.own_shack, game.board["walkable"]
            )
            if legal:
                tracker.mark(
                    unit_id,
                    frame.turn,
                    {"turn": frame.turn, "verb": verb, "legal": sorted(legal), "pos": [unit["x"], unit["y"]]},
                )
                active.add(unit_id)
        for run in tracker.sweep(active):
            episodes.append(_finish_idle_with_work(game, run))
    for run in tracker.flush():
        episodes.append(_finish_idle_with_work(game, run))
    return episodes


def _finish_idle_with_work(game: DecodedGame, run: dict) -> dict:
    details = run["details"]
    legal_union = sorted({action for row in details for action in row["legal"]})
    verb_counts = dict(Counter(row["verb"] for row in details))
    detail = {
        "legal_actions_seen": legal_union,
        "verb_counts": verb_counts,
        "positions": [row["pos"] for row in details],
    }
    return _episode(game, "idle_with_work", run, extra_key={"unit_id": run["key"]}, detail=detail)


# ---------------------------------------------------------------------------
# Detector 2: unbanked_carry
# ---------------------------------------------------------------------------


def detect_unbanked_carry(game: DecodedGame) -> list[dict]:
    """Long stretches (>= UNBANKED_CARRY_MIN_RUN turns) where a worker simultaneously
    holds cargo (a DROP always fully empties carry) *and* stays within
    UNBANKED_CARRY_DOOR_RADIUS BFS (walkable-graph) steps of an own door, the whole
    stretch, without ever banking.  Both conditions are required on every turn of the
    run (not just glimpsed once) so a unit that simply spends a long time walking home
    from a distant chop site -- genuinely too far to bank for most of that time, then
    banks immediately on arrival -- is not misclassified as loitering near its own
    door; this only flags sustained proximity-with-cargo-but-no-drop.  Episode = one
    such qualifying run per unit.
    """

    tracker = RunTracker()
    episodes = []
    for frame in iter_turn_frames(game):
        active = set()
        for unit_id, unit in frame.after_units.items():
            if sum(unit["carry"]) <= 0:
                continue
            pos = (unit["x"], unit["y"])
            distance = game.own_distance.get(pos)
            if distance is None or distance > UNBANKED_CARRY_DOOR_RADIUS:
                continue
            tracker.mark(
                unit_id,
                frame.turn,
                {"turn": frame.turn, "pos": list(pos), "carry": list(unit["carry"]), "door_distance": distance},
            )
            active.add(unit_id)
        for run in tracker.sweep(active):
            episode = _maybe_finish_unbanked_carry(game, run)
            if episode is not None:
                episodes.append(episode)
    for run in tracker.flush():
        episode = _maybe_finish_unbanked_carry(game, run)
        if episode is not None:
            episodes.append(episode)
    return episodes


def _maybe_finish_unbanked_carry(game: DecodedGame, run: dict) -> dict | None:
    duration = run["end"] - run["start"] + 1
    if duration < UNBANKED_CARRY_MIN_RUN:
        return None
    distances = [row["door_distance"] for row in run["details"]]
    detail = {
        "closest_door_distance": min(distances),
        "carry_at_start": run["details"][0]["carry"],
        "carry_at_end": run["details"][-1]["carry"],
        "carried_value_at_end": carried_value(run["details"][-1]["carry"]),
    }
    return _episode(game, "unbanked_carry", run, extra_key={"unit_id": run["key"]}, detail=detail)


# ---------------------------------------------------------------------------
# Detector 3: harvest_slack
# ---------------------------------------------------------------------------


def detect_harvest_slack(game: DecodedGame) -> list[dict]:
    """Own or unclaimed ripe fruit (a plant with fruits > 0, on a cell no closer to
    the opponent's doors than to the resident's own -- i.e. not strictly opponent
    territory) that sits within HARVEST_SLACK_ADJACENT_RADIUS (Manhattan) of an own
    worker for >= HARVEST_SLACK_MIN_RUN consecutive turns without being harvested (the
    run ends the moment fruit count drops, by whoever's harvest, or the tree/adjacency
    condition lapses).  Episode = one such run per plant cell.

    "Adjacent to a worker" only requires *an* own worker nearby, regardless of that
    worker's own harvest_power -- a worker with harvest_power 0 parked on ripe fruit
    while dedicated to chopping is not itself acting wrongly, but a persistent nearby
    opportunity can still reflect a real cross-worker allocation gap (nobody was ever
    routed to it).  To let the report distinguish the two, each turn also records
    whether at least one *capable* (harvest_power >= 1) own worker was in range; the
    finished episode's ``any_capable_worker_seen`` flag summarizes this across the run.
    """

    tracker = RunTracker()
    episodes = []
    for turn in range(1, game.turns + 1):
        state = game.states[turn]
        own_units = [unit for unit in state["units"] if unit["player"] == game.me]
        active = set()
        for plant in state["plants"]:
            if plant["fruits"] <= 0:
                continue
            cell = (plant["x"], plant["y"])
            if game.own_distance.get(cell, UNREACHABLE) > game.opp_distance.get(cell, UNREACHABLE):
                continue  # strictly opponent territory; out of scope
            distances = [manhattan(cell, (unit["x"], unit["y"])) for unit in own_units]
            in_range = [d <= HARVEST_SLACK_ADJACENT_RADIUS for d in distances]
            if not any(in_range):
                continue
            capable_in_range = any(
                d <= HARVEST_SLACK_ADJACENT_RADIUS and unit["hp"] >= 1
                for d, unit in zip(distances, own_units)
            )
            tracker.mark(
                cell,
                turn,
                {
                    "turn": turn,
                    "fruits": plant["fruits"],
                    "type": plant["type"],
                    "nearest_worker_distance": min(distances),
                    "capable_worker_in_range": capable_in_range,
                },
            )
            active.add(cell)
        for run in tracker.sweep(active):
            episode = _maybe_finish_harvest_slack(game, run)
            if episode is not None:
                episodes.append(episode)
    for run in tracker.flush():
        episode = _maybe_finish_harvest_slack(game, run)
        if episode is not None:
            episodes.append(episode)
    return episodes


def _maybe_finish_harvest_slack(game: DecodedGame, run: dict) -> dict | None:
    duration = run["end"] - run["start"] + 1
    if duration < HARVEST_SLACK_MIN_RUN:
        return None
    details = run["details"]
    detail = {
        "plant_type": details[0]["type"],
        "fruits_at_start": details[0]["fruits"],
        "fruits_at_end": details[-1]["fruits"],
        "closest_worker_distance_seen": min(row["nearest_worker_distance"] for row in details),
        "any_capable_worker_seen": any(row["capable_worker_in_range"] for row in details),
    }
    return _episode(game, "harvest_slack", run, extra_key={"cell": list(run["key"])}, detail=detail)


# ---------------------------------------------------------------------------
# Detector 4: door_queue
# ---------------------------------------------------------------------------


def detect_door_queue(game: DecodedGame) -> list[dict]:
    """Turns lost to serialized banking: >= 2 own workers simultaneously within
    Manhattan distance 1 of the *same* own door, each carrying cargo, where not all of
    them end the turn with empty carry (a DROP always fully empties carry, so "not all
    empty" means at least one of the clustered carriers did not bank this turn despite
    being right there).  This is a conservative proxy for physical blocking -- it does
    not by itself prove one worker's presence caused another's non-bank, only that the
    two conditions (clustering + partial-or-no banking) co-occurred; worst episodes
    should be read as candidates for manual confirmation, not a proven mechanism.
    Episode = a maximal run of consecutive flagged turns for the same door cell.
    """

    tracker = RunTracker()
    episodes = []
    for frame in iter_turn_frames(game):
        active = set()
        for door in game.own_doors:
            here = [
                unit_id
                for unit_id, unit in frame.before_units.items()
                if manhattan((unit["x"], unit["y"]), door) <= 1 and sum(unit["carry"]) > 0
            ]
            if len(here) < 2:
                continue
            banked = [unit_id for unit_id in here if _fully_banked(frame, unit_id)]
            if len(banked) == len(here):
                continue
            tracker.mark(door, frame.turn, {"turn": frame.turn, "units": here, "banked": banked})
            active.add(door)
        for run in tracker.sweep(active):
            episodes.append(_finish_door_queue(game, run))
    for run in tracker.flush():
        episodes.append(_finish_door_queue(game, run))
    return episodes


def _fully_banked(frame: TurnFrame, unit_id: int) -> bool:
    """True only if this unit actually issued (and completed) a DROP this turn --
    *not* merely "ended the turn with empty carry", since PLANT can also zero out
    carry (by spending the unit's one and only carried seed) without ever banking."""

    command = frame.assigned.get(unit_id)
    if command is None or command.split()[0].upper() != "DROP":
        return False
    unit = frame.after_units.get(unit_id)
    return unit is not None and sum(unit["carry"]) == 0


def _finish_door_queue(game: DecodedGame, run: dict) -> dict:
    details = run["details"]
    units_involved = sorted({unit_id for row in details for unit_id in row["units"]})
    detail = {
        "units_involved": units_involved,
        "turns_with_zero_banked": sum(1 for row in details if not row["banked"]),
        "turns_with_partial_banked": sum(1 for row in details if row["banked"] and len(row["banked"]) < len(row["units"])),
    }
    return _episode(game, "door_queue", run, extra_key={"door": list(run["key"])}, detail=detail)


# ---------------------------------------------------------------------------
# Detector 5: late_train_window
# ---------------------------------------------------------------------------


def detect_late_train_window(game: DecodedGame) -> list[dict]:
    """Informational: turns where a TRAIN was fully affordable in deposited (banked)
    stock and stayed affordable for >= LATE_TRAIN_MIN_RUN consecutive turns with no
    TRAIN command issued, using the resident's *own* revealed bill for that game (the
    talent vector of its own next successful TRAIN) as the affordability target -- the
    only "the resident's own policy would want" bill this decoder-reuse tool can ground
    in evidence rather than assumption.  Scanned only in the window strictly before
    each successful TRAIN in that same game; games where the resident never trains
    contribute no episodes (no revealed bill to check against; documented scope
    limitation, not "no waste found").  Training policy itself (what to train, when)
    is strategy; a *missed* window the policy's own later choice reveals it wanted is
    execution.
    """

    episodes = []
    window_start = 1
    for event in game.train_events:
        tracker = RunTracker()
        talents = event["talents"]
        for turn in range(window_start, event["turn"]):
            bank_before = game.states[turn - 1]["inventories"][game.me]
            n_before = sum(1 for unit in game.states[turn - 1]["units"] if unit["player"] == game.me)
            issued_train = any(
                command.split()[0].upper() == "TRAIN"
                for command in action_commands(game.trajectory[turn - 1].get(f"commands{game.me}"))
            )
            affordable = training_affordable(n_before, talents, bank_before, game.iron_present)
            active = set()
            if affordable and not issued_train:
                tracker.mark(
                    "pretrain",
                    turn,
                    {"turn": turn, "bank": list(bank_before), "own_workers": n_before},
                )
                active.add("pretrain")
            for run in tracker.sweep(active):
                episode = _maybe_finish_late_train(game, event, run)
                if episode is not None:
                    episodes.append(episode)
        for run in tracker.flush():
            episode = _maybe_finish_late_train(game, event, run)
            if episode is not None:
                episodes.append(episode)
        window_start = event["turn"] + 1
    return episodes


def _maybe_finish_late_train(game: DecodedGame, event: dict, run: dict) -> dict | None:
    duration = run["end"] - run["start"] + 1
    if duration < LATE_TRAIN_MIN_RUN:
        return None
    details = run["details"]
    detail = {
        "reference_train_turn": event["turn"],
        "reference_talents": list(event["talents"]),
        "own_workers_during_window": details[0]["own_workers"],
        "bank_at_window_start": details[0]["bank"],
        "bank_at_window_end": details[-1]["bank"],
    }
    return _episode(game, "late_train_window", run, extra_key={"unit_id": None}, detail=detail)


# ---------------------------------------------------------------------------
# Detector 6: repeated_failed_command
# ---------------------------------------------------------------------------


def detect_repeated_failed_command(game: DecodedGame) -> list[dict]:
    """The same command (identical verb + unit + args, or an identical TRAIN talent
    vector) failing -- producing no state effect, per its rules-level precondition for
    HARVEST/PICK/PLANT/CHOP/DROP/MINE/TRAIN, or landing back on its origin cell for
    MOVE -- for >= REPEATED_FAILED_COMMAND_MIN_RUN consecutive turns.  WAIT is excluded
    (a no-op by design, not a failure).  Episode = one such consecutive-occurrence run
    per unit (or the synthetic "TRAIN" key for the not-unit-scoped TRAIN command).
    """

    episodes = []
    state: dict = {}
    for frame in iter_turn_frames(game):
        candidates = _turn_command_candidates(game, frame)
        seen_keys = set()
        for key, command, failed in candidates:
            seen_keys.add(key)
            prior = state.get(key)
            if failed:
                if prior is not None and prior["command"] == command:
                    prior["length"] += 1
                    prior["end"] = frame.turn
                else:
                    if prior is not None and prior["length"] >= REPEATED_FAILED_COMMAND_MIN_RUN:
                        episodes.append(_finish_repeated_failed_command(game, key, prior))
                    state[key] = {"command": command, "length": 1, "start": frame.turn, "end": frame.turn}
            else:
                if prior is not None and prior["length"] >= REPEATED_FAILED_COMMAND_MIN_RUN:
                    episodes.append(_finish_repeated_failed_command(game, key, prior))
                state.pop(key, None)
        for key in list(state):
            if key not in seen_keys:
                finished = state.pop(key)
                if finished["length"] >= REPEATED_FAILED_COMMAND_MIN_RUN:
                    episodes.append(_finish_repeated_failed_command(game, key, finished))
    for key, finished in state.items():
        if finished["length"] >= REPEATED_FAILED_COMMAND_MIN_RUN:
            episodes.append(_finish_repeated_failed_command(game, key, finished))
    return episodes


def _turn_command_candidates(game: DecodedGame, frame: TurnFrame) -> list[tuple]:
    candidates = []
    for unit_id, unit in frame.before_units.items():
        command = frame.assigned.get(unit_id)
        if command is None:
            continue
        fields = command.split()
        if not fields:
            continue
        verb = fields[0].upper()
        if verb == "WAIT":
            continue
        if verb == "MOVE":
            after_unit = frame.after_units.get(unit_id)
            if after_unit is None:
                continue
            failed = (after_unit["x"], after_unit["y"]) == (unit["x"], unit["y"])
        else:
            met = command_precondition_met(
                verb, fields, unit, frame.before_plants, frame.bank_before,
                game.own_shack, game.board["iron"], game.board["walkable"],
            )
            if met is None:
                continue
            failed = not met
        candidates.append((unit_id, command, failed))

    train_command = next(
        (command for command in frame.my_commands if command.split()[0].upper() == "TRAIN"), None
    )
    if train_command is not None:
        fields = train_command.split()
        if len(fields) == 5:
            try:
                talents = tuple(int(value) for value in fields[1:5])
            except ValueError:
                talents = None
            if talents is not None:
                n_before = len(frame.before_units)
                ok = training_affordable(
                    n_before, talents, frame.bank_before, game.iron_present
                ) and not training_blocked(frame.before_units.values(), game.own_shack)
                candidates.append(("TRAIN", train_command, not ok))
    return candidates


def _finish_repeated_failed_command(game: DecodedGame, key, run: dict) -> dict:
    detail = {"command": run["command"], "repeat_count": run["length"]}
    unit_id = None if key == "TRAIN" else key
    episode = {
        "game_id": game.game_id,
        "detector": "repeated_failed_command",
        "unit_id": unit_id,
        "start_turn": run["start"],
        "end_turn": run["end"],
        "duration": run["end"] - run["start"] + 1,
        "detail": detail,
    }
    episode["causality"] = causality_context(game, run["start"], run["end"])
    return episode


DETECTORS = {
    "idle_with_work": detect_idle_with_work,
    "unbanked_carry": detect_unbanked_carry,
    "harvest_slack": detect_harvest_slack,
    "door_queue": detect_door_queue,
    "late_train_window": detect_late_train_window,
    "repeated_failed_command": detect_repeated_failed_command,
}

DETECTOR_THRESHOLDS = {
    "idle_with_work": {},
    "unbanked_carry": {
        "min_run_turns": UNBANKED_CARRY_MIN_RUN,
        "door_radius_bfs_steps": UNBANKED_CARRY_DOOR_RADIUS,
    },
    "harvest_slack": {
        "min_run_turns": HARVEST_SLACK_MIN_RUN,
        "adjacent_radius_manhattan": HARVEST_SLACK_ADJACENT_RADIUS,
    },
    "door_queue": {},
    "late_train_window": {"min_run_turns": LATE_TRAIN_MIN_RUN},
    "repeated_failed_command": {"min_consecutive_turns": REPEATED_FAILED_COMMAND_MIN_RUN},
}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def summarize_detector(name: str, games_meta: list[dict], episodes_by_game: dict[int, list[dict]]) -> dict:
    all_episodes = [episode for episodes in episodes_by_game.values() for episode in episodes]
    per_game_counts = {str(game["game_id"]): len(episodes_by_game.get(game["game_id"], [])) for game in games_meta}
    counts_list = list(per_game_counts.values())
    games_with_episode = sum(1 for count in counts_list if count > 0)

    def bucket(predicate) -> dict:
        matched = [episode for episode in all_episodes if predicate(episode)]
        game_ids = {episode["game_id"] for episode in matched}
        return {"episodes": len(matched), "games_with_episode": len(game_ids)}

    worst = sorted(
        all_episodes,
        key=lambda episode: (episode["duration"], episode["game_id"], episode["start_turn"]),
        reverse=True,
    )[:WORST_EPISODES_KEPT]

    return {
        "detector": name,
        "definition": (DETECTORS[name].__doc__ or "").strip(),
        "thresholds": DETECTOR_THRESHOLDS[name],
        "games_swept": len(games_meta),
        "total_episodes": len(all_episodes),
        "total_flagged_turns": sum(episode["duration"] for episode in all_episodes),
        "games_with_episode": games_with_episode,
        "episodes_per_game": {
            "mean": statistics.mean(counts_list) if counts_list else 0,
            "median": statistics.median(counts_list) if counts_list else 0,
            "max": max(counts_list) if counts_list else 0,
        },
        "per_game_counts": per_game_counts,
        "wins": bucket(lambda episode: episode["causality"]["game_won"]),
        "losses": bucket(
            lambda episode: not episode["causality"]["game_won"] and episode["causality"]["game_margin"] < 0
        ),
        "catastrophes": bucket(lambda episode: episode["causality"]["catastrophe"]),
        "worst_episodes": worst,
    }


def _analyze_one_game(game_id: int) -> dict:
    try:
        game = decode_game(game_id)
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit, one bad game shouldn't abort the sweep
        return {"ok": False, "game_id": game_id, "error": f"{type(exc).__name__}: {exc}"}
    episodes = {name: detector(game) for name, detector in DETECTORS.items()}
    return {
        "ok": True,
        "game_id": game_id,
        "margin": game.margin,
        "won": game.won,
        "turns": game.turns,
        "opponent": game.opponent_name,
        "train_events": len(game.train_events),
        "episodes": episodes,
    }


def sweep(game_ids: list[int], jobs: int = 8) -> dict:
    results = []
    if jobs == 1:
        for game_id in game_ids:
            results.append(_analyze_one_game(game_id))
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            for result in executor.map(_analyze_one_game, game_ids, chunksize=2):
                results.append(result)

    ok = [result for result in results if result["ok"]]
    failed = [result for result in results if not result["ok"]]
    ok.sort(key=lambda result: result["game_id"])

    games_meta = [
        {
            "game_id": result["game_id"],
            "margin": result["margin"],
            "won": result["won"],
            "turns": result["turns"],
            "opponent": result["opponent"],
            "train_events": result["train_events"],
        }
        for result in ok
    ]

    report = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only standing execution-waste sweep over the resident's own decoded arena "
            "replays; no arena writes, no strategy changes"
        ),
        "resident_agent_id": RESIDENT_AGENT_ID,
        "games_requested": len(game_ids),
        "games_decoded_ok": len(ok),
        "games_failed": len(failed),
        "failures": failed[:50],
        "games": games_meta,
        "detectors": {},
    }
    for name in DETECTORS:
        episodes_by_game = {result["game_id"]: result["episodes"][name] for result in ok}
        summary = summarize_detector(name, games_meta, episodes_by_game)
        if name == "late_train_window":
            summary["games_with_reference_bill"] = sum(1 for result in ok if result["train_events"] > 0)
        report["detectors"][name] = summary
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True, help="path to write the JSON sweep report")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 means every resident game in the corpus")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 16:
        parser.error("--jobs must be between 1 and 16")
    if args.limit < 0:
        parser.error("--limit cannot be negative")

    game_ids = resident_game_ids()
    if args.limit:
        game_ids = game_ids[: args.limit]
    if not game_ids:
        raise SystemExit("no resident games found in the corpus")

    report = sweep(game_ids, jobs=args.jobs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")

    print(f"resident games swept: {report['games_decoded_ok']}/{report['games_requested']}")
    if report["games_failed"]:
        print(f"decode failures: {report['games_failed']}")
    for name, summary in report["detectors"].items():
        print(
            f"  {name}: {summary['total_episodes']} episodes across "
            f"{summary['games_with_episode']}/{summary['games_swept']} games"
        )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
