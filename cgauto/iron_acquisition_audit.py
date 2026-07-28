#!/usr/bin/env python3
"""B3.9 -- IRON acquisition audit and combined affordability counterfactual.

Read-only diagnostic (backlog B3.9, the vein B3.8 opened). B3.8 (report:
``/tmp/.../scratchpad/b38-training-currency-audit-report.md``, script
``cgauto/training_currency_audit.py``) established that crediting every uncollected
reachable *fruit* (ours + opponent's) opens a cheap-helper ``(1,1,0,1)`` TRAIN-bill
affordability window in only ~10% of games and the balanced chopper ``(2,2,0,2)`` in
0/205 games -- because IRON limits 97.3-100% of the remaining failures, and IRON only
ever enters the bank via MINE, never HARVEST. This script asks the mining side of the
same question directly: how much do we actually mine, how much reachable iron did we
leave unmined, why (source-level root cause), and -- the decisive number -- does
crediting BOTH the fruit slack and the iron slack ever open a window B3.8's fruit-only
counterfactual could not?

Reuses (does NOT re-derive replay parsing or the counterfactual-window machinery):

- ``cgauto.waste_sweep``: ``decode_game``/``resident_game_ids``/``DecodedGame`` for
  exact official per-turn state + BFS door geometry; ``iter_turn_frames`` for per-turn
  command attribution; ``RunTracker`` for maximal-run episode tracking (the same class
  every one of waste_sweep's six standing detectors uses); ``command_precondition_met``
  for the exact, already-established MINE rules precondition (``chop>0 and free>0 and
  adjacent`` -- the same rule ``detect_repeated_failed_command`` relies on); ``training_
  cost``/``training_pay_indices`` for the exact ``apply_train`` cost port.
- ``cgauto.top_player_opening_analysis``: ``bfs``/``adjacent`` for map BFS geometry and
  ``analyze_players`` for per-worker ordinal/role/spec/spawn-turn/mined-IRON bookkeeping
  (already computes a per-worker ``mined`` item vector and a ``commands`` verb-count
  Counter -- reused directly rather than re-deriving worker identity tracking).
- ``cgauto.analyze_d95a_rank_one_scaler``: ``reconstruct_actions`` for turn-level,
  ordinal-tagged, success-classified MINE events (the same machinery D95a/D101a/B3.8 use
  for material-action attribution) and ``ratio`` for None-safe percentages.
- ``cgauto.training_currency_audit`` (B3.8, STANDING, REUSED VERBATIM for the
  counterfactual core): ``enumerate_fruit_events``/``deposit_schedule``/
  ``augmented_bank_series``/``worker3_windows``/``closest_approach``/``scenario_events``/
  ``SPECS``/``WORKER3_N``/``window_summary``/``load_top5_occurrences``/
  ``analyze_top5_occurrence``/``DEFAULT_TOP5_SNAPSHOT``/``mean``/``median``. This script
  adds an iron deposit schedule (see ``iron_deposit_schedule``) and merges it with B3.8's
  own fruit deposit schedule (see ``merge_schedules``) before calling B3.8's *unmodified*
  ``augmented_bank_series``/``worker3_windows``/``closest_approach``/``window_summary`` --
  the bill-cost/window logic itself is never re-implemented, only its credit input is
  extended, so the fruit-only sub-case of every combined run must (and does, see the
  report's methodology section) exactly reproduce B3.8's own published numbers.
- ``cgauto.analyze_d61p_field_snapshot``: ``load_open_inputs``/``read_jsonl`` for the
  frozen, QA-gated top-5 open-game snapshot (identical to B3.8's step-5 sample).
- ``cgauto.recent_resident_field_census``: ``decoded_states`` for top-5 occurrence
  decoding (identical to B3.8's own top-5 loading path).

No replay-parsing or counterfactual-window logic is re-derived; only new mining-specific
aggregation (opportunity geometry, reachability episodes, iron deposit scheduling) is
written.

CLI usage::

    .venv/bin/python cgauto/iron_acquisition_audit.py --output <path/to/report.json> \
        [--jobs 8] [--limit N] [--skip-top5]
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import load_open_inputs, read_jsonl  # noqa: E402
from cgauto.analyze_d95a_rank_one_scaler import reconstruct_actions  # noqa: E402
from cgauto.analyze_d95a_rank_one_scaler import ratio as safe_ratio  # noqa: E402
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.top_player_opening_analysis import adjacent, analyze_players, bfs  # noqa: E402
from cgauto.training_currency_audit import (  # noqa: E402
    DEFAULT_TOP5_SNAPSHOT,
    SPECS,
    analyze_top5_occurrence,
    augmented_bank_series,
    closest_approach,
    deposit_schedule,
    enumerate_fruit_events,
    load_top5_occurrences,
    mean,
    median,
    scenario_events,
    window_summary,
    worker3_windows,
)
from cgauto.waste_sweep import (  # noqa: E402
    DecodedGame,
    RunTracker,
    UNREACHABLE,
    build_decoded_game,
    command_precondition_met,
    decode_game,
    iter_turn_frames,
    resident_game_ids,
    training_cost,
    training_pay_indices,
)

REPO = Path(__file__).resolve().parent.parent
SCRATCHPAD = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/"
    "b87b2a84-2e59-408b-9c9e-ecb58289a6d1/scratchpad"
)
DEFAULT_OUTPUT = SCRATCHPAD / "b39-iron-acquisition-audit-result.json"

ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ITEM_INDEX = {name: index for index, name in enumerate(ITEMS)}
IRON_INDEX = ITEM_INDEX["IRON"]

IRON_REACH_BFS_RADIUS = 3  # task spec: "BFS distance <= 3 of an iron source"
MAX_EXAMPLES_PER_GAME = 5


# ---------------------------------------------------------------------------
# Shared per-game helpers
# ---------------------------------------------------------------------------


def own_states_by_turn(game: DecodedGame) -> list[list[dict]]:
    """``own_by_turn[t]`` = this player's own unit dicts at state index ``t`` (0..turns)."""

    return [[unit for unit in state["units"] if unit["player"] == game.me] for state in game.states]


