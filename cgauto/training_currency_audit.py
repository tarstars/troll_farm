#!/usr/bin/env python3
"""B3.8 counterfactual training-currency audit.

Read-only diagnostic (backlog B3.8). Owner thesis test: production and consumption
should scale together (plant more, train more trolls to convert it), but every past
attempt to couple them failed, and D93/D160 suggest a specific mechanism -- TRAIN bills
are paid in PLUM/LEMON/APPLE/IRON, not WOOD, and the resident never accumulates a
worker-3 bill naturally (D160: zero affordability windows in 195/195 games). B3.5 found
the busy-unit planner never constructs a HARVEST candidate and every trained unit is
hardcoded ``harvest_power: 0`` -- so ripe, reachable fruit is routinely left uncollected
(2,163 ``harvest_slack`` episodes / ~536 pts gross, per the standing waste sweep).

This script asks the *funding* question directly: if the resident had banked all of that
uncollected-but-reachable fruit at the turn it became reachable (a pure stock-accounting
counterfactual -- no rerun of the game, no other behaviour changed), would a TRAIN bill
ever have become affordable, and how far short does even the full counterfactual haul
fall?

Reuses (does NOT re-derive replay parsing):

- ``cgauto.waste_sweep``: ``decode_game``/``build_decoded_game``/``resident_game_ids``
  for exact official per-turn state (BFS-door-distance/territory plumbing already
  computed in ``DecodedGame``), and its ``training_cost``/``training_pay_indices``/
  ``training_affordable``/``training_blocked`` -- an exact port of
  ``sim.engine.apply_train``'s cost formula (cross-checked directly against
  ``bot/main.py:training_cost`` and ``sim/engine.py:apply_train`` for this audit; see the
  methodology section of the accompanying report).
- ``cgauto.top_player_opening_analysis``: ``bfs`` (single-source BFS distance from a
  fruit cell, used for the "BFS distance <= 3 of one of our units" reachability test) and
  ``assigned_unit_commands``.
- The B3.5/D173a "chop-shadow" sub-classification rule (dominant own verb CHOP on the
  exact cell for >= 50% of the window) is reused verbatim from
  ``cgauto/analyze_d173a_harvest_before_chop.py:is_chop_shadow_shack2``, minus its own
  ``shack_distance <= 2`` gate, so it can be cross-tabulated against an independent
  own-door BFS-distance histogram (D173b's fix is scoped to shack distance <= 2; this
  audit measures how much near-camp value sits outside that scope).
- ``cgauto.analyze_d61p_field_snapshot.load_open_inputs`` (the frozen, QA-gated top-20
  open-game snapshot) plus ``cgauto.top_player_opening_analysis.analyze_players`` and
  ``cgauto.analyze_d95a_rank_one_scaler.reconstruct_actions``/``MATERIAL_VERBS`` for the
  top-5 funding-source contrast (step 5) -- the same machinery D95a/D101a use for
  ordinal-scoped material-action attribution.

Two distinct BFS distance concepts are used throughout and must not be confused:

1. "Reachable to a unit" (task's inclusion test, radius 3): per-turn BFS distance from
   the fruit CELL to the nearest OWN UNIT'S current position.
2. "Near camp" (spatial section, ``own_door_distance``): the static BFS distance from the
   fruit cell to the nearest cell in the resident's own door set -- ``DecodedGame.
   own_distance``, the exact same table ``analyze_d173a_harvest_before_chop.
   is_chop_shadow_shack2`` uses for its own ``shack_distance`` gate.

CLI usage::

    .venv/bin/python cgauto/training_currency_audit.py --output <path/to/report.json> \
        [--jobs 8] [--limit N] [--skip-top5]
"""

from __future__ import annotations

import argparse
import bisect
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import load_open_inputs, read_jsonl  # noqa: E402
from cgauto.analyze_d95a_rank_one_scaler import (  # noqa: E402
    MATERIAL_VERBS,
    reconstruct_actions,
)
from cgauto.analyze_d95a_rank_one_scaler import ratio as safe_ratio  # noqa: E402
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    analyze_players,
    assigned_unit_commands,
    bfs,
)
from cgauto.waste_sweep import (  # noqa: E402
    DecodedGame,
    build_decoded_game,
    decode_game,
    resident_game_ids,
    training_affordable,
    training_blocked,
    training_cost,
    training_pay_indices,
)

REPO = Path(__file__).resolve().parent.parent
SCRATCHPAD = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/"
    "b87b2a84-2e59-408b-9c9e-ecb58289a6d1/scratchpad"
)
DEFAULT_OUTPUT = SCRATCHPAD / "b38-training-currency-audit-result.json"
DEFAULT_TOP5_SNAPSHOT = REPO / "data/raw/snapshots/20260721T105508Z-d61p"

ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ITEM_INDEX = {name: index for index, name in enumerate(ITEMS)}
FRUIT_SPECIES = ("PLUM", "LEMON", "APPLE", "BANANA")
BILL_FRUIT_SPECIES = ("PLUM", "LEMON", "APPLE")  # the three fruit slots a TRAIN bill can charge
IRON_INDEX = ITEM_INDEX["IRON"]
UNREACHABLE = 10_000

