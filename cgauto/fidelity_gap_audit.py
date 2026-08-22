#!/usr/bin/env python3
"""H13 fidelity-gap replay cross-check: our resident vs yamo's ladder agent.

Read-only. Task record: coordination/tasks/20260729-h13-fidelity-gap.md. The resident
(agent 6561795) is a reproduction of Yann Moisan's (yamo, agent 6479814) #3-Legend
Troll Farm bot; yamo currently outranks the resident by ~2.94 points at the identical
fixed 2-troll roster. This script does NOT diff source code (that is done by hand
against ``git show HEAD:rust/src/bin/yamo_orchard_live.rs`` -- see the report). It
cross-checks specific source-level deviations against *observed play* in the local
replay corpus, using ``cgauto.waste_sweep``'s agent-agnostic decoder so the resident
and yamo are each decoded from their own seat by the identical code path -- "us" and
"yamo" differ only in whose replays and whose shack/seat feed the same functions.

Five matched measurements, one per named behavioural deviation in the task brief:

  1. ``focus_type``/typeToCut consistency -- share of a player's own CHOP actions that
     land on the postmortem-predicted focus species. Port of
     ``rust/src/bin/yamo_orchard_live.rs:749`` (``MoisanBot::focus_type``): the LEMON/
     PLUM species whose turn-0 trees have the lower summed BFS distance from the
     player's own shack doors (ties favour LEMON, matching Rust's ``min_by_key`` over
     ``[Lemon, Plum]``).
  2. Denial-chop distance signature -- among focus-type CHOPs, is the chopped tree
     closer to the OPPONENT's shack while ``opponent_trolls <= 2`` (the live gate at
     ``yamo_orchard_live.rs:1102``) than while ``opponent_trolls > 2``? A non-focus-type
     placebo split is reported alongside (the code's `+900/(1+dist)` bonus at line 1104
     only fires for focus-type trees, so the placebo split should show no such gap).
  3. Endgame planting timing/volume -- median first successful PLANT turn and PLANTs/
     game, matched the same way B4.4 measured the resident against a 25-agent cohort,
     but here computed for yamo's own 140 games specifically.
  4. Contested/zero-yield chop waste -- rate of own CHOP turns where an opponent unit
     is simultaneously chopping the identical cell (a direct behavioural probe of the
     ``opponent_eta_penalty`` risk term at ``yamo_orchard_live.rs:2868-2916``, confirmed
     by source reading to be permanently inert in the deployed spec: constructed with
     penalty 0 via ``regeneration_unblocked_with_routing(policy, 0)``), plus the rate of
     chop "episodes" (one unit's contiguous CHOP run on one cell) that end in the tree's
     death with zero wood ever banked, restricted to turns where the chopper had free
     capacity (excluding the already-closed B3.6 full-capacity artifact).
  5. Same-two-cell oscillation incidence -- B3.4's signature (root-caused to the
     memoryless detour tie-break in ``resolve_move_conflicts_with_priority_and_forbidden``,
     ``yamo_orchard_live.rs:1440-1528``), applied with one fixed, disclosed definition to
     both cohorts. This is an independently-defined detector, not a byte-reproduction of
     B3.4's own script; it exists to get a same-method YAMO-side number, which has never
     been computed before. Cite B3.4/D171a's own published numbers (18/194 games, worst
     131 turns) as the record for the resident side.

CLI::

    python3 cgauto/fidelity_gap_audit.py [--output PATH] [--limit N] [--jobs N]

Writes a JSON report (both cohort summaries plus a diff section) to ``--output`` if
given, else prints it to stdout.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import adjacent, assigned_unit_commands, bfs
from cgauto.waste_sweep import (
    WOOD_INDEX,
    DecodedGame,
    RESIDENT_AGENT_ID,
    agent_game_ids,
    decode_game_for_agent,
    manhattan,
)

RESIDENT_LABEL = "resident"
YAMO_LABEL = "yamo"
YAMO_AGENT_ID = 6479814

FOCUS_KINDS = ("LEMON", "PLUM")  # rust iterates [Lemon, Plum]; ties favour Lemon
OSCILLATION_MIN_RUN = 6  # >=3 back-and-forth cycles; module constant, not CLI-tunable

# ---------------------------------------------------------------------------
# Port of MoisanBot::focus_type (yamo_orchard_live.rs:749-766)
# ---------------------------------------------------------------------------


def focus_type(game: DecodedGame) -> str:
    """This player's turn-1 typeToCut, computed the same way the live bot computes it
    once at game start: BFS distance from the player's own shack doors, summed over
    every turn-0 tree of each candidate species, lower sum wins (ties -> LEMON)."""

    starts = [cell for cell in adjacent(game.own_shack) if cell in game.board["walkable"]]
    dist = bfs(game.board["walkable"], starts)
    initial_plants = game.states[0]["plants"]
    sums = {}
    for kind in FOCUS_KINDS:
        sums[kind] = sum(
            dist.get((plant["x"], plant["y"]), 10_000)
            for plant in initial_plants
            if plant["type"] == kind
        )
    return "LEMON" if sums["LEMON"] <= sums["PLUM"] else "PLUM"


# ---------------------------------------------------------------------------
# Per-turn decode (both players, positions + assigned commands + plant deltas)
# ---------------------------------------------------------------------------


@dataclass
class FullTurn:
    turn: int
    my_before: dict
    opp_before: dict
    my_after: dict
    my_assigned: dict
    opp_assigned: dict
    before_plants: dict
    after_plants: dict


def iter_full_turns(game: DecodedGame):
    for turn in range(1, game.turns + 1):
        before = game.states[turn - 1]
        after = game.states[turn]
        row = game.trajectory[turn - 1]
        my_cmds = action_commands(row.get(f"commands{game.me}"))
        opp_cmds = action_commands(row.get(f"commands{game.opponent}"))
        my_before = {unit["id"]: unit for unit in before["units"] if unit["player"] == game.me}
        opp_before = {unit["id"]: unit for unit in before["units"] if unit["player"] == game.opponent}
        my_after = {unit["id"]: unit for unit in after["units"] if unit["player"] == game.me}
        yield FullTurn(
            turn=turn,
            my_before=my_before,
            opp_before=opp_before,
            my_after=my_after,
            my_assigned=assigned_unit_commands(my_cmds, list(my_before.values())),
            opp_assigned=assigned_unit_commands(opp_cmds, list(opp_before.values())),
            before_plants={(p["x"], p["y"]): p for p in before["plants"]},
            after_plants={(p["x"], p["y"]): p for p in after["plants"]},
        )


# ---------------------------------------------------------------------------
# Per-game metric extraction
# ---------------------------------------------------------------------------


@dataclass
class GameMetrics:
    game_id: int
    turns: int
    focus: str
    focus_gap: int  # |lemon_sum - plum_sum|, descriptive only
    chop_events: list = field(default_factory=list)
    plant_events: list = field(default_factory=list)
    opp_plant_events: list = field(default_factory=list)
    chop_episodes: list = field(default_factory=list)
    oscillation_runs: list = field(default_factory=list)


def free_capacity(unit: dict) -> int:
    return unit["cc"] - sum(unit["carry"])


def analyze_game_metrics(game: DecodedGame) -> GameMetrics:
    focus = focus_type(game)
    starts = [cell for cell in adjacent(game.own_shack) if cell in game.board["walkable"]]
    dist0 = bfs(game.board["walkable"], starts)
    initial_plants = game.states[0]["plants"]
    lemon_sum = sum(
        dist0.get((p["x"], p["y"]), 10_000) for p in initial_plants if p["type"] == "LEMON"
    )
    plum_sum = sum(
        dist0.get((p["x"], p["y"]), 10_000) for p in initial_plants if p["type"] == "PLUM"
    )
    metrics = GameMetrics(
        game_id=game.game_id, turns=game.turns, focus=focus, focus_gap=abs(lemon_sum - plum_sum)
    )

    open_episode: dict[int, dict] = {}

    def close_episode(unit_id: int) -> None:
        episode = open_episode.pop(unit_id, None)
        if episode is not None:
            metrics.chop_episodes.append(episode)

    for ft in iter_full_turns(game):
        opp_troll_count = len(ft.opp_before)

        # --- CHOP events (own units only; CHOP has no coordinate, so the target
        # cell is the unit's own position at the start of this turn). ---
        chopping_units = set()
        for unit_id, command in ft.my_assigned.items():
            fields = command.split()
            if not fields or fields[0] != "CHOP":
                continue
            unit = ft.my_before.get(unit_id)
            if unit is None:
                continue
            cell = (unit["x"], unit["y"])
            plant = ft.before_plants.get(cell)
            species = plant["type"] if plant is not None else None
            after_unit = ft.my_after.get(unit_id)
            wood_gained = 0
            if after_unit is not None:
                wood_gained = after_unit["carry"][WOOD_INDEX] - unit["carry"][WOOD_INDEX]
            died_this_turn = cell not in ft.after_plants
            contested = any(
                (opp_unit["x"], opp_unit["y"]) == cell
                and ft.opp_assigned.get(opp_id, "").split()[:1] == ["CHOP"]
                for opp_id, opp_unit in ft.opp_before.items()
            )
            copresent = any(
                (opp_unit["x"], opp_unit["y"]) == cell for opp_unit in ft.opp_before.values()
            )
            metrics.chop_events.append(
                {
                    "turn": ft.turn,
                    "species": species,
                    "is_focus": species == focus,
                    "opp_troll_count": opp_troll_count,
                    "dist_opp_shack": manhattan(cell, game.opp_shack),
                    "dist_own_shack": manhattan(cell, game.own_shack),
                    "contested": contested,
                    "copresent": copresent,
                    "wood_gained": wood_gained,
                    "died_this_turn": died_this_turn,
                    "free_capacity": free_capacity(unit),
                }
            )
            chopping_units.add(unit_id)

            episode = open_episode.get(unit_id)
            if (
                episode is not None
                and episode["cell"] == cell
                and episode["last_turn"] == ft.turn - 1
            ):
                episode["last_turn"] = ft.turn
                episode["wood"] += max(wood_gained, 0)
                episode["last_free_capacity"] = free_capacity(unit)
                episode["died"] = died_this_turn
            else:
                close_episode(unit_id)
                open_episode[unit_id] = {
                    "unit_id": unit_id,
                    "cell": cell,
                    "species": species,
                    "start_turn": ft.turn,
                    "last_turn": ft.turn,
                    "wood": max(wood_gained, 0),
                    "last_free_capacity": free_capacity(unit),
                    "died": died_this_turn,
                }

        for unit_id in list(open_episode):
            if unit_id not in chopping_units:
                close_episode(unit_id)

        # --- successful PLANT events (own units only). ---
        for cell, plant in ft.after_plants.items():
            if cell in ft.before_plants:
                continue
            creator = None
            for unit_id, command in ft.my_assigned.items():
                fields = command.split()
                unit = ft.my_before.get(unit_id)
                if (
                    len(fields) >= 3
                    and fields[0] == "PLANT"
                    and unit is not None
                    and (unit["x"], unit["y"]) == cell
                    and fields[2] == plant["type"]
                ):
                    creator = unit_id
                    break
            if creator is not None:
                metrics.plant_events.append({"turn": ft.turn, "species": plant["type"], "cell": cell})
                continue
            # --- successful OPPONENT PLANT events -- probes the postmortem's endgame
            # "park adjacent to the opponent's shack ... contest any last-minute
            # planting" clause (yann-moisan-postmortem-2026-05-26.txt:130-139), which
            # has no corresponding code anywhere in yamo_orchard_live.rs (view.shacks[1]
            # occurs only at the denial bonus and the orchard-geometry gates, never as an
            # endgame fallback position). "Ahead" uses the same bank-equivalent score the
            # live endgame() trigger itself reads (build_decoded_game's margin_series).
            opp_creator = None
            for unit_id, command in ft.opp_assigned.items():
                fields = command.split()
                unit = ft.opp_before.get(unit_id)
                if (
                    len(fields) >= 3
                    and fields[0] == "PLANT"
                    and unit is not None
                    and (unit["x"], unit["y"]) == cell
                    and fields[2] == plant["type"]
                ):
                    opp_creator = unit_id
                    break
            if opp_creator is not None:
                ahead = game.margin_series[ft.turn - 1] > 0
                metrics.opp_plant_events.append(
                    {
                        "turn": ft.turn,
                        "species": plant["type"],
                        "cell": cell,
                        "ahead": ahead,
                        # turn > 250 mirrors the live endgame() trigger's own literal
                        # threshold (yamo_orchard_live.rs:3428) and the postmortem's
                        # stated number, isolating the specific endgame-contest clause
                        # rather than routine mid-game farming (plants happen
                        # continuously all game, diluting an unrestricted "ahead" count).
                        "endgame_window": ft.turn > 250,
                    }
                )

    for unit_id in list(open_episode):
        close_episode(unit_id)

    # --- same-two-cell oscillation (own units only). ---
    by_unit: dict[int, list[tuple[int, int]]] = {}
    for state in game.states:
        for unit in state["units"]:
            if unit["player"] != game.me:
                continue
            by_unit.setdefault(unit["id"], []).append((unit["x"], unit["y"]))
    for unit_id, sequence in by_unit.items():
        n = len(sequence)
        i = 0
        while i < n - 2:
            if sequence[i] == sequence[i + 2] and sequence[i] != sequence[i + 1]:
                j = i
                while (
                    j + 2 < n and sequence[j] == sequence[j + 2] and sequence[j] != sequence[j + 1]
                ):
                    j += 1
                run_len = j - i + 2
                if run_len >= OSCILLATION_MIN_RUN:
                    metrics.oscillation_runs.append(
                        {"unit_id": unit_id, "start_index": i, "length": run_len}
                    )
                i = j + 1
            else:
                i += 1

    return metrics


# ---------------------------------------------------------------------------
# Cohort aggregation
# ---------------------------------------------------------------------------


def _analyze_one_game(game_id: int, agent_id: int) -> dict:
    try:
        game = decode_game_for_agent(game_id, agent_id)
    except Exception as exc:  # noqa: BLE001 -- one bad game must not abort the sweep
        return {"ok": False, "game_id": game_id, "error": f"{type(exc).__name__}: {exc}"}
    metrics = analyze_game_metrics(game)
    return {"ok": True, "game_id": game_id, "margin": game.margin, "metrics": metrics}


def mean_or_none(values: list[float]):
    return statistics.mean(values) if values else None


def median_or_none(values: list[float]):
    return statistics.median(values) if values else None


def summarize_cohort(label: str, agent_id: int, game_ids: list[int], jobs: int) -> dict:
    worker = partial(_analyze_one_game, agent_id=agent_id)
    results = []
    if jobs == 1:
        for game_id in game_ids:
            results.append(worker(game_id))
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            for result in executor.map(worker, game_ids, chunksize=2):
                results.append(result)
    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    focus_counts = {"LEMON": 0, "PLUM": 0}
    total_chop_turns = 0
    focus_chop_turns = 0
    focus_chop_le2 = 0
    focus_chop_gt2 = 0
    nonfocus_chop_le2 = 0
    nonfocus_chop_gt2 = 0
    dist_focus_le2 = []
    dist_focus_gt2 = []
    dist_nonfocus_le2 = []
    dist_nonfocus_gt2 = []
    contested_chop_turns = 0
    copresent_chop_turns = 0

    total_episodes = 0
    wasted_episodes = 0  # zero wood, tree died on our last chopping turn, had free capacity
    zero_wood_episodes = 0  # zero wood, any reason, had free capacity on the last turn

    games_with_plant = 0
    first_plant_turns = []
    plants_per_game = []

    opp_plants_total = 0
    opp_plants_while_ahead = 0
    games_with_opp_plant_while_ahead = 0
    opp_plants_while_ahead_per_game = []
    opp_plants_endgame_while_ahead = 0
    games_with_opp_plant_endgame_while_ahead = 0
    opp_plants_endgame_while_ahead_per_game = []
    games_reaching_endgame_window = 0

    games_with_oscillation = 0
    oscillation_lengths = []

    per_game_rows = []

    for result in ok:
        metrics: GameMetrics = result["metrics"]
        focus_counts[metrics.focus] += 1

        game_focus_chops = 0
        game_total_chops = 0
        for event in metrics.chop_events:
            total_chop_turns += 1
            game_total_chops += 1
            if event["contested"]:
                contested_chop_turns += 1
            if event["copresent"]:
                copresent_chop_turns += 1
            le2 = event["opp_troll_count"] <= 2
            if event["is_focus"]:
                focus_chop_turns += 1
                game_focus_chops += 1
                if le2:
                    focus_chop_le2 += 1
                    dist_focus_le2.append(event["dist_opp_shack"])
                else:
                    focus_chop_gt2 += 1
                    dist_focus_gt2.append(event["dist_opp_shack"])
            else:
                if le2:
                    nonfocus_chop_le2 += 1
                    dist_nonfocus_le2.append(event["dist_opp_shack"])
                else:
                    nonfocus_chop_gt2 += 1
                    dist_nonfocus_gt2.append(event["dist_opp_shack"])

        for episode in metrics.chop_episodes:
            total_episodes += 1
            if episode["wood"] == 0 and episode["last_free_capacity"] > 0:
                zero_wood_episodes += 1
                if episode["died"]:
                    wasted_episodes += 1

        plant_count = len(metrics.plant_events)
        plants_per_game.append(plant_count)
        if plant_count > 0:
            games_with_plant += 1
            first_plant_turns.append(min(e["turn"] for e in metrics.plant_events))

        game_opp_plants_while_ahead = sum(1 for e in metrics.opp_plant_events if e["ahead"])
        opp_plants_total += len(metrics.opp_plant_events)
        opp_plants_while_ahead += game_opp_plants_while_ahead
        opp_plants_while_ahead_per_game.append(game_opp_plants_while_ahead)
        if game_opp_plants_while_ahead > 0:
            games_with_opp_plant_while_ahead += 1

        game_opp_plants_endgame_while_ahead = sum(
            1 for e in metrics.opp_plant_events if e["ahead"] and e["endgame_window"]
        )
        opp_plants_endgame_while_ahead += game_opp_plants_endgame_while_ahead
        if metrics.turns > 250:
            games_reaching_endgame_window += 1
            opp_plants_endgame_while_ahead_per_game.append(game_opp_plants_endgame_while_ahead)
            if game_opp_plants_endgame_while_ahead > 0:
                games_with_opp_plant_endgame_while_ahead += 1

        if metrics.oscillation_runs:
            games_with_oscillation += 1
            oscillation_lengths.extend(run["length"] for run in metrics.oscillation_runs)

        per_game_rows.append(
            {
                "game_id": result["game_id"],
                "margin": result["margin"],
                "focus": metrics.focus,
                "chop_turns": game_total_chops,
                "focus_chop_turns": game_focus_chops,
                "plants": plant_count,
                "opp_plants_while_ahead": game_opp_plants_while_ahead,
                "oscillation_episodes": len(metrics.oscillation_runs),
            }
        )

    return {
        "label": label,
        "agent_id": agent_id,
        "games_requested": len(game_ids),
        "games_decoded_ok": len(ok),
        "games_failed": len(failed),
        "failures": failed[:20],
        "focus_species_counts": focus_counts,
        "chop": {
            "total_chop_turns": total_chop_turns,
            "focus_chop_turns": focus_chop_turns,
            "focus_share": focus_chop_turns / total_chop_turns if total_chop_turns else None,
            "focus_chop_le2_opp": focus_chop_le2,
            "focus_chop_gt2_opp": focus_chop_gt2,
            "focus_share_le2_opp": focus_chop_le2 / (focus_chop_le2 + nonfocus_chop_le2)
            if (focus_chop_le2 + nonfocus_chop_le2)
            else None,
            "focus_share_gt2_opp": focus_chop_gt2 / (focus_chop_gt2 + nonfocus_chop_gt2)
            if (focus_chop_gt2 + nonfocus_chop_gt2)
            else None,
            "mean_dist_opp_shack_focus_le2": mean_or_none(dist_focus_le2),
            "mean_dist_opp_shack_focus_gt2": mean_or_none(dist_focus_gt2),
            "n_focus_le2": len(dist_focus_le2),
            "n_focus_gt2": len(dist_focus_gt2),
            "mean_dist_opp_shack_nonfocus_le2": mean_or_none(dist_nonfocus_le2),
            "mean_dist_opp_shack_nonfocus_gt2": mean_or_none(dist_nonfocus_gt2),
            "n_nonfocus_le2": len(dist_nonfocus_le2),
            "n_nonfocus_gt2": len(dist_nonfocus_gt2),
            "contested_chop_turn_rate": contested_chop_turns / total_chop_turns
            if total_chop_turns
            else None,
            "copresent_chop_turn_rate": copresent_chop_turns / total_chop_turns
            if total_chop_turns
            else None,
        },
        "chop_episodes": {
            "total_episodes": total_episodes,
            "wasted_episodes": wasted_episodes,
            "wasted_rate": wasted_episodes / total_episodes if total_episodes else None,
            "zero_wood_episodes": zero_wood_episodes,
            "zero_wood_rate": zero_wood_episodes / total_episodes if total_episodes else None,
        },
        "planting": {
            "games_with_successful_plant": games_with_plant,
            "games_with_successful_plant_share": games_with_plant / len(ok) if ok else None,
            "median_first_plant_turn": median_or_none(first_plant_turns),
            "mean_first_plant_turn": mean_or_none(first_plant_turns),
            "mean_plants_per_game": mean_or_none(plants_per_game),
        },
        "opponent_endgame_planting": {
            "opp_plants_total": opp_plants_total,
            "opp_plants_while_ahead": opp_plants_while_ahead,
            "opp_plants_while_ahead_share_of_opp_plants": opp_plants_while_ahead / opp_plants_total
            if opp_plants_total
            else None,
            "mean_opp_plants_while_ahead_per_game": mean_or_none(opp_plants_while_ahead_per_game),
            "games_with_opp_plant_while_ahead_share": games_with_opp_plant_while_ahead / len(ok)
            if ok
            else None,
            "games_reaching_endgame_window_gt_turn_250": games_reaching_endgame_window,
            "games_reaching_endgame_window_share": games_reaching_endgame_window / len(ok)
            if ok
            else None,
            "mean_opp_plants_endgame_while_ahead_per_game_reaching_window": mean_or_none(
                opp_plants_endgame_while_ahead_per_game
            ),
            "games_with_opp_plant_endgame_while_ahead_share_of_reaching_window": (
                games_with_opp_plant_endgame_while_ahead / games_reaching_endgame_window
                if games_reaching_endgame_window
                else None
            ),
        },
        "oscillation": {
            "games_with_episode": games_with_oscillation,
            "games_with_episode_share": games_with_oscillation / len(ok) if ok else None,
            "n_episodes": len(oscillation_lengths),
            "worst_episode_length": max(oscillation_lengths) if oscillation_lengths else None,
            "mean_episode_length": mean_or_none(oscillation_lengths),
        },
        "per_game": per_game_rows,
    }


def diff_section(resident: dict, yamo: dict) -> dict:
    def get(cohort, *path):
        node = cohort
        for key in path:
            if node is None:
                return None
            node = node.get(key)
        return node

    return {
        "focus_share": {
            "resident": get(resident, "chop", "focus_share"),
            "yamo": get(yamo, "chop", "focus_share"),
        },
        "focus_share_le2_minus_gt2_opp": {
            "resident": (
                None
                if get(resident, "chop", "focus_share_le2_opp") is None
                or get(resident, "chop", "focus_share_gt2_opp") is None
                else get(resident, "chop", "focus_share_le2_opp")
                - get(resident, "chop", "focus_share_gt2_opp")
            ),
            "yamo": (
                None
                if get(yamo, "chop", "focus_share_le2_opp") is None
                or get(yamo, "chop", "focus_share_gt2_opp") is None
                else get(yamo, "chop", "focus_share_le2_opp") - get(yamo, "chop", "focus_share_gt2_opp")
            ),
        },
        "denial_distance_gap_focus_gt2_minus_le2": {
            "resident": (
                None
                if get(resident, "chop", "mean_dist_opp_shack_focus_gt2") is None
                or get(resident, "chop", "mean_dist_opp_shack_focus_le2") is None
                else get(resident, "chop", "mean_dist_opp_shack_focus_gt2")
                - get(resident, "chop", "mean_dist_opp_shack_focus_le2")
            ),
            "yamo": (
                None
                if get(yamo, "chop", "mean_dist_opp_shack_focus_gt2") is None
                or get(yamo, "chop", "mean_dist_opp_shack_focus_le2") is None
                else get(yamo, "chop", "mean_dist_opp_shack_focus_gt2")
                - get(yamo, "chop", "mean_dist_opp_shack_focus_le2")
            ),
        },
        "denial_distance_gap_nonfocus_placebo_gt2_minus_le2": {
            "resident": (
                None
                if get(resident, "chop", "mean_dist_opp_shack_nonfocus_gt2") is None
                or get(resident, "chop", "mean_dist_opp_shack_nonfocus_le2") is None
                else get(resident, "chop", "mean_dist_opp_shack_nonfocus_gt2")
                - get(resident, "chop", "mean_dist_opp_shack_nonfocus_le2")
            ),
            "yamo": (
                None
                if get(yamo, "chop", "mean_dist_opp_shack_nonfocus_gt2") is None
                or get(yamo, "chop", "mean_dist_opp_shack_nonfocus_le2") is None
                else get(yamo, "chop", "mean_dist_opp_shack_nonfocus_gt2")
                - get(yamo, "chop", "mean_dist_opp_shack_nonfocus_le2")
            ),
        },
        "contested_chop_turn_rate": {
            "resident": get(resident, "chop", "contested_chop_turn_rate"),
            "yamo": get(yamo, "chop", "contested_chop_turn_rate"),
        },
        "chop_episode_wasted_rate": {
            "resident": get(resident, "chop_episodes", "wasted_rate"),
            "yamo": get(yamo, "chop_episodes", "wasted_rate"),
        },
        "chop_episode_zero_wood_rate": {
            "resident": get(resident, "chop_episodes", "zero_wood_rate"),
            "yamo": get(yamo, "chop_episodes", "zero_wood_rate"),
        },
        "median_first_plant_turn": {
            "resident": get(resident, "planting", "median_first_plant_turn"),
            "yamo": get(yamo, "planting", "median_first_plant_turn"),
        },
        "mean_plants_per_game": {
            "resident": get(resident, "planting", "mean_plants_per_game"),
            "yamo": get(yamo, "planting", "mean_plants_per_game"),
        },
        "games_with_successful_plant_share": {
            "resident": get(resident, "planting", "games_with_successful_plant_share"),
            "yamo": get(yamo, "planting", "games_with_successful_plant_share"),
        },
        "mean_opp_plants_while_ahead_per_game": {
            "resident": get(resident, "opponent_endgame_planting", "mean_opp_plants_while_ahead_per_game"),
            "yamo": get(yamo, "opponent_endgame_planting", "mean_opp_plants_while_ahead_per_game"),
        },
        "games_with_opp_plant_while_ahead_share": {
            "resident": get(resident, "opponent_endgame_planting", "games_with_opp_plant_while_ahead_share"),
            "yamo": get(yamo, "opponent_endgame_planting", "games_with_opp_plant_while_ahead_share"),
        },
        "games_reaching_endgame_window_share": {
            "resident": get(resident, "opponent_endgame_planting", "games_reaching_endgame_window_share"),
            "yamo": get(yamo, "opponent_endgame_planting", "games_reaching_endgame_window_share"),
        },
        "mean_opp_plants_endgame_while_ahead_per_game_reaching_window": {
            "resident": get(
                resident,
                "opponent_endgame_planting",
                "mean_opp_plants_endgame_while_ahead_per_game_reaching_window",
            ),
            "yamo": get(
                yamo,
                "opponent_endgame_planting",
                "mean_opp_plants_endgame_while_ahead_per_game_reaching_window",
            ),
        },
        "games_with_opp_plant_endgame_while_ahead_share_of_reaching_window": {
            "resident": get(
                resident,
                "opponent_endgame_planting",
                "games_with_opp_plant_endgame_while_ahead_share_of_reaching_window",
            ),
            "yamo": get(
                yamo,
                "opponent_endgame_planting",
                "games_with_opp_plant_endgame_while_ahead_share_of_reaching_window",
            ),
        },
        "oscillation_games_share": {
            "resident": get(resident, "oscillation", "games_with_episode_share"),
            "yamo": get(yamo, "oscillation", "games_with_episode_share"),
        },
        "oscillation_worst_episode_length": {
            "resident": get(resident, "oscillation", "worst_episode_length"),
            "yamo": get(yamo, "oscillation", "worst_episode_length"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()

    resident_ids = agent_game_ids(RESIDENT_AGENT_ID)
    yamo_ids = agent_game_ids(YAMO_AGENT_ID)
    if args.limit is not None:
        resident_ids = resident_ids[: args.limit]
        yamo_ids = yamo_ids[: args.limit]

    resident_summary = summarize_cohort(RESIDENT_LABEL, RESIDENT_AGENT_ID, resident_ids, args.jobs)
    yamo_summary = summarize_cohort(YAMO_LABEL, YAMO_AGENT_ID, yamo_ids, args.jobs)

    report = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only H13 fidelity-gap replay cross-check; no arena writes, no strategy "
            "changes, no source edits"
        ),
        "resident_agent_id": RESIDENT_AGENT_ID,
        "yamo_agent_id": YAMO_AGENT_ID,
        "cohorts": {RESIDENT_LABEL: resident_summary, YAMO_LABEL: yamo_summary},
        "diff": diff_section(resident_summary, yamo_summary),
    }

    text = json.dumps(report, indent=2, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
