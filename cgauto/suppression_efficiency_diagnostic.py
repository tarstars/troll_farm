#!/usr/bin/env python3
"""B4.6 -- suppression-efficiency diagnostic (read-only research scout).

Decomposes the two remaining execution-class gaps B4.4 found and left unexplained:
the resident realises **0.3142 wood per successful CHOP action** against the STRONG
peer cohort's **0.4271** (PEER/WEAK 0.4571), and contacts (chops or harvests, ever)
only **41.1%** of the opponent's own planted crop generations across their lifetime,
against STRONG's **46.6%** (PEER/WEAK 25.3%). Those exact pooled figures come from
``peer_cohort_analysis.py``'s ``score_production``/``production_suppression`` blocks
(full B4.4 cohort: 204 resident + 2,024 STRONG + 559 PEER/WEAK occurrences) and are
reused here verbatim as ground truth -- see ``load_b44_ground_truth`` below -- rather
than recomputed, because this script's own heavy per-chop pass runs over a bounded
per-agent game cap (``GAMES_PER_AGENT_CAP``) for tractability. This script's own
top-line numbers are reported ALONGSIDE that ground truth as a consistency check.

Every other production route this programme tried is now closed by causal experiment
(D173a/b harvest capability, D174a mining/scaling, D175a early planting -- all net
negative or capped) -- this is the last item on B4.6 in ``docs/BACKLOG.md``, and the
one lead that plays *to* the architecture's actual strength (denial/wood) rather than
against it.

Reuse, not reinvention (per the B4.6 brief):

- ``cgauto.waste_sweep.decode_game``/``decode_game_for_agent``/``agent_game_ids`` --
  the standing agent-agnostic decode layer. ``DecodedGame.states[t]["plants"]``
  already carries ``size``/``health`` per tree (confirmed against
  ``cgauto/replay_state.py``'s ``DiffDecoder``) -- exactly the "tree maturity at chop
  time" signal the brief asks for; no new decoder was written.
- ``cgauto.analyze_d101a_production_suppression.reconstruct_generation_actions`` --
  the validated (dual-implementation cross-checked against d95a's
  ``reconstruct_actions``, 100% ``event_reference_compatible``/
  ``lineage_reference_compatible`` in every prior run, including B4.4's own
  2,787-occurrence heavy pass) per-cell crop-generation lineage tracker: birth turn,
  kind, origin (actor/opponent/natural), and a stable generation id every chop/harvest
  event can be joined against. Called as-is; this script only ADDS what it doesn't
  already compute -- tree size/health at chop time, the acting unit's free capacity,
  same-turn own-unit contention, and each generation's eventual fate/feller -- via one
  extra pass over the same decoded ``states``/``trajectory`` (see
  ``analyze_chops_for_occurrence``).
- ``cgauto.peer_cohort_analysis.build_cohort`` -- the frozen STRONG/PEER-WEAK cohort
  selection (Legend, >=10 games, mean roster within 0.2 of the resident's own 2.000).
- ``cgauto.top_player_opening_analysis.assigned_unit_commands``/``player_commands``/
  ``bfs``/``adjacent`` -- turn-string -> unit-id-keyed command resolution and map
  geometry, reused for the bilateral (both players') per-turn command lookups the
  generation-fate pass needs, and for the chop-target-scoring reconstruction.
- ``cgauto.roster_outcome_pricing`` -- corpus loading, ``is_clean``, bootstrap/CI.

Root cause, verified by direct source trace (``git show HEAD:rust/src/bin/
yamo_orchard_live.rs``), not assumed:

- The deployed chop-target scorer is reached ``main()`` (:6008) -> ``SecureOrchardBot::
  new()`` (:3824) -> ``with_policy`` (:4052) -> inner ``YamoBot::
  tuned_carry_regeneration_transit_idle_harvest`` (:1691) for the roster/opening
  policy, and every unit's per-turn candidates come from ``YamoBot::main_candidates``
  (:3084) -> ``YamoBot::yamo_chop_candidates`` (:2863-2917) -> ``MoisanBot::
  chop_candidates`` (:1050-1118). The score is ``1000.0 * wood / turns`` where
  ``turns = travel_turns + chop_turns + return_turns + 1`` (a full round trip: travel
  to the tree, turns to fell it accounting for predicted growth/opponent contest, and
  the walk back to a door to bank) and **``wood = final_size.min(unit.free_capacity())``**
  -- the score caps a tree's perceived wood value at the ACTING UNIT's own current free
  capacity, not the tree's true potential yield.
- ``yamo_chop_candidates``'s only value-add over the bare Moisan scorer is dead: the
  ``opponent_eta_penalty`` risk term short-circuits (``if opponent_eta_penalty <= 0 {
  return candidates; }`` at :2874) because the field is provably 0 on every path
  ``main()`` reaches -- independently re-traced here end to end
  (``SecureOrchardBot::new()`` :3824 -> ``YamoBot::
  tuned_carry_regeneration_transit_idle_harvest`` :1691 -> ``...transit`` :1685 ->
  ``...unblocked`` :1679 -> ``regeneration_unblocked_with_policy`` :1723 ->
  ``regeneration_unblocked_with_routing(opening_policy, 0)`` :1724, a literal 0, never
  overridden downstream at :1742) -- matching and confirming B3.6's prior finding.
- ``sim/engine.py::apply_chop`` (:284-309) confirms the mechanism this scoring choice
  is downstream of: when a tree dies, wood is handed out to choppers WITH FREE
  CAPACITY up to the tree's ``size`` (capped at ``MAX_SIZE=4``); any of that ``size``
  beyond what the participating choppers can carry is destroyed, not banked by anyone.
  A solo capacity-1 starter chopper (``Stats::STARTER_GOLD``: ``carry_capacity: 1``)
  felling any tree of size >= 2 provably wastes >= 50% of that tree's wood, structurally
  -- confirmed independently, on an earlier resident vintage but the identical engine
  mechanic, by the standing controlled-game probe ``data/panels/
  top5-wood-conversion-telemetry.json`` (``wood_conversion_field_probe.py``):
  95.1% (408/429 units) of all wood lost to carry overflow was ``wood_unavoidable_at_
  capacity`` (the chopper's own trained ``cc`` stat too small for the tree, no amount
  of banking discipline could have helped) versus 2.3% ``wood_recoverable_by_banking``.

CLI usage::

    .venv/bin/python cgauto/suppression_efficiency_diagnostic.py \\
        --output <path/to/report.json> [--jobs 12] [--games-per-agent-cap 30] \\
        [--reconstruction-examples 5]
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.waste_sweep import (  # noqa: E402
    RESIDENT_AGENT_ID,
    agent_game_ids,
    decode_game,
    decode_game_for_agent,
    manhattan,
)
from cgauto.analyze_d101a_production_suppression import (  # noqa: E402
    reconstruct_generation_actions,
)
from cgauto.top_player_opening_analysis import (  # noqa: E402
    adjacent,
    assigned_unit_commands,
    bfs,
    player_commands,
)
from cgauto.peer_cohort_analysis import build_cohort  # noqa: E402
from cgauto.roster_outcome_pricing import (  # noqa: E402
    is_clean,
    latest_leaderboard_path,
    load_games,
    load_leaderboard,
)

REPO = Path(__file__).resolve().parent.parent
SCRATCH_DIR = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/b87b2a84-2e59-408b-9c9e-ecb58289a6d1/scratchpad"
)
DEFAULT_OUTPUT = SCRATCH_DIR / "b46-suppression-efficiency-data.json"
B44_DATA_PATH = SCRATCH_DIR / "b44-peer-cohort-data.json"

GAMES_PER_AGENT_CAP = 30  # tractability bound for the STRONG/PEER-WEAK heavy pass;
    # the resident itself is always run over its FULL corpus (no cap). b44's own
    # full-cohort pooled wood/chop and contact-coverage figures are reused verbatim
    # as ground truth alongside this script's own (capped-sample) recomputation.
DEFAULT_JOBS = 12
REACHABLE_ETA_THRESHOLD = 20  # matches recent_resident_field_census.crop_provenance's
    # existing "reachable_within_20_at_birth" convention
DEFAULT_RECONSTRUCTION_EXAMPLES = 5
WOOD_POINTS = 4  # score.rs: score = sum(fruit) + 4*wood; matches sim/engine.py

# ---------------------------------------------------------------------------
# Game constants, ported from rust/src/bin/yamo_orchard_live.rs (game::rules) for
# the chop-target-scoring reconstruction in Part 4.  Kept minimal and exactly
# matching the source cited in this module's docstring; not reused from elsewhere
# because no existing Python module ports the live scorer.
# ---------------------------------------------------------------------------
TOTAL_TURNS = 300
MAX_SIZE = 4
TREE_HEALTH_PARAMS = {"PLUM": (4, 2), "LEMON": (4, 2), "APPLE": (8, 3), "BANANA": (2, 1)}
PLANT_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}


def tree_health(kind: str, size: int) -> int:
    base, slope = TREE_HEALTH_PARAMS[kind]
    return base + slope * size


def effective_cooldown(kind: str, near_water: bool) -> int:
    return PLANT_COOLDOWN[kind] - (WATER_BOOST[kind] if near_water else 0)


def ceil_div(a: int, b: int) -> int:
    return 10_000 if b <= 0 else -(-a // b)


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


# ---------------------------------------------------------------------------
# Part 0: ground truth + cohort selection
# ---------------------------------------------------------------------------


def load_b44_ground_truth() -> dict | None:
    """Reuse B4.4's already-computed, full-cohort pooled figures verbatim (no
    recomputation): wood/chop and opponent-crop contact-coverage for resident/
    STRONG/PEER-WEAK, plus the exact STRONG/PEER-WEAK agent-id lists, so this
    script's own (capped-sample) cohort can be checked for consistency against it."""

    if not B44_DATA_PATH.exists():
        return None
    data = json.loads(B44_DATA_PATH.read_text())
    sp = data["score_production"]
    ps = data["production_suppression"]

    def wood_per_chop(row):
        wcpg = row["wood_collected_per_game"]["mean"]
        clpg = row["chops_landed_per_game"]["mean"]
        return wcpg / clpg if clpg else None

    return {
        "generated_at": data["generated_at"],
        "leaderboard_snapshot": data["leaderboard_snapshot"],
        "wood_per_chop_games_jsonl_definition": {
            group: {
                "wood_collected_per_game": sp[group]["wood_collected_per_game"]["mean"],
                "chops_landed_per_game_NONLETHAL_ONLY": sp[group]["chops_landed_per_game"]["mean"],
                "ratio": wood_per_chop(sp[group]),
            }
            for group in ("resident", "strong", "peer_weak")
        },
        "opponent_contact_coverage": {
            group: ps[group]["opponent_generations"]["pooled_contact_coverage"]
            for group in ("resident", "strong", "peer_weak")
        },
        "strong_agent_ids": sorted(row["agent_id"] for row in data["cohort"]["strong"]),
        "peer_weak_agent_ids": sorted(row["agent_id"] for row in data["cohort"]["peer_weak"]),
        "note": (
            "games.jsonl's effects.chops_landed (data/scripts/parse.py:206-207) is an "
            "`elif` branch that only fires on 'damaged a tree' referee messages -- a "
            "felling ('collected N WOOD') turn is counted under effects.collected_WOOD "
            "(a wood AMOUNT) and never increments chops_landed (an action COUNT). So "
            "this 'official' wood/chop ratio's denominator is NON-FELLING chop actions "
            "only, not all successful chop actions. This script's own wood_per_chop "
            "(Part 1) uses a clean all-successful-chops denominator instead and reports "
            "both for transparency -- see 'reconciliation' in the output."
        ),
    }