# Owner-named bill vocabulary; talent order matches apply_train's own
# (movement_speed, carry_capacity, harvest_power, chop_power), and both keys/values are
# taken verbatim from d160a's frozen SPECS dict for direct comparability with the
# established "zero affordability windows in 195/195 games" baseline.
SPECS = {
    "cheap_helper_1101": (1, 1, 0, 1),
    "balanced_chopper_2202": (2, 2, 0, 2),
}
WORKER3_N = 2  # own-unit count immediately before training a 3rd worker (D160a's scope)

REACH_BFS_RADIUS = 3  # task step 1(b): "passed within BFS distance <= 3 of one of our units"

# Coordinator's spatial buckets (BFS distance from cell to the nearest own shack door).
DISTANCE_BUCKETS = [
    (0, 1, "0-1"),
    (2, 2, "2"),
    (3, 4, "3-4"),
    (5, 8, "5-8"),
    (9, None, "9+"),
]
NEAR_CAMP_MAX_DISTANCE = 2  # "near camp" = own_door_distance <= 2

CHOP_SHADOW_VERB_FRACTION = 0.5  # reused from analyze_d173a_harvest_before_chop
D173B_SHACK_DISTANCE = 2  # D173b/D173a's own trigger bound (matches NEAR_CAMP_MAX_DISTANCE)
DISPLACEMENT_TURN_BUDGET = 2  # coordinator's "~2 turns of displaced work" capture budget


# ---------------------------------------------------------------------------
# Step 1-2: per-game enumeration of uncollected-but-reachable ripe fruit
# ---------------------------------------------------------------------------


def bucket_for_distance(distance: int) -> str:
    for low, high, label in DISTANCE_BUCKETS:
        if distance >= low and (high is None or distance <= high):
            return label
    return "unknown"  # pragma: no cover -- buckets are exhaustive from 0 upward


