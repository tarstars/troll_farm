#!/usr/bin/env python3
"""Command and referee parity gates for the linked exact-champion Strategy.

The load-bearing ``paired`` mode starts from completed Rust full-environment
games.  The linked champion has therefore already consumed the environment's
exact state and emitted the commands retained in each replay.  This script
renders those same pre-turn states through the platform text protocol, feeds
them in order to the authoritative standalone submission, and compares the two
stateful command streams.  The replay is also checked transition by transition
and at its terminal state with the independent Python simulator.

``recorded-proxy`` preserves the earlier diagnostic against reconstructed
ladder games.  Those replays do not contain literal player stdin and are not a
command-parity authority.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import json
import selectors
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
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
DEFAULT_MAPS = ROOT / "local_claude_1" / "nn-bot" / "maps-slice-1000.jsonl"
AUTHORITATIVE_SOURCE = (
    ROOT / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
)
AUTHORITATIVE_SHA256 = "0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c"
CHAMPION_AGENT_ID = 6670954
CHAMPION_OPPONENT_ID = 7
POLICY_MODES = ("random_legal", "first_legal", "middle_legal", "last_legal")


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


def run_recorded_proxy_gate(package: Path, library: Path, limit: int | None) -> dict:
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


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol_header(game_map: dict, seat: int) -> str:
    """Render the static map exactly as a standalone bot on ``seat`` sees it."""

    if seat not in (0, 1):
        raise ValueError(f"seat {seat} is not 0 or 1")
    rows = list(game_map["rows"])
    if seat == 1:
        rows = [
            "".join("1" if cell == "0" else "0" if cell == "1" else cell for cell in row)
            for row in rows
        ]
    return f"{game_map['w']} {game_map['h']}\n" + "\n".join(rows) + "\n"


def protocol_turn(snapshot: dict, seat: int) -> str:
    """Render one exact environment pre-turn state through the player protocol."""

    if seat not in (0, 1):
        raise ValueError(f"seat {seat} is not 0 or 1")
    inventories = snapshot["inventories"]
    plants = list(snapshot["plants"])
    if "plant_order" in snapshot:
        by_cell = {(int(plant["x"]), int(plant["y"])): plant for plant in plants}
        order = [tuple(int(value) for value in cell) for cell in snapshot["plant_order"]]
        if len(by_cell) != len(plants) or set(order) != set(by_cell):
            raise ValueError("replay plant_order is not a permutation of the plant cells")
        plants = [by_cell[cell] for cell in order]
    lines = [
        " ".join(str(value) for value in inventories[seat]),
        " ".join(str(value) for value in inventories[1 - seat]),
        str(len(plants)),
    ]
    lines.extend(
        " ".join(
            str(value)
            for value in (
                plant["type"],
                plant["x"],
                plant["y"],
                plant["size"],
                plant["health"],
                plant["fruits"],
                plant["cooldown"],
            )
        )
        for plant in plants
    )
    lines.append(str(len(snapshot["units"])))
    for unit in snapshot["units"]:
        lines.append(
            " ".join(
                str(value)
                for value in (
                    unit["id"],
                    int(unit["player"] != seat),
                    unit["x"],
                    unit["y"],
                    unit["ms"],
                    unit["cc"],
                    unit["hp"],
                    unit["chop"],
                    *unit["carry"],
                )
            )
        )
    return "\n".join(lines) + "\n"


class StandaloneChampion:
    """One authoritative standalone process, stateful for exactly one game."""

    def __init__(self, binary: Path, header: str, timeout_seconds: float) -> None:
        self.process = subprocess.Popen(
            [str(binary.resolve())],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.timeout_seconds = timeout_seconds
        self.process.stdin.write(header)
        self.process.stdin.flush()

    def turn(self, block: str) -> tuple[list[str], float]:
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        started = time.perf_counter()
        self.process.stdin.write(block)
        self.process.stdin.flush()
        if not self.selector.select(self.timeout_seconds):
            raise TimeoutError(
                f"authoritative standalone produced no line in {self.timeout_seconds:.3f}s"
            )
        line = self.process.stdout.readline()
        elapsed = time.perf_counter() - started
        if not line:
            stderr = ""
            if self.process.stderr is not None:
                stderr = self.process.stderr.read()
            raise RuntimeError(
                f"authoritative standalone exited {self.process.poll()}: {stderr[-1000:]}"
            )
        return [fragment for fragment in line.rstrip("\r\n").split(";") if fragment], elapsed

    def close(self) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()
        self.selector.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def __enter__(self) -> "StandaloneChampion":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def split_commands(line: list[str]) -> tuple[list[str], list[str]]:
    return line, gameplay_commands(line)


def compare_paired_replay(
    replay: dict,
    standalone: Path,
    timeout_seconds: float,
) -> dict:
    """Compare one environment-linked command stream to the standalone target."""

    if replay.get("opponent_id") != CHAMPION_OPPONENT_ID:
        raise ValueError(f"replay opponent is {replay.get('opponent_id')}, expected champion")
    champion_seat = 1 - int(replay["learned_seat"])
    command_key = f"commands{champion_seat}"
    header = protocol_header(replay["map"], champion_seat)
    protocol_digest = hashlib.sha256(header.encode())
    snapshot = replay["initial_state"]
    raw_turns = 0
    gameplay_turns = 0
    raw_first_divergence = None
    gameplay_first_divergence = None
    latencies: list[float] = []
    with StandaloneChampion(standalone, header, timeout_seconds) as policy:
        for replay_turn in replay["turns"]:
            if int(snapshot["turn"]) != int(replay_turn["turn"]):
                raise AssertionError(
                    f"pre-turn state {snapshot['turn']} does not match replay turn "
                    f"{replay_turn['turn']}"
                )
            block = protocol_turn(snapshot, champion_seat)
            protocol_digest.update(block.encode())
            standalone_raw, elapsed = policy.turn(block)
            latencies.append(elapsed)
            linked_raw = list(replay_turn[command_key])
            protocol_digest.update((";".join(linked_raw) + "\n").encode())
            standalone_pair = split_commands(standalone_raw)
            linked_pair = split_commands(linked_raw)
            if standalone_pair[0] == linked_pair[0]:
                raw_turns += 1
            elif raw_first_divergence is None:
                raw_first_divergence = {
                    "turn": int(replay_turn["turn"]),
                    "standalone": standalone_pair[0],
                    "linked": linked_pair[0],
                }
            if standalone_pair[1] == linked_pair[1]:
                gameplay_turns += 1
            else:
                gameplay_first_divergence = {
                    "turn": int(replay_turn["turn"]),
                    "standalone_without_msg": standalone_pair[1],
                    "linked_without_msg": linked_pair[1],
                }
                break
            snapshot = replay_turn["state"]
    compared = gameplay_turns + int(gameplay_first_divergence is not None)
    return {
        "champion_seat": champion_seat,
        "turns_expected": len(replay["turns"]),
        "turns_compared": compared,
        "raw_turns_passed": raw_turns,
        "gameplay_turns_passed": gameplay_turns,
        "raw_first_divergence": raw_first_divergence,
        "gameplay_first_divergence": gameplay_first_divergence,
        "protocol_digest": protocol_digest.hexdigest(),
        "latencies": latencies,
    }


def varied_legal_actions(env: object, rng: object) -> tuple[object, tuple[str, ...]]:
    """Four deterministic legal action selectors, assigned by environment slot."""

    import numpy as np

    from cgauto.rl_full_env import ACTION_SIZE, PHASE_PLAN, PHASE_TROLL

    actions = np.zeros(env.num_envs, dtype=np.int32)
    modes: list[str] = []
    flat_masks = env.masks.reshape(env.num_envs, ACTION_SIZE)
    for slot in range(env.num_envs):
        mode = POLICY_MODES[slot % len(POLICY_MODES)]
        modes.append(mode)
        if env.phase[slot] == PHASE_PLAN:
            legal = np.flatnonzero(env.plan_masks[slot])
        elif env.phase[slot] == PHASE_TROLL:
            legal = np.flatnonzero(flat_masks[slot])
        else:
            continue
        if legal.size == 0:
            raise AssertionError(f"slot {slot} phase {env.phase[slot]} has no legal action")
        if mode == "random_legal":
            actions[slot] = int(rng.choice(legal))
        elif mode == "first_legal":
            actions[slot] = int(legal[0])
        elif mode == "middle_legal":
            actions[slot] = int(legal[len(legal) // 2])
        else:
            actions[slot] = int(legal[-1])
    return actions, tuple(modes)


def portable_replay_record(replay: dict) -> dict:
    """Timing-free proof record small enough to hash without retaining trajectories."""

    return {
        "episode_seed": replay["episode_seed"],
        "map_index": replay["map_index"],
        "learned_seat": replay["learned_seat"],
        "opponent_id": replay["opponent_id"],
        "initial_state": replay["initial_state"],
        "turns": [
            {
                "turn": turn["turn"],
                "commands0": turn["commands0"],
                "commands1": turn["commands1"],
                "state_hash": turn["state_hash"],
            }
            for turn in replay["turns"]
        ],
        "terminal_kind": replay["terminal_kind"],
        "terminal_reason": replay["terminal_reason"],
        "terminal_stall_counter": replay["terminal_stall_counter"],
        "terminal_state_hash": replay["terminal_state_hash"],
    }


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def run_paired_gate(
    *,
    episodes: int,
    num_envs: int,
    seed_base: int,
    random_seed: int,
    maps: Path,
    library: Path,
    standalone: Path,
    timeout_seconds: float,
) -> dict:
    """Run the load-bearing 200-game command, transition and terminal gate."""

    import numpy as np

    from cgauto.rl_full_env import (
        FullVecEnv,
        verify_terminal_parity,
        verify_transition_parity,
    )

    if episodes <= 0 or num_envs <= 0:
        raise ValueError("episodes and num-envs must be positive")
    rng = np.random.default_rng(random_seed)
    completed: set[int] = set()
    mode_games: Counter[str] = Counter()
    seat_games: Counter[int] = Counter()
    map_indices: set[int] = set()
    raw_games = gameplay_games = 0
    raw_turns = gameplay_turns = total_turns = 0
    transition_parity = terminal_parity = 0
    illegal_commands = 0
    latencies: list[float] = []
    first_raw_divergence = None
    first_gameplay_divergence = None
    portable_digest = hashlib.sha256()
    protocol_digest = hashlib.sha256()
    env_step_seconds = 0.0
    env_turn_steps = 0
    env_decisions = 0
    started = time.perf_counter()
    with FullVecEnv(
        num_envs,
        seed_base,
        maps,
        {"champion_exact": 1.0},
        library=library,
    ) as env:
        while len(completed) < episodes and first_gameplay_divergence is None:
            actions, slot_modes = varied_legal_actions(env, rng)
            env_decisions += int(np.count_nonzero(env.phase != 2))
            step_started = time.perf_counter()
            _, info = env.step(actions)
            env_step_seconds += time.perf_counter() - step_started
            env_turn_steps += int(info.turn_completed.sum())
            for slot in np.flatnonzero(info.dones):
                seed = int(info.episode_seeds[slot])
                replay = env.take_replay(int(slot))
                if not seed_base <= seed < seed_base + episodes:
                    continue
                if seed in completed:
                    raise AssertionError(f"duplicate completed episode seed {seed}")
                if replay is None:
                    raise AssertionError(f"seed {seed} completed without a replay")
                verify_transition_parity(replay)
                transition_parity += 1
                verify_terminal_parity(replay)
                terminal_parity += 1
                paired = compare_paired_replay(replay, standalone, timeout_seconds)
                completed.add(seed)
                mode_games[slot_modes[int(slot)]] += 1
                seat_games[paired["champion_seat"]] += 1
                map_indices.add(int(replay["map_index"]))
                turns = len(replay["turns"])
                total_turns += turns
                raw_turns += int(paired["raw_turns_passed"])
                gameplay_turns += int(paired["gameplay_turns_passed"])
                latencies.extend(paired.pop("latencies"))
                portable_digest.update(
                    json.dumps(
                        portable_replay_record(replay),
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                )
                protocol_digest.update(bytes.fromhex(paired["protocol_digest"]))
                illegal_commands += int(info.illegal_commands[slot])
                if paired["raw_first_divergence"] is None:
                    raw_games += 1
                elif first_raw_divergence is None:
                    first_raw_divergence = {
                        "episode_seed": seed,
                        "map_index": int(replay["map_index"]),
                        "champion_seat": paired["champion_seat"],
                        **paired["raw_first_divergence"],
                    }
                if paired["gameplay_first_divergence"] is None:
                    gameplay_games += 1
                else:
                    first_gameplay_divergence = {
                        "episode_seed": seed,
                        "map_index": int(replay["map_index"]),
                        "champion_seat": paired["champion_seat"],
                        **paired["gameplay_first_divergence"],
                    }
                    break
    elapsed = time.perf_counter() - started
    return {
        "schema_version": 2,
        "gate": "paired_exact_input_champion",
        "episodes_requested": episodes,
        "episodes_completed": len(completed),
        "episode_seed_base": seed_base,
        "random_seed": random_seed,
        "num_envs": num_envs,
        "maps": str(maps),
        "unique_map_indices": len(map_indices),
        "opponent_action_modes": dict(sorted(mode_games.items())),
        "champion_seats": {str(seat): count for seat, count in sorted(seat_games.items())},
        "authoritative_source": str(AUTHORITATIVE_SOURCE),
        "authoritative_sha256": sha256_path(AUTHORITATIVE_SOURCE),
        "standalone_binary": str(standalone),
        "standalone_sha256": sha256_path(standalone),
        "library": str(library),
        "library_sha256": sha256_path(library),
        "raw_command_games_passed": raw_games,
        "raw_command_turns_passed": raw_turns,
        "gameplay_command_games_passed": gameplay_games,
        "gameplay_command_turns_passed": gameplay_turns,
        "total_turns": total_turns,
        "raw_first_divergence": first_raw_divergence,
        "gameplay_first_divergence": first_gameplay_divergence,
        "transition_parity": transition_parity,
        "terminal_parity": terminal_parity,
        "illegal_commands": illegal_commands,
        "portable_digest": portable_digest.hexdigest(),
        "protocol_digest": protocol_digest.hexdigest(),
        "environment": {
            "decisions": env_decisions,
            "turn_steps": env_turn_steps,
            "step_seconds": env_step_seconds,
            "turn_steps_per_second": env_turn_steps / env_step_seconds,
        },
        "standalone_protocol_latency_ms": {
            "samples": len(latencies),
            "median": statistics.median(latencies) * 1000 if latencies else 0.0,
            "p95": percentile(latencies, 0.95) * 1000,
            "maximum": max(latencies) * 1000 if latencies else 0.0,
        },
        "elapsed_seconds": elapsed,
    }


def compile_authoritative(source: Path, output: Path) -> None:
    digest = sha256_path(source)
    if digest != AUTHORITATIVE_SHA256:
        raise SystemExit(
            f"authoritative source hash drift: expected {AUTHORITATIVE_SHA256}, got {digest}"
        )
    rustc = shutil.which("rustc")
    if rustc is None:
        fallback = Path.home() / ".cargo" / "bin" / "rustc"
        if not fallback.is_file():
            raise FileNotFoundError("rustc is neither on PATH nor in ~/.cargo/bin")
        rustc = str(fallback)
    subprocess.run([rustc, "--edition=2021", "-O", str(source), "-o", str(output)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("paired", "recorded-proxy"), default="paired")
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--num-envs", type=int, default=20)
    parser.add_argument("--seed-base", type=int, default=410_000)
    parser.add_argument("--random-seed", type=int, default=20260830)
    parser.add_argument("--maps", type=Path, default=DEFAULT_MAPS)
    parser.add_argument("--source", type=Path, default=AUTHORITATIVE_SOURCE)
    parser.add_argument("--standalone", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "recorded-proxy":
        report = run_recorded_proxy_gate(args.package, args.library, args.limit)
    elif args.standalone is not None:
        report = run_paired_gate(
            episodes=args.episodes,
            num_envs=args.num_envs,
            seed_base=args.seed_base,
            random_seed=args.random_seed,
            maps=args.maps,
            library=args.library,
            standalone=args.standalone,
            timeout_seconds=args.timeout_seconds,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="champion-exact-") as directory:
            standalone = Path(directory) / "champion"
            compile_authoritative(args.source, standalone)
            report = run_paired_gate(
                episodes=args.episodes,
                num_envs=args.num_envs,
                seed_base=args.seed_base,
                random_seed=args.random_seed,
                maps=args.maps,
                library=args.library,
                standalone=standalone,
                timeout_seconds=args.timeout_seconds,
            )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")
    if args.mode == "recorded-proxy":
        return 0 if report["gameplay_first_divergence"] is None else 1
    passed = (
        report["episodes_completed"] == args.episodes
        and report["raw_command_games_passed"] == args.episodes
        and report["gameplay_command_games_passed"] == args.episodes
        and report["transition_parity"] == args.episodes
        and report["terminal_parity"] == args.episodes
        and report["illegal_commands"] == 0
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
