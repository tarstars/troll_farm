#!/usr/bin/env python3
"""Extract exact first P→S→P return classes from the immutable D164 field panel."""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import tempfile

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import analyze_d164a_current_field_macro_transitions as d164


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
LOCK = BASE / "d166a-producer-job-successor-affordance-audit-lock.json"
SNAPSHOT = ROOT / "data/external/arena-corpus/snapshots/20260723T074715Z-d164a"
ARTIFACT_BASE = (
    ROOT
    / "artifacts"
    / "experiments"
    / "d166a-producer-job-successor-affordance"
)
DEFAULT_OUTPUT = ARTIFACT_BASE / "d166a-field-return-classes-jobs20.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    if lock.get("schema") != "troll-farm-d166a-producer-job-successor-affordance-lock-v1":
        raise ValueError("unknown D166 lock schema")
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"D166 frozen input differs: {relative}")
    return lock


def role(event: dict) -> str | None:
    if event["verb"] == "PLANT" and event["created_origin"] == "actor":
        return "P"
    if event["verb"] == "HARVEST" and event["target_origin"] == "actor":
        return "P"
    if event["verb"] == "CHOP" and event["target_origin"] == "opponent":
        return "S"
    return None


def generation_id(event: dict) -> str | None:
    return event.get("created_generation") or event.get("target_generation")


def generation_cell(generations: dict, identifier: str | None) -> list[int] | None:
    if identifier is None or identifier not in generations:
        return None
    return [int(value) for value in generations[identifier]["cell"]]


def first_cycle(events: list[dict]) -> list[dict] | None:
    by_worker: dict[int, list[dict]] = defaultdict(list)
    for event in events:
        by_worker[int(event["ordinal"])].append(event)
    cycles = []
    for ordinal, rows in sorted(by_worker.items()):
        compressed = []
        for event in sorted(rows, key=lambda row: (row["turn"], row["ordinal"])):
            event_role = role(event)
            if event_role is not None and (
                not compressed or compressed[-1][0] != event_role
            ):
                compressed.append((event_role, event))
        selected = []
        index = 0
        for event_role, event in compressed:
            if event_role == ("P", "S", "P")[index]:
                selected.append(event)
                index += 1
                if index == 3:
                    cycles.append((int(selected[1]["turn"]), ordinal, selected))
                    break
    return min(cycles, default=(0, 0, None))[2] if cycles else None


def live_generation(
    lineage: list[dict], identifier: str | None, action_turn: int
) -> bool:
    if identifier is None or not lineage:
        return False
    before_index = max(0, min(action_turn - 1, len(lineage) - 1))
    return identifier in set(lineage[before_index].values())