def enumerate_fruit_events(game: DecodedGame) -> tuple[list[dict], dict]:
    """Every ripe fruit unit that was reachable to an own unit and never harvested by us.

    Walks the game's own already-decoded per-turn states once. For every plant cell,
    tracks the tree's whole lifetime (from first appearance -- turn 0 for a natural/
    map-start tree, or the turn a PLANT command creates it -- to death by CHOP or game
    end) as a FIFO queue of individual fruit-ripening events. Each turn, the queue grows
    by the plant's fruit-count delta (net of anyone's harvest that same turn -- HARVEST
    resolves before CHOP in the referee's own turn order, so a fruit can be picked the
    same turn its tree is chopped down) and shrinks by whatever WE or the OPPONENT
    harvest that turn (via exact own/opponent carry-delta attribution, not a re-derived
    harvest simulation). Entries we harvest are popped and discarded (never enter the
    audit, by construction of the game's income identity -- fruit can *only* enter a
    bank via HARVEST-then-DROP). Every other entry (opponent-harvested, destroyed when
    the tree was chopped with fruit still on it, or still on a live tree at game end) is
    "never harvested by us" per the task's inclusion test, and is INCLUDED here only if
    an own unit was ever within ``REACH_BFS_RADIUS`` BFS steps of the cell at some turn
    from the fruit's birth through its removal -- fruit that was never in reach at any
    point during its own existence is excluded (it was never a real "we failed to grab
    it" case). The earliest such turn is recorded as ``bankable_turn`` -- the turn the
    stock-accounting counterfactual in step 3 credits the deposit.
    """

    board = game.board
    walkable = board["walkable"]
    me, opp = game.me, game.opponent
    cell_distance_cache: dict[tuple[int, int], dict[tuple[int, int], int]] = {}
    reachable_turns_cache: dict[tuple[int, int], list[int]] = {}

    def dist_from_cell(cell: tuple[int, int]) -> dict[tuple[int, int], int]:
        cached = cell_distance_cache.get(cell)
        if cached is None:
            cached = bfs(walkable, [cell])
            cell_distance_cache[cell] = cached
        return cached

    own_positions = [
        [(unit["x"], unit["y"]) for unit in state["units"] if unit["player"] == me]
        for state in game.states
    ]

    def nearest_own_distance(cell: tuple[int, int], state_index: int) -> int:
        distances = dist_from_cell(cell)
        best = UNREACHABLE
        for pos in own_positions[state_index]:
            candidate = distances.get(pos, UNREACHABLE)
            if candidate < best:
                best = candidate
        return best

    def reachable_turns_for_cell(cell: tuple[int, int]) -> list[int]:
        cached = reachable_turns_cache.get(cell)
        if cached is None:
            cached = [
                t
                for t in range(0, game.turns + 1)
                if nearest_own_distance(cell, t) <= REACH_BFS_RADIUS
            ]
            reachable_turns_cache[cell] = cached
        return cached

    def first_bankable(cell: tuple[int, int], birth_turn: int, removal_turn: int) -> int | None:
        turns = reachable_turns_for_cell(cell)
        index = bisect.bisect_left(turns, birth_turn)
        if index < len(turns) and turns[index] <= removal_turn:
            return turns[index]
        return None

    def territory_of(cell: tuple[int, int]) -> str:
        own_d = game.own_distance.get(cell, UNREACHABLE)
        opp_d = game.opp_distance.get(cell, UNREACHABLE)
        return "own_or_unclaimed" if own_d <= opp_d else "opponent_territory"

    assigned_cache: dict[int, dict[int, str]] = {}

    def own_assigned(turn: int) -> dict[int, str]:
        cached = assigned_cache.get(turn)
        if cached is None:
            before_units = {
                unit["id"]: unit for unit in game.states[turn - 1]["units"] if unit["player"] == me
            }
            commands = action_commands(game.trajectory[turn - 1].get(f"commands{me}"))
            cached = assigned_unit_commands(commands, list(before_units.values()))
            assigned_cache[turn] = cached
        return cached

    def chop_dominant_fraction(cell: tuple[int, int], start_turn: int, end_turn: int) -> float:
        start_turn = max(start_turn, 1)
        end_turn = min(end_turn, game.turns)
        if end_turn < start_turn:
            return 0.0
        chop_turns = 0
        total = 0
        for turn in range(start_turn, end_turn + 1):
            before_units = {
                unit["id"]: unit for unit in game.states[turn - 1]["units"] if unit["player"] == me
            }
            assigned = own_assigned(turn)
            total += 1
            hit = any(
                (unit["x"], unit["y"]) == cell
                and assigned.get(unit_id, "WAIT").split()[0].upper() == "CHOP"
                for unit_id, unit in before_units.items()
            )
            chop_turns += int(hit)
        return chop_turns / total if total else 0.0

    events: list[dict] = []
    anomalies = 0

    def finalize(cell: tuple[int, int], species: str, entry: dict, removal_turn: int, fate: str) -> None:
        nonlocal anomalies
        bankable_turn = first_bankable(cell, entry["birth_turn"], removal_turn)
        if bankable_turn is None:
            return
        events.append(
            {
                "cell": list(cell),
                "species": species,
                "territory": territory_of(cell),
                "birth_turn": entry["birth_turn"],
                "bankable_turn": bankable_turn,
                "removal_turn": removal_turn,
                "fate": fate,
                "death_by": entry.get("death_by"),
                "own_door_distance": game.own_distance.get(cell, UNREACHABLE),
                "nearest_unit_distance_at_bankable": nearest_own_distance(cell, bankable_turn),
                "chop_dominant_fraction": chop_dominant_fraction(cell, bankable_turn, removal_turn),
            }
        )

    lifetimes: dict[tuple[int, int], dict] = {}
    for plant in game.states[0]["plants"]:
        cell = (plant["x"], plant["y"])
        life = {"species": plant["type"], "queue": []}
        for _ in range(int(plant["fruits"])):
            life["queue"].append({"birth_turn": 0})
        lifetimes[cell] = life

    for turn in range(1, game.turns + 1):
        before = game.states[turn - 1]
        after = game.states[turn]
        before_plants = {(plant["x"], plant["y"]): plant for plant in before["plants"]}
        after_plants = {(plant["x"], plant["y"]): plant for plant in after["plants"]}
        before_units_me = {unit["id"]: unit for unit in before["units"] if unit["player"] == me}
        before_units_opp = {unit["id"]: unit for unit in before["units"] if unit["player"] == opp}
        after_units_by_id = {unit["id"]: unit for unit in after["units"]}
        commands_me = action_commands(game.trajectory[turn - 1].get(f"commands{me}"))
        commands_opp = action_commands(game.trajectory[turn - 1].get(f"commands{opp}"))
        assigned_me = assigned_unit_commands(commands_me, list(before_units_me.values()))
        assigned_cache[turn] = assigned_me
        assigned_opp = assigned_unit_commands(commands_opp, list(before_units_opp.values()))

        harvested_us: dict[tuple[int, int], int] = defaultdict(int)
        harvested_opp: dict[tuple[int, int], int] = defaultdict(int)
        chopped_by_me: set[tuple[int, int]] = set()
        chopped_by_opp: set[tuple[int, int]] = set()

        for unit_id, unit in before_units_me.items():
            command = assigned_me.get(unit_id)
            if not command:
                continue
            verb = command.split()[0].upper()
            cell = (unit["x"], unit["y"])
            if verb == "CHOP":
                chopped_by_me.add(cell)
            elif verb == "HARVEST":
                plant = before_plants.get(cell)
                if plant is None or plant["fruits"] <= 0:
                    continue
                after_unit = after_units_by_id.get(unit_id)
                if after_unit is None:
                    continue
                idx = ITEM_INDEX[plant["type"]]
                gained = after_unit["carry"][idx] - unit["carry"][idx]
                if gained > 0:
                    harvested_us[cell] += gained

        for unit_id, unit in before_units_opp.items():
            command = assigned_opp.get(unit_id)
            if not command:
                continue
            verb = command.split()[0].upper()
            cell = (unit["x"], unit["y"])
            if verb == "CHOP":
                chopped_by_opp.add(cell)
            elif verb == "HARVEST":
                plant = before_plants.get(cell)
                if plant is None or plant["fruits"] <= 0:
                    continue
                after_unit = after_units_by_id.get(unit_id)
                if after_unit is None:
                    continue
                idx = ITEM_INDEX[plant["type"]]
                gained = after_unit["carry"][idx] - unit["carry"][idx]
                if gained > 0:
                    harvested_opp[cell] += gained

        for cell, plant in after_plants.items():
            if cell not in lifetimes:
                lifetimes[cell] = {"species": plant["type"], "queue": []}

        for cell, life in list(lifetimes.items()):
            fruits_before = before_plants.get(cell, {}).get("fruits", 0)
            h_us = harvested_us.get(cell, 0)
            h_opp = harvested_opp.get(cell, 0)
            still_present = cell in after_plants
            if still_present:
                fruits_after = after_plants[cell]["fruits"]
                growth = fruits_after - fruits_before + h_us + h_opp
                if growth < 0:
                    anomalies += 1
                    growth = 0
                elif growth > 1:
                    anomalies += 1
                    growth = 1
                for _ in range(growth):
                    life["queue"].append({"birth_turn": turn})
            for _ in range(h_us):
                if life["queue"]:
                    life["queue"].pop(0)
            for _ in range(h_opp):
                if life["queue"]:
                    entry = life["queue"].pop(0)
                    finalize(cell, life["species"], entry, turn, "opponent")
            if not still_present:
                death_by = (
                    "us"
                    if cell in chopped_by_me
                    else "opponent"
                    if cell in chopped_by_opp
                    else "unknown"
                )
                for entry in life["queue"]:
                    entry["death_by"] = death_by
                    finalize(cell, life["species"], entry, turn, "destroyed_by_chop")
                del lifetimes[cell]

    for cell, life in lifetimes.items():
        for entry in life["queue"]:
            finalize(cell, life["species"], entry, game.turns, "alive_at_game_end")

    return events, {"growth_anomalies": anomalies}