def select_cohort() -> dict:
    leaderboard = load_leaderboard(latest_leaderboard_path())
    all_games = load_games()
    clean_games = [game for game in all_games if is_clean(game)]
    cohort = build_cohort(clean_games, leaderboard)
    return {
        "cohort": cohort,
        "strong_ids": sorted(row["agent_id"] for row in cohort["strong"]),
        "peer_ids": sorted(row["agent_id"] for row in cohort["peer_weak"]),
        "leaderboard_path": str(latest_leaderboard_path().relative_to(REPO)),
    }


# ---------------------------------------------------------------------------
# Part 1: per-CHOP-action decomposition
# ---------------------------------------------------------------------------


def analyze_chops_for_occurrence(game_id: int, actor: int, states: list[dict], trajectory: list[dict]):
    """Per-CHOP-action decomposition for one (game, actor-seat) occurrence.  See the
    module docstring for what is reused vs added here.  Returns
    ``(chop_records, opponent_generation_rows, quality)``.
    """

    events, generations, lineage_by_state, quality = reconstruct_generation_actions(
        states, trajectory, actor, {}
    )
    opponent = 1 - actor
    usable = min(len(states) - 1, len(trajectory))

    events_by_turn: dict[int, list] = defaultdict(list)
    events_by_generation: dict[str, list] = defaultdict(list)
    for event in events:
        events_by_turn[event["turn"]].append(event)
        if event["target_generation"] is not None:
            events_by_generation[event["target_generation"]].append(event)

    fate = {
        gid: {
            "birth_turn": meta["birth_turn"],
            "cell": tuple(meta["cell"]),
            "kind": meta["kind"],
            "origin": meta["origin"],
            "death_turn": None,
            "felled_by": "survived_to_end",
            "size_at_death": None,
            "opponent_co_chopped": False,
            "contacted_by_actor": any(
                e["verb"] in ("CHOP", "HARVEST") for e in events_by_generation.get(gid, [])
            ),
            "first_contact_turn": min(
                (
                    e["turn"]
                    for e in events_by_generation.get(gid, [])
                    if e["verb"] in ("CHOP", "HARVEST")
                ),
                default=None,
            ),
        }
        for gid, meta in generations.items()
    }

    chop_records = []

    for turn in range(1, usable + 1):
        before = states[turn - 1]
        before_plants = {(p["x"], p["y"]): p for p in before["plants"]}
        before_units = {u["id"]: u for u in before["units"]}
        before_active = lineage_by_state[turn - 1]
        after_active = lineage_by_state[turn]

        assigned = {
            player: assigned_unit_commands(
                player_commands(trajectory[turn - 1], player),
                [u for u in before["units"] if u["player"] == player],
            )
            for player in (0, 1)
        }
        choppers_by_cell = {0: defaultdict(list), 1: defaultdict(list)}
        for player in (0, 1):
            for unit_id, command in assigned[player].items():
                fields = command.split()
                if fields and fields[0].upper() == "CHOP":
                    unit = before_units.get(unit_id)
                    if unit is not None:
                        choppers_by_cell[player][(unit["x"], unit["y"])].append(unit_id)

        # -- generation fate: any cell whose active generation id changed this turn --
        for cell, gid in before_active.items():
            if after_active.get(cell) == gid:
                continue
            record = fate.get(gid)
            if record is None or record["death_turn"] is not None:
                continue
            record["death_turn"] = turn
            plant = before_plants.get(cell)
            record["size_at_death"] = plant["size"] if plant else None
            actor_hit = bool(choppers_by_cell[actor].get(cell))
            opponent_hit = bool(choppers_by_cell[opponent].get(cell))
            record["opponent_co_chopped"] = actor_hit and opponent_hit
            if actor_hit:
                record["felled_by"] = "actor"
            elif opponent_hit:
                record["felled_by"] = "opponent"
            else:
                record["felled_by"] = "unaccounted"  # decode edge case; expect ~0

        # -- augment this turn's actor CHOP events --
        turn_chop_events = [e for e in events_by_turn.get(turn, []) if e["verb"] == "CHOP"]
        if not turn_chop_events:
            continue
        contention: Counter = Counter()
        for event in turn_chop_events:
            unit = before_units.get(event["unit_id"])
            if unit is not None:
                contention[(unit["x"], unit["y"])] += 1
        for event in turn_chop_events:
            unit = before_units.get(event["unit_id"])
            if unit is None:
                continue
            cell = (unit["x"], unit["y"])
            plant = before_plants.get(cell)
            free_capacity = unit["cc"] - sum(unit["carry"])
            chop_records.append(
                {
                    "game_id": game_id,
                    "turn": turn,
                    "unit_id": event["unit_id"],
                    "cell": cell,
                    "landed": event["success"],
                    "wood_gained": event["gained"].get("WOOD", 0),
                    "target_origin": event["target_origin"] or "unknown",
                    "target_generation": event["target_generation"],
                    "kind": plant["type"] if plant else event["target_kind"],
                    "size_before": plant["size"] if plant else None,
                    "health_before": plant["health"] if plant else None,
                    "unit_cc": unit["cc"],
                    "free_capacity_before": free_capacity,
                    "own_contention": contention[cell],
                }
            )

    for record in chop_records:
        gid = record["target_generation"]
        info = fate.get(gid) if gid else None
        if info is None:
            record["felled_this_turn"] = None
            record["eventual_feller"] = None
        else:
            record["felled_this_turn"] = (
                info["death_turn"] == record["turn"] and info["felled_by"] == "actor"
            )
            record["eventual_feller"] = info["felled_by"]
            record["size_at_death"] = info["size_at_death"]

    opponent_generation_rows = [
        {
            "gid": gid,
            "cell": list(info["cell"]),
            "kind": info["kind"],
            "birth_turn": info["birth_turn"],
            "contacted": info["contacted_by_actor"],
            "first_contact_turn": info["first_contact_turn"],
        }
        for gid, info in fate.items()
        if info["origin"] == "opponent"
    ]

    return chop_records, opponent_generation_rows, quality


