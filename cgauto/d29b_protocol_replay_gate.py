#!/usr/bin/env python3
"""Replay the compiled one-file D29b bot against exact reference transcripts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT / "rust/target/release/d29b_integrated_parity"
DEFAULT_SOURCE = (
    ROOT
    / "cgauto/submissions/candidate-agent6553250-d29b-spatial-option-critic.min.rs"
)
SEED_BLOCKS = ((0, 5), (53720, 5))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def run(reference: Path, candidate_binary: Path, candidate_source: Path) -> dict:
    digest = hashlib.sha256()
    mismatches = []
    command_lines = 0
    transcript_bytes = 0
    cases = 0
    with tempfile.TemporaryDirectory(prefix="d29b-protocol-") as directory:
        temporary = Path(directory)
        for seed_start, seed_count in SEED_BLOCKS:
            for seed in range(seed_start, seed_start + seed_count):
                for seat in (0, 1):
                    for opponent in range(8):
                        stem = temporary / f"{seed}-{seat}-{opponent}"
                        input_path = stem.with_suffix(".in")
                        expected_path = stem.with_suffix(".expected")
                        subprocess.run(
                            [
                                reference,
                                "fixture",
                                str(seed),
                                str(seat),
                                str(opponent),
                                input_path,
                                expected_path,
                            ],
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        actual = subprocess.run(
                            [candidate_binary],
                            input=input_path.read_bytes(),
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        ).stdout
                        expected = expected_path.read_bytes()
                        item = (seed, seat, opponent)
                        if actual != expected:
                            mismatches.append(item)
                        digest.update(f"{seed}:{seat}:{opponent}\0".encode())
                        digest.update(expected)
                        command_lines += expected.count(b"\n")
                        transcript_bytes += len(expected)
                        cases += 1
    source_bytes = candidate_source.stat().st_size
    return {
        "schema": 1,
        "complete": not mismatches and cases == 160 and source_bytes < 100_000,
        "seed_blocks": SEED_BLOCKS,
        "cases": cases,
        "mismatches": len(mismatches),
        "mismatch_examples": mismatches[:20],
        "command_lines": command_lines,
        "transcript_bytes": transcript_bytes,
        "transcript_sha256": digest.hexdigest(),
        "candidate_source_bytes": source_bytes,
        "candidate_source_sha256": sha256(candidate_source),
        "candidate_binary_sha256": sha256(candidate_binary),
        "reference_binary_sha256": sha256(reference),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--candidate-binary", type=Path, required=True)
    parser.add_argument("--candidate-source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.reference, args.candidate_binary, args.candidate_source)
    text = json.dumps(result, indent=1) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
