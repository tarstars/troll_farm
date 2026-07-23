#!/usr/bin/env python3
"""Compare a local opening planner with one replay agent's trained workers."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def parse_train(command: str) -> tuple[int, int, int, int]:
    fields = command.split()
    if len(fields) != 5 or fields[0] != "TRAIN":
        raise ValueError(f"bad TRAIN command {command!r}")
    return tuple(int(value) for value in fields[1:])


def read_plans(path: Path, policy: str, seat: int = 0) -> dict[int, tuple[int, ...]]:
    plans = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row["policy"] != policy or int(row["seat"]) != seat:
                continue
            game_id = int(row["seed"])
            if game_id in plans:
                raise ValueError(f"duplicate plan for game {game_id}")
            plans[game_id] = parse_train(row["train"])
    return plans


def audit(analysis: dict, agent_id: int, plans: dict[int, tuple[int, ...]], policy: str) -> dict:
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    expected = {row["game_id"] for row in occurrences}
    if set(plans) != expected:
        raise ValueError(
            f"plan coverage mismatch; missing={sorted(expected - set(plans))[:5]}, "
            f"extra={sorted(set(plans) - expected)[:5]}"
        )
    rows = []
    for occurrence in occurrences:
        events = occurrence["training_events"]
        if len(events) != 1:
            raise ValueError(
                f"game {occurrence['game_id']} has {len(events)} successful trains"
            )
        event = events[0]
        actual = tuple(event["spec"])
        planned = plans[occurrence["game_id"]]
        maximum = tuple(event["max_affordable_spec"])
        max_hp0 = (maximum[0], maximum[1], 0, maximum[3])
        rows.append(
            {
                "game_id": occurrence["game_id"],
                "actual_turn": event["turn"],
                "actual": actual,
                "planned": planned,
                "exact": actual == planned,
                "talent_l1": sum(abs(left - right) for left, right in zip(actual, planned)),
                "actual_is_max_affordable_hp0": actual == max_hp0,
                "first_affordable_turn": event["first_affordable_turn"],
                "delay_after_affordable": event["delay_after_affordable"],
            }
        )
    return {
        "schema": 1,
        "scope": (
            "observational replay worker specs versus a turn-one local opening plan; "
            "planner alignment is not command imitation or causal value evidence"
        ),
        "agent_id": agent_id,
        "policy": policy,
        "games": len(rows),
        "planned_spec_exact": sum(row["exact"] for row in rows),
        "mean_talent_l1": statistics.mean(row["talent_l1"] for row in rows),
        "maximum_talent_l1": max(row["talent_l1"] for row in rows),
        "actual_max_affordable_hp0": sum(
            row["actual_is_max_affordable_hp0"] for row in rows
        ),
        "trained_on_first_chosen_spec_affordability": sum(
            row["delay_after_affordable"] == 0 for row in rows
        ),
        "rows": rows,
        "interpretation_limit": (
            "The local plan is computed from turn-one state. The replay agent's max-affordable "
            "spec is measured at its actual train turn. Matching specs do not prove matching "
            "pre-train trajectories, train timing, targets, or terminal strength."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--plans", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(
        json.loads(args.analysis.read_text()),
        args.agent_id,
        read_plans(args.plans, args.policy),
        args.policy,
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "games",
                    "planned_spec_exact",
                    "mean_talent_l1",
                    "maximum_talent_l1",
                    "actual_max_affordable_hp0",
                    "trained_on_first_chosen_spec_affordability",
                )
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