def opponent_generation_reachability(game, opponent_generation_rows: list[dict]) -> list[dict]:
    """Add a BFS-based 'our_eta_at_birth' (how fast the actor could in principle reach
    a just-planted opponent crop) to each opponent-origin generation, for the
    selection-vs-reachability split in Part 2.  Mirrors ``recent_resident_field_census
    .crop_provenance``'s ``our_eta_at_birth``/``unit_eta`` convention (best ETA over the
    actor's own units, BFS distance / that unit's movement speed) but computed directly
    against this script's own generation/lineage pass for methodological consistency."""

    walkable = game.board["walkable"]
    out = []
    for row in opponent_generation_rows:
        birth_turn = row["birth_turn"]
        eta = None
        if birth_turn < len(game.states):
            state = game.states[birth_turn]
            actor_units = [u for u in state["units"] if u["player"] == game.me]
            cell = tuple(row["cell"])
            for unit in actor_units:
                distances = bfs(walkable, [(unit["x"], unit["y"])])
                d = distances.get(cell)
                if d is None:
                    continue
                e = ceil_div(d, max(unit["ms"], 1))
                if eta is None or e < eta:
                    eta = e
        out.append(
            {
                **row,
                "eta_at_birth": eta,
                "reachable": eta is not None and eta <= REACHABLE_ETA_THRESHOLD,
            }
        )
    return out