def worker_ordinals_for(game: DecodedGame) -> tuple[dict[int, int], dict]:
    """Per-worker ordinal/role/spec/spawn-turn/mined-IRON bookkeeping, reused verbatim
    from ``top_player_opening_analysis.analyze_players`` (ordinal 0 = starter, 1 = first
    trained worker, 2 = second trained worker, ...)."""

    analysis = analyze_players(game.states, game.trajectory)[game.me]
    ordinals = {int(worker["unit_id"]): int(worker["ordinal"]) for worker in analysis["workers"]}
    return ordinals, analysis


# ---------------------------------------------------------------------------
# Task step 1: our mining behaviour, measured
# ---------------------------------------------------------------------------


def mining_behavior_for_game(game: DecodedGame) -> dict:
    """Every MINE action we issued (turn, unit, ordinal, own-unit-count-before, success,
    IRON gained), plus the game's own IRON bank/carry/spend time series, cross-checked
    by an internal conservation identity (mined == bank + carried + spent at every
    turn, since IRON only ever enters via MINE and only ever leaves via a TRAIN bill --
    ``apply_mine``/``apply_train`` are the only two IRON-touching effects in the whole
    referee, per ``sim/engine.py`` and B3.8's own cross-checked cost-formula reading).
    """

    ordinals, analysis = worker_ordinals_for(game)
    action_events, _lineage, _quality = reconstruct_actions(game.states, game.trajectory, game.me, ordinals)

    mine_events = []
    for event in action_events:
        if event["verb"] != "MINE":
            continue
        before_units = {
            unit["id"]: unit for unit in game.states[event["turn"] - 1]["units"] if unit["player"] == game.me
        }
        unit = before_units.get(event["unit_id"])
        mine_events.append(
            {
                "turn": event["turn"],
                "unit_id": event["unit_id"],
                "ordinal": event["ordinal"],
                "workforce_before": event["workforce"],
                "success": event["success"],
                "iron_gained": event["gained"].get("IRON", 0),
                "pos": [unit["x"], unit["y"]] if unit else None,
                "chop": unit["chop"] if unit else None,
                "free_before": (unit["cc"] - sum(unit["carry"])) if unit else None,
            }
        )
    # DROP events that banked IRON -- the unambiguous "iron actually deposited" signal
    # (a DROP banks everything the unit carries; ``spent["IRON"]`` isolates the iron
    # share of that drop). Used both for "time to first deposit" and as an independent
    # cross-check on the conservation identity below.
    iron_drops = [
        {"turn": event["turn"], "unit_id": event["unit_id"], "iron_deposited": event["spent"].get("IRON", 0)}
        for event in action_events
        if event["verb"] == "DROP" and event["success"] and event["spent"].get("IRON", 0) > 0
    ]

    iron_bank_series = [state["inventories"][game.me][IRON_INDEX] for state in game.states]
    iron_carry_series = [
        sum(unit["carry"][IRON_INDEX] for unit in state["units"] if unit["player"] == game.me)
        for state in game.states
    ]
    # The real referee grants both players an identical, map-seeded *nonzero* starting
    # inventory (B3.8's own finding, re-confirmed here directly: e.g. game 896347357
    # starts at bank IRON=4) -- the conservation identity below must include it as a
    # third income source alongside MINE, or every game with a nonzero iron endowment
    # spuriously "fails" the check from turn 0 onward.
    starting_iron = int(game.states[0]["inventories"][game.me][IRON_INDEX])

    train_iron_by_turn: dict[int, int] = defaultdict(int)
    for event in game.train_events:
        cost = training_cost(event["n_before"], event["talents"])
        pay = training_pay_indices(game.iron_present)
        if IRON_INDEX in pay:
            train_iron_by_turn[event["turn"]] += cost[IRON_INDEX]
    spent_cumulative = [0] * (game.turns + 1)
    running_spent = 0
    for t in range(0, game.turns + 1):
        if t > 0:
            running_spent += train_iron_by_turn.get(t, 0)
        spent_cumulative[t] = running_spent

    mined_by_turn: dict[int, int] = defaultdict(int)
    for event in mine_events:
        mined_by_turn[event["turn"]] += event["iron_gained"]
    mined_cumulative = [0] * (game.turns + 1)
    running_mined = 0
    for t in range(0, game.turns + 1):
        if t > 0:
            running_mined += mined_by_turn.get(t, 0)
        mined_cumulative[t] = running_mined

    identity_mismatches = sum(
        1
        for t in range(0, game.turns + 1)
        if starting_iron + mined_cumulative[t] != iron_bank_series[t] + iron_carry_series[t] + spent_cumulative[t]
    )

    successful = [event for event in mine_events if event["success"]]
    first_mine_turn = min((event["turn"] for event in successful), default=None)
    first_deposit_turn = min((drop["turn"] for drop in iron_drops), default=None)
    total_deposited_via_drop = sum(drop["iron_deposited"] for drop in iron_drops)

    return {
        "mine_events": mine_events,
        "mine_action_count": len(mine_events),
        "mine_success_count": len(successful),
        "mine_success_rate": safe_ratio(len(successful), len(mine_events)),
        "starting_iron_endowment": starting_iron,
        "total_iron_mined": mined_cumulative[-1],
        "total_iron_deposited_via_drop": total_deposited_via_drop,
        "total_iron_spent_training": spent_cumulative[-1],
        "final_iron_bank": iron_bank_series[-1],
        "final_iron_carried_unbanked": iron_carry_series[-1],
        "first_mine_action_turn": first_mine_turn,
        "first_iron_deposit_turn": first_deposit_turn,
        "identity_mismatch_turns": identity_mismatches,
        "distinct_units_that_mined": sorted({event["unit_id"] for event in successful}),
        "ordinals_that_mined": sorted({event["ordinal"] for event in successful}),
        "workforce_at_mine_hist": dict(sorted(Counter(event["workforce_before"] for event in mine_events).items())),
    }