# ---------------------------------------------------------------------------
# Step 3-4: counterfactual TRAIN-bill affordability windows
# ---------------------------------------------------------------------------


def deposit_schedule(events: list[dict]) -> dict[int, list[int]]:
    schedule: dict[int, list[int]] = defaultdict(lambda: [0] * 6)
    for event in events:
        idx = ITEM_INDEX[event["species"]]
        schedule[event["bankable_turn"]][idx] += 1
    return schedule


def augmented_bank_series(game: DecodedGame, schedule: dict[int, list[int]]) -> list[list[int]]:
    cumulative = [0] * 6
    series = []
    for t in range(0, game.turns + 1):
        deltas = schedule.get(t)
        if deltas is not None:
            cumulative = [cumulative[i] + deltas[i] for i in range(6)]
        real = game.states[t]["inventories"][game.me]
        series.append([real[i] + cumulative[i] for i in range(6)])
    return series


def worker3_windows(game: DecodedGame, bank_series: list[list[int]], talents: tuple[int, int, int, int]) -> dict:
    stock_windows = []
    executable_windows = []
    for t in range(1, game.turns + 1):
        own_units_before = [unit for unit in game.states[t - 1]["units"] if unit["player"] == game.me]
        if len(own_units_before) != WORKER3_N:
            continue
        bank = bank_series[t - 1]
        if training_affordable(WORKER3_N, talents, bank, game.iron_present):
            stock_windows.append(t)
            if not training_blocked(own_units_before, game.own_shack):
                executable_windows.append(t)
    return {
        "stock_windows": stock_windows,
        "executable_windows": executable_windows,
        "first_stock_window_turn": stock_windows[0] if stock_windows else None,
        "window_count": len(stock_windows),
    }


def closest_approach(game: DecodedGame, bank_series: list[list[int]], talents: tuple[int, int, int, int]) -> dict | None:
    cost = training_cost(WORKER3_N, talents)
    pay = training_pay_indices(game.iron_present)
    best = None
    for t in range(1, game.turns + 1):
        own_units_before = [unit for unit in game.states[t - 1]["units"] if unit["player"] == game.me]
        if len(own_units_before) != WORKER3_N:
            continue
        bank = bank_series[t - 1]
        deficit = [max(0, cost[i] - bank[i]) for i in range(6)]
        total_deficit = sum(deficit[i] for i in pay)
        if best is None or total_deficit < best["total_deficit"]:
            best = {"turn": t, "total_deficit": total_deficit, "deficit": deficit}
    if best is None:
        return None
    limiting = [ITEMS[i] for i in pay if best["deficit"][i] > 0]
    return {
        "turn": best["turn"],
        "total_deficit": best["total_deficit"],
        "deficit": best["deficit"],
        "limiting_resources": limiting,
    }


SCENARIOS = ("baseline_real_bank_only", "own_or_unclaimed_only", "own_plus_opponent")


def scenario_events(all_events: list[dict], scenario: str) -> list[dict]:
    if scenario == "baseline_real_bank_only":
        return []
    if scenario == "own_or_unclaimed_only":
        return [event for event in all_events if event["territory"] == "own_or_unclaimed"]
    return list(all_events)  # own_plus_opponent


# ---------------------------------------------------------------------------
# Per-game driver (also used as the multiprocessing worker)
# ---------------------------------------------------------------------------


