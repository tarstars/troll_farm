#!/usr/bin/env python3
"""Bed the generated one-file neural clone against its signed Python reference."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import bench  # noqa: E402
import nn_runtime as nr  # noqa: E402


MAPS = ROOT / "local_claude_1" / "third-troll" / "smoke-maps-seed0.jsonl"
REFERENCE = HERE / "results" / "clone-2026-08-30-a" / "bench-argmax-replays.jsonl"
QUANTIZED = ROOT / "codex_1" / "results" / "nn-bot-way-b-export" / "bench-quantized-python-replays.jsonl"
CANDIDATE = ROOT / "cgauto" / "submissions" / "candidate-nn-clone.rs"
CHAMPION = ROOT / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
REPORT = ROOT / "codex_1" / "results" / "nn-bot-way-b-export" / "bed-full-bot.json"
FULL_SEAT_CORPUS = Path("/home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz")
PILOT_SEAT_CORPUS = HERE / "results" / "pilot" / "states-pilot.jsonl.gz"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)]


def source_size_counts(source: str) -> dict[str, int]:
    return {
        "unicode_code_points": len(source),
        "utf16_code_units": len(source.encode("utf-16-le")) // 2,
        "utf8_bytes": len(source.encode()),
    }


def summarize_timing(first_ms: list[float], warm_ms: list[float]) -> dict[str, float]:
    return {
        "first_turn_max_ms": round(max(first_ms), 3),
        "first_turn_median_ms": round(percentile(first_ms, 0.5), 3),
        "warm_turn_max_ms": round(max(warm_ms), 3),
        "warm_turn_p99_ms": round(percentile(warm_ms, 0.99), 3),
        "warm_turn_median_ms": round(percentile(warm_ms, 0.5), 3),
    }


def certify_timing(runs: list[dict[str, float]], context: str) -> dict[str, Any]:
    if len(runs) != 3:
        raise ValueError(f"the frozen timing rule requires exactly three runs, got {len(runs)}")
    p99_values = [float(run["warm_turn_p99_ms"]) for run in runs]
    first_values = [float(run["first_turn_max_ms"]) for run in runs]
    median_p99 = percentile(p99_values, 0.5)
    numerical_pass = median_p99 <= 15.0 and max(p99_values) <= 20.0
    is_host_record = context == "host-of-record-quiet"
    return {
        "context": context,
        "required_context": "host-of-record-quiet, with no training run active",
        "runs": runs,
        "warm_turn_p99_values_ms": p99_values,
        "first_turn_max_values_ms": first_values,
        "median_warm_turn_p99_ms": median_p99,
        "every_warm_turn_p99_at_most_20_ms": max(p99_values) <= 20.0,
        "median_warm_turn_p99_at_most_15_ms": median_p99 <= 15.0,
        "numerical_pass": numerical_pass,
        "certified": numerical_pass if is_host_record else None,
    }


def compile_rust(
    source: Path,
    binary: Path,
    rustc: str,
    *,
    cfg: str | tuple[str, ...] | None = None,
) -> None:
    command = [rustc, "--edition=2021", "-O", "-Awarnings"]
    cfgs = (cfg,) if isinstance(cfg, str) else (() if cfg is None else cfg)
    for value in cfgs:
        command.extend(["--cfg", value])
    command.extend([str(source), "-o", str(binary)])
    subprocess.run(
        command,
        check=True,
    )


def read_runtime_path(binary: Path) -> str:
    completed = subprocess.run([str(binary)], text=True, capture_output=True, check=True)
    path = completed.stdout.strip()
    if path not in {"avx2", "baseline_fallback"}:
        raise RuntimeError(f"unexpected generated runtime path {path!r}")
    return path


def check_turn1_seat_corpus(path: Path) -> dict[str, Any]:
    """Check the signed id rule on every seat-0 turn-one state in a compact shard."""

    games: set[int] = set()
    exceptions: list[dict[str, Any]] = []
    with gzip.open(path, "rt") as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            if int(row.get("turn", -1)) != 1 or int(row.get("seat", -1)) != 0:
                continue
            game = int(row["game"])
            if game in games:
                continue
            games.add(game)
            units = row["state"]["units"]
            ids = sorted(int(unit["id"]) for unit in units)
            owners = {
                player: sorted(int(unit["id"]) for unit in units if int(unit["player"]) == player)
                for player in (0, 1)
            }
            if ids != [0, 1] or owners != {0: [0], 1: [1]}:
                exceptions.append(
                    {"game": game, "line": line_number, "ids": ids, "owners": owners}
                )
    return {
        "path": str(path),
        "sha256": sha256(path),
        "seat0_turn1_games": len(games),
        "exceptions": exceptions,
        "valid": bool(games) and not exceptions,
    }


def _view_cell(ref: Any, seat: int, cell: tuple[int, int]) -> tuple[int, int]:
    if seat == 0:
        return cell
    return len(ref.rows[0]) - 1 - cell[0], len(ref.rows) - 1 - cell[1]


def _free_near_shack(ref: Any, seat: int) -> tuple[int, int]:
    shack = tuple(ref.shacks[seat])
    occupied = {tuple(unit["cell"]) for unit in ref.units.values()}
    choices = [
        cell
        for cell in sorted(ref.walk)
        if cell not in occupied and abs(cell[0] - shack[0]) + abs(cell[1] - shack[1]) <= 1
    ]
    if not choices:
        raise RuntimeError(f"no unoccupied shack-adjacent cell for seat {seat}")
    return choices[0]


def _probe(binary: Path, text: str) -> dict[str, str]:
    completed = subprocess.run(
        [str(binary)], input=text, text=True, capture_output=True, check=True
    )
    result: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        key, value = line.split(" ", 1)
        result[key] = value
    return result


def run_direct_seat_parity(
    item: dict[str, Any], probe_binary: Path, builder: nr.PlaneBuilder
) -> dict[str, Any]:
    """Compare the exact standalone parser/builder/codec against the signed shared library."""

    cases: list[dict[str, Any]] = []
    for seat in (0, 1):
        initial = bench.make_referee(item["rec"], item["draw"])
        later = copy.deepcopy(initial)
        later.units[2] = {
            "player": 0,
            "cell": _free_near_shack(later, 0),
            "speed": 2,
            "cap": 2,
            "harvest": 1,
            "chop": 1,
            "carry": [1, 0, 0, 0, 0, 0],
        }
        later.units[3] = {
            "player": 1,
            "cell": _free_near_shack(later, 1),
            "speed": 2,
            "cap": 2,
            "harvest": 1,
            "chop": 1,
            "carry": [1, 0, 0, 0, 0, 0],
        }
        first_troll, active_troll = (0, 2) if seat == 0 else (1, 3)
        later.units[first_troll]["carry"] = [1, 0, 0, 0, 0, 0]
        first_view = _view_cell(later, seat, tuple(later.units[first_troll]["cell"]))
        active_view = _view_cell(later, seat, tuple(later.units[active_troll]["cell"]))
        staged_action = nr.flat(3, *first_view)
        decoded_action = nr.flat(3, *active_view)
        staged = [(first_troll, staged_action)]
        plan_index = 1
        state = nr.state_json_from_referee(later, 2, staged=staged)
        expected_obs, expected_action, _ = builder.observe(
            state,
            seat,
            active_troll,
            nr.PHASE_TROLL,
            plan_index,
            want_mask=True,
            want_plan_mask=False,
        )
        _, _, expected_plan = builder.observe(
            nr.state_json_from_referee(later, 2),
            seat,
            -1,
            nr.PHASE_PLAN,
            0,
            want_mask=False,
            want_plan_mask=True,
        )
        if expected_action[decoded_action] != 1:
            raise AssertionError("the non-MOVE direct-parity decode action is not legal")
        expected_command = builder.decode_action(
            decoded_action, active_troll, seat, len(later.rows[0]), len(later.rows)
        )
        rendering = nr.SeatRendering(seat)
        protocol = (
            rendering.map_header(initial)
            + rendering.turn_text(initial)
            + rendering.turn_text(later)
            + f"1 {plan_index} {active_troll} 0 {active_troll} {decoded_action}\n"
            + f"{len(staged)}\n"
            + "".join(f"{troll} {action}\n" for troll, action in staged)
        )
        actual = _probe(probe_binary, protocol)
        comparisons = {
            "seat": actual.get("SEAT") == str(seat),
            "observation": actual.get("OBS") == expected_obs.hex(),
            "spatial_mask": actual.get("ACTION") == expected_action.hex(),
            "plan_mask": actual.get("PLAN") == expected_plan.hex(),
            "decoded_command": actual.get("COMMAND") == expected_command,
        }
        if not all(comparisons.values()):
            raise AssertionError(f"direct standalone parity failed for seat {seat}: {comparisons}")
        cases.append(
            {
                "seat": seat,
                "active_troll": active_troll,
                "staged_non_move_action": staged_action,
                "decoded_non_move_action": decoded_action,
                "decoded_command": expected_command,
                "observation_sha256": hashlib.sha256(expected_obs).hexdigest(),
                "spatial_mask_sha256": hashlib.sha256(expected_action).hexdigest(),
                "plan_mask_sha256": hashlib.sha256(expected_plan).hexdigest(),
                "comparisons": comparisons,
            }
        )

    invalid = bench.make_referee(item["rec"], item["draw"])
    invalid.units[2] = invalid.units.pop(1)
    rendering = nr.SeatRendering(0)
    malformed = (
        rendering.map_header(invalid)
        + rendering.turn_text(invalid)
        + rendering.turn_text(invalid)
    )
    rejected = _probe(probe_binary, malformed) == {}
    if not rejected:
        raise AssertionError("standalone accepted a turn-one id set other than {0,1}")
    return {"cases": cases, "turn1_invalid_id_set_rejected": rejected, "valid": True}


def compare_python_replays(
    reference: list[dict[str, Any]], quantized: list[dict[str, Any]]
) -> tuple[int, int, list[dict[str, Any]]]:
    semantic = (
        "map_hash",
        "policy_seat",
        "turns",
        "ended_reason",
        "bot_score",
        "policy_score",
    )
    identical = commands = 0
    differences: list[dict[str, Any]] = []
    if len(reference) != len(quantized):
        differences.append(
            {"scope": "file", "reference_games": len(reference), "quantized_games": len(quantized)}
        )
    for game, (left, right) in enumerate(zip(reference, quantized), 1):
        metadata = {key: [left[key], right[key]] for key in semantic if left[key] != right[key]}
        first = None
        if len(left["replay"]) != len(right["replay"]):
            first = {"turn": "length", "reference": len(left["replay"]), "quantized": len(right["replay"])}
        for expected, actual in zip(left["replay"], right["replay"]):
            commands += 1
            if expected != actual and first is None:
                first = {
                    "turn": expected["turn"],
                    "reference": expected,
                    "quantized": actual,
                }
        if metadata or first:
            differences.append({"game": game, "metadata": metadata, "first": first})
        else:
            identical += 1
    return identical, commands, differences


def run_compiled_bed(
    maps: list[dict[str, Any]],
    reference: list[dict[str, Any]],
    candidate_binary: Path,
    champion_binary: Path,
) -> tuple[int, int, list[float], list[float], list[dict[str, Any]]]:
    identical = commands = 0
    first_ms: list[float] = []
    warm_ms: list[float] = []
    differences: list[dict[str, Any]] = []
    for game, expected_game in enumerate(reference, 1):
        item = maps[(game - 1) // 2]
        if expected_game["map_hash"] != item["rec"]["map_hash"]:
            raise ValueError(f"reference/map order drift at game {game}")
        neural_seat = expected_game["policy_seat"]
        champion_seat = 1 - neural_seat
        ref = bench.make_referee(item["rec"], item["draw"])
        neural_rendering = nr.SeatRendering(neural_seat)
        champion_rendering = nr.SeatRendering(champion_seat)
        startup = time.perf_counter()
        neural = bench.BotProcess(candidate_binary, neural_rendering.map_header(ref))
        champion = bench.BotProcess(champion_binary, champion_rendering.map_header(ref))
        first_difference = None
        try:
            for turn_index, expected in enumerate(expected_game["replay"]):
                neural_text = neural_rendering.turn_text(ref)
                champion_text = champion_rendering.turn_text(ref)
                started = time.perf_counter()
                neural_line = neural.turn(neural_text)
                stopped = time.perf_counter()
                champion_line = champion.turn(champion_text)
                latency = (stopped - (startup if turn_index == 0 else started)) * 1000.0
                (first_ms if turn_index == 0 else warm_ms).append(latency)
                commands += 1
                if first_difference is None and neural_line != expected["policy"]:
                    first_difference = {
                        "turn": expected["turn"],
                        "side": "neural",
                        "reference": expected["policy"],
                        "compiled": neural_line,
                    }
                if first_difference is None and champion_line != expected["bot"]:
                    first_difference = {
                        "turn": expected["turn"],
                        "side": "champion",
                        "reference": expected["bot"],
                        "compiled": champion_line,
                    }
                if first_difference is not None:
                    break
                if neural_seat == 0:
                    ref.apply_two(neural_line, champion_line)
                else:
                    ref.apply_two(champion_line, neural_line)
                ref.grow()
        finally:
            neural.close()
            champion.close()
        if first_difference is None:
            identical += 1
        else:
            differences.append({"game": game, "map_hash": expected_game["map_hash"], **first_difference})
    return identical, commands, first_ms, warm_ms, differences


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maps", type=Path, default=MAPS)
    parser.add_argument("--reference-replays", type=Path, default=REFERENCE)
    parser.add_argument("--quantized-replays", type=Path, default=QUANTIZED)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--champion", type=Path, default=CHAMPION)
    parser.add_argument("--out", type=Path, default=REPORT)
    parser.add_argument("--rustc", default=None)
    parser.add_argument(
        "--timing-context",
        choices=("information", "host-of-record-quiet"),
        default="information",
        help="only host-of-record-quiet turns the frozen three-run timing rule into a gate",
    )
    parser.add_argument(
        "--seat-corpus",
        type=Path,
        default=None,
        help="compact state shard for the turn-one id-rule check",
    )
    args = parser.parse_args()

    rustc = args.rustc or shutil.which("rustc")
    if rustc is None:
        fallback = Path.home() / ".rustup" / "toolchains" / "stable-x86_64-unknown-linux-gnu" / "bin" / "rustc"
        rustc = str(fallback) if fallback.is_file() else None
    if rustc is None:
        raise SystemExit("rustc not found")

    maps = read_jsonl(args.maps)
    reference = read_jsonl(args.reference_replays)
    quantized = read_jsonl(args.quantized_replays)
    if len(maps) != 24 or len(reference) != 48:
        raise SystemExit(f"the signed bed is 24 maps/48 games, got {len(maps)}/{len(reference)}")
    python_identical, python_commands, python_differences = compare_python_replays(
        reference, quantized
    )
    corpus_path = args.seat_corpus
    if corpus_path is None:
        corpus_path = FULL_SEAT_CORPUS if FULL_SEAT_CORPUS.is_file() else PILOT_SEAT_CORPUS
    seat_corpus = check_turn1_seat_corpus(corpus_path)

    source = args.candidate.read_text()
    candidate_size = source_size_counts(source)
    with tempfile.TemporaryDirectory(prefix="full-bot-bed-") as directory:
        work = Path(directory)
        candidate_binary = work / "candidate"
        fallback_binary = work / "candidate-fallback"
        champion_binary = work / "champion"
        probe_binary = work / "candidate-parity-probe"
        path_probe_binary = work / "candidate-path-probe"
        fallback_path_probe_binary = work / "candidate-fallback-path-probe"
        compile_rust(args.candidate, candidate_binary, rustc)
        compile_rust(args.candidate, fallback_binary, rustc, cfg="tf_nn_force_fallback")
        compile_rust(args.champion, champion_binary, rustc)
        compile_rust(args.candidate, probe_binary, rustc, cfg="tf_full_parity_probe")
        compile_rust(args.candidate, path_probe_binary, rustc, cfg="tf_nn_path_probe")
        compile_rust(
            args.candidate,
            fallback_path_probe_binary,
            rustc,
            cfg=("tf_nn_path_probe", "tf_nn_force_fallback"),
        )
        runtime_path = read_runtime_path(path_probe_binary)
        forced_runtime_path = read_runtime_path(fallback_path_probe_binary)
        if forced_runtime_path != "baseline_fallback":
            raise RuntimeError(f"forced fallback selected {forced_runtime_path!r}")
        direct_parity = run_direct_seat_parity(
            maps[0], probe_binary, nr.PlaneBuilder(nr.DEFAULT_LIBRARY)
        )
        normal_runs = [run_compiled_bed(maps, reference, candidate_binary, champion_binary)]
        fallback_run = run_compiled_bed(maps, reference, fallback_binary, champion_binary)
        for _ in range(2):
            normal_runs.append(
                run_compiled_bed(maps, reference, candidate_binary, champion_binary)
            )

    compiled_identical, compiled_commands, first_ms, warm_ms, compiled_differences = normal_runs[0]
    (
        fallback_identical,
        fallback_commands,
        fallback_first_ms,
        fallback_warm_ms,
        fallback_differences,
    ) = fallback_run
    timing_runs = [summarize_timing(run[2], run[3]) for run in normal_runs]
    timing = timing_runs[0]
    fallback_timing = summarize_timing(fallback_first_ms, fallback_warm_ms)
    timing_certification = certify_timing(timing_runs, args.timing_context)
    gates = {
        "python_clone_games_identical": python_identical == 48,
        "runtime_dispatch_games_identical": compiled_identical == 48,
        "forced_fallback_games_identical": fallback_identical == 48,
        "three_timing_runs_command_identical": all(run[0] == 48 for run in normal_runs),
        "runtime_dispatch_first_turn_at_most_500_ms": timing["first_turn_max_ms"] <= 500.0,
        "forced_fallback_first_turn_at_most_500_ms": fallback_timing["first_turn_max_ms"]
        <= 500.0,
        "forced_fallback_warm_p99_at_most_50_ms": fallback_timing["warm_turn_p99_ms"]
        <= 50.0,
        "source_under_100000_utf16_code_units": candidate_size["utf16_code_units"]
        < 100_000,
        "direct_seat_parity": bool(direct_parity["valid"]),
        "turn1_id_corpus_valid": bool(seat_corpus["valid"]),
    }
    if args.timing_context == "host-of-record-quiet":
        gates["three_run_timing_certified"] = bool(timing_certification["certified"])
    report = {
        "what": "full-game generated neural clone bed against the committed Python-clone/champion stream",
        "maps": str(args.maps),
        "reference_replays": str(args.reference_replays),
        "reference_replays_sha256": sha256(args.reference_replays),
        "quantized_replays": str(args.quantized_replays),
        "quantized_replays_sha256": sha256(args.quantized_replays),
        "candidate": str(args.candidate),
        "candidate_sha256": sha256(args.candidate),
        "candidate_characters": candidate_size["unicode_code_points"],
        "candidate_size": candidate_size,
        "champion": str(args.champion),
        "champion_sha256": sha256(args.champion),
        "games": 48,
        "python_clone_games_identical": python_identical,
        "python_turns_compared": python_commands,
        "compiled_games_identical": compiled_identical,
        "compiled_turns_compared": compiled_commands,
        "runtime_paths": {
            "runtime_dispatch": {
                "selected_path": runtime_path,
                "forced": False,
                "games_identical": compiled_identical,
                "turns_compared": compiled_commands,
                "timing": timing,
                "differences": compiled_differences,
            },
            "forced_fallback": {
                "selected_path": forced_runtime_path,
                "forced": True,
                "forcing_mechanism": "rustc --cfg tf_nn_force_fallback",
                "games_identical": fallback_identical,
                "turns_compared": fallback_commands,
                "timing": fallback_timing,
                "differences": fallback_differences,
            },
        },
        "direct_seat_parity": direct_parity,
        "turn1_id_corpus": seat_corpus,
        "turn1_id_corpus_authoritative_card_result": {
            "source": "coordination/messages/local_claude_1/20260830T125730Z-20260829-nn-bot-way-b-export-handoff.md",
            "seat0_turn1_games": 370,
            "exceptions": 0,
        },
        "timing": timing,
        "timing_certification": timing_certification,
        "gates": gates,
        "python_differences": python_differences,
        "compiled_differences": compiled_differences,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f"parity runtime {runtime_path} {compiled_identical}/48; forced fallback "
        f"{fallback_identical}/48; Python export {python_identical}/48; commands "
        f"{compiled_commands}/{fallback_commands}/{python_commands}"
    )
    print(
        "timing p99 runs "
        + ", ".join(f"{run['warm_turn_p99_ms']:.3f}" for run in timing_runs)
        + f" ms; median {timing_certification['median_warm_turn_p99_ms']:.3f} ms; "
        f"context {args.timing_context}"
    )
    print(
        f"fallback first max {fallback_timing['first_turn_max_ms']:.3f} ms; warm median "
        f"{fallback_timing['warm_turn_median_ms']:.3f} ms, p99 "
        f"{fallback_timing['warm_turn_p99_ms']:.3f} ms"
    )
    print(
        f"size {candidate_size['unicode_code_points']} code points; "
        f"{candidate_size['utf16_code_units']} UTF-16 code units; "
        f"{candidate_size['utf8_bytes']} UTF-8 bytes; report -> {args.out}"
    )
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
