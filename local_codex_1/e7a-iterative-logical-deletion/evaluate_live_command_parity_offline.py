#!/usr/bin/env python3
"""Compare a candidate with frozen E7a live outputs without network credentials."""

from __future__ import annotations

import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
BASELINE = REPO / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
AUDIT_SHA256 = "8c29f433982fa9df05e16203bccdc15f290bae36ff5801084e862a882547af5a"
PACKET_SCHEMA = "troll-farm-e7a-live-command-parity-offline-packet-v1"
AGENT_ID = 6_590_141
SUBMISSION_ID = 41_081_503
REQUIRED_GAME = 897_832_286
VALID_ARITIES = {
    "WAIT": 1,
    "MOVE": 4,
    "CHOP": 2,
    "HARVEST": 2,
    "DROP": 2,
    "PLANT": 3,
    "PICK": 3,
    "MINE": 2,
    "TRAIN": 5,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def parse_commands(line: str) -> list[str]:
    commands = [
        command.strip()
        for command in re.split(r"[;\n]+", line)
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]
    for command in commands:
        fields = command.split()
        verb = fields[0].upper() if fields else ""
        if verb not in VALID_ARITIES or len(fields) != VALID_ARITIES[verb]:
            raise ValueError(f"malformed candidate command: {command!r}")
        for value in fields[1:]:
            if verb not in ("PLANT", "PICK") or value != fields[-1]:
                int(value)
    return commands


def longest_period2(lines: list[str]) -> int:
    moves: dict[int, list[tuple[int, tuple[int, int]]]] = defaultdict(list)
    for turn, line in enumerate(lines, 1):
        for command in parse_commands(line):
            fields = command.split()
            if fields[0].upper() == "MOVE":
                moves[int(fields[1])].append((turn, (int(fields[2]), int(fields[3]))))
    longest = 0
    for sequence in moves.values():
        run = 0
        previous_turn = None
        previous = None
        two_back = None
        for turn, target in sequence:
            consecutive = previous_turn is not None and turn == previous_turn + 1
            if consecutive and two_back == target and previous != target:
                run += 1
            elif consecutive and previous != target:
                run = 2
            else:
                run = 1
            longest = max(longest, run)
            previous_turn, two_back, previous = turn, previous, target
    return longest


def compile_candidate(directory: Path, candidate: Path, candidate_sha256: str) -> Path:
    if sha256(candidate) != candidate_sha256:
        raise RuntimeError("candidate hash mismatch")
    binary = directory / "candidate"
    completed = subprocess.run(
        [
            "rustc",
            "--crate-name",
            "e7a_offline_live_parity_candidate",
            "--edition=2021",
            "-O",
            "-Awarnings",
            str(candidate),
            "-o",
            str(binary),
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr[:4000])
    return binary


def load_packet(path: Path, expected_sha256: str) -> dict:
    if sha256(path) != expected_sha256:
        raise RuntimeError("offline packet hash mismatch")
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        packet = json.load(stream)
    if packet.get("schema") != PACKET_SCHEMA:
        raise RuntimeError("offline packet schema mismatch")
    selection = packet.get("selection") or {}
    baseline = packet.get("baseline") or {}
    metrics = packet.get("metrics") or {}
    rows = packet.get("rows") or []
    if selection.get("audit_sha256") != AUDIT_SHA256:
        raise RuntimeError("offline packet audit provenance mismatch")
    if int(selection.get("agent_id", -1)) != AGENT_ID:
        raise RuntimeError("offline packet agent mismatch")
    if int(selection.get("submission_id", -1)) != SUBMISSION_ID:
        raise RuntimeError("offline packet submission mismatch")
    if int(selection.get("required_game", -1)) != REQUIRED_GAME:
        raise RuntimeError("offline packet required-game mismatch")
    if baseline.get("sha256") != BASELINE_SHA256:
        raise RuntimeError("offline packet baseline mismatch")
    if packet.get("sacred_sha256") != SACRED_SHA256:
        raise RuntimeError("offline packet sacred-source mismatch")
    game_ids = [int(row["game_id"]) for row in rows]
    if len(rows) != 25 or len(set(game_ids)) != 25 or REQUIRED_GAME not in game_ids:
        raise RuntimeError("offline packet game coverage mismatch")
    if sum(int(row["turns"]) for row in rows) != 7_234:
        raise RuntimeError("offline packet turn coverage mismatch")
    if int(metrics.get("games", -1)) != 25 or int(metrics.get("turns", -1)) != 7_234:
        raise RuntimeError("offline packet metric mismatch")
    for row in rows:
        transcript = row["transcript"]
        expected_output = row["baseline_output"]
        expected_lines = expected_output.splitlines()
        if text_sha256(transcript) != row["transcript_sha256"]:
            raise RuntimeError(f"transcript hash mismatch on {row['game_id']}")
        if text_sha256(expected_output) != row["baseline_output_sha256"]:
            raise RuntimeError(f"baseline output hash mismatch on {row['game_id']}")
        if len(expected_lines) != int(row["turns"]):
            raise RuntimeError(f"baseline command coverage mismatch on {row['game_id']}")
        for line in expected_lines:
            parse_commands(line)
        if longest_period2(expected_lines) != int(row["baseline_maximum_period2"]):
            raise RuntimeError(f"baseline liveness mismatch on {row['game_id']}")
    return packet


def compare_game(binary: Path, row: dict) -> dict:
    game_id = int(row["game_id"])
    turns = int(row["turns"])
    completed = subprocess.run(
        [str(binary)],
        cwd=REPO,
        input=row["transcript"],
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode:
        raise RuntimeError(
            f"candidate exited {completed.returncode} on {game_id}: "
            f"{completed.stderr[:1000]}"
        )
    if completed.stderr:
        raise RuntimeError(f"candidate stderr on {game_id}: {completed.stderr[:1000]}")
    candidate_lines = completed.stdout.splitlines()
    if len(candidate_lines) != turns:
        raise RuntimeError(
            f"candidate command coverage mismatch on {game_id}: "
            f"{len(candidate_lines)} != {turns}"
        )
    for line in candidate_lines:
        parse_commands(line)
    baseline_lines = row["baseline_output"].splitlines()
    first_difference = next(
        (
            turn
            for turn, (left, right) in enumerate(zip(baseline_lines, candidate_lines), 1)
            if left != right
        ),
        None,
    )
    return {
        "game_id": game_id,
        "seat": int(row["seat"]),
        "opponent": row["opponent"],
        "turns": turns,
        "unknown_diff_updates": int(row["unknown_diff_updates"]),
        "exact_command_lines": baseline_lines == candidate_lines,
        "first_different_turn": first_difference,
        "baseline_output_sha256": row["baseline_output_sha256"],
        "candidate_output_sha256": text_sha256("\n".join(candidate_lines) + "\n"),
        "baseline_maximum_period2": int(row["baseline_maximum_period2"]),
        "candidate_maximum_period2": longest_period2(candidate_lines),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--packet-sha256", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet_path = args.packet.resolve()
    candidate = args.candidate.resolve()
    output = args.output.resolve()

    if output.exists():
        parser.error("refusing to overwrite offline parity evidence")
    if sha256(BASELINE) != BASELINE_SHA256:
        raise RuntimeError("exact live baseline hash mismatch")
    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred source hash mismatch")
    if sha256(candidate) != args.candidate_sha256:
        raise RuntimeError("candidate hash mismatch")
    packet = load_packet(packet_path, args.packet_sha256)

    with tempfile.TemporaryDirectory(prefix="e7a-offline-live-parity-") as directory:
        binary = compile_candidate(Path(directory), candidate, args.candidate_sha256)
        rows = [compare_game(binary, row) for row in packet["rows"]]

    gates = {
        "all_25_counterexamples": len(rows) == 25,
        "required_game_present": any(row["game_id"] == REQUIRED_GAME for row in rows),
        "zero_unknown_diff_updates": all(row["unknown_diff_updates"] == 0 for row in rows),
        "exact_command_parity": all(row["exact_command_lines"] for row in rows),
        "exact_liveness_parity": all(
            row["baseline_maximum_period2"] == row["candidate_maximum_period2"]
            for row in rows
        ),
    }
    result = {
        "schema": "troll-farm-e7a-offline-live-command-parity-v1",
        "evidence_boundary": packet["evidence_boundary"],
        "selection": {
            "packet_path": str(packet_path.relative_to(REPO)),
            "packet_sha256": args.packet_sha256,
            "audit_sha256": AUDIT_SHA256,
            "agent_id": AGENT_ID,
            "submission_id": SUBMISSION_ID,
            "games": len(rows),
        },
        "baseline": packet["baseline"],
        "candidate": {
            "path": str(candidate.relative_to(REPO)),
            "bytes": candidate.stat().st_size,
            "sha256": args.candidate_sha256,
        },
        "sacred_sha256": SACRED_SHA256,
        "metrics": {
            "games": len(rows),
            "turns": sum(row["turns"] for row in rows),
            "different_games": sum(not row["exact_command_lines"] for row in rows),
            "maximum_period2": max(row["candidate_maximum_period2"] for row in rows),
        },
        "gates": gates,
        "rows": rows,
    }
    result["verdict"] = (
        "LIVE_COMMAND_PARITY_PASS" if all(gates.values()) else "LIVE_COMMAND_PARITY_FAIL"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], **result["metrics"]}, sort_keys=True))
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