def move_chop_ratio_for_game(game) -> dict:
    """Travel-overhead proxy: for units that ever CHOP at least once this game, the
    total MOVE vs CHOP commands they issue across their whole game-life.  A coarse
    'chop utilization' signal, not a per-tree travel-time measurement -- see Part 1's
    'travel_overhead' section in the report for the caveat."""

    usable = min(len(game.states) - 1, len(game.trajectory))
    per_turn_assigned = []
    chopper_ids: set[int] = set()
    for turn in range(1, usable + 1):
        before = game.states[turn - 1]
        my_units = [u for u in before["units"] if u["player"] == game.me]
        assigned = assigned_unit_commands(player_commands(game.trajectory[turn - 1], game.me), my_units)
        per_turn_assigned.append(assigned)
        for unit_id, command in assigned.items():
            fields = command.split()
            if fields and fields[0].upper() == "CHOP":
                chopper_ids.add(unit_id)
    move_count = 0
    chop_count = 0
    for assigned in per_turn_assigned:
        for unit_id, command in assigned.items():
            if unit_id not in chopper_ids:
                continue
            fields = command.split()
            verb = fields[0].upper() if fields else "WAIT"
            if verb == "MOVE":
                move_count += 1
            elif verb == "CHOP":
                chop_count += 1
    return {"move_count": move_count, "chop_count": chop_count, "chopper_units": len(chopper_ids)}


# ---------------------------------------------------------------------------
# Part 4 (scoring reconstruction) helper functions -- ported game mechanics
# ---------------------------------------------------------------------------


def focus_type(board: dict, state: dict) -> str:
    """Port of MoisanBot::focus_type (:749-765): the one-shot, memoized-at-turn-1
    choice of which of LEMON/PLUM is (by summed BFS distance from our own door
    cells) closer to home -- used only by the live urgency-chase bonus term."""

    own_shack = board["shacks"][0]
    starts = [c for c in adjacent(own_shack) if c in board["walkable"]]
    dist = bfs(board["walkable"], starts)
    best_kind, best_total = None, None
    for kind in ("LEMON", "PLUM"):
        total = sum(
            dist.get((p["x"], p["y"]), 10_000) for p in state["plants"] if p["type"] == kind
        )
        if best_total is None or total < best_total:
            best_total, best_kind = total, kind
    return best_kind or "LEMON"


def predict_opp_chop(state: dict, plant: dict, opponent_seat: int) -> int:
    """Port of MoisanBot::predicted_opp_chop (:965-980)."""

    cell = (plant["x"], plant["y"])
    on_tree = sum(
        u["chop"] for u in state["units"] if u["player"] == opponent_seat and (u["x"], u["y"]) == cell
    )
    if on_tree > 0:
        return on_tree
    expected = tree_health(plant["type"], plant["size"])
    return 1 if plant["health"] < expected else 0


def predict_tree(state: dict, plant: dict, turns: int, opponent_seat: int, near_water: bool):
    """Port of MoisanBot::predict_tree (:981-1013), fruits tracking dropped (fruits
    never feed back into health/size, so it cannot change the wood-yield prediction;
    see this module's docstring)."""

    size, health, cooldown = plant["size"], plant["health"], plant["cooldown"]
    opp_chop = predict_opp_chop(state, plant, opponent_seat)
    for _ in range(turns):
        if opp_chop > 0:
            health -= opp_chop
            if health <= 0:
                return None
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and health > 0 and size < MAX_SIZE:
            size += 1
            health += TREE_HEALTH_PARAMS[plant["type"]][1]
            cooldown = effective_cooldown(plant["type"], near_water)
    return {"size": size, "health": health, "cooldown": cooldown}


def chop_outcome(plant: dict, predicted: dict, chop_power: int, near_water: bool):
    """Port of MoisanBot::chop_outcome (:1014-1042)."""

    if chop_power <= 0:
        return None
    cooldown_reset = effective_cooldown(plant["type"], near_water)
    growth_health = TREE_HEALTH_PARAMS[plant["type"]][1]
    size, health, cooldown = predicted["size"], predicted["health"], predicted["cooldown"]
    for turns in range(1, 101):
        health -= chop_power
        if health <= 0:
            return turns, size
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and size < MAX_SIZE:
            size += 1
            health += growth_health
            cooldown = cooldown_reset
    return None


def score_chop_candidates(
    state: dict,
    board: dict,
    unit: dict,
    opponent_seat: int,
    type_to_cut: str,
    decision_turn: int,
    near_water_cells: set,
) -> list[dict]:
    """Port of MoisanBot::chop_candidates (:1050-1118), the deployed scorer (reached
    via yamo_chop_candidates with opponent_eta_penalty provably 0 and protected_tree
    provably None on the live path -- see module docstring), scoped to ONE unit."""

    walkable = board["walkable"]
    unit_cell = (unit["x"], unit["y"])
    from_unit = bfs(walkable, [unit_cell])
    shack_starts = [c for c in adjacent(board["shacks"][0]) if c in walkable]
    to_shack = bfs(walkable, shack_starts)
    opponent_trolls = sum(1 for u in state["units"] if u["player"] == opponent_seat)
    free_capacity = unit["cc"] - sum(unit["carry"])
    candidates = []
    for plant in state["plants"]:
        if plant["health"] <= 0:
            continue
        cell = (plant["x"], plant["y"])
        if cell not in from_unit:
            continue
        travel_turns = ceil_div(from_unit[cell], max(unit["ms"], 1))
        near_water = cell in near_water_cells
        predicted = predict_tree(state, plant, travel_turns, opponent_seat, near_water)
        if predicted is None or predicted["size"] <= 0 or predicted["health"] <= 0:
            continue
        raw_return = to_shack.get(cell)
        return_turns = (
            ceil_div(raw_return, max(unit["ms"], 1))
            if raw_return is not None
            else ceil_div(manhattan(cell, board["shacks"][0]), max(unit["ms"], 1))
        )
        outcome = chop_outcome(plant, predicted, unit["chop"], near_water)
        if outcome is None:
            continue
        chop_turns, final_size = outcome
        turns = max(1, travel_turns + chop_turns + return_turns + 1)
        if turns > TOTAL_TURNS - decision_turn + 1:
            continue
        wood = min(final_size, free_capacity)
        if wood <= 0:
            continue
        score = 1000.0 * wood / turns
        if plant["type"] == type_to_cut and opponent_trolls <= 2:
            opp_distance = manhattan(cell, board["shacks"][1])
            score += 900.0 / (1 + opp_distance)
        candidates.append(
            {
                "cell": list(cell),
                "kind": plant["type"],
                "score": round(score, 3),
                "predicted_wood": wood,
                "predicted_turns": turns,
                "travel_turns": travel_turns,
                "chop_turns": chop_turns,
                "return_turns": return_turns,
                "final_size": final_size,
                "size_now": plant["size"],
                "health_now": plant["health"],
            }
        )
    candidates.sort(key=lambda c: -c["score"])
    return candidates