def analyze_one_game(game_id: int) -> dict:
    try:
        game = decode_game(game_id)
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit
        return {"ok": False, "game_id": game_id, "error": f"{type(exc).__name__}: {exc}"}

    events, diagnostics = enumerate_fruit_events(game)

    windows: dict[str, dict] = {}
    for scenario in SCENARIOS:
        subset = scenario_events(events, scenario)
        bank_series = augmented_bank_series(game, deposit_schedule(subset))
        per_spec = {}
        for spec_name, talents in SPECS.items():
            report = worker3_windows(game, bank_series, talents)
            report["closest_approach"] = closest_approach(game, bank_series, talents)
            per_spec[spec_name] = report
        windows[scenario] = per_spec

    return {
        "ok": True,
        "game_id": game_id,
        "margin": game.margin,
        "won": game.won,
        "turns": game.turns,
        "iron_present": game.iron_present,
        "opponent": game.opponent_name,
        "diagnostics": diagnostics,
        "events": events,
        "windows": windows,
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def mean(values) -> float | None:
    selected = list(values)
    return statistics.fmean(selected) if selected else None


def median(values) -> float | None:
    selected = list(values)
    return statistics.median(selected) if selected else None


def species_haul_summary(pooled_events: list[dict]) -> dict:
    by_species = Counter(event["species"] for event in pooled_events)
    by_fate = Counter(event["fate"] for event in pooled_events)
    death_by = Counter(
        event["death_by"] for event in pooled_events if event["fate"] == "destroyed_by_chop"
    )
    bill_relevant = sum(count for species, count in by_species.items() if species in BILL_FRUIT_SPECIES)
    return {
        "total_events": len(pooled_events),
        "by_species": dict(sorted(by_species.items())),
        "bill_relevant_events_plum_lemon_apple": bill_relevant,
        "banana_events_never_bill_relevant": by_species.get("BANANA", 0),
        "by_fate": dict(sorted(by_fate.items())),
        "chop_deaths_by_who": dict(sorted(death_by.items())),
    }


def window_summary(per_game_results: list[dict], scenario: str, spec_name: str, iron_only: bool | None = None) -> dict:
    rows = per_game_results
    if iron_only is not None:
        rows = [row for row in rows if row["iron_present"] == iron_only]
    entries = [row["windows"][scenario][spec_name] for row in rows]
    games_with_window = [entry for entry in entries if entry["window_count"] > 0]
    first_turns = [entry["first_stock_window_turn"] for entry in games_with_window]
    window_counts = [entry["window_count"] for entry in games_with_window]
    zero_window_rows = [
        (row, entry)
        for row, entry in zip(rows, entries)
        if entry["window_count"] == 0 and entry["closest_approach"] is not None
    ]
    limiting_at_closest = Counter()
    for _row, entry in zero_window_rows:
        for resource in entry["closest_approach"]["limiting_resources"]:
            limiting_at_closest[resource] += 1
    deficits = [entry["closest_approach"]["total_deficit"] for _row, entry in zero_window_rows]
    iron_still_limiting_with_iron_present = sum(
        1
        for row, entry in zero_window_rows
        if row["iron_present"] and "IRON" in entry["closest_approach"]["limiting_resources"]
    )
    return {
        "games": len(entries),
        "games_with_at_least_one_window": len(games_with_window),
        "pct_games_with_window": safe_ratio(len(games_with_window), len(entries)),
        "first_window_turn": {
            "median": median(first_turns),
            "mean": mean(first_turns),
            "min": min(first_turns) if first_turns else None,
            "max": max(first_turns) if first_turns else None,
        },
        "windows_per_game_given_at_least_one": {
            "median": median(window_counts),
            "mean": mean(window_counts),
            "max": max(window_counts) if window_counts else None,
        },
        "zero_window_games": len(zero_window_rows),
        "zero_window_closest_deficit": {
            "median": median(deficits),
            "min": min(deficits) if deficits else None,
            "max": max(deficits) if deficits else None,
        },
        "zero_window_limiting_resource_game_counts": dict(sorted(limiting_at_closest.items())),
        "zero_window_games_still_iron_short_on_iron_maps": iron_still_limiting_with_iron_present,
    }


def spatial_summary(pooled_events: list[dict]) -> dict:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for event in pooled_events:
        label = bucket_for_distance(event["own_door_distance"])
        buckets[label].append(event)

    bucket_rows = []
    for _low, _high, label in DISTANCE_BUCKETS:
        rows = buckets.get(label, [])
        chop_shadow = [row for row in rows if row["chop_dominant_fraction"] >= CHOP_SHADOW_VERB_FRACTION]
        non_chop_shadow = [row for row in rows if row["chop_dominant_fraction"] < CHOP_SHADOW_VERB_FRACTION]
        bill_relevant = sum(1 for row in rows if row["species"] in BILL_FRUIT_SPECIES)
        bucket_rows.append(
            {
                "bucket": label,
                "events": len(rows),
                "points_all_species": len(rows),
                "training_currency_units_plum_lemon_apple": bill_relevant,
                "by_species": dict(sorted(Counter(row["species"] for row in rows).items())),
                "chop_shadow_events": len(chop_shadow),
                "chop_shadow_points": len(chop_shadow),
                "non_chop_shadow_events": len(non_chop_shadow),
                "non_chop_shadow_points": len(non_chop_shadow),
            }
        )

    near_camp_rows = [row for row in pooled_events if row["own_door_distance"] <= NEAR_CAMP_MAX_DISTANCE]
    near_camp_chop_shadow = [row for row in near_camp_rows if row["chop_dominant_fraction"] >= CHOP_SHADOW_VERB_FRACTION]
    near_camp_non_chop_shadow = [
        row for row in near_camp_rows if row["chop_dominant_fraction"] < CHOP_SHADOW_VERB_FRACTION
    ]
    # D173b's own scope is chop-shadow AND own_door_distance<=2 -- by construction every
    # near_camp_chop_shadow row is inside D173b's trigger geometry; every
    # near_camp_non_chop_shadow row is near-camp value D173b's fix cannot touch even if
    # it worked perfectly (transit-passthrough-near-camp, per the coordinator's hypothesis).
    pure_detour = [
        row["nearest_unit_distance_at_bankable"] + row["own_door_distance"] for row in near_camp_rows
    ]
    realistically_capturable = [
        row for row, detour in zip(near_camp_rows, pure_detour) if detour <= DISPLACEMENT_TURN_BUDGET
    ]
    detour_histogram = Counter(pure_detour)

    return {
        "distance_buckets": bucket_rows,
        "near_camp_distance_le_2": {
            "events": len(near_camp_rows),
            "points": len(near_camp_rows),
            "training_currency_units_plum_lemon_apple": sum(
                1 for row in near_camp_rows if row["species"] in BILL_FRUIT_SPECIES
            ),
            "chop_shadow_events": len(near_camp_chop_shadow),
            "chop_shadow_points": len(near_camp_chop_shadow),
            "chop_shadow_pct_of_near_camp": safe_ratio(len(near_camp_chop_shadow), len(near_camp_rows)),
            "non_chop_shadow_events_outside_d173b_scope": len(near_camp_non_chop_shadow),
            "non_chop_shadow_points_outside_d173b_scope": len(near_camp_non_chop_shadow),
            "non_chop_shadow_pct_outside_d173b_scope": safe_ratio(
                len(near_camp_non_chop_shadow), len(near_camp_rows)
            ),
            "pure_detour_turns_definition": (
                "BFS(unit_at_bankable_turn -> cell) + BFS(cell -> nearest own door); "
                "excludes the two mandatory HARVEST+DROP action turns themselves, which "
                "would need to happen in some form regardless -- this isolates the "
                "avoidable walking detour"
            ),
            "pure_detour_turns_histogram": dict(sorted(detour_histogram.items())),
            "realistically_capturable_le_2_turn_detour": {
                "events": len(realistically_capturable),
                "points": len(realistically_capturable),
                "pct_of_near_camp": safe_ratio(len(realistically_capturable), len(near_camp_rows)),
                "training_currency_units_plum_lemon_apple": sum(
                    1 for row in realistically_capturable if row["species"] in BILL_FRUIT_SPECIES
                ),
            },
        },
    }


# ---------------------------------------------------------------------------
# Step 5: top-5 cohort funding-source contrast
# ---------------------------------------------------------------------------


def load_top5_occurrences(snapshot_path: Path) -> tuple[list[tuple[dict, int, dict]], dict]:
    inputs = load_open_inputs(snapshot_path)
    players = json.loads((snapshot_path.resolve() / "players.json").read_text())
    top5 = {int(row["agent_id"]): row for row in players if int(row.get("source_rank", 999)) <= 5}
    occurrences = []
    for task in inputs["tasks"]:
        present = {int(row.get("agentId", -1)) for row in task["game"]["players"]}
        for agent_id in sorted(set(task.get("top_source_ids", [])) & present & set(top5)):
            occurrences.append((task, agent_id, top5[agent_id]))
    return occurrences, {"snapshot": str(snapshot_path), "top5_agents": {str(k): v["pseudo"] for k, v in top5.items()}}


def analyze_top5_occurrence(occurrence: tuple[dict, int, dict]) -> dict:
    task, agent_id, meta = occurrence
    game_id = None
    try:
        raw = json.loads(Path(task["raw_path"]).read_text())
        game_id = int(raw.get("gameId"))
        trajectory = read_jsonl(Path(task["trajectory_path"]))
        decoded_map, states, unknown = decoded_states(raw, trajectory)
        agents = raw.get("agents") or []
        seat = next(
            index for index in (0, 1) if index < len(agents) and int((agents[index] or {}).get("agentId", -1)) == agent_id
        )
        game = build_decoded_game(
            game_id=game_id,
            me=seat,
            map_rows=decoded_map["rows"],
            states=states,
            trajectory=trajectory,
            scores=raw["scores"],
            ranks=raw.get("ranks") or [],
            opponent_name="?",
        )
        # Provenance, not just bill composition: the real referee grants both players an
        # identical, map-seeded nonzero starting inventory (verified empirically -- e.g.
        # resident game 896347357 starts both seats at [7,10,4,3,4,0]; the *local offline*
        # simulator's ``sim/state.py:from_ascii`` zero default is a synthetic-test
        # convenience, not what happens in real arena games). PLUM/LEMON/APPLE can only
        # ever be replenished by HARVEST and IRON only by MINE (apply_train is the only
        # sink for these four slots; nothing else destroys banked stock) -- so any bill
        # currency beyond the still-unspent starting endowment must be earned income.
        # FIFO convention: each bill draws down the still-unspent starting endowment
        # first, before being attributed to earned (harvested/mined) income.
        starting_bank = [int(value) for value in states[0]["inventories"][seat]]
        remaining_starting = list(starting_bank)
        bill_rows = []
        for event in game.train_events:
            cost = training_cost(event["n_before"], event["talents"])
            pay = training_pay_indices(game.iron_present)
            fruit_cost = sum(cost[i] for i in pay if i in (0, 1, 2))
            iron_cost = cost[IRON_INDEX] if IRON_INDEX in pay else 0
            from_starting = {}
            from_earned = {}
            for i in pay:
                take = min(cost[i], max(0, remaining_starting[i]))
                remaining_starting[i] -= take
                from_starting[ITEMS[i]] = take
                from_earned[ITEMS[i]] = cost[i] - take
            starting_fruit = sum(from_starting.get(name, 0) for name in BILL_FRUIT_SPECIES)
            starting_iron = from_starting.get("IRON", 0)
            bill_rows.append(
                {
                    "turn": event["turn"],
                    "talents": list(event["talents"]),
                    "n_before": event["n_before"],
                    "fruit_cost": fruit_cost,
                    "iron_cost": iron_cost,
                    "total_cost": fruit_cost + iron_cost,
                    "from_starting_endowment": {"fruit": starting_fruit, "iron": starting_iron},
                    "from_earned_income": {
                        "fruit": fruit_cost - starting_fruit,
                        "iron": iron_cost - starting_iron,
                    },
                }
            )
        starting_bank_nonzero = any(value != 0 for value in starting_bank)

        analyses = analyze_players(states, trajectory)
        analysis = analyses[seat]
        worker_ordinals = {int(worker["unit_id"]): int(worker["ordinal"]) for worker in analysis["workers"]}
        recon_events, _lineage, _quality = reconstruct_actions(states, trajectory, seat, worker_ordinals)
        later_events = [event for event in recon_events if event["ordinal"] >= 2]
        later_successes = Counter(
            event["verb"] for event in later_events if event["success"] and event["verb"] in MATERIAL_VERBS
        )
        later_total = sum(later_successes.values())
        chop_drop_share = safe_ratio(later_successes["CHOP"] + later_successes["DROP"], later_total)

        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": agent_id,
            "agent": meta.get("pseudo"),
            "source_rank": meta.get("source_rank"),
            "seat": seat,
            "iron_present": game.iron_present,
            "starting_bank": starting_bank,
            "starting_bank_nonzero": starting_bank_nonzero,
            "final_workers": sum(1 for unit in states[-1]["units"] if unit["player"] == seat),
            "train_events": bill_rows,
            "later_worker_material_actions": dict(sorted(later_successes.items())),
            "later_worker_material_action_count": later_total,
            "later_worker_chop_drop_share": chop_drop_share,
        }
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit
        return {"ok": False, "game_id": game_id, "agent_id": agent_id, "error": f"{type(exc).__name__}: {exc}"}


