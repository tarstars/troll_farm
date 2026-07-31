#!/usr/bin/env python3
"""H4 read-only opponent worker-three bill deniability census.

The frozen population and verdict gates are defined in
``docs/h4-opponent-bill-deniability-census-protocol-2026-07-31.md``.  This analyzer
reads only the exact 200 game IDs named by the accepted D159 artifact.  It never writes
raw/processed data, simulates a terminal alternative, edits policy source, or accesses
the Arena.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cgauto.waste_sweep as waste_sweep
from cgauto.replay_conformance import action_commands
from cgauto.top_player_opening_analysis import assigned_unit_commands, bfs


REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "data/analysis/live-agent-6553250"
DEFAULT_MANIFEST = BASE / "d159a-current-resident-all-finished-effect-refresh-raw.json"
DEFAULT_ACCEPTED_RESULT = (
    BASE / "d159a-current-resident-all-finished-effect-refresh-result.json"
)
DEFAULT_DATA_ROOT = REPO / "data"
DEFAULT_OUTPUT = BASE / "h4-opponent-bill-deniability-census-result-2026-07-31.json"

EXPECTED_MANIFEST_SHA256 = (
    "97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443"
)
EXPECTED_ACCEPTED_RESULT_SHA256 = (
    "bd3fe4571aec423cdb57d514a2f610c0dcfe9845099b5500a6721e98d72965ac"
)
EXPECTED_RESIDENT_AGENT_ID = 6561795
EXPECTED_RESIDENT_SOURCE_SHA256 = (
    "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
)
EXPECTED_GAMES = 200
CATASTROPHE_MARGIN = -100
WORKER_THREE_N_BEFORE = 2
BILL_INDICES = (0, 1, 2, 4)
BILL_ITEMS = ("PLUM", "LEMON", "APPLE", "IRON")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def contribution_bounds(
    *, starting: int, external_supply_upper: int, bank: int, cost: int
) -> dict[str, int]:
    """Conservative exact intervals induced by a fungible bank.

    ``external_supply_upper`` is the number of post-start units ever acquired from
    HARVEST/MINE before payment.  Some may have been carried or spent, so it is an upper
    bound on external units present in the bank.  Starting units are bounded the same
    way.  Conservation then yields valid lower/upper bill-contribution intervals without
    imposing FIFO/LIFO token identity.
    """

    if min(starting, external_supply_upper, bank, cost) < 0:
        raise ValueError("contribution inputs must be non-negative")
    if bank < cost:
        raise ValueError("successful payment cannot have bank below cost")
    starting_bank_min = max(0, bank - external_supply_upper)
    starting_bank_max = min(starting, bank)
    external_bank_min = max(0, bank - starting)
    external_bank_max = min(external_supply_upper, bank)
    return {
        "starting_bank_min": starting_bank_min,
        "starting_bank_max": starting_bank_max,
        "external_bank_min": external_bank_min,
        "external_bank_max": external_bank_max,
        "starting_bill_min": max(0, cost - external_bank_max),
        "starting_bill_max": min(cost, starting_bank_max),
        "external_bill_min": max(0, cost - starting_bank_max),
        "external_bill_max": min(cost, external_bank_max),
    }


def remaining_supply_caps(
    *,
    starting: int,
    total_external_supply: int,
    prior_train_cost: int,
    external_supply_before_prior_train: int,
) -> dict[str, int]:
    """Upper bounds remaining after earlier successful TRAIN payments.

    To maximize original starting stock at the target TRAIN, credit every external unit
    acquired before the earlier payment first.  To maximize external stock, credit
    starting stock first.  The two maxima need not be jointly attainable; using both is
    deliberately conservative for every later minimum-contribution claim.
    """

    if min(
        starting,
        total_external_supply,
        prior_train_cost,
        external_supply_before_prior_train,
    ) < 0:
        raise ValueError("supply-cap inputs must be non-negative")
    minimum_starting_spent = max(
        0, prior_train_cost - external_supply_before_prior_train
    )
    minimum_external_spent = max(0, prior_train_cost - starting)
    return {
        "minimum_starting_spent_on_prior_trains": minimum_starting_spent,
        "minimum_external_spent_on_prior_trains": minimum_external_spent,
        "remaining_starting_stock_upper": max(
            0, starting - minimum_starting_spent
        ),
        "remaining_external_supply_upper": max(
            0, total_external_supply - minimum_external_spent
        ),
    }


def source_minimum_bill_contribution(
    *,
    starting: int,
    total_external_supply: int,
    source_amount: int,
    bank: int,
    cost: int,
) -> int:
    """Minimum units from one definitely deposited source that the bill must use."""

    if source_amount < 0 or source_amount > total_external_supply:
        raise ValueError("source amount must lie within external supply")
    other_supply_upper = starting + total_external_supply - source_amount
    source_in_bank_min = max(0, bank - other_supply_upper)
    return max(0, cost - (bank - source_in_bank_min))


def strict_block(required_source_units: int, removable_units: int, bank_slack: int) -> bool:
    """Whether removing one source batch makes the original payment unaffordable."""

    needed = bank_slack + 1
    return (
        needed > 0
        and required_source_units >= needed
        and removable_units >= needed
    )


def classify_command(command: str | None) -> str:
    verb = (command or "WAIT").split()[0].upper()
    if verb == "WAIT":
        return "idle"
    if verb == "MOVE":
        return "movement"
    if verb in {"DROP", "PICK"}:
        return "banking_logistics"
    if verb == "CHOP":
        return "suppression"
    if verb in {"HARVEST", "PLANT", "MINE"}:
        return "production"
    return "other"


def harvest_gains(fruits: int, units: list[dict[str, int]]) -> dict[int, int]:
    """Exact ``apply_harvest`` round-robin allocation for one occupied cell."""

    remaining = fruits
    gains = {unit["id"]: 0 for unit in units}
    for level in range(1, 4):
        if remaining == 0:
            break
        for unit in units:
            if unit["hp"] >= level and unit["carry_total"] + gains[unit["id"]] < unit["cc"]:
                gains[unit["id"]] += 1
                remaining -= 1
                if remaining == 0:
                    break
    return gains


def same_turn_harvest_reduction(
    *,
    fruits: int,
    opponent_player: int,
    resident_player: int,
    actual_harvesters: dict[int, list[dict[str, int]]],
    candidate: dict[str, int],
) -> int:
    """Opponent fruit removed by inserting one legal resident HARVEST.

    Players resolve in seat order.  Within the candidate's player, placing it first is
    the best legal command order and therefore an existence upper bound.  A positive
    result is still subjected to provenance and no-refill gates by the caller.
    """

    baseline_order = actual_harvesters.get(0, []) + actual_harvesters.get(1, [])
    baseline = harvest_gains(fruits, baseline_order)
    counterfactual = {0: list(actual_harvesters.get(0, [])), 1: list(actual_harvesters.get(1, []))}
    counterfactual[resident_player] = [candidate] + [
        unit for unit in counterfactual[resident_player] if unit["id"] != candidate["id"]
    ]
    changed_order = counterfactual[0] + counterfactual[1]
    changed = harvest_gains(fruits, changed_order)
    baseline_opponent = sum(
        amount
        for unit_id, amount in baseline.items()
        if any(
            unit["id"] == unit_id
            for unit in actual_harvesters.get(opponent_player, [])
        )
    )
    changed_opponent = sum(
        amount
        for unit_id, amount in changed.items()
        if any(
            unit["id"] == unit_id
            for unit in actual_harvesters.get(opponent_player, [])
        )
    )
    return max(0, baseline_opponent - changed_opponent)


def command_maps(game: waste_sweep.DecodedGame, turn: int) -> dict[int, dict[int, str]]:
    row = game.trajectory[turn - 1]
    result: dict[int, dict[int, str]] = {}
    before = game.states[turn - 1]
    for player in (0, 1):
        units = [unit for unit in before["units"] if unit["player"] == player]
        commands = action_commands(row.get(f"commands{player}"))
        result[player] = assigned_unit_commands(commands, units)
    return result


def unit_harvesters_at(
    game: waste_sweep.DecodedGame, turn: int, cell: tuple[int, int]
) -> dict[int, list[dict[str, int]]]:
    before = game.states[turn - 1]
    maps = command_maps(game, turn)
    ordered: dict[int, list[dict[str, int]]] = {0: [], 1: []}
    for player in (0, 1):
        commands = action_commands(
            game.trajectory[turn - 1].get(f"commands{player}")
        )
        by_id = {
            unit["id"]: unit
            for unit in before["units"]
            if unit["player"] == player
        }
        assigned = maps[player]
        command_order: list[int] = []
        for command in commands:
            if not command.upper().startswith("HARVEST "):
                continue
            try:
                command_order.append(int(command.split()[1]))
            except (IndexError, ValueError):
                continue
        for unit_id in command_order:
            unit = by_id.get(unit_id)
            if (
                unit is None
                or (unit["x"], unit["y"]) != cell
                or not assigned.get(unit_id, "").upper().startswith("HARVEST ")
            ):
                continue
            ordered[player].append(
                {
                    "id": unit_id,
                    "hp": int(unit["hp"]),
                    "cc": int(unit["cc"]),
                    "carry_total": sum(int(value) for value in unit["carry"]),
                }
            )
    return ordered


def add_unknown_lot(
    lots: list[dict[str, Any]], amount: int, *, reason: str
) -> None:
    if amount <= 0:
        return
    lots.append(
        {
            "source_id": None,
            "amount": amount,
            "external": False,
            "ambiguous": True,
            "reason": reason,
        }
    )


def consume_lots(lots: list[dict[str, Any]], amount: int) -> None:
    active = [lot for lot in lots if lot["amount"] > 0]
    if amount <= 0:
        return
    if sum(lot["amount"] for lot in active) < amount:
        raise ValueError("lot underflow")
    if len(active) > 1:
        for lot in active:
            if lot["external"]:
                lot["ambiguous"] = True
    remaining = amount
    for lot in active:
        take = min(lot["amount"], remaining)
        lot["amount"] -= take
        remaining -= take
        if remaining == 0:
            break


def extract_source_batches(
    game: waste_sweep.DecodedGame, train_turn: int
) -> tuple[list[dict[str, Any]], dict[str, int], list[str]]:
    """Track pre-payment external acquisitions and definite deposits."""

    tracked: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    sources: list[dict[str, Any]] = []
    source_by_id: dict[int, dict[str, Any]] = {}
    external_supply = [0] * 6
    errors: list[str] = []
    next_source_id = 1
    me = game.me

    for unit in game.states[0]["units"]:
        if unit["player"] != me:
            continue
        for item in BILL_INDICES:
            add_unknown_lot(
                tracked[(unit["id"], item)],
                int(unit["carry"][item]),
                reason="initial_carry",
            )

    for turn in range(1, train_turn):
        before_units = {
            unit["id"]: unit
            for unit in game.states[turn - 1]["units"]
            if unit["player"] == me
        }
        after_units = {
            unit["id"]: unit
            for unit in game.states[turn]["units"]
            if unit["player"] == me
        }
        assigned = command_maps(game, turn)[me]

        for unit_id, before in before_units.items():
            after = after_units.get(unit_id)
            if after is None:
                errors.append(f"turn {turn} unit {unit_id}: disappeared")
                continue
            command = assigned.get(unit_id, "WAIT")
            verb = command.split()[0].upper()
            cell = (int(before["x"]), int(before["y"]))
            for item in BILL_INDICES:
                lots = tracked[(unit_id, item)]
                lot_total = sum(int(lot["amount"]) for lot in lots)
                before_amount = int(before["carry"][item])
                if lot_total != before_amount:
                    add_unknown_lot(
                        lots,
                        before_amount - lot_total,
                        reason=f"turn_{turn}_reconcile_before",
                    )
                    lot_total = sum(int(lot["amount"]) for lot in lots)
                    if lot_total != before_amount:
                        errors.append(
                            f"turn {turn} unit {unit_id} item {item}: "
                            f"lot total {lot_total} != carry {before_amount}"
                        )
                        continue
                after_amount = int(after["carry"][item])
                delta = after_amount - before_amount

                if delta > 0:
                    if verb in {"HARVEST", "MINE"}:
                        expected_item = item != 4 if verb == "HARVEST" else item == 4
                        if not expected_item:
                            errors.append(
                                f"turn {turn} unit {unit_id}: {verb} gained "
                                f"{waste_sweep.ITEMS[item]}"
                            )
                        source = {
                            "source_id": next_source_id,
                            "turn": turn,
                            "unit_id": unit_id,
                            "action": verb,
                            "item": waste_sweep.ITEMS[item],
                            "item_index": item,
                            "cell": [cell[0], cell[1]],
                            "amount": delta,
                            "ambiguous": False,
                            "definite_deposit_turn": None,
                            "definite_deposited_amount": 0,
                            "source_minimum_bill_contribution": 0,
                            "reachable_upper_bound": False,
                        }
                        next_source_id += 1
                        sources.append(source)
                        source_by_id[source["source_id"]] = source
                        lots.append(
                            {
                                "source_id": source["source_id"],
                                "amount": delta,
                                "external": True,
                                "ambiguous": False,
                            }
                        )
                        external_supply[item] += delta
                    elif verb == "PICK":
                        add_unknown_lot(lots, delta, reason="bank_pick")
                    else:
                        errors.append(
                            f"turn {turn} unit {unit_id} item {item}: "
                            f"unclassified positive carry delta {delta} under {verb}"
                        )
                        add_unknown_lot(
                            lots, delta, reason=f"unclassified_gain_{verb}"
                        )

                elif delta < 0:
                    removed = -delta
                    if verb == "DROP":
                        for lot in lots:
                            if not lot["external"] or lot["amount"] <= 0:
                                continue
                            source = source_by_id[int(lot["source_id"])]
                            if lot["ambiguous"]:
                                source["ambiguous"] = True
                            else:
                                source["definite_deposited_amount"] += int(
                                    lot["amount"]
                                )
                                source["definite_deposit_turn"] = turn
                        consume_lots(lots, removed)
                    elif verb == "PLANT":
                        consume_lots(lots, removed)
                        for lot in lots:
                            if lot["external"] and lot["ambiguous"]:
                                source_by_id[int(lot["source_id"])]["ambiguous"] = True
                    else:
                        errors.append(
                            f"turn {turn} unit {unit_id} item {item}: "
                            f"unclassified negative carry delta {delta} under {verb}"
                        )
                        consume_lots(lots, removed)

                final_total = sum(int(lot["amount"]) for lot in lots)
                if final_total != after_amount:
                    errors.append(
                        f"turn {turn} unit {unit_id} item {item}: "
                        f"post lot total {final_total} != carry {after_amount}"
                    )

    totals = {
        waste_sweep.ITEMS[item]: int(external_supply[item])
        for item in BILL_INDICES
    }
    return sources, totals, errors


def source_refilled_before_deposit(
    source: dict[str, Any], sources: list[dict[str, Any]]
) -> bool:
    deposit_turn = source["definite_deposit_turn"]
    if deposit_turn is None:
        return True
    return any(
        other["source_id"] != source["source_id"]
        and other["unit_id"] == source["unit_id"]
        and other["item"] == source["item"]
        and source["turn"] < other["turn"] <= deposit_turn
        for other in sources
    )


def reachable_before_source(
    game: waste_sweep.DecodedGame,
    *,
    resident_player: int,
    cell: tuple[int, int],
    source_turn: int,
) -> bool:
    distances = bfs(game.board["walkable"], [cell])
    for state_index in range(source_turn):
        turns_available = source_turn - (state_index + 1)
        for unit in game.states[state_index]["units"]:
            if unit["player"] != resident_player:
                continue
            distance = distances.get((unit["x"], unit["y"]))
            if distance is not None and distance <= turns_available * max(1, unit["ms"]):
                return True
    return False


def plant_at(state: dict[str, Any], cell: tuple[int, int]) -> dict[str, Any] | None:
    return next(
        (
            plant
            for plant in state["plants"]
            if (plant["x"], plant["y"]) == cell
        ),
        None,
    )


def strict_candidates(
    game: waste_sweep.DecodedGame,
    *,
    train_turn: int,
    cost_by_item: dict[str, int],
    bank_by_item: dict[str, int],
    sources: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    resident = 1 - game.me
    candidates: list[dict[str, Any]] = []
    funnel_sets: dict[str, set[int]] = {
        "mandatory_fruit_batches": set(),
        "same_turn_resident_colocated_batches": set(),
        "same_turn_legal_harvest_batches": set(),
        "positive_same_turn_harvest_reduction_batches": set(),
        "prior_resident_colocated_lethal_chop_batches": set(),
    }

    for source in sources:
        if (
            source["action"] != "HARVEST"
            or source["item"] not in {"PLUM", "LEMON", "APPLE"}
            or source["ambiguous"]
            or source["definite_deposited_amount"] != source["amount"]
            or source["source_minimum_bill_contribution"] <= 0
        ):
            continue
        funnel_sets["mandatory_fruit_batches"].add(int(source["source_id"]))
        turn = int(source["turn"])
        cell = tuple(source["cell"])
        before = game.states[turn - 1]
        plant = plant_at(before, cell)
        if plant is None or int(plant["fruits"]) <= 0:
            continue
        maps = command_maps(game, turn)
        harvesters = unit_harvesters_at(game, turn, cell)
        bank_slack = (
            bank_by_item[source["item"]] - cost_by_item[source["item"]]
        )

        resident_on_cell = [
            unit
            for unit in before["units"]
            if unit["player"] == resident
            and (unit["x"], unit["y"]) == cell
        ]
        if resident_on_cell:
            funnel_sets["same_turn_resident_colocated_batches"].add(
                int(source["source_id"])
            )
        for unit in resident_on_cell:
            if (
                unit["hp"] <= 0
                or sum(unit["carry"]) >= unit["cc"]
                or maps[resident].get(unit["id"], "WAIT")
                .upper()
                .startswith("HARVEST ")
            ):
                continue
            funnel_sets["same_turn_legal_harvest_batches"].add(
                int(source["source_id"])
            )
            candidate_unit = {
                "id": int(unit["id"]),
                "hp": int(unit["hp"]),
                "cc": int(unit["cc"]),
                "carry_total": sum(int(value) for value in unit["carry"]),
            }
            reduction = same_turn_harvest_reduction(
                fruits=int(plant["fruits"]),
                opponent_player=game.me,
                resident_player=resident,
                actual_harvesters=harvesters,
                candidate=candidate_unit,
            )
            if source_refilled_before_deposit(source, sources):
                reduction = 0
            if reduction > 0:
                funnel_sets[
                    "positive_same_turn_harvest_reduction_batches"
                ].add(int(source["source_id"]))
            if strict_block(
                int(source["source_minimum_bill_contribution"]),
                reduction,
                bank_slack,
            ):
                displaced = maps[resident].get(unit["id"], "WAIT")
                candidates.append(
                    {
                        "kind": "same_turn_harvest",
                        "turn": turn,
                        "unit_id": int(unit["id"]),
                        "cell": list(cell),
                        "item": source["item"],
                        "removable_units": reduction,
                        "bank_slack": bank_slack,
                        "required_source_units": source[
                            "source_minimum_bill_contribution"
                        ],
                        "displaced_command": displaced,
                        "displacement_class": classify_command(displaced),
                        "blocks_original_train_turn": True,
                    }
                )

        # A prior one-command lethal CHOP removes this source generation.  Require the
        # plant to remain continuously present through acquisition and no later refill
        # on the acquiring unit before its definite DROP.
        if source_refilled_before_deposit(source, sources):
            continue
        for action_turn in range(1, turn):
            action_state = game.states[action_turn - 1]
            action_plant = plant_at(action_state, cell)
            if action_plant is None:
                continue
            if any(
                plant_at(game.states[index], cell) is None
                for index in range(action_turn - 1, turn)
            ):
                continue
            maps_at_action = command_maps(game, action_turn)
            for unit in action_state["units"]:
                if (
                    unit["player"] != resident
                    or (unit["x"], unit["y"]) != cell
                    or unit["chop"] < action_plant["health"]
                    or maps_at_action[resident]
                    .get(unit["id"], "WAIT")
                    .upper()
                    .startswith("CHOP ")
                ):
                    continue
                funnel_sets[
                    "prior_resident_colocated_lethal_chop_batches"
                ].add(int(source["source_id"]))
                bank_slack = (
                    bank_by_item[source["item"]]
                    - cost_by_item[source["item"]]
                )
                removable = int(source["amount"])
                if not strict_block(
                    int(source["source_minimum_bill_contribution"]),
                    removable,
                    bank_slack,
                ):
                    continue
                displaced = maps_at_action[resident].get(unit["id"], "WAIT")
                candidates.append(
                    {
                        "kind": "prior_lethal_chop",
                        "turn": action_turn,
                        "source_turn": turn,
                        "unit_id": int(unit["id"]),
                        "cell": list(cell),
                        "item": source["item"],
                        "removable_units": removable,
                        "bank_slack": bank_slack,
                        "required_source_units": source[
                            "source_minimum_bill_contribution"
                        ],
                        "displaced_command": displaced,
                        "displacement_class": classify_command(displaced),
                        "blocks_original_train_turn": True,
                    }
                )
    candidates.sort(
        key=lambda row: (
            row["turn"],
            row["unit_id"],
            row["kind"],
            row["item"],
        )
    )
    funnel = {key: len(value) for key, value in funnel_sets.items()}
    funnel["strict_one_action_candidates"] = len(candidates)
    return candidates, funnel


def audit_primary_game(
    row: dict[str, Any],
    opponent: waste_sweep.DecodedGame,
    resident: waste_sweep.DecodedGame,
    event: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    turn = int(event["turn"])
    talents = tuple(int(value) for value in event["talents"])
    cost = waste_sweep.training_cost(WORKER_THREE_N_BEFORE, talents)
    bank = [
        int(value)
        for value in opponent.states[turn - 1]["inventories"][opponent.me]
    ]
    starting = [
        int(value) for value in opponent.states[0]["inventories"][opponent.me]
    ]
    errors: list[str] = []
    pay = waste_sweep.training_pay_indices(opponent.iron_present)
    if tuple(pay) != BILL_INDICES:
        errors.append(f"game {row['game_id']}: unexpected non-Legend pay indices {pay}")
    if any(bank[index] < cost[index] for index in pay):
        errors.append(f"game {row['game_id']}: successful third TRAIN below cost")
    before_workers = sum(
        unit["player"] == opponent.me
        for unit in opponent.states[turn - 1]["units"]
    )
    after_workers = sum(
        unit["player"] == opponent.me for unit in opponent.states[turn]["units"]
    )
    if before_workers != 2 or after_workers != 3:
        errors.append(
            f"game {row['game_id']}: third TRAIN worker transition "
            f"{before_workers}->{after_workers}"
        )

    sources, external_supply, provenance_errors = extract_source_batches(
        opponent, turn
    )
    errors.extend(f"game {row['game_id']}: {error}" for error in provenance_errors)
    prior_trains = [
        earlier
        for earlier in opponent.train_events
        if int(earlier["turn"]) < turn
    ]
    last_prior_train_turn = max(
        (int(earlier["turn"]) for earlier in prior_trains), default=0
    )
    item_rows: dict[str, Any] = {}
    cost_by_item: dict[str, int] = {}
    bank_by_item: dict[str, int] = {}
    for index in BILL_INDICES:
        item = waste_sweep.ITEMS[index]
        prior_train_cost = sum(
            waste_sweep.training_cost(
                int(earlier["n_before"]),
                tuple(int(value) for value in earlier["talents"]),
            )[index]
            for earlier in prior_trains
        )
        external_before_prior = sum(
            int(source["amount"])
            for source in sources
            if source["item_index"] == index
            and int(source["turn"]) < last_prior_train_turn
        )
        caps = remaining_supply_caps(
            starting=starting[index],
            total_external_supply=external_supply[item],
            prior_train_cost=prior_train_cost,
            external_supply_before_prior_train=external_before_prior,
        )
        if (
            bank[index]
            > caps["remaining_starting_stock_upper"]
            + caps["remaining_external_supply_upper"]
        ):
            errors.append(
                f"game {row['game_id']} {item}: bank exceeds conservative "
                "remaining supply caps"
            )
        bounds = contribution_bounds(
            starting=caps["remaining_starting_stock_upper"],
            external_supply_upper=caps["remaining_external_supply_upper"],
            bank=bank[index],
            cost=cost[index],
        )
        item_rows[item] = {
            "cost": int(cost[index]),
            "bank_before": int(bank[index]),
            "bank_slack": int(bank[index] - cost[index]),
            "starting_stock": int(starting[index]),
            "post_start_external_supply_upper": int(external_supply[item]),
            "prior_train_cost": int(prior_train_cost),
            **caps,
            **bounds,
            "mechanically_deniable": item != "IRON",
        }
        cost_by_item[item] = int(cost[index])
        bank_by_item[item] = int(bank[index])

    for source in sources:
        source["reachable_upper_bound"] = reachable_before_source(
            opponent,
            resident_player=1 - opponent.me,
            cell=tuple(source["cell"]),
            source_turn=int(source["turn"]),
        )
        if (
            source["definite_deposited_amount"] == source["amount"]
            and not source["ambiguous"]
            and int(source["definite_deposit_turn"] or 0) > last_prior_train_turn
        ):
            item = source["item"]
            source["source_minimum_bill_contribution"] = (
                source_minimum_bill_contribution(
                    starting=item_rows[item][
                        "remaining_starting_stock_upper"
                    ],
                    total_external_supply=item_rows[item][
                        "remaining_external_supply_upper"
                    ],
                    source_amount=int(source["amount"]),
                    bank=item_rows[item]["bank_before"],
                    cost=item_rows[item]["cost"],
                )
            )

    candidates, strict_action_funnel = strict_candidates(
        opponent,
        train_turn=turn,
        cost_by_item=cost_by_item,
        bank_by_item=bank_by_item,
        sources=sources,
    )
    strict = bool(candidates)
    best_candidate = candidates[0] if candidates else None
    definite_sources = [
        source
        for source in sources
        if source["definite_deposited_amount"] == source["amount"]
        and not source["ambiguous"]
    ]
    mandatory_sources = [
        source
        for source in definite_sources
        if source["source_minimum_bill_contribution"] > 0
    ]
    source_funnel = {
        "external_acquisition_batches": len(sources),
        "definitely_deposited_batches": len(definite_sources),
        "reachable_fruit_upper_bound_batches": sum(
            source["reachable_upper_bound"] and source["item"] != "IRON"
            for source in sources
        ),
        "individually_mandatory_bill_batches": len(mandatory_sources),
        "strict_one_action_candidates": len(candidates),
    }
    return (
        {
            "game_id": int(row["game_id"]),
            "opponent": row["opponent"],
            "opponent_agent_id": int(row["opponent_agent_id"]),
            "resident_seat": int(row["seat"]),
            "resident_margin": int(row["margin"]),
            "crossover_turn": int(resident.crossover_turn),
            "third_train_turn": turn,
            "scale_to_crossover_lead": int(resident.crossover_turn - turn),
            "talents": list(talents),
            "items": item_rows,
            **source_funnel,
            "source_funnel": source_funnel,
            "mandatory_deposit_items": [
                item
                for item, values in item_rows.items()
                if values["external_bill_min"] > 0
            ],
            "strict_one_action_blockable": strict,
            "strict_candidates": candidates,
            "strict_action_funnel": strict_action_funnel,
            "best_candidate": best_candidate,
            # Only individually load-bearing sources can enter a decision.  Keeping
            # every ordinary acquisition event would turn this compact result into a
            # replay dump while adding no gate evidence.
            "decision_relevant_source_batches": mandatory_sources,
        },
        errors,
    )


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    strict = [row for row in rows if row["strict_one_action_blockable"]]
    displacement = Counter(
        row["best_candidate"]["displacement_class"] for row in strict
    )
    opponent_ids = {row["opponent_agent_id"] for row in rows}
    strict_ids = {row["opponent_agent_id"] for row in strict}
    strict_seats = {row["resident_seat"] for row in strict}
    cheap_strict = sum(
        row["best_candidate"]["displacement_class"] in {"idle", "movement"}
        for row in strict
    )
    materiality = {
        "primary_at_least_8_games": len(rows) >= 8,
        "primary_at_least_4_opponent_identities": len(opponent_ids) >= 4,
        "strict_blockable_at_least_25pct": bool(
            rows and len(strict) / len(rows) >= 0.25
        ),
        "strict_at_least_3_opponent_identities": len(strict_ids) >= 3,
        "strict_covers_both_resident_seats": strict_seats == {0, 1},
        "cheap_displacement_at_least_50pct": bool(
            strict and cheap_strict / len(strict) >= 0.50
        ),
    }
    return {
        "primary_games": len(rows),
        "opponent_identities": len(opponent_ids),
        "resident_seats": sorted({row["resident_seat"] for row in rows}),
        "scale_to_crossover_lead": {
            "minimum": min(
                (row["scale_to_crossover_lead"] for row in rows), default=None
            ),
            "median": (
                statistics.median(
                    row["scale_to_crossover_lead"] for row in rows
                )
                if rows
                else None
            ),
            "maximum": max(
                (row["scale_to_crossover_lead"] for row in rows), default=None
            ),
        },
        "games_with_mandatory_post_start_deposit": sum(
            bool(row["mandatory_deposit_items"]) for row in rows
        ),
        "games_with_reachable_upper_bound": sum(
            row["reachable_fruit_upper_bound_batches"] > 0 for row in rows
        ),
        "source_funnel": {
            key: sum(row["source_funnel"][key] for row in rows)
            for key in (
                "external_acquisition_batches",
                "definitely_deposited_batches",
                "reachable_fruit_upper_bound_batches",
                "individually_mandatory_bill_batches",
                "strict_one_action_candidates",
            )
        },
        "strict_action_funnel": {
            key: sum(row["strict_action_funnel"][key] for row in rows)
            for key in (
                "mandatory_fruit_batches",
                "same_turn_resident_colocated_batches",
                "same_turn_legal_harvest_batches",
                "positive_same_turn_harvest_reduction_batches",
                "prior_resident_colocated_lethal_chop_batches",
                "strict_one_action_candidates",
            )
        },
        "strict_one_action_blockable_games": len(strict),
        "strict_one_action_blockable_rate": len(strict) / len(rows) if rows else 0.0,
        "strict_opponent_identities": len(strict_ids),
        "strict_resident_seats": sorted(strict_seats),
        "strict_displacement_classes": dict(sorted(displacement.items())),
        "cheap_strict_displacements": cheap_strict,
        "materiality_gates": materiality,
        "materiality_pass": all(materiality.values()),
    }


def run(
    *,
    manifest_path: Path,
    accepted_result_path: Path,
    data_root: Path,
) -> dict[str, Any]:
    manifest_hash = sha256(manifest_path)
    result_hash = sha256(accepted_result_path)
    manifest = json.loads(manifest_path.read_text())
    accepted = json.loads(accepted_result_path.read_text())
    rows = manifest.get("rows") or []
    ids = [int(row["game_id"]) for row in rows]

    raw_games = data_root / "raw/games"
    trajectories = data_root / "processed/trajectories"
    waste_sweep.RAW_GAMES = raw_games
    waste_sweep.TRAJECTORIES = trajectories

    integrity_errors: list[str] = []
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        integrity_errors.append("D159 manifest hash mismatch")
    if result_hash != EXPECTED_ACCEPTED_RESULT_SHA256:
        integrity_errors.append("D159 accepted-result hash mismatch")
    if len(rows) != EXPECTED_GAMES or len(set(ids)) != EXPECTED_GAMES:
        integrity_errors.append("D159 game ID count/uniqueness mismatch")
    if accepted.get("identity", {}).get("resident_agent_id") != EXPECTED_RESIDENT_AGENT_ID:
        integrity_errors.append("accepted result resident identity mismatch")
    if (
        accepted.get("identity", {}).get("resident_source_sha256")
        != EXPECTED_RESIDENT_SOURCE_SHA256
    ):
        integrity_errors.append("accepted result source hash mismatch")

    missing_raw = [
        game_id for game_id in ids if not (raw_games / f"{game_id}.json").is_file()
    ]
    missing_trajectories = [
        game_id
        for game_id in ids
        if not (trajectories / f"{game_id}.jsonl").is_file()
    ]
    if missing_raw:
        integrity_errors.append(f"missing raw games: {missing_raw}")
    if missing_trajectories:
        integrity_errors.append(f"missing trajectories: {missing_trajectories}")

    decoded: dict[int, tuple[waste_sweep.DecodedGame, waste_sweep.DecodedGame]] = {}
    decode_errors: list[str] = []
    if not missing_raw and not missing_trajectories:
        for row in rows:
            game_id = int(row["game_id"])
            try:
                resident = waste_sweep.decode_game(game_id)
                opponent = waste_sweep.decode_game_for_agent(
                    game_id, int(row["opponent_agent_id"])
                )
            except Exception as exc:  # retain complete census diagnostics
                decode_errors.append(
                    f"{game_id}: {type(exc).__name__}: {exc}"
                )
                continue
            if resident.me != int(row["seat"]):
                decode_errors.append(
                    f"{game_id}: resident seat {resident.me} != manifest {row['seat']}"
                )
            decoded[game_id] = (resident, opponent)
    integrity_errors.extend(decode_errors)

    catastrophes = [row for row in rows if int(row["margin"]) <= CATASTROPHE_MARGIN]
    any_third = 0
    scale_linked_catastrophes = 0
    primary_rows: list[dict[str, Any]] = []
    for row in rows:
        game_id = int(row["game_id"])
        if game_id not in decoded:
            continue
        resident, opponent = decoded[game_id]
        thirds = [
            event
            for event in opponent.train_events
            if int(event["n_before"]) == WORKER_THREE_N_BEFORE
        ]
        if thirds:
            any_third += 1
        if int(row["margin"]) > CATASTROPHE_MARGIN:
            continue
        if thirds:
            scale_linked_catastrophes += 1
        before_crossover = [
            event
            for event in thirds
            if int(event["turn"]) < int(resident.crossover_turn)
        ]
        if not before_crossover:
            continue
        audited, errors = audit_primary_game(
            row, opponent, resident, before_crossover[0]
        )
        primary_rows.append(audited)
        integrity_errors.extend(errors)

    summary = summarize_rows(primary_rows)
    integrity = {
        "exact_200_game_id_set": len(rows) == EXPECTED_GAMES
        and len(set(ids)) == EXPECTED_GAMES,
        "manifest_hash_exact": manifest_hash == EXPECTED_MANIFEST_SHA256,
        "accepted_result_hash_exact": result_hash
        == EXPECTED_ACCEPTED_RESULT_SHA256,
        "resident_identity_exact": accepted.get("identity", {}).get(
            "resident_agent_id"
        )
        == EXPECTED_RESIDENT_AGENT_ID,
        "resident_source_hash_exact": accepted.get("identity", {}).get(
            "resident_source_sha256"
        )
        == EXPECTED_RESIDENT_SOURCE_SHA256,
        "all_named_raw_games_present": not missing_raw,
        "all_named_trajectories_present": not missing_trajectories,
        "all_games_decoded": len(decoded) == EXPECTED_GAMES,
        "zero_train_or_provenance_errors": not integrity_errors,
        "outside_game_ids_read": 0,
    }
    integrity_pass = all(
        value is True or (key == "outside_game_ids_read" and value == 0)
        for key, value in integrity.items()
    )
    if not integrity_pass:
        verdict = "UNIDENTIFIABLE"
    elif summary["materiality_pass"]:
        verdict = "MATERIAL_PREFLIGHT_ONLY"
    else:
        verdict = "NO_MATERIAL_DENIABLE_BILL"

    return {
        "schema": "troll-farm-h4-opponent-bill-deniability-census-v1",
        "date": "2026-07-31",
        "verdict": verdict,
        "population": {
            "manifest": str(manifest_path.relative_to(REPO)),
            "manifest_sha256": manifest_hash,
            "accepted_result": str(accepted_result_path.relative_to(REPO)),
            "accepted_result_sha256": result_hash,
            "games": len(rows),
            "catastrophes": len(catastrophes),
            "games_with_opponent_third_train": any_third,
            "catastrophes_with_opponent_third_train": scale_linked_catastrophes,
            "primary_definition": (
                "resident margin <= -100 and successful opponent TRAIN with "
                "n_before=2 strictly before permanent resident crossover"
            ),
            "primary_games": len(primary_rows),
        },
        "integrity": {
            "gates": integrity,
            "pass": integrity_pass,
            "errors": integrity_errors,
        },
        "mechanics": {
            "starting_inventory_deniable": False,
            "iron_terrain_depletes": False,
            "iron_source_deniable": False,
            "strict_action_types": [
                "same-turn already-positioned HARVEST",
                "prior already-positioned lethal CHOP",
            ],
            "reachable_upper_bound_is_decision_bearing": False,
        },
        "summary": summary,
        "primary_rows": primary_rows,
        "decision": {
            "construct_policy": False,
            "open_experiment": False,
            "candidate_or_arena": False,
            "next_step": (
                "request separate causal-preflight decision"
                if verdict == "MATERIAL_PREFLIGHT_ONLY"
                else "close H4; do not implement timed denial"
                if verdict == "NO_MATERIAL_DENIABLE_BILL"
                else "resolve integrity/identifiability before any continuation"
            ),
        },
    }


def self_test() -> None:
    bounds = contribution_bounds(
        starting=4, external_supply_upper=9, bank=8, cost=6
    )
    assert bounds["external_bill_min"] == 2
    assert bounds["external_bill_max"] == 6
    assert (
        source_minimum_bill_contribution(
            starting=4,
            total_external_supply=9,
            source_amount=5,
            bank=8,
            cost=6,
        )
        == 0
    )
    assert strict_block(2, 2, 1)
    assert not strict_block(1, 3, 1)
    assert classify_command("MOVE 7 2 3") == "movement"
    print("self-test: ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--accepted-result", type=Path, default=DEFAULT_ACCEPTED_RESULT
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help="logical repository data root containing raw/games and processed/trajectories",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run(
        # Preserve the repository-logical paths in the result.  These compact analysis
        # files are symlinked to external storage; resolving them would replace the
        # reproducible repo-relative locator with the observed physical mount path.
        manifest_path=args.manifest.absolute(),
        accepted_result_path=args.accepted_result.absolute(),
        data_root=args.data_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], **result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
