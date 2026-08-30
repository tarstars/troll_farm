#!/usr/bin/env python3
"""Bed the generated one-file neural clone against its signed Python reference."""

from __future__ import annotations

import argparse
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)]


def compile_rust(source: Path, binary: Path, rustc: str) -> None:
    subprocess.run(
        [rustc, "--edition=2021", "-O", "-Awarnings", str(source), "-o", str(binary)],
        check=True,
    )


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

    source = args.candidate.read_text()
    with tempfile.TemporaryDirectory(prefix="full-bot-bed-") as directory:
        work = Path(directory)
        candidate_binary, champion_binary = work / "candidate", work / "champion"
        compile_rust(args.candidate, candidate_binary, rustc)
        compile_rust(args.champion, champion_binary, rustc)
        compiled_identical, compiled_commands, first_ms, warm_ms, compiled_differences = (
            run_compiled_bed(maps, reference, candidate_binary, champion_binary)
        )

    timing = {
        "first_turn_max_ms": round(max(first_ms), 3),
        "first_turn_median_ms": round(percentile(first_ms, 0.5), 3),
        "warm_turn_max_ms": round(max(warm_ms), 3),
        "warm_turn_p99_ms": round(percentile(warm_ms, 0.99), 3),
        "warm_turn_median_ms": round(percentile(warm_ms, 0.5), 3),
    }
    gates = {
        "python_clone_games_identical": python_identical == 48,
        "compiled_games_identical": compiled_identical == 48,
        "first_turn_at_most_500_ms": timing["first_turn_max_ms"] <= 500.0,
        "warm_turn_p99_at_most_15_ms": timing["warm_turn_p99_ms"] <= 15.0,
        "source_under_100000_characters": len(source) < 100_000,
    }
    report = {
        "what": "full-game generated neural clone bed against the committed Python-clone/champion stream",
        "maps": str(args.maps),
        "reference_replays": str(args.reference_replays),
        "reference_replays_sha256": sha256(args.reference_replays),
        "quantized_replays": str(args.quantized_replays),
        "quantized_replays_sha256": sha256(args.quantized_replays),
        "candidate": str(args.candidate),
        "candidate_sha256": sha256(args.candidate),
        "candidate_characters": len(source),
        "champion": str(args.champion),
        "champion_sha256": sha256(args.champion),
        "games": 48,
        "python_clone_games_identical": python_identical,
        "python_turns_compared": python_commands,
        "compiled_games_identical": compiled_identical,
        "compiled_turns_compared": compiled_commands,
        "timing": timing,
        "gates": gates,
        "python_differences": python_differences,
        "compiled_differences": compiled_differences,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f"parity {compiled_identical}/48 compiled games; Python export {python_identical}/48; "
        f"commands {compiled_commands}/{python_commands}"
    )
    print(
        f"timing first max {timing['first_turn_max_ms']:.3f} ms; warm median "
        f"{timing['warm_turn_median_ms']:.3f} ms, p99 {timing['warm_turn_p99_ms']:.3f} ms, "
        f"max {timing['warm_turn_max_ms']:.3f} ms"
    )
    print(f"size {len(source)} characters; report -> {args.out}")
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