def reconstruct_examples(game_ids: list[int], n_examples: int) -> dict:
    """Task item 3: >=N real episode reconstructions (state in -> decision out). For
    each candidate decision turn (an empty-handed, non-carrying resident unit whose
    actual command targets a live tree), replicate chop_candidates for that ONE unit
    against the real decoded state and check whether the top-ranked candidate matches
    the unit's actually-issued command's target cell.  This is a single-unit replica
    of the live scorer (not the full 2-unit joint select() optimizer -- see the
    'scope' note in the returned dict), sufficient to confirm the throughput-formula
    mechanism against real recorded decisions."""

    examples = []
    checked = 0
    matched = 0
    mismatches_sample = []
    games_used = 0
    max_games = max(40, n_examples * 4)
    max_examples_per_game = 2  # forces diversity across games rather than one long streak
    for game_id in game_ids:
        if checked >= max(150, n_examples * 25) or games_used >= max_games:
            break
        try:
            game = decode_game(game_id)
        except Exception:  # noqa: BLE001
            continue
        games_used += 1
        examples_this_game = 0
        board = game.board
        water = board["water"]
        near_water_cells = {c for c in board["walkable"] if any(w in adjacent(c) for w in water)}
        me, opponent = game.me, game.opponent
        kind0 = focus_type(board, game.states[0])
        usable = min(len(game.states) - 1, len(game.trajectory))
        for turn in range(30, min(usable, 250)):
            if examples_this_game >= max_examples_per_game:
                break
            state = game.states[turn - 1]
            my_units = [u for u in state["units"] if u["player"] == me]
            assigned = assigned_unit_commands(player_commands(game.trajectory[turn - 1], me), my_units)
            for unit in my_units:
                if sum(unit["carry"]) > 0:
                    continue
                command = assigned.get(unit["id"])
                if not command:
                    continue
                fields = command.split()
                verb = fields[0].upper() if fields else "WAIT"
                if verb == "CHOP":
                    actual_cell = (unit["x"], unit["y"])
                elif verb == "MOVE" and len(fields) == 4:
                    actual_cell = (int(fields[2]), int(fields[3]))
                else:
                    continue
                plant_here = next(
                    (
                        p
                        for p in state["plants"]
                        if (p["x"], p["y"]) == actual_cell and p["health"] > 0
                    ),
                    None,
                )
                if plant_here is None:
                    continue
                candidates = score_chop_candidates(
                    state, board, unit, opponent, kind0, turn, near_water_cells
                )
                if not candidates:
                    continue
                checked += 1
                top = candidates[0]
                is_match = tuple(top["cell"]) == actual_cell
                if is_match:
                    matched += 1
                    if len(examples) < n_examples and examples_this_game < max_examples_per_game:
                        examples.append(
                            {
                                "game_id": game_id,
                                "turn": turn,
                                "unit_id": unit["id"],
                                "unit_stats": {
                                    "ms": unit["ms"],
                                    "cc": unit["cc"],
                                    "chop": unit["chop"],
                                },
                                "actual_command": command,
                                "actual_cell": list(actual_cell),
                                "top_5_predicted_candidates": candidates[:5],
                            }
                        )
                        examples_this_game += 1
                elif len(mismatches_sample) < 5:
                    mismatches_sample.append(
                        {
                            "game_id": game_id,
                            "turn": turn,
                            "unit_id": unit["id"],
                            "actual_cell": list(actual_cell),
                            "predicted_top_cell": top["cell"],
                            "predicted_top_score": top["score"],
                            "actual_cell_predicted_rank": next(
                                (
                                    index
                                    for index, cand in enumerate(candidates)
                                    if tuple(cand["cell"]) == actual_cell
                                ),
                                None,
                            ),
                        }
                    )
    return {
        "scope": (
            "single-unit replica of MoisanBot::chop_candidates (the deployed scorer); "
            "does not replicate select()'s 2-unit joint pairwise optimization, "
            "bank_candidates, ring_chop_candidates (banana-adjacent to own shack), or "
            "endgame_candidates (turn>275) -- decision turns are restricted to "
            "30<=turn<250, unit carrying nothing, actual command targeting a live tree, "
            "which keeps chop_candidates the dominant/only relevant candidate source "
            "per main_candidates' own dispatch (:3084)."
        ),
        "decision_points_checked": checked,
        "top1_match_count": matched,
        "top1_match_rate": ratio(matched, checked),
        "matched_examples": examples,
        "mismatch_sample": mismatches_sample,
    }


# ---------------------------------------------------------------------------
# Multiprocessing driver
# ---------------------------------------------------------------------------


