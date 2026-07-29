#!/usr/bin/env python3
"""B3.7 crop-fate census: what happens to every crop a player plants.

Read-only diagnostic: it never touches the arena, never edits corpus data, and never
proposes strategy changes.  It tests the owner's hypothesis that planting is only worth
it if the planter can service its own orchard faster than the opponent takes it away --
i.e. that a capacity/pacing constraint, not opponent theft, explains why the resident
reaps only 0.94% of the crops it creates (D101) while the top-5 cohort reaps 24.16%.

Reuse (per the B3.7 brief -- this deliberately does not write a new replay parser):

- ``cgauto.recent_resident_field_census.decoded_states`` -- exact official per-turn
  state reconstruction from ``frame.diff`` data (also the foundation of
  ``cgauto/waste_sweep.py``).
- ``cgauto.top_player_opening_analysis.{terrain,adjacent,bfs,analyze_players}`` -- map
  geometry/BFS and per-player worker/training bookkeeping (worker ordinals, trained
  harvest_power).
- ``cgauto.analyze_d101a_production_suppression.reconstruct_generation_actions`` --
  the crop-lineage/ownership reconstruction that produced D101's 24.16%/0.94% reap
  rates; its per-generation ``origin`` labels (actor/opponent/natural/ambiguous/unknown)
  and per-turn ``lineage_by_state`` cell->generation map are the foundation of this
  census.  It is called once per seat per game (see ``analyze_occurrence``) so that an
  opponent's HARVEST/CHOP on *our* generations is captured too; generation ids are
  actor-invariant (an empirically-verified assumption -- see
  ``lineage_consistent_across_seats``/``generation_keys_consistent_across_seats`` in the
  per-occurrence integrity block), so both calls address the same crops.

Mechanics ground truth (verified 2026-07-28 against ``rust/src/game/engine.rs``
(``tick_plants``/``apply_chop``/``apply_chop_on_cells``) and the parity-checked
``sim/engine.py`` port): a tree is removed from the board ONLY by CHOP driving health to
0.  ``tick_plants`` only grows size or adds a fruit (capped at 3); it never removes a
plant, and nothing else in the engine does either.  There is therefore no
natural-death/timeout mechanic for trees.  The owner's fate (e), "died/expired
unserviced", cannot be a tree-disposal method distinct from "chopped by us"/"chopped by
opponent" -- it is operationalized here at the RIPE-FRUIT level instead: a maximal run of
consecutive turns with ``fruits > 0`` on one of our trees that ends via a chop or via
game end rather than via a harvest (see ``ripe_runs`` / "expired" episodes below). The
mutually-exclusive TREE-level fate partition below has 5 live buckets (a/b/c/d/f); a 6th,
``disappeared_unattributed``, exists only as an integrity trap (expected count 0 -- a
tree disappearing without a matching successful CHOP at that exact turn would be a decode
gap, not a game mechanic) and is reported honestly if it ever fires.

Also verified from source (``git show HEAD:rust/src/bin/yamo_orchard_live.rs``, the
resident's dev copy, ``troll_farm::resident_policy``): the "ScarceIntent" reserve
machinery the task brief points at is, in the live default config
(``SecureOrchardBot::new()`` -> ``task_market_enabled = false``), the *orchard mother*
mechanism: the starter plants exactly one APPLE tree on one of the resident's own door
cells (Manhattan distance 1 from its shack) that is also water-adjacent, chosen once at
init (``mothers`` candidate list, farthest from the enemy).  ``yamo_chop_candidates``
explicitly removes that cell from the resident's own chop targets
(``external_protected_tree``), and -- because ``task_market_enabled`` is false in the
live binary -- once that tree is alive the starter is FORCED, every single turn for the
rest of the game, into a MOVE-to-door / DROP / HARVEST / WAIT cycle on that one cell
(``SecureOrchardBot::commands``, the ``forced = if let Some(mother) = ...`` block).  So a
healthy mother tree should overwhelmingly land in the ``harvested_by_owner`` bucket, not
"unserviced" -- ``is_mother_candidate`` flags candidate cells (APPLE, own-door,
water-adjacent, AND planted by ordinal 0 -- the starter, never a trained worker in this
code path) so this can be checked directly rather than assumed.  The starter-ordinal
requirement was added after finding a false positive without it: a trained worker
(ordinal 1) running an ordinary repeated PLANT-then-CHOP wood-farming cycle on a door
cell that coincidentally happened to be water-adjacent too (game 896347357, cell
(10,2)) -- unrelated to the orchard mechanism, since only the starter ever executes the
mother's CarryingSeed/PLANT step.  This flag is resident-only: it encodes a fact about
this specific binary, not about the top-5 cohort's (unknown) source.

Usage::

    python3 cgauto/crop_fate_census.py --output <path/to/report.json> [--jobs 8]
        [--resident-limit N] [--top5-games-per-agent N] [--top5-count N]
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d101a_production_suppression import reconstruct_generation_actions
from cgauto.recent_resident_field_census import decoded_states
from cgauto.top_player_opening_analysis import adjacent, analyze_players, bfs, terrain

REPO = Path(__file__).resolve().parent.parent
RAW_GAMES = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
GAMES_INDEX = REPO / "data/processed/games.jsonl"
LEADERBOARD = REPO / "data/raw/leaderboard.json"

RESIDENT_AGENT_ID = 6561795
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
FRUIT_ITEMS = ITEMS[:4]
CHECKPOINT_TURNS = tuple(range(25, 301, 25))  # 25, 50, ..., 300
EXPIRY_BFS_RADIUS = 3  # task spec: "harvest-capable unit ... within reach (BFS distance <= 3)"
UNREACHABLE = 10_000

FATES = (
    "harvested_by_owner",
    "harvested_by_opponent",
    "chopped_by_owner",
    "chopped_by_opponent",
    "alive_at_end",
    "disappeared_unattributed",
)


# ---------------------------------------------------------------------------
# Corpus indexing
# ---------------------------------------------------------------------------


def load_games_index() -> dict[int, dict]:
    index = {}
    with GAMES_INDEX.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            index[int(row["gameId"])] = row
    return index


def top_agents(n: int) -> list[dict]:
    """The top-``n`` Legend-league agents by rank, from the current leaderboard read."""

    payload = json.loads(LEADERBOARD.read_text())
    legend = [
        row
        for row in payload["users"]
        if (row.get("league") or {}).get("divisionIndex") == 5
    ]
    legend.sort(key=lambda row: row.get("rank", 10**9))
    return legend[:n]


def select_occurrences(
    games_index: dict[int, dict],
    resident_id: int,
    top_cohort: list[dict],
    top_games_per_agent: int,
    resident_limit: int,
) -> list[tuple[int, int, int, str, str]]:
    """Return ``(game_id, actor_id, seat, cohort, pseudo)`` rows to analyze.

    Resident: every game in the corpus (full coverage, as the brief asks for), unless
    ``resident_limit`` caps it.  Top cohort: the first ``top_games_per_agent`` games per
    agent by game id (deterministic, reproducible) -- the population counts this script
    prints comfortably clear the brief's ">=300 crops" floor at any sane cap, since D101
    already established the top cohort plants ~35 crops/game.
    """

    rows = []
    resident_game_ids = sorted(
        game_id
        for game_id, row in games_index.items()
        if any(int(p["agentId"]) == resident_id for p in row["players"])
    )
    if resident_limit:
        resident_game_ids = resident_game_ids[:resident_limit]
    for game_id in resident_game_ids:
        player_row = next(
            p for p in games_index[game_id]["players"] if int(p["agentId"]) == resident_id
        )
        rows.append((game_id, resident_id, int(player_row["index"]), "resident", "resident"))

    top_ids = {int(row["agentId"]): row["pseudo"] for row in top_cohort}
    per_agent_game_ids: dict[int, list[int]] = defaultdict(list)
    for game_id, row in games_index.items():
        for player in row["players"]:
            agent_id = int(player["agentId"])
            if agent_id in top_ids:
                per_agent_game_ids[agent_id].append(game_id)
    for agent_id, game_ids in per_agent_game_ids.items():
        game_ids.sort()
        selected = game_ids[:top_games_per_agent] if top_games_per_agent else game_ids
        for game_id in selected:
            player_row = next(
                p for p in games_index[game_id]["players"] if int(p["agentId"]) == agent_id
            )
            rows.append(
                (game_id, agent_id, int(player_row["index"]), "top5", top_ids[agent_id])
            )
    rows.sort(key=lambda item: (item[3], item[4], item[0]))
    return rows


def load_game(game_id: int) -> tuple[dict, list[dict]]:
    raw = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
    trajectory = [
        json.loads(line)
        for line in (TRAJECTORIES / f"{game_id}.jsonl").read_text().splitlines()
        if line.strip()
    ]
    return raw, trajectory


# ---------------------------------------------------------------------------
# Per-occurrence analysis
# ---------------------------------------------------------------------------


def fruit_units_from_gained(gained: dict) -> int:
    return sum(int(gained.get(name, 0)) for name in FRUIT_ITEMS)


def resident_mother_candidate_cells(board: dict, own_shack: tuple[int, int]) -> set:
    """Cells matching the resident's own orchard-mother selection signature: one of its
    own door cells (Manhattan distance 1 from its shack) that is also water-adjacent --
    reproduced from ``yamo_orchard_live.rs``'s ``mothers`` candidate filter (see module
    docstring).  Behavioural proxy, not literal internal-state extraction; validated by
    the resulting per-game candidate-count distribution reported alongside it (expected
    to be almost always 0 or 1, since the bot commits to a single ``geometry.mother``).
    """

    doors = {cell for cell in adjacent(own_shack) if cell in board["walkable"]}
    return {
        cell
        for cell in doors
        if any(neighbor in board["water"] for neighbor in adjacent(cell))
    }


def analyze_occurrence(game_id: int, actor_id: int, seat: int, cohort: str, pseudo: str) -> dict:
    try:
        raw, trajectory = load_game(game_id)
        map_data, states, unknown = decoded_states(raw, trajectory)
        usable = min(len(states) - 1, len(trajectory))
        if unknown or usable != len(trajectory) or usable != len(states) - 1:
            return {
                "ok": False,
                "game_id": game_id,
                "agent_id": actor_id,
                "error": (
                    f"decode mismatch: unknown={unknown} usable={usable} "
                    f"states={len(states)} trajectory={len(trajectory)}"
                ),
            }
        actor = seat
        opponent = 1 - actor
        scores = [float(value) for value in raw["scores"]]
        ranks = raw.get("ranks") or []
        margin = scores[actor] - scores[opponent]
        won = bool(ranks and len(ranks) == 2 and ranks[actor] == 0 and margin > 0)

        analyses = analyze_players(states, trajectory)
        own_ordinals = {
            int(worker["unit_id"]): int(worker["ordinal"])
            for worker in analyses[actor]["workers"]
        }
        opp_ordinals = {
            int(worker["unit_id"]): int(worker["ordinal"])
            for worker in analyses[opponent]["workers"]
        }

        events, generations, lineage_by_state, quality = reconstruct_generation_actions(
            states, trajectory, actor, own_ordinals
        )
        events_opp, generations_opp, lineage_by_state_opp, _quality_opp = (
            reconstruct_generation_actions(states, trajectory, opponent, opp_ordinals)
        )
        # Generation ids / lineage are computed from plant history alone and should not
        # depend on which seat was passed as "actor" (only the origin label swaps) --
        # verify that empirically rather than assume it.
        lineage_consistent = lineage_by_state == lineage_by_state_opp
        generation_keys_consistent = set(generations) == set(generations_opp)

        board = terrain(map_data)
        own_shack = board["shacks"][actor]
        walkable = board["walkable"]

        plants_by_cell_per_turn = [
            {(plant["x"], plant["y"]): plant for plant in state["plants"]} for state in states
        ]
        own_units_per_turn = [
            [unit for unit in state["units"] if int(unit["player"]) == actor] for state in states
        ]

        mother_cells = (
            resident_mother_candidate_cells(board, own_shack)
            if actor_id == RESIDENT_AGENT_ID
            else set()
        )
        planter_ordinal_by_gen = {
            event["created_generation"]: event["ordinal"]
            for event in events
            if event["verb"] == "PLANT" and event["success"] and event["created_generation"]
        }

        def bucket_events(rows: list[dict]) -> tuple[dict, dict]:
            harvest_by_gen: dict[str, list[tuple[int, int]]] = defaultdict(list)
            chop_by_gen: dict[str, list[tuple[int, int]]] = defaultdict(list)
            for event in rows:
                if not event["success"]:
                    continue
                gid = event["target_generation"]
                if gid is None:
                    continue
                if event["verb"] == "HARVEST":
                    harvest_by_gen[gid].append((event["turn"], fruit_units_from_gained(event["gained"])))
                elif event["verb"] == "CHOP":
                    chop_by_gen[gid].append((event["turn"], int(event["gained"].get("WOOD", 0))))
            return harvest_by_gen, chop_by_gen

        own_harvest_by_gen, own_chop_by_gen = bucket_events(events)
        opp_harvest_by_gen, opp_chop_by_gen = bucket_events(events_opp)

        last_state_index = usable
        crops = []
        disappearance_unattributed = 0
        generations_without_alive_turn = 0
        non_contiguous_lineage = 0

        for gid, generation in generations.items():
            if generation["origin"] != "actor":
                continue
            cell = tuple(generation["cell"])
            birth_turn = int(generation["birth_turn"])
            kind = generation["kind"]

            alive_turns = [
                t
                for t in range(birth_turn, last_state_index + 1)
                if lineage_by_state[t].get(cell) == gid
            ]
            if not alive_turns:
                generations_without_alive_turn += 1
                continue
            if alive_turns != list(range(alive_turns[0], alive_turns[-1] + 1)):
                non_contiguous_lineage += 1
            last_turn_alive = alive_turns[-1]
            alive_at_end = last_turn_alive == last_state_index
            death_turn = None if alive_at_end else last_turn_alive + 1

            own_harvest_turns = sorted(turn for turn, _ in own_harvest_by_gen.get(gid, []))
            opp_harvest_turns = sorted(turn for turn, _ in opp_harvest_by_gen.get(gid, []))
            own_fruit_harvested = sum(value for _, value in own_harvest_by_gen.get(gid, []))
            opp_fruit_harvested = sum(value for _, value in opp_harvest_by_gen.get(gid, []))
            own_wood_from_chops = sum(value for _, value in own_chop_by_gen.get(gid, []))
            opp_wood_from_chops = sum(value for _, value in opp_chop_by_gen.get(gid, []))

            disposal = None
            if not alive_at_end:
                if any(turn == death_turn for turn, _ in own_chop_by_gen.get(gid, [])):
                    disposal = "owner"
                elif any(turn == death_turn for turn, _ in opp_chop_by_gen.get(gid, [])):
                    disposal = "opponent"
                else:
                    disposal = "unattributed"
                    disappearance_unattributed += 1

            if own_harvest_turns:
                fate = "harvested_by_owner"
            elif opp_harvest_turns:
                fate = "harvested_by_opponent"
            elif disposal == "owner":
                fate = "chopped_by_owner"
            elif disposal == "opponent":
                fate = "chopped_by_opponent"
            elif alive_at_end:
                fate = "alive_at_end"
            else:
                fate = "disappeared_unattributed"

            # Ripe-run / expiry analysis: maximal consecutive-turn runs of fruits > 0.
            distances = bfs(walkable, [cell])
            raw_runs = []
            run_start = None
            for t in range(birth_turn, last_turn_alive + 1):
                plant = plants_by_cell_per_turn[t].get(cell)
                fruits = int(plant["fruits"]) if plant is not None else 0
                if fruits > 0 and run_start is None:
                    run_start = t
                if fruits <= 0 and run_start is not None:
                    raw_runs.append((run_start, t - 1))
                    run_start = None
            if run_start is not None:
                raw_runs.append((run_start, last_turn_alive))

            ripe_runs = []
            for start, end in raw_runs:
                if end == last_turn_alive and not alive_at_end:
                    end_reason = "chopped"
                elif end == last_turn_alive and alive_at_end:
                    end_reason = "game_end"
                else:
                    end_reason = "harvested"
                capable_in_range_turns = 0
                capable_ever_in_range = False
                min_distance_seen = None
                for t in range(start, end + 1):
                    capable_positions = [
                        (unit["x"], unit["y"])
                        for unit in own_units_per_turn[t]
                        if int(unit["hp"]) >= 1
                    ]
                    if not capable_positions:
                        continue
                    reach = min(distances.get(pos, UNREACHABLE) for pos in capable_positions)
                    if min_distance_seen is None or reach < min_distance_seen:
                        min_distance_seen = reach
                    if reach <= EXPIRY_BFS_RADIUS:
                        capable_in_range_turns += 1
                        capable_ever_in_range = True
                ripe_runs.append(
                    {
                        "start_turn": start,
                        "end_turn": end,
                        "duration": end - start + 1,
                        "end_reason": end_reason,
                        "serviced": end_reason == "harvested",
                        "capable_owner_worker_ever_in_range": capable_ever_in_range,
                        "capable_owner_worker_turns_in_range": capable_in_range_turns,
                        "min_bfs_distance_seen": min_distance_seen,
                    }
                )

            crops.append(
                {
                    "generation_id": gid,
                    "cell": list(cell),
                    "kind": kind,
                    "birth_turn": birth_turn,
                    "last_turn_alive": last_turn_alive,
                    "death_turn": death_turn,
                    "alive_at_end": alive_at_end,
                    "disposal": disposal,
                    "fate": fate,
                    "planted_by_ordinal": planter_ordinal_by_gen.get(gid),
                    "is_mother_candidate": (
                        cell in mother_cells
                        and kind == "APPLE"
                        and planter_ordinal_by_gen.get(gid) == 0
                    ),
                    "own_harvest_turns": own_harvest_turns,
                    "opp_harvest_turns": opp_harvest_turns,
                    "own_fruit_harvested": own_fruit_harvested,
                    "opp_fruit_harvested": opp_fruit_harvested,
                    "own_wood_from_chops": own_wood_from_chops,
                    "opp_wood_from_chops": opp_wood_from_chops,
                    "ripe_runs": ripe_runs,
                }
            )

        own_gen_ids = {gid for gid, gen in generations.items() if gen["origin"] == "actor"}
        servicing_series = []
        for t in CHECKPOINT_TURNS:
            if t > last_state_index:
                break
            live_own_crops = sum(1 for gid in lineage_by_state[t].values() if gid in own_gen_ids)
            own_units = own_units_per_turn[t]
            capable = sum(1 for unit in own_units if int(unit["hp"]) >= 1)
            servicing_series.append(
                {
                    "turn": t,
                    "live_own_crops": live_own_crops,
                    "capable_own_workers": capable,
                    "total_own_workers": len(own_units),
                    "ratio": (live_own_crops / capable) if capable else None,
                }
            )

        trained_specs = [
            {
                "ordinal": event["ordinal"],
                "turn": event["turn"],
                "harvest_power": int(event["spec"][2]),
            }
            for event in analyses[actor]["training_events"]
        ]

        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": actor_id,
            "cohort": cohort,
            "pseudo": pseudo,
            "seat": actor,
            "turns": usable,
            "margin": margin,
            "won": won,
            "final_workers": 1 + len(trained_specs),
            "trained_specs": trained_specs,
            "crops": crops,
            "servicing_series": servicing_series,
            "integrity": {
                "unknown_diff_updates": unknown,
                "unknown_births": quality.get("unknown_births", 0),
                "ambiguous_births": quality.get("ambiguous_births", 0),
                "missing_live_generations": quality.get("missing_live_generations", 0),
                "missing_worker_ordinals": quality.get("missing_worker_ordinals", 0),
                "lineage_consistent_across_seats": lineage_consistent,
                "generation_keys_consistent_across_seats": generation_keys_consistent,
                "disappearance_unattributed": disappearance_unattributed,
                "generations_without_alive_turn": generations_without_alive_turn,
                "non_contiguous_lineage": non_contiguous_lineage,
            },
        }
    except Exception as exc:  # noqa: BLE001 -- keep a complete sweep; one bad game shouldn't abort it
        return {
            "ok": False,
            "game_id": game_id,
            "agent_id": actor_id,
            "error": f"{type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def mean(values):
    selected = [value for value in values if value is not None]
    return statistics.mean(selected) if selected else None


def median(values):
    selected = [value for value in values if value is not None]
    return statistics.median(selected) if selected else None


def quantiles(values, n=4):
    selected = sorted(value for value in values if value is not None)
    if len(selected) < 2:
        return None
    return statistics.quantiles(selected, n=n)


def fate_value(crop: dict) -> dict:
    fate = crop["fate"]
    if fate == "harvested_by_owner":
        fruit = crop["own_fruit_harvested"]
        return {"fruit_units": fruit, "wood_units": 0, "score_equivalent": fruit}
    if fate == "harvested_by_opponent":
        fruit = crop["opp_fruit_harvested"]
        return {"fruit_units": fruit, "wood_units": 0, "score_equivalent": fruit}
    if fate == "chopped_by_owner":
        wood = crop["own_wood_from_chops"]
        return {"fruit_units": 0, "wood_units": wood, "score_equivalent": 4 * wood}
    if fate == "chopped_by_opponent":
        wood = crop["opp_wood_from_chops"]
        return {"fruit_units": 0, "wood_units": wood, "score_equivalent": 4 * wood}
    return {"fruit_units": 0, "wood_units": 0, "score_equivalent": 0}


def fate_summary(occurrences: list[dict]) -> dict:
    crops = [crop for occ in occurrences for crop in occ["crops"]]
    total = len(crops)
    counts = Counter(crop["fate"] for crop in crops)
    per_fate = {}
    for name in FATES:
        selected = [crop for crop in crops if crop["fate"] == name]
        values = [fate_value(crop) for crop in selected]
        per_fate[name] = {
            "count": len(selected),
            "rate": ratio(len(selected), total),
            "total_fruit_units": sum(row["fruit_units"] for row in values),
            "total_wood_units": sum(row["wood_units"] for row in values),
            "total_score_equivalent": sum(row["score_equivalent"] for row in values),
            "mean_score_equivalent_per_crop": mean(row["score_equivalent"] for row in values)
            if values
            else None,
        }
    return {
        "games": len(occurrences),
        "crops": total,
        "crops_per_game": ratio(total, len(occurrences)),
        "counts": dict(sorted(counts.items())),
        "by_fate": per_fate,
    }


def mother_summary(occurrences: list[dict]) -> dict:
    """Resident-only: fate breakdown restricted to orchard-mother candidate cells."""

    crops = [crop for occ in occurrences for crop in occ["crops"] if crop["is_mother_candidate"]]
    per_game_counts = Counter()
    for occ in occurrences:
        per_game_counts[
            sum(1 for crop in occ["crops"] if crop["is_mother_candidate"])
        ] += 1
    fate_counts = Counter(crop["fate"] for crop in crops)
    return {
        "games": len(occurrences),
        "candidate_crops": len(crops),
        "games_with_candidate_count_histogram": dict(sorted(per_game_counts.items())),
        "fate_counts": dict(sorted(fate_counts.items())),
        "never_harvested_candidates": [
            {
                "cell": crop["cell"],
                "birth_turn": crop["birth_turn"],
                "fate": crop["fate"],
                "alive_at_end": crop["alive_at_end"],
            }
            for crop in crops
            if crop["fate"] not in ("harvested_by_owner", "harvested_by_opponent")
        ],
    }


def expiry_summary(occurrences: list[dict]) -> dict:
    runs = [
        {**run, "kind": crop["kind"], "is_mother_candidate": crop["is_mother_candidate"]}
        for occ in occurrences
        for crop in occ["crops"]
        for run in crop["ripe_runs"]
    ]
    serviced = [row for row in runs if row["serviced"]]
    expired = [row for row in runs if not row["serviced"]]
    expired_non_mother = [row for row in expired if not row["is_mother_candidate"]]
    return {
        "ripe_runs_total": len(runs),
        "serviced_by_harvest": len(serviced),
        "expired_unserviced": len(expired),
        "expired_unserviced_rate": ratio(len(expired), len(runs)),
        "expired_end_reason_counts": dict(sorted(Counter(row["end_reason"] for row in expired).items())),
        "expired_capable_owner_worker_ever_in_range_rate": ratio(
            sum(row["capable_owner_worker_ever_in_range"] for row in expired), len(expired)
        ),
        "expired_duration_turns": {
            "mean": mean(row["duration"] for row in expired),
            "median": median(row["duration"] for row in expired),
            "quartiles": quantiles([row["duration"] for row in expired]),
        },
        "expired_excluding_mother_candidates": {
            "count": len(expired_non_mother),
            "rate_of_all_runs": ratio(len(expired_non_mother), len(runs)),
            "capable_owner_worker_ever_in_range_rate": ratio(
                sum(row["capable_owner_worker_ever_in_range"] for row in expired_non_mother),
                len(expired_non_mother),
            ),
            "duration_turns_mean": mean(row["duration"] for row in expired_non_mother),
            "duration_turns_median": median(row["duration"] for row in expired_non_mother),
        },
    }


def servicing_ratio_summary(occurrences: list[dict]) -> dict:
    by_turn = defaultdict(list)
    zero_capable_by_turn = defaultdict(list)
    for occ in occurrences:
        for sample in occ["servicing_series"]:
            by_turn[sample["turn"]].append(sample["ratio"])
            zero_capable_by_turn[sample["turn"]].append(sample["capable_own_workers"] == 0)
    per_turn = {}
    for turn in CHECKPOINT_TURNS:
        samples = by_turn.get(turn, [])
        if not samples:
            continue
        defined = [value for value in samples if value is not None]
        per_turn[str(turn)] = {
            "games_sampled": len(samples),
            "zero_capable_worker_rate": ratio(sum(zero_capable_by_turn[turn]), len(samples)),
            "defined_ratio_samples": len(defined),
            "mean": mean(defined),
            "median": median(defined),
            "quartiles": quantiles(defined),
            "max": max(defined) if defined else None,
        }
    return {"per_turn": per_turn}


def harvest_power_summary(occurrences: list[dict]) -> dict:
    trained = [spec for occ in occurrences for spec in occ["trained_specs"]]
    zero = sum(1 for spec in trained if spec["harvest_power"] == 0)
    return {
        "trained_workers": len(trained),
        "trained_with_harvest_power_zero": zero,
        "trained_with_harvest_power_zero_rate": ratio(zero, len(trained)),
        "harvest_power_value_counts": dict(
            sorted(Counter(spec["harvest_power"] for spec in trained).items())
        ),
    }


def integrity_summary(all_results: list[dict]) -> dict:
    ok = [row for row in all_results if row["ok"]]
    return {
        "occurrences_ok": len(ok),
        "occurrences_failed": len(all_results) - len(ok),
        "zero_unknown_diff_updates": sum(row["integrity"]["unknown_diff_updates"] for row in ok),
        "zero_unknown_births": sum(row["integrity"]["unknown_births"] for row in ok),
        "zero_ambiguous_births": sum(row["integrity"]["ambiguous_births"] for row in ok),
        "zero_missing_live_generations": sum(
            row["integrity"]["missing_live_generations"] for row in ok
        ),
        "zero_missing_worker_ordinals": sum(
            row["integrity"]["missing_worker_ordinals"] for row in ok
        ),
        "all_lineage_consistent_across_seats": all(
            row["integrity"]["lineage_consistent_across_seats"] for row in ok
        ),
        "all_generation_keys_consistent_across_seats": all(
            row["integrity"]["generation_keys_consistent_across_seats"] for row in ok
        ),
        "zero_disappearance_unattributed": sum(
            row["integrity"]["disappearance_unattributed"] for row in ok
        ),
        "zero_generations_without_alive_turn": sum(
            row["integrity"]["generations_without_alive_turn"] for row in ok
        ),
        "zero_non_contiguous_lineage": sum(row["integrity"]["non_contiguous_lineage"] for row in ok),
    }


def outcome_correlation(occurrences: list[dict], turn: int = 100) -> dict:
    rows = []
    for occ in occurrences:
        sample = next((row for row in occ["servicing_series"] if row["turn"] == turn), None)
        if sample is None:
            continue
        rows.append({"won": occ["won"], "margin": occ["margin"], "ratio": sample["ratio"], "zero_capable": sample["capable_own_workers"] == 0})
    defined = [row for row in rows if row["ratio"] is not None]
    wins = [row for row in defined if row["won"]]
    losses = [row for row in defined if not row["won"]]
    correlation = None
    if len(defined) >= 3:
        ratios = [row["ratio"] for row in defined]
        margins = [row["margin"] for row in defined]
        if len(set(ratios)) > 1 and len(set(margins)) > 1:
            correlation = statistics.correlation(ratios, margins)
    return {
        "caveat": "descriptive association only, not a causal claim (small n, single cut, confounded by game length/opponent)",
        "turn": turn,
        "games_with_sample": len(rows),
        "games_with_defined_ratio": len(defined),
        "zero_capable_worker_rate_at_turn": ratio(sum(row["zero_capable"] for row in rows), len(rows)),
        "mean_ratio_wins": mean(row["ratio"] for row in wins),
        "median_ratio_wins": median(row["ratio"] for row in wins),
        "mean_ratio_losses": mean(row["ratio"] for row in losses),
        "median_ratio_losses": median(row["ratio"] for row in losses),
        "pearson_correlation_ratio_vs_margin": correlation,
    }


def interaction_totals(occurrences: list[dict]) -> dict:
    """Realized fruit/wood summed across EVERY owner-planted crop regardless of its
    (mutually-exclusive, dominant-interaction) fate bucket.  ``fate_summary``'s
    ``by_fate`` values only count value within the bucket that "won" the fate
    priority order (e.g. a crop the owner harvested once and the opponent later
    finished off for wood is entirely a ``harvested_by_owner`` crop there, so its
    opponent-chop wood would otherwise go uncounted) -- this reports the true totals
    so the theft-limited hypothesis can be quantified on its own terms, comparable
    directly to the CONSTRAINTS-recorded 2.32 wood/game own-crop leakage figure.
    """

    crops = [crop for occ in occurrences for crop in occ["crops"]]
    games = len(occurrences)
    totals = {
        "own_fruit_harvested": sum(crop["own_fruit_harvested"] for crop in crops),
        "opp_fruit_harvested": sum(crop["opp_fruit_harvested"] for crop in crops),
        "own_wood_from_chops": sum(crop["own_wood_from_chops"] for crop in crops),
        "opp_wood_from_chops": sum(crop["opp_wood_from_chops"] for crop in crops),
    }
    return {
        "games": games,
        "totals": totals,
        "per_game": {key: ratio(value, games) for key, value in totals.items()},
    }


def build_cohort_report(occurrences: list[dict]) -> dict:
    return {
        "games": len(occurrences),
        "fate": fate_summary(occurrences),
        "interaction_totals": interaction_totals(occurrences),
        "expiry": expiry_summary(occurrences),
        "servicing_ratio": servicing_ratio_summary(occurrences),
        "harvest_power": harvest_power_summary(occurrences),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resident-limit", type=int, default=0, help="0 = every resident game")
    parser.add_argument("--top5-count", type=int, default=5)
    parser.add_argument("--top5-games-per-agent", type=int, default=20, help="0 = every game")
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")

    games_index = load_games_index()
    top_cohort = top_agents(args.top5_count)
    occurrences = select_occurrences(
        games_index, RESIDENT_AGENT_ID, top_cohort, args.top5_games_per_agent, args.resident_limit
    )

    if args.jobs == 1:
        results = [analyze_occurrence(*row) for row in occurrences]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            results = list(
                executor.map(
                    analyze_occurrence,
                    [row[0] for row in occurrences],
                    [row[1] for row in occurrences],
                    [row[2] for row in occurrences],
                    [row[3] for row in occurrences],
                    [row[4] for row in occurrences],
                    chunksize=2,
                )
            )

    failed = [row for row in results if not row["ok"]]
    resident_occ = [row for row in results if row["ok"] and row["cohort"] == "resident"]
    top5_occ = [row for row in results if row["ok"] and row["cohort"] == "top5"]

    report = {
        "schema": 1,
        "scope": "read-only B3.7 crop-fate census; no arena writes, no strategy changes",
        "resident_agent_id": RESIDENT_AGENT_ID,
        "top5_agents": [
            {"agent_id": int(row["agentId"]), "pseudo": row["pseudo"], "rank": row.get("rank")}
            for row in top_cohort
        ],
        "population": {
            "resident_games_requested": sum(1 for row in occurrences if row[3] == "resident"),
            "resident_games_ok": len(resident_occ),
            "top5_games_requested": sum(1 for row in occurrences if row[3] == "top5"),
            "top5_games_ok": len(top5_occ),
            "failure_count": len(failed),
            "failures": failed[:50],
        },
        "integrity": integrity_summary(results),
        "resident": build_cohort_report(resident_occ),
        "top5": build_cohort_report(top5_occ),
        "resident_mother_orchard": mother_summary(resident_occ),
        "outcome_correlation_resident_t100": outcome_correlation(resident_occ, turn=100),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(
        f"resident games ok: {len(resident_occ)} ({report['resident']['fate']['crops']} crops), "
        f"top5 games ok: {len(top5_occ)} ({report['top5']['fate']['crops']} crops), "
        f"failures: {len(failed)}"
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
