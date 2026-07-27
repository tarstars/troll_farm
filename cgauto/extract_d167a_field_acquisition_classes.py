#!/usr/bin/env python3
"""Recover D167a field acquisition-path classes for D166's PLANT-return cycles.

Reuses (unchanged): cgauto.analyze_d164a_current_field_macro_transitions for state
decoding/generation reconstruction, and cgauto.extract_d166a_field_return_classes for
occurrence enumeration and exact P->S->P cycle selection. This module adds only the
species-provenance acquisition-path ledger described in the D167a protocol.
"""

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
from cgauto import extract_d166a_field_return_classes as d166fx


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
LOCK = BASE / "d167a-successor-acquisition-path-lock.json"
SNAPSHOT = ROOT / "data/external/arena-corpus/snapshots/20260723T074715Z-d164a"
ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d167a-successor-acquisition-path"
DEFAULT_OUTPUT = ARTIFACT_BASE / "d167a-field-acquisition-classes-jobs20.jsonl"

FRUIT_ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA")
TAG_TO_CLASS = {
    "BANK": "BANK_SEED",
    "FIELD": "FIELD_FRUIT",
    "OPPONENT": "OPPONENT_DERIVED",
    "OTHER": "OTHER_MIXED",
}
REMOVAL_PRIORITY = ("OTHER", "OPPONENT", "BANK", "FIELD")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    if lock.get("schema") != "troll-farm-d167a-successor-acquisition-path-lock-v1":
        raise ValueError("unknown D167a lock schema")
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"D167a frozen input differs: {relative}")
    return lock


def harvest_tag(origin: str | None) -> str:
    if origin in ("actor", "natural"):
        return "FIELD"
    if origin == "opponent":
        return "OPPONENT"
    return "OTHER"


def remove_units(tags: dict[str, int], count: int) -> bool:
    """Remove `count` units in a fixed deterministic priority order. Returns True
    iff the removal drew from a genuinely mixed (>1 distinct tag) stash."""

    distinct_before = sum(1 for value in tags.values() if value > 0)
    remaining = count
    for tag in REMOVAL_PRIORITY:
        if remaining <= 0:
            break
        take = min(remaining, tags.get(tag, 0))
        tags[tag] = tags.get(tag, 0) - take
        remaining -= take
    return distinct_before > 1 and count > 0


def classify_acquisition(history_events: list[dict], species: str) -> dict:
    """Walk the species-provenance ledger exactly as the D167a local Rust runner
    does, over `history_events` (sorted, filtered to this worker's ordinal,
    successful, MATERIAL_VERBS, turn <= return_turn — the *entire* relevant
    history, not just the post-suppression window). A full-history walk is
    required because the field data (unlike the local 0/237 fact from D166)
    sometimes carries a seed *through* the suppression action rather than
    acquiring it afterward (see the result doc's field-only finding)."""

    tags: dict[str, int] = defaultdict(int)
    ambiguous_partial_spends = 0
    earliest_contributing_turn = None
    for index, event in enumerate(history_events):
        is_last = index == len(history_events) - 1
        verb = event["verb"]
        gained = event["gained"]
        spent = event["spent"]
        if verb == "HARVEST" and gained.get(species, 0) > 0:
            tags[harvest_tag(event["target_origin"])] += gained[species]
            earliest_contributing_turn = earliest_contributing_turn or event["turn"]
        elif verb == "PICK" and gained.get(species, 0) > 0:
            tags["BANK"] += gained[species]
            earliest_contributing_turn = earliest_contributing_turn or event["turn"]
        elif verb == "DROP" and spent.get(species, 0) > 0:
            # DROP always banks the full carry: clear every tag for this species.
            for tag in list(tags):
                tags[tag] = 0
            earliest_contributing_turn = None
        elif verb == "PLANT" and spent.get(species, 0) > 0:
            if is_last:
                # Terminal return: classify from the ledger's pre-spend state.
                break
            if remove_units(tags, spent[species]):
                ambiguous_partial_spends += 1

    distinct = sorted(tag for tag, count in tags.items() if count > 0)
    if len(distinct) == 1:
        acquisition_class = TAG_TO_CLASS[distinct[0]]
    elif not distinct:
        acquisition_class = "EMPTY_LEDGER_INTEGRITY_FAILURE"
    else:
        acquisition_class = "OTHER_MIXED"
    return {
        "acquisition_class": acquisition_class,
        "acquisition_tags": "+".join(distinct),
        "bank_units": tags.get("BANK", 0),
        "field_units": tags.get("FIELD", 0),
        "opponent_units": tags.get("OPPONENT", 0),
        "other_units": tags.get("OTHER", 0),
        "ledger_integrity_ok": bool(distinct),
        "ledger_ambiguous_partial_spends": ambiguous_partial_spends,
        "earliest_contributing_turn": earliest_contributing_turn,
    }


def window_waypoints(window_events: list[dict]) -> dict:
    """Descriptive-only view of the command trajectory strictly between the
    suppression turn and the return PLANT (the literal "path" of the protocol),
    independent of where the classification ledger ultimately finds the seed."""

    waypoints = [
        {
            "turn": event["turn"],
            "verb": event["verb"],
            "target_origin": event["target_origin"],
            "target_kind": event["target_kind"],
            "gained": event["gained"],
            "spent": event["spent"],
        }
        for event in window_events
    ]
    return {
        "waypoints": waypoints,
        "material_waypoints": max(0, len(window_events) - 1),
    }


