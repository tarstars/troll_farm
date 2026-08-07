#!/usr/bin/env python3
"""Run and require exact terminal equality on the consumed development panel."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


REPO = Path(__file__).resolve().parents[2]
SHARED_PATH = (
    REPO
    / "local_codex_1/e7a-half-size-logical-simplification/evaluate_open_panel.py"
)
RUNNER = Path(__file__).resolve().parent / "open_panel_live_candidate_runner.rs"
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


def load_shared():
    specification = importlib.util.spec_from_file_location(
        "e7a_single_delete_open_panel", SHARED_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load frozen open-panel evaluator")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    panel = args.panel.resolve()
    output = args.output.resolve()
    if panel.exists() or output.exists():
        parser.error("refusing to overwrite development equality evidence")

    shared = load_shared()
    shared.RUNNER = RUNNER
    shared.CANDIDATE = candidate
    shared.CANDIDATE_SHA256 = args.candidate_sha256
    with tempfile.TemporaryDirectory(prefix="e7a-single-delete-result-") as directory:
        base_output = Path(directory) / "base-result.json"
        sys.argv = [
            str(SHARED_PATH),
            "--start", "9854000",
            "--maps", "43",
            "--threads", "8",
            "--bootstrap", "50000",
            "--candidate", str(candidate),
            "--candidate-sha256", args.candidate_sha256,
            "--panel", str(panel),
            "--output", str(base_output),
        ]
        shared.main()
        result = json.loads(base_output.read_text())

    rows, _latency = shared.parse_panel(panel)
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
    exact_gate = len(rows) == 516 and not differences
    result["schema"] = "troll-farm-e7a-single-logical-deletion-development-equality-v1"
    result["evidence_boundary"] = (
        "already-consumed development maps; exact equality can qualify development only, "
        "never untouched transfer"
    )
    result["exact_equality"] = {
        "field_pairs": [list(pair) for pair in PAIRS],
        "tasks": len(rows),
        "different_tasks": len(differences),
        "differences": differences,
    }
    result["gates"]["exact_terminal_equality_516"] = exact_gate
    result["verdict"] = (
        "DEVELOPMENT_EXACT_EQUALITY_PASS"
        if all(result["gates"].values())
        else "DEVELOPMENT_EXACT_EQUALITY_FAIL"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "tasks": len(rows),
                "different_tasks": len(differences),
                "latency_p95_ratio": result["metrics"]["latency"]["candidate_p95_ratio"],
            },
            sort_keys=True,
        )
    )
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