def _occurrence_worker(task: dict) -> dict:
    game_id = task["game_id"]
    agent_id = task["agent_id"]
    try:
        game = (
            decode_game(game_id)
            if agent_id == RESIDENT_AGENT_ID
            else decode_game_for_agent(game_id, agent_id)
        )
        chop_records, opponent_generation_rows, quality = analyze_chops_for_occurrence(
            game_id, game.me, game.states, game.trajectory
        )
        opponent_generation_rows = opponent_generation_reachability(game, opponent_generation_rows)
        move_chop = move_chop_ratio_for_game(game)
        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": agent_id,
            "cohort": task["cohort"],
            "margin": game.margin,
            "won": game.won,
            "chop_records": chop_records,
            "opponent_generations": opponent_generation_rows,
            "move_chop": move_chop,
            "quality": quality,
        }
    except Exception as exc:  # noqa: BLE001 -- keep a complete audit; one bad game
        # shouldn't abort the sweep
        return {
            "ok": False,
            "game_id": game_id,
            "agent_id": agent_id,
            "cohort": task["cohort"],
            "error": f"{type(exc).__name__}: {exc}",
        }


def build_tasks(strong_ids: list[int], peer_ids: list[int], games_per_agent_cap: int) -> list[dict]:
    tasks = []
    for game_id in agent_game_ids(RESIDENT_AGENT_ID):
        tasks.append({"game_id": game_id, "agent_id": RESIDENT_AGENT_ID, "cohort": "resident"})
    for agent_id in strong_ids:
        for game_id in agent_game_ids(agent_id)[:games_per_agent_cap]:
            tasks.append({"game_id": game_id, "agent_id": agent_id, "cohort": "strong"})
    for agent_id in peer_ids:
        for game_id in agent_game_ids(agent_id)[:games_per_agent_cap]:
            tasks.append({"game_id": game_id, "agent_id": agent_id, "cohort": "peer_weak"})
    return tasks


def run_heavy_pass(tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_occurrence_worker(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_occurrence_worker, tasks, chunksize=2))
    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]
    return ok, failed


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def summarize_cohort_chops(rows: list[dict]) -> dict:
    """The wood/chop decomposition table (task item 1) for one cohort's pooled
    chop_records."""

    records = [record for row in rows for record in row["chop_records"]]
    landed = [r for r in records if r["landed"]]
    n_landed = len(landed)
    total_wood = sum(r["wood_gained"] for r in landed)

    felling = [r for r in landed if r["felled_this_turn"]]
    non_felling = [r for r in landed if not r["felled_this_turn"]]
    non_felling_actor = [r for r in non_felling if r["eventual_feller"] == "actor"]
    non_felling_opponent = [r for r in non_felling if r["eventual_feller"] == "opponent"]
    non_felling_survives = [r for r in non_felling if r["eventual_feller"] == "survived_to_end"]
    non_felling_unaccounted = [
        r for r in non_felling if r["eventual_feller"] not in ("actor", "opponent", "survived_to_end")
    ]

    capacity_blocked_felling = [r for r in felling if r["free_capacity_before"] <= 0]
    contended_felling = [r for r in felling if r["own_contention"] >= 2]
    solo_felling = [r for r in felling if r["own_contention"] <= 1]
    solo_capacity_blocked = [r for r in solo_felling if r["free_capacity_before"] <= 0]
    # provable overflow-destroyed wood: solo (no other own chopper could have taken the
    # surplus), capacity-blocked (free<=0), tree size > 0 -- the whole size is
    # unrecoverable *by anyone on our side* on this turn (matches sim/engine.py's
    # apply_chop: with a single free<=0 chopper, size-1 units of wood are destroyed,
    # not banked by anyone).
    solo_capacity_blocked_wood_destroyed = sum(r["size_at_death"] or 0 for r in solo_capacity_blocked)

    # Capacity-shortfall split, mirroring wood_conversion_field_probe.py's
    # wood_recoverable_by_banking / wood_unavoidable_at_capacity (a live-game,
    # instrumented-binary probe run 2026-07-16 against an earlier resident vintage;
    # data/panels/top5-wood-conversion-telemetry.json found 95.1% of its lost wood
    # "unavoidable" -- structural to the felling unit's own trained cc stat, not
    # banking timing). Applied here to solo felling chops only (own_contention<=1,
    # which is ~100% of felling chops in every cohort -- see contended_felling
    # above): unavoidable = max(0, size_at_death - unit_cc) -- no amount of
    # pre-banking could have captured this, the unit's own stat ceiling is the
    # limit; recoverable = max(0, min(size_at_death, unit_cc) - min(size_at_death,
    # free_capacity_before)) -- wood lost only because the unit hadn't banked yet,
    # which a fuller-capacity-at-decision-time policy could have captured.
    solo_felling_capacity = []
    for r in solo_felling:
        size = r["size_at_death"] or 0
        cc = r["unit_cc"]
        free = max(0, r["free_capacity_before"])
        unavoidable = max(0, size - cc)
        recoverable = max(0, min(size, cc) - min(size, free))
        solo_felling_capacity.append({"unavoidable": unavoidable, "recoverable": recoverable})
    total_unavoidable = sum(row["unavoidable"] for row in solo_felling_capacity)
    total_recoverable = sum(row["recoverable"] for row in solo_felling_capacity)

    origin_counts = Counter(r["target_origin"] for r in landed)
    kind_counts = Counter(r["kind"] for r in landed if r["kind"])

    size_at_death = [r["size_at_death"] for r in felling if r["size_at_death"] is not None]

    move_count = sum(row["move_chop"]["move_count"] for row in rows)
    chop_count = sum(row["move_chop"]["chop_count"] for row in rows)

    def wood_per(subset):
        n = len(subset)
        return ratio(sum(r["wood_gained"] for r in subset), n)

    return {
        "occurrences": len(rows),
        "total_chop_events_recorded": len(records),
        "landed_chop_events": n_landed,
        "landed_rate": ratio(n_landed, len(records)),
        "wood_per_chop_all_landed": ratio(total_wood, n_landed),
        "wood_per_chop_games_jsonl_style_nonfelling_denominator": ratio(total_wood, len(non_felling)),
        "chops_per_occurrence": ratio(n_landed, len(rows)),
        "felling": {
            "share_of_landed_chops": ratio(len(felling), n_landed),
            "n": len(felling),
            "wood_per_felling_chop": wood_per(felling),
            "capacity_blocked_free_leq_0": {
                "definition": (
                    "felling chop where the acting unit's free capacity was already "
                    "<=0 at decision time -- the live chop_candidates() scorer "
                    "(yamo_orchard_live.rs:1050-1053) refuses to generate ANY chop "
                    "candidate when free_capacity()<=0, so this should be ~0 for any "
                    "agent sharing that guard; nonzero values indicate a different "
                    "policy (e.g. a peer agent without this guard)."
                ),
                "n": len(capacity_blocked_felling),
                "share_of_felling": ratio(len(capacity_blocked_felling), len(felling)),
            },
            "contended_2plus_own_units": {
                "n": len(contended_felling),
                "share_of_felling": ratio(len(contended_felling), len(felling)),
                "wood_per_chop_contended": wood_per(contended_felling),
                "wood_per_chop_solo": wood_per(solo_felling),
            },
            "solo_capacity_blocked_wood_destroyed_units": solo_capacity_blocked_wood_destroyed,
            "solo_capacity_blocked_wood_destroyed_per_occurrence": ratio(
                solo_capacity_blocked_wood_destroyed, len(rows)
            ),
            "capacity_shortfall_solo_felling": {
                "definition": (
                    "size_at_death vs the felling unit's own stat cc (carry_capacity) "
                    "and its free capacity at decision time -- mirrors "
                    "wood_conversion_field_probe.py's wood_unavoidable_at_capacity / "
                    "wood_recoverable_by_banking (see module docstring)"
                ),
                "n_solo_felling": len(solo_felling),
                "unavoidable_units_total": total_unavoidable,
                "unavoidable_units_per_occurrence": ratio(total_unavoidable, len(rows)),
                "recoverable_by_banking_units_total": total_recoverable,
                "recoverable_by_banking_units_per_occurrence": ratio(total_recoverable, len(rows)),
                "unavoidable_share_of_total_shortfall": ratio(
                    total_unavoidable, total_unavoidable + total_recoverable
                ),
            },
            "size_at_felling": {
                "mean": mean(size_at_death),
                "histogram": dict(sorted(Counter(size_at_death).items())),
                "share_size_1": ratio(size_at_death.count(1), len(size_at_death)),
                "share_size_4": ratio(size_at_death.count(4), len(size_at_death)),
            },
        },
        "non_felling_investment_chops": {
            "share_of_landed_chops": ratio(len(non_felling), n_landed),
            "n": len(non_felling),
            "eventual_feller_actor_normal_progress": {
                "n": len(non_felling_actor),
                "share_of_non_felling": ratio(len(non_felling_actor), len(non_felling)),
            },
            "wasted_eventual_feller_opponent": {
                "n": len(non_felling_opponent),
                "share_of_non_felling": ratio(len(non_felling_opponent), len(non_felling)),
                "share_of_all_landed_chops": ratio(len(non_felling_opponent), n_landed),
            },
            "wasted_survives_to_end": {
                "n": len(non_felling_survives),
                "share_of_non_felling": ratio(len(non_felling_survives), len(non_felling)),
                "share_of_all_landed_chops": ratio(len(non_felling_survives), n_landed),
            },
            "unaccounted_edge_case": {
                "n": len(non_felling_unaccounted),
                "share_of_non_felling": ratio(len(non_felling_unaccounted), len(non_felling)),
            },
        },
        "target_origin_composition_of_all_landed_chops": {
            origin: {"n": count, "share": ratio(count, n_landed)}
            for origin, count in sorted(origin_counts.items())
        },
        "target_kind_composition": {
            kind: {
                "n": count,
                "share": ratio(count, n_landed),
                "wood_per_chop": wood_per([r for r in landed if r["kind"] == kind]),
            }
            for kind, count in sorted(kind_counts.items())
        },
        "travel_overhead_proxy": {
            "definition": (
                "for units that ever CHOP >=1 time this game, total MOVE commands "
                "issued over their whole game-life / total CHOP commands issued -- a "
                "coarse chop-utilization signal, not a per-tree travel-time measure"
            ),
            "pooled_move_count": move_count,
            "pooled_chop_count": chop_count,
            "move_to_chop_ratio": ratio(move_count, chop_count),
        },
    }


