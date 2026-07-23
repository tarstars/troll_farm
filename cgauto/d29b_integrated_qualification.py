#!/usr/bin/env python3
"""Qualify integrated D29b predictions and selected branches on frozen rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mmap
from pathlib import Path
import statistics
import struct


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
OPPONENTS = (
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
)
PARTITIONS = ((53000, 600), (53600, 120), (53720, 120))
LABELS = (
    ANALYSIS / "d29-option-labels-development-53000-53599.tsv",
    ANALYSIS / "d29-option-labels-confirmation-53600-53719.tsv",
    ANALYSIS / "d29b-option-labels-confirmation-53720-53839.tsv",
)
CORPUS = ANALYSIS / "d29b-rust-parity-corpus-2026-07-20.bin"
INTEGRATED = ANALYSIS / "d29b-integrated-parity-53000-53839.tsv"
CANDIDATE = (
    ROOT
    / "cgauto/submissions/candidate-agent6553250-d29b-spatial-option-critic.min.rs"
)
EXPECTED_CORPUS_SHA256 = (
    "bcf126bfabd9d4c4ceaac7c57c6197a1f0c69ebd40b9ff5b07d8d7d323af48db"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["seed"]), int(row["seat"]), row["opponent"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def expected_predictions(path: Path) -> dict[tuple[int, int, str], tuple[float, bool]]:
    if sha256(path) != EXPECTED_CORPUS_SHA256:
        raise ValueError("D29b parity corpus differs from frozen input")
    keys = [
        (seed, seat, opponent)
        for seed_start, seed_count in PARTITIONS
        for seed in range(seed_start, seed_start + seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
    ]
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        magic, rows, grid, scalars, threshold = struct.unpack_from("<8sIIIf", data)
        if magic != b"D29BPRT1" or rows != len(keys) or threshold != 4.0:
            raise ValueError("D29b parity corpus header differs")
        row_bytes = 2 * grid + 4 * scalars + 5
        if len(data) != 24 + rows * row_bytes:
            raise ValueError("D29b parity corpus length differs")
        result = {}
        expected_offset = 2 * grid + 4 * scalars
        for index, item in enumerate(keys):
            offset = 24 + index * row_bytes + expected_offset
            raw, decision = struct.unpack_from("<fB", data, offset)
            result[item] = raw, bool(decision)
    return result


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * fraction))]


def qualify(integrated_path: Path, candidate_path: Path) -> dict:
    predictions = expected_predictions(CORPUS)
    integrated_rows = read_tsv(integrated_path)
    integrated = {key(row): row for row in integrated_rows}
    duplicate_integrated = len(integrated_rows) - len(integrated)
    label_rows = [row for path in LABELS for row in read_tsv(path)]
    labels = {(key(row), row["option"]): row for row in label_rows}

    expected_keys = set(predictions)
    missing_integrated = expected_keys - set(integrated)
    unexpected_integrated = set(integrated) - expected_keys
    raw_errors = []
    decision_mismatches = []
    branch_mismatches: list[dict] = []
    reached_failures = []
    selection_ns = []
    switches = 0
    deltas = []
    for item in sorted(expected_keys & set(integrated)):
        row = integrated[item]
        expected_raw, expected_switch = predictions[item]
        actual_raw = float(row["raw_prediction"])
        actual_switch = bool(int(row["switched"]))
        raw_errors.append(abs(actual_raw - expected_raw))
        if actual_switch != expected_switch:
            decision_mismatches.append(item)
        if int(row["reached_cut"]) != 1:
            reached_failures.append(item)
        selection_ns.append(int(row["selection_ns"]))
        switches += int(actual_switch)
        option = "ownership2" if expected_switch else "resident"
        selected = labels[(item, option)]
        resident = labels[(item, "resident")]
        deltas.append(int(selected["margin"]) - int(resident["margin"]))
        comparisons = {
            "final_turn": (int(row["final_turn"]), int(selected["final_turn"])),
            "margin": (int(row["margin"]), int(selected["margin"])),
            "my_score": (int(row["my_score"]), int(selected["my_score"])),
            "opponent_score": (
                int(row["opponent_score"]),
                int(selected["opponent_score"]),
            ),
            "command_hash": (
                int(row["command_hash"]),
                int(selected["command_hash"]),
            ),
        }
        for field, values in comparisons.items():
            if values[0] != values[1]:
                branch_mismatches.append(
                    {"key": item, "option": option, "field": field, "values": values}
                )
        if row["mismatch"]:
            branch_mismatches.append(
                {"key": item, "field": "runtime_commands", "value": row["mismatch"]}
            )

    candidate_bytes = candidate_path.stat().st_size
    latency_median = percentile(selection_ns, 0.50)
    latency_p95 = percentile(selection_ns, 0.95)
    latency_maximum = max(selection_ns)
    complete = not any(
        (
            duplicate_integrated,
            missing_integrated,
            unexpected_integrated,
            decision_mismatches,
            branch_mismatches,
            reached_failures,
        )
    ) and (
        candidate_bytes < 100_000
        and max(raw_errors, default=float("inf")) <= 0.001
        and latency_p95 <= 20_000_000
        and latency_maximum <= 45_000_000
    )
    return {
        "schema": 1,
        "complete": complete,
        "rows_expected": len(expected_keys),
        "rows_integrated": len(integrated_rows),
        "duplicate_integrated": duplicate_integrated,
        "missing_integrated": len(missing_integrated),
        "unexpected_integrated": len(unexpected_integrated),
        "reached_failures": len(reached_failures),
        "maximum_raw_prediction_error": max(raw_errors, default=None),
        "decision_mismatches": len(decision_mismatches),
        "switches": switches,
        "switch_rate": switches / len(expected_keys),
        "branch_mismatches": len(branch_mismatches),
        "branch_mismatch_examples": branch_mismatches[:20],
        "selected_cell_mean_margin_delta": statistics.mean(deltas),
        "selection_latency_ns": {
            "median": latency_median,
            "p95": latency_p95,
            "maximum": latency_maximum,
        },
        "candidate": str(candidate_path),
        "candidate_bytes": candidate_bytes,
        "candidate_sha256": sha256(candidate_path),
        "corpus_sha256": sha256(CORPUS),
        "integrated_sha256": sha256(integrated_path),
        "label_sha256": {str(path): sha256(path) for path in LABELS},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integrated", type=Path, default=INTEGRATED)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = qualify(args.integrated, args.candidate)
    text = json.dumps(result, indent=1) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