def immediate_mine_opportunities(game: DecodedGame) -> list[dict]:
    """Turns where MINE's exact rules precondition held for some own unit -- reusing
    ``waste_sweep.command_precondition_met`` (the same rule ``detect_repeated_failed_
    command`` already relies on: ``chop>0 and free>0 and manhattan(pos,ore)==1``) rather
    than re-deriving it -- joined with what the policy actually assigned that unit that
    turn. This is the tightest, zero-detour opportunity measure: no BFS/geometry
    modelling, a direct read of "was MINE legal right now".
    """

    iron_cells = game.board["iron"]
    walkable = game.board["walkable"]
    shack = game.own_shack
    results = []
    for frame in iter_turn_frames(game):
        for unit_id, unit in frame.before_units.items():
            legal = command_precondition_met(
                "MINE", ["MINE", str(unit_id)], unit, frame.before_plants,
                frame.bank_before, shack, iron_cells, walkable,
            )
            if not legal:
                continue
            command = frame.assigned.get(unit_id) or "WAIT"
            verb = command.split()[0].upper() if command else "WAIT"
            results.append(
                {
                    "turn": frame.turn,
                    "unit_id": unit_id,
                    "workforce_before": len(frame.before_units),
                    "pos": [unit["x"], unit["y"]],
                    "chop": unit["chop"],
                    "free_before": unit["cc"] - sum(unit["carry"]),
                    "assigned_command": command,
                    "assigned_verb": verb,
                    "mined": verb == "MINE",
                }
            )
    return results


# ---------------------------------------------------------------------------
# Task step 2: iron opportunity, measured (geometry + reachability)
# ---------------------------------------------------------------------------


def iron_source_geometry(game: DecodedGame) -> list[dict]:
    """Per iron source: its walkable ortho-neighbour cells (the only cells a unit can
    stand on to MINE it -- iron cells themselves are not walkable terrain, confirmed by
    ``top_player_opening_analysis.terrain``'s mutually-exclusive walkable/iron cell
    classification) and the multi-source BFS distance *from every walkable cell to
    being-adjacent-to-this-source* (``dist_map[cell]`` -- 0 means already adjacent, i.e.
    MINE is legal from there right now). ``dist_map`` is an internal working field (dict
    keyed by (x, y) tuples) and is stripped before JSON serialization by
    :func:`source_report`.
    """

    walkable = game.board["walkable"]
    sources = []
    for cell in sorted(game.board["iron"]):
        neighbors = [n for n in adjacent(cell) if n in walkable]
        dist_map = bfs(walkable, neighbors) if neighbors else {}
        own_door_distance = min((dist_map.get(door, UNREACHABLE) for door in game.own_doors), default=UNREACHABLE)
        opp_door_distance = min((dist_map.get(door, UNREACHABLE) for door in game.opp_doors), default=UNREACHABLE)
        sources.append(
            {
                "cell": cell,
                "neighbor_count": len(neighbors),
                "dist_map": dist_map,
                "own_door_distance": own_door_distance,
                "opp_door_distance": opp_door_distance,
            }
        )
    return sources


def closest_own_approach(source: dict, own_by_turn: list[list[dict]]) -> dict | None:
    best = None
    for turn, units in enumerate(own_by_turn):
        for unit in units:
            distance = source["dist_map"].get((unit["x"], unit["y"]), UNREACHABLE)
            if best is None or distance < best["distance"]:
                best = {"distance": distance, "turn": turn, "unit_id": unit["id"]}
    return best


def source_report(source: dict, own_by_turn: list[list[dict]]) -> dict:
    """JSON-safe per-source summary (strips the raw ``dist_map``)."""

    return {
        "cell": list(source["cell"]),
        "neighbor_count": source["neighbor_count"],
        "own_door_distance": source["own_door_distance"],
        "opp_door_distance": source["opp_door_distance"],
        "closest_own_trajectory_approach": closest_own_approach(source, own_by_turn),
    }