def summarize_cohort_contact(rows: list[dict]) -> dict:
    """The opponent-crop contact-coverage decomposition (task item 2) for one
    cohort's pooled opponent-origin generations."""

    gens = [g for row in rows for g in row["opponent_generations"]]
    contacted = [g for g in gens if g["contacted"]]
    reachable = [g for g in gens if g["reachable"]]
    unreachable = [g for g in gens if not g["reachable"]]
    reachable_contacted = [g for g in reachable if g["contacted"]]
    unreachable_contacted = [g for g in unreachable if g["contacted"]]
    etas = [g["eta_at_birth"] for g in gens if g["eta_at_birth"] is not None]

    return {
        "opponent_origin_generations": len(gens),
        "contacted": len(contacted),
        "contact_coverage": ratio(len(contacted), len(gens)),
        "eta_at_birth": {
            "coverage": ratio(len(etas), len(gens)),
            "mean": mean(etas),
            "median": statistics.median(etas) if etas else None,
        },
        "reachable_within_20": {
            "n": len(reachable),
            "share_of_all": ratio(len(reachable), len(gens)),
            "contact_coverage_among_reachable": ratio(len(reachable_contacted), len(reachable)),
        },
        "unreachable_beyond_20_or_no_path": {
            "n": len(unreachable),
            "share_of_all": ratio(len(unreachable), len(gens)),
            "contact_coverage_among_unreachable": ratio(len(unreachable_contacted), len(unreachable)),
        },
    }