def idle_and_cell_diagnostics(
    events: list[dict],
    states: list[dict],
    unit_id: int,
    ordinal: int,
    suppression_turn: int,
    return_turn: int,
) -> dict:
    """An idle turn is a turn with no position change AND no successful action of
    any kind (mirrors the Rust local runner: a stationary HARVEST/PICK/DROP/CHOP/
    MINE is real work, not idling, even though the worker does not move)."""

    def unit_pos(state: dict) -> tuple[int, int] | None:
        for unit in state["units"]:
            if int(unit["id"]) == unit_id:
                return (int(unit["x"]), int(unit["y"]))
        return None

    success_turns = {
        int(event["turn"])
        for event in events
        if int(event["ordinal"]) == ordinal and event["success"]
    }

    visited = set()
    idle_turns = 0
    for turn in range(suppression_turn + 1, return_turn + 1):
        after_pos = unit_pos(states[turn])
        if after_pos is not None:
            visited.add(after_pos)
        if turn not in success_turns:
            idle_turns += 1
    return {
        "distinct_cells_visited": len(visited),
        "idle_turns": idle_turns,
        "single_persistent_job": idle_turns == 0,
    }


def entry_carry_nonzero(states: list[dict], unit_id: int, suppression_turn: int) -> bool:
    state = states[suppression_turn]
    unit = next((u for u in state["units"] if int(u["id"]) == unit_id), None)
    if unit is None:
        return True
    return any(int(unit["carry"][index]) > 0 for index in range(4))


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
        raise ValueError(f"D167a decoded-state mismatch in game {game['gameId']}")
    analysis = d164.analyze_players(states, trajectory)[seat]
    worker_ordinals = {
        int(worker["unit_id"]): int(worker["ordinal"])
        for worker in analysis["workers"]
    }
    events, generations, lineage, quality = d164.reconstruct_generation_actions(
        states, trajectory, seat, worker_ordinals
    )
    d164.resolve_joint_births(events, generations, quality, states, trajectory)
    successful = [
        event
        for event in events
        if event["success"] and event["verb"] in d164.MATERIAL_VERBS
    ]
    cycle = d166fx.first_cycle(successful)
    base = {
        "game_id": int(game["gameId"]),
        "actor_id": int(actor_id),
        "actor": metadata["pseudo"],
        "source_rank": int(metadata["source_rank"]),
        "cohort": metadata["cohort"],
        "seat": seat,
        "in_scope": False,
        "has_cycle": cycle is not None,
    }
    if cycle is None:
        return {**base, "return_verb": None}
    prior, suppression, returned = cycle
    return_verb = returned["verb"]
    base["return_verb"] = return_verb
    if return_verb != "PLANT" or metadata["cohort"] not in ("rank_1_5", "rank_6_20"):
        return {**base, "in_scope": False}

    unit_id = int(prior["unit_id"])
    suppression_turn = int(suppression["turn"])
    return_turn = int(returned["turn"])
    return_generation = returned.get("created_generation")
    species = generations.get(return_generation, {}).get("kind") if return_generation else None
    if species not in FRUIT_ITEMS:
        raise ValueError(
            f"D167a expected a fruit species at the PLANT return in game {game['gameId']}, "
            f"got {species!r}"
        )

    ordinal_material_events = sorted(
        (
            event
            for event in events
            if int(event["ordinal"]) == int(prior["ordinal"])
            and event["success"]
            and event["verb"] in d164.MATERIAL_VERBS
            and event["turn"] <= return_turn
        ),
        key=lambda event: event["turn"],
    )
    window_events = [
        event for event in ordinal_material_events if event["turn"] > suppression_turn
    ]
    if not window_events or window_events[-1]["turn"] != return_turn or window_events[-1]["verb"] != "PLANT":
        raise ValueError(
            f"D167a window does not end at the expected return PLANT in game {game['gameId']}"
        )
    if (
        not ordinal_material_events
        or ordinal_material_events[-1]["turn"] != return_turn
        or ordinal_material_events[-1]["verb"] != "PLANT"
    ):
        raise ValueError(
            f"D167a full history does not end at the expected return PLANT in game {game['gameId']}"
        )

    classification = classify_acquisition(ordinal_material_events, species)
    waypoints = window_waypoints(window_events)
    diagnostics = idle_and_cell_diagnostics(
        events, states, unit_id, int(prior["ordinal"]), suppression_turn, return_turn
    )
    carry_nonzero_at_entry = entry_carry_nonzero(states, unit_id, suppression_turn)
    acquisition_predates_suppression = bool(
        classification["earliest_contributing_turn"] is not None
        and classification["earliest_contributing_turn"] <= suppression_turn
    )
    return {
        **base,
        "in_scope": True,
        "worker_ordinal": int(prior["ordinal"]),
        "unit_id": unit_id,
        "suppression_turn": suppression_turn,
        "return_turn": return_turn,
        "path_length_turns": return_turn - suppression_turn,
        "species_planted": species,
        "entry_carry_nonzero": carry_nonzero_at_entry,
        "acquisition_predates_suppression": acquisition_predates_suppression,
        **classification,
        **waypoints,
        **diagnostics,
    }


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
    work = d166fx.occurrences()
    if len(work) != 392:
        raise ValueError(f"D167a expected 392 occurrences, found {len(work)}")
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
    in_scope = [row for row in rows if row["in_scope"]]
    atomic_write_rows(output, in_scope)
    return in_scope


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
    print(
        json.dumps(
            {
                "rows": len(rows),
                "rank_1_5": sum(row["cohort"] == "rank_1_5" for row in rows),
                "rank_6_20": sum(row["cohort"] == "rank_6_20" for row in rows),
                "output": str(args.output),
                "sha256": sha256(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