def iron_reachability_episodes(
    game: DecodedGame, sources: list[dict], own_by_turn: list[list[dict]]
) -> dict[str, list[dict]]:
    """Maximal-run "visit" episodes (via ``waste_sweep.RunTracker``, the same class
    every standing waste-sweep detector uses) of "own unit U was within
    ``IRON_REACH_BFS_RADIUS`` BFS steps of source S and had chop_power > 0", keyed by
    (source_index, unit_id) so simultaneous multi-unit or multi-source episodes are all
    counted independently (the real referee lets multiple units mine the same source
    from different adjacent cells simultaneously -- ``sim/engine.py:apply_mine`` has no
    per-source exclusivity).

    Both STRICT and GENEROUS share the *same* visit boundary (distance<=radius and
    chop>0) -- deliberately NOT re-opening a new episode every time free carry capacity
    flickers turn to turn while the unit stays put (an earlier version of this function
    gated the run boundary itself on instantaneous free capacity and produced 100+
    "episodes" for a single stationary unit whose carry oscillated turn to turn; that is
    a bookkeeping artefact, not 100 distinct opportunities to detour and mine). They
    differ only in how each visit is credited:

    - STRICT (the task's literal definition, "at a time when it had free carry
      capacity"): credited only if free capacity > 0 at *some* turn during the visit,
      using the best real yield ``min(chop, free)`` observed during the visit (a single
      mining action's worth, at the turn that maximum was achieved) -- 0 credit, no
      episode, if the unit was never actually empty enough to mine during that visit.
    - GENEROUS: always credited, at the visit's first turn, using ``min(chop, cc)`` --
      the unit's best-case yield if it had been empty, capped by its own total carry
      capacity (not just chop_power, so it never credits more iron than the unit could
      ever physically hold in one action) -- i.e. ignore the momentary capacity
      constraint entirely (a full unit could trivially have dropped cargo first).

    Credit is a single mining action's worth per visit (not a whole mining spree, and
    not repeated every turn of the visit -- BFS<=3 for many consecutive turns does not
    mean many actual MINE actions were possible; only true adjacency, distance 0, allows
    that), directly analogous to B3.8's fruit ``bankable_turn`` convention of crediting
    one discrete unit at the first turn it became reachable.
    """

    tracker = RunTracker()
    visits: list[dict] = []

    for turn, own_units in enumerate(own_by_turn):
        active = set()
        for source_index, source in enumerate(sources):
            dist_map = source["dist_map"]
            for unit in own_units:
                if unit["chop"] <= 0:
                    continue
                pos = (unit["x"], unit["y"])
                distance = dist_map.get(pos, UNREACHABLE)
                if distance > IRON_REACH_BFS_RADIUS:
                    continue
                free = unit["cc"] - sum(unit["carry"])
                key = (source_index, unit["id"])
                detail = {
                    "turn": turn,
                    "distance": distance,
                    "chop": unit["chop"],
                    "cc": unit["cc"],
                    "free": free,
                    "workforce": len(own_units),
                }
                tracker.mark(key, turn, detail)
                active.add(key)
        for run in tracker.sweep(active):
            visits.append(_finish_iron_visit(run, sources))
    for run in tracker.flush():
        visits.append(_finish_iron_visit(run, sources))

    episodes: dict[str, list[dict]] = {
        "strict": [visit["strict"] for visit in visits if visit["strict"] is not None],
        "generous": [visit["generous"] for visit in visits],
    }
    return episodes


def _finish_iron_visit(run: dict, sources: list[dict]) -> dict:
    source_index, unit_id = run["key"]
    details = run["details"]
    first = details[0]
    base = {
        "source_index": source_index,
        "source_cell": list(sources[source_index]["cell"]),
        "unit_id": unit_id,
        "start_turn": run["start"],
        "end_turn": run["end"],
        "duration": run["end"] - run["start"] + 1,
        "workforce_at_start": first["workforce"],
        "distance_at_start": first["distance"],
        "min_distance_in_run": min(detail["distance"] for detail in details),
    }

    generous_credit = min(first["chop"], first["cc"])
    generous = dict(base, credit_turn=run["start"], credit_iron=generous_credit)

    strict = None
    best_yield = -1
    best_detail = None
    for detail in details:
        realized = min(detail["chop"], detail["free"])
        if realized > best_yield:
            best_yield = realized
            best_detail = detail
    if best_yield > 0:
        strict = dict(
            base,
            credit_turn=best_detail["turn"],
            credit_iron=best_yield,
            workforce_at_credit=best_detail["workforce"],
        )

    return {"strict": strict, "generous": generous}


def iron_deposit_schedule(episodes: list[dict]) -> dict[int, list[int]]:
    """Same shape as ``training_currency_audit.deposit_schedule`` (turn -> 6-vector of
    deltas), so it can be merged with B3.8's own fruit schedule and fed unmodified into
    B3.8's ``augmented_bank_series``."""

    schedule: dict[int, list[int]] = defaultdict(lambda: [0] * 6)
    for episode in episodes:
        schedule[episode["credit_turn"]][IRON_INDEX] += episode["credit_iron"]
    return schedule


def merge_schedules(*schedules: dict[int, list[int]]) -> dict[int, list[int]]:
    merged: dict[int, list[int]] = defaultdict(lambda: [0] * 6)
    for schedule in schedules:
        for turn, vector in schedule.items():
            for index in range(6):
                merged[turn][index] += vector[index]
    return merged


# ---------------------------------------------------------------------------
# Task step 4: the combined counterfactual (reuses B3.8's window machinery verbatim)
# ---------------------------------------------------------------------------