def kind_mix_decomposition(base_kinds: dict, other_kinds: dict) -> dict:
    """Standard mix/rate (Oaxaca-style) decomposition of the wood/chop gap between
    two cohorts' ``target_kind_composition`` blocks: how much of the gap is 'we chop
    a worse MIX of tree kinds' (mix effect, own within-kind rates held fixed) versus
    'we get less wood even for the SAME kind' (rate effect, own kind-mix held
    fixed)."""

    kinds = sorted(set(base_kinds) & set(other_kinds))
    base_actual = sum(base_kinds[k]["share"] * base_kinds[k]["wood_per_chop"] for k in kinds)
    other_actual = sum(other_kinds[k]["share"] * other_kinds[k]["wood_per_chop"] for k in kinds)
    # base's mix, other's rates -- isolates the rate (within-kind efficiency) effect
    base_mix_other_rate = sum(base_kinds[k]["share"] * other_kinds[k]["wood_per_chop"] for k in kinds)
    # other's mix, base's rates -- isolates the mix (kind-choice) effect
    other_mix_base_rate = sum(other_kinds[k]["share"] * base_kinds[k]["wood_per_chop"] for k in kinds)
    rate_effect = base_mix_other_rate - base_actual
    mix_effect = other_mix_base_rate - base_actual
    total_gap = other_actual - base_actual
    return {
        "kinds": kinds,
        "base_actual_wood_per_chop": base_actual,
        "other_actual_wood_per_chop": other_actual,
        "total_gap": total_gap,
        "rate_effect_same_mix_others_efficiency": rate_effect,
        "mix_effect_others_mix_own_efficiency": mix_effect,
        "interaction_residual": total_gap - rate_effect - mix_effect,
        "interpretation": (
            "rate_effect: value gained if we chopped OUR OWN kind mix but got the "
            "other cohort's within-kind wood/chop. mix_effect: value gained if we "
            "chopped the OTHER cohort's kind mix at OUR OWN within-kind efficiency. "
            "Both are evaluated holding the other factor at our own baseline (a "
            "standard first-order decomposition); they need not sum exactly to "
            "total_gap (interaction_residual carries the remainder)."
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOBS)
    parser.add_argument("--games-per-agent-cap", type=int, default=GAMES_PER_AGENT_CAP)
    parser.add_argument("--reconstruction-examples", type=int, default=DEFAULT_RECONSTRUCTION_EXAMPLES)
    parser.add_argument(
        "--skip-reconstruction", action="store_true", help="skip Part 4 (scoring reconstruction)"
    )
    args = parser.parse_args()

    b44_ground_truth = load_b44_ground_truth()
    cohort_info = select_cohort()
    strong_ids = cohort_info["strong_ids"]
    peer_ids = cohort_info["peer_ids"]
    print(
        f"cohort: {len(strong_ids)} strong, {len(peer_ids)} peer_weak "
        f"(leaderboard {cohort_info['leaderboard_path']})"
    )
    if b44_ground_truth is not None:
        cohort_matches_b44 = (
            strong_ids == b44_ground_truth["strong_agent_ids"]
            and peer_ids == b44_ground_truth["peer_weak_agent_ids"]
        )
        print(f"cohort identity matches b44 snapshot: {cohort_matches_b44}")
    else:
        cohort_matches_b44 = None
        print("no b44 ground-truth file found; proceeding without cross-check")

    tasks = build_tasks(strong_ids, peer_ids, args.games_per_agent_cap)
    print(f"heavy pass: {len(tasks)} occurrences queued (games-per-agent-cap={args.games_per_agent_cap})")
    ok_rows, failures = run_heavy_pass(tasks, jobs=args.jobs)
    print(f"heavy pass done: {len(ok_rows)} ok, {len(failures)} failed")

    rows_by_cohort: dict[str, list[dict]] = defaultdict(list)
    for row in ok_rows:
        rows_by_cohort[row["cohort"]].append(row)

    chop_decomposition = {
        cohort: summarize_cohort_chops(rows_by_cohort.get(cohort, []))
        for cohort in ("resident", "strong", "peer_weak")
    }
    contact_decomposition = {
        cohort: summarize_cohort_contact(rows_by_cohort.get(cohort, []))
        for cohort in ("resident", "strong", "peer_weak")
    }
    print(
        "wood/chop (this script, capped sample): "
        f"resident={chop_decomposition['resident']['wood_per_chop_all_landed']:.4f} "
        f"strong={chop_decomposition['strong']['wood_per_chop_all_landed']:.4f} "
        f"peer_weak={chop_decomposition['peer_weak']['wood_per_chop_all_landed']:.4f}"
    )
    print(
        "contact coverage (this script, capped sample): "
        f"resident={contact_decomposition['resident']['contact_coverage']:.4f} "
        f"strong={contact_decomposition['strong']['contact_coverage']:.4f} "
        f"peer_weak={contact_decomposition['peer_weak']['contact_coverage']:.4f}"
    )

    kind_mix = {
        "resident_vs_strong": kind_mix_decomposition(
            chop_decomposition["resident"]["target_kind_composition"],
            chop_decomposition["strong"]["target_kind_composition"],
        ),
        "resident_vs_peer_weak": kind_mix_decomposition(
            chop_decomposition["resident"]["target_kind_composition"],
            chop_decomposition["peer_weak"]["target_kind_composition"],
        ),
    }
    print(
        "kind-mix decomposition resident-vs-strong: "
        f"rate_effect={kind_mix['resident_vs_strong']['rate_effect_same_mix_others_efficiency']:.4f} "
        f"mix_effect={kind_mix['resident_vs_strong']['mix_effect_others_mix_own_efficiency']:.4f}"
    )

    reconstruction = None
    if not args.skip_reconstruction:
        resident_game_ids = agent_game_ids(RESIDENT_AGENT_ID)
        reconstruction = reconstruct_examples(resident_game_ids, args.reconstruction_examples)
        print(
            f"reconstruction: {reconstruction['top1_match_count']}/"
            f"{reconstruction['decision_points_checked']} top-1 matches "
            f"({reconstruction['top1_match_rate']:.1%})"
        )

    report = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only field-data diagnostic (B4.6): no arena writes, no strategy "
            "changes, no corpus mutation"
        ),
        "resident_agent_id": RESIDENT_AGENT_ID,
        "b44_ground_truth": b44_ground_truth,
        "cohort_identity_matches_b44_snapshot": cohort_matches_b44,
        "cohort": {
            "leaderboard_path": cohort_info["leaderboard_path"],
            "strong_agent_ids": strong_ids,
            "peer_weak_agent_ids": peer_ids,
        },
        "tunables": {
            "games_per_agent_cap": args.games_per_agent_cap,
            "reachable_eta_threshold": REACHABLE_ETA_THRESHOLD,
        },
        "occurrences": {
            cohort: {
                "n": len(rows_by_cohort.get(cohort, [])),
                "distinct_agents": len({row["agent_id"] for row in rows_by_cohort.get(cohort, [])}),
            }
            for cohort in ("resident", "strong", "peer_weak")
        },
        "failures": failures[:50],
        "chop_decomposition": chop_decomposition,
        "contact_decomposition": contact_decomposition,
        "kind_mix_decomposition": kind_mix,
        "reconstruction": reconstruction,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
