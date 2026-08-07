#!/usr/bin/env python3
"""Candidate-driven acceptance tests for the owner's Banana R2 contract.

These are closed-loop tests: the compiled candidate receives each state, its
commands are applied by the repository mini-referee, and the next state is fed
back.  Unlike the historical R2/R3 fixtures, every protected mother in the
positive cases is actually founded by the candidate itself.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLAUDE = REPO / "claude_1" / "banana-restoration-r2"
sys.path.insert(0, str(CLAUDE))

spec = importlib.util.spec_from_file_location(
    "banana_trace_driver", CLAUDE / "make_banana_traces.py"
)
mbt = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = mbt
spec.loader.exec_module(mbt)

BANANA = 3
WOOD = 5


class RecordingMixin:
    events: list[dict[str, Any]]
    turn_number: int

    def _recording_init(self) -> None:
        self.events = []
        self.turn_number = 1

    def apply(self, command_line: str) -> None:  # type: ignore[override]
        before_units = copy.deepcopy(self.units)
        before_plants = copy.deepcopy(self.plants)
        before_inv = list(self.inv)
        parsed: list[tuple[list[str], tuple[int, int] | None]] = []
        for raw in command_line.split(";"):
            parts = raw.strip().split()
            if not parts or parts[0].upper() in {"WAIT", "MSG", "TRAIN"}:
                continue
            try:
                uid = int(parts[1])
            except (IndexError, ValueError):
                continue
            cell = before_units.get(uid, {}).get("cell")
            parsed.append((parts, cell))

        super().apply(command_line)  # type: ignore[misc]

        for parts, cell in parsed:
            if cell is None:
                continue
            verb = parts[0].upper()
            uid = int(parts[1])
            before_unit = before_units.get(uid)
            after_unit = self.units.get(uid)
            event: dict[str, Any] = {
                "turn": self.turn_number,
                "unit": uid,
                "verb": verb,
                "cell": list(cell),
            }
            if verb == "PLANT" and len(parts) >= 3:
                event["kind"] = parts[2].upper()
                event["landed"] = (
                    cell not in before_plants
                    and cell in self.plants
                    and self.plants[cell]["kind"] == parts[2].upper()
                )
            elif verb in {"HARVEST", "CHOP"}:
                plant = before_plants.get(cell)
                event["kind"] = None if plant is None else plant["kind"]
                event["landed"] = before_plants.get(cell) != self.plants.get(cell)
                if before_unit and after_unit:
                    event["banana_delta"] = (
                        after_unit["carry"][BANANA] - before_unit["carry"][BANANA]
                    )
                    event["wood_delta"] = (
                        after_unit["carry"][WOOD] - before_unit["carry"][WOOD]
                    )
            elif verb == "DROP":
                event["banana_before"] = (
                    0 if before_unit is None else before_unit["carry"][BANANA]
                )
                event["wood_before"] = (
                    0 if before_unit is None else before_unit["carry"][WOOD]
                )
                event["banana_bank_delta"] = self.inv[BANANA] - before_inv[BANANA]
                event["wood_bank_delta"] = self.inv[WOOD] - before_inv[WOOD]
                event["landed"] = bool(
                    event["banana_bank_delta"] or event["wood_bank_delta"]
                )
            elif verb == "PICK" and len(parts) >= 3:
                event["kind"] = parts[2].upper()
                event["landed"] = before_inv != self.inv
            else:
                event["landed"] = True
            self.events.append(event)
        self.turn_number += 1


class RecordingReferee(RecordingMixin, mbt.Referee):
    def __init__(self, inventory, plants, units):
        mbt.Referee.__init__(self, inventory, plants, units)
        self._recording_init()


class RecordingDynamicReferee(RecordingMixin, mbt.DynamicOpponentReferee):
    def __init__(self, inventory, plants, units, opp_targets):
        mbt.DynamicOpponentReferee.__init__(
            self, inventory, plants, units, opp_targets
        )
        self._recording_init()


def clone_static(base: mbt.Referee) -> RecordingReferee:
    return RecordingReferee(
        list(base.inv), copy.deepcopy(base.plants), copy.deepcopy(base.units)
    )


def clone_dynamic(base: mbt.DynamicOpponentReferee) -> RecordingDynamicReferee:
    return RecordingDynamicReferee(
        list(base.inv),
        copy.deepcopy(base.plants),
        copy.deepcopy(base.units),
        copy.deepcopy(base.opp_targets),
    )


def is_ring(cell: tuple[int, int]) -> bool:
    return max(abs(cell[0] - mbt.TENT[0]), abs(cell[1] - mbt.TENT[1])) == 1


def is_diag(cell: tuple[int, int]) -> bool:
    return (
        abs(cell[0] - mbt.TENT[0]) == 1
        and abs(cell[1] - mbt.TENT[1]) == 1
    )


def is_orth(cell: tuple[int, int]) -> bool:
    return (
        abs(cell[0] - mbt.TENT[0]) + abs(cell[1] - mbt.TENT[1]) == 1
    )


def assert_detector_pass(report: dict[str, Any], scenario: str) -> None:
    failures = [
        result
        for result in report["detectors"]
        if result.get("verdict") != "PASS"
    ]
    if failures:
        raise AssertionError(
            f"{scenario}: detector failure(s): {json.dumps(failures, sort_keys=True)}"
        )


def banana_command_turns(events: list[dict[str, Any]]) -> list[int]:
    return [
        int(event["turn"])
        for event in events
        if (
            event.get("kind") == "BANANA"
            or event.get("banana_delta")
            or event.get("banana_before")
            or event.get("banana_bank_delta")
        )
    ]


def run_tests(candidate: Path, output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    mbt.TRACES = output / "traces"
    source = candidate.read_text()
    summary: dict[str, Any] = {
        "candidate": str(candidate),
        "scenarios": {},
    }

    with tempfile.TemporaryDirectory(prefix="banana-owner-contract-") as directory:
        binary = Path(directory) / "candidate"
        mbt.sh.compile_text(source, binary, "banana_owner_contract")

        # 1. Complete private lifecycle: candidate-founded diagonal mother,
        # renewable harvest/replant, orthogonal wood conversion, and banking.
        lifecycle = clone_static(mbt.scenario_t1())
        lifecycle_report = mbt.run_scenario(
            "owner_lifecycle", binary, lifecycle, 300
        )
        assert_detector_pass(lifecycle_report, "owner_lifecycle")
        banana_plants = [
            event
            for event in lifecycle.events
            if event.get("verb") == "PLANT"
            and event.get("kind") == "BANANA"
            and event.get("landed")
        ]
        diagonal_plants = [
            event for event in banana_plants if is_diag(tuple(event["cell"]))
        ]
        orthogonal_plants = [
            event for event in banana_plants if is_orth(tuple(event["cell"]))
        ]
        outside = [
            event for event in banana_plants if not is_ring(tuple(event["cell"]))
        ]
        harvests = [
            event
            for event in lifecycle.events
            if event.get("verb") == "HARVEST"
            and event.get("kind") == "BANANA"
            and event.get("banana_delta", 0) > 0
        ]
        wood_chops = [
            event
            for event in lifecycle.events
            if event.get("verb") == "CHOP"
            and event.get("kind") == "BANANA"
            and is_orth(tuple(event["cell"]))
            and event.get("wood_delta", 0) > 0
        ]
        banking = [
            event
            for event in lifecycle.events
            if event.get("verb") == "DROP"
            and (
                event.get("banana_bank_delta", 0) > 0
                or event.get("wood_bank_delta", 0) > 0
            )
        ]
        if not diagonal_plants:
            raise AssertionError("owner_lifecycle: no candidate-founded diagonal mother")
        if not orthogonal_plants:
            raise AssertionError("owner_lifecycle: no orthogonal banana wood tree")
        if not harvests:
            raise AssertionError("owner_lifecycle: no own banana harvest")
        if not wood_chops:
            raise AssertionError("owner_lifecycle: no completed orthogonal wood conversion")
        if not banking:
            raise AssertionError("owner_lifecycle: no banana/wood banking")
        if outside:
            raise AssertionError(f"owner_lifecycle: outside-ring plants: {outside}")
        summary["scenarios"]["lifecycle"] = {
            "verdict": "PASS",
            "diagonal_plants": len(diagonal_plants),
            "orthogonal_plants": len(orthogonal_plants),
            "harvests": len(harvests),
            "completed_wood_chops": len(wood_chops),
            "banking_events": len(banking),
            "final_inventory": list(lifecycle.inv),
        }

        # 2. Unsafe founding: a nearby harvester/chopper must prevent any
        # renewable diagonal mother from being created.
        unsafe = RecordingReferee(
            inventory=[0, 0, 0, 2, 0, 0],
            plants={},
            units={
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                1: mbt.unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
                5: mbt.unit_row(5, 1, (4, 2), cap=2, harvest=1, chop=1),
            },
        )
        unsafe_report = mbt.run_scenario("owner_unsafe", binary, unsafe, 80)
        assert_detector_pass(unsafe_report, "owner_unsafe")
        unsafe_diag = [
            event
            for event in unsafe.events
            if event.get("verb") == "PLANT"
            and event.get("kind") == "BANANA"
            and event.get("landed")
            and is_diag(tuple(event["cell"]))
        ]
        if unsafe_diag:
            raise AssertionError(f"owner_unsafe: unsafe mother founded: {unsafe_diag}")
        summary["scenarios"]["unsafe_founding"] = {
            "verdict": "PASS",
            "diagonal_plants": 0,
        }

        # 3. Dynamic loss response on a candidate-founded mother.  The
        # opponent may approach, but it must never receive the fruit.
        dynamic = clone_dynamic(mbt.scenario_r4_flip_reach())
        dynamic_report = mbt.run_scenario(
            "owner_dynamic_response", binary, dynamic, 30
        )
        assert_detector_pass(dynamic_report, "owner_dynamic_response")
        dynamic_diag = [
            event
            for event in dynamic.events
            if event.get("verb") == "PLANT"
            and event.get("kind") == "BANANA"
            and event.get("landed")
            and is_diag(tuple(event["cell"]))
        ]
        dynamic_chops = [
            event
            for event in dynamic.events
            if event.get("verb") == "CHOP"
            and event.get("kind") == "BANANA"
            and is_diag(tuple(event["cell"]))
        ]
        if not dynamic_diag:
            raise AssertionError("owner_dynamic_response: candidate never founded mother")
        if not dynamic_chops:
            raise AssertionError("owner_dynamic_response: no conversion response")
        if dynamic.units[5]["carry"][BANANA] != 0:
            raise AssertionError("owner_dynamic_response: opponent harvested our banana")
        summary["scenarios"]["dynamic_response"] = {
            "verdict": "PASS",
            "diagonal_plants": len(dynamic_diag),
            "diagonal_chop_turns": [event["turn"] for event in dynamic_chops],
            "opponent_banana_carry": dynamic.units[5]["carry"][BANANA],
        }

        # 4. Funding prefix: with no trained second worker, no banana channel
        # may activate at all.
        solo = RecordingReferee(
            inventory=[0, 0, 0, 2, 0, 0],
            plants={},
            units={
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                5: mbt.unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=1),
            },
        )
        solo_report = mbt.run_scenario("owner_funding_prefix", binary, solo, 40)
        assert_detector_pass(solo_report, "owner_funding_prefix")
        solo_banana = banana_command_turns(solo.events)
        if solo_banana:
            raise AssertionError(
                f"owner_funding_prefix: banana work before worker two: {solo_banana}"
            )
        summary["scenarios"]["funding_prefix"] = {
            "verdict": "PASS",
            "banana_command_turns": [],
        }

        # 5. A peer carrying wood owns the bank route.  Banana activation may
        # begin only after its DROP has landed.
        carrier = RecordingReferee(
            inventory=[0, 0, 0, 2, 0, 0],
            plants={},
            units={
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                2: mbt.unit_row(
                    2,
                    0,
                    (6, 1),
                    cap=2,
                    harvest=0,
                    chop=1,
                    carry=[0, 0, 0, 0, 0, 2],
                ),
                5: mbt.unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=1),
            },
        )
        carrier_report = mbt.run_scenario(
            "owner_carrier_priority", binary, carrier, 100
        )
        assert_detector_pass(carrier_report, "owner_carrier_priority")
        peer_drops = [
            event["turn"]
            for event in carrier.events
            if event.get("unit") == 2
            and event.get("verb") == "DROP"
            and event.get("wood_bank_delta", 0) > 0
        ]
        if not peer_drops:
            raise AssertionError("owner_carrier_priority: peer wood never banked")
        banana_turns = banana_command_turns(carrier.events)
        if banana_turns and min(banana_turns) <= min(peer_drops):
            raise AssertionError(
                "owner_carrier_priority: banana work displaced committed wood banking"
            )
        summary["scenarios"]["carrier_priority"] = {
            "verdict": "PASS",
            "peer_drop_turn": min(peer_drops),
            "first_banana_turn": None if not banana_turns else min(banana_turns),
            "final_inventory": list(carrier.inv),
        }

    summary["verdict"] = "PASS"
    output.mkdir(parents=True, exist_ok=True)
    (output / "owner-contract-results.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run_tests(args.candidate.resolve(), args.output.resolve())
    except Exception as exc:
        failure = {"verdict": "FAIL", "error": str(exc)}
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "owner-contract-results.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n"
        )
        print(json.dumps(failure, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