SCENARIOS = (
    "baseline_real_bank_only",
    "fruit_only_own_or_unclaimed",
    "iron_only_strict",
    "iron_only_generous",
    "combined_strict",
    "combined_generous",
    "combined_generous_with_opponent_fruit",
)


def counterfactual_windows_for_game(
    game: DecodedGame, fruit_events: list[dict], iron_strict: list[dict], iron_generous: list[dict]
) -> dict:
    own_fruit = scenario_events(fruit_events, "own_or_unclaimed_only")
    all_fruit = scenario_events(fruit_events, "own_plus_opponent")
    fruit_schedule_own = deposit_schedule(own_fruit)
    fruit_schedule_all = deposit_schedule(all_fruit)
    iron_schedule_strict = iron_deposit_schedule(iron_strict)
    iron_schedule_generous = iron_deposit_schedule(iron_generous)

    scenario_schedules = {
        "baseline_real_bank_only": {},
        "fruit_only_own_or_unclaimed": fruit_schedule_own,
        "iron_only_strict": iron_schedule_strict,
        "iron_only_generous": iron_schedule_generous,
        "combined_strict": merge_schedules(fruit_schedule_own, iron_schedule_strict),
        "combined_generous": merge_schedules(fruit_schedule_own, iron_schedule_generous),
        "combined_generous_with_opponent_fruit": merge_schedules(fruit_schedule_all, iron_schedule_generous),
    }

    windows = {}
    for scenario_name in SCENARIOS:
        schedule = scenario_schedules[scenario_name]
        bank_series = augmented_bank_series(game, schedule)
        per_spec = {}
        for spec_name, talents in SPECS.items():
            report = worker3_windows(game, bank_series, talents)
            report["closest_approach"] = closest_approach(game, bank_series, talents)
            per_spec[spec_name] = report
        windows[scenario_name] = per_spec
    return windows


# ---------------------------------------------------------------------------
# Per-game driver (resident corpus)
# ---------------------------------------------------------------------------


def analyze_one_game(game_id: int) -> dict:
    try:
        game = decode_game(game_id)
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit
        return {"ok": False, "game_id": game_id, "error": f"{type(exc).__name__}: {exc}"}

    own_by_turn = own_states_by_turn(game)
    behavior = mining_behavior_for_game(game)
    sources = iron_source_geometry(game)
    reach = iron_reachability_episodes(game, sources, own_by_turn)
    immediate = immediate_mine_opportunities(game)
    fruit_events, fruit_diag = enumerate_fruit_events(game)
    windows = counterfactual_windows_for_game(game, fruit_events, reach["strict"], reach["generous"])

    immediate_wf1 = [row for row in immediate if row["workforce_before"] == 1]
    immediate_wf2p = [row for row in immediate if row["workforce_before"] >= 2]
    immediate_wf2p_missed = [row for row in immediate_wf2p if not row["mined"]]

    return {
        "ok": True,
        "game_id": game.game_id,
        "margin": game.margin,
        "won": game.won,
        "turns": game.turns,
        "iron_present": game.iron_present,
        "opponent": game.opponent_name,
        "iron_sources": [source_report(source, own_by_turn) for source in sources],
        "mining_behavior": {key: value for key, value in behavior.items() if key != "mine_events"},
        "mine_events": behavior["mine_events"],
        "reachability_episodes": reach,
        "immediate_opportunity": {
            "workforce1_turns": len(immediate_wf1),
            "workforce1_mined_turns": sum(1 for row in immediate_wf1 if row["mined"]),
            "workforce2plus_turns": len(immediate_wf2p),
            "workforce2plus_mined_turns": sum(1 for row in immediate_wf2p if row["mined"]),
            "workforce2plus_missed_examples": immediate_wf2p_missed[:MAX_EXAMPLES_PER_GAME],
        },
        "fruit_growth_anomalies": fruit_diag["growth_anomalies"],
        "windows": windows,
    }


# ---------------------------------------------------------------------------
# Task step 5: top-5 cohort mining contrast (same D61p snapshot occurrences as B3.8)
# ---------------------------------------------------------------------------


