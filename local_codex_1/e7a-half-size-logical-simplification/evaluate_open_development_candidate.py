#!/usr/bin/env python3
"""Run a named development source through the frozen r32 open-panel evaluator.

This wrapper changes only the candidate path and expected hash.  It is for attribution on
an already-consumed development range; it cannot produce a qualification verdict for a new
successor.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys


DIRECTORY = Path(__file__).resolve().parent
EVALUATOR = DIRECTORY / "evaluate_open_panel.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--maps", type=int, required=True)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--bootstrap", type=int, default=50_000)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidate = args.candidate.resolve()
    if sha256(candidate) != args.candidate_sha256:
        raise RuntimeError("development candidate hash mismatch")

    specification = importlib.util.spec_from_file_location(
        "e7a_frozen_open_panel", EVALUATOR
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load frozen evaluator")
    evaluator = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(evaluator)
    evaluator.CANDIDATE = candidate
    evaluator.CANDIDATE_SHA256 = args.candidate_sha256

    sys.argv = [
        str(EVALUATOR),
        "--start",
        str(args.start),
        "--maps",
        str(args.maps),
        "--threads",
        str(args.threads),
        "--bootstrap",
        str(args.bootstrap),
        "--panel",
        str(args.panel),
        "--output",
        str(args.output),
    ]
    return int(evaluator.main())


if __name__ == "__main__":
    raise SystemExit(main())
