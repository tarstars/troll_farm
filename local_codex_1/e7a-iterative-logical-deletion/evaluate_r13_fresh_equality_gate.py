#!/usr/bin/env python3
"""Run the locked one-shot untouched equality gate for iterative E7a round 13."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[2]
DIRECTORY = Path(__file__).resolve().parent
SHARED_EVALUATOR = (
    REPO
    / "local_codex_1/e7a-single-logical-deletion/evaluate_fresh_equality_gate.py"
)
specification = importlib.util.spec_from_file_location(
    "e7a_iterative_r13_fresh_shared", SHARED_EVALUATOR
)
if specification is None or specification.loader is None:
    raise RuntimeError("cannot load frozen single-deletion fresh evaluator")
shared = importlib.util.module_from_spec(specification)
specification.loader.exec_module(shared)


shared.DIRECTORY = DIRECTORY
shared.CANDIDATE = DIRECTORY / "candidate-r13-remove-movement-tie-mode.rs"
shared.CANDIDATE_SHA256 = (
    "6b9fdc99c960b4ddc969729d9452b1e5b7b252b06f8314a8567e969e27f5ba34"
)
shared.FRESH_START = 9_868_000
shared.FRESH_MAPS = 43
shared.FRESH_END = shared.FRESH_START + shared.FRESH_MAPS
original_compile_runner = shared.compile_runner


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_runner(directory: Path):
    binary, compiler = original_compile_runner(directory)
    compiler["fresh_evaluator_sha256"] = sha256(Path(__file__))
    return binary, compiler


shared.compile_runner = compile_runner


def main() -> int:
    result_code = shared.main()
    try:
        output = Path(sys.argv[sys.argv.index("--output") + 1])
    except (ValueError, IndexError) as error:
        raise RuntimeError("locked output argument is missing") from error
    result = json.loads(output.read_text())
    result["schema"] = "troll-farm-e7a-iterative-logical-deletion-r13-fresh-v1"
    result["fresh_gate"]["task_id"] = "20260803-e7a-iterative-logical-deletion"
    result["fresh_gate"]["accepted_rounds"] = 13
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