def analyze_occurrence(task: dict, actor_id: int, metadata: dict) -> dict:
    game = task["game"]
    player_row = next(
        row for row in game["players"] if int(row.get("agentId", -1)) == actor_id
    )
    seat = int(player_row["index"])
    raw = json.loads(Path(task["raw_path"]).read_text())
    trajectory = d164.read_jsonl(Path(task["trajectory_path"]))
    _map, states, unknown = d164.decoded_states(raw, trajectory)
    if unknown or len(states) != len(trajectory) + 1:
        raise ValueError(f"D166 decoded-state mismatch in game {game['gameId']}")
    analysis = d164.analyze_players(states, trajectory)[seat]
    worker_ordinals = {
        int(worker["unit_id"]): int(worker["ordinal"])
        for worker in analysis["workers"]
    }
    events, generations, lineage, quality = d164.reconstruct_generation_actions(
        states, trajectory, seat, worker_ordinals
    )
    joint_repairs = d164.resolve_joint_births(
        events, generations, quality, states, trajectory
    )
    successful = [
        event
        for event in events
        if event["success"] and event["verb"] in d164.MATERIAL_VERBS
    ]
    cycle = first_cycle(successful)
    base = {
        "game_id": int(game["gameId"]),
        "actor_id": int(actor_id),
        "actor": metadata["pseudo"],
        "source_rank": int(metadata["source_rank"]),
        "cohort": metadata["cohort"],
        "seat": seat,
        "decoded_turns": len(states) - 1,
        "trajectory_turns": len(trajectory),
        "unknown_diff_updates": int(unknown),
        "joint_birth_repairs": joint_repairs,
        "unknown_births": int(quality.get("unknown_births", 0)),
        "ambiguous_births": int(quality.get("ambiguous_births", 0)),
        "has_cycle": cycle is not None,
    }
    if cycle is None:
        return {
            **base,
            "worker_ordinal": -1,
            "unit_id": -1,
            "prior_verb": None,
            "prior_turn": -1,
            "prior_generation": None,
            "prior_cell": None,
            "prior_kind": None,
            "suppression_turn": -1,
            "suppression_generation": None,
            "suppression_cell": None,
            "suppression_kind": None,
            "workforce_at_suppression": -1,
            "return_verb": None,
            "return_turn": -1,
            "return_generation": None,
            "return_cell": None,
            "return_kind": None,
            "suppression_duration": -1,
            "prior_generation_live_at_suppression": False,
            "return_generation_live_at_suppression": False,
            "return_reuses_prior_generation": False,
            "return_reuses_prior_cell": False,
        }

    prior, suppression, returned = cycle
    prior_generation = generation_id(prior)
    suppression_generation = generation_id(suppression)
    return_generation = generation_id(returned)
    prior_cell = generation_cell(generations, prior_generation)
    suppression_cell = generation_cell(generations, suppression_generation)
    return_cell = generation_cell(generations, return_generation)
    suppression_turn = int(suppression["turn"])
    return {
        **base,
        "worker_ordinal": int(prior["ordinal"]),
        "unit_id": int(prior["unit_id"]),
        "prior_verb": prior["verb"],
        "prior_turn": int(prior["turn"]),
        "prior_generation": prior_generation,
        "prior_cell": prior_cell,
        "prior_kind": (
            generations.get(prior_generation, {}).get("kind")
            if prior_generation is not None
            else None
        ),
        "suppression_turn": suppression_turn,
        "suppression_generation": suppression_generation,
        "suppression_cell": suppression_cell,
        "suppression_kind": suppression.get("target_kind"),
        "workforce_at_suppression": int(suppression["workforce"]),
        "return_verb": returned["verb"],
        "return_turn": int(returned["turn"]),
        "return_generation": return_generation,
        "return_cell": return_cell,
        "return_kind": (
            generations.get(return_generation, {}).get("kind")
            if return_generation is not None
            else None
        ),
        "suppression_duration": int(returned["turn"]) - suppression_turn,
        "prior_generation_live_at_suppression": live_generation(
            lineage, prior_generation, suppression_turn
        ),
        "return_generation_live_at_suppression": live_generation(
            lineage, return_generation, suppression_turn
        ),
        "return_reuses_prior_generation": (
            prior_generation is not None and prior_generation == return_generation
        ),
        "return_reuses_prior_cell": (
            prior_cell is not None and prior_cell == return_cell
        ),
    }


def occurrences() -> list[tuple[dict, int, dict]]:
    loaded = d164.load_open_inputs(SNAPSHOT)
    players = json.loads((SNAPSHOT / "players.json").read_text())
    top = {
        int(row["agent_id"]): row
        for row in players
        if "legend_top20" in (row.get("groups") or [])
    }
    resident_id = int(loaded["resident_agent_id"])
    resident_row = next(
        row for row in players if int(row["agent_id"]) == resident_id
    )
    result = []
    for task in loaded["tasks"]:
        present = {int(row.get("agentId", -1)) for row in task["game"]["players"]}
        for actor_id in sorted(set(task["top_source_ids"]) & present):
            source = top[actor_id]
            result.append(
                (
                    task,
                    actor_id,
                    {
                        "pseudo": source["pseudo"],
                        "source_rank": int(source["source_rank"]),
                        "cohort": (
                            "rank_1_5"
                            if int(source["source_rank"]) <= 5
                            else "rank_6_20"
                        ),
                    },
                )
            )
        if resident_id in present:
            result.append(
                (
                    task,
                    resident_id,
                    {
                        "pseudo": resident_row["pseudo"],
                        "source_rank": int(resident_row["source_rank"]),
                        "cohort": "resident",
                    },
                )
            )
    return sorted(result, key=lambda item: (item[1], int(item[0]["game"]["gameId"])))


def atomic_write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            for row in sorted(
                rows, key=lambda item: (item["actor_id"], item["game_id"])
            ):
                target.write(
                    json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n"
                )
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def run(output: Path, jobs: int) -> list[dict]:
    verify_lock()
    work = occurrences()
    if len(work) != 392:
        raise ValueError(f"D166 expected 392 occurrences, found {len(work)}")
    if jobs == 1:
        rows = [analyze_occurrence(*item) for item in work]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            rows = list(
                executor.map(
                    analyze_occurrence,
                    (task for task, _, _ in work),
                    (actor_id for _, actor_id, _ in work),
                    (metadata for _, _, metadata in work),
                    chunksize=2,
                )
            )
    atomic_write_rows(output, rows)
    return rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    if not 1 <= args.jobs <= 32:
        raise ValueError("jobs must be between 1 and 32")
    rows = run(args.output, args.jobs)
    counts = {
        cohort: sum(row["has_cycle"] for row in rows if row["cohort"] == cohort)
        for cohort in ("rank_1_5", "rank_6_20", "resident")
    }
    print(
        json.dumps(
            {
                "rows": len(rows),
                "cycles": counts,
                "output": str(args.output),
                "sha256": sha256(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
