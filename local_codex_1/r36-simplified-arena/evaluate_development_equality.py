#!/usr/bin/env python3
"""Run round 36 through the consumed 43-map/516-task exact-equality gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
SHARED_DIRECTORY = REPO / "local_codex_1/e7a-half-size-logical-simplification"
import sys

if str(SHARED_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SHARED_DIRECTORY))
import evaluate_open_panel as shared


CANDIDATE = (
    REPO
    / "claude_1/r36-submission/candidate-agent6553250-e7a-r36-simplified.min.rs"
)
CANDIDATE_SHA256 = (
    "2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381"
)
RUNNER_TEMPLATE = (
    REPO / "local_codex_1/e7a-single-logical-deletion/open_panel_live_candidate_runner.rs"
)
RUNNER_TEMPLATE_SHA256 = (
    "d9a118d715ab0b5f0e55f2a5a846afaa9007b725a3de1cad605feadb69a83c18"
)
START_SEED = 9_854_000
MAPS = 43
THREADS = 8
BOOTSTRAP_SAMPLES = 50_000
FIELD_PAIRS = (
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


def derived_runner_source() -> str:
    """Adapt the qualified live-candidate runner to round 36's deleted score field."""

    if sha256(RUNNER_TEMPLATE) != RUNNER_TEMPLATE_SHA256:
        raise RuntimeError("live-candidate runner template hash mismatch")
    source = RUNNER_TEMPLATE.read_text()
    anchor = "fn candidate_view(game: &GameState, player: usize)"
    if source.count(anchor) != 1:
        raise RuntimeError("candidate-view runner anchor is not unique")
    prefix, candidate_suffix = source.split(anchor, 1)
    obsolete_initializer = (
        "        scores: [game.scores[player], game.scores[opponent]],\n"
    )
    if candidate_suffix.count(obsolete_initializer) != 1:
        raise RuntimeError("candidate score initializer is not unique")
    candidate_suffix = candidate_suffix.replace(obsolete_initializer, "", 1)
    return prefix + anchor + candidate_suffix


def exact_differences(rows: list[dict]) -> list[dict]:
    differences = []
    for row in rows:
        changed = {
            left: {"baseline": row[left], "candidate": row[right]}
            for left, right in FIELD_PAIRS
            if row[left] != row[right]
        }
        if row["delta"] != 0:
            changed["delta"] = {"baseline": 0, "candidate": row["delta"]}
        if changed:
            differences.append(
                {
                    "map_seed": row["map_seed"],
                    "seat": row["seat"],
                    "opponent": row["opponent"],
                    "fields": changed,
                }
            )
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.panel.exists() or args.output.exists():
        parser.error("output paths must not already exist")

    with tempfile.TemporaryDirectory(prefix="e7a-r36-development-") as directory:
        generated_runner = Path(directory) / "r36_development_runner.rs"
        runner_source = derived_runner_source()
        generated_runner.write_text(runner_source)
        previous_runner = shared.RUNNER
        try:
            shared.RUNNER = generated_runner
            binary, compiler = shared.compile_runner(
                Path(directory), CANDIDATE, CANDIDATE_SHA256
            )
        finally:
            shared.RUNNER = previous_runner
        compiler.update(
            {
                "live_candidate_runner_template_sha256": RUNNER_TEMPLATE_SHA256,
                "generated_round36_runner_sha256": hashlib.sha256(
                    runner_source.encode()
                ).hexdigest(),
            }
        )
        completed = subprocess.run(
            [str(binary), str(START_SEED), str(MAPS), str(args.panel), str(THREADS)],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=3600,
        )
        if completed.returncode:
            raise RuntimeError(f"development panel failed:\n{completed.stderr[-12000:]}")

    rows, latency = shared.parse_panel(args.panel)
    expected_seeds = list(range(START_SEED, START_SEED + MAPS))
    if sorted({row["map_seed"] for row in rows}) != expected_seeds:
        raise RuntimeError("development range identity mismatch")

    result = shared.analyze(
        rows,
        latency,
        maps=MAPS,
        bootstrap_samples=BOOTSTRAP_SAMPLES,
        compiler=compiler,
        panel_path=args.panel,
        candidate=CANDIDATE,
        candidate_sha256=CANDIDATE_SHA256,
        runner=RUNNER_TEMPLATE,
        evidence_boundary=(
            "already-consumed development maps; exact equality qualifies deployment "
            "validity only, not Arena strength"
        ),
    )
    differences = exact_differences(rows)
    exact_gate = len(rows) == 516 and not differences
    result["schema"] = "troll-farm-e7a-r36-development-equality-v1"
    result["exact_equality"] = {
        "field_pairs": [list(pair) for pair in FIELD_PAIRS],
        "tasks": len(rows),
        "different_tasks": len(differences),
        "first_difference": differences[0] if differences else None,
        "differences": differences,
    }
    result["gates"]["exact_terminal_equality_516"] = exact_gate
    result["run_stderr"] = completed.stderr.strip()
    passed = all(result["gates"].values())
    result["verdict"] = (
        "DEVELOPMENT_EXACT_EQUALITY_PASS"
        if passed
        else "DEVELOPMENT_EXACT_EQUALITY_FAIL"
    )
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "tasks": len(rows),
                "different_tasks": len(differences),
                "first_difference": differences[0] if differences else None,
                "failed_gates": [
                    name for name, value in result["gates"].items() if not value
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