def top5_summary(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row["ok"]]
    total_starting_fruit = 0
    total_starting_iron = 0
    total_earned_fruit = 0
    total_earned_iron = 0
    per_bill_earned_share = []
    games_any_starting_bank = 0
    chop_drop_shares = []
    for row in ok_rows:
        if row["starting_bank_nonzero"]:
            games_any_starting_bank += 1
        for bill in row["train_events"]:
            total_starting_fruit += bill["from_starting_endowment"]["fruit"]
            total_starting_iron += bill["from_starting_endowment"]["iron"]
            total_earned_fruit += bill["from_earned_income"]["fruit"]
            total_earned_iron += bill["from_earned_income"]["iron"]
            if bill["total_cost"] > 0:
                earned_total = bill["from_earned_income"]["fruit"] + bill["from_earned_income"]["iron"]
                per_bill_earned_share.append(earned_total / bill["total_cost"])
        if row["later_worker_chop_drop_share"] is not None:
            chop_drop_shares.append(row["later_worker_chop_drop_share"])
    grand_total = total_starting_fruit + total_starting_iron + total_earned_fruit + total_earned_iron
    return {
        "games_analyzed": len(ok_rows),
        "games_failed": len(rows) - len(ok_rows),
        "games_any_nonzero_starting_bank": games_any_starting_bank,
        "total_train_events": sum(len(row["train_events"]) for row in ok_rows),
        "provenance_note": (
            "FIFO convention: each bill draws down the still-unspent map-seeded starting "
            "endowment first; only currency beyond that is attributed to earned "
            "(harvested/mined) income. PLUM/LEMON/APPLE can only ever be replenished by "
            "HARVEST and IRON only by MINE (apply_train is the only sink for these four "
            "bank slots), so this FIFO split is exact for 'starting vs not', and the "
            "earned total is unambiguously fruit-vs-iron by construction."
        ),
        "pooled_bill_currency_provenance": {
            "starting_endowment_fruit": total_starting_fruit,
            "starting_endowment_iron": total_starting_iron,
            "earned_harvest_fruit": total_earned_fruit,
            "earned_mine_iron": total_earned_iron,
            "starting_endowment_share_of_total": safe_ratio(
                total_starting_fruit + total_starting_iron, grand_total
            ),
            "earned_share_of_total": safe_ratio(total_earned_fruit + total_earned_iron, grand_total),
            "of_earned_only_fruit_share": safe_ratio(
                total_earned_fruit, total_earned_fruit + total_earned_iron
            ),
            "of_earned_only_iron_share": safe_ratio(
                total_earned_iron, total_earned_fruit + total_earned_iron
            ),
        },
        "per_bill_earned_share": {
            "median": median(per_bill_earned_share),
            "mean": mean(per_bill_earned_share),
        },
        "later_worker_chop_drop_share": {
            "median": median(chop_drop_shares),
            "mean": mean(chop_drop_shares),
            "games_with_later_workers": len(chop_drop_shares),
            "d95_reference_value": 0.9387,
        },
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------


def run_main_audit(game_ids: list[int], jobs: int) -> list[dict]:
    if jobs == 1:
        return [analyze_one_game(game_id) for game_id in game_ids]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(analyze_one_game, game_ids, chunksize=2))


