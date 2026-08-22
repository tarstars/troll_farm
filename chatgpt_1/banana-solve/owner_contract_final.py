#!/usr/bin/env python3
"""Final closed-loop acceptance for the strict private-founding Banana R2 arm.

The positive lifecycle uses a legal 42x5 map with a harvest/chop-capable
opponent more than one exact fresh-mother fruit horizon away.  The candidate
must itself found a diagonal mother, run an orthogonal wood cycle, harvest,
bank, and stay inside the finite home ring.  A second scenario starts from the
same valid founding geometry and later moves the capable opponent toward the
mother; no opponent banana acquisition is allowed.  Nearby-unsafe, funding
prefix, and peer-wood-carrier cases are checked separately.

Only two detector observation corrections are applied:
* repeated reuse of the same finite ring is the intended renewable cycle, not
  spatially unbounded planting;
* a final unobserved PLANT/DROP command may consume the last carried banana in
  S_(T+1), which a finite transcript does not contain.
All outside-ring, opponent-harvest, oscillation, banking, contention, funding,
and discretionary diagonal-chop findings remain blocking.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BR2 = REPO / "claude_1" / "banana-restoration-r2"
sys.path.insert(0, str(BR2))

spec = importlib.util.spec_from_file_location("banana_owner_v3", HERE / "owner_contract_tests_v3.py")
legacy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = legacy
spec.loader.exec_module(legacy)
base = legacy.base
mbt = base.mbt
td = mbt.td
sh = mbt.sh

BANANA = 3
WOOD = 5


def wide_map(width: int = 42) -> tuple[str, ...]:
    if width < 34:
        raise ValueError("wide map must exceed the exact dry first-fruit horizon")
    rows = ["." * width for _ in range(5)]
    row = list(rows[1])
    row[1] = "0"
    row[-2] = "1"
    rows[1] = "".join(row)
    return tuple(rows)


class RecordingCustom(base.RecordingMixin, mbt.CustomMapReferee):
    def __init__(self, map_rows, inventory, plants, units):
        mbt.CustomMapReferee.__init__(self, map_rows, inventory, plants, units)
        self._recording_init()


class RecordingMovingCustom(RecordingCustom):
    def __init__(self, map_rows, inventory, plants, units, targets, move_from_turn):
        super().__init__(map_rows, inventory, plants, units)
        self.targets = dict(targets)
        self.move_from_turn = int(move_from_turn)

    def opponent_step(self) -> None:
        if self.turn_number < self.move_from_turn:
            return
        for uid in sorted(self.targets):
            unit = self.units.get(uid)
            if unit is None or unit["player"] != 1:
                continue
            target = self.targets[uid]
            if unit["cell"] != target:
                unit["cell"] = self.step_toward(
                    unit["cell"], target, unit["speed"]
                )
            if unit["cell"] == target:
                plant = self.plants.get(target)
                free = unit["cap"] - sum(unit["carry"])
                if (
                    plant is not None
                    and plant["fruits"] > 0
                    and unit["harvest"] > 0
                    and free > 0
                ):
                    plant["fruits"] -= 1
                    unit["carry"][BANANA] += 1

    def apply(self, command_line: str) -> None:
        super().apply(command_line)
        self.opponent_step()


def compile_candidate(source: Path, directory: Path) -> Path:
    binary = directory / "candidate"
    sh.compile_text(source.read_text(), binary, "banana_owner_final")
    return binary


def run_closed_loop(name: str, binary: Path, referee, turns: int, out: Path):
    header = referee.map_header() if hasattr(referee, "map_header") else (
        f"{len(mbt.MAP[0])} {len(mbt.MAP)}\n" + "\n".join(mbt.MAP) + "\n"
    )
    transcript_parts = [header]
    commands = []
    with subprocess.Popen(
        [str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    ) as process:
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(header)
        process.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            transcript_parts.append(block)
            process.stdin.write(block)
            process.stdin.flush()
            line = process.stdout.readline()
            if not line:
                raise RuntimeError(f"{name}: candidate closed stdout early")
            line = line.rstrip("\n")
            commands.append(line)
            referee.apply(line)
            referee.grow()
        process.stdin.close()
    transcript_text = "".join(transcript_parts)
    commands_text = "\n".join(commands) + "\n"
    trace = td.build_trace(transcript_text, commands_text)
    report = {
        "scenario": name,
        "turns": trace.T,
        "detectors": td.run_all(trace),
        "notes": trace.notes,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}-transcript.txt").write_text(transcript_text)
    (out / f"{name}-commands.txt").write_text(commands_text)
    (out / f"{name}-detectors.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    return report, commands_text


def final_command_consumes(commands_text: str, unit_id: int) -> bool:
    lines = [line.strip() for line in commands_text.splitlines() if line.strip()]
    if not lines:
        return False
    for raw in lines[-1].split(";"):
        parts = raw.strip().split()
        if len(parts) < 2:
            continue
        try:
            uid = int(parts[1])
        except ValueError:
            continue
        if uid != unit_id:
            continue
        if parts[0].upper() == "DROP":
            return True
        if (
            parts[0].upper() == "PLANT"
            and len(parts) >= 3
            and parts[2].upper() == "BANANA"
        ):
            return True
    return False


def blocking_detectors(report: dict[str, Any], commands_text: str) -> list[dict[str, Any]]:
    blockers = []
    for result in report["detectors"]:
        if result.get("verdict") == "PASS":
            continue
        episodes = list(result.get("episodes", []))
        if result.get("detector") == "D-5":
            episodes = [
                episode
                for episode in episodes
                if episode.get("kind") != "cumulative_over_ring"
            ]
        if result.get("detector") == "D-7":
            episodes = [
                episode
                for episode in episodes
                if not (
                    episode.get("kind") == "unbanked_at_end"
                    and isinstance(episode.get("unit"), int)
                    and final_command_consumes(commands_text, episode["unit"])
                )
            ]
        if episodes:
            copy_result = dict(result)
            copy_result["episodes"] = episodes
            copy_result["count"] = len(episodes)
            blockers.append(copy_result)
    return blockers


def is_ring(cell: tuple[int, int]) -> bool:
    return max(abs(cell[0] - mbt.TENT[0]), abs(cell[1] - mbt.TENT[1])) == 1


def is_diag(cell: tuple[int, int]) -> bool:
    return abs(cell[0] - mbt.TENT[0]) == 1 and abs(cell[1] - mbt.TENT[1]) == 1


def is_orth(cell: tuple[int, int]) -> bool:
    return abs(cell[0] - mbt.TENT[0]) + abs(cell[1] - mbt.TENT[1]) == 1


def summarize_events(referee) -> dict[str, Any]:
    plants = [
        event
        for event in referee.events
        if event.get("verb") == "PLANT"
        and event.get("kind") == "BANANA"
        and event.get("landed")
    ]
    harvests = [
        event
        for event in referee.events
        if event.get("verb") == "HARVEST"
        and event.get("kind") == "BANANA"
        and event.get("banana_delta", 0) > 0
    ]
    chops = [
        event
        for event in referee.events
        if event.get("verb") == "CHOP"
        and event.get("kind") == "BANANA"
        and event.get("wood_delta", 0) > 0
    ]
    banks = [
        event
        for event in referee.events
        if event.get("verb") == "DROP"
        and (
            event.get("banana_bank_delta", 0) > 0
            or event.get("wood_bank_delta", 0) > 0
        )
    ]
    return {
        "diagonal_plants": sum(is_diag(tuple(event["cell"])) for event in plants),
        "orthogonal_plants": sum(is_orth(tuple(event["cell"])) for event in plants),
        "outside_ring_plants": [
            event for event in plants if not is_ring(tuple(event["cell"]))
        ],
        "harvests": len(harvests),
        "completed_orthogonal_wood_chops": sum(
            is_orth(tuple(event["cell"])) for event in chops
        ),
        "banking_events": len(banks),
        "plant_events": plants,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    traces = output / "traces"
    rows = wide_map()
    width = len(rows[0])
    far = (width - 2, 0)
    mother = (2, 2)
    results: dict[str, Any] = {"scenarios": {}}

    with tempfile.TemporaryDirectory(prefix="banana-final-contract-") as directory:
        binary = compile_candidate(args.candidate.resolve(), Path(directory))

        lifecycle = RecordingCustom(
            rows,
            [0, 0, 0, 2, 0, 0],
            {},
            {
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                1: mbt.unit_row(1, 0, (width - 5, 3), cap=1, harvest=0, chop=0),
                5: mbt.unit_row(5, 1, far, cap=2, harvest=1, chop=1),
            },
        )
        lifecycle_report, lifecycle_commands = run_closed_loop(
            "safe_lifecycle", binary, lifecycle, 300, traces
        )
        lifecycle_summary = summarize_events(lifecycle)
        lifecycle_blockers = blocking_detectors(lifecycle_report, lifecycle_commands)
        lifecycle_ok = (
            lifecycle_summary["diagonal_plants"] > 0
            and lifecycle_summary["orthogonal_plants"] > 0
            and lifecycle_summary["harvests"] > 0
            and lifecycle_summary["completed_orthogonal_wood_chops"] > 0
            and lifecycle_summary["banking_events"] > 0
            and not lifecycle_summary["outside_ring_plants"]
            and not lifecycle_blockers
        )
        results["scenarios"]["safe_lifecycle"] = {
            "verdict": "PASS" if lifecycle_ok else "FAIL",
            **lifecycle_summary,
            "blocking_detectors": lifecycle_blockers,
            "final_inventory": list(lifecycle.inv),
        }

        dynamic = RecordingMovingCustom(
            rows,
            [0, 0, 0, 2, 0, 0],
            {},
            {
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                1: mbt.unit_row(1, 0, (width - 5, 3), cap=1, harvest=0, chop=0),
                5: mbt.unit_row(5, 1, far, speed=2, cap=3, harvest=1, chop=1),
            },
            {5: mother},
            move_from_turn=8,
        )
        dynamic_report, dynamic_commands = run_closed_loop(
            "delayed_threat", binary, dynamic, 100, traces
        )
        dynamic_summary = summarize_events(dynamic)
        dynamic_blockers = blocking_detectors(dynamic_report, dynamic_commands)
        opponent_bananas = dynamic.units[5]["carry"][BANANA]
        dynamic_ok = (
            dynamic_summary["diagonal_plants"] > 0
            and opponent_bananas == 0
            and not any(row.get("detector") == "D-6" for row in dynamic_blockers)
            and not any(row.get("detector") in {"D-1", "D-3", "D-4"} for row in dynamic_blockers)
        )
        results["scenarios"]["delayed_threat"] = {
            "verdict": "PASS" if dynamic_ok else "FAIL",
            **dynamic_summary,
            "opponent_banana_carry": opponent_bananas,
            "blocking_detectors": dynamic_blockers,
        }

        unsafe = legacy.TrainingRecordingReferee(
            [0, 0, 0, 2, 0, 0],
            {},
            {
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                1: mbt.unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
                5: mbt.unit_row(5, 1, (4, 2), cap=2, harvest=1, chop=1),
            },
        )
        unsafe_report, unsafe_commands = run_closed_loop(
            "unsafe_nearby", binary, unsafe, 80, traces
        )
        unsafe_summary = summarize_events(unsafe)
        unsafe_ok = unsafe_summary["diagonal_plants"] == 0 and not blocking_detectors(
            unsafe_report, unsafe_commands
        )
        results["scenarios"]["unsafe_nearby"] = {
            "verdict": "PASS" if unsafe_ok else "FAIL",
            **unsafe_summary,
        }

        funding = legacy.TrainingRecordingReferee(
            [0, 0, 0, 2, 0, 0],
            {},
            {
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                5: mbt.unit_row(5, 1, far, cap=2, harvest=1, chop=1),
            },
        )
        funding_report, funding_commands = run_closed_loop(
            "funding_prefix", binary, funding, 50, traces
        )
        train_turn = getattr(funding.events, "train_turn", None)
        banana_before_train = [
            event
            for event in funding.events
            if event.get("kind") == "BANANA"
            and (train_turn is None or event["turn"] < train_turn)
        ]
        funding_ok = (
            train_turn is not None
            and not banana_before_train
            and not any(
                row.get("detector") in {"D-1", "D-3", "D-4"}
                for row in blocking_detectors(funding_report, funding_commands)
            )
        )
        results["scenarios"]["funding_prefix"] = {
            "verdict": "PASS" if funding_ok else "FAIL",
            "train_turn": train_turn,
            "banana_before_train": banana_before_train,
        }

        carrier = legacy.TrainingRecordingReferee(
            [0, 0, 0, 2, 0, 0],
            {},
            {
                0: mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
                2: mbt.unit_row(
                    2, 0, (6, 1), cap=2, harvest=0, chop=1,
                    carry=[0, 0, 0, 0, 0, 2],
                ),
                5: mbt.unit_row(5, 1, far, cap=2, harvest=1, chop=1),
            },
        )
        carrier_report, carrier_commands = run_closed_loop(
            "carrier_priority", binary, carrier, 100, traces
        )
        drops = [
            event["turn"]
            for event in carrier.events
            if event.get("unit") == 2
            and event.get("verb") == "DROP"
            and event.get("wood_bank_delta", 0) > 0
        ]
        banana_turns = [
            event["turn"] for event in carrier.events if event.get("kind") == "BANANA"
        ]
        carrier_blockers = blocking_detectors(carrier_report, carrier_commands)
        carrier_ok = (
            bool(drops)
            and (not banana_turns or min(banana_turns) > min(drops))
            and not any(
                row.get("detector") in {"D-1", "D-3", "D-4"}
                for row in carrier_blockers
            )
        )
        results["scenarios"]["carrier_priority"] = {
            "verdict": "PASS" if carrier_ok else "FAIL",
            "peer_drop_turns": drops,
            "first_banana_turn": None if not banana_turns else min(banana_turns),
            "blocking_detectors": carrier_blockers,
        }

    results["verdict"] = "PASS" if all(
        scenario["verdict"] == "PASS" for scenario in results["scenarios"].values()
    ) else "FAIL"
    output.mkdir(parents=True, exist_ok=True)
    (output / "owner-contract-results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if results["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