def analyze_top5_iron(occurrence: tuple[dict, int, dict]) -> dict:
    task, agent_id, meta = occurrence
    bill = analyze_top5_occurrence(occurrence)  # B3.8's own bill-provenance analysis, reused verbatim
    if not bill.get("ok"):
        return {"ok": False, "game_id": bill.get("game_id"), "agent_id": agent_id, "error": bill.get("error")}
    try:
        raw = json.loads(Path(task["raw_path"]).read_text())
        game_id = int(raw.get("gameId"))
        trajectory = read_jsonl(Path(task["trajectory_path"]))
        decoded_map, states, _unknown = decoded_states(raw, trajectory)
        agents = raw.get("agents") or []
        seat = next(
            index
            for index in (0, 1)
            if index < len(agents) and int((agents[index] or {}).get("agentId", -1)) == agent_id
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
        behavior = mining_behavior_for_game(game)
        _ordinals, analysis = worker_ordinals_for(game)
        worker_meta = {worker["unit_id"]: worker for worker in analysis["workers"]}

        miner_breakdown = []
        for unit_id in behavior["distinct_units_that_mined"]:
            worker = worker_meta.get(unit_id, {})
            commands = worker.get("commands", {})
            total_commands = sum(commands.values()) or 1
            miner_breakdown.append(
                {
                    "unit_id": unit_id,
                    "ordinal": worker.get("ordinal"),
                    "role": worker.get("role"),
                    "spec": worker.get("spec"),
                    "spawn_turn": worker.get("spawn_turn"),
                    "mine_command_count": commands.get("MINE", 0),
                    "total_command_count": total_commands,
                    "mine_share_of_own_commands": safe_ratio(commands.get("MINE", 0), total_commands),
                    "iron_mined": worker.get("mined", {}).get("IRON", 0),
                }
            )

        bill_iron_from_starting = sum(row["from_starting_endowment"]["iron"] for row in bill["train_events"])
        bill_iron_from_earned = sum(row["from_earned_income"]["iron"] for row in bill["train_events"])

        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": agent_id,
            "agent": meta.get("pseudo"),
            "source_rank": meta.get("source_rank"),
            "iron_present": game.iron_present,
            "mining_behavior": {key: value for key, value in behavior.items() if key != "mine_events"},
            "mine_events": behavior["mine_events"],
            "miner_breakdown": miner_breakdown,
            "bill_iron_from_starting_endowment": bill_iron_from_starting,
            "bill_iron_from_earned_income": bill_iron_from_earned,
        }
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit
        return {"ok": False, "game_id": bill.get("game_id"), "agent_id": agent_id, "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate_mining_behavior(ok_rows: list[dict]) -> dict:
    behaviors = [row["mining_behavior"] for row in ok_rows]
    total_actions = sum(b["mine_action_count"] for b in behaviors)
    total_success = sum(b["mine_success_count"] for b in behaviors)
    workforce_hist: Counter = Counter()
    for b in behaviors:
        for workforce, count in b["workforce_at_mine_hist"].items():
            workforce_hist[int(workforce)] += count
    first_turns = [b["first_mine_action_turn"] for b in behaviors if b["first_mine_action_turn"] is not None]
    games_with_mine = sum(1 for b in behaviors if b["mine_action_count"] > 0)
    return {
        "games": len(ok_rows),
        "games_with_any_mine_action": games_with_mine,
        "pct_games_with_any_mine_action": safe_ratio(games_with_mine, len(ok_rows)),
        "total_mine_actions_issued": total_actions,
        "total_mine_actions_successful": total_success,
        "corpus_mine_success_rate": safe_ratio(total_success, total_actions),
        "total_starting_iron_endowment_corpus": sum(b["starting_iron_endowment"] for b in behaviors),
        "total_iron_mined_corpus": sum(b["total_iron_mined"] for b in behaviors),
        "total_iron_deposited_via_drop_corpus": sum(b["total_iron_deposited_via_drop"] for b in behaviors),
        "total_iron_spent_training_corpus": sum(b["total_iron_spent_training"] for b in behaviors),
        "total_iron_stranded_carried_at_game_end": sum(b["final_iron_carried_unbanked"] for b in behaviors),
        "mean_iron_mined_per_game": mean(b["total_iron_mined"] for b in behaviors),
        "median_iron_mined_per_game": median(b["total_iron_mined"] for b in behaviors),
        "mean_mine_actions_per_game": mean(b["mine_action_count"] for b in behaviors),
        "first_mine_action_turn": {
            "median": median(first_turns),
            "mean": mean(first_turns),
            "n_games_ever_mined": len(first_turns),
        },
        "workforce_before_mine_action_histogram": dict(sorted(workforce_hist.items())),
        "identity_check_mismatch_turns_total": sum(b["identity_mismatch_turns"] for b in behaviors),
    }


def aggregate_immediate_opportunity(ok_rows: list[dict]) -> dict:
    wf1_turns = sum(row["immediate_opportunity"]["workforce1_turns"] for row in ok_rows)
    wf1_mined = sum(row["immediate_opportunity"]["workforce1_mined_turns"] for row in ok_rows)
    wf2_turns = sum(row["immediate_opportunity"]["workforce2plus_turns"] for row in ok_rows)
    wf2_mined = sum(row["immediate_opportunity"]["workforce2plus_mined_turns"] for row in ok_rows)
    games_with_wf2_opportunity = sum(1 for row in ok_rows if row["immediate_opportunity"]["workforce2plus_turns"] > 0)
    return {
        "workforce1_immediate_legal_turns": wf1_turns,
        "workforce1_immediate_legal_turns_mined": wf1_mined,
        "workforce1_immediate_take_rate": safe_ratio(wf1_mined, wf1_turns),
        "workforce2plus_immediate_legal_turns": wf2_turns,
        "workforce2plus_immediate_legal_turns_mined": wf2_mined,
        "workforce2plus_immediate_take_rate": safe_ratio(wf2_mined, wf2_turns),
        "games_with_workforce2plus_immediate_opportunity": games_with_wf2_opportunity,
    }


def aggregate_reachability(ok_rows: list[dict], mode: str) -> dict:
    all_episodes = [episode for row in ok_rows for episode in row["reachability_episodes"][mode]]
    total_credit = sum(episode["credit_iron"] for episode in all_episodes)
    wf1_credit = sum(episode["credit_iron"] for episode in all_episodes if episode["workforce_at_start"] == 1)
    wf2p_credit = sum(episode["credit_iron"] for episode in all_episodes if episode["workforce_at_start"] >= 2)
    games_with_episode = sum(1 for row in ok_rows if row["reachability_episodes"][mode])
    games_with_episode_zero_mined = sum(
        1
        for row in ok_rows
        if row["reachability_episodes"][mode] and row["mining_behavior"]["mine_success_count"] == 0
    )
    return {
        "total_episodes": len(all_episodes),
        "games_with_episode": games_with_episode,
        "pct_games_with_episode": safe_ratio(games_with_episode, len(ok_rows)),
        "games_with_episode_but_zero_actual_mining": games_with_episode_zero_mined,
        "total_credit_iron": total_credit,
        "credit_iron_while_workforce_1": wf1_credit,
        "credit_iron_while_workforce_2plus": wf2p_credit,
        "pct_credit_iron_while_workforce_2plus": safe_ratio(wf2p_credit, total_credit),
        "mean_episodes_per_game": mean(len(row["reachability_episodes"][mode]) for row in ok_rows),
    }


def aggregate_sources(ok_rows: list[dict]) -> dict:
    all_sources = [source for row in ok_rows for source in row["iron_sources"]]
    unreachable = [source for source in all_sources if source["neighbor_count"] == 0]
    own_distances = [source["own_door_distance"] for source in all_sources if source["own_door_distance"] < UNREACHABLE]
    approaches = [
        source["closest_own_trajectory_approach"]["distance"]
        for source in all_sources
        if source["closest_own_trajectory_approach"] is not None
        and source["closest_own_trajectory_approach"]["distance"] < UNREACHABLE
    ]
    never_approached = sum(
        1
        for source in all_sources
        if source["closest_own_trajectory_approach"] is None
        or source["closest_own_trajectory_approach"]["distance"] >= UNREACHABLE
    )
    return {
        "total_iron_sources_across_corpus": len(all_sources),
        "sources_per_game": {
            "mean": mean(len(row["iron_sources"]) for row in ok_rows),
            "median": median(len(row["iron_sources"]) for row in ok_rows),
        },
        "sources_with_zero_walkable_neighbors": len(unreachable),
        "own_door_distance": {"median": median(own_distances), "mean": mean(own_distances)},
        "closest_trajectory_approach_distance": {"median": median(approaches), "mean": mean(approaches)},
        "sources_own_units_never_approached": never_approached,
    }


def pick_root_cause_examples(ok_rows: list[dict], limit: int = 4) -> dict:
    early_example = None
    immediate_misses = []
    reachable_misses = []
    for row in ok_rows:
        if early_example is None:
            for event in row["mine_events"]:
                if event["success"] and event["workforce_before"] == 1:
                    early_example = {"game_id": row["game_id"], **event}
                    break
        if len(immediate_misses) < limit:
            for example in row["immediate_opportunity"]["workforce2plus_missed_examples"]:
                immediate_misses.append({"game_id": row["game_id"], **example})
                if len(immediate_misses) >= limit:
                    break
    for row in ok_rows:
        if len(reachable_misses) >= limit:
            break
        mined_turns = {event["turn"] for event in row["mine_events"] if event["success"]}
        for episode in row["reachability_episodes"]["strict"]:
            if episode["workforce_at_start"] < 2:
                continue
            overlap = any(episode["start_turn"] <= turn <= episode["end_turn"] for turn in mined_turns)
            if not overlap:
                reachable_misses.append({"game_id": row["game_id"], **episode})
                break
    return {
        "early_phase_successful_mine_example": early_example,
        "workforce2plus_immediate_precondition_met_but_not_mined_examples": immediate_misses,
        "workforce2plus_bfs3_reachable_but_never_mined_episode_examples": reachable_misses,
    }


def aggregate_top5(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row["ok"]]
    behaviors = [row["mining_behavior"] for row in ok_rows]
    total_actions = sum(b["mine_action_count"] for b in behaviors)
    total_success = sum(b["mine_success_count"] for b in behaviors)
    games_with_mine = sum(1 for b in behaviors if b["mine_action_count"] > 0)
    first_turns = [b["first_mine_action_turn"] for b in behaviors if b["first_mine_action_turn"] is not None]

    by_agent: dict[str, list[dict]] = defaultdict(list)
    for row in ok_rows:
        by_agent[row["agent"] or str(row["agent_id"])].append(row)
    per_agent = {}
    for agent, agent_rows in sorted(by_agent.items()):
        agent_behaviors = [row["mining_behavior"] for row in agent_rows]
        per_agent[agent] = {
            "games": len(agent_rows),
            "games_with_any_mine_action": sum(1 for b in agent_behaviors if b["mine_action_count"] > 0),
            "total_iron_mined": sum(b["total_iron_mined"] for b in agent_behaviors),
            "mean_iron_mined_per_game": mean(b["total_iron_mined"] for b in agent_behaviors),
            "total_mine_actions": sum(b["mine_action_count"] for b in agent_behaviors),
            "bill_iron_from_starting_endowment": sum(row["bill_iron_from_starting_endowment"] for row in agent_rows),
            "bill_iron_from_earned_income": sum(row["bill_iron_from_earned_income"] for row in agent_rows),
        }

    all_miners = [miner for row in ok_rows for miner in row["miner_breakdown"]]
    dedicated_leaning = sum(1 for miner in all_miners if (miner["mine_share_of_own_commands"] or 0) >= 0.3)

    return {
        "games_analyzed": len(ok_rows),
        "games_failed": len(rows) - len(ok_rows),
        "games_with_any_mine_action": games_with_mine,
        "pct_games_with_any_mine_action": safe_ratio(games_with_mine, len(ok_rows)),
        "total_mine_actions_issued": total_actions,
        "total_mine_actions_successful": total_success,
        "total_iron_mined": sum(b["total_iron_mined"] for b in behaviors),
        "mean_iron_mined_per_game": mean(b["total_iron_mined"] for b in behaviors),
        "median_iron_mined_per_game": median(b["total_iron_mined"] for b in behaviors),
        "first_mine_action_turn": {"median": median(first_turns), "mean": mean(first_turns)},
        "bill_iron_from_starting_endowment_total": sum(row["bill_iron_from_starting_endowment"] for row in ok_rows),
        "bill_iron_from_earned_income_total": sum(row["bill_iron_from_earned_income"] for row in ok_rows),
        "distinct_miners_observed": len(all_miners),
        "miners_with_mine_share_ge_0.3_dedicated_leaning": dedicated_leaning,
        "miners_with_mine_share_lt_0.3_opportunistic_leaning": len(all_miners) - dedicated_leaning,
        "miner_role_counts": dict(sorted(Counter(miner["role"] for miner in all_miners).items())),
        "miner_ordinal_counts": dict(sorted(Counter(miner["ordinal"] for miner in all_miners).items())),
        "per_agent": per_agent,
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

    windows_block = {
        scenario: {spec_name: window_summary(ok, scenario, spec_name) for spec_name in SPECS}
        for scenario in SCENARIOS
    }

    games_meta = [
        {
            "game_id": row["game_id"],
            "margin": row["margin"],
            "won": row["won"],
            "turns": row["turns"],
            "opponent": row["opponent"],
            "mine_action_count": row["mining_behavior"]["mine_action_count"],
            "total_iron_mined": row["mining_behavior"]["total_iron_mined"],
            "first_mine_action_turn": row["mining_behavior"]["first_mine_action_turn"],
            "iron_sources": len(row["iron_sources"]),
        }
        for row in ok
    ]

    report = {
        "schema": "troll-farm-b39-iron-acquisition-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only IRON-acquisition audit + combined (fruit+iron) affordability "
            "counterfactual over the resident's own decoded arena replays; no arena "
            "writes, no strategy changes, no rerun of any game"
        ),
        "caveat": (
            "The combined counterfactual (windows.combined_strict / combined_generous / "
            "combined_generous_with_opponent_fruit) is an UPPER BOUND, not a causal "
            "simulation: it banks iron/fruit at the turn a unit was reachable with no "
            "other change to behaviour -- it ignores that mining/harvesting/banking cost "
            "real turns and would change the trajectory (unit positions, opponent "
            "responses, later opportunity availability) in ways this script does not "
            "model. Iron credit is a single mining action's worth per reachable episode "
            "(not a whole mining spree), banked at the episode's first turn."
        ),
        "games_requested": len(per_game_results),
        "games_decoded_ok": len(ok),
        "games_failed": len(failed),
        "failures": failed[:50],
        "iron_present_games": sum(1 for row in ok if row["iron_present"]),
        "reach_bfs_radius": IRON_REACH_BFS_RADIUS,
        "mining_behavior": aggregate_mining_behavior(ok),
        "immediate_opportunity": aggregate_immediate_opportunity(ok),
        "reachability_opportunity": {
            "strict": aggregate_reachability(ok, "strict"),
            "generous": aggregate_reachability(ok, "generous"),
        },
        "iron_source_geometry": aggregate_sources(ok),
        "root_cause_examples": pick_root_cause_examples(ok),
        "windows": windows_block,
        "games": games_meta,
    }
    if top5_rows is not None:
        report["top5_mining_contrast"] = {"meta": top5_meta, **aggregate_top5(top5_rows)}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 means every resident game in the corpus")
    parser.add_argument("--skip-top5", action="store_true", help="skip the step-5 top-cohort mining contrast")
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
            top5_rows = [analyze_top5_iron(occurrence) for occurrence in occurrences]
        else:
            with ProcessPoolExecutor(max_workers=args.jobs) as executor:
                top5_rows = list(executor.map(analyze_top5_iron, occurrences, chunksize=2))

    report = build_report(per_game_results, top5_rows, top5_meta)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")

    print(f"resident games decoded: {report['games_decoded_ok']}/{report['games_requested']}")
    if report["games_failed"]:
        print(f"decode failures: {report['games_failed']}")
    mb = report["mining_behavior"]
    print(
        f"mining: {mb['games_with_any_mine_action']}/{mb['games']} games mine at least once "
        f"({mb['pct_games_with_any_mine_action']:.1%}), {mb['total_mine_actions_issued']} MINE actions issued, "
        f"{mb['total_iron_mined_corpus']} IRON mined, workforce histogram={mb['workforce_before_mine_action_histogram']}, "
        f"identity mismatches={mb['identity_check_mismatch_turns_total']}"
    )
    io = report["immediate_opportunity"]
    print(
        f"immediate opportunity: workforce=1 take-rate={io['workforce1_immediate_take_rate']}, "
        f"workforce>=2 take-rate={io['workforce2plus_immediate_take_rate']} "
        f"({io['workforce2plus_immediate_legal_turns']} legal turns across "
        f"{io['games_with_workforce2plus_immediate_opportunity']} games)"
    )
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
        t5 = report["top5_mining_contrast"]
        print(
            f"  top5 mining: {t5['games_with_any_mine_action']}/{t5['games_analyzed']} games mine "
            f"({t5['pct_games_with_any_mine_action']:.1%}), mean iron/game={t5['mean_iron_mined_per_game']}"
        )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