def build_report(per_game_results: list[dict], top5_rows: list[dict] | None, top5_meta: dict | None) -> dict:
    ok = [row for row in per_game_results if row["ok"]]
    failed = [row for row in per_game_results if not row["ok"]]
    ok.sort(key=lambda row: row["game_id"])

    all_events = [event for row in ok for event in row["events"]]
    own_events = [event for event in all_events if event["territory"] == "own_or_unclaimed"]
    opp_events = [event for event in all_events if event["territory"] == "opponent_territory"]

    windows_block = {
        scenario: {spec_name: window_summary(ok, scenario, spec_name) for spec_name in SPECS}
        for scenario in SCENARIOS
    }
    windows_by_iron_presence = {
        scenario: {
            spec_name: {
                "iron_present_maps": window_summary(ok, scenario, spec_name, iron_only=True),
                "iron_absent_maps": window_summary(ok, scenario, spec_name, iron_only=False),
            }
            for spec_name in SPECS
        }
        for scenario in SCENARIOS
    }
    games_meta = [
        {
            "game_id": row["game_id"],
            "margin": row["margin"],
            "won": row["won"],
            "turns": row["turns"],
            "iron_present": row["iron_present"],
            "opponent": row["opponent"],
            "own_or_unclaimed_events": sum(
                1 for event in row["events"] if event["territory"] == "own_or_unclaimed"
            ),
            "opponent_territory_events": sum(
                1 for event in row["events"] if event["territory"] == "opponent_territory"
            ),
            "first_window_turn": {
                scenario: {spec_name: row["windows"][scenario][spec_name]["first_stock_window_turn"] for spec_name in SPECS}
                for scenario in SCENARIOS
            },
        }
        for row in ok
    ]

    report = {
        "schema": "troll-farm-b38-training-currency-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only stock-accounting counterfactual over the resident's own decoded "
            "arena replays; no arena writes, no strategy changes, no rerun of any game"
        ),
        "caveat": (
            "UPPER BOUND, not a causal simulation: this counterfactual banks fruit at the "
            "turn it was reachable with no other change to behaviour -- it ignores that "
            "harvesting and banking cost real turns and would change the trajectory "
            "(unit positions, opponent responses, later fruit availability) in ways this "
            "script does not model."
        ),
        "games_requested": len(per_game_results),
        "games_decoded_ok": len(ok),
        "games_failed": len(failed),
        "failures": failed[:50],
        "bill_specs": {name: list(talents) for name, talents in SPECS.items()},
        "worker3_n": WORKER3_N,
        "reach_bfs_radius": REACH_BFS_RADIUS,
        "growth_anomalies_total": sum(row["diagnostics"]["growth_anomalies"] for row in ok),
        "uncollected_haul": {
            "own_or_unclaimed": species_haul_summary(own_events),
            "opponent_territory_increment": species_haul_summary(opp_events),
            "combined": species_haul_summary(all_events),
        },
        "iron_present_games": sum(1 for row in ok if row["iron_present"]),
        "iron_absent_games": sum(1 for row in ok if not row["iron_present"]),
        "windows": windows_block,
        "windows_by_iron_presence": windows_by_iron_presence,
        "spatial": spatial_summary(own_events),
        "spatial_including_opponent_territory": spatial_summary(all_events),
        "games": games_meta,
    }
    if top5_rows is not None:
        report["top5_funding_contrast"] = {"meta": top5_meta, **top5_summary(top5_rows)}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 means every resident game in the corpus")
    parser.add_argument("--skip-top5", action="store_true", help="skip the step-5 top-cohort funding contrast")
    parser.add_argument("--top5-snapshot", type=Path, default=DEFAULT_TOP5_SNAPSHOT)
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

    per_game_results = run_main_audit(game_ids, jobs=args.jobs)

    top5_rows = None
    top5_meta = None
    if not args.skip_top5:
        occurrences, top5_meta = load_top5_occurrences(args.top5_snapshot)
        if args.jobs == 1:
            top5_rows = [analyze_top5_occurrence(occurrence) for occurrence in occurrences]
        else:
            with ProcessPoolExecutor(max_workers=args.jobs) as executor:
                top5_rows = list(executor.map(analyze_top5_occurrence, occurrences, chunksize=2))

    report = build_report(per_game_results, top5_rows, top5_meta)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")

    print(f"resident games decoded: {report['games_decoded_ok']}/{report['games_requested']}")
    if report["games_failed"]:
        print(f"decode failures: {report['games_failed']}")
    print(f"growth anomalies (should be 0): {report['growth_anomalies_total']}")
    for scope in ("own_or_unclaimed", "combined"):
        haul = report["uncollected_haul"][scope]
        print(f"  haul[{scope}] total_events={haul['total_events']} by_species={haul['by_species']}")
    for scenario in SCENARIOS:
        for spec_name in SPECS:
            summary = report["windows"][scenario][spec_name]
            print(
                f"  windows[{scenario}][{spec_name}]: "
                f"{summary['games_with_at_least_one_window']}/{summary['games']} games "
                f"({summary['pct_games_with_window']:.1%}), "
                f"median first turn={summary['first_window_turn']['median']}"
            )
    if top5_rows is not None:
        split = report["top5_funding_contrast"]["pooled_bill_currency_provenance"]
        print(
            f"  top5 bill provenance: starting_endowment_share={split['starting_endowment_share_of_total']:.3f} "
            f"earned_share={split['earned_share_of_total']:.3f} "
            f"(of earned: fruit={split['of_earned_only_fruit_share']:.3f} "
            f"iron={split['of_earned_only_iron_share']:.3f}) "
            f"(games={report['top5_funding_contrast']['games_analyzed']})"
        )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
