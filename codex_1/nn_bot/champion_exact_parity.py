#!/usr/bin/env python3
"""Replay command parity for the linked exact-champion Strategy."""

from __future__ import annotations

import argparse
import ctypes
import gzip
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from local_claude_1.reconstructions.fits.reconstruct import (  # noqa: E402
    Reconstructor,
    build_game,
    parse_frame0,
)


DEFAULT_PACKAGE = (
    ROOT
    / "local_claude_1"
    / "ladder-queue"
    / "games-41208579"
    / "games-agent6670954-submission41208579.jsonl.gz"
)
DEFAULT_LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"
CHAMPION_AGENT_ID = 6670954


class ChampionExactPolicy:
    """Dependency-free ctypes client for the linked stateful strategy."""

    def __init__(self, library: Path) -> None:
        self._lib = ctypes.CDLL(str(library.resolve()))
        self._lib.tf_full_champion_create.restype = ctypes.c_void_p
        self._lib.tf_full_champion_destroy.argtypes = [ctypes.c_void_p]
        self._lib.tf_full_champion_commands_from_state.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        self._lib.tf_full_champion_commands_from_state.restype = ctypes.c_int32
        self._handle = self._lib.tf_full_champion_create()
        if not self._handle:
            raise RuntimeError("Rust champion strategy allocation failed")

    def commands(self, state: dict, seat: int) -> list[str]:
        payload = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
        source = ctypes.create_string_buffer(payload)
        output = ctypes.create_string_buffer(4096)
        status = self._lib.tf_full_champion_commands_from_state(
            self._handle,
            ctypes.cast(source, ctypes.c_void_p),
            len(payload),
            int(seat),
            ctypes.cast(output, ctypes.c_void_p),
            len(output),
        )
        if status < 0:
            raise RuntimeError(f"tf_full_champion_commands_from_state failed with {status}")
        return [command for command in output.raw[:status].decode().split(";") if command]

    def close(self) -> None:
        if self._handle:
            self._lib.tf_full_champion_destroy(self._handle)
            self._handle = None

    def __enter__(self) -> "ChampionExactPolicy":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class ReplayReconstructor(Reconstructor):
    """The existing exact reconstructor initialized from an in-memory package row."""

    def __init__(self, replay: dict) -> None:
        self.game_id = int(replay["gameId"])
        self.replay = replay
        self.frames = replay["frames"]
        width, height, rows, units, plants, inventories = parse_frame0(self.frames[0])
        self.map = {"w": width, "h": height, "rows": rows}
        self.game = build_game(width, height, rows, units, plants, inventories)
        self.unit_by_eid = {}
        self.plant_by_eid = {}
        by_id = {unit.id: unit for unit in self.game.units}
        for entity_id, unit in units.items():
            self.unit_by_eid[entity_id] = by_id[unit["id"]]
        by_pos = {plant.pos: plant for plant in self.game.plants}
        for entity_id, plant in plants.items():
            self.plant_by_eid[entity_id] = by_pos[(plant["x"], plant["y"])]
        self.mismatch = Counter()
        self.examples = {}
        self.agents = {agent["index"]: agent for agent in replay["agents"]}
        self.n_turns = (len(self.frames) - 1) // 2


def gameplay_commands(commands: list[str]) -> list[str]:
    return [command for command in commands if not command.startswith("MSG")]


def champion_seat(replay: dict) -> int:
    matches = [
        int(agent["index"])
        for agent in replay.get("agents", [])
        if agent.get("agentId") == CHAMPION_AGENT_ID
    ]
    if len(matches) != 1:
        raise ValueError(
            f"game {replay.get('gameId')} has {len(matches)} champion seats, expected one"
        )
    return matches[0]


def json_state(reconstructor: ReplayReconstructor, snapshot: dict) -> dict:
    return {
        "w": reconstructor.map["w"],
        "h": reconstructor.map["h"],
        "rows": reconstructor.map["rows"],
        "turn": snapshot["turn"],
        "inv": snapshot["inv"],
        "units": snapshot["units"],
        "plants": snapshot["plants"],
        "staged_actions": [],
    }


def load_package(path: Path) -> list[dict]:
    with gzip.open(path, "rt") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def run_gate(package: Path, library: Path, limit: int | None) -> dict:
    replays = sorted(load_package(package), key=lambda replay: int(replay["gameId"]))
    if limit is not None:
        replays = replays[:limit]
    gameplay_games_passed = 0
    gameplay_turns_passed = 0
    raw_games_passed = 0
    raw_turns_passed = 0
    reconstruction_mismatches: Counter[str] = Counter()
    gameplay_first_divergence = None
    raw_first_divergence = None
    with ChampionExactPolicy(library) as policy:
        for replay in replays:
            reconstructor = ReplayReconstructor(replay)
            states = reconstructor.run(keep_states=True)
            reconstruction_mismatches.update(reconstructor.mismatch)
            seat = champion_seat(replay)
            raw_game_matches = True
            for turn in range(1, reconstructor.n_turns + 1):
                recorded_raw = reconstructor.commands(turn)[seat]
                linked_raw = policy.commands(
                    json_state(reconstructor, states[turn - 1]), seat
                )
                if linked_raw != recorded_raw:
                    raw_game_matches = False
                    if raw_first_divergence is None:
                        raw_first_divergence = {
                            "game_id": reconstructor.game_id,
                            "turn": turn,
                            "seat": seat,
                            "linked": linked_raw,
                            "recorded": recorded_raw,
                        }
                elif raw_first_divergence is None:
                    raw_turns_passed += 1
                recorded = gameplay_commands(recorded_raw)
                linked = gameplay_commands(linked_raw)
                if linked != recorded:
                    gameplay_first_divergence = {
                        "game_id": reconstructor.game_id,
                        "turn": turn,
                        "seat": seat,
                        "linked": linked,
                        "recorded_without_msg": recorded,
                    }
                    break
                gameplay_turns_passed += 1
            if raw_game_matches:
                raw_games_passed += 1
            if gameplay_first_divergence is not None:
                break
            gameplay_games_passed += 1
    return {
        "schema_version": 1,
        "package": str(package),
        "library": str(library),
        "champion_agent_id": CHAMPION_AGENT_ID,
        "games_requested": len(replays),
        "gameplay_games_passed": gameplay_games_passed,
        "gameplay_turns_passed": gameplay_turns_passed,
        "gameplay_first_divergence": gameplay_first_divergence,
        "raw_games_passed": raw_games_passed,
        "raw_turns_passed_before_first_divergence": raw_turns_passed,
        "raw_first_divergence": raw_first_divergence,
        "reconstruction_mismatches": dict(sorted(reconstruction_mismatches.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_gate(args.package, args.library, args.limit)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0 if report["gameplay_first_divergence"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
