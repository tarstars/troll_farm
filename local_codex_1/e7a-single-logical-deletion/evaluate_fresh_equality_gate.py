#!/usr/bin/env python3
"""Run the locked one-shot untouched equality gate for the single deletion."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys


REPO = Path(__file__).resolve().parents[2]
DIRECTORY = Path(__file__).resolve().parent
SHARED_DIRECTORY = REPO / "local_codex_1/e7a-half-size-logical-simplification"
if str(SHARED_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SHARED_DIRECTORY))
import evaluate_open_panel as shared


CANDIDATE = DIRECTORY / "candidate-e7a-remove-generic-selector.rs"
CANDIDATE_SHA256 = "ab0934740171cc7f5f4cd65cdfb8cf879ca92d8236c9505903e4741e0a7c57c2"
RUNNER_TEMPLATE = DIRECTORY / "open_panel_live_candidate_runner.rs"
RUNNER_TEMPLATE_SHA256 = "d9a118d715ab0b5f0e55f2a5a846afaa9007b725a3de1cad605feadb69a83c18"
FRESH_START = 9_867_000
FRESH_MAPS = 43
FRESH_END = FRESH_START + FRESH_MAPS
THREADS = 8
BOOTSTRAP_SAMPLES = 50_000
PAIRS = (
    ("baseline_score", "candidate_score"),
    ("baseline_opponent_score", "candidate_opponent_score"),
    ("baseline_margin", "candidate_margin"),
    ("baseline_wood", "candidate_wood"),
    ("baseline_opponent_wood", "candidate_opponent_wood"),
    ("baseline_turn", "candidate_turn"),
    ("baseline_train_turn", "candidate_train_turn"),
    ("baseline_workers", "candidate_workers"),
    ("baseline_period2", "candidate_period2"),
    ("baseline_issues", "candidate_issues"),
    ("baseline_critical", "candidate_critical"),
    ("baseline_unclassified", "candidate_unclassified"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fresh_runner_source() -> str:
    if sha256(RUNNER_TEMPLATE) != RUNNER_TEMPLATE_SHA256:
        raise RuntimeError("runner-template hash mismatch")
    source = RUNNER_TEMPLATE.read_text()
    replacements = {
        "const OPEN_START: i64 = 9_854_000;": (
            f"const OPEN_START: i64 = {FRESH_START:_};"
        ),
        "const OPEN_END: i64 = 9_854_128;": f"const OPEN_END: i64 = {FRESH_END:_};",
    }
    for old, new in replacements.items():
        if source.count(old) != 1:
            raise RuntimeError(f"runner range marker is not unique: {old}")
        source = source.replace(old, new, 1)
    return source


def compile_runner(directory: Path) -> tuple[Path, dict]:
    if sha256(shared.BASELINE) != shared.BASELINE_SHA256:
        raise RuntimeError("baseline hash mismatch")
    if sha256(CANDIDATE) != CANDIDATE_SHA256:
        raise RuntimeError("candidate hash mismatch")
    if sha256(shared.SACRED) != shared.SACRED_SHA256:
        raise RuntimeError("sacred hash mismatch")
    runner_text = fresh_runner_source()
    runner_file = tempfile.NamedTemporaryFile(
        mode="w",
        prefix="e7a_single_delete_fresh_runner_",
        suffix=".rs",
        dir=DIRECTORY,
        delete=False,
    )
    old_runner = shared.RUNNER
    try:
        runner_file.write(runner_text)
        runner_file.close()
        shared.RUNNER = Path(runner_file.name)
        binary, compiler = shared.compile_runner(
            directory, CANDIDATE, CANDIDATE_SHA256
        )
    finally:
        shared.RUNNER = old_runner
        Path(runner_file.name).unlink(missing_ok=True)
    compiler.update(
        {
            "fresh_evaluator_sha256": sha256(Path(__file__)),
            "runner_template_sha256": RUNNER_TEMPLATE_SHA256,
            "fresh_runner_sha256": hashlib.sha256(runner_text.encode()).hexdigest(),
        }
    )
    return binary, compiler


def exact_differences(rows: list[dict]) -> list[dict]:
    differences = []
    for row in rows:
        fields = [left for left, right in PAIRS if row[left] != row[right]]
        if row["delta"] != 0:
            fields.append("delta")
        if fields:
            differences.append(
                {
                    "map_seed": row["map_seed"],
                    "seat": row["seat"],
                    "opponent": row["opponent"],
                    "fields": fields,
                }
            )
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.panel.exists() or args.output.exists():
        parser.error("one-shot output path already exists")

    with tempfile.TemporaryDirectory(prefix="e7a-single-delete-fresh-") as directory:
        binary, compiler = compile_runner(Path(directory))
        completed = subprocess.run(
            [str(binary), str(FRESH_START), str(FRESH_MAPS), str(args.panel), str(THREADS)],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=3600,
        )
        if completed.returncode:
            raise RuntimeError(f"fresh panel failed:\n{completed.stderr[-12000:]}")
        run_stderr = completed.stderr.strip()

    rows, latency = shared.parse_panel(args.panel)
    expected_seeds = list(range(FRESH_START, FRESH_END))
    if sorted({row["map_seed"] for row in rows}) != expected_seeds:
        raise RuntimeError("fresh range identity mismatch")
    result = shared.analyze(
        rows,
        latency,
        maps=FRESH_MAPS,
        bootstrap_samples=BOOTSTRAP_SAMPLES,
        compiler=compiler,
        panel_path=args.panel,
        candidate=CANDIDATE,
        candidate_sha256=CANDIDATE_SHA256,
        runner=RUNNER_TEMPLATE,
        evidence_boundary=(
            "one-shot untouched exact-equality transfer gate; not an Arena-rating predictor"
        ),
    )
    differences = exact_differences(rows)
    exact_gate = len(rows) == 516 and not differences
    result["schema"] = "troll-farm-e7a-single-logical-deletion-fresh-equality-v1"
    result["fresh_gate"] = {
        "locked_start_seed": FRESH_START,
        "locked_end_seed_inclusive": FRESH_END - 1,
        "maps": FRESH_MAPS,
        "one_shot": True,
        "range_arguments_exposed": False,
        "map_count_arguments_exposed": False,
        "thread_count_arguments_exposed": False,
        "bootstrap_arguments_exposed": False,
        "threads": THREADS,
        "bootstrap_samples": BOOTSTRAP_SAMPLES,
    }
    result["exact_equality"] = {
        "field_pairs": [list(pair) for pair in PAIRS],
        "tasks": len(rows),
        "different_tasks": len(differences),
        "differences": differences,
    }
    result["gates"]["exact_terminal_equality_516"] = exact_gate
    result["run_stderr"] = run_stderr
    result["verdict"] = (
        "UNTOUCHED_EXACT_EQUALITY_PASS"
        if all(result["gates"].values())
        else "UNTOUCHED_EXACT_EQUALITY_FAIL"
    )
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "tasks": len(rows),
                "different_tasks": len(differences),
                "failed_gates": [
                    name for name, passed in result["gates"].items() if not passed
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
